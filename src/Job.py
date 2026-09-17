import Activity
import zoneinfo
import datetime
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes
)

import logging
from tzlocal import get_localzone

logger = logging.getLogger(__name__)

async def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_job(update: Update, context: ContextTypes.DEFAULT_TYPE, callback: callable, job_name: str, data: str, job_days: tuple[int, ...], hour: int = 12, minute: int = 0, second: int = 0):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    await remove_job_if_exists(job_name, context)
    tz = get_localzone()
    target_time = datetime.time(hour=hour, minute=minute, second=second, tzinfo=tz)

    context.job_queue.run_daily(
        callback=callback,
        time = target_time,
        days=job_days,
        chat_id=chat_id,
        user_id=user_id,
        name=job_name,
        data=data
    )
    current_job = context.job_queue.get_jobs_by_name(job_name)
    for job in current_job:
        logger.info(f'job: {job.name} was scheduled for:{job.next_t}')