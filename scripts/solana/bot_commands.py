"""
Telegram Bot Commands for Solana Trading
======================================

This module implements the Telegram bot commands for:
- Wallet management
- Position opening/closing
- Position monitoring
- Token information
"""

import logging
from decimal import Decimal
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, CallbackContext, CallbackQueryHandler,
    MessageHandler, filters
)
from .trading_engine import TradingEngine
from .token_tracker import TokenTracker

logger = logging.getLogger(__name__)

class TradingCommands:
    """Handles all trading-related bot commands"""
    
    def __init__(self, trading_engine: TradingEngine, token_tracker: TokenTracker):
        self.trading_engine = trading_engine
        self.token_tracker = token_tracker
        self.user_manager = trading_engine.user_manager

    async def cmd_help(self, update: Update, context: CallbackContext) -> None:
        """Show help information"""
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
            logger.error(f"Error in help command: {e}")
            await update.message.reply_text("Error displaying help message. Please try again.")

    async def cmd_wallet(self, update: Update, context: CallbackContext) -> None:
        """Show user's wallet balance and positions"""
        try:
            user_id = update.effective_user.id
            wallet = await self.trading_engine.get_wallet(user_id)
            
            if not wallet:
                await update.message.reply_text("Error accessing wallet.")
                return
            
            # Get open positions
            positions = await self.trading_engine.get_positions(user_id, status='open')
            
            # Format wallet info
            message = (
                f"💰 *Wallet Balance*: {wallet['balance']:.4f} SOL\n\n"
                f"📊 *Open Positions*: {len(positions)}\n"
            )
            
            if positions:
                message += "\n*Current Positions:*\n"
                for pos in positions:
                    pnl = pos['pnl_sol'] if 'pnl_sol' in pos else Decimal('0')
                    message += (
                        f"ID: `{pos['position_id']}`\n"
                        f"Token: {pos['symbol']}\n"
                        f"Size: {pos['size_sol']:.4f} SOL\n"
                        f"PnL: {pnl:.4f} SOL\n"
                        f"Type: {pos['position_type']}\n\n"
                    )
            
            keyboard = [
                [
                    InlineKeyboardButton("📈 Open Position", callback_data='open_position'),
                    InlineKeyboardButton("📊 View Positions", callback_data='view_positions')
                ],
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data='refresh_wallet')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in wallet command: {e}")
            await update.message.reply_text("Error processing wallet command.")

    async def cmd_open_position(self, update: Update, context: CallbackContext) -> None:
        """Open a new trading position"""
        try:
            args = context.args
            if len(args) < 3:
                message = (
                    "*Open New Position*\n\n"
                    "Use the command format:\n"
                    "`/open <token_address> <size_sol> <type>`\n\n"
                    "Example:\n"
                    "`/open EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 10 long`\n\n"
                    "*Position Types:*\n"
                    "• long - Buy position\n"
                    "• short - Sell position"
                )
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            token_address = args[0]
            size_sol = Decimal(args[1])
            position_type = args[2].lower()
            
            if position_type not in ['long', 'short']:
                await update.message.reply_text("Position type must be 'long' or 'short'")
                return
            
            # Open position
            position = await self.trading_engine.open_position(
                user_id=update.effective_user.id,
                token_address=token_address,
                size_sol=size_sol,
                position_type=position_type
            )
            
            if position:
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "❌ Close Position", 
                            callback_data=f"close_{position['position_id']}"
                        ),
                        InlineKeyboardButton(
                            "�� View Details", 
                            callback_data=f"details_{position['position_id']}"
                        )
                    ],
                    [
                        InlineKeyboardButton("📈 Open Another", callback_data='open_position'),
                        InlineKeyboardButton("💰 View Wallet", callback_data='view_wallet')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"Position opened successfully!\n"
                    f"ID: `{position['position_id']}`\n"
                    f"Entry Price: {position['entry_price']:.4f} SOL\n"
                    f"Size: {position['size']:.4f} SOL\n"
                    f"Type: {position['type']}",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("Failed to open position.")
                
        except ValueError as e:
            await update.message.reply_text(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error opening position: {e}")
            await update.message.reply_text("Error processing open position command.")

    async def cmd_close_position(self, update: Update, context: CallbackContext) -> None:
        """Close an existing position"""
        try:
            if not context.args:
                message = (
                    "*Close Position*\n\n"
                    "Use the command format:\n"
                    "`/close <position_id>`\n\n"
                    "Example:\n"
                    "`/close 123`\n\n"
                    "Use /positions to see your open positions."
                )
                await update.message.reply_text(message, parse_mode='Markdown')
                return
            
            position_id = int(context.args[0])
            
            # Close position
            result = await self.trading_engine.close_position(position_id)
            
            if result:
                keyboard = [
                    [
                        InlineKeyboardButton("📈 Open New Position", callback_data='open_position'),
                        InlineKeyboardButton("📊 View History", callback_data='view_history')
                    ],
                    [
                        InlineKeyboardButton("💰 View Wallet", callback_data='view_wallet')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"Position closed successfully!\n"
                    f"Exit Price: {result['exit_price']:.4f} SOL\n"
                    f"PnL: {result['pnl']:.4f} SOL",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text("Failed to close position.")
                
        except ValueError as e:
            await update.message.reply_text(f"Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            await update.message.reply_text("Error processing close position command.")

    async def cmd_positions(self, update: Update, context: CallbackContext) -> None:
        """Show user's positions"""
        try:
            status = 'open'
            if context.args and context.args[0].lower() in ['open', 'closed']:
                status = context.args[0].lower()
            
            positions = await self.trading_engine.get_positions(
                update.effective_user.id, 
                status=status
            )
            
            if not positions:
                keyboard = [
                    [
                        InlineKeyboardButton("📈 Open Position", callback_data='open_position'),
                        InlineKeyboardButton("💰 View Wallet", callback_data='view_wallet')
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"No {status} positions found.",
                    reply_markup=reply_markup
                )
                return
            
            message = f"*{status.title()} Positions:*\n\n"
            for pos in positions:
                pnl = pos['pnl_sol'] if 'pnl_sol' in pos else Decimal('0')
                message += (
                    f"ID: `{pos['position_id']}`\n"
                    f"Token: {pos['symbol']}\n"
                    f"Size: {pos['size_sol']:.4f} SOL\n"
                    f"Entry: {pos['entry_price_sol']:.4f} SOL\n"
                    f"PnL: {pnl:.4f} SOL\n"
                    f"Type: {pos['position_type']}\n\n"
                )
            
            keyboard = []
            if status == 'open':
                keyboard.append([
                    InlineKeyboardButton("❌ Close All", callback_data='close_all'),
                    InlineKeyboardButton("📊 View Closed", callback_data='view_closed')
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton("📈 Open New", callback_data='open_position'),
                    InlineKeyboardButton("📊 View Open", callback_data='view_open')
                ])
            
            keyboard.append([
                InlineKeyboardButton("🔄 Refresh", callback_data=f'refresh_{status}'),
                InlineKeyboardButton("💰 View Wallet", callback_data='view_wallet')
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in positions command: {e}")
            await update.message.reply_text("Error retrieving positions.")

    async def cmd_info(self, update: Update, context: CallbackContext) -> None:
        """Get token information"""
        try:
            args = context.args
            if not args:
                message = (
                    "*Token Information*\n\n"
                    "Use the command format:\n"
                    "`/info <token_address>`\n\n"
                    "Example:\n"
                    "`/info EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`"
                )
                await update.message.reply_text(message, parse_mode='Markdown')
                return

            token_address = args[0]
            token_info = await self.token_tracker.get_token_info(token_address)
            
            if not token_info:
                await update.message.reply_text("Token not found.")
                return
            
            # Get current price
            price = await self.token_tracker.get_latest_price(token_address)
            
            message = (
                f"*Token Information*\n\n"
                f"Address: `{token_info['token_address']}`\n"
                f"Symbol: {token_info['symbol'] or 'Unknown'}\n"
                f"Name: {token_info['name'] or 'Unknown'}\n"
                f"Price: {price:.4f} SOL\n"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📈 Trade", callback_data=f'trade_{token_address}'),
                    InlineKeyboardButton("🔄 Refresh", callback_data=f'refresh_info_{token_address}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await update.message.reply_text("Error getting token information.")

    async def cmd_settings(self, update: Update, context: CallbackContext) -> None:
        """View and modify user settings"""
        try:
            user_id = update.effective_user.id
            user = await self.user_manager.get_user(user_id)
            
            if not user:
                await update.message.reply_text("User not found.")
                return
            
            message = (
                f"*User Settings*\n\n"
                f"User ID: `{user_id}`\n"
                f"Username: {user['username']}\n"
                f"Role: {user['role']}\n"
                f"Created: {user['created_at']}\n\n"
                f"*Trading Settings*\n"
                f"Max Position Size: {self.trading_engine.position_limits[user['role']]} SOL\n"
                f"Max Leverage: 1.0x\n"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Trading History", callback_data='view_history'),
                    InlineKeyboardButton("⚙️ Preferences", callback_data='edit_preferences')
                ],
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data='refresh_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in settings command: {e}")
            await update.message.reply_text("Error accessing settings.")

    async def cmd_price(self, update: Update, context: CallbackContext) -> None:
        """Get current token price"""
        try:
            args = context.args
            if not args:
                message = (
                    "*Token Price*\n\n"
                    "Use the command format:\n"
                    "`/price <token_address>`\n\n"
                    "Example:\n"
                    "`/price EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`"
                )
                await update.message.reply_text(message, parse_mode='Markdown')
                return

            token_address = args[0]
            token_info = await self.token_tracker.get_token_info(token_address)
            
            if not token_info:
                await update.message.reply_text("Token not found.")
                return
            
            # Get current price
            price = await self.token_tracker.get_latest_price(token_address)
            
            message = (
                f"*Current Price*\n\n"
                f"Token: {token_info['symbol'] or token_address}\n"
                f"Price: {price:.4f} SOL\n"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📈 Trade", callback_data=f'trade_{token_address}'),
                    InlineKeyboardButton("ℹ️ Info", callback_data=f'info_{token_address}')
                ],
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data=f'refresh_price_{token_address}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error in price command: {e}")
            await update.message.reply_text("Error getting token price.")

    async def callback_handler(self, update: Update, context: CallbackContext) -> None:
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        try:
            data = query.data
            
            if data == 'view_wallet':
                await self.cmd_wallet(update, context)
            elif data == 'view_positions':
                await self.cmd_positions(update, context)
            elif data == 'open_position':
                await self.show_open_position_form(query)
            elif data.startswith('close_'):
                position_id = int(data.split('_')[1])
                context.args = [str(position_id)]
                await self.cmd_close_position(update, context)
            elif data == 'refresh_wallet':
                await self.cmd_wallet(update, context)
            elif data.startswith('refresh_'):
                if data.startswith('refresh_info_'):
                    token_address = data.split('_')[2]
                    context.args = [token_address]
                    await self.cmd_info(update, context)
                elif data.startswith('refresh_price_'):
                    token_address = data.split('_')[2]
                    context.args = [token_address]
                    await self.cmd_price(update, context)
                else:
                    status = data.split('_')[1]
                    context.args = [status]
                    await self.cmd_positions(update, context)
            elif data == 'view_closed':
                context.args = ['closed']
                await self.cmd_positions(update, context)
            elif data == 'view_open':
                context.args = ['open']
                await self.cmd_positions(update, context)
            elif data.startswith('trade_'):
                token_address = data.split('_')[1]
                await self.show_trade_form(query, token_address)
            elif data.startswith('info_'):
                token_address = data.split('_')[1]
                context.args = [token_address]
                await self.cmd_info(update, context)
            elif data == 'show_help':
                await self.cmd_help(update, context)
            elif data == 'show_settings':
                await self.cmd_settings(update, context)
            elif data == 'start_trading':
                await self.show_open_position_form(query)
            elif data == 'edit_preferences':
                await self.show_preferences_form(query)
            elif data == 'view_history':
                context.args = ['closed']
                await self.cmd_positions(update, context)
            
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.message.reply_text("Error processing your request.")

    async def show_open_position_form(self, query) -> None:
        """Show form for opening a new position"""
        try:
            message = (
                "*Open New Position*\n\n"
                "Use the command format:\n"
                "`/open <token_address> <size_sol> <type>`\n\n"
                "Example:\n"
                "`/open EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v 10 long`\n\n"
                "*Position Types:*\n"
                "• long - Buy position\n"
                "• short - Sell position"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("💰 View Wallet", callback_data='view_wallet'),
                    InlineKeyboardButton("📊 View Positions", callback_data='view_positions')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing position form: {e}")
            await query.message.reply_text("Error displaying form.")

    async def show_trade_form(self, query, token_address: str) -> None:
        """Show form for trading a specific token"""
        try:
            token_info = await self.token_tracker.get_token_info(token_address)
            price = await self.token_tracker.get_latest_price(token_address)
            
            message = (
                f"*Trade {token_info['symbol'] or 'Token'}*\n\n"
                f"Current Price: {price:.4f} SOL\n\n"
                f"To open a position:\n"
                f"`/open {token_address} <size_sol> <type>`\n\n"
                f"Example for 10 SOL long position:\n"
                f"`/open {token_address} 10 long`"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("Long", callback_data=f'preset_long_{token_address}'),
                    InlineKeyboardButton("Short", callback_data=f'preset_short_{token_address}')
                ],
                [
                    InlineKeyboardButton("🔄 Refresh Price", callback_data=f'refresh_price_{token_address}'),
                    InlineKeyboardButton("ℹ️ Token Info", callback_data=f'info_{token_address}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing trade form: {e}")
            await query.message.reply_text("Error displaying trade form.")

    async def show_preferences_form(self, query) -> None:
        """Show user preferences form"""
        try:
            message = (
                "*User Preferences*\n\n"
                "Coming soon:\n"
                "• Default position size\n"
                "• Risk limits\n"
                "• Notifications\n"
                "• Display settings"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("🔙 Back to Settings", callback_data='show_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.reply_text(
                message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing preferences form: {e}")
            await query.message.reply_text("Error displaying preferences.")
