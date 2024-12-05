"""
Telegram Bot Commands for Solana Trading
======================================

This file handles all Telegram bot interactions including:
1. Main menu and navigation
2. Trading operations (buy/sell)
3. Account management
4. Help and support

File Structure:
- Class initialization
- Main command handlers (/start, /commands, etc.)
- Menu display methods (show_trading_menu, show_account_menu, etc.)
- Action handlers (handle_trade_action, handle_account_action, etc.)
- Helper methods

UI Customization:
- Messages and button texts can be edited directly in the relevant sections
- Each menu has its own method for easy customization
- Error messages are centralized for consistent messaging
"""

import logging
from decimal import Decimal
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes

from .trading_engine import TradingEngine
from .token_tracker import TokenTracker

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
# UI Text Templates
#------------------------------------------------------------------------------

# Main Menu Messages
MESSAGES = {
    'welcome': {
        'title': "🤖 *Welcome to KiTraderBot!*",
        'description': """
Your advanced Solana trading assistant.

*Features:*
• Real-time token tracking
• Position management
• Risk monitoring
• Performance analytics

Select an option to begin:""",
    },
    
    'trading': {
        'menu': """
*Trading Menu*

Select your trading action:
• Buy - Purchase tokens
• Sell - Sell tokens
• Positions - View your holdings
• Wallet - Check your balance""",
        
        'buy_token': """
*Select Token to Buy*

Choose from popular tokens or search:
• SOL - Solana
• USDC - USD Coin
• Search for other tokens""",
        
        'sell_token': """
*Select Token to Sell*

Choose from your holdings:
• View balance
• Recent trades
• Search holdings"""
    },
    
    'account': {
        'menu': """
*Account Menu*

Manage your account:
• View balance
• Check statistics
• Configure settings""",
        
        'balance': """
*Wallet Balance*

💰 Available: {available} SOL
🔒 Locked: {locked} SOL
📈 Total Value: ${total}""",
        
        'stats': """
*Trading Statistics*

📊 Total Trades: {total_trades}
✅ Profitable: {profitable}
❌ Unprofitable: {unprofitable}
📈 ROI: {roi}%"""
    },
    
    'help': {
        'menu': """
*Help & Information*

Get help with:
• Getting started with trading
• Understanding trading features
• Common questions
• Technical support

Select a topic:""",
        
        'getting_started': """
*Getting Started Guide*

1. Connect your wallet
2. Fund your account
3. Start trading

Need help? Contact support."""
    },
    
    'errors': {
        'general': "An error occurred. Please try again.",
        'invalid_action': "Invalid action. Please try again.",
        'not_implemented': "This feature is coming soon...",
        'no_permission': "You don't have permission for this action.",
        'service_unavailable': "Service temporarily unavailable."
    },
    
    'commands': {
        'menu': """
*Available Commands*

📈 *Trading Commands*
/trade - Open trading menu
/price <token> - Get token price
/positions - View open positions
/history - Trading history

💼 *Account Commands*
/wallet - View wallet balance
/settings - Account settings
/stats - Trading statistics

🔔 *Alert Commands*
/alerts - Manage price alerts
/notify - Notification settings""",
    },
}

# Button Labels
BUTTONS = {
    'main_menu': {
        'trading': "🚀 Start Trading",
        'account': "💰 My Account",
        'commands': "📈 Commands",
        'help': "ℹ️ Help & Info"
    },
    
    'trading': {
        'buy': "💵 Buy",
        'sell': "💸 Sell",
        'positions': "📊 My Positions",
        'wallet': "💰 My Wallet"
    },
    
    'account': {
        'balance': "💰 Balance",
        'stats': "📈 Statistics",
        'settings': "⚙️ Settings",
        'history': "📜 History"
    },
    
    'navigation': {
        'back': "🔙 Back",
        'back_main': "🔙 Main Menu",
        'back_trading': "🔙 Back to Trading",
        'back_account': "🔙 Back to Account"
    }
}

