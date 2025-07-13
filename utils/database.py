from motor.motor_asyncio import AsyncIOMotorClient
from config import Config
from datetime import datetime
print("MONGO_URI:", Config.MONGO_URI)

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client[Config.MONGO_DB_NAME]
        self.articles = self.db.articles
        self.users = self.db.users
        self.news_sessions = self.db.news_sessions
    
    async def create_indexes(self):
        await self.db.articles.create_index([("category", 1), ("published", -1)])
        await self.db.user_reads.create_index([("user_id", 1), ("article_id", 1)])

    def update_last_active(self):
        self.db.heartbeat.update_one(
            {"_id": "trueshorts-backend"},
            {"$set": {"last_active": datetime.utcnow()}},
            upsert=True
        )

db = Database()

def update_last_active():
    db.update_last_active()
