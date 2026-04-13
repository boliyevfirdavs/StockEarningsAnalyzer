from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(_API_ROOT / ".env", override=False)

_DEFAULT_TICKERS = (
    "AAPL,MSFT,GOOGL,AMZN,NVDA,"
    "META,JPM,JNJ,V,PG,UNH,XOM,COST,WMT,DIS,MA,HD,CVX,BAC,ABBV,"
    "TSLA,BRK-B,CRM,ADBE,ORCL,CSCO,AVGO,AMD,INTC,"
    "LLY,MRK,PFE,KO,PEP,MCD,NKE,BA,CAT,UPS,GS,MS,"
    "NFLX,CMCSA,NEE,COP,EOG"
)


class Settings(BaseSettings):
    """Ticker cohort is NOT a field here — Pydantic would map `default_tickers` to env `DEFAULT_TICKERS` and break with common shell exports. Use `configured_tickers()` instead."""

    model_config = SettingsConfigDict(
        env_file=str(_API_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./earnings.db"
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


def cohort_tickers_csv() -> str:
    v = (os.environ.get("STOCK_EARNINGS_DEFAULT_TICKERS") or "").strip()
    return v if v else _DEFAULT_TICKERS


def configured_tickers() -> list[str]:
    return parse_tickers(cohort_tickers_csv())
