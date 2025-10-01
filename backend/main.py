from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import finnhub
import os
from datetime import datetime, timedelta
import json

app = FastAPI(title="Financial News API", version="1.0.0")

# CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_PATH = "../database/financial_news.db"


def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create queries table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """
    )

    # Create news_results table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS news_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_id INTEGER,
            headline TEXT NOT NULL,
            summary TEXT,
            url TEXT,
            published_date TEXT,
            source TEXT,
            category TEXT,
            image_url TEXT,
            finnhub_id INTEGER,
            related_ticker TEXT,
            FOREIGN KEY (query_id) REFERENCES queries (id)
        )
    """
    )

    conn.commit()
    conn.close()


# Initialize database on startup
init_database()


class NewsItem(BaseModel):
    headline: str
    summary: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[str] = None
    source: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    finnhub_id: Optional[int] = None
    related_ticker: Optional[str] = None


class NewsResponse(BaseModel):
    company_name: str
    news_items: List[NewsItem]
    query_id: int
    timestamp: str


@app.get("/")
async def root():
    return {"message": "Financial News API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/news", response_model=NewsResponse)
async def get_company_news(
    ticker: str = Query(..., description="Company ticker symbol (e.g., AAPL, MSFT)"),
    from_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    max_articles: int = Query(
        3, ge=1, le=10, description="Maximum number of articles to return (1-10)"
    ),
):
    """
    Get financial news for a specific company ticker within a date range
    """
    try:
        # Validate and parse dates
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

        if from_dt >= to_dt:
            raise HTTPException(
                status_code=400, detail="from_date must be before to_date"
            )

        # Store query in database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queries (company_name, status) VALUES (?, ?)",
            (ticker.upper(), "processing"),
        )
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Get news from Finnhub API
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, detail="Finnhub API key not configured"
            )

        # Initialize Finnhub client
        finnhub_client = finnhub.Client(api_key=api_key)

        # Fetch news from Finnhub
        news_data = finnhub_client.company_news(
            ticker.upper(), _from=from_date, to=to_date
        )

        # Process and store news items
        news_items = []
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Limit to max_articles and process
        for item in news_data[:max_articles]:
            news_item = NewsItem(
                headline=item.get("headline", ""),
                summary=item.get("summary", ""),
                url=item.get("url", ""),
                published_date=(
                    datetime.fromtimestamp(item.get("datetime", 0)).isoformat()
                    if item.get("datetime")
                    else None
                ),
                source=item.get("source", ""),
                category=item.get("category", ""),
                image_url=item.get("image", ""),
                finnhub_id=item.get("id"),
                related_ticker=item.get("related", ""),
            )
            news_items.append(news_item)

            # Store in database
            cursor.execute(
                """INSERT INTO news_results 
                   (query_id, headline, summary, url, published_date, source, 
                    category, image_url, finnhub_id, related_ticker) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    query_id,
                    news_item.headline,
                    news_item.summary,
                    news_item.url,
                    news_item.published_date,
                    news_item.source,
                    news_item.category,
                    news_item.image_url,
                    news_item.finnhub_id,
                    news_item.related_ticker,
                ),
            )

        # Update query status
        cursor.execute(
            "UPDATE queries SET status = ? WHERE id = ?", ("completed", query_id)
        )

        conn.commit()
        conn.close()

        return NewsResponse(
            company_name=ticker.upper(),
            news_items=news_items,
            query_id=query_id,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        # Update query status to failed
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE queries SET status = ? WHERE id = ?", ("failed", query_id)
            )
            conn.commit()
            conn.close()
        except:
            pass  # If we can't update the status, continue with error

        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")


@app.get("/queries")
async def get_all_queries():
    """Get all previous queries"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queries ORDER BY timestamp DESC")
    queries = cursor.fetchall()
    conn.close()

    return {"queries": queries}


@app.get("/queries/{query_id}/news")
async def get_news_by_query_id(query_id: int):
    """Get news results for a specific query"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Get query info
    cursor.execute("SELECT * FROM queries WHERE id = ?", (query_id,))
    query = cursor.fetchone()

    if not query:
        raise HTTPException(status_code=404, detail="Query not found")

    # Get news results
    cursor.execute("SELECT * FROM news_results WHERE query_id = ?", (query_id,))
    news_results = cursor.fetchall()
    conn.close()

    return {"query": query, "news_results": news_results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
