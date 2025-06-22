from pydantic import BaseModel
from typing import Optional

class Article(BaseModel):
    title: str
    content: str
    category: Optional[str]
    published: Optional[str]
    source: Optional[str]
    seen: bool = False

class ReadEvent(BaseModel):
    user_id: str
    article_id: str
    duration: int  # in seconds
