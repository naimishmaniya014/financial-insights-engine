from fastapi import FastAPI, HTTPException, Query
from orchestrator import build_company_digest

app = FastAPI(title="Financial Insights Engine", version="0.1.0")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/news/digest")
async def news_digest(ticker: str = Query(..., min_length=1, max_length=8)):
    """
    Public endpoint that orchestrates fetching, cleaning,
    deduplication, summarization, and digest building.
    """
    try:
        result = await build_company_digest(ticker.upper())
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
