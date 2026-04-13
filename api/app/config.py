from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./earnings.db"
    default_tickers: str = (
        "AAPL,MSFT,GOOGL,AMZN,NVDA,"
        "META,JPM,JNJ,V,PG,UNH,XOM,COST,WMT,DIS,MA,HD,CVX,BAC,ABBV"
    )
    freshness_hours: int = 24
    max_quarters: int = 12
    refresh_secret: str | None = None
    cors_origins: str = "http://localhost:3000"
    auto_ingest_on_startup: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


def parse_tickers(raw: str) -> list[str]:
    return [t.strip().upper() for t in raw.split(",") if t.strip()]
