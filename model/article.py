from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime
import uuid

class Article(BaseModel):
    title: str
    content: str
    category: Optional[str]
    published: Optional[str]
    source: Optional[str]
    seen: bool = False
    verified: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Sample News Title",
                "content": "This is the content of the news article.",
                "category": "sports",
                "published": "2024-05-01T12:00:00Z",
                "source": "gnews",
                "seen": False,
                "verified": False
            }
        }

class ArticleOut(BaseModel):
    article_id: Optional[str] = None
    title: str
    content: str
    category: Optional[str]
    published: Optional[str]
    source: Optional[str]
    url: Optional[str] = None
    user_id: Optional[str] = None
    embedding: Optional[List[float]] = None
    fetched_at: Optional[datetime] = None
    seen: bool = False
    verified: bool = False
    verdict: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "article_id": "507f1f77bcf86cd799439011",
                "title": "Sample News Title",
                "content": "This is the content of the news article.",
                "category": "sports",
                "published": "2024-05-01T12:00:00Z",
                "source": "gnews",
                "url": "https://example.com/news/123",
                "user_id": "user123",
                "seen": False,
                "verified": False,
                "verdict": "REAL",
                "explanation": "This news has been verified by multiple sources."
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

class ClaimInput(BaseModel):
    claim: str
    class Config:
        json_schema_extra = {"example": {"claim": "COVID-19 vaccines cause microchips to be implanted in people."}}

class ClaimVerdictOut(BaseModel):
    verdict: str
    explanation: str
    class Config:
        json_schema_extra = {"example": {"verdict": "FAKE", "explanation": "Multiple reputable sources and fact-checks confirm that COVID-19 vaccines do not contain microchips."}}

class NewsAgentSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    article_id: str
    context: Any
    last_accessed: datetime
    class Config:
        json_schema_extra = {"example": {"session_id": "123e4567-e89b-12d3-a456-426614174000", "user_id": "user123", "article_id": "article456", "context": {"timeline": "...", "analysis": "..."}, "last_accessed": "2024-05-01T13:00:00Z"}}

class NewsAgentInput(BaseModel):
    article_id: str
    class Config:
        json_schema_extra = {"example": {"article_id": "article456"}}

class NewsAgentOutput(BaseModel):
    session_id: str
    timeline: str
    analysis: str
    class Config:
        json_schema_extra = {"example": {"session_id": "123e4567-e89b-12d3-a456-426614174000", "timeline": "Timeline of the news...", "analysis": "Analysis of the news..."}}

class NewsAgentFollowUpInput(BaseModel):
    session_id: str
    question: str
    class Config:
        json_schema_extra = {"example": {"session_id": "123e4567-e89b-12d3-a456-426614174000", "question": "What was the public reaction?"}}

class NewsAgentFollowUpOutput(BaseModel):
    session_id: str
    answer: str
    class Config:
        json_schema_extra = {"example": {"session_id": "123e4567-e89b-12d3-a456-426614174000", "answer": "The public reaction was..."}}
