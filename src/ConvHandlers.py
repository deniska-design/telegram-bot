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
import Job
import datetime
import logging

logger = logging.getLogger(__name__)

ANALITIC_PROCESSING, LOG_PROCESSING, STATISTIC_PROCESSING, REVOKE_PROCESSING, LOG_END = range(5)

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    for activity in Activity:
        context.user_data.setdefault(activity, [0.0] * 7)

    await Job.set_job(
        update = update, 
        context = context, 
        callback = revoke_activities, 
        job_name = f'revoke_job{user_id}', 
        data = 'your activities were revoked', 
        job_days=(3, ),
        hour=16,
        minute=40
    ) # 6 corresponds to Saturday
    logger.info("revoke job set")
    await Job.set_job(
        update = update,
        context = context,
        callback = remind,
        job_name = f'remind_job{user_id}',
        data = 'Don\'t forget to log your activities!',
        job_days=(1, 2, 3, 4, 5, 6, 0),  # 0-6 corresponds to Monday-Sunday
        hour=21,
        minute=0
    ) # 1-7 corresponds to Monday-Sunday
    logger.info("remind job set")
    await update.effective_message.reply_text(
        'Hello! I am your activity logging bot. You can log your activities, get analytics, and view statistics. Type /help to see the list of available commands.\n' \
        'Your activities will be revoked every Saturday at 12:00 AM\n'
        'you will receive a reminder every day at 9:00 PM to log your activities.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
    'basic:\n'
    '"/start" - start the bot\n'
    '"/help" - get help\n'
    '"/cancel" -  cancel your conversation\n' 
    'activities:\n'
    '"/log" - to log information about the user\n'
    '"/analytic" - get data about activity\n'
    '"/statistic" - get statistic of activity\n'
    '"/revoke" - revoke data for today\n')

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

async def revoke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[activity for activity in Activity]]
    await update.message.reply_text(
        'choose activity you want to revoke:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        )
    )
    return REVOKE_PROCESSING

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

async def revoke_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text not in Activity:
        await update.message.reply_text('Invalid activity. Please choose a valid activity.')
        await revoke_command(update, context)
        return 

    user = update.message.from_user
    logger.info("User %s is revoking %s", user.first_name, update.message.text)
    now = datetime.datetime.now()
    day_idx = now.weekday()
    context.user_data[update.message.text][day_idx] = 0
    await update.message.reply_text(f'Your {update.message.text} activities have been revoked for today.')
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

async def revoke_activities(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    for activity in Activity:
        for day in range(7):
            context.user_data[activity][day] = 0
    await context.bot.send_message(chat_id=job.chat_id, text=job.data)
    logger.info("activities revoked")

async def remind(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=job.data)
    logger.info("reminder sent")