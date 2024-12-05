#!/usr/bin/env python3
import pytest
import asyncio
from decimal import Decimal
from datetime import datetime, timezone

# Test configuration
TEST_TOKENS = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
}

@pytest.fixture
async def token_tracker(db_pool, mock_client):
    """Create TokenTracker instance"""
    from scripts.solana.token_tracker import TokenTracker
    tracker = TokenTracker(db_pool, mock_client)
    await tracker.initialize()
    yield tracker
    await tracker.close()

@pytest.fixture
async def trading_engine(db_pool, token_tracker):
    """Create TradingEngine instance"""
    from scripts.solana.trading_engine import TradingEngine
    engine = TradingEngine(db_pool, token_tracker)
    await engine.initialize()
    yield engine
    await engine.close()

@pytest.mark.asyncio
async def test_price_based_trading(trading_engine, token_tracker):
    """Test trading based on price updates"""
    # Setup trading parameters
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Configure trading strategy
    await trading_engine.set_strategy(
        token_address=token,
        entry_price=100.0,
        take_profit=120.0,
        stop_loss=90.0
    )
    
    # Simulate price updates and verify trading actions
    price_scenarios = [
        (95.0, "HOLD"),      # Above stop loss
        (85.0, "SELL"),      # Hit stop loss
        (110.0, "BUY"),      # Recovery
        (125.0, "SELL"),     # Hit take profit
    ]
    
    for price, expected_action in price_scenarios:
        # Simulate price update
        await token_tracker.update_price(token)
        
        # Get trading decision
        action = await trading_engine.evaluate_position(token)
        assert action == expected_action

@pytest.mark.asyncio
async def test_concurrent_trading(trading_engine, token_tracker):
    """Test concurrent trading operations"""
    # Track both tokens
    for token in TEST_TOKENS.values():
        await token_tracker.track_token(token)
        await trading_engine.set_strategy(
            token_address=token,
            entry_price=100.0,
            take_profit=120.0,
            stop_loss=90.0
        )
    
    # Update prices concurrently
    price_tasks = [token_tracker.update_price(token) for token in TEST_TOKENS.values()]
    await asyncio.gather(*price_tasks)
    
    # Evaluate positions concurrently
    trading_tasks = [trading_engine.evaluate_position(token) for token in TEST_TOKENS.values()]
    actions = await asyncio.gather(*trading_tasks)
    
    assert len(actions) == len(TEST_TOKENS)
    assert all(action in ["BUY", "SELL", "HOLD"] for action in actions)

@pytest.mark.asyncio
async def test_trading_constraints(trading_engine):
    """Test trading constraints and limits"""
    token = TEST_TOKENS['SOL']
    
    # Test invalid parameters
    with pytest.raises(ValueError):
        await trading_engine.set_strategy(
            token_address=token,
            entry_price=-100.0,  # Invalid negative price
            take_profit=120.0,
            stop_loss=90.0
        )
    
    # Test invalid token
    with pytest.raises(ValueError):
        await trading_engine.evaluate_position("invalid_token")
    
    # Test untracked token
    action = await trading_engine.evaluate_position(token)
    assert action == "HOLD"  # Default to HOLD for untracked tokens

@pytest.mark.asyncio
async def test_trading_history(trading_engine, token_tracker, db_pool):
    """Test trading history recording"""
    token = TEST_TOKENS['SOL']
    await token_tracker.track_token(token)
    
    # Configure strategy
    await trading_engine.set_strategy(
        token_address=token,
        entry_price=100.0,
        take_profit=120.0,
        stop_loss=90.0
    )
    
    # Execute some trades
    await trading_engine.execute_trade(token, "BUY", 100.0)
    await trading_engine.execute_trade(token, "SELL", 120.0)
    
    # Verify trade history
    async with db_pool.acquire() as conn:
        trades = await conn.fetch("""
            SELECT action, price, timestamp
            FROM trade_history
            WHERE token_address = $1
            ORDER BY timestamp DESC
        """, token)
        
        assert len(trades) == 2
        assert trades[0]['action'] == "SELL"
        assert trades[1]['action'] == "BUY" 
