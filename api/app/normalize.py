"""Pure normalization: estimate vs actual -> beat / meet / miss / unknown."""

from __future__ import annotations

from decimal import Decimal
from typing import Literal

Result = Literal["beat", "meet", "miss", "unknown"]

MEET_EPS = Decimal("0.005")
MEET_REV_PCT = Decimal("0.001")  # 0.1% of estimate for large revenue numbers


def _to_decimal(v: float | int | Decimal | None) -> Decimal | None:
    if v is None:
        return None
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def classify_eps(actual: float | None, estimate: float | None) -> Result:
    a, e = _to_decimal(actual), _to_decimal(estimate)
    if a is None or e is None:
        return "unknown"
    diff = a - e
    if diff > MEET_EPS:
        return "beat"
    if diff < -MEET_EPS:
        return "miss"
    return "meet"


def classify_revenue(actual: float | None, estimate: float | None) -> Result:
    a, e = _to_decimal(actual), _to_decimal(estimate)
    if a is None or e is None:
        return "unknown"
    if e == 0:
        return "unknown"
    rel = abs(a - e) / abs(e)
    if rel <= MEET_REV_PCT:
        return "meet"
    if a > e:
        return "beat"
    return "miss"


def surprise_pct(actual: float | None, estimate: float | None) -> float | None:
    a, e = _to_decimal(actual), _to_decimal(estimate)
    if a is None or e is None or e == 0:
        return None
    return float((a - e) / abs(e) * Decimal("100"))
