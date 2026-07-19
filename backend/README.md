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

- Accepted internal/candidate market seeds: `data/seed/market-data/live_extended/<YYYY-MM-DD>/<TICKER>_<YYYY-MM-DD>.json` for SPY, QQQ, and the existing SPX format.
- Tracked runtime/Pages input: `data/sqlite/tang_strategy_live_extended.db`.
- Safe rebuild: `PYTHONPATH=. python scripts/rebuild_live_extended_db.py`.

The standing daily entry is `scripts/update_spy_qqq_market_day.py`. It stages SPY and QQQ from one provider, rejects mixed or partial pairs, refreshes the canonical trade projection, and promotes one verified candidate. Real TV/IB calls still require the applicable provider authority.

Rebuild imports into a candidate and refuses empty/invalid bars, count disagreement, integrity/foreign-key failure, market-day loss, strategy/teaching shrink, or live DB drift. `--allow-date-loss` is an explicit supervised override for intentional market-day shrink only.

## API Surface

- `POST /api/auth/login` — exchange the configured readonly/admin password for a bearer token.
- `GET /api/health`
- `GET /api/tickers`
- `GET /api/market-days` and `GET /api/market-days/{market_day_id}`
- `GET /api/market-days/{market_day_id}/bars?timeframe=1m|5m`
- `GET /api/strategies` and `GET /api/strategies/{strategy_id}`
- `GET /api/reviews/assemble?market_day_id=<id>&strategy_id=<id>`
- `GET /api/trade-records` — readonly/admin filters for ticker, date/range, trader, status, review status, and eligibility.
- `GET /api/teaching/{asset_type}`
- admin-only: `PUT /api/admin/traders`, `PUT /api/admin/trade-records`, and the existing import endpoints.

Admin trader/day writes validate the whole canonical repository, atomically replace the content file, rebuild the normalized SQLite projection on a candidate, and roll both boundaries back on failure. There is no unrestricted rebuild endpoint.

## Static Export

`scripts/export_static_reviews.py` reads the tracked DB plus canonical normalized trade records and writes generated JSON for every accepted ticker unless `--ticker` narrows the scope. It does not publish by itself.
