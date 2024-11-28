"""
Integration Tests for KiTraderBot
===============================

Tests the complete flow from bot commands to trading engine
"""

import asyncio
import logging
import sys
import os
from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from scripts.solana import SolanaRPCManager, TokenTracker, TradingEngine

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from telegram import Update, User, Message, Chat
from telegram.ext import CallbackContext

from scripts.solana.rpc_manager import SolanaRPCManager
from scripts.solana.token_tracker import TokenTracker
from scripts.solana.trading_engine import TradingEngine
from scripts.solana.bot_commands import TradingCommands
from scripts.user_management import UserManager, UserRole

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

async def setup_test_environment():
    """Setup test environment"""
    try:
        # Initialize components
        user_manager = UserManager()
        db_pool = await user_manager.init_db()
        
        rpc_manager = SolanaRPCManager()
        token_tracker = TokenTracker(rpc_manager, db_pool)
        trading_engine = TradingEngine(db_pool, token_tracker)
        trading_commands = TradingCommands(trading_engine, token_tracker)
        
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
        
        return update, context, trading_commands, db_pool
        
    except Exception as e:
        logger.error(f"Error setting up test environment: {e}")
        raise

async def test_wallet_command():
    """Test wallet command"""
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        messages = []
        update.message.reply_text = AsyncMock(side_effect=messages.append)
        
        # Test wallet command
        await commands.cmd_wallet(update, context)
        
        # Verify response
        assert len(messages) > 0, "No response from wallet command"
        wallet_message = messages[0]
        assert "Wallet Balance" in wallet_message, "Wallet balance not shown"
        logger.info(f"Wallet response: {wallet_message}")
        logger.info("Wallet command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Wallet command test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await db_pool.close()

async def test_open_position_command():
    """Test position opening command"""
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        messages = []
        update.message.reply_text = AsyncMock(side_effect=messages.append)
        
        # Setup command arguments
        context.args = [TEST_TOKENS['USDC'], '10.0', 'long']
        
        # Test open position command
        await commands.cmd_open_position(update, context)
        
        # Verify response
        assert len(messages) > 0, "No response from open position command"
        position_message = messages[0]
        assert "Position opened successfully" in position_message, "Position not opened"
        logger.info(f"Position response: {position_message}")
        logger.info("Open position command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Open position command test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await db_pool.close()

async def test_positions_command():
    """Test positions listing command"""
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        messages = []
        update.message.reply_text = AsyncMock(side_effect=messages.append)
        
        # Test positions command
        await commands.cmd_positions(update, context)
        
        # Verify response
        assert len(messages) > 0, "No response from positions command"
        positions_message = messages[0]
        assert "Positions" in positions_message, "Positions not listed"
        logger.info(f"Positions response: {positions_message}")
        logger.info("Positions command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Positions command test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await db_pool.close()

async def test_help_command():
    """Test help command"""
    try:
        update, context, commands, db_pool = await setup_test_environment()
        
        # Mock reply method
        messages = []
        update.message.reply_text = AsyncMock(side_effect=messages.append)
        
        # Test help command
        await commands.cmd_help(update, context)
        
        # Verify response
        assert len(messages) > 0, "No response from help command"
        help_message = messages[0]
        assert "Available Commands" in help_message, "Help message not shown"
        logger.info(f"Help response: {help_message}")
        logger.info("Help command test passed")
        return True
        
    except Exception as e:
        logger.error(f"Help command test failed: {e}")
        return False
    finally:
        if 'db_pool' in locals():
            await db_pool.close()

async def run_all_tests():
    """Run all integration tests"""
    logger.info("Starting integration tests...")
    
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
                logger.info("Positions command tests passed")
                
                help_success = await test_help_command()
                if help_success:
                    logger.info("Help command tests passed")
    
    logger.info("All integration tests completed")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
