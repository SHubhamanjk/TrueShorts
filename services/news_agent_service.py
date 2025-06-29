import uuid
from datetime import datetime, timedelta
from config import Config
from model.article import NewsAgentSession
from utils.database import db
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from duckduckgo_search import DDGS
import wikipedia
import asyncio
from bson import ObjectId
from duckduckgo_search.exceptions import DuckDuckGoSearchException

# Ensure TTL index exists
async def ensure_ttl_index():
    await db.db.news_sessions.create_index("last_accessed", expireAfterSeconds=600)

# Helper: get Groq LLM
def get_groq_llm():
    return ChatGroq(
        model="gemma2-9b-it",
        temperature=0.2,
        api_key=Config.GROQ_API_KEY,
    )

# Helper: get tools
async def get_tools():
    tools = []
    # DuckDuckGo tool with error handling
    def safe_ddg(q):
        try:
            return next(DDGS().text(q, max_results=3))
        except DuckDuckGoSearchException as e:
            # Log and skip DuckDuckGo if rate-limited
            import logging
            logging.warning(f"DuckDuckGo rate limit: {e}")
            return None
        except Exception as e:
            import logging
            logging.warning(f"DuckDuckGo error: {e}")
            return None
    # Wikipedia tool with error handling
    def safe_wiki(q):
        try:
            return wikipedia.summary(q, sentences=3)
        except Exception as e:
            import logging
            logging.warning(f"Wikipedia error: {e}")
            return None
    # Add tools only if they work
    ddg_result = safe_ddg("test")
    wiki_result = safe_wiki("test")
    if ddg_result:
        tools.append(Tool(
            name="DuckDuckGoSearch",
            func=safe_ddg,
            description="Searches the web using DuckDuckGo."
        ))
    if wiki_result:
        tools.append(Tool(
            name="Wikipedia",
            func=safe_wiki,
            description="Searches Wikipedia for summaries."
        ))
    if not tools:
        # Fallback tool: use only LLM
        def llm_only_tool(q):
            llm = get_groq_llm()
            prompt = f"Answer the following question using your own knowledge and reasoning.\nQuestion: {q}"
            return llm.invoke(prompt) if hasattr(llm, 'invoke') else llm(q)
        tools.append(Tool(
            name="LLMOnly",
            func=llm_only_tool,
            description="Fallback tool that uses only the LLM when all search APIs are unavailable."
        ))
    return tools

async def start_news_agent_session(article_id: str):
    await ensure_ttl_index()
    # Try to convert article_id to ObjectId if possible
    try:
        obj_id = ObjectId(article_id)
        article = await db.db.articles.find_one({"_id": obj_id})
    except Exception:
        article = await db.db.articles.find_one({"_id": article_id})
    if not article:
        raise ValueError("Article not found")
    llm = get_groq_llm()
    tools = await get_tools()
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=False)
    # Compose the prompt for timeline and analysis
    prompt = f"""
Given the following news article:
Title: {article.get('title', '')}
Content: {article.get('content', '')}

1. Provide a timeline of the news from its start to the present.
2. Explain how it is affecting lives, who is benefiting, and all relevant context.
Be as comprehensive as possible, using web and Wikipedia search as needed.
"""
    result = await asyncio.get_event_loop().run_in_executor(None, lambda: agent.run(prompt))
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    context = {
        "timeline": result,
        "analysis": result,
        "history": [
            {"role": "system", "content": prompt},
            {"role": "assistant", "content": result}
        ]
    }
    session = NewsAgentSession(
        session_id=session_id,
        article_id=str(article_id),
        context=context,
        last_accessed=now
    )
    await db.db.news_sessions.insert_one(session.dict())
    return session_id, result, result

async def follow_up_news_agent_session(session_id: str, question: str):
    session = await db.db.news_sessions.find_one({"session_id": session_id})
    if not session:
        raise ValueError("Session not found or expired")
    llm = get_groq_llm()
    tools = await get_tools()
    agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=False)
    # Compose the prompt with full context
    history = session["context"].get("history", [])
    context_str = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    prompt = f"Context so far:\n{context_str}\n\nFollow-up question: {question}\nAnswer in detail."
    answer = await asyncio.get_event_loop().run_in_executor(None, lambda: agent.run(prompt))
    # Update session context and last_accessed
    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": answer})
    await db.db.news_sessions.update_one(
        {"session_id": session_id},
        {"$set": {"context.history": history, "last_accessed": datetime.utcnow()}}
    )
    return session_id, answer 