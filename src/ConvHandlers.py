from multiprocessing import context
from turtle import update
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler
)
import matplotlib.pyplot as plt
from Activity import Activity 
import io
import Revoke
import datetime
import logging

logger = logging.getLogger(__name__)

ANALITIC_PROCESSING, LOG_PROCESSING, STATISTIC_PROCESSING, LOG_END = range(4)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('this bot is to track your activities and achieve goals.\nTo get further information write "/help"')
    await Revoke.set_saturday_job(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('basic:\n"/start" - to start the bot\n"/help" - provides help\n"/cancel" - to cancel your conversation\nactivities:\n"/log" - to log information about the user\n"/analytic" - to get analytic about previously logged information\n"/setcancellation" - to revoke your activities on Saturday\n"/unsetcancellation" - to cancel cancellation on Saturday')

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("End of the conversation with %s.", user.first_name)
    await update.message.reply_text(
        "Bye!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def log_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [[activity for activity in Activity]]
    await update.message.reply_text(
        'choose activity you want to log:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return LOG_PROCESSING

async def analytic_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [[activity for activity in Activity]]
    await update.message.reply_text(
        'choose activity you want to get analitic of:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return ANALITIC_PROCESSING

async def statistic_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [[activity for activity in Activity]]
    await update.message.reply_text(
        'choose activity you want to get statistic of:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return STATISTIC_PROCESSING

# Handlers
async def log_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in Activity:
        await update.message.reply_text('Invalid activity. Please choose a valid activity.')
        await log_start_command(update, context)
        return LOG_PROCESSING

    user = update.message.from_user

    context.user_data['activity'] = update.message.text

    logger.info("User %s is logging %s", user.first_name, update.message.text)
    await update.message.reply_text('Enter the number you want to log:')
    return LOG_END

async def analitic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in Activity:
        await update.message.reply_text('Invalid activity. Please choose a valid activity.')
        await analytic_start_command(update, context)
        return ANALITIC_PROCESSING

    user = update.message.from_user
    logger.info("%s analitic of %s", update.message.text, user.first_name)

    now = datetime.datetime.now()
    day_idx = now.weekday() 

    await update.message.reply_text(f'analitic of {update.message.text}: {context.user_data.get(update.message.text, [0] * 7)[day_idx]}')
    return ConversationHandler.END

async def statistic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text not in Activity:
        await update.message.reply_text('Invalid activity. Please choose a valid activity.')
        await statistic_start_command(update, context)
        return STATISTIC_PROCESSING

    user = update.message.from_user
    logger.info("%s statistic of %s", update.message.text, user.first_name)

    chosen_activity = update.message.text

    x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    y = context.user_data.get(chosen_activity, [0] * 7)
    fig, ax = plt.subplots()

    ax.plot(x, y, label=chosen_activity)
    ax.set_title(f'statistic')
    ax.set_ylabel('duration')
    ax.set_xlabel('week days')
    ax.grid(True)
    ax.legend()

    buffer = io.BytesIO()
    fig.savefig(buffer, format = 'png', bbox_inches='tight', dpi=200)
    buffer.seek(0)

    plt.close(fig)

    await update.message.reply_photo(photo=buffer)

    return ConversationHandler.END

async def log_end_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    chosen_activity = context.user_data.get('activity')
    try:
        number = float(update.message.text) if '.' in update.message.text else int(update.message.text)
    except ValueError:
        await update.message.reply_text('Invalid number. Please enter a valid number.')
        return LOG_END

    logger.info("chosen_activity: %s; duration: %s ", chosen_activity, number)

    now = datetime.datetime.now()
    day_idx = now.weekday()  # Monday is 0 and Sunday is 6

    activity_data = context.user_data.setdefault(chosen_activity, [0.0] * 7)
    activity_data[day_idx] += number

    await update.message.reply_text('Done!')
    return ConversationHandler.END
