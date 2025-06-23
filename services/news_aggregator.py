import aiohttp
import asyncio
import feedparser
import logging
from config import Config
from utils.faiss_manager import faiss_manager
from utils.database import db
from services.recommender import embed_text
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

async def extract_full_article(session: aiohttp.ClientSession, url: str) -> str:
    """Extract main text content from article URL"""
    try:
        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            
            for element in soup(['script', 'style', 'header', 'footer', 'nav']):
                element.decompose()
            
            content_containers = [
                *soup.select('article, .article, .content, .post, .story'),
                *soup.find_all(['p', 'div'], class_=lambda x: x and 'content' in x)
            ]
            
            if content_containers:
                return ' '.join([container.get_text(separator=' ', strip=True) 
                                for container in content_containers])
            
            return soup.get_text(separator=' ', strip=True)[:10000]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"Error fetching {url}: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error parsing {url}")
    return None

async def fetch_rss_articles(source_name: str, rss_url: str) -> list:
    """Fetch and parse RSS feed articles asynchronously"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rss_url) as response:
                xml = await response.text()
                feed = feedparser.parse(xml)
                
                tasks = []
                for entry in feed.entries[:20]: 
                    if 'link' in entry:
                        tasks.append(process_rss_entry(session, source_name, entry))
                
                results = await asyncio.gather(*tasks)
                return [article for article in results if article]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"RSS fetch failed for {source_name}: {str(e)}")
    return []

async def process_rss_entry(session: aiohttp.ClientSession, source_name: str, entry) -> dict:
    """Process individual RSS entry and extract content"""
    try:
        content = await extract_full_article(session, entry.link)
        if not content:
            return None
        category = None
        if hasattr(entry, 'tags') and entry.tags:
            category = entry.tags[0]['term'] if 'term' in entry.tags[0] else None
        elif hasattr(entry, 'category'):
            category = entry.category
        return {
            "title": entry.title,
            "content": content,
            "published": entry.get("published", ""),
            "url": entry.link,
            "category": category,
            "source": source_name
        }
    except Exception as e:
        logger.exception(f"Error processing RSS entry: {entry.title}")
        return None

async def fetch_gnews_articles() -> list:
    """Fetch articles from GNews API"""
    try:
        url = f"https://gnews.io/api/v4/top-headlines?country=in&max=20&token={Config.GNEWS_API_KEY}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                
                tasks = []
                for item in data.get("articles", [])[:20]: 
                    if 'url' in item:
                        tasks.append(process_gnews_item(session, item))
                
                results = await asyncio.gather(*tasks)
                return [article for article in results if article]
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error(f"GNews fetch failed: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected error in GNews fetch")
    return []

async def process_gnews_item(session: aiohttp.ClientSession, item: dict) -> dict:
    """Process individual GNews item and extract content"""
    try:
        content = await extract_full_article(session, item['url'])
        if not content:
            return None
        category = item.get('category', None)
        return {
            "title": item["title"],
            "content": content,
            "published": item.get("publishedAt", ""),
            "url": item["url"],
            "category": category,
            "source": "gnews"
        }
    except Exception as e:
        logger.exception(f"Error processing GNews item: {item['title']}")
        return None

async def fetch_all_articles() -> list:
    """Fetch articles from all sources concurrently"""
    try:
        rss_tasks = [
            fetch_rss_articles(source, url)
            for source, url in Config.RSS_SOURCES.items()
        ]
        
        all_tasks = rss_tasks + [fetch_gnews_articles()]
        
        results = await asyncio.gather(*all_tasks, return_exceptions=True)
        
        articles = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Fetch task failed: {str(result)}")
            elif result:
                articles.extend(result)
        
        logger.info(f"Fetched {len(articles)} articles from all sources")
        return articles
    except Exception as e:
        logger.exception("Unexpected error in fetch_all_articles")
        return []
