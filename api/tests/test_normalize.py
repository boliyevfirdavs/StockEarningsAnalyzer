import pytest

from app.normalize import classify_eps, classify_revenue, surprise_pct


@pytest.mark.parametrize(
    "actual,estimate,expected",
    [
        (1.5, 1.0, "beat"),
        (1.0, 1.5, "miss"),
        (1.0, 1.0, "meet"),
        (1.004, 1.0, "meet"),
        (None, 1.0, "unknown"),
        (1.0, None, "unknown"),
    ],
)
def test_classify_eps(actual, estimate, expected):
    assert classify_eps(actual, estimate) == expected


@pytest.mark.parametrize(
    "actual,estimate,expected",
    [
        (110.0, 100.0, "beat"),
        (90.0, 100.0, "miss"),
        (100.0, 100.0, "meet"),
        (100.05e9, 100e9, "meet"),
        (None, 100.0, "unknown"),
        (100.0, None, "unknown"),
        (100.0, 0.0, "unknown"),
    ],
)
def test_classify_revenue(actual, estimate, expected):
    assert classify_revenue(actual, estimate) == expected


def test_surprise_pct():
    assert surprise_pct(110.0, 100.0) == pytest.approx(10.0)
    assert surprise_pct(None, 100.0) is None
