#!/usr/bin/env python3
import pytest
import asyncio
from datetime import datetime
from decimal import Decimal

# Test configuration
TEST_TOKENS = {
    'SOL': 'So11111111111111111111111111111111111111112',
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
}

MOCK_PRICE_RESPONSE = {
    "success": True,
    "data": {
        "value": 127.98210121063606,
        "updateUnixTime": 1726672273,
        "updateTime": "2024-09-18T15:11:13",
        "liquidity": 7026264396.957431
    }
}

@pytest.fixture
async def mock_client():
    """Create mock Birdeye client"""
    class MockClient:
        async def get_token_price(self, token_address):
            # Only return price for valid tokens
            if token_address in TEST_TOKENS.values():
                return MOCK_PRICE_RESPONSE
            # For invalid tokens, simulate API error
            raise Exception("API error: Invalid token address")
        async def close(self):
            pass
    return MockClient()

@pytest.fixture
async def tracker(db_pool, mock_client):
    """Create TokenTracker instance"""
    from scripts.solana.token_tracker import TokenTracker
    tracker = TokenTracker(db_pool, mock_client)
    await tracker.initialize()
    yield tracker
    await tracker.close()

@pytest.mark.asyncio
async def test_basic_price_tracking(tracker):
    """Test basic price tracking"""
    token = TEST_TOKENS['SOL']
    
    # Track token
    success = await tracker.track_token(token)
    assert success, "Failed to track token"
    
    # Update price
    price_data = await tracker.update_price(token)
    assert price_data is not None
    assert 'value' in price_data
    
    # Get stored price
    stored = await tracker.get_price(token)
    assert stored is not None
    assert stored['price_sol'] == Decimal(str(price_data['value']))

@pytest.mark.asyncio
async def test_multiple_price_updates(tracker):
    """Test multiple price updates for the same token"""
    token = TEST_TOKENS['SOL']
    
    # Track token
    await tracker.track_token(token)
    
    # Do multiple updates
    for _ in range(3):
        price_data = await tracker.update_price(token)
        assert price_data is not None
        
    # Get price history
    async with tracker._pool.acquire() as conn:
        prices = await conn.fetch("""
            SELECT price_sol, timestamp 
            FROM token_prices 
            WHERE token_address = $1 
            ORDER BY timestamp DESC
        """, token)
        
    assert len(prices) == 3, "Should have 3 price records"
    
@pytest.mark.asyncio
async def test_invalid_token(tracker):
    """Test handling of invalid token address"""
    invalid_token = "invalid_address"
    
    # Try to track invalid token
    success = await tracker.track_token(invalid_token)
    assert success, "Should be able to track any address"
    
    # Try to update price
    price_data = await tracker.update_price(invalid_token)
    assert price_data is None, "Should return None for invalid token"

@pytest.mark.asyncio
async def test_concurrent_updates(tracker):
    """Test concurrent price updates"""
    # Track both tokens
    for token in TEST_TOKENS.values():
        await tracker.track_token(token)
    
    # Update prices concurrently
    tasks = [tracker.update_price(token) for token in TEST_TOKENS.values()]
    results = await asyncio.gather(*tasks)
    
    assert all(r is not None for r in results), "All updates should succeed"
    
    # Verify all prices were stored
    for token in TEST_TOKENS.values():
        stored = await tracker.get_price(token)
        assert stored is not None
        assert stored['price_sol'] == Decimal(str(MOCK_PRICE_RESPONSE['data']['value']))

@pytest.mark.asyncio
async def test_database_operations(tracker):
    """Test database operations and constraints"""
    token = TEST_TOKENS['SOL']
    
    # Test duplicate tracking
    success1 = await tracker.track_token(token)
    success2 = await tracker.track_token(token)
    assert success1 and success2, "Should handle duplicate tracking gracefully"
    
    # Test price updates
    price1 = await tracker.update_price(token)
    assert price1 is not None
    
    # Verify last_update is updated
    async with tracker._pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT last_update 
            FROM solana_tokens 
            WHERE token_address = $1
        """, token)
        assert row['last_update'] is not None

@pytest.mark.asyncio
async def test_cleanup(tracker):
    """Test cleanup functionality"""
    token = TEST_TOKENS['SOL']
    await tracker.track_token(token)
    
    # Add multiple price records
    for _ in range(3):
        await tracker.update_price(token)
        await asyncio.sleep(0.1)  # Small delay between updates
    
    # Verify records exist
    async with tracker._pool.acquire() as conn:
        count_before = await conn.fetchval("""
            SELECT COUNT(*) FROM token_prices 
            WHERE token_address = $1
        """, token)
        assert count_before == 3
        
        # Test cleanup method if it exists
        if hasattr(tracker, 'cleanup_old_prices'):
            await tracker.cleanup_old_prices(hours=0)  # Cleanup all prices
            
            count_after = await conn.fetchval("""
                SELECT COUNT(*) FROM token_prices 
                WHERE token_address = $1
            """, token)
            assert count_after < count_before

@pytest.mark.asyncio
async def test_error_handling(tracker):
    """Test error handling in various scenarios"""
    # Test with None token address
    with pytest.raises(ValueError):
        await tracker.update_price(None)
    
    # Test with empty string token address
    with pytest.raises(ValueError):
        await tracker.update_price("")
    
    # Test with very long token address
    long_address = "x" * 1000
    with pytest.raises(ValueError):
        await tracker.update_price(long_address)
