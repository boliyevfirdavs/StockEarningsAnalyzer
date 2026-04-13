from __future__ import annotations

import datetime as dt

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Symbol(Base):
    __tablename__ = "symbol"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC))

    quarters: Mapped[list[EarningsQuarter]] = relationship(back_populates="symbol", cascade="all, delete-orphan")
    sync_state: Mapped[SymbolSyncState | None] = relationship(
        back_populates="symbol", cascade="all, delete-orphan", uselist=False
    )


class EarningsQuarter(Base):
    __tablename__ = "earnings_quarter"
    __table_args__ = (UniqueConstraint("symbol_id", "fiscal_quarter_end", name="uq_symbol_quarter"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbol.id", ondelete="CASCADE"), nullable=False, index=True)
    fiscal_quarter_end: Mapped[dt.date] = mapped_column(Date, nullable=False)

    eps_actual: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    eps_estimate: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    revenue_actual: Mapped[float | None] = mapped_column(Numeric(24, 2), nullable=True)
    revenue_estimate: Mapped[float | None] = mapped_column(Numeric(24, 2), nullable=True)
    eps_surprise_pct: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    revenue_surprise_pct: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)

    eps_result: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")
    revenue_result: Mapped[str] = mapped_column(String(16), nullable=False, default="unknown")

    symbol: Mapped[Symbol] = relationship(back_populates="quarters")


class SymbolSyncState(Base):
    __tablename__ = "symbol_sync_state"

    symbol_id: Mapped[int] = mapped_column(ForeignKey("symbol.id", ondelete="CASCADE"), primary_key=True)
    last_attempt_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    symbol: Mapped[Symbol] = relationship(back_populates="sync_state")