# Callback Data - Used for button actions
CALLBACKS = {
    'main': {
        'trading': 'start_trading',
        'account': 'view_account',
        'commands': 'show_commands',
        'help': 'show_help'
    },
    'navigation': {
        'back_main': 'back_main',
        'back_trading': 'back_trading',
        'back_account': 'back_account',
        'back_commands': 'back_commands',
        'back_help': 'back_help'
    },
    'trading': {
        'buy': 'trade_buy',
        'sell': 'trade_sell',
        'positions': 'trade_positions',
        'wallet': 'trade_wallet'
    },
    'account': {
        'balance': 'account_balance',
        'stats': 'account_stats',
        'settings': 'account_settings',
        'history': 'account_history'
    },
    'help': {
        'start': 'help_start',
        'trading': 'help_trading',
        'faq': 'help_faq',
        'support': 'help_support'
    },
    'commands': {
        'trading': 'command_trading',
        'account': 'command_account',
        'alerts': 'command_alerts',
        'help': 'command_help',
        'price_alerts': 'command_price_alerts',
        'notifications': 'command_notifications',
        'active_alerts': 'command_active_alerts',
        'alert_history': 'command_alert_history',
        'positions': 'command_positions',
        'wallet': 'command_wallet',
        'markets': 'command_markets'
    }
}

#------------------------------------------------------------------------------
# Menu Builders - Functions to create consistent menu layouts
#------------------------------------------------------------------------------

def build_main_menu() -> InlineKeyboardMarkup:
    """Build the main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("🚀 Start Trading", callback_data=CALLBACKS['main']['trading']),
            InlineKeyboardButton("💰 My Account", callback_data=CALLBACKS['main']['account'])
        ],
        [
            InlineKeyboardButton("📈 Commands", callback_data=CALLBACKS['main']['commands']),
            InlineKeyboardButton("ℹ️ Help & Info", callback_data=CALLBACKS['main']['help'])
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_trading_menu() -> InlineKeyboardMarkup:
    """Build the trading menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("💵 Buy", callback_data=CALLBACKS['trading']['buy']),
            InlineKeyboardButton("💸 Sell", callback_data=CALLBACKS['trading']['sell'])
        ],
        [
            InlineKeyboardButton("📊 Positions", callback_data=CALLBACKS['trading']['positions']),
            InlineKeyboardButton("💰 Wallet", callback_data=CALLBACKS['trading']['wallet'])
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data=CALLBACKS['navigation']['back_main'])
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_account_menu() -> InlineKeyboardMarkup:
    """Build the account menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(BUTTONS['account']['balance'], callback_data=CALLBACKS['account']['balance']),
            InlineKeyboardButton(BUTTONS['account']['stats'], callback_data=CALLBACKS['account']['stats'])
        ],
        [
            InlineKeyboardButton(BUTTONS['account']['settings'], callback_data=CALLBACKS['account']['settings']),
            InlineKeyboardButton(BUTTONS['account']['history'], callback_data=CALLBACKS['account']['history'])
        ],
        [
            InlineKeyboardButton(BUTTONS['navigation']['back'], callback_data=CALLBACKS['navigation']['back_main'])
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_back_button(callback_data: str) -> InlineKeyboardMarkup:
    """Build a single back button"""
    keyboard = [[
        InlineKeyboardButton(BUTTONS['navigation']['back'], callback_data=callback_data)
    ]]
    return InlineKeyboardMarkup(keyboard)

def build_commands_menu() -> InlineKeyboardMarkup:
    """Build the commands menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📈 Trading", callback_data=CALLBACKS['commands']['trading']),
            InlineKeyboardButton("💼 Account", callback_data=CALLBACKS['commands']['account'])
        ],
        [
            InlineKeyboardButton("🔔 Alerts", callback_data=CALLBACKS['commands']['alerts']),
            InlineKeyboardButton("ℹ️ Help", callback_data=CALLBACKS['commands']['help'])
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data=CALLBACKS['navigation']['back_main'])
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

