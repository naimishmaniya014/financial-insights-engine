from fetcher import fetch_recent_news
from preprocessor import normalize_articles
from deduplication import deduplicate_articles
from summarizer import summarize_and_score
from digest_builder import build_digest_payload

async def build_company_digest(ticker: str) -> dict:
    """
    High-level orchestration for a single ticker.
    """
    if not ticker.isalnum():
        raise ValueError("Invalid ticker")

    # 1) Fetch raw
    raw_articles = await fetch_recent_news(ticker)

    # 2) Clean/normalize
    clean_articles = normalize_articles(raw_articles)

    # 3) Deduplicate
    unique_articles = deduplicate_articles(clean_articles)

    # 4) Summarize + sentiment
    annotated = await summarize_and_score(unique_articles, ticker=ticker)

    # 5) Build digest
    digest = build_digest_payload(ticker, annotated)

    return digest
