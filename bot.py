#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

"""
KiTraderBot - Telegram Trading Bot
=================================

This bot provides trading functionality through Telegram, supporting:
- User management (admin, premium, basic users)
- Trading operations (buy, sell, account management)
- Auto-trading subscriptions
- Price alerts and monitoring
"""

#------------------------------------------------------------------------------
# IMPORTS
#------------------------------------------------------------------------------

# Standard library imports
import pytz
import logging
import json
from os import path
from datetime import datetime, timedelta

# Third-party imports
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from telegram.error import Unauthorized, TimedOut

# Local imports
import scripts.gmail as alerts
import scripts.bitstamp as trading
from scripts.user_management import UserManager, UserRole

#------------------------------------------------------------------------------
# CONFIGURATION AND INITIALIZATION
#------------------------------------------------------------------------------

# Load Telegram token
try:
    with open("tokens/telegram", 'r') as telegram_token:
        TELEGRAM_API_TOKEN = telegram_token.read().strip()
except FileNotFoundError:
    print("tokens/telegram not found!")
    exit(1)

# Load superusers
try:
    with open("superusers", 'r') as users:
        SUPERUSERS = set(users.read().split('\n'))
except FileNotFoundError:
    SUPERUSERS = set()

# Initialize user manager
user_manager = UserManager()

# Initialize bot and get name
bot = Bot(TELEGRAM_API_TOKEN)
NAME = bot.get_me().first_name

#------------------------------------------------------------------------------
# UTILITY FUNCTIONS
#------------------------------------------------------------------------------

def debug(update, answer):
    """Log debug information about user interactions."""
    user = update.message.from_user
    logging.info(f"DEBUG - User Info: username={user.username}, id={user.id}, first_name={user.first_name}")
    logging.info(f"{datetime.now()} - {user.username} ({update.message.chat_id}): {update.message.text}\n{answer}\n")

def reply(update, text):
    """Send a reply to the user and log it."""
    debug(update, text)
    update.message.reply_text(text)

def is_superuser(update):
    """Check if the user is a superuser."""
    return str(update.message.from_user.id) in SUPERUSERS

#------------------------------------------------------------------------------
# DECORATORS
#------------------------------------------------------------------------------

def restricted(handler, required_role=UserRole.BASIC):
    """Restrict command access based on user role."""
    def response(update, context, **kwargs):
        user_id = str(update.message.from_user.id)
        logging.info(f"DEBUG - Access Check: user_id={user_id}")
        logging.info(f"DEBUG - Current users: {user_manager.users}")
        if user_manager.is_authorized(user_id, required_role):
            handler(update, context, **kwargs)
        else:
            reply(update, "You don't have permission to use this command.")
    return response

def wrap(f):
    """Wrap a function to handle Telegram updates."""
    def response(update, context):
        reply(update, f())
    return response

def send(f, args=False):
    """Wrap a function to handle sending messages."""
    if args:
        def response(update, context):
            reply(update, f(update.message.from_user.username, ' '.join(context.args)))
    else:
        def response(update, context):
            reply(update, f(update.message.from_user.username))
    return response

def account(f):
    """Wrap a function to handle account operations."""
    def response(update, context):
        reply(update, f(NAME, update.message.from_user.username, is_superuser(update), ' '.join(context.args)))
    return response

#------------------------------------------------------------------------------
# SUBSCRIPTION MANAGEMENT
#------------------------------------------------------------------------------

SUBSCRIPTIONS = dict()  # users to job
UPDATE_ALERTS_SECONDS = 900

lastUpdate = alerts.get_last_alert_date() or datetime.now(pytz.UTC) - timedelta(hours=24)
newAlerts = []
updating = False

