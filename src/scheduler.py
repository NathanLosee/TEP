"""Module for scheduled background tasks."""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.logger.app_logger import get_logger
from src.logger.formatter import CustomFormatter

formatter = CustomFormatter("%(asctime)s")
logger = get_logger(__name__, formatter)

# Store the cleanup task reference for cancellation
_cleanup_task: Optional[asyncio.Task] = None


def cleanup_stale_browser_sessions() -> int:
    """Clean up stale browser sessions.

    Returns:
        int: Number of sessions cleared.

    """
    from src.registered_browser.repository import clear_stale_sessions

    db: Session = SessionLocal()
    try:
        # Get count before cleanup for logging
        from src.registered_browser.models import RegisteredBrowser
        from sqlalchemy import select
        from datetime import datetime, timedelta

        timeout_minutes = 30
        cutoff_time = datetime.now() - timedelta(minutes=timeout_minutes)

        stale_count = db.scalar(
            select(RegisteredBrowser)
            .where(
                RegisteredBrowser.active_session_started.isnot(None),
                RegisteredBrowser.last_seen < cutoff_time,
            )
            .with_only_columns(RegisteredBrowser.id)
        )

        # Actually clear them
        clear_stale_sessions(db, timeout_minutes=timeout_minutes)

        return stale_count if stale_count else 0
    finally:
        db.close()


async def periodic_cleanup(interval_minutes: int = 5) -> None:
    """Run periodic cleanup of stale browser sessions.

    Args:
        interval_minutes (int): Interval between cleanup runs in minutes.

    """
    logger.info(
        f"Starting periodic browser session cleanup (every {interval_minutes} minutes)"
    )

    while True:
        try:
            await asyncio.sleep(interval_minutes * 60)
            cleared = cleanup_stale_browser_sessions()
            if cleared > 0:
                logger.info(f"Cleared {cleared} stale browser session(s)")
        except asyncio.CancelledError:
            logger.info("Periodic cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Error during periodic cleanup: {e}")


def start_scheduler() -> None:
    """Start the background scheduler tasks."""
    global _cleanup_task

    loop = asyncio.get_event_loop()
    _cleanup_task = loop.create_task(periodic_cleanup())


def stop_scheduler() -> None:
    """Stop the background scheduler tasks."""
    global _cleanup_task

    if _cleanup_task and not _cleanup_task.done():
        _cleanup_task.cancel()


@asynccontextmanager
async def lifespan_scheduler(app):
    """Lifespan context manager for scheduler.

    This can be used with FastAPI's lifespan parameter for cleaner
    startup/shutdown handling.

    """
    global _cleanup_task

    # Startup
    _cleanup_task = asyncio.create_task(periodic_cleanup())
    logger.info("Scheduler started")

    yield

    # Shutdown
    if _cleanup_task and not _cleanup_task.done():
        _cleanup_task.cancel()
        try:
            await _cleanup_task
        except asyncio.CancelledError:
            pass
    logger.info("Scheduler stopped")
