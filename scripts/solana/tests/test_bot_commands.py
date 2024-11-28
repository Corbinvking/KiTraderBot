import asyncio
import logging
import sys
import os
import asyncpg
from unittest.mock import MagicMock, AsyncMock
from decimal import Decimal
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from telegram import Update, User, Message, Chat
from telegram.ext import CallbackContext
from scripts.solana.bot_commands import TradingCommands
from scripts.solana.trading_engine import TradingEngine
from scripts.solana.token_tracker import TokenTracker
from scripts.solana.rpc_manager import SolanaRPCManager

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

async def setup_test_environment():
    """Setup test environment with mocked objects"""
    try:
        # Create mock update
        update = MagicMock(spec=Update)
        update.effective_user = MagicMock(spec=User)
        update.effective_user.id = TEST_USER_ID
        update.effective_user.first_name = "Test User"
        update.message = MagicMock(spec=Message)
        update.message.chat = MagicMock(spec=Chat)
        update.message.chat.id = TEST_USER_ID
        
        # Create mock context
        context = MagicMock(spec=CallbackContext)
        
        # Setup database pool
        db_pool = await setup_database()
        if not db_pool:
            raise Exception("Failed to setup database connection")
            
        # Ensure test user exists
        test_user = await ensure_test_user(db_pool)
        if not test_user:
            raise Exception("Failed to create test user")
        
        # Setup components
        rpc = SolanaRPCManager()
        token_tracker = TokenTracker(rpc, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)
        commands = TradingCommands(trading_engine, token_tracker)
        
        return update, context, commands, db_pool
        
    except Exception as e:
        logger.error(f"Error setting up test environment: {e}")
        if 'db_pool' in locals():
            await db_pool.close()
        raise

async def test_wallet_command():
    """Test wallet command functionality"""
    db_pool = None
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        update.message.reply_text = AsyncMock()
        
        # Test wallet command
        await commands.cmd_wallet(update, context)
        
        # Verify response
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]  # Get first positional argument
        assert "Wallet Balance" in call_args, "Wallet balance not shown"
        logger.info(f"Wallet response: {call_args}")
        logger.info("Wallet command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Wallet command test failed: {e}")
        return False
    finally:
        if db_pool:
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def test_open_position_command():
    """Test position opening command"""
    db_pool = None
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        update.message.reply_text = AsyncMock()
        
        # Setup command arguments
        context.args = [TEST_TOKENS['USDC'], '10.0', 'long']
        
        # Test open position command
        await commands.cmd_open_position(update, context)
        
        # Verify response
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Position opened successfully" in call_args, "Position not opened"
        logger.info(f"Position response: {call_args}")
        logger.info("Open position command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Open position command test failed: {e}")
        return False
    finally:
        if db_pool:
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def test_positions_command():
    """Test positions listing command"""
    db_pool = None
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        update.message.reply_text = AsyncMock()
        
        # Test positions command
        await commands.cmd_positions(update, context)
        
        # Verify response
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args[0][0]
        assert "Positions" in call_args, "Positions not listed"
        logger.info(f"Positions response: {call_args}")
        logger.info("Positions command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Positions command test failed: {e}")
        return False
    finally:
        if db_pool:
            await cleanup_test_data(db_pool)
            await db_pool.close()

async def run_all_tests():
    """Run all bot command tests"""
    logger.info("Starting Bot Commands tests...")
    
    # Test wallet functionality
    wallet_success = await test_wallet_command()
    if wallet_success:
        logger.info("Wallet command tests passed")
        
        # Test position operations
        position_success = await test_open_position_command()
        if position_success:
            logger.info("Position command tests passed")
            
            positions_success = await test_positions_command()
            if positions_success:
                logger.info("Positions listing tests passed")
    
    logger.info("All Bot Commands tests completed")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
