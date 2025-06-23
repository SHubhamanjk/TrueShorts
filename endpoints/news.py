from fastapi import APIRouter, HTTPException, Depends, Query
from services.news_service import get_news_for_user, track_user_read, deduplicate_articles, deduplicate_articles_for_user
from utils.database import db
from jose import jwt
from config import Config
from utils.mongo_helpers import to_json_serializable
from tasks.background import scheduler
from datetime import datetime
from bson.objectid import ObjectId
from services.news_aggregator import fetch_all_articles
from googletrans import Translator
from model.article import ArticleOut, SavedArticleOut, SearchArticleOut
from typing import List, Dict, Any

router = APIRouter()

async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/news", response_model=ArticleOut)
async def get_news(token: str = Depends(get_current_user)):
    articles = await get_news_for_user(token)
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")
    return articles[0][0]

# @router.get("/news/{category}")
# async def get_category_news(category: str, token: str = Depends(get_current_user)):
#     articles = await get_news_for_user(token, category)
#     if not articles:
#         raise HTTPException(status_code=404, detail="No articles in category")
#     return to_json_serializable(articles[0][0])

# @router.get("/news/by_source/{source}")
# async def get_source_news(source: str, token: str = Depends(get_current_user)):
#     articles = await get_news_for_user(token, source=source)
#     if not articles:
#         raise HTTPException(status_code=404, detail="No articles for this source")
#     return to_json_serializable(articles[0][0])

@router.post("/read/{article_id}", response_model=Dict[str, str])
async def track_read(article_id: str, duration: int, token: str = Depends(get_current_user)):
    success = await track_user_read(token, article_id, duration)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"msg": "Reading tracked"}

@router.post("/fetch-latest-news", response_model=Dict[str, Any])
async def fetch_latest_news(token: str = Depends(get_current_user)):
    """
    Manually trigger deduplication and fetch new articles from feeds/APIs for the authenticated user.
    """
    try:
        new_articles = await deduplicate_articles_for_user(token)
        return {"status": "success", "new_articles": len(new_articles)}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.post("/news/save/{article_id}", response_model=Dict[str, str])
async def save_article(article_id: str, token: str = Depends(get_current_user)):
    user_id = token
    existing = await db.db.saved_articles.find_one({"user_id": user_id, "article_id": article_id})
    if existing:
        return {"msg": "Article already saved"}
    article = await db.db.articles.find_one({"_id": ObjectId(article_id), "user_id": user_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found for this user")
    save_doc = {
        "user_id": user_id,
        "article_id": article_id,
        "saved_at": datetime.utcnow(),
        "article": article
    }
    await db.db.saved_articles.insert_one(save_doc)
    return {"msg": "Article saved"}

@router.get("/news/saved", response_model=List[ArticleOut])
async def get_saved_articles(token: str = Depends(get_current_user)):
    user_id = token
    cursor = db.db.saved_articles.find({"user_id": user_id}).sort("saved_at", -1)
    saved = []
    async for doc in cursor:
        # Return just the article details for each saved article
        saved.append(ArticleOut(**doc["article"]))
    return saved

@router.get("/news/search", response_model=List[SearchArticleOut])
async def search_news(query: str = Query(..., description="Keywords or description to search in news")):
    articles = await fetch_all_articles()
    query_lower = query.lower()
    filtered = [
        SearchArticleOut(
            headline=a.get("title"),
            content=a.get("content"),
            timestamp=a.get("published"),
            source=a.get("source"),
            category=a.get("category"),
            url=a.get("url")
        )
        for a in articles
        if query_lower in (a.get("title", "").lower() + " " + a.get("content", "").lower())
    ]
    return filtered

@router.get("/news/translate/{article_id}", response_model=ArticleOut)
async def translate_article(article_id: str, token: str = Depends(get_current_user)):
    user_id = token
    article = await db.db.articles.find_one({"_id": ObjectId(article_id), "user_id": user_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found for this user")
    translator = Translator()
    try:
        title = article.get("title", "") or ""
        content = article.get("content", "") or ""
        if not title and not content:
            raise ValueError("No title or content to translate.")
        translated_title = title
        translated_content = content
        if title:
            try:
                result = translator.translate(title, dest='hi')
                if result and hasattr(result, 'text') and result.text:
                    translated_title = result.text
            except Exception:
                pass
        if content:
            try:
                result = translator.translate(content, dest='hi')
                if result and hasattr(result, 'text') and result.text:
                    translated_content = result.text
            except Exception:
                pass
        if translated_title == title and translated_content == content:
            raise ValueError("Translation service unavailable or failed. Returning original text.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    translated_article = article.copy()
    translated_article["title"] = translated_title
    translated_article["content"] = translated_content
    return ArticleOut(**translated_article)
