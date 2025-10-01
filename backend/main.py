from fastapi import FastAPI

app = FastAPI()

@app.get("/news/digest")
async def get_digest(ticker: str):
    return {"ticker": ticker, "digest": "Sample response - workflow integration coming soon!"}
