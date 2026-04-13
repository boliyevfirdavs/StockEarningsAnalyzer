# Stock Earnings API

FastAPI service that ingests Yahoo Finance data via `yfinance`, stores normalized quarterly rows in SQL, and serves read-only JSON to the Next.js app.

## Setup

```bash
cd api
python3 -m venv .venv
./.venv/bin/python -m pip install -e ".[dev]"
./.venv/bin/alembic upgrade head
```

On macOS, `pip` may not exist on your PATH even when Python does; **`./.venv/bin/python -m pip`** always targets this project’s venv.

## Run

```bash
cd api
./.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or: `bash run-api.sh` from this directory (same as the `uvicorn` line above).

On startup, default tickers from `DEFAULT_TICKERS` are ensured in the DB. If `AUTO_INGEST_ON_STARTUP=true` (default), a background thread runs a full ingest.

### Changing `DEFAULT_TICKERS`

1. Set `DEFAULT_TICKERS` in `api/.env` to a comma-separated list (no spaces required).
2. **Restart the process** so `ensure_symbols` runs again and adds any new tickers.
3. Run `POST /admin/refresh` (or rely on the next startup ingest) to load quarters for new symbols.

The baked-in default is defined in `app/config.py` (~20 large-cap names). Override via env for a custom cohort without editing code.

## Refresh data

```bash
curl -X POST http://127.0.0.1:8000/admin/refresh
```

Optional: `POST /admin/refresh?tickers=AAPL,MSFT`. If `REFRESH_SECRET` is set, pass header `X-Refresh-Token: <secret>`.

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///./earnings.db` | SQLAlchemy URL (Postgres supported) |
| `DEFAULT_TICKERS` | ~20 mega-caps (see `app/config.py`) | Comma-separated cohort to seed and ingest |
| `FRESHNESS_HOURS` | `24` | API marks sync stale after this age |
| `MAX_QUARTERS` | `12` | Quarters to keep per ingest |
| `AUTO_INGEST_ON_STARTUP` | `true` | Background ingest on API boot |
| `REFRESH_SECRET` | unset | If set, required for `/admin/refresh` |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

## Tests

```bash
cd api
./.venv/bin/pytest
```
