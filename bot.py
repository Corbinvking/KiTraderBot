#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
KiTraderBot - Telegram Trading Bot
=================================

This bot provides trading functionality through Telegram, supporting:
- User management (admin, premium, basic users)
- Solana token tracking and trading
- Simulated trading operations
- Price monitoring and alerts
"""

import os
import sys
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/kitraderbot/bot.log'),
        logging.FileHandler('/var/log/kitraderbot/error.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from scripts.user_management import UserManager, UserRole
from scripts.solana import SolanaRPCManager, TokenTracker, TradingEngine
from scripts.solana.bot_commands import TradingCommands

class TradingBot:
    def __init__(self):
        try:
            # Load token
            token_path = os.path.join(project_root, "tokens/telegram")
            with open(token_path, 'r') as f:
                self.token = f.read().strip()
                
            self.user_manager = UserManager()
            self.rpc_manager = SolanaRPCManager()
            self.token_tracker = None
            self.trading_engine = None
            self.trading_commands = None
            self.db_pool = None
            self.application = None
            logger.info("Bot initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            raise

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        try:
            user = update.effective_user
            # Initialize user in database
            await self.user_manager.add_user(
                user_id=user.id,
                username=user.username or user.first_name,
                role=UserRole.BASIC
            )
            
            message = (
                f"Hi {user.first_name}! Welcome to Solana Trading Bot!\n\n"
                f"This bot allows you to:\n"
                f"• Trade Solana tokens\n"
                f"• Track positions\n"
                f"• Monitor prices\n\n"
                f"Use /help to see available commands."
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("💰 Open Wallet", callback_data='view_wallet'),
                    InlineKeyboardButton("📈 Start Trading", callback_data='open_position')
                ],
                [
                    InlineKeyboardButton("❓ Help", callback_data='show_help'),
                    InlineKeyboardButton("⚙️ Settings", callback_data='show_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            logger.info(f"Start command sent to user {user.id}")
        except Exception as e:
            logger.error(f"Error in start command: {e}", exc_info=True)
            await update.message.reply_text(
                "Welcome! Use /help to see available commands.\n\n"
                "If you experience any issues, please try again."
            )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        try:
            help_text = (
                "*Available Commands*\n\n"
                "💰 *Wallet Commands:*\n"
                "`/wallet` - Show your wallet balance and positions\n"
                "`/positions` - List your open positions\n"
                "`/positions closed` - List your closed positions\n\n"
                "📈 *Trading Commands:*\n"
                "`/open <token_address> <size_sol> <type>` - Open a new position\n"
                "`/close <position_id>` - Close an existing position\n"
                "`/price <token_address>` - Get current token price\n"
                "`/info <token_address>` - Get token information\n\n"
                "⚙️ *Settings:*\n"
                "`/settings` - View your account settings"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("💰 Wallet", callback_data='view_wallet'),
                    InlineKeyboardButton("📊 Positions", callback_data='view_positions')
                ],
                [
                    InlineKeyboardButton("📈 Trade", callback_data='open_position'),
                    InlineKeyboardButton("⚙️ Settings", callback_data='show_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            logger.info(f"Help command sent to user {update.effective_user.id}")
        except Exception as e:
            logger.error(f"Error in help command: {e}", exc_info=True)
            await update.message.reply_text("Error displaying help message. Please try again.")

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle unknown commands."""
        try:
            await update.message.reply_text(
                f"Sorry, I didn't understand command: {update.message.text}\n"
                f"Use /help to see available commands."
            )
            logger.info(f"Unknown command from user {update.effective_user.id}: {update.message.text}")
        except Exception as e:
            logger.error(f"Error handling unknown command: {e}")

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors."""
        logger.error(f"Exception while handling an update: {context.error}")
        if update and isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, an error occurred while processing your request. Please try again."
            )

    async def initialize(self) -> None:
        """Initialize bot components"""
        try:
            logger.info("Starting initialization...")
            
            # Initialize database
            self.db_pool = await self.user_manager.init_db()
            logger.info("Database initialized")
            
            # Initialize Solana components
            self.token_tracker = TokenTracker(self.rpc_manager, self.db_pool)
            self.trading_engine = TradingEngine(self.db_pool, self.token_tracker, self.user_manager)
            self.trading_commands = TradingCommands(self.trading_engine, self.token_tracker)
            logger.info("Solana components initialized")
            
            # Create the Application
            self.application = Application.builder().token(self.token).build()
            logger.info("Application created")

            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("help", self.help))
            
            # Setup trading commands
            self.application.add_handler(CommandHandler("wallet", self.trading_commands.cmd_wallet))
            self.application.add_handler(CommandHandler("open", self.trading_commands.cmd_open_position))
            self.application.add_handler(CommandHandler("close", self.trading_commands.cmd_close_position))
            self.application.add_handler(CommandHandler("positions", self.trading_commands.cmd_positions))
            self.application.add_handler(CommandHandler("info", self.trading_commands.cmd_info))
            self.application.add_handler(CommandHandler("price", self.trading_commands.cmd_price))
            self.application.add_handler(CommandHandler("settings", self.trading_commands.cmd_settings))
            
            # Add callback query handler
            self.application.add_handler(CallbackQueryHandler(self.trading_commands.callback_handler))
            
            # Unknown command handler
            self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown))
            
            # Error handler
            self.application.add_error_handler(self.error_handler)
            
            logger.info("Bot components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot components: {e}")
            raise

    async def cleanup(self) -> None:
        """Cleanup resources"""
        logger.info("Starting cleanup...")
        try:
            if self.db_pool:
                await self.db_pool.close()
                logger.info("Database connection closed")
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Application stopped")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def run(self) -> None:
        """Run the bot."""
        try:
            # Initialize event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize components
            loop.run_until_complete(self.initialize())
            
            logger.info("Starting bot...")
            
            # Run the application
            self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                close_loop=False
            )
            
        except Exception as e:
            logger.error(f"Error running bot: {e}", exc_info=True)
            raise
        finally:
            try:
                # Cleanup
                if 'loop' in locals():
                    loop.run_until_complete(self.cleanup())
                    loop.close()
                logger.info("Bot shutdown complete")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}", exc_info=True)

def main() -> None:
    """Start the bot."""
    try:
        logger.info("Initializing bot...")
        bot = TradingBot()
        bot.run()
    except Exception as e:
        logger.error(f"Bot failed to start: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
