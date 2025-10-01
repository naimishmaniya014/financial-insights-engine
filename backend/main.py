from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import requests
import os
from datetime import datetime
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
            title TEXT NOT NULL,
            summary TEXT,
            url TEXT,
            published_date TEXT,
            source TEXT,
            FOREIGN KEY (query_id) REFERENCES queries (id)
        )
    """
    )

    conn.commit()
    conn.close()


# Initialize database on startup
init_database()


class NewsItem(BaseModel):
    title: str
    summary: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[str] = None
    source: Optional[str] = None


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


@app.post("/news/{company_name}", response_model=NewsResponse)
async def get_company_news(company_name: str):
    """
    Get latest financial news for a specific company
    """
    try:
        # Store query in database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO queries (company_name, status) VALUES (?, ?)",
            (company_name, "processing"),
        )
        query_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Get news from Finnhub API (you'll need to set FINNHUB_API_KEY environment variable)
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500, detail="Finnhub API key not configured"
            )

        # Fetch news from Finnhub
        url = f"https://finnhub.io/api/v1/company-news"
        params = {
            "symbol": company_name.upper(),
            "from": (datetime.now().timestamp() - 7 * 24 * 3600),  # Last 7 days
            "to": datetime.now().timestamp(),
            "token": api_key,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        news_data = response.json()

        # Process and store news items
        news_items = []
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        for item in news_data[:10]:  # Limit to top 10 news items
            news_item = NewsItem(
                title=item.get("headline", ""),
                summary=item.get("summary", ""),
                url=item.get("url", ""),
                published_date=(
                    datetime.fromtimestamp(item.get("datetime", 0)).isoformat()
                    if item.get("datetime")
                    else None
                ),
                source=item.get("source", ""),
            )
            news_items.append(news_item)

            # Store in database
            cursor.execute(
                """INSERT INTO news_results 
                   (query_id, title, summary, url, published_date, source) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    query_id,
                    news_item.title,
                    news_item.summary,
                    news_item.url,
                    news_item.published_date,
                    news_item.source,
                ),
            )

        # Update query status
        cursor.execute(
            "UPDATE queries SET status = ? WHERE id = ?", ("completed", query_id)
        )

        conn.commit()
        conn.close()

        return NewsResponse(
            company_name=company_name,
            news_items=news_items,
            query_id=query_id,
            timestamp=datetime.now().isoformat(),
        )

    except requests.RequestException as e:
        # Update query status to failed
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE queries SET status = ? WHERE id = ?", ("failed", query_id)
        )
        conn.commit()
        conn.close()

        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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
