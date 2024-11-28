import asyncio
import logging
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from scripts.solana.rpc_manager import SolanaRPCManager
from scripts.solana.token_tracker import TokenTracker
from scripts.solana.trading_engine import SimulatedTrading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test token address (USDC on Solana)
TEST_TOKEN_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

async def test_rpc_connection():
    """Test RPC connection and failover"""
    rpc = SolanaRPCManager()
    try:
        assert await rpc.initialize(), "Failed to initialize RPC connection"
        version = await rpc.client.get_version()
        logger.info(f"Connected successfully. Version: {version}")
        return True
    except Exception as e:
        logger.error(f"RPC connection test failed: {e}")
        return False
    finally:
        await rpc.close()

async def test_token_data():
    """Test token data retrieval"""
    rpc = SolanaRPCManager()
    try:
        await rpc.initialize()
        token_data = await rpc.get_token_data(TEST_TOKEN_ADDRESS)
        assert token_data is not None, "Failed to get token data"
        logger.info(f"Token data: {token_data}")
        return True
    except Exception as e:
        logger.error(f"Token data test failed: {e}")
        return False
    finally:
        await rpc.close()

async def run_all_tests():
    """Run all tests"""
    logger.info("Starting Solana integration tests...")
    
    connection_result = await test_rpc_connection()
    if connection_result:
        logger.info("RPC connection test passed")
        
        token_result = await test_token_data()
        if token_result:
            logger.info("Token data test passed")
    
    logger.info("All tests completed")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
