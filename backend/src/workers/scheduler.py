"""
APScheduler configuration and job registration.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging

from .tasks import subscription_tasks, payment_tasks, broadcast_tasks

logger = logging.getLogger(__name__)


def create_scheduler() -> AsyncIOScheduler:
    """
    Create and configure APScheduler.
    
    Returns:
        Configured scheduler instance
    """
    scheduler = AsyncIOScheduler(
        timezone="UTC",
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 300,
        },
    )
    
    # Register jobs
    register_jobs(scheduler)
    
    return scheduler


def register_jobs(scheduler: AsyncIOScheduler) -> None:
    """
    Register all background jobs.
    
    Args:
        scheduler: Scheduler instance
    """
    # Subscription jobs - run every 10 minutes
    scheduler.add_job(
        subscription_tasks.check_expired_subscriptions,
        trigger=IntervalTrigger(minutes=10),
        id="check_expired_subscriptions",
        name="Check and expire subscriptions",
        replace_existing=True,
    )
    
    scheduler.add_job(
        subscription_tasks.process_auto_renewals,
        trigger=CronTrigger(hour=0, minute=5),
        id="process_auto_renewals",
        name="Process automatic subscription renewals",
        replace_existing=True,
    )
    
    scheduler.add_job(
        subscription_tasks.send_renewal_reminders,
        trigger=CronTrigger(hour=9, minute=0),
        id="send_renewal_reminders",
        name="Send renewal reminders",
        replace_existing=True,
    )
    
    # Payment jobs - run every 5 minutes
    scheduler.add_job(
        payment_tasks.verify_pending_payments,
        trigger=IntervalTrigger(minutes=5),
        id="verify_pending_payments",
        name="Verify pending payments",
        replace_existing=True,
    )
    
    # Broadcast jobs - run every minute
    scheduler.add_job(
        broadcast_tasks.send_scheduled_broadcasts,
        trigger=IntervalTrigger(minutes=1),
        id="send_scheduled_broadcasts",
        name="Send scheduled broadcasts",
        replace_existing=True,
    )
    
    logger.info("Background jobs registered")


def start_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Start the scheduler.
    
    Args:
        scheduler: Scheduler instance
    """
    scheduler.start()
    logger.info("Scheduler started")


def shutdown_scheduler(scheduler: AsyncIOScheduler) -> None:
    """
    Shutdown the scheduler.
    
    Args:
        scheduler: Scheduler instance
    """
    scheduler.shutdown()
    logger.info("Scheduler stopped")
