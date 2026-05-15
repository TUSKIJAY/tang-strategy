# Tang Strategy

Tang Strategy is organized as a frontend/backend workspace for market replay, strategy visualization, browser-side backtesting, and teaching.

## Layout

- `backend/` — FastAPI service, SQLite schema, auth, seed import, and provider stubs.
- `frontend/` — React/Vite app for readonly review, replay backtests, stats, and teaching.
- `strategies/` — strategy JSON definitions.
- `content/` — structured teaching/rules/cases assets.
- `data/seed/` — source JSON seed store.
- `data/sqlite/` — runtime SQLite DB (`tang_strategy_live_extended.db`).

## Runtime defaults

- Source market files: `data/seed/market-data/live_extended/`
- Runtime DB: `data/sqlite/tang_strategy_live_extended.db`

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:18080`, authenticate, then use admin import if needed. The backend API is published at `http://localhost:18091`.

## Run backend only

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

Import/rebuild seed data:

```bash
PYTHONPATH=. python scripts/rebuild_live_extended_db.py
```

## Run frontend only

```bash
cd frontend
npm install
npm run dev
```

## Publish one SPY daily review

With IB Gateway running locally on `127.0.0.1:4001`, run:

```powershell
.\scripts\publish_spy_review.ps1
```

That command fetches the latest completed SPY extended session from IB, writes the active
`live_extended` JSON locally, rebuilds `data/sqlite/tang_strategy_live_extended.db`,
validates a static frontend build, commits the DB update, pushes `main`, and waits for the
existing GitHub Pages workflow to publish the review page.

For a specific day:

```powershell
.\scripts\publish_spy_review.ps1 -Date 2026-05-14
```

The published URL format is:

```text
https://tuskijay.github.io/tang-strategy/#spy-YYYY-MM-DD-extended
```

## Notes

`legacy/` runtime artifacts are removed; current docs and workflows are maintained in `docs/`.
