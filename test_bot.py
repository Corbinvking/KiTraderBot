#!/usr/bin/env python3
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Load token
with open("tokens/telegram", 'r') as f:
    TOKEN = f.read().strip()

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(f'Hi {user.first_name}! Bot is working!')

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help message')

def main() -> None:
    """Start the bot."""
    # Create the Updater
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Basic commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start the Bot
    logger.info("Starting bot...")
    updater.start_polling()
    logger.info("Bot is running!")

    # Run the bot until Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
