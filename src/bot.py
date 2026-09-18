from multiprocessing import context
from turtle import update
from typing import Final
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence
)
import ConvHandlers as ConHandlers
import Activity

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# loading variables from .env file
load_dotenv()

# Getting token
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")

TOKEN: Final = BOT_TOKEN
USERNAME: Final = BOT_USERNAME

# Error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'update{update} caused error: {context.error}')

if __name__ == '__main__':
    logger.info('Starting bot...')
    # 1. Crating the bot
    persistence = PicklePersistence(filepath='bot_data.pkl')
    app = ( 
        Application.
        builder().
        token(TOKEN).
        persistence(persistence).
        build()
    )

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('log', ConHandlers.log_start_command),
            CommandHandler('get', ConHandlers.analytic_start_command),
            CommandHandler('getstatistic', ConHandlers.statistic_start_command),
            CommandHandler('revoke', ConHandlers.revoke_command)
        ],
        states={
            ConHandlers.ANALITIC_PROCESSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, ConHandlers.analitic_handler)],
            ConHandlers.LOG_PROCESSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, ConHandlers.log_handler)],
            ConHandlers.STATISTIC_PROCESSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, ConHandlers.statistic_handler)],
            ConHandlers.REVOKE_PROCESSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, ConHandlers.revoke_handler)],
            ConHandlers.LOG_END: [MessageHandler(filters.ALL & ~filters.COMMAND, ConHandlers.log_end_handler)]
        },
        fallbacks=[
            CommandHandler("cancel", ConHandlers.cancel_command)
        ],
        name = 'conversation_handler',
        persistent = False
    )

    # 2. We link the command name to a specific functions:
    # Commands:
    app.add_handler(CommandHandler('start', ConHandlers.start_command))
    app.add_handler(CommandHandler('help', ConHandlers.help_command))

    # Сonversation:
    app.add_handler(conv_handler)

    # Error:
    app.add_error_handler(error)

    # 3.Polls bot
    logger.info('Polling...')
    app.run_polling()