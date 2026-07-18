# Tang Strategy Backend

FastAPI service for authenticated market data access, SQLite-backed review assembly, controlled imports, and static review export.

## Run Locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

TradingView fetch/tests additionally require the pins in `requirements-tv.txt`.

## Data Contract

- Accepted market seed: `data/seed/market-data/live_extended/<YYYY-MM-DD>/SPY_<YYYY-MM-DD>.json` (and the equivalent SPX name).
- Tracked runtime/Pages input: `data/sqlite/tang_strategy_live_extended.db`.
- Safe rebuild: `PYTHONPATH=. python scripts/rebuild_live_extended_db.py`.

Rebuild imports into a candidate and refuses empty/invalid bars, count disagreement, integrity/foreign-key failure, market-day loss, strategy/teaching shrink, or live DB drift. `--allow-date-loss` is an explicit supervised override for intentional market-day shrink only.

## API Surface

- `POST /api/auth/login` — exchange the configured readonly/admin password for a bearer token.
- `GET /api/health`
- `GET /api/tickers`
- `GET /api/market-days` and `GET /api/market-days/{market_day_id}`
- `GET /api/market-days/{market_day_id}/bars?timeframe=1m|5m`
- `GET /api/strategies` and `GET /api/strategies/{strategy_id}`
- `GET /api/reviews/assemble?market_day_id=<id>&strategy_id=<id>`
- `GET /api/teaching/{asset_type}`
- admin-only: `POST /api/admin/import/seed`, `/api/admin/import/market-json`, `/api/admin/import/strategy-json`

There is no rebuild or content-write HTTP endpoint. Repository-managed DB writes share the same lock used by recovery/rebuild promotion.

## Static Export

`scripts/export_static_reviews.py` reads the tracked DB and writes generated JSON to an explicit output directory, normally `frontend/public/reviews` in CI. It does not publish by itself.
