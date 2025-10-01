import httpx
from datetime import datetime, timedelta
from config import settings

BASE_URL = "https://finnhub.io/api/v1/company-news"

async def fetch_recent_news(ticker: str):
    """
    Fetch recent news from Finnhub (or stub if no key).
    """
    if settings.FINNHUB_API_KEY == "REPLACE_ME":
        # Stub data if API key not set (useful for local dev & tests)
        return [
            {"headline": f"{ticker} launches new product", "source": "Example",
             "datetime": datetime.utcnow().isoformat(), "url": "https://example.com/a"},
            {"headline": f"{ticker} beats earnings", "source": "Example",
             "datetime": datetime.utcnow().isoformat(), "url": "https://example.com/b"},
            {"headline": f"{ticker} leadership change", "source": "Example",
             "datetime": datetime.utcnow().isoformat(), "url": "https://example.com/c"},
        ]

    _to = datetime.utcnow().date()
    _from = _to - timedelta(days=settings.NEWS_WINDOW_DAYS)

    params = {
        "symbol": ticker,
        "from": _from.isoformat(),
        "to": _to.isoformat(),
        "token": settings.FINNHUB_API_KEY,
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()

    # Normalize to a consistent shape
    return [
        {
            "headline": item.get("headline", ""),
            "source": item.get("source", ""),
            "datetime": item.get("datetime"),
            "url": item.get("url", ""),
            "summary": item.get("summary", ""),
        }
        for item in data
    ]
