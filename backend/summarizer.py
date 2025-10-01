# NOTE:
# For Sprint 1, we stub the LLM. In Sprint 2, we’ll route to AI100-accelerated LLM.
# Keep the same function signature so later work is a drop-in replacement.

async def summarize_and_score(articles: list[dict], ticker: str) -> list[dict]:
    """
    Returns each article with 'summary5' (<=5 lines) and 'sentiment' in {positive, neutral, negative}.
    Stubbed heuristics for now.
    """
    annotated = []
    for a in articles:
        headline = a.get("headline", "")
        # naive sentiment heuristic
        h = headline.lower()
        if any(k in h for k in ["beats", "record", "surge", "increase", "growth", "upgrade"]):
            sentiment = "positive"
        elif any(k in h for k in ["misses", "plunge", "drop", "downgrade", "lawsuit"]):
            sentiment = "negative"
        else:
            sentiment = "neutral"

        summary5 = a.get("summary") or f"{ticker}: {headline} — details to follow."
        annotated.append({**a, "summary5": summary5[:500], "sentiment": sentiment})
    return annotated
