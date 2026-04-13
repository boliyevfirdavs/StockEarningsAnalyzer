import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import select

from app.models import Base, Symbol
from app.repository import ensure_symbols, load_companies_with_quarters, upsert_quarters


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_ensure_symbols_idempotent(db_session):
    ensure_symbols(db_session, ["AAPL", "MSFT"])
    ensure_symbols(db_session, ["AAPL", "NVDA"])
    rows = list(db_session.scalars(select(Symbol).order_by(Symbol.ticker)).all())
    assert [r.ticker for r in rows] == ["AAPL", "MSFT", "NVDA"]


def test_upsert_quarters_updates_existing(db_session):
    ensure_symbols(db_session, ["AAPL"])
    sym = db_session.scalars(select(Symbol)).one()
    upsert_quarters(
        db_session,
        sym,
        [
            {
                "fiscal_quarter_end": dt.date(2024, 12, 31),
                "eps_actual": 1.0,
                "eps_estimate": 0.9,
                "revenue_actual": 100.0,
                "revenue_estimate": None,
                "eps_surprise_pct": 10.0,
                "revenue_surprise_pct": None,
                "eps_result": "beat",
                "revenue_result": "unknown",
            }
        ],
    )
    upsert_quarters(
        db_session,
        sym,
        [
            {
                "fiscal_quarter_end": dt.date(2024, 12, 31),
                "eps_actual": 1.1,
                "eps_estimate": 0.9,
                "revenue_actual": 100.0,
                "revenue_estimate": None,
                "eps_surprise_pct": 22.0,
                "revenue_surprise_pct": None,
                "eps_result": "beat",
                "revenue_result": "unknown",
            }
        ],
    )
    loaded = load_companies_with_quarters(db_session, ["AAPL"])
    assert len(loaded) == 1
    q = loaded[0].quarters[0]
    assert float(q.eps_actual) == pytest.approx(1.1)
