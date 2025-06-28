from utils.database import db
from utils.faiss_manager import faiss_manager
from services.recommender import embed_text, is_similar, recommend_similar
from jose import jwt
import os
import numpy as np
import logging
from bson import ObjectId
from datetime import datetime, timedelta
import pytz
import asyncio
from services.fake_news_service import handle_claim_verification

logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')

async def deduplicate_articles():
    from services.news_aggregator import fetch_all_articles
    articles = await fetch_all_articles()
    global_index = faiss_manager.get_index("global.index")
    
    new_articles = []
    for article in articles:
        embedding = embed_text(article["title"] + " " + article["content"])
        if not is_similar(embedding, global_index):
            article["embedding"] = embedding.tolist()
            article["verified"] = False
            result = await db.db.articles.insert_one(article)
            article_id = result.inserted_id
            faiss_id = int(article_id.binary.hex(), 16) % (2**63)
            global_index.add_with_ids(
                np.array([embedding], dtype=np.float32),
                np.array([faiss_id], dtype=np.int64)
            )
            new_articles.append(article)
    
    faiss_manager.save_index("global.index", global_index)
    return new_articles

async def deduplicate_articles_for_user(user_id):
    from services.news_aggregator import fetch_all_articles
    articles = await fetch_all_articles()
    user_index = faiss_manager.get_index(f"user_{user_id}.index")
    new_articles = []
    for article in articles:
        embedding = embed_text(article["title"] + " " + article["content"])
        article["embedding"] = embedding.tolist()
        article["user_id"] = user_id
        article["seen"] = False
        article["fetched_at"] = datetime.now(IST)
        article["verified"] = False
        result = await db.db.articles.insert_one(article)
        article_id = result.inserted_id
        faiss_id = int(article_id.binary.hex(), 16) % (2**63)
        user_index.add_with_ids(
            np.array([embedding], dtype=np.float32),
            np.array([faiss_id], dtype=np.int64)
        )
        new_articles.append(article)
    faiss_manager.save_index(f"user_{user_id}.index", user_index)
    return new_articles

async def get_news_for_user(user_id: str, category: str = None, source: str = None, _refresh: bool = True):
    user_index = faiss_manager.get_index(f"user_{user_id}.index")
    # Only show articles that are (verified=True and seen=False) or (verified=False and seen=False)
    query = {"user_id": user_id, "seen": False, "$or": [{"verified": True}, {"verified": False}]}
    if category:
        query["category"] = category
    if source:
        query["source"] = source
    cursor = db.db.articles.find(query).sort("published", -1).limit(100)
    read_cursor = db.db.user_reads.find({"user_id": user_id})
    read_ids = set()
    async for read in read_cursor:
        read_ids.add(read["article_id"])
    recommendations = []
    for article in await cursor.to_list(length=100):
        if str(article["_id"]) in read_ids:
            continue
        embedding = np.array(article["embedding"], dtype=np.float32)
        if user_index.ntotal == 0 or not is_similar(embedding, user_index, threshold=0.9):
            _, similarities = recommend_similar(embedding, user_index, top_k=1)
            score = similarities[0] if similarities else 0
            recommendations.append((article, score))
    if not recommendations and _refresh:
        await deduplicate_articles_for_user(user_id)
        return await get_news_for_user(user_id, category, source, _refresh=False)
    if recommendations:
        await db.db.articles.update_one({"_id": recommendations[0][0]["_id"]}, {"$set": {"seen": True}})
    return sorted(recommendations, key=lambda x: x[1], reverse=True)[:10]

async def track_user_read(user_id: str, article_id: str, duration: int):
    article = await db.db.articles.find_one({"_id": ObjectId(article_id), "user_id": user_id})
    if not article:
        return False
    user_index = faiss_manager.get_index(f"user_{user_id}.index")
    embedding = np.array(article["embedding"], dtype=np.float32)
    oid = ObjectId(article_id)
    faiss_id = int(oid.binary.hex(), 16) % (2**63)
    user_index.add_with_ids(
        np.array([embedding], dtype=np.float32),
        np.array([faiss_id], dtype=np.int64)
    )
    faiss_manager.save_index(f"user_{user_id}.index", user_index)
    await db.db.user_reads.insert_one({
        "user_id": user_id,
        "article_id": article_id,
        "duration": duration,
        "timestamp": datetime.utcnow()
    })
    return True

async def delete_old_articles_for_user(user_id):
    cutoff = datetime.now(IST) - timedelta(days=3)
    result = await db.db.articles.delete_many({"user_id": user_id, "fetched_at": {"$lt": cutoff}})
    return result.deleted_count

async def verify_unverified_articles_for_user(user_id):
    from utils.database import db
    # Find all unverified articles for the user
    cursor = db.db.articles.find({"user_id": user_id, "verified": {"$ne": True}})
    tasks = []
    async for article in cursor:
        claim = article.get("title", "")
        article_id = article["_id"]
        # Launch verification in the background for each article
        tasks.append(_verify_and_update_article(user_id, article_id, claim))
    if tasks:
        await asyncio.gather(*tasks)

async def _verify_and_update_article(user_id, article_id, claim):
    from utils.database import db
    verdict, explanation = await handle_claim_verification(claim)
    if verdict == "REAL":
        await db.db.articles.update_one({"_id": article_id, "user_id": user_id}, {"$set": {"verified": True, "verdict": verdict, "explanation": explanation}})
    else:
        await db.db.articles.update_one({"_id": article_id, "user_id": user_id}, {"$set": {"verified": False, "verdict": verdict, "explanation": explanation}})

async def verify_unverified_articles_global():
    cursor = db.db.articles.find({"verified": False}).sort("published", -1)
    async for article in cursor:
        claim = article.get("title", "")
        article_id = article["_id"]
        logger.info(f"Verifying article {article_id}: {claim}")
        verdict, explanation = await handle_claim_verification(claim)
        await db.db.articles.update_one({"_id": article_id}, {"$set": {"verified": True, "verdict": verdict, "explanation": explanation}})
        logger.info(f"Article {article_id} verified: {verdict}")
