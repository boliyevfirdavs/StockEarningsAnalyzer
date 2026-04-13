from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import Settings, get_settings, parse_tickers
from app.db import get_db
from app.ingest import ingest_all_configured, ingest_ticker

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/refresh")
def post_refresh(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    x_refresh_token: str | None = Header(default=None, alias="X-Refresh-Token"),
    tickers: str | None = Query(default=None, description="Optional comma list; default all DEFAULT_TICKERS"),
) -> dict:
    if settings.refresh_secret:
        if x_refresh_token != settings.refresh_secret:
            raise HTTPException(status_code=401, detail="invalid refresh token")
    if tickers:
        for t in parse_tickers(tickers):
            ingest_ticker(db, t, settings)
    else:
        ingest_all_configured(db, settings)
    return {"status": "ok"}
