from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db = self.client.news
    
    async def create_indexes(self):
        await self.db.articles.create_index([("category", 1), ("published", -1)])
        await self.db.user_reads.create_index([("user_id", 1), ("article_id", 1)])

db = Database()
