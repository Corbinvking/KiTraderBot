"""
Test script for BirdeyeClient
"""
import os
import asyncio
import logging
from scripts.solana.birdeye_client import BirdeyeClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_token(client: BirdeyeClient, name: str, address: str):
    """Test token info retrieval"""
    logger.info(f"\nTesting {name} ({address}):")
    
    try:
        logger.info("Testing token price...")
        price_data = await client.get_token_price(address)
        if price_data:
            logger.info(f"Price data: {price_data}")
        else:
            logger.warning(f"Could not get price data")
            
        logger.info("Testing token metadata...")
        metadata = await client.get_token_metadata(address)
        if metadata:
            logger.info(f"Metadata: {metadata}")
        else:
            logger.warning(f"Could not get metadata")
            
        logger.info("Testing 24h data...")
        data_24h = await client.get_token_24h_data(address)
        if data_24h:
            logger.info(f"24h data: {data_24h}")
        else:
            logger.warning(f"Could not get 24h data")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

async def test_historical_price(client: BirdeyeClient, name: str, address: str):
    """Test historical price data retrieval"""
    logger.info(f"\nTesting historical price for {name} ({address}):")
    
    try:
        address_type = "token"
        interval_type = "15m"
        historical_data = await client.get_historical_price(address, address_type, interval_type)
        if historical_data:
            logger.info(f"Historical price data: {historical_data}")
        else:
            logger.warning(f"Could not get historical price data")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")

async def run_async_tests():
    logger.info("Starting Birdeye client tests...")
    client = BirdeyeClient(api_key="65cce27c021346ea85203479dae66ccd")  # Replace with your API key
    await client.initialize()

    try:
        # Test with some known tokens
        await test_token(client, "USDC", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")
        await test_token(client, "SOL", "So11111111111111111111111111111111111111112")
        
        # Test historical price data
        await test_historical_price(client, "SOL", "So11111111111111111111111111111111111111112")
        
        # Get performance metrics
        metrics = await client.get_performance_metrics()
        logger.info(f"\nPerformance metrics: {metrics}")
        
    finally:
        if client.session:
            await client.session.close()

if __name__ == "__main__":
    asyncio.run(run_async_tests())
