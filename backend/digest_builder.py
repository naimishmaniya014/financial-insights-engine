from collections import Counter

def build_digest_payload(ticker: str, articles: list[dict]) -> dict:
    """
    Create a compact digest: top bullets + overall sentiment.
    """
    sentiments = [a.get("sentiment", "neutral") for a in articles]
    counts = Counter(sentiments)
    # majority sentiment (with neutral as fallback)
    overall = max(counts, key=counts.get) if counts else "neutral"

    bullets = []
    for a in articles[:5]:  # top 3–5 bullets
        bullets.append({
            "headline": a.get("headline"),
            "summary": a.get("summary5"),
            "sentiment": a.get("sentiment"),
            "source": a.get("source"),
            "url": a.get("url"),
        })

    return {
        "ticker": ticker,
        "overall_sentiment": overall,
        "bullets": bullets,
        "count": len(articles),
    }
