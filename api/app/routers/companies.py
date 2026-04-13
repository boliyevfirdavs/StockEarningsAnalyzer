from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import Settings, get_settings, parse_tickers
from app.db import get_db
from app.repository import load_companies_with_quarters
from app.schemas import CompanyOut, EarningsResponse, QuarterOut, SyncOut

router = APIRouter(prefix="/companies", tags=["companies"])


def _to_utc(value: dt.datetime | None) -> dt.datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=dt.UTC)
    return value.astimezone(dt.UTC)


def _is_stale(last_success: dt.datetime | None, last_error: str | None, freshness: dt.timedelta) -> bool:
    if last_error:
        return True
    ok = _to_utc(last_success)
    if ok is None:
        return True
    return dt.datetime.now(dt.UTC) - ok > freshness


@router.get("/earnings", response_model=EarningsResponse)
def get_earnings(
    tickers: str | None = Query(
        default=None,
        description="Comma-separated tickers; defaults to DEFAULT_TICKERS from env",
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> EarningsResponse:
    if tickers:
        want = parse_tickers(tickers)
    else:
        want = parse_tickers(settings.default_tickers)
    freshness = dt.timedelta(hours=settings.freshness_hours)
    companies_orm = load_companies_with_quarters(db, want)
    by_ticker = {c.ticker: c for c in companies_orm}

    companies: list[CompanyOut] = []
    for t in want:
        sym = by_ticker.get(t)
        if sym is None:
            companies.append(
                CompanyOut(
                    ticker=t,
                    sync=SyncOut(never_synced=True, is_stale=True),
                    quarters=[],
                )
            )
            continue
        st = sym.sync_state
        last_ok = st.last_success_at if st else None
        last_err = st.last_error if st else None
        last_attempt = st.last_attempt_at if st else None
        never = last_ok is None and (st is None or not sym.quarters)
        stale = never or _is_stale(last_ok, last_err, freshness)

        quarters = sorted(sym.quarters, key=lambda q: q.fiscal_quarter_end, reverse=True)
        companies.append(
            CompanyOut(
                ticker=sym.ticker,
                sync=SyncOut(
                    last_attempt_at=last_attempt,
                    last_success_at=last_ok,
                    last_error=last_err,
                    is_stale=stale,
                    never_synced=never and not sym.quarters,
                ),
                quarters=[
                    QuarterOut(
                        fiscal_quarter_end=q.fiscal_quarter_end,
                        eps_actual=float(q.eps_actual) if q.eps_actual is not None else None,
                        eps_estimate=float(q.eps_estimate) if q.eps_estimate is not None else None,
                        revenue_actual=float(q.revenue_actual) if q.revenue_actual is not None else None,
                        revenue_estimate=float(q.revenue_estimate) if q.revenue_estimate is not None else None,
                        eps_surprise_pct=float(q.eps_surprise_pct) if q.eps_surprise_pct is not None else None,
                        revenue_surprise_pct=float(q.revenue_surprise_pct)
                        if q.revenue_surprise_pct is not None
                        else None,
                        eps_result=q.eps_result,  # type: ignore[arg-type]
                        revenue_result=q.revenue_result,  # type: ignore[arg-type]
                    )
                    for q in quarters
                ],
            )
        )

    return EarningsResponse(freshness_hours=settings.freshness_hours, companies=companies)