class BotCommands:
    """
    Main bot command handler class
    
    This class manages all bot interactions and menu navigation.
    Each method represents either a command handler or a menu display.
    """
    
    def __init__(self, trading_engine: TradingEngine, token_tracker: TokenTracker):
        """Initialize bot with required components"""
        self.trading_engine = trading_engine
        self.token_tracker = token_tracker
        self.test_mode = False  # For development testing

    #--------------------------------------------------------------------------
    # Main Command Handlers
    #--------------------------------------------------------------------------
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        try:
            # Add test mode indicator if enabled
            prefix = "[TEST MODE] " if self.test_mode else ""
            
            await update.message.reply_text(
                f"{prefix}{MESSAGES['welcome']['title']}\n\n{MESSAGES['welcome']['description']}",
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text(MESSAGES['errors']['general'])

    async def cmd_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Main command menu with categories"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📈 Trading Commands", callback_data='command_trading'),
                    InlineKeyboardButton("💼 Account Management", callback_data='command_account')
                ],
                [
                    InlineKeyboardButton("🔔 Alerts & Notifications", callback_data='command_alerts'),
                    InlineKeyboardButton("ℹ️ Help Center", callback_data='command_help')
                ],
                [
                    InlineKeyboardButton(BUTTONS['navigation']['back'], callback_data='back_main')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await update.message.reply_text(
                f"{prefix}{MESSAGES['commands']['menu']}",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing commands: {e}")
            await update.message.reply_text(MESSAGES['errors']['general'])

    #--------------------------------------------------------------------------
    # Callback Handlers - Handle button clicks and menu navigation
    #--------------------------------------------------------------------------
    
    async def callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle menu navigation"""
        query = update.callback_query
        await query.answer()
        
        try:
            data = query.data
            prefix = "[TEST MODE] " if self.test_mode else ""
            
            # Main menu navigation
            if data in CALLBACKS['main'].values():
                if data == CALLBACKS['main']['trading']:
                    await self.show_trading_menu(query)
                elif data == CALLBACKS['main']['account']:
                    await self.show_account_menu(query)
                elif data == CALLBACKS['main']['commands']:
                    await self.show_commands_menu(query)
                elif data == CALLBACKS['main']['help']:
                    await self.show_help_menu(query)
                return

            # Back navigation - Handle this first
            if data.startswith('back_'):
                if data == 'back_main':
                    await self.handle_back_to_main(query)
                elif data == 'back_trading':
                    await self.show_trading_menu(query)
                elif data == 'back_account':
                    await self.show_account_menu(query)
                elif data == 'back_commands':
                    await self.show_commands_menu(query)
                elif data == 'back_help':
                    await self.show_help_menu(query)
                return

            # Section handlers
            if data.startswith('trade_'):
                await self.handle_trading_action(query, data.split('_')[1])
                return
            
            if data.startswith('account_'):
                await self.handle_account_action(query, data.split('_')[1])
                return
            
            if data.startswith('command_'):
                await self.handle_command_action(query, data.split('_')[1])
                return
            
            if data.startswith('help_'):
                await self.handle_help_action(query, data.split('_')[1])
                return

            # Unknown callback
            logger.warning(f"Unknown callback data: {data}")
            await query.message.edit_text(
                f"{prefix}{MESSAGES['errors']['invalid_action']}\n\nUse /start to return to main menu.",
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )
                
        except Exception as e:
            logger.error(f"Error in callback: {e}")
            await query.message.edit_text(
                f"{prefix}{MESSAGES['errors']['general']}\n\nUse /start to return to main menu.",
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    async def handle_main_menu_navigation(self, query: CallbackQuery, action: str) -> None:
        """
        Handle navigation to main menu sections
        
        Actions:
        - start_trading: Show trading menu
        - view_account: Show account menu
        - show_commands: Show commands menu
        - show_help: Show help menu
        """
        try:
            if action == CALLBACKS['main']['trading']:
                await self.show_trading_menu(query)
            elif action == CALLBACKS['main']['account']:
                await self.show_account_menu(query)
            elif action == CALLBACKS['main']['commands']:
                await self.show_commands_menu(query)
            elif action == CALLBACKS['main']['help']:
                await self.show_help_menu(query)
            else:
                logger.warning(f"Unknown main menu action: {action}")
                
        except Exception as e:
            logger.error(f"Error in main menu navigation: {e}")
            await query.message.reply_text(MESSAGES['errors']['general'])

    async def handle_token_selection(self, query: CallbackQuery, params: list) -> None:
        """
        Handle token selection for trading
        
        Format: token_<symbol>_<action>
        Example: token_SOL_buy
        """
        try:
            if len(params) < 2:
                await query.message.reply_text(MESSAGES['errors']['invalid_action'])
                return
                
            symbol, action = params
            
            if action not in ['buy', 'sell']:
                await query.message.reply_text(MESSAGES['errors']['invalid_action'])
                return
                
            # Here we'll add token selection logic
            await query.message.edit_text(
                f"Selected {symbol} for {action}. Amount entry coming soon...",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        BUTTONS['navigation']['back_trading'],
                        callback_data=CALLBACKS['navigation']['back_trading']
                    )
                ]])
            )
            
        except Exception as e:
            logger.error(f"Error in token selection: {e}")
            await query.message.reply_text(MESSAGES['errors']['general'])

    #--------------------------------------------------------------------------
    # Menu Display Methods - All menu rendering functions
    #--------------------------------------------------------------------------
    
    async def show_trading_menu(self, query: CallbackQuery) -> None:
        """Display trading interface menu"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💵 Buy", 
                                       callback_data='trade_buy'),
                    InlineKeyboardButton("💸 Sell", 
                                       callback_data='trade_sell')
                ],
                [
                    InlineKeyboardButton("📊 My Positions", 
                                       callback_data='trade_positions'),
                    InlineKeyboardButton("💰 My Wallet", 
                                       callback_data='trade_wallet')
                ],
                [
                    InlineKeyboardButton(BUTTONS['navigation']['back'], 
                                       callback_data='back_main')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Trading Menu*\n\n"
                "Select your trading action:\n"
                "• Buy - Purchase tokens\n"
                "• Sell - Sell tokens\n"
                "• Positions - View your holdings\n"
                "• Wallet - Check your balance",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing trading menu: {e}")
            await query.message.edit_text(
                MESSAGES['errors']['general'],
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    async def show_account_menu(self, query: CallbackQuery) -> None:
        """Display account management menu"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💰 Balance", 
                                       callback_data='account_balance'),
                    InlineKeyboardButton("📈 Statistics", 
                                       callback_data='account_stats')
                ],
                [
                    InlineKeyboardButton("⚙️ Settings", 
                                       callback_data='account_settings'),
                    InlineKeyboardButton("📜 History", 
                                       callback_data='account_history')
                ],
                [
                    InlineKeyboardButton("🔙 Back", 
                                       callback_data='back_main')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Account Menu*\n\n"
                "Manage your account:\n"
                "• View balance\n"
                "• Check statistics\n"
                "• Configure settings\n"
                "• View history",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing account menu: {e}")
            await query.message.edit_text(
                MESSAGES['errors']['general'],
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    async def show_help_menu(self, query: CallbackQuery) -> None:
        """Display help and support menu"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📚 Getting Started", 
                                       callback_data=CALLBACKS['help']['start']),
                    InlineKeyboardButton("📈 Trading Guide", 
                                       callback_data=CALLBACKS['help']['trading'])
                ],
                [
                    InlineKeyboardButton("❓ FAQ", 
                                       callback_data=CALLBACKS['help']['faq']),
                    InlineKeyboardButton("🆘 Support", 
                                       callback_data=CALLBACKS['help']['support'])
                ],
                [
                    InlineKeyboardButton(BUTTONS['navigation']['back'], 
                                       callback_data=CALLBACKS['navigation']['back_main'])
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}{MESSAGES['help']['menu']}",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing help menu: {e}")
            await query.message.edit_text(
                MESSAGES['errors']['general'],
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    # Test mode commands (admin only)
    async def cmd_test_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Toggle test mode for development"""
        if not await self.is_admin(update.effective_user.id):
            await update.message.reply_text("Admin access required.")
            return
            
        self.test_mode = not self.test_mode
        await update.message.reply_text(
            f"Test mode {'enabled' if self.test_mode else 'disabled'}"
        )

    async def is_admin(self, user_id: int) -> bool:
        """Check if user has admin privileges"""
        # Implement admin check logic
        return True  # Temporary for development

    async def show_commands_menu(self, query: CallbackQuery) -> None:
        """Show commands menu"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("📈 Trading Commands", 
                                       callback_data='command_trading'),
                    InlineKeyboardButton("💼 Account Management", 
                                       callback_data='command_account')
                ],
                [
                    InlineKeyboardButton("🔔 Alerts & Notifications", 
                                       callback_data='command_alerts'),
                    InlineKeyboardButton("ℹ️ Help Center", 
                                       callback_data='command_help')
                ],
                [
                    InlineKeyboardButton("�� Back", callback_data='back_main')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}{MESSAGES['commands']['menu']}",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing commands menu: {e}")
            await query.message.edit_text(
                MESSAGES['errors']['general'],
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    #--------------------------------------------------------------------------
    # Action Handlers - Process user actions and interactions
    #--------------------------------------------------------------------------
    
    async def handle_trading_action(self, query: CallbackQuery, action: str) -> None:
        """Handle trading menu actions"""
        try:
            if action == 'buy':
                await self.show_buy_menu(query)
            elif action == 'sell':
                await self.show_sell_menu(query)
            elif action == 'positions':
                await self.show_positions(query)
            elif action == 'wallet':
                await self.show_wallet(query)
            else:
                await query.message.edit_text(
                    MESSAGES['errors']['not_implemented'],
                    parse_mode='Markdown',
                    reply_markup=build_back_button(CALLBACKS['navigation']['back_trading'])
                )
        except Exception as e:
            logger.error(f"Error in trading action: {e}")
            await self.show_trading_menu(query)

    async def handle_account_action(self, query: CallbackQuery, action: str) -> None:
        """
        Process account-related actions
        
        Actions:
        - balance: Show wallet balance
        - stats: Show trading statistics
        - settings: Show account settings
        - history: Show transaction history
        """
        try:
            if action == 'balance':
                # In the future, get real balance from trading engine
                test_data = {
                    'available': '100.00',
                    'locked': '0.00',
                    'total': '10,000.00'
                }
                message = MESSAGES['account']['balance'].format(**test_data)
            elif action == 'stats':
                test_data = {
                    'total_trades': 0,
                    'profitable': 0,
                    'unprofitable': 0,
                    'roi': '0.00'
                }
                message = MESSAGES['account']['stats'].format(**test_data)
            elif action == 'settings':
                message = MESSAGES['errors']['not_implemented']
            else:
                message = MESSAGES['errors']['invalid_action']

            await query.message.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=build_back_button(CALLBACKS['navigation']['back_account'])
            )
        except Exception as e:
            logger.error(f"Error in account action: {e}")
            await query.message.reply_text(MESSAGES['errors']['general'])

    async def handle_help_action(self, query: CallbackQuery, action: str) -> None:
        """Handle help-related actions"""
        try:
            if action == 'start':
                message = (
                    "*Getting Started Guide*\n\n"
                    "1. Connect your wallet\n"
                    "2. Fund your account\n"
                    "3. Start trading\n\n"
                    "Need help? Contact support."
                )
            elif action == 'trading':
                message = (
                    "*Trading Guide*\n\n"
                    "• How to buy tokens\n"
                    "• How to sell tokens\n"
                    "• Managing positions\n"
                    "• Understanding fees"
                )
            elif action == 'faq':
                message = (
                    "*Frequently Asked Questions*\n\n"
                    "• What tokens can I trade?\n"
                    "• How are fees calculated?\n"
                    "• Is my wallet secure?\n"
                    "• How to contact support?"
                )
            elif action == 'support':
                message = (
                    "*Support*\n\n"
                    "Need help? Contact us:\n"
                    "• Email: support@kitraderbot.com\n"
                    "• Telegram: @KiTraderSupport"
                )
            else:
                message = "Invalid help topic"

            await query.message.edit_text(
                message,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='show_help')
                ]])
            )
        except Exception as e:
            logger.error(f"Error in help action: {e}")
            await query.message.reply_text("Error displaying help information")

    async def handle_command_menu_navigation(self, query: CallbackQuery, action: str) -> None:
        """Handle navigation from commands menu"""
        try:
            if action == CALLBACKS['commands']['trading']:
                await self.show_trading_commands(query)
            elif action == CALLBACKS['commands']['account']:
                await self.show_account_commands(query)
            elif action == CALLBACKS['commands']['alerts']:
                await self.show_alert_commands(query)
            elif action == CALLBACKS['commands']['help']:
                await self.show_help_menu(query)
            else:
                # Return to commands menu instead of main menu
                await self.show_commands_menu(query)
                
        except Exception as e:
            logger.error(f"Error in command menu navigation: {e}")
            await self.show_commands_menu(query)  # Return to commands menu on error

    async def show_trading_commands(self, query: CallbackQuery) -> None:
        """Show trading commands submenu"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💵 Buy/Sell", 
                                       callback_data='command_trade_buysell'),
                    InlineKeyboardButton("📊 Positions", 
                                       callback_data='command_trade_positions')
                ],
                [
                    InlineKeyboardButton("💰 Wallet", 
                                       callback_data='command_trade_wallet'),
                    InlineKeyboardButton("📈 Markets", 
                                       callback_data='command_trade_markets')
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Trading Commands*\n\n"
                "Available commands:\n"
                "• /buy <token> <amount> - Buy tokens\n"
                "• /sell <token> <amount> - Sell tokens\n"
                "• /price <token> - Get token price\n"
                "• /positions - View open positions",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing trading commands: {e}")
            await self.show_commands_menu(query)

    async def show_alert_commands(self, query: CallbackQuery) -> None:
        """Show alerts and notifications submenu"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("⚡ Price Alerts", 
                                       callback_data=CALLBACKS['commands']['price_alerts']),
                    InlineKeyboardButton("📱 Notifications", 
                                       callback_data=CALLBACKS['commands']['notifications'])
                ],
                [
                    InlineKeyboardButton("📊 Active Alerts", 
                                       callback_data=CALLBACKS['commands']['active_alerts']),
                    InlineKeyboardButton("📜 Alert History", 
                                       callback_data=CALLBACKS['commands']['alert_history'])
                ],
                [
                    InlineKeyboardButton(BUTTONS['navigation']['back'], 
                                       callback_data=CALLBACKS['navigation']['back_commands'])
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Alert Commands*\n\n"
                "• /alert <token> <price> - Set price alert\n"
                "• /alerts - View active alerts\n"
                "• /notify - Configure notifications\n"
                "• /history - View alert history",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing alert commands: {e}")
            await self.show_commands_menu(query)

    async def handle_command_action(self, query: CallbackQuery, action: str) -> None:
        """Handle command menu actions"""
        try:
            if action.startswith('trade_'):
                sub_action = action.split('_')[1]
                if sub_action == 'buysell':
                    await self.show_buy_menu(query)
                elif sub_action == 'positions':
                    await self.show_positions(query)
                elif sub_action == 'wallet':
                    await self.show_wallet(query)
                elif sub_action == 'markets':
                    await query.message.edit_text(
                        "*Market Overview*\n\nMarket data coming soon...",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                        ]])
                    )
            elif action.startswith('account_'):
                sub_action = action.split('_')[1]
                if sub_action == 'balance':
                    await query.message.edit_text(
                        "*Balance Commands*\n\n"
                        "• /balance - Show current balance\n"
                        "• /deposit - Get deposit address\n"
                        "• /withdraw - Withdraw funds",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                        ]])
                    )
                elif sub_action == 'stats':
                    await query.message.edit_text(
                        "*Statistics Commands*\n\n"
                        "• /stats - View trading stats\n"
                        "• /pnl - Show profit/loss\n"
                        "• /performance - Trading performance",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                        ]])
                    )
                elif sub_action == 'settings':
                    await query.message.edit_text(
                        "*Settings Commands*\n\n"
                        "• /settings - Account settings\n"
                        "• /notifications - Alert settings\n"
                        "• /security - Security settings",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                        ]])
                    )
                elif sub_action == 'history':
                    await query.message.edit_text(
                        "*History Commands*\n\n"
                        "• /history - Transaction history\n"
                        "• /trades - Trading history\n"
                        "• /transfers - Transfer history",
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                        ]])
                    )
            elif action == 'alerts':
                await self.show_alert_commands(query)
            elif action == 'help':
                await self.show_help_menu(query)
            else:
                await query.message.edit_text(
                    MESSAGES['errors']['not_implemented'],
                    parse_mode='Markdown',
                    reply_markup=build_back_button('back_commands')
                )
        except Exception as e:
            logger.error(f"Error in command action: {e}")
            await self.show_commands_menu(query)

    async def handle_back_navigation(self, query: CallbackQuery, data: str) -> None:
        """Handle back button navigation"""
        try:
            if data == 'back_main':
                await self.cmd_start(query, query.message)
            elif data == 'back_trading':
                await self.show_trading_menu(query)
            elif data == 'back_account':
                await self.show_account_menu(query)
            elif data == 'back_commands':
                await self.show_commands_menu(query)
            elif data == 'back_help':
                await self.show_help_menu(query)
            else:
                logger.warning(f"Unknown back navigation: {data}")
                await self.cmd_start(query, query.message)
        except Exception as e:
            logger.error(f"Error in back navigation: {e}")
            await query.message.edit_text(
                MESSAGES['errors']['general'],
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    async def show_buy_menu(self, query: CallbackQuery) -> None:
        """Show token selection for buying"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("SOL", callback_data='token_SOL_buy'),
                    InlineKeyboardButton("USDC", callback_data='token_USDC_buy')
                ],
                [
                    InlineKeyboardButton("Search Token", callback_data='token_search_buy'),
                    InlineKeyboardButton("Recent", callback_data='token_recent_buy')
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data='back_trading')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Select Token to Buy*\n\n"
                "Choose from popular tokens or search:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing buy menu: {e}")
            await self.show_trading_menu(query)

    async def show_sell_menu(self, query: CallbackQuery) -> None:
        """Show token selection for selling"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("SOL", callback_data='token_SOL_sell'),
                    InlineKeyboardButton("USDC", callback_data='token_USDC_sell')
                ],
                [
                    InlineKeyboardButton("Search Token", callback_data='token_search_sell'),
                    InlineKeyboardButton("Recent", callback_data='token_recent_sell')
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data='back_trading')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Select Token to Sell*\n\n"
                "Choose from your holdings:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing sell menu: {e}")
            await self.show_trading_menu(query)

    async def show_positions(self, query: CallbackQuery) -> None:
        """Show user's trading positions"""
        try:
            # This will be replaced with actual position data from trading engine
            keyboard = [
                [
                    InlineKeyboardButton("Open Positions", callback_data='trade_open_positions'),
                    InlineKeyboardButton("Closed Positions", callback_data='trade_closed_positions')
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data='back_trading')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Your Trading Positions*\n\n"
                "No open positions\n\n"
                "Select an option to view more details:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing positions: {e}")
            await self.show_trading_menu(query)

    async def show_wallet(self, query: CallbackQuery) -> None:
        """Show wallet balance and options"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("Deposit", callback_data='trade_deposit'),
                    InlineKeyboardButton("Withdraw", callback_data='trade_withdraw')
                ],
                [
                    InlineKeyboardButton("Transaction History", callback_data='trade_history')
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data='back_trading')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Wallet Balance*\n\n"
                "💰 Available: 100.00 SOL\n"
                "🔒 Locked: 0.00 SOL\n"
                "📈 Total Value: $10,000.00\n\n"
                "Select an option:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error showing wallet: {e}")
            await self.show_trading_menu(query)

    async def handle_back_to_main(self, query: CallbackQuery) -> None:
        """Special handler for returning to main menu"""
        try:
            keyboard = build_main_menu()
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}{MESSAGES['welcome']['title']}\n\n{MESSAGES['welcome']['description']}",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error returning to main menu: {e}")
            await query.message.edit_text(
                MESSAGES['errors']['general'],
                parse_mode='Markdown',
                reply_markup=build_main_menu()
            )

    async def show_account_commands(self, query: CallbackQuery) -> None:
        """Show account management commands"""
        try:
            keyboard = [
                [
                    InlineKeyboardButton("💰 Balance Commands", 
                                       callback_data='command_account_balance'),
                    InlineKeyboardButton("📊 Stats Commands", 
                                       callback_data='command_account_stats')
                ],
                [
                    InlineKeyboardButton("⚙️ Settings Commands", 
                                       callback_data='command_account_settings'),
                    InlineKeyboardButton("📜 History Commands", 
                                       callback_data='command_account_history')
                ],
                [
                    InlineKeyboardButton("🔙 Back", callback_data='back_commands')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            prefix = "[TEST MODE] " if self.test_mode else ""
            await query.message.edit_text(
                f"{prefix}*Account Management Commands*\n\n"
                "Available commands:\n"
                "• /balance - Check your wallet balance\n"
                "• /stats - View your trading statistics\n"
                "• /settings - Configure account settings\n"
                "• /history - View transaction history",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing account commands: {e}")
            await self.show_commands_menu(query)

