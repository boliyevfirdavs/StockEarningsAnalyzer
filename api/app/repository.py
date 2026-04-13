from __future__ import annotations

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import EarningsQuarter, Symbol, SymbolSyncState


def ensure_symbols(db: Session, tickers: list[str]) -> None:
    existing = {s.ticker for s in db.scalars(select(Symbol)).all()}
    for t in tickers:
        if t not in existing:
            db.add(Symbol(ticker=t))
    db.commit()


def get_symbol_by_ticker(db: Session, ticker: str) -> Symbol | None:
    return db.scalar(select(Symbol).where(Symbol.ticker == ticker))


def upsert_quarters(
    db: Session,
    symbol: Symbol,
    rows: list[dict],
) -> None:
    """rows: dicts with keys matching EarningsQuarter fields (no id/symbol_id)."""
    existing = {
        q.fiscal_quarter_end: q
        for q in db.scalars(
            select(EarningsQuarter).where(EarningsQuarter.symbol_id == symbol.id)
        ).all()
    }
    for data in rows:
        end = data["fiscal_quarter_end"]
        if end in existing:
            q = existing[end]
            for k, v in data.items():
                setattr(q, k, v)
        else:
            db.add(EarningsQuarter(symbol_id=symbol.id, **data))
    db.commit()


def update_sync_state(
    db: Session,
    symbol: Symbol,
    *,
    attempt_at: dt.datetime,
    success: bool,
    error: str | None,
) -> None:
    st = db.get(SymbolSyncState, symbol.id)
    if st is None:
        st = SymbolSyncState(symbol_id=symbol.id)
        db.add(st)
    st.last_attempt_at = attempt_at
    if success:
        st.last_success_at = attempt_at
        st.last_error = None
    else:
        st.last_error = (error or "unknown error")[:2000]
    db.commit()


def load_companies_with_quarters(db: Session, tickers: list[str]) -> list[Symbol]:
    stmt = (
        select(Symbol)
        .where(Symbol.ticker.in_(tickers))
        .options(
            selectinload(Symbol.quarters),
            selectinload(Symbol.sync_state),
        )
        .order_by(Symbol.ticker)
    )
    return list(db.scalars(stmt).all())
