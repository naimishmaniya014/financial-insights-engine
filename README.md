# Financial News Dashboard

A simple web application that fetches and displays financial news for specific companies using the Finnhub API.

## Features

- **FastAPI Backend**: RESTful API for fetching financial news
- **Simple UI**: Clean, responsive web interface for entering company symbols
- **SQLite Database**: Stores query history and news results
- **Real-time News**: Fetches latest financial news from Finnhub API

## Project Structure

```
financial-news-dashboard/
├── backend/
│   └── main.py              # FastAPI application
├── frontend/
│   └── index.html           # Web UI
├── database/
│   └── financial_news.db    # SQLite database (created automatically)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Finnhub API Key

1. Go to [Finnhub.io](https://finnhub.io/)
2. Sign up for a free account
3. Get your API key from the dashboard

### 3. Set Environment Variable

```bash
export FINNHUB_API_KEY="your_api_key_here"
```

Or create a `.env` file in the project root:

```
FINNHUB_API_KEY=your_api_key_here
```

### 4. Start Both Servers

**Easy way (recommended):**

```bash
./start.sh
```

This will start both backend and frontend servers automatically.

**Manual way:**

```bash
# Terminal 1 - Backend
source venv/bin/activate
export FINNHUB_API_KEY="your_api_key_here"
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 3000
```

### 5. Access the Application

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 6. Stop the Servers

**If using start.sh:**

- Press `Ctrl+C` in the terminal where you ran `./start.sh`

**Manual stop:**

```bash
./stop.sh
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - API status
- `POST /news/{company_name}` - Get news for a company
- `GET /queries` - Get all previous queries
- `GET /queries/{query_id}/news` - Get news for a specific query

## Usage

1. Enter a company symbol (e.g., AAPL, MSFT, GOOGL) in the search box
2. Click "Search News" to fetch the latest financial news
3. View the results in a clean, card-based layout
4. Access previous queries in the history section

## Database Schema

### queries table

- `id`: Primary key
- `company_name`: Company symbol searched
- `timestamp`: When the query was made
- `status`: Query status (pending, processing, completed, failed)

### news_results table

- `id`: Primary key
- `query_id`: Foreign key to queries table
- `title`: News headline
- `summary`: News summary
- `url`: Link to full article
- `published_date`: When the news was published
- `source`: News source

## Notes

- The free Finnhub API has rate limits
- News is fetched for the last 7 days
- Results are limited to the top 10 news items
- All queries and results are stored in the SQLite database
