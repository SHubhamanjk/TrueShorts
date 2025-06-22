from fastapi import APIRouter, HTTPException, Depends
from services.news_service import get_news_for_user, track_user_read, deduplicate_articles, deduplicate_articles_for_user
from utils.database import db
from jose import jwt
from config import Config
from utils.mongo_helpers import to_json_serializable
from tasks.background import scheduler

router = APIRouter()

async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/news")
async def get_news(token: str = Depends(get_current_user)):
    articles = await get_news_for_user(token)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    # Return only the top unique article (already seen logic is in get_news_for_user)
    return to_json_serializable(articles[0][0])

@router.get("/news/{category}")
async def get_category_news(category: str, token: str = Depends(get_current_user)):
    articles = await get_news_for_user(token, category)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles in category")
    # Return only the top unique article for the category
    return to_json_serializable(articles[0][0])

@router.get("/news/by_source/{source}")
async def get_source_news(source: str, token: str = Depends(get_current_user)):
    articles = await get_news_for_user(token, source=source)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles for this source")
    return to_json_serializable(articles[0][0])

@router.post("/read/{article_id}")
async def track_read(article_id: str, duration: int, token: str = Depends(get_current_user)):
    success = await track_user_read(token, article_id, duration)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"msg": "Reading tracked"}

@router.post("/fetch-latest-news")
async def fetch_latest_news(token: str = Depends(get_current_user)):
    """
    Manually trigger deduplication and fetch new articles from feeds/APIs for the authenticated user.
    """
    try:
        new_articles = await deduplicate_articles_for_user(token)
        return {"status": "success", "new_articles": len(new_articles)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
