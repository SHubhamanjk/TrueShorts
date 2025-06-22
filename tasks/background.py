from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.news_service import deduplicate_articles
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=30)
async def periodic_deduplication():
    try:
        new_articles = await deduplicate_articles()
        logger.info(f"Deduplicated {len(new_articles)} new articles")
    except Exception as e:
        logger.error(f"Deduplication failed: {str(e)}")
