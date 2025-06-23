from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Article(BaseModel):
    title: str
    content: str
    category: Optional[str]
    published: Optional[str]
    source: Optional[str]
    seen: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample News Title",
                "content": "This is the content of the news article.",
                "category": "sports",
                "published": "2024-05-01T12:00:00Z",
                "source": "gnews",
                "seen": False
            }
        }

class ArticleOut(Article):
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample News Title",
                "content": "This is the content of the news article.",
                "category": "sports",
                "published": "2024-05-01T12:00:00Z",
                "source": "gnews",
                "seen": False
            }
        }

class SavedArticleOut(BaseModel):
    user_id: str
    article_id: str
    saved_at: datetime
    article: ArticleOut

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "article_id": "article456",
                "saved_at": "2024-05-01T13:00:00Z",
                "article": ArticleOut.Config.json_schema_extra["example"]
            }
        }

class SearchArticleOut(BaseModel):
    headline: str
    content: str
    timestamp: Optional[str]
    source: Optional[str]
    category: Optional[str]
    url: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "headline": "Sample News Title",
                "content": "This is the content of the news article.",
                "timestamp": "2024-05-01T12:00:00Z",
                "source": "gnews",
                "category": "sports",
                "url": "https://example.com/news/123"
            }
        }

class ReadEvent(BaseModel):
    user_id: str
    article_id: str
    duration: int  # in seconds
