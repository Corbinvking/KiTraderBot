"""
Solana Integration Tests
======================

Tests the complete Solana integration:
- RPC connection
- Token tracking
- Price updates
- Trading operations
"""

import asyncio
import logging
import sys
import os
from decimal import Decimal
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from scripts.solana import SolanaRPCManager, TokenTracker, TradingEngine
from scripts.user_management import UserManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Test data
TEST_USER_ID = 1
TEST_TOKENS = {
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'USDT': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
}

async def cleanup_resources(rpc=None, db_pool=None):
    """Cleanup test resources"""
    try:
        if rpc:
            await rpc.close()
        if db_pool:
            await db_pool.close()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

async def test_database_connection():
    """Test database connection"""
    db_pool = None
    try:
        user_manager = UserManager()
        db_pool = await user_manager.init_db()
        assert db_pool is not None, "Failed to create database pool"
        
        # Test simple query
        async with db_pool.acquire() as conn:
            version = await conn.fetchval("SELECT version()")
            assert version is not None, "Failed to query database"
            logger.info(f"Database version: {version}")
            
        logger.info("Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
    finally:
        await cleanup_resources(db_pool=db_pool)

async def test_rpc_connection():
    """Test RPC connection"""
    rpc = None
    try:
        rpc = SolanaRPCManager()
        
        # Test getVersion
        version = await rpc.get_version()
        assert version is not None, "Failed to get version"
        logger.info(f"Solana version: {version}")
        
        # Test getSlot
        slot = await rpc.get_slot()
        assert slot is not None, "Failed to get slot"
        logger.info(f"Current slot: {slot}")
        
        # Test getRecentBlockhash
        blockhash = await rpc.get_latest_blockhash()
        assert blockhash is not None, "Failed to get latest blockhash"
        logger.info(f"Latest blockhash: {blockhash}")
        
        logger.info("RPC connection test passed")
        return True
    except Exception as e:
        logger.error(f"RPC connection test failed: {e}")
        return False
    finally:
        await cleanup_resources(rpc=rpc)

async def test_token_tracking():
    """Test token tracking"""
    rpc = None
    db_pool = None
    try:
        user_manager = UserManager()
        db_pool = await user_manager.init_db()
        
        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        
        # Test token info retrieval
        token_info = await token_tracker.get_token_info(TEST_TOKENS['USDC'])
        assert token_info is not None, "Failed to get token info"
        logger.info(f"Token info retrieved: {token_info}")
        
        # Test price update
        price = await token_tracker.update_token_price(TEST_TOKENS['USDC'])
        assert price is not None, "Failed to update token price"
        logger.info(f"Token price updated: {price}")
        
        logger.info("Token tracking test passed")
        return True
        
    except Exception as e:
        logger.error(f"Token tracking test failed: {e}")
        return False
    finally:
        await cleanup_resources(rpc=rpc, db_pool=db_pool)

async def test_trading_operations():
    """Test trading operations"""
    rpc = None
    db_pool = None
    try:
        user_manager = UserManager()
        db_pool = await user_manager.init_db()
        
        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)
        
        # Test wallet creation
        wallet = await trading_engine.get_wallet(TEST_USER_ID)
        assert wallet is not None, "Failed to create wallet"
        logger.info(f"Wallet created: {wallet}")
        
        # Test position opening
        position = await trading_engine.open_position(
            user_id=TEST_USER_ID,
            token_address=TEST_TOKENS['USDC'],
            size_sol=Decimal('10.0'),
            position_type='long'
        )
        assert position is not None, "Failed to open position"
        logger.info(f"Position opened: {position}")
        
        # Test position closing
        result = await trading_engine.close_position(position['position_id'])
        assert result is not None, "Failed to close position"
        logger.info(f"Position closed: {result}")
        
        logger.info("Trading operations test passed")
        return True
        
    except Exception as e:
        logger.error(f"Trading operations test failed: {e}")
        return False
    finally:
        await cleanup_resources(rpc=rpc, db_pool=db_pool)

async def run_all_tests():
    """Run all Solana integration tests"""
    logger.info("Starting Solana integration tests...")
    
    # Test database connection first
    db_success = await test_database_connection()
    if db_success:
        logger.info("Database connection tests passed")
        
        # Test RPC connection
        rpc_success = await test_rpc_connection()
        if rpc_success:
            logger.info("RPC connection tests passed")
            
            # Test token tracking
            tracking_success = await test_token_tracking()
            if tracking_success:
                logger.info("Token tracking tests passed")
                
                # Test trading operations
                trading_success = await test_trading_operations()
                if trading_success:
                    logger.info("Trading operations tests passed")
    
    logger.info("All Solana integration tests completed")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
