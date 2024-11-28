import asyncio
import logging
import sys
import os
import asyncpg
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from scripts.solana.rpc_manager import SolanaRPCManager
from scripts.solana.token_tracker import TokenTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test token addresses (USDC and USDT on Solana)
TEST_TOKENS = {
    'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'USDT': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
}

async def setup_database():
    """Create a test database connection"""
    try:
        # Using password authentication for kitrader
        pool = await asyncpg.create_pool(
            user='kitrader',
            password='kitraderpass',  # Added password
            database='fantasysol',
            host='localhost',
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Test the connection
        async with pool.acquire() as conn:
            version = await conn.fetchval('SELECT version()')
            logger.info(f"Connected to PostgreSQL: {version}")
            
            # Verify we can access our database
            db_name = await conn.fetchval('SELECT current_database()')
            logger.info(f"Using database: {db_name}")
            
            # Verify our permissions
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            logger.info(f"Found {len(tables)} tables in database")
            
        logger.info("Database connection established and verified")
        return pool
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error(f"Connection details: user=kitrader, database=fantasysol")
        return None

async def verify_database_tables(pool):
    """Verify that required database tables exist"""
    try:
        async with pool.acquire() as conn:
            # Check if tables exist
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            required_tables = {'solana_tokens', 'token_prices', 'token_metrics'}
            existing_tables = {table['table_name'] for table in tables}
            
            missing_tables = required_tables - existing_tables
            if missing_tables:
                logger.error(f"Missing required tables: {missing_tables}")
                return False
                
            logger.info("All required database tables exist")
            return True
            
    except Exception as e:
        logger.error(f"Error verifying database tables: {e}")
        return False

async def test_token_tracking():
    """Test token tracking functionality"""
    rpc = None
    db_pool = None
    try:
        # Setup
        rpc = SolanaRPCManager()
        db_pool = await setup_database()
        if not db_pool:
            logger.error("Failed to setup database connection")
            return False

        # Verify database tables
        if not await verify_database_tables(db_pool):
            logger.error("Database tables verification failed")
            return False

        tracker = TokenTracker(rpc, db_pool)
        
        # Test tracking new tokens
        for name, address in TEST_TOKENS.items():
            logger.info(f"Testing tracking for {name} token...")
            success = await tracker.track_new_token(address)
            assert success, f"Failed to track {name} token"
            logger.info(f"Successfully tracked {name} token")

        # Test price updates
        logger.info("Testing price updates...")
        await tracker.update_token_prices()
        logger.info("Price update completed")

        # Verify data in database
        async with db_pool.acquire() as conn:
            # Check tokens table
            tokens = await conn.fetch("""
                SELECT token_address, is_active, metadata 
                FROM solana_tokens 
                WHERE token_address = ANY($1)
            """, list(TEST_TOKENS.values()))
            
            assert len(tokens) == len(TEST_TOKENS), "Not all tokens were stored"
            logger.info(f"Found {len(tokens)} tokens in database")

            # Check prices table
            prices = await conn.fetch("""
                SELECT token_address, price_sol, timestamp 
                FROM token_prices 
                WHERE token_address = ANY($1)
                ORDER BY timestamp DESC 
                LIMIT 2
            """, list(TEST_TOKENS.values()))
            
            assert len(prices) > 0, "No price data stored"
            logger.info(f"Found {len(prices)} price entries")

            # Log some price data for verification
            for price in prices:
                logger.info(f"Price data: {price}")

        # Test metrics calculation
        logger.info("Testing metrics calculation...")
        for address in TEST_TOKENS.values():
            await tracker.calculate_metrics(address)
        logger.info("Metrics calculation completed")

        return True

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
    finally:
        # Cleanup
        if db_pool:
            await db_pool.close()
        if rpc:
            await rpc.close()

async def run_all_tests():
    """Run all token tracker tests"""
    logger.info("Starting TokenTracker tests...")
    
    success = await test_token_tracking()
    if success:
        logger.info("All TokenTracker tests passed successfully")
    else:
        logger.error("TokenTracker tests failed")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
