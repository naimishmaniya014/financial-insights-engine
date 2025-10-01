from datetime import datetime

def normalize_articles(articles: list[dict]) -> list[dict]:
    """
    Normalize missing fields and coerce datetime strings.
    """
    out = []
    for a in articles:
        dt = a.get("datetime")
        if isinstance(dt, (int, float)):
            # Finnhub sometimes uses epoch seconds
            dt = datetime.utcfromtimestamp(dt).isoformat()
        elif isinstance(dt, str):
            # try to keep as is
            pass
        else:
            dt = None

        out.append({
            "headline": (a.get("headline") or "").strip(),
            "source": (a.get("source") or "").strip(),
            "datetime": dt,
            "url": (a.get("url") or "").strip(),
            "summary": (a.get("summary") or "").strip(),
        })
    return out
