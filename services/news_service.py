from utils.database import db
from utils.faiss_manager import faiss_manager
from services.recommender import embed_text, is_similar, recommend_similar
from jose import jwt
import os
import numpy as np
import logging
from bson import ObjectId
from datetime import datetime

logger = logging.getLogger(__name__)

async def deduplicate_articles():
    from services.news_aggregator import fetch_all_articles
    articles = await fetch_all_articles()
    global_index = faiss_manager.get_index("global.index")
    
    new_articles = []
    for article in articles:
        embedding = embed_text(article["title"] + " " + article["content"])
        if not is_similar(embedding, global_index):
            article["embedding"] = embedding.tolist()
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
        if not is_similar(embedding, user_index):
            article["embedding"] = embedding.tolist()
            article["user_id"] = user_id
            article["seen"] = False
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
    query = {"user_id": user_id, "seen": False}
    if category:
        query["category"] = category
    if source:
        query["source"] = source
    pipeline = [
        {"$match": query},
        {"$sample": {"size": 100}}
    ]
    cursor = db.db.articles.aggregate(pipeline)
    recommendations = []
    read_cursor = db.db.user_reads.find({"user_id": user_id})
    read_ids = set()
    async for read in read_cursor:
        read_ids.add(read["article_id"])
    if user_index.ntotal == 0:
        async for article in cursor:
            if str(article["_id"]) in read_ids:
                continue
            recommendations.append((article, 0))
        if not recommendations and _refresh:
            await deduplicate_articles_for_user(user_id)
            return await get_news_for_user(user_id, category, source, _refresh=False)
        # Mark the first article as seen if available
        if recommendations:
            await db.db.articles.update_one({"_id": recommendations[0][0]["_id"]}, {"$set": {"seen": True}})
        return recommendations[:10]
    async for article in cursor:
        if str(article["_id"]) in read_ids:
            continue
        embedding = np.array(article["embedding"], dtype=np.float32)
        if not is_similar(embedding, user_index, threshold=0.9):
            _, similarities = recommend_similar(embedding, user_index, top_k=1)
            score = similarities[0] if similarities else 0
            recommendations.append((article, score))
    if not recommendations and _refresh:
        await deduplicate_articles_for_user(user_id)
        return await get_news_for_user(user_id, category, source, _refresh=False)
    # Mark the first article as seen if available
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
