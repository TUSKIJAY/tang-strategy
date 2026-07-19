# Tang Strategy Architecture

## Runtime Modes

Tang Strategy has one data source of truth and two delivery modes:

- interactive: FastAPI reads the tracked SQLite DB; authenticated React pages call the API;
- static Pages: CI reads the same DB, exports JSON, builds `StaticReviewsApp`, and publishes the Vite output to `gh-pages`.

The shared runtime input is `data/sqlite/tang_strategy_live_extended.db`. The accepted local seed shape is `data/seed/market-data/live_extended/<date>/<ticker>_<date>.json`.

## Daily Data And DB Flow

1. `update_spy_qqq_market_day.py` invokes the tracked one-symbol adapters into temporary staging, using TradingView first.
2. Both tickers must pass the same NYSE/session/OHLCV/RTH/5m/VWAP and same-provider gates; otherwise accepted seeds and DB remain on the prior pair.
3. The orchestrator imports both payloads and the canonical trade repository into one candidate, verifies preservation/integrity/drift, then atomically promotes and replaces the accepted seed pair.
4. If TV retries or a named hard gate fail, the operator may separately start IB Gateway and rerun the complete pair with `--provider ibkr`; one accepted pair never mixes providers.
5. The tracked DB carries logical market days, provider datasets, bars, strategies, teaching assets, and normalized trade projections into runtime and Pages export. Canonical source remains under `content/traders` and `content/trades`.

Rebuild never deletes the current DB before candidate validation. Default replacement requires the candidate market-day set to be a superset of the current set; the daily workflow never uses the intentional date-loss override.

## Interactive API Flow

- login: `POST /api/auth/login`;
- discovery: `GET /api/tickers`, `/api/market-days`, `/api/strategies`;
- bars: `GET /api/market-days/{market_day_id}/bars?timeframe=1m|5m`;
- assembled review: `GET /api/reviews/assemble?market_day_id=<id>&strategy_id=<id>`;
- normalized trade reads: `GET /api/trade-records`;
- teaching assets: `GET /api/teaching/{asset_type}`;
- controlled writes: atomic admin trader/day endpoints plus the existing import endpoints.

Readonly/admin endpoints use bearer auth. Admin canonical writes are validation-, candidate-, drift-, and rollback-protected; there is no unrestricted rebuild endpoint.

## Static Pages Flow

`.github/workflows/publish-static-reviews.yml` runs only for its configured `main` push/manual trigger:

1. checkout the tracked DB;
2. run `export_static_reviews.py` into `frontend/public/reviews`;
3. build with `VITE_STATIC_REVIEWS=true` into `frontend/dist`;
4. replace the remote `gh-pages` branch with that build.

The current static format is a Vite SPA plus generated review/strategy JSON. It is not the retired collection of standalone per-day HTML under `docs/`.

## Frontend Modules

- Data/Dashboard loads tickers, days, strategies, and admin import controls.
- Review requests one assembled payload and runs browser scanner/lifecycle rendering.
- Backtest loads bars for recent days, runs the browser-side backtest, and renders results through the shared engine.
- Teaching loads structured content and uses the same chart/replay surface.
- `frontend/src/kline/` owns the shared chart engine; new consumers must not create a page-specific replacement.

## Ownership Boundaries

- strategy JSON: `strategies/json`; canonical intent guide: `strategies/STRATEGY.md`;
- teaching/rules/cases/trades: `content/`;
- product direction: `docs/roadmap.md`;
- governed execution: `docs/exec-plans/`;
- generated JSON/build: `frontend/public/reviews` and `frontend/dist`;
- publication: `gh-pages`, never `docs/`.
