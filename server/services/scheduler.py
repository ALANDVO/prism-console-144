from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from server.services.health_check import health_check_service
from server.config import settings


scheduler = AsyncIOScheduler()


async def start_scheduler():
    """Start the background scheduler."""
    # Add health check job
    scheduler.add_job(
        health_check_service.run_all_health_checks,
        trigger=IntervalTrigger(seconds=settings.health_check_interval_seconds),
        id="health_check",
        name="Provider Health Checks",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()


async def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown(wait=True)
    await health_check_service.close()
