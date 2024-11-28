import asyncio
import logging
import sys
import os
import asyncpg
from decimal import Decimal
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from scripts.solana.rpc_manager import SolanaRPCManager
from scripts.solana.token_tracker import TokenTracker
from scripts.solana.trading_engine import TradingEngine, Position

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test data
TEST_USER_ID = 1
TEST_TOKENS = {
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'USDT': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
}

async def setup_database():
    """Create a test database connection"""
    try:
        pool = await asyncpg.create_pool(
            user='kitrader',
            password='kitraderpass',
            database='fantasysol',
            host='localhost',
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        logger.info("Database connection established")
        return pool
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

async def ensure_test_user(pool):
    """Ensure test user exists in the database"""
    try:
        async with pool.acquire() as conn:
            # Check if user exists
            user = await conn.fetchrow("""
                SELECT user_id, telegram_id, username, role
                FROM users
                WHERE user_id = $1
            """, TEST_USER_ID)
            
            if not user:
                # Create test user if doesn't exist
                user = await conn.fetchrow("""
                    INSERT INTO users (
                        user_id, telegram_id, username, role, 
                        registration_date, account_status
                    ) VALUES (
                        $1, $2, $3, $4, 
                        CURRENT_TIMESTAMP, 'active'
                    ) RETURNING user_id, telegram_id, username, role
                """, TEST_USER_ID, 123456789, 'test_user', 'basic')
                
                # Create user settings
                await conn.execute("""
                    INSERT INTO user_settings (
                        user_id, notification_preferences, 
                        risk_settings, ui_preferences
                    ) VALUES (
                        $1, 
                        '{"enabled": true}'::jsonb,
                        '{"max_position_size": 100}'::jsonb,
                        '{}'::jsonb
                    )
                """, TEST_USER_ID)
                
                logger.info(f"Created test user: {user}")
            else:
                logger.info(f"Using existing test user: {user}")
            
            return user
            
    except Exception as e:
        logger.error(f"Error ensuring test user exists: {e}")
        return None

async def cleanup_test_data(pool):
    """Clean up test data after tests"""
    try:
        async with pool.acquire() as conn:
            # Clean up positions
            await conn.execute("""
                DELETE FROM positions WHERE user_id = $1
            """, TEST_USER_ID)
            
            # Clean up virtual wallet
            await conn.execute("""
                DELETE FROM virtual_wallets WHERE user_id = $1
            """, TEST_USER_ID)
            
            logger.info("Test data cleaned up")
            
    except Exception as e:
        logger.error(f"Error cleaning up test data: {e}")

async def test_wallet_creation():
    """Test virtual wallet creation and management"""
    try:
        db_pool = await setup_database()
        if not db_pool:
            return False

        # Ensure test user exists
        test_user = await ensure_test_user(db_pool)
        if not test_user:
            logger.error("Failed to create test user")
            return False

        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)

        # Test wallet creation
        wallet = await trading_engine.get_wallet(TEST_USER_ID)
        assert wallet is not None, "Failed to create wallet"
        assert wallet['balance'] == Decimal('1000.0'), "Incorrect initial balance"
        
        logger.info(f"Wallet created successfully: {wallet}")
        return True

    except Exception as e:
        logger.error(f"Wallet test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def test_position_opening():
    """Test opening trading positions"""
    try:
        db_pool = await setup_database()
        if not db_pool:
            return False

        # Ensure test user exists
        test_user = await ensure_test_user(db_pool)
        if not test_user:
            logger.error("Failed to create test user")
            return False

        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)

        # Test opening a position
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=TEST_TOKENS['USDC'],
            size_sol=Decimal('10.0'),
            position_type='long',
            leverage=Decimal('1.0')
        )

        assert position is not None, "Failed to open position"
        logger.info(f"Position opened successfully: {position}")

        # Verify wallet balance was updated
        wallet = await trading_engine.get_wallet(TEST_USER_ID)
        assert wallet['balance'] < Decimal('1000.0'), "Wallet balance not updated"
        
        return True

    except Exception as e:
        logger.error(f"Position opening test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def test_position_closing():
    """Test closing trading positions"""
    try:
        db_pool = await setup_database()
        if not db_pool:
            return False

        # Ensure test user exists
        test_user = await ensure_test_user(db_pool)
        if not test_user:
            logger.error("Failed to create test user")
            return False

        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)

        # First open a position
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=TEST_TOKENS['USDC'],
            size_sol=Decimal('10.0'),
            position_type='long'
        )

        assert position is not None, "Failed to open position"
        
        # Close the position
        closed = await trading_engine.close_position(position['position_id'])
        assert closed is not None, "Failed to close position"
        
        logger.info(f"Position closed successfully: {closed}")

        # Verify position status
        positions = await trading_engine.get_positions(TEST_USER_ID, status='closed')
        assert len(positions) > 0, "No closed positions found"
        
        return True

    except Exception as e:
        logger.error(f"Position closing test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def test_position_pnl():
    """Test PnL calculations"""
    try:
        db_pool = await setup_database()
        if not db_pool:
            return False

        # Ensure test user exists
        test_user = await ensure_test_user(db_pool)
        if not test_user:
            logger.error("Failed to create test user")
            return False

        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)

        # Open a position
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=TEST_TOKENS['USDC'],
            size_sol=Decimal('10.0'),
            position_type='long'
        )

        assert position is not None, "Failed to open position"
        
        # Wait for price update
        await asyncio.sleep(5)
        
        # Close position and check PnL
        closed = await trading_engine.close_position(position['position_id'])
        assert closed is not None, "Failed to close position"
        assert 'pnl' in closed, "No PnL calculated"
        
        logger.info(f"Position PnL calculation successful: {closed['pnl']} SOL")
        return True

    except Exception as e:
        logger.error(f"PnL calculation test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def run_all_tests():
    """Run all trading engine tests"""
    logger.info("Starting Trading Engine tests...")
    
    # Test wallet functionality
    wallet_success = await test_wallet_creation()
    if wallet_success:
        logger.info("Wallet tests passed")
        
        # Test position operations
        position_success = await test_position_opening()
        if position_success:
            logger.info("Position opening tests passed")
            
            close_success = await test_position_closing()
            if close_success:
                logger.info("Position closing tests passed")
                
                pnl_success = await test_position_pnl()
                if pnl_success:
                    logger.info("PnL calculation tests passed")
    
    logger.info("All Trading Engine tests completed")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
