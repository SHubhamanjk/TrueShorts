import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
    FAISS_INDEX_DIR = "faiss_indexes"
    RSS_SOURCES = {
        "bbc": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "reuters": "https://www.reuters.com/world/rss.xml",
        "ndtv": "https://www.ndtv.com/rss",
        "thehindu": "https://www.thehindu.com/news/national/?service=rss"
    }
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
    SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
    GOOGLE_FACT_CHECK_API_KEY = os.getenv("GOOGLE_FACT_CHECK_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "news")