def update_alerts(force=False):
    """Update alerts from Gmail."""
    global lastUpdate, newAlerts, updating
    if updating or not alerts.ENABLED:
        return
    updating = True
    now = datetime.now(pytz.UTC)
    newAlerts = []
    if force or lastUpdate < now - timedelta(seconds=UPDATE_ALERTS_SECONDS // 2):
        try:
            newAlerts = alerts.update_alerts()
            lastUpdate = now
        except Exception:
            logging.exception("Cannot update alerts")
    updating = False

def subscription_update(bot, chat_id, force=False):
    """Process subscription updates."""
    update_alerts(force)
    for _, newAlertText in newAlerts:
        if not trading.existsAccount(NAME):
            trading.newAccount(NAME)
        result = trading.tradeAll(NAME, newAlertText)
        if 'BUY' not in result and 'SELL' not in result:
            result = newAlertText + '\n' + result
        text = f"🚨 New Alert!\n\n{result}"
        logging.info(text)
        bot.send_message(chat_id=chat_id, text=text)

def subscription_job(context):
    """Handle subscription job updates."""
    subscription_update(context.bot, chat_id=context.job.context)

def loadSubscriptions():
    """Load saved subscriptions from file."""
    if path.isfile('subscriptions'):
        with open('subscriptions', 'r') as subscriptionsFile:
            subscriptionUsers = json.load(subscriptionsFile)
            for subscriber in subscriptionUsers:
                job = updater.job_queue.run_repeating(subscription_job, 
                    interval=UPDATE_ALERTS_SECONDS, 
                    first=30, 
                    context=subscriber['chat_id'])
                SUBSCRIPTIONS[subscriber['user']] = job

def saveSubscriptions():
    """Save current subscriptions to file."""
    with open('subscriptions', 'w') as subscriptionsFile:
        json.dump([{ 'user': user, 'chat_id': job.context } 
                  for user, job in SUBSCRIPTIONS.items()], 
                 subscriptionsFile)

def __unsubscribe(update):
    """Internal function to handle unsubscription."""
    user = update.message.from_user.username
    if user in SUBSCRIPTIONS:
        SUBSCRIPTIONS[user].schedule_removal()
        SUBSCRIPTIONS.pop(user)
        return "Unsubscribed successfully."
    return "You are not subscribed."

#------------------------------------------------------------------------------
# COMMAND HANDLERS
#------------------------------------------------------------------------------

def start(update, context):
    """Handle the /start command - show available commands."""
    logger = logging.getLogger(__name__)
    user = update.message.from_user
    logger.info(f"Start command received from user {user.username} (ID: {user.id})")
    
    superuser = is_superuser(update)
    logger.info(f"User {user.username} superuser status: {superuser}")
    
    text = f"Hi, {user.first_name}! I'm {NAME}, your trading assistant!\n\nAvailable commands:"
    
    # Basic commands
    text += "\n/start - Shows this message"
    text += "\n/ping - Test connection with trading API"
    text += "\n/list - Show the available symbols"
    text += "\n/price symbol - Current price for provided symbol"
    
    # Account commands
    text += "\n/newAccount [balance] [currency] - Creates an account for mock trading"
    text += "\n/deleteAccount - Deletes your trading account"
    
    if superuser:
        logger.info(f"Adding superuser commands for {user.username}")
        text += f"\n/account [{NAME}, {user.username}] - View your account or the bot account"
        text += f"\n/history [{NAME}, {user.username}] - View your trades or the bot trades"
        text += "\n/adduser telegram_id role - Add new user (roles: admin, premium, basic)"
        text += "\n/removeuser telegram_id - Remove a user"
        text += "\n/users - List all users and their roles"
        text += f"\n/subscribe - Receive updates from the {NAME} auto-trading account"
        text += f"\n/unsubscribe - Stop receiving updates"
        text += f"\n/update - Force an update check"
    
    logger.info(f"Sending start message to user {user.username}")
    reply(update, text)

def subscribe(update, context):
    """Handle subscription requests."""
    user = update.message.from_user.username
    if user not in SUBSCRIPTIONS:
        job = context.job_queue.run_repeating(subscription_job, 
            interval=UPDATE_ALERTS_SECONDS, 
            first=0, 
            context=update.message.chat_id)
        SUBSCRIPTIONS[user] = job
        reply(update, f"Now you are subscribed to {NAME} trades.")
    else:
        reply(update, "Already subscribed.")

def unsubscribe(update, context):
    """Handle unsubscription requests."""
    reply(update, __unsubscribe(update))

def force_update(update, context):
    """Force an update check."""
    if not alerts.ENABLED:
        reply(update, "Alerts are disabled.")
        return
    reply(update, "Updating. Please, wait a few seconds.")
    subscription_update(context.bot, update.message.chat_id, force=True)
    if not newAlerts:
        reply(update, "Alerts are up to date.")

def add_user(update, context):
    """Add a new user to the bot with specified role."""
    if len(context.args) < 2:
        reply(update, "Usage: /adduser telegram_id role\nRoles: admin, premium, basic")
        return
    
    try:
        user_id = context.args[0]
        role = UserRole(context.args[1].lower())
        user_manager.add_user(user_id, role)
        reply(update, f"User {user_id} added with role {role.value}")
    except ValueError:
        reply(update, "Invalid role. Use: admin, premium, or basic")

def remove_user(update, context):
    """Remove a user from the bot."""
    if len(context.args) < 1:
        reply(update, "Usage: /removeuser telegram_id")
        return
    
    user_id = context.args[0]
    user_manager.remove_user(user_id)
    reply(update, f"User {user_id} has been removed")

def list_users(update, context):
    """List all users and their roles."""
    users = user_manager.users
    if not users:
        reply(update, "No users registered")
        return
    
    text = "Registered Users:\n"
    for user_id, data in users.items():
        status = "✅" if data["active"] else "❌"
        text += f"\n{status} {user_id}: {data['role']}"
    reply(update, text)

def unknown(update, context):
    """Handle unknown commands."""
    reply(update, f"Sorry, I didn't understand command {update.message.text}.")

#------------------------------------------------------------------------------
# MAIN FUNCTION
#------------------------------------------------------------------------------

def main():
    """Initialize and start the bot."""
    print("Starting bot...")
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)

    updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("subscribe", restricted(subscribe, UserRole.ADMIN)))
    dispatcher.add_handler(CommandHandler("unsubscribe", restricted(unsubscribe, UserRole.ADMIN)))
    dispatcher.add_handler(CommandHandler("update", restricted(force_update, UserRole.ADMIN)))
    dispatcher.add_handler(CommandHandler("adduser", restricted(add_user, UserRole.ADMIN)))
    dispatcher.add_handler(CommandHandler("removeuser", restricted(remove_user, UserRole.ADMIN)))
    dispatcher.add_handler(CommandHandler("users", restricted(list_users, UserRole.ADMIN)))
    dispatcher.add_handler(CommandHandler("ping", wrap(trading.ping)))
    dispatcher.add_handler(CommandHandler("price", send(trading.price, args=True)))
    dispatcher.add_handler(CommandHandler("list", send(trading.list_symbols)))
    dispatcher.add_handler(CommandHandler("account", account(trading.account)))
    dispatcher.add_handler(CommandHandler("history", account(trading.history)))
    dispatcher.add_handler(CommandHandler("trade", send(trading.trade, args=True)))
    dispatcher.add_handler(CommandHandler("tradeAll", send(trading.tradeAll, args=True)))
    dispatcher.add_handler(CommandHandler("newAccount", send(trading.newAccount, args=True)))
    dispatcher.add_handler(CommandHandler("deleteAccount", send(trading.deleteAccount)))
    
    # Add handler for unknown commands
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Load saved subscriptions
    loadSubscriptions()

    # Start the Bot
    print(f"Bot {NAME} is running...")
    updater.start_polling()

    # Run the bot until you send a signal to stop
    updater.idle()

if __name__ == '__main__':
    main()


