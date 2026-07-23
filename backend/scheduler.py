from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

from pipeline import run_pipeline

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="America/Denver")


def _run_daily_job():
    logger.info("Running scheduled daily news analysis pipeline...")
    result = run_pipeline()
    logger.info(f"Daily pipeline result: {result}")


def start_scheduler():
    scheduler.add_job(
        _run_daily_job,
        trigger=CronTrigger(hour=6, minute=0, timezone="America/Denver"),
        id="daily_news_analysis",
        name="Daily news analysis (6:00 AM America/Denver)",
        misfire_grace_time=3600,
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — daily run at 6:00 AM America/Denver")


def stop_scheduler():
    scheduler.shutdown()
