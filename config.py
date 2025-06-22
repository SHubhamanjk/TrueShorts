import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    FAISS_INDEX_DIR = "faiss_indexes"
    RSS_SOURCES = {
        "bbc": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "reuters": "https://www.reuters.com/world/rss.xml",
        "ndtv": "https://www.ndtv.com/rss",
        "thehindu": "https://www.thehindu.com/news/national/?service=rss"
    }
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

