#!/usr/bin/env python3
import pytest
from decimal import Decimal
import asyncpg

# Test configuration
TEST_USER_ID = 1
TEST_TOKENS = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
}

@pytest.fixture(autouse=True)
async def cleanup_db(db_pool):
    """Clean up database between tests"""
    async with db_pool.acquire() as conn:
        await conn.execute("DELETE FROM trade_history")
        await conn.execute("DELETE FROM trading_positions")
        await conn.execute("DELETE FROM virtual_wallets")
    yield

@pytest.fixture
async def mock_birdeye():
    """Create mock Birdeye client"""
    class MockBirdeyeClient:
        def __init__(self):
            self._token_info = {
                'symbol': 'SOL',
                'mc': 1000000,
                'liquidity': 100000
            }

        async def get_token_info(self, token_address):
            return self._token_info

        def set_token_info(self, info):
            self._token_info = info

        async def close(self):
            pass

    return MockBirdeyeClient()

@pytest.fixture
async def trading_engine(db_pool, token_tracker, mock_birdeye):
    """Create TradingEngine instance"""
    from scripts.solana.trading_engine import TradingEngine
    engine = TradingEngine(db_pool, token_tracker, mock_birdeye)
    await engine.initialize()
    yield engine
    await engine.close()

@pytest.mark.asyncio
async def test_database_initialization(trading_engine, db_pool):
    """Test database tables are created correctly"""
    async with db_pool.acquire() as conn:
        # Check positions table
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'trading_positions'
            )
        """)
        assert result is True
        
        # Check trade history table
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'trade_history'
            )
        """)
        assert result is True
        
        # Verify constraints
        # Test size limits
        with pytest.raises(Exception):
            await conn.execute("""
                INSERT INTO trading_positions (
                    user_id, token_address, position_type, size_sol, entry_price
                ) VALUES ($1, $2, $3, $4, $5)
            """, TEST_USER_ID, TEST_TOKENS['SOL'], 'long', 0.05, 100.0)  # Too small

