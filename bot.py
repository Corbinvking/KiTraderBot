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
import gmail as alerts
import bitstamp as trading
from user_management import UserManager, UserRole

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

#------------------------------------------------------------------------------
# UTILITY FUNCTIONS
#------------------------------------------------------------------------------

def debug(update, answer):
    """Log debug information about user interactions."""
    print(f"{datetime.now()} - {update.message.from_user.username} ({update.message.chat_id}): {update.message.text}\n{answer}\n")

def reply(update, text):
    """Send a reply to the user and log it."""
    debug(update, text)
    update.message.reply_text(text)

def is_superuser(update):
    """Check if the user is a superuser."""
    return update.message.from_user.username in SUPERUSERS

#------------------------------------------------------------------------------
# DECORATORS
#------------------------------------------------------------------------------

def restricted(handler, required_role=UserRole.BASIC):
    """Restrict command access based on user role."""
    def response(update, context, **kwargs):
        username = update.message.from_user.username
        if user_manager.is_authorized(username, required_role):
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
        print(text)
        bot.send_message(chat_id=chat_id, text=text)

def subscription_job(context):
    """Handle subscription job updates."""
    subscription_update(context.bot, chat_id=context.job.context)

def loadSubscriptions():
    """Load saved subscriptions from file."""
    global updater
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

#------------------------------------------------------------------------------
# COMMAND HANDLERS
#------------------------------------------------------------------------------

def start(update, context):
    """Handle the /start command - show available commands."""
    user = update.message.from_user
    superuser = is_superuser(update)
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
        text += f"\n/account [{NAME}, {user.username}] - View your account or the bot account"
        text += f"\n/history [{NAME}, {user.username}] - View your trades or the bot trades"
        text += "\n/adduser username role - Add new user (roles: admin, premium, basic)"
        text += "\n/removeuser username - Remove a user"
        text += "\n/users - List all users and their roles"
        text += f"\n/subscribe - Receive updates from the {NAME} auto-trading account"
        text += f"\n/unsubscribe - Stop receiving updates"
        text += f"\n/update - Force an update check"
    
    reply(update, text)

def unknown(update, context):
    """Handle unknown commands."""
    reply(update, f"Sorry, I didn't understand command {update.message.text}.")

def add_user(update, context):
    """Add a new user to the bot with specified role."""
    if len(context.args) < 2:
        reply(update, "Usage: /adduser username role\nRoles: admin, premium, basic")
        return
    
    try:
        username = context.args[0]
        role = UserRole(context.args[1].lower())
        user_manager.add_user(username, role)
        reply(update, f"User {username} added with role {role.value}")
    except ValueError:
        reply(update, "Invalid role. Use: admin, premium, or basic")

def remove_user(update, context):
    """Remove a user from the bot."""
    if len(context.args) < 1:
        reply(update, "Usage: /removeuser username")
        return
    
    username = context.args[0]
    user_manager.remove_user(username)
    reply(update, f"User {username} has been removed")

def list_users(update, context):
    """List all users and their roles."""
    users = user_manager.users
    if not users:
        reply(update, "No users registered")
        return
    
    text = "Registered Users:\n"
    for username, data in users.items():
        status = "✅" if data["active"] else "❌"
        text += f"\n{status} {username}: {data['role']}"
    reply(update, text)

#------------------------------------------------------------------------------
# INITIALIZATION
#------------------------------------------------------------------------------

print("Starting bot...")

bot = Bot(TELEGRAM_API_TOKEN)
NAME = bot.get_me().first_name
updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# ERROR HANDLING
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN)

def error_callback(update, context):
    try:
        raise context.error
    except Unauthorized:
        __unsubscribe(update)
    except TimedOut:
        pass

print('Adding command handlers...')

dispatcher.add_error_handler(error_callback)

#------------------------------------------------------------------------------
# COMMAND HANDLERS REGISTRATION
#------------------------------------------------------------------------------

# User Management Handlers
dispatcher.add_handler(CommandHandler('adduser', restricted(add_user, required_role=UserRole.ADMIN)))
dispatcher.add_handler(CommandHandler('removeuser', restricted(remove_user, required_role=UserRole.ADMIN)))
dispatcher.add_handler(CommandHandler('users', restricted(list_users, required_role=UserRole.ADMIN)))

# Subscription Handlers
dispatcher.add_handler(CommandHandler('subscribe', restricted(subscribe), pass_job_queue=True))
dispatcher.add_handler(CommandHandler('unsubscribe', restricted(unsubscribe)))
dispatcher.add_handler(CommandHandler('update', restricted(force_update)))

# Trading Handlers
dispatcher.add_handler(CommandHandler('ping', wrap(trading.ping)))
dispatcher.add_handler(CommandHandler('price', send(trading.price, args=True)))
dispatcher.add_handler(CommandHandler('list', send(trading.list_symbols)))
dispatcher.add_handler(CommandHandler('account', account(trading.account)))
dispatcher.add_handler(CommandHandler('history', account(trading.history)))
dispatcher.add_handler(CommandHandler('trade', send(trading.trade, args=True)))
dispatcher.add_handler(CommandHandler('tradeAll', send(trading.tradeAll, args=True)))
dispatcher.add_handler(CommandHandler('newAccount', send(trading.newAccount, args=True)))
dispatcher.add_handler(CommandHandler('deleteAccount', send(trading.deleteAccount)))

# Default Handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))
dispatcher.add_handler(MessageHandler(Filters.text, start))

#------------------------------------------------------------------------------
# START BOT
#------------------------------------------------------------------------------

print('Loading trading API...')
trading.load()

print('Loading subscriptions...')
loadSubscriptions()

updater.start_polling()

print(f"\n{NAME} Started!\n")

updater.idle()

# STOP
print("Saving accounts...")
trading.save()
saveSubscriptions()

print("Done! Goodbye!")


