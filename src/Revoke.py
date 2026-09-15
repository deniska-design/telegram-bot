import Activity
import zoneinfo
import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes
)

import logging

logger = logging.getLogger(__name__)

# Cancellation timer
async def revoke_activities(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    for activity in Activity:
        for day in range(7):
            context.user_data[activity][day] = 0
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
        callback=revoke_activities,
        time = target_time,
        days=(6,),
        chat_id=chat_id,
        user_id=user_id,
        name='saturday_job',
        data='cancellation of activities'
    )
    current_job = context.job_queue.get_jobs_by_name('saturday_job')
    for job in current_job:
        logger.info(f'job: {job.name} was scheduled for:{job.next_t}')
    await update.effective_message.reply_text('Your activities will be revoked every Saturday at 12:00 PM (Berlin time).')
