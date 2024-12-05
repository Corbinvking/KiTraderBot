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
import json
import logging
import asyncio
import asyncpg
from telegram.ext import Application, CommandHandler
from scripts.solana.bot_commands import BotCommands
from scripts.solana.trading_engine import TradingEngine
from scripts.solana.token_tracker import TokenTracker
from scripts.solana.birdeye_client import BirdeyeClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    """Handle the /start command"""
    try:
        async with context.bot_data['db_pool'].acquire() as conn:
            user_id = update.effective_user.id
            user = await conn.fetchrow('SELECT * FROM users WHERE telegram_id = $1', user_id)
            
            if not user:
                await conn.execute(
                    'INSERT INTO users (telegram_id, username, role) VALUES ($1, $2, $3)',
                    user_id, update.effective_user.username, 'basic'
                )
                await update.message.reply_text('Welcome! You have been registered as a new user.')
            else:
                await update.message.reply_text(f'Welcome back! Your role is: {user["role"]}')
    except Exception as e:
        logger.error(f"Database error in start_command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def error_handler(update, context):
    """Handle errors"""
    logger.error(f"Error: {context.error}")

def load_config():
    """Load configuration from config.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise

async def init_database(config):
    """Initialize database connection pool"""
    try:
        db_config = config['database']
        pool = await asyncpg.create_pool(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            min_size=5,
            max_size=10
        )
        async with pool.acquire() as conn:
            version = await conn.fetchval('SELECT version()')
            logger.info(f"Connected to PostgreSQL: {version}")
        return pool
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def init_components(application: Application, db_pool):
    """Initialize bot components"""
    try:
        # Initialize BirdEye client
        birdeye_client = BirdeyeClient(application.bot_data['birdeye_api_key'])
        
        # Initialize TokenTracker
        token_tracker = TokenTracker(db_pool, birdeye_client)
        
        # Initialize TradingEngine
        trading_engine = TradingEngine(db_pool, token_tracker, birdeye_client)
        await trading_engine.initialize()
        
        # Initialize BotCommands
        bot_commands = BotCommands(trading_engine, token_tracker)
        
        # Store in application context
        application.bot_data.update({
            'birdeye_client': birdeye_client,
            'token_tracker': token_tracker,
            'trading_engine': trading_engine,
            'bot_commands': bot_commands
        })
        
        return bot_commands
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

async def post_init(application: Application):
    """Post initialization hook"""
    # Initialize database
    config = application.bot_data['config']
    db_pool = await init_database(config)
    application.bot_data['db_pool'] = db_pool
    
    # Initialize components
    bot_commands = await init_components(application, db_pool)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", bot_commands.cmd_start))
    application.add_handler(CommandHandler("commands", bot_commands.cmd_commands))
    application.add_handler(CommandHandler("test_mode", bot_commands.cmd_test_mode))
    
    # Add callback query handler
    from telegram.ext import CallbackQueryHandler
    application.add_handler(CallbackQueryHandler(bot_commands.callback_handler))
    
    logger.info("Bot initialized successfully!")

async def post_shutdown(application: Application):
    """Post shutdown hook"""
    if 'db_pool' in application.bot_data:
        await application.bot_data['db_pool'].close()
        logger.info("Database connection closed")

def main():
    """Main function to run the bot"""
    try:
        # Load config
        config = load_config()
        
        # Create application
        application = (
            Application.builder()
            .token(config['telegram_token'])
            .post_init(post_init)
            .post_shutdown(post_shutdown)
            .build()
        )
        
        # Store config in bot_data
        application.bot_data['config'] = config
        application.bot_data['birdeye_api_key'] = config['birdeye_api_key']

        # Add error handler only (other handlers added in post_init)
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("Starting bot...")
        application.run_polling(drop_pending_updates=True)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

