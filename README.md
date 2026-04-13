# Stock Earnings Analyzer

Web dashboard plus API for a **small curated list of large-cap (e.g. S&amp;P 500–style) tickers**: latest-quarter **EPS beat / meet / miss vs estimates** (when Yahoo provides estimates), **revenue levels by quarter** (trend), and historical quarter tables. Data is pulled with **`yfinance`** and stored in **SQL** so brief Yahoo outages do not blank the UI.

**Disclaimer:** Yahoo Finance is an unofficial data source. Figures may be wrong, late, or missing—especially revenue estimates.

## Prerequisites

- Python 3.11+
- Node.js 20+ (for the web app)

## 1. API (FastAPI)

Use the **virtualenv’s binaries** (works even when your shell has no global `pip`, or only `pip3`):

```bash
cd api
python3 -m venv .venv
./.venv/bin/python -m pip install -e ".[dev]"
./.venv/bin/alembic upgrade head
./.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Alternative: `source .venv/bin/activate` then run `pip`, `alembic`, and `uvicorn` as usual.

Or from `api/`: `bash run-api.sh` (starts uvicorn; assumes deps already installed).

If you see **`zsh: command not found: pip`** you are not using the venv (or macOS only exposes `pip3`). Prefer `./.venv/bin/python -m pip` as above.

See [api/README.md](api/README.md) for environment variables and `POST /admin/refresh`.

### Changing the ticker cohort (`DEFAULT_TICKERS`)

The default watchlist is a comma-separated list of symbols in the API (see `default_tickers` in [`api/app/config.py`](api/app/config.py)). To customize:

1. Set `DEFAULT_TICKERS=AAPL,MSFT,...` in `api/.env` (or change the default in code).
2. **Restart the API** so new symbols are inserted into the `symbol` table on startup.
3. Trigger ingest: wait for background ingest on boot, or run `curl -X POST http://127.0.0.1:8000/admin/refresh`.

The web app uses the API default unless you set optional `WATCHLIST_TICKERS` in `web/.env.local` (see [`web/.env.example`](web/.env.example)), which adds `?tickers=` to the earnings request.

## 2. Web (Next.js)

In another terminal:

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Ensure `API_URL` in `web/.env.local` matches the API (default `http://127.0.0.1:8000`). Optional: `WATCHLIST_TICKERS` to request a subset or different list without changing the API default.

## Project layout

- `api/` — FastAPI, SQLAlchemy, Alembic, `yfinance` ingest
- `web/` — Next.js App Router UI (table + charts)

## License

Use at your own risk for educational purposes; verify any trading or investment decisions with primary sources.
