"""
Fetcher module for retrieving raw financial news articles.

This minimal implementation hits Finnhub's company-news endpoint when a
`FINNHUB_API_KEY` environment variable is present. If not configured or the
request fails, it returns a small, deterministic dummy payload so downstream
stages can be developed and tested without external dependencies.
"""

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen


FINNHUB_BASE_URL = "https://finnhub.io/api/v1/company-news"


@dataclass
class RawArticle:
    """Lightweight container for a raw news article."""

    ticker: str
    source: str
    headline: str
    summary: str
    url: str
    published_at: datetime
    image_url: Optional[str]


def _http_get_json(url: str, params: Dict[str, Any]) -> Any:
    query = urlencode(params)
    full_url = f"{url}?{query}" if query else url
    request = Request(full_url, headers={"User-Agent": "financial-insights-engine/0.1"})
    with urlopen(request, timeout=15) as response:
        payload = response.read()
    return json.loads(payload)


def _to_datetime_from_unix(unix_seconds: Optional[int]) -> Optional[datetime]:
    if unix_seconds is None:
        return None
    try:
        return datetime.utcfromtimestamp(unix_seconds)
    except Exception:
        return None


def _build_article(ticker: str, item: Dict[str, Any]) -> RawArticle:
    return RawArticle(
        ticker=ticker,
        source=item.get("source") or "unknown",
        headline=item.get("headline") or "",
        summary=item.get("summary") or "",
        url=item.get("url") or "",
        published_at=_to_datetime_from_unix(item.get("datetime")) or datetime.utcnow(),
        image_url=item.get("image") or None,
    )


def fetch_company_news(
    ticker: str,
    start: date,
    end: date,
    limit: int = 50,
    allow_dummy: bool = True,
) -> List[RawArticle]:
    """
    Fetch company news from Finnhub within [start, end].

    If `FINNHUB_API_KEY` is not available or the request fails and
    `allow_dummy` is True, returns a small dummy list to keep the pipeline working.
    """
    normalized_ticker = (ticker or "").strip().upper()
    if not normalized_ticker:
        return []

    api_key = os.getenv("FINNHUB_API_KEY")
    if api_key:
        try:
            data = _http_get_json(
                FINNHUB_BASE_URL,
                {
                    "symbol": normalized_ticker,
                    "from": start.isoformat(),
                    "to": end.isoformat(),
                    "token": api_key,
                },
            )

            if not isinstance(data, list):
                data = []

            articles = [_build_article(normalized_ticker, item) for item in data]
            if limit > 0:
                articles = articles[:limit]
            return articles
        except Exception:
            # Fall through to dummy if allowed
            pass

    if not allow_dummy:
        return []

    now = datetime.utcnow()
    dummy = [
        RawArticle(
            ticker=normalized_ticker,
            source="dummy",
            headline=f"{normalized_ticker} announces product update",
            summary=f"{normalized_ticker} shared incremental updates to its product roadmap.",
            url="https://example.com/article/1",
            published_at=now - timedelta(hours=6),
            image_url=None,
        ),
        RawArticle(
            ticker=normalized_ticker,
            source="dummy",
            headline=f"Analyst revises outlook on {normalized_ticker}",
            summary=f"Coverage update with modest changes to near-term revenue expectations.",
            url="https://example.com/article/2",
            published_at=now - timedelta(days=1, hours=2),
            image_url=None,
        ),
    ]
    return dummy[:limit] if limit > 0 else dummy


def fetch_recent_company_news(
    ticker: str,
    days_back: int = 7,
    limit: int = 50,
    allow_dummy: bool = True,
) -> List[RawArticle]:
    """Convenience wrapper to fetch recent news for `ticker` over the last N days."""
    end = date.today()
    start = end - timedelta(days=max(0, days_back))
    return fetch_company_news(ticker=ticker, start=start, end=end, limit=limit, allow_dummy=allow_dummy)


__all__ = [
    "RawArticle",
    "fetch_company_news",
    "fetch_recent_company_news",
]


if __name__ == "__main__":
    # Simple manual test: prints a couple of headlines (dummy if no API key)
    articles = fetch_recent_company_news("QCOM", days_back=3, limit=3)
    for a in articles:
        print(f"[{a.published_at.isoformat()}] {a.ticker}: {a.headline} -> {a.url}")


