from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.news_service import deduplicate_articles_for_user, delete_old_articles_for_user
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=30)
async def periodic_deduplication():
    try:
        from utils.database import db
        user_ids = await db.db.users.distinct('_id')
        total_new = 0
        for user_id in user_ids:
            new_articles = await deduplicate_articles_for_user(str(user_id))
            total_new += len(new_articles)
        logger.info(f"Deduplicated {total_new} new articles userwise")
    except Exception as e:
        logger.error(f"Deduplication failed: {str(e)}")

@scheduler.scheduled_job('interval', hours=12)
async def periodic_cleanup():
    from utils.database import db
    user_ids = await db.db.articles.distinct('user_id')
    total_deleted = 0
    for user_id in user_ids:
        deleted = await delete_old_articles_for_user(user_id)
        total_deleted += deleted
    logger.info(f"Deleted {total_deleted} old articles (older than 3 days)")
