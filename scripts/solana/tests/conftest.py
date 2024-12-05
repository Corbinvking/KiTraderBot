import pytest
import asyncio
import logging
import asyncpg
from ..token_tracker import TokenTracker
from ..birdeye_client import BirdeyeClient

pytest_plugins = ["pytest_asyncio"]

TEST_DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'kitraderbot_test',
    'password': 'kitraderbot_test_password',
    'database': 'kitraderbot_test',
    'command_timeout': 60
}

@pytest.fixture(scope="function")
async def db_pool():
    """Create test database pool"""
    pool = await asyncpg.create_pool(**TEST_DB_CONFIG)
    
    try:
        # Clean up any existing test data
        async with pool.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS token_prices CASCADE")
            await conn.execute("DROP TABLE IF EXISTS solana_tokens CASCADE")
            await conn.execute('SELECT 1')  # Test the connection
        
        yield pool
    finally:
        await pool.close()

@pytest.fixture(scope="function")
async def birdeye_client():
    """Create Birdeye client"""
    client = BirdeyeClient()
    try:
        yield client
    finally:
        if hasattr(client, 'close'):
            await client.close()

@pytest.fixture(scope="function")
async def token_tracker(db_pool, birdeye_client):
    """Create token tracker instance"""
    tracker = TokenTracker(db_pool, birdeye_client)
    try:
        await tracker.initialize()
        yield tracker
    finally:
        if hasattr(tracker, 'close'):
            await tracker.close()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    force=True
)

@pytest.fixture(autouse=True)
async def cleanup(request):
    """Cleanup all resources after each test"""
    yield
    
    if hasattr(request, 'node'):
        if hasattr(request.node, 'funcargs'):
            token_tracker = request.node.funcargs.get('token_tracker')
            birdeye_client = request.node.funcargs.get('birdeye_client')
            db_pool = request.node.funcargs.get('db_pool')
            
            # Clean up in reverse order
            if token_tracker:
                await token_tracker.close()
            if birdeye_client and hasattr(birdeye_client, 'close'):
                await birdeye_client.close()
            if db_pool:
                await db_pool.close()
