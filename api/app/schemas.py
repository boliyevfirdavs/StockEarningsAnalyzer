from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

Result = Literal["beat", "meet", "miss", "unknown"]


class QuarterOut(BaseModel):
    fiscal_quarter_end: dt.date
    eps_actual: float | None = None
    eps_estimate: float | None = None
    revenue_actual: float | None = None
    revenue_estimate: float | None = None
    eps_surprise_pct: float | None = None
    revenue_surprise_pct: float | None = None
    eps_result: Result
    revenue_result: Result


class SyncOut(BaseModel):
    last_attempt_at: dt.datetime | None = None
    last_success_at: dt.datetime | None = None
    last_error: str | None = None
    is_stale: bool = False
    never_synced: bool = False


class CompanyOut(BaseModel):
    ticker: str
    sync: SyncOut
    quarters: list[QuarterOut]


class EarningsResponse(BaseModel):
    freshness_hours: int = Field(description="Hours after last success before is_stale=true")
    companies: list[CompanyOut]
