import requests
from bs4 import BeautifulSoup
import os

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from duckduckgo_search import DDGS
import wikipedia


groq_llm = ChatGroq(
    model="gemma2-9b-it",
    temperature=0.2,
)


def scrape_full_article(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.content, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = " ".join([p.get_text() for p in soup.find_all("p")])
        return text[:40000]  # Trim to avoid token overflow
    except Exception as e:
        return f"[Error scraping {url}]"


summarization_prompt = PromptTemplate.from_template("""
You are a professional fact-focused summarizer.

Given the article below, summarize it in 4–6 bullet points. Focus only on factual claims, findings, and key ideas related to the original topic.

ARTICLE:
{text}

SUMMARY:
- 
""")

summary_chain = LLMChain(llm=groq_llm, prompt=summarization_prompt)


def summarize_article(article_text):
    if not article_text.strip():
        return "[Empty Article]"
    try:
        summary = summary_chain.run({"text": article_text[:4000]})  # token-safe
        return summary.strip()
    except Exception as e:
        return "[Summary failed]"


def serper_urls(claim):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": "0f8f7d962eeb0953e4190e2311e140c5a6c02d50",
        "Content-Type": "application/json"
    }
    payload = {"q": claim}
    response = requests.post(url, headers=headers, json=payload)
    return [r["link"] for r in response.json().get("organic", [])[:5]]


def ddg_urls(claim):
    with DDGS() as ddgs:
        return [r["href"] for r in ddgs.text(claim, max_results=5)]



def wiki_urls(claim):
    try:
        titles = wikipedia.search(claim, results=5)
        return [f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}" for title in titles]
    except:
        return []


def google_fact_check_urls(claim):
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": claim,
        "key": "AIzaSyDLMGxKA8LhHeejl52owJ6kLEYYWEnnnbw"
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    links = []
    for claim_data in response.json().get("claims", [])[:5]:
        for review in claim_data.get("claimReview", []):
            link = review.get("url", "")
            if link:
                links.append(link)
    return links[:5]


def run_all_sources_with_summary(claim):
    all_urls = []

    all_urls += serper_urls(claim)
    all_urls += ddg_urls(claim)
    all_urls += wiki_urls(claim)
    all_urls += google_fact_check_urls(claim)

    print(f"🔗 Found {len(all_urls)} URLs.")

    summarized_articles = []
    for idx, url in enumerate(all_urls):
        print(f"🔎 Scraping and summarizing {idx+1}/{len(all_urls)}: {url}")
        article = scrape_full_article(url)
        summary = summarize_article(article)
        summarized_articles.append(f"URL: {url}\n{summary}")

    return summarized_articles


def get_final_verdict_from_llm(claim, all_evidence_texts):
    evidence_combined = "\n\n".join(all_evidence_texts[:20])[:45000]  # trim for tokens

    prompt_template = PromptTemplate.from_template("""
You are a news verification expert.

Given the following claim:
CLAIM: "{claim}"

Here is summary of evidences from multiple sources:
                                                   {evidence}


Based on this information, is the claim REAL or FAKE?
Answer with just "REAL" or "FAKE" and a short 2-3 sentence explanation.
""")


    chain = LLMChain(llm=groq_llm, prompt=prompt_template)
    return chain.run({"claim": claim, "evidence": evidence_combined})