@pytest.mark.asyncio
async def test_wallet_initialization(trading_engine, db_pool):
    """Test virtual wallet creation and management"""
    # Test wallet creation
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    assert wallet['balance_sol'] == Decimal('1000.0')  # Default balance
    assert wallet['locked_sol'] == Decimal('0.0')
    
    # Verify wallet in database
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT balance_sol, locked_sol
            FROM virtual_wallets
            WHERE user_id = $1
        """, TEST_USER_ID)
        
        assert row is not None
        assert row['balance_sol'] == Decimal('1000.0')
        assert row['locked_sol'] == Decimal('0.0')

@pytest.mark.asyncio
async def test_wallet_constraints(trading_engine, db_pool):
    """Test wallet balance constraints"""
    # Initialize wallet first
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    async with db_pool.acquire() as conn:
        # Test negative balance prevention
        with pytest.raises(asyncpg.exceptions.CheckViolationError):
            await conn.execute("""
                UPDATE virtual_wallets
                SET balance_sol = -100.0
                WHERE user_id = $1
            """, TEST_USER_ID)
            
        # Test negative locked amount prevention
        with pytest.raises(asyncpg.exceptions.CheckViolationError):
            await conn.execute("""
                UPDATE virtual_wallets
                SET locked_sol = -50.0
                WHERE user_id = $1
            """, TEST_USER_ID)

@pytest.mark.asyncio
async def test_position_opening(trading_engine, token_tracker):
    """Test opening trading positions"""
    # Initialize wallet first
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    # First track the token
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Open a long position
    position = await trading_engine.open_position(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('1.0'),
        position_type='long'
    )
    
    assert position is not None
    assert position['size'] == Decimal('1.0')
    assert position['type'] == 'long'
    
    # Verify wallet balance is updated
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet['balance_sol'] == Decimal('999.0')  # 1000 - 1
    assert wallet['locked_sol'] == Decimal('1.0')

@pytest.mark.asyncio
async def test_position_limits(trading_engine, token_tracker):
    """Test position size limits"""
    # Initialize wallet first
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Test minimum size
    with pytest.raises(ValueError, match="Position size too small"):
        await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=token,
            size_sol=Decimal('0.05'),  # Below MIN_TRADE_SIZE
            position_type='long'
        )
    
    # Test maximum size
    with pytest.raises(ValueError, match="Position size too large"):
        await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=token,
            size_sol=Decimal('150.0'),  # Above MAX_TRADE_SIZE
            position_type='long'
        )
    
    # Test maximum positions per user
    # First open max allowed positions
    positions = []
    for _ in range(trading_engine.MAX_POSITIONS_PER_USER):
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=token,
            size_sol=Decimal('1.0'),
            position_type='long'
        )
        assert position is not None
        positions.append(position)
    
    # Verify we have max positions
    assert len(positions) == trading_engine.MAX_POSITIONS_PER_USER
    
    # Try to open one more - should fail
    with pytest.raises(ValueError, match="Maximum positions reached"):
        await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=token,
            size_sol=Decimal('1.0'),
            position_type='long'
        )

@pytest.mark.asyncio
async def test_position_closing(trading_engine, token_tracker):
    """Test closing trading positions"""
    # Initialize wallet and open position
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Open a position
    position = await trading_engine.open_position(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('1.0'),
        position_type='long'
    )
    assert position is not None
    
    # Close the position
    result = await trading_engine.close_position(position['position_id'])
    assert result is not None
    assert 'pnl' in result
    
    # Verify wallet is updated
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet['locked_sol'] == Decimal('0.0')  # Position is closed
    assert wallet['balance_sol'] >= Decimal('999.0')  # Original balance minus fees

@pytest.mark.asyncio
async def test_position_pnl_calculation(trading_engine, token_tracker, mock_birdeye):
    """Test PnL calculation for positions"""
    # Initialize wallet
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Modify mock price for entry
    mock_birdeye.set_token_info({'symbol': 'SOL', 'mc': 1000000, 'liquidity': 10000})  # Price = 100
    
    # Open a long position
    position = await trading_engine.open_position(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('1.0'),
        position_type='long'
    )
    
    # Modify mock price for exit (10% increase)
    mock_birdeye.set_token_info({'symbol': 'SOL', 'mc': 1100000, 'liquidity': 10000})  # Price = 110
    
    # Close position and verify PnL
    result = await trading_engine.close_position(position['position_id'])
    assert result['pnl'] == Decimal('10.0')  # 10% profit on 1 SOL

@pytest.mark.asyncio
async def test_position_querying(trading_engine, token_tracker):
    """Test position querying functionality"""
    # Initialize wallet
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Open multiple positions
    positions_to_create = 5
    created_positions = []
    
    for i in range(positions_to_create):
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=token,
            size_sol=Decimal('1.0'),
            position_type='long' if i % 2 == 0 else 'short'
        )
        assert position is not None
        created_positions.append(position)
        
        # Close every other position
        if i % 2 == 0:
            await trading_engine.close_position(position['position_id'])
    
    # Test querying open positions
    open_positions = await trading_engine.get_user_positions(
        user_id=TEST_USER_ID,
        status='open'
    )
    assert len(open_positions) == positions_to_create // 2
    
    # Test querying closed positions
    closed_positions = await trading_engine.get_user_positions(
        user_id=TEST_USER_ID,
        status='closed'
    )
    assert len(closed_positions) == (positions_to_create + 1) // 2
    
    # Test pagination
    paginated = await trading_engine.get_user_positions(
        user_id=TEST_USER_ID,
        status='all',
        limit=2,
        offset=1
    )
    assert len(paginated) == 2
    
    # Verify position details
    position = open_positions[0]
    assert 'position_id' in position
    assert 'token_symbol' in position
    assert 'unrealized_pnl' in position
    assert position['status'] == 'open'

@pytest.mark.asyncio
async def test_position_history(trading_engine, token_tracker, mock_birdeye):
    """Test position history functionality"""
    # Initialize wallet
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Set initial price
    mock_birdeye.set_token_info({'symbol': 'SOL', 'mc': 1000000, 'liquidity': 10000})  # Price = 100
    
    # Open position
    position = await trading_engine.open_position(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('1.0'),
        position_type='long'
    )
    
    # Get history without price updates
    history = await trading_engine.get_position_history(
        position_id=position['position_id'],
        include_price_updates=False
    )
    
    assert history is not None
    assert history['position_id'] == position['position_id']
    assert 'trades' in history
    assert len(history['trades']) == 1  # Opening trade
    assert 'price_updates' not in history
    
    # Get history with price updates
    history_with_prices = await trading_engine.get_position_history(
        position_id=position['position_id'],
        include_price_updates=True
    )
    
    assert 'price_updates' in history_with_prices
    
    # Close position and verify history
    mock_birdeye.set_token_info({'symbol': 'SOL', 'mc': 1100000, 'liquidity': 10000})  # Price = 110
    result = await trading_engine.close_position(position['position_id'])
    
    final_history = await trading_engine.get_position_history(position['position_id'])
    assert final_history['status'] == 'closed'
    assert 'duration' in final_history
    assert 'roi' in final_history
    assert len(final_history['trades']) == 2  # Open and close trades

@pytest.mark.asyncio
async def test_risk_validation(trading_engine, token_tracker):
    """Test risk management validation"""
    # Initialize wallet
    wallet = await trading_engine.get_wallet(TEST_USER_ID)
    assert wallet is not None
    
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Test normal position
    valid, message = await trading_engine.validate_position_risk(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('10.0'),  # 1% of balance
        position_type='long'
    )
    assert valid, message
    
    # Test excessive position size
    valid, message = await trading_engine.validate_position_risk(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('800.0'),  # 80% of balance
        position_type='long'
    )
    assert not valid
    assert "exposure limit" in message.lower()
    
    # Open multiple positions and test limits
    for _ in range(3):
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=token,
            size_sol=Decimal('10.0'),
            position_type='long'
        )
        assert position is not None
    
    # Try to validate another long position
    valid, message = await trading_engine.validate_position_risk(
        user_id=TEST_USER_ID,
        token_address=token,
        size_sol=Decimal('10.0'),
        position_type='long'
    )
    assert not valid
    assert "maximum long positions" in message.lower()

