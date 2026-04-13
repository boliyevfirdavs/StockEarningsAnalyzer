# Stock Earnings Analyzer

Web dashboard plus API for a **curated multi-sector S&amp;P 500–style watchlist** (default ~46 liquid names from mega-cap through large-cap tiers): latest-quarter **EPS beat / meet / miss vs estimates** (when Yahoo provides estimates), **revenue levels by quarter** (trend), and historical quarter tables. Data is pulled with **`yfinance`** and stored in **SQL** so brief Yahoo outages do not blank the UI.

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

### Changing the ticker cohort

The default watchlist is defined in [`api/app/config.py`](api/app/config.py). To override without editing code:

1. Create `api/.env` (see [`api/.env.example`](api/.env.example)) and set **`STOCK_EARNINGS_DEFAULT_TICKERS=AAPL,MSFT,...`** (comma-separated). **Do not use `DEFAULT_TICKERS`** — many tutorials set that env var to a short five-ticker list; this project **ignores** `DEFAULT_TICKERS` so stray shell exports cannot shrink your cohort.
2. **Restart the API** so new symbols are inserted into the `symbol` table on startup.
3. Trigger ingest: wait for background ingest on boot, or run `curl -X POST http://127.0.0.1:8000/admin/refresh`.

The web app uses the API default unless you set optional **`STOCK_EARNINGS_DASHBOARD_TICKERS`** in `web/.env.local` (see [`web/.env.example`](web/.env.example)), which adds `?tickers=` to the earnings request.

## 2. Web (Next.js)

In another terminal:

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

Or a single helper (no inline `#` comments—safer when pasting from chat):

```bash
bash web/setup.sh
cd web && npm run dev
```

**If you see `cp: needed: Not a directory`:** `cp` was given extra words (`if`, `needed`)—usually the `#` comment was dropped or `#` was not recognized. Run **`cp .env.example .env.local`** alone, or use **`bash web/setup.sh`**.

**If you see `npm error Invalid tag name "#"`:** `npm` received `#` as a package name—often from **`npm install # ...`** in **cmd.exe** (where `#` is not a comment) or a bad paste. Run **`npm install`** with no arguments from the **`web/`** directory, or use **`bash web/setup.sh`**.

**If the dashboard shows fewer tickers than you expect:** (1) Run `curl -s http://127.0.0.1:8000/health/cohort` — expect **`symbol_count": 46`** with the stock default (this ignores stray `DEFAULT_TICKERS` in your shell). (2) Run `curl -sI http://127.0.0.1:8000/companies/earnings | grep -i x-cohort` — same number in **`X-Cohort-Size`**. (3) Use **`STOCK_EARNINGS_DEFAULT_TICKERS`** in `api/.env` only to override the API cohort. (4) In `web/.env.local`, **delete** **`STOCK_EARNINGS_DASHBOARD_TICKERS`** if present; restart **`npm run dev`**. (5) Check the API **uvicorn log** on startup for `Earnings cohort: N symbols`.

Open [http://localhost:3000](http://localhost:3000). Ensure `API_URL` in `web/.env.local` matches the API (default `http://127.0.0.1:8000`). Optional: `STOCK_EARNINGS_DASHBOARD_TICKERS` to request a subset without changing the API default.

## Project layout

- `api/` — FastAPI, SQLAlchemy, Alembic, `yfinance` ingest
- `web/` — Next.js App Router UI (table + charts)

## License

Use at your own risk for educational purposes; verify any trading or investment decisions with primary sources.
