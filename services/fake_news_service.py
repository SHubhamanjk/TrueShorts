import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
# from duckduckgo_search import DDGS
import wikipedia
from typing import Tuple, List
from config import Config
import json
import asyncio
import httpx

# Lazy initialization for Groq LLM

def get_groq_llm():
    return ChatGroq(
        model="gemma2-9b-it",
        temperature=0.2,
        api_key=Config.GROQ_API_KEY,
    )

async def async_scrape_full_article(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return ""
            soup = BeautifulSoup(response.content, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            return text[:40000]
    except Exception:
        return f"[Error scraping {url}]"

summarization_prompt = PromptTemplate.from_template("""
You are a professional fact-focused summarizer.
Given the article below, summarize it in 4–6 bullet points. Focus only on factual claims, findings, and key ideas related to the original topic.
ARTICLE:
{text}
SUMMARY:
- 
""")

async def async_summarize_article(article_text):
    if not article_text.strip():
        return "[Empty Article]"
    try:
        groq_llm = get_groq_llm()
        chain = summarization_prompt | groq_llm
        loop = asyncio.get_event_loop()
        # Run the blocking LLM call in a thread pool for concurrency
        summary = await loop.run_in_executor(None, lambda: chain.invoke({"text": article_text[:4000]}))
        return summary.strip() if isinstance(summary, str) else str(summary)
    except Exception:
        return "[Summary failed]"

def serper_urls(claim):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": Config.SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": claim}
    response = requests.post(url, headers=headers, json=payload)
    return [r["link"] for r in response.json().get("organic", [])[:3]]

# def ddg_urls(claim):
#     with DDGS() as ddgs:
#         return [r["href"] for r in ddgs.text(claim, max_results=3)]

def wiki_urls(claim):
    try:
        titles = wikipedia.search(claim, results=3)
        return [f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}" for title in titles]
    except:
        return []

def google_fact_check_urls(claim):
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": claim,
        "key": Config.GOOGLE_FACT_CHECK_API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    links = []
    for claim_data in response.json().get("claims", [])[:3]:
        for review in claim_data.get("claimReview", []):
            link = review.get("url", "")
            if link:
                links.append(link)
    return links[:3]

async def run_all_sources_with_summary(claim) -> List[str]:
    all_urls = []
    all_urls += serper_urls(claim)
    # all_urls += ddg_urls(claim)
    all_urls += wiki_urls(claim)
    all_urls += google_fact_check_urls(claim)
    # Scrape all articles concurrently
    articles = await asyncio.gather(*(async_scrape_full_article(url) for url in all_urls))
    # Summarize all articles concurrently
    summaries = await asyncio.gather(*(async_summarize_article(article) for article in articles if article and not article.startswith("[Error")))
    return summaries

def get_final_verdict_from_llm(claim, all_evidence_texts) -> Tuple[str, str]:
    evidence_combined = "\n\n".join(all_evidence_texts[:20])[:45000]
    prompt_template = PromptTemplate.from_template("""
You are a news verification expert.
Given the following claim:
CLAIM: "{claim}"
Here is summary of evidences from multiple sources:
{evidence}
Based on this information, is the claim REAL or FAKE?
Respond ONLY in the following JSON format:
{{
  "verdict": "REAL or FAKE",
  "explanation": "A short 2-3 sentence explanation."
}}
""")
    groq_llm = get_groq_llm()
    chain = prompt_template | groq_llm
    result = chain.invoke({"claim": claim, "evidence": evidence_combined})
    # Try to parse result as JSON
    try:
        if hasattr(result, "content"):
            result_str = result.content
        elif isinstance(result, str):
            result_str = result
        else:
            result_str = str(result)
        json_start = result_str.find('{')
        json_end = result_str.rfind('}') + 1
        json_str = result_str[json_start:json_end]
        parsed = json.loads(json_str)
        verdict = parsed.get("verdict", "UNKNOWN")
        explanation = parsed.get("explanation", result_str)
    except Exception:
        verdict = "UNKNOWN"
        explanation = result_str
    return verdict, explanation

async def handle_claim_verification(claim: str) -> Tuple[str, str]:
    evidence = await run_all_sources_with_summary(claim)
    verdict, explanation = get_final_verdict_from_llm(claim, evidence)
    return verdict, explanation 