from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, parse_tickers
from app.db import SessionLocal
from app.ingest import ingest_all_configured
from app.repository import ensure_symbols
from app.routers import admin, companies

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _background_ingest() -> None:
    try:
        settings = get_settings()
        db = SessionLocal()
        try:
            ingest_all_configured(db, settings)
        finally:
            db.close()
    except Exception:
        logger.exception("background ingest failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    db = SessionLocal()
    try:
        tickers = parse_tickers(settings.default_tickers)
        ensure_symbols(db, tickers)
    finally:
        db.close()
    if settings.auto_ingest_on_startup:
        threading.Thread(target=_background_ingest, daemon=True).start()
    yield


app = FastAPI(title="Stock Earnings Analyzer API", lifespan=lifespan)
_settings = get_settings()
_origins = [o.strip() for o in _settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(companies.router)
app.include_router(admin.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
