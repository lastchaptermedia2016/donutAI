"""APScheduler-based scheduler service for reminders and background tasks.

Manages:
- Time-based reminder triggers
- Recurring reminder scheduling
- Background health checks
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None


async def reminder_callback(reminder_id: str, message: str) -> None:
    """Callback fired when a reminder triggers."""
    logger.info(f"🔔 Reminder triggered: {reminder_id} - {message}")
    # TODO: Integrate with notification system (WebSocket push, email, etc.)


async def health_check_callback() -> None:
    """Periodic health check callback."""
    logger.debug("Scheduler health check: OK")


def get_scheduler() -> AsyncIOScheduler:
    """Get or create the scheduler singleton."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
        logger.info("Scheduler service initialized")
    return _scheduler


async def start_scheduler() -> None:
    """Start the scheduler service."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        # Add daily health check
        scheduler.add_job(
            health_check_callback,
            IntervalTrigger(hours=1),
            id="health_check",
            replace_existing=True,
            name="System Health Check",
        )
        logger.info("Scheduler service started")


async def stop_scheduler() -> None:
    """Stop the scheduler service."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler service stopped")


async def schedule_reminder(
    reminder_id: str,
    message: str,
    remind_at: datetime,
    repeat: str = "none",
) -> None:
    """Schedule a reminder job.

    Args:
        reminder_id: Unique identifier for the reminder
        message: Reminder message
        remind_at: When to trigger
        repeat: Recurrence pattern ('none', 'daily', 'weekly', 'monthly')
    """
    scheduler = get_scheduler()

    kwargs = {
        "args": (reminder_id, message),
        "replace_existing": True,
        "name": f"Reminder: {message[:50]}",
        "id": f"reminder_{reminder_id}",
    }

    if repeat == "none":
        trigger = DateTrigger(run_date=remind_at)
    elif repeat == "daily":
        trigger = CronTrigger(
            hour=remind_at.hour,
            minute=remind_at.minute,
            second=remind_at.second,
        )
    elif repeat == "weekly":
        trigger = CronTrigger(
            day_of_week=remind_at.strftime("%a").lower(),
            hour=remind_at.hour,
            minute=remind_at.minute,
            second=remind_at.second,
        )
    elif repeat == "monthly":
        trigger = CronTrigger(
            day=remind_at.day,
            hour=remind_at.hour,
            minute=remind_at.minute,
            second=remind_at.second,
        )
    else:
        trigger = DateTrigger(run_date=remind_at)

    scheduler.add_job(reminder_callback, trigger, **kwargs)
    logger.info(f"Scheduled reminder {reminder_id}: {message}")


async def cancel_reminder(reminder_id: str) -> bool:
    """Cancel a scheduled reminder job."""
    scheduler = get_scheduler()
    job_id = f"reminder_{reminder_id}"
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Cancelled reminder job {job_id}")
        return True
    except Exception as e:
        logger.warning(f"Could not cancel reminder {job_id}: {e}")
        return False


async def list_scheduled_jobs() -> list[dict]:
    """List all scheduled jobs."""
    scheduler = get_scheduler()
    jobs = scheduler.get_jobs()
    return [
        {
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "trigger": str(job.trigger),
        }
        for job in jobs
    ]