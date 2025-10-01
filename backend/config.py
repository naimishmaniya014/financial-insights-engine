from pydantic import BaseSettings

class Settings(BaseSettings):
    FINNHUB_API_KEY: str = "REPLACE_ME"  # or load from .env
    NEWS_WINDOW_DAYS: int = 7

settings = Settings()
