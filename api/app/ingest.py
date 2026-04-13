from __future__ import annotations

import datetime as dt
import logging
from typing import Any

import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session

from app.config import Settings, configured_tickers, get_settings
from app.normalize import classify_eps, classify_revenue, surprise_pct
from app.repository import get_symbol_by_ticker, update_sync_state, upsert_quarters

logger = logging.getLogger(__name__)


def _match_earnings_row(ed_df: pd.DataFrame, eps_actual: float | None) -> pd.Series | None:
    if eps_actual is None or ed_df is None or ed_df.empty:
        return None
    for _, erow in ed_df.sort_index(ascending=False).iterrows():
        rep = erow.get("Reported EPS")
        if pd.isna(rep):
            continue
        try:
            if abs(float(rep) - float(eps_actual)) < 0.02:
                return erow
        except (TypeError, ValueError):
            continue
    return None


def fetch_quarters_yfinance(ticker: str, max_quarters: int) -> list[dict[str, Any]]:
    t = yf.Ticker(ticker)
    inc = t.quarterly_income_stmt
    fin = t.quarterly_financials
    try:
        ed = t.earnings_dates
    except Exception as exc:  # pragma: no cover - network
        logger.warning("earnings_dates failed for %s: %s", ticker, exc)
        ed = None

    if inc is None or fin is None:
        return []
    if "Total Revenue" not in inc.index or "Diluted EPS" not in fin.index:
        return []

    cols = [c for c in inc.columns if c in fin.columns]
    cols = sorted(cols, key=lambda x: pd.Timestamp(x), reverse=True)[:max_quarters]

    ed_df = ed if ed is not None and len(ed) else None

    rows: list[dict[str, Any]] = []
    for col in cols:
        fiscal_end = pd.Timestamp(col).date()
        rev_raw = inc.loc["Total Revenue", col]
        eps_raw = fin.loc["Diluted EPS", col]
        revenue_actual = float(rev_raw) if pd.notna(rev_raw) else None
        eps_actual = float(eps_raw) if pd.notna(eps_raw) else None

        eps_estimate: float | None = None
        eps_surprise_pct: float | None = None
        match = _match_earnings_row(ed_df, eps_actual) if ed_df is not None else None
        if match is not None:
            eest = match.get("EPS Estimate")
            if pd.notna(eest):
                eps_estimate = float(eest)
            sur = match.get("Surprise(%)")
            if pd.notna(sur):
                eps_surprise_pct = float(sur)
        if eps_surprise_pct is None:
            eps_surprise_pct = surprise_pct(eps_actual, eps_estimate)

        revenue_estimate: float | None = None
        revenue_surprise_pct: float | None = surprise_pct(revenue_actual, revenue_estimate)

        rows.append(
            {
                "fiscal_quarter_end": fiscal_end,
                "eps_actual": eps_actual,
                "eps_estimate": eps_estimate,
                "revenue_actual": revenue_actual,
                "revenue_estimate": revenue_estimate,
                "eps_surprise_pct": eps_surprise_pct,
                "revenue_surprise_pct": revenue_surprise_pct,
                "eps_result": classify_eps(eps_actual, eps_estimate),
                "revenue_result": classify_revenue(revenue_actual, revenue_estimate),
            }
        )
    return rows


def ingest_ticker(db: Session, ticker: str, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    now = dt.datetime.now(dt.UTC)
    sym = get_symbol_by_ticker(db, ticker)
    if sym is None:
        raise ValueError(f"unknown ticker {ticker}")
    try:
        rows = fetch_quarters_yfinance(ticker, settings.max_quarters)
        upsert_quarters(db, sym, rows)
        update_sync_state(db, sym, attempt_at=now, success=True, error=None)
    except Exception as exc:
        logger.exception("ingest failed for %s", ticker)
        update_sync_state(db, sym, attempt_at=now, success=False, error=str(exc))


def ingest_all_configured(db: Session, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    tickers = configured_tickers()
    for t in tickers:
        ingest_ticker(db, t, settings)
