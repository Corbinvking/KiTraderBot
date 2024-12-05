#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
import logging
import pytest
import asyncpg
from datetime import datetime
from decimal import Decimal
from ..token_tracker import TokenTracker
from ..birdeye_client import BirdeyeClient

# Configure logging per project standards
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/kitraderbot/test_token_tracker.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Test configuration
TEST_DB_CONFIG = {
    'user': 'postgres',
    'database': 'fantasysol',
    'host': '/var/run/postgresql',
    'port': 5432
}

# Test data - using real Solana token addresses
TEST_TOKENS = {
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'SOL': 'So11111111111111111111111111111111111111112',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'ORCA': '8FRFC6MoGGkMFQwngccyu69VnYbzykGeez7ignHVAFSN',
    'RAY': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R'
}

# Expected schema definitions
REQUIRED_TABLES = {
    'solana_tokens': '''
        CREATE TABLE IF NOT EXISTS solana_tokens (
            token_address VARCHAR(44) PRIMARY KEY,
            is_active BOOLEAN DEFAULT true,
            verification_status VARCHAR(20) DEFAULT 'pending',
            first_seen_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_birdeye_update TIMESTAMP WITH TIME ZONE,
            birdeye_metadata JSONB
        )
    ''',
    'token_prices': '''
        CREATE TABLE IF NOT EXISTS token_prices (
            id SERIAL PRIMARY KEY,
            token_address VARCHAR(44) REFERENCES solana_tokens(token_address),
            price_sol NUMERIC(24,12) NOT NULL,
            source VARCHAR(20) NOT NULL,
            source_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
            source_latency INTEGER,
            confidence_score FLOAT,
            price_metadata JSONB,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    '''
}

@pytest.fixture
async def db_pool():
    """Create database connection pool and ensure schema"""
    try:
        # Create pool
        pool = await asyncpg.create_pool(
            **TEST_DB_CONFIG,
            min_size=5,
            max_size=10
        )
        
        # Verify and create schema
        async with pool.acquire() as conn:
            for table_name, schema in REQUIRED_TABLES.items():
                try:
                    await conn.execute(schema)
                    logger.info(f"Verified table: {table_name}")
                except Exception as e:
                    logger.error(f"Failed to verify {table_name}: {e}")
                    raise
        
        yield pool
        await pool.close()
        
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

@pytest.fixture
async def token_tracker(db_pool):
    """Create token tracker instance"""
    try:
        birdeye_client = BirdeyeClient()
        tracker = TokenTracker(db_pool, birdeye_client)
        await tracker.initialize()
        logger.info(f"Yielding tracker: {tracker}")
        yield tracker
        await tracker.close()
    except Exception as e:
        logger.error(f"Failed to initialize token tracker: {e}")
        raise

@pytest.mark.asyncio
async def test_initialization(token_tracker):
    """Test tracker initialization"""
    logger.info(f"Testing tracker: {token_tracker}")
    assert token_tracker._running
    assert token_tracker.birdeye is not None
    logger.info("Initialization test passed")

@pytest.mark.asyncio
async def test_token_tracking(token_tracker):
    """Test tracking a new token"""
    logger.info("Starting token tracking test...")

    # Test USDC tracking
    token_address = TEST_TOKENS['USDC']
    logger.info(f"Testing USDC tracking: {token_address}")

    try:
        # Track new token with timeout
        success = await asyncio.wait_for(
            token_tracker.track_new_token(token_address),
            timeout=30.0  # 30 second timeout
        )
        assert success, "Failed to track USDC token"
        logger.info("Successfully tracked USDC token")

        # Verify token info with timeout
        token_info = await asyncio.wait_for(
            token_tracker.get_token_info(token_address),
            timeout=15.0
        )
        assert token_info is not None, "Failed to get token info"
        assert token_info['token_address'] == token_address
        assert token_info['is_active'] is True
        logger.info("Successfully verified token info")

    except asyncio.TimeoutError:
        logger.error("Test timed out waiting for database operations")
        raise
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise

@pytest.mark.asyncio
async def test_multiple_tokens(token_tracker):
    """Test tracking multiple tokens"""
    logger.info("Starting multiple token test...")
    
    results = {}
    for name, address in TEST_TOKENS.items():
        try:
            success = await token_tracker.track_new_token(address)
            results[name] = success
            logger.info(f"{name} tracking {'succeeded' if success else 'failed'}")
        except Exception as e:
            logger.error(f"Error tracking {name}: {e}")
            results[name] = False
    
    assert any(results.values()), "Failed to track any tokens"
    logger.info(f"Multiple token test results: {results}")

@pytest.mark.asyncio
async def test_price_updates(token_tracker):
    """Test price update functionality"""
    logger.info("Starting price update test...")
    
    token_address = TEST_TOKENS['USDC']
    try:
        # Get initial price
        initial_info = await token_tracker.get_token_info(token_address)
        assert initial_info is not None
        
        # Wait for update interval
        await asyncio.sleep(token_tracker.update_interval)
        
        # Get updated price
        updated_info = await token_tracker.get_token_info(token_address)
        assert updated_info is not None
        
        # Compare timestamps
        initial_time = initial_info.get('last_birdeye_update')
        updated_time = updated_info.get('last_birdeye_update')
        
        if initial_time and updated_time:
            assert updated_time > initial_time
            logger.info("Price update verified")
        
    except Exception as e:
        logger.error(f"Price update test failed: {e}")
        raise

async def main():
    """Run tests"""
    logger.info("Starting TokenTracker tests...")
    start_time = datetime.now()
    results = []

    try:
        # Create pool with timeout
        pool = await asyncio.wait_for(
            asyncpg.create_pool(**TEST_DB_CONFIG),
            timeout=30.0
        )
        
        # Initialize tracker with timeout
        birdeye_client = BirdeyeClient()
        tracker = TokenTracker(pool, birdeye_client)
        await asyncio.wait_for(
            tracker.initialize(),
            timeout=30.0
        )

        # Run tests
        tests = [
            ('Initialization', test_initialization),
            ('Token Tracking', test_token_tracking),
            ('Multiple Tokens', test_multiple_tokens),
            ('Price Updates', test_price_updates)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                # Run each test with a timeout
                await asyncio.wait_for(
                    test_func(tracker),
                    timeout=60.0  # 1 minute timeout per test
                )
                passed += 1
                results.append((test_name, True, None))
                logger.info(f"✓ {test_name}")
            except Exception as e:
                results.append((test_name, False, str(e)))
                logger.error(f"✗ {test_name}: {e}")

        # Cleanup
        await tracker.close()
        await pool.close()
        
        # Print summary
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("\n=== Test Summary ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")

        if passed < total:
            logger.info("\nErrors:")
            for name, success, error in results:
                if not success:
                    logger.info(f"  - {name}: {error}")

    except Exception as e:
        logger.error(f"Tests failed: {str(e)}")
        duration = (datetime.now() - start_time).total_seconds()
        logger.info("\n=== Test Summary ===")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("Passed: 0/1 (0.0%)")

if __name__ == "__main__":
    asyncio.run(main())
