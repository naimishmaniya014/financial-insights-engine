def deduplicate_articles(articles: list[dict]) -> list[dict]:
    """
    Simple URL + headline de-duplication.
    """
    seen = set()
    unique = []
    for a in articles:
        key = (a.get("url"), a.get("headline"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(a)
    return unique
