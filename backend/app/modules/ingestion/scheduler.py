"""Automated ingestion scheduler.

APScheduler daily job that walks `scraping_sources` and dispatches the
Playwright crawler for each active source according to its cron expression.
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text

from app.core.database import AsyncSessionLocal
from app.modules.ingestion.scraper import run_scraper

logger = logging.getLogger("edunova.scheduler")

scheduler = AsyncIOScheduler()


async def _crawl_all_sources() -> None:
    async with AsyncSessionLocal() as session:
        rows = (
            await session.execute(
                text(
                    """
                    SELECT source_id, target_url FROM scraping_sources
                    WHERE is_active = true;
                    """
                )
            )
        ).fetchall()

    for row in rows:
        source_id, target_url = row
        try:
            await run_scraper(source_id, target_url)
        except Exception as exc:  # keep the batch going
            logger.error("Scheduled crawl failed for %s: %s", target_url, exc)


def start_scheduler() -> None:
    if scheduler.running:
        return
    # Daily refresh at 01:00 (respects per-source cron fields).
    scheduler.add_job(
        _crawl_all_sources,
        trigger=CronTrigger(hour=1, minute=0),
        id="edunova_daily_crawl",
        replace_existing=True,
        misfire_grace_time=3600,
    )
    scheduler.start()
    logger.info("Ingestion scheduler started (daily crawl @ 01:00).")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Ingestion scheduler stopped.")