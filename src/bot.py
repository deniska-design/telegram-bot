from typing import Final
from enum import StrEnum
import logging
import os
import zoneinfo
import datetime
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

class Activity(StrEnum):
    SLEEP = "Sleep"
    SPORT = 'Sport'

SATURDAY: Final = 5

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

ANALITIC_PRECCESING, LOG_PRECCESING, ANALITIC_END, LOG_END = range(4)

# Commands
async def StartCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('this bot is to track your activities and achieve goals.\nTo get further information write "/help"')

async def HelpCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('basic:\n"/start" - to start the bot\n"/help" - provides help\n"/cancel" - to cancel your conversation\nactivities:\n"/log" - to log information about the user\n"/analytic" - to get analytic about previously logged information\n"/setcancellation" - to revoke your activities on Saturday\n"/unsetcancellation" - to cancel cancellation on Saturday')

async def LogCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Sport', 'Sleep']]
    await update.message.reply_text(
        'choose activity you want to log:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return LOG_PRECCESING

async def AnalyticCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Sport', 'Sleep']]
    await update.message.reply_text(
        'choose activity you want to get analitic of:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return ANALITIC_PRECCESING

async def CancelCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("End of the conversation with %s.", user.first_name)
    await update.message.reply_text(
        "Bye!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Handlers
async def LogHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user

    context.user_data['activity'] = update.message.text

    logger.info("User %s is logging %s", user.first_name, update.message.text)
    await update.message.reply_text('Enter the number you want to log:')
    return LOG_END

async def AnalyticHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("%s analitic of %s", update.message.text, user.first_name)
    await update.message.reply_text(f'analitic of {update.message.text}: {context.user_data.get(update.message.text, 0)}')
    return ConversationHandler.END

async def LogEnd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chosen_activity = context.user_data.get('activity')
    number = int(update.message.text)

    if chosen_activity == Activity.SPORT:
        context.user_data[Activity.SPORT] = context.user_data.get(Activity.SPORT, 0) + number
    elif chosen_activity == Activity.SLEEP:
        context.user_data[Activity.SLEEP] = context.user_data.get(Activity.SLEEP, 0) + number

    logger.info("chosen_activity: %s duration: %s ", chosen_activity, number)
    await update.message.reply_text('Done!')
    return ConversationHandler.END

# Error
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update{update} caused error: {context.error}')

# Cancellation timer
async def RevokeActivities(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    context.user_data[Activity.SPORT] = 0
    context.user_data[Activity.SLEEP] = 0
    await context.bot.send_message(chat_id=job.chat_id, text=context.job.data)
    logger.info("activities were revoked")

async def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_saturday_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    user_id = update.effective_user.id

    await remove_job_if_exists('saturday_job', context)
    tz = zoneinfo.ZoneInfo('Europe/Berlin')
    target_time = datetime.time(hour=12,minute=0,second=0, tzinfo=tz)

    context.job_queue.run_daily(
        callback=RevokeActivities,
        time = target_time,
        days=(6,),
        chat_id=chat_id,
        user_id=user_id,
        name='saturday_job',
        data='cancellation of activities'
    )
    await update.effective_message.reply_text('Done')
    current_job = context.job_queue.get_jobs_by_name('saturday_job')
    for job in current_job:
        logger.info(f'job: {job.name} was scheduled for:{job.next_t}')

async def unset_saturday_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    job_removed = remove_job_if_exists('saturday_job', context)
    text = 'cancellation was cancelled' if job_removed else 'you did not set cancellation'
    await update.message.reply_text(text)
    logger.info("Saturday job was succesfully unset")


if __name__ == '__main__':
    print('Starting bot...')
    # 1. Crating the bot
    app = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states ANALITIC_PRECCESING, LOG_PRECCESING and LOG_END
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('log', LogCommand),
            CommandHandler('analytic', AnalyticCommand)
        ],
        states={
            ANALITIC_PRECCESING: [MessageHandler(filters.TEXT, AnalyticHandler)],
            LOG_PRECCESING: [MessageHandler(filters.TEXT, LogHandler)],
            LOG_END: [MessageHandler(filters.Regex(r'^\d+$'), LogEnd)]
        },
        fallbacks=[
            CommandHandler("cancel", CancelCommand)
        ],
    )

    # 2. We link the command name to a specific functions:
    # Commands:
    app.add_handler(CommandHandler('start', StartCommand))
    app.add_handler(CommandHandler('help', HelpCommand))
    app.add_handler(CommandHandler('setcancellation', set_saturday_job))
    app.add_handler(CommandHandler('unsetcancellation', unset_saturday_job))

    # Сonversation:
    app.add_handler(conv_handler)

    # Error:
    app.add_error_handler(error)

    # 3.Polls bot
    print('Polling...')
    app.run_polling(poll_interval=3)