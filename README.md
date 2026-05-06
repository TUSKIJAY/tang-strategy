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

Open `http://localhost:8080`, authenticate, then use admin import if needed.

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

## Notes

`legacy/` runtime artifacts are removed; current docs and workflows are maintained in `docs/`.
