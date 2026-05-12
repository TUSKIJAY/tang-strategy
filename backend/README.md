# Tang Strategy Backend

FastAPI service for market data management and review payload assembly.

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

## Data source policy (current baseline)

The backend now uses one source format:

- `data/seed/market-data/live_extended/**`

Files are imported into:

- `data/sqlite/tang_strategy_live_extended.db`

## Import commands

```bash
# import/update seed + strategy + teaching assets
PYTHONPATH=. python scripts/import_seed.py

# clean rebuild (delete + import) from live_extended
PYTHONPATH=. python scripts/rebuild_live_extended_db.py
```

## Auth endpoints

`POST /api/auth/login` accepts `TANG_READONLY_PASSWORD` and `TANG_ADMIN_PASSWORD`. 

- Readonly token: `GET` APIs only.
- Admin token: import/rebuild and content-write endpoints.
