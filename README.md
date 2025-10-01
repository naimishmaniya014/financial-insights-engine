# Financial Insights Engine (AI100 Accelerated)

## Overview
This project is a financial insights engine powered by Large Language Models (LLMs) and accelerated using Qualcomm’s AI100 hardware. Users can request a digest for a specific company ticker, and the system will fetch news, market data, enrich the results, deduplicate, and generate a concise AI-powered summary with sentiment analysis.

The application is built with a FastAPI backend and is designed to serve quick JSON responses for integration into a mobile or web app.

---

## Key Features
- **API Endpoint**: `GET /news/digest?ticker=QCOM` returns a financial news digest  
- **Validation**: Request parameters are validated and normalized (e.g., ticker uppercasing)  
- **Data Fetching**: Pulls news and market data from external APIs like Finnhub  
- **Preparation**: Cleans, normalizes, tags, and enriches raw articles with metadata  
- **Deduplication**: Detects near-duplicates and selects top K articles by recency, quality, and diversity  
- **LLM Analysis**: Generates one-line summaries per article and infers sentiment scores  
- **Digest Builder**: Groups themes, creates 3–5 bullet takeaways, computes overall sentiment, and attaches citations  
- **Persistence**: Stores articles, features, and digests in PostgreSQL for reuse and subscriptions  
- **Response**: Returns a clean JSON digest back to the client  

---

## Architecture Flow
1. **User Request** → FastAPI endpoint  
2. **Validation** → Checks ticker and request params  
3. **Fetch Stage** → News and market APIs  
4. **Prepare/Enrich** → Clean and feature engineering  
5. **Deduplication** → Remove duplicates, rank, and select  
6. **LLM Analysis** → Per-article summaries and sentiment  
7. **Digest Builder** → Group insights and build final digest  
8. **Database** → Save articles and digest in PostgreSQL  
9. **Response** → Return digest JSON to user  

---
