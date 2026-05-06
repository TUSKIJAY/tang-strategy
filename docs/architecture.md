# Tang Strategy Architecture

## Current baseline

The project runs as a frontend/backend split:

- Backend (`backend/`): FastAPI + SQLite API, auth, seed import, and data adapters.
- Frontend (`frontend/`): Vite React UI for Review, Teaching, Backtest, replay, and statistics.
- Shared data layer: `data/sqlite/tang_strategy_live_extended.db`.
- Rebuild source: `data/seed/market-data/live_extended/`.

## Data flow

1. External fetchers (Polygon/IBKR planned) produce JSON files in `data/seed/market-data/live_extended/<YYYY-MM-DD>/`.
2. Backend importer reads `live_extended` and writes:
   - `market_days`
   - `bars_1m`
   - `bars_5m`
   - strategy metadata and annotation payloads
3. Frontend requests assembled payloads from `GET /api/reviews/assemble?day_id=...`.
4. Review, Teaching, and Backtest render from the same payload shape.
5. UI charts use the shared kline engine; no per-day static HTML is required.

## Runtime Modules

### Daily Review

- Lists market days from SQLite.
- Assembles one canonical day payload.
- Drives replay, annotation review, and session-level statistics.

### Backtest

- Uses the assembled review payload.
- Runs browser-side signal lifecycle and timing-window evaluation.
- Shares chart state and indicator behavior with Review.

### Teaching System

- Reads cases, checkpoints, and rules from `content/`.
- Uses the same chart engine and replay controls.
- Explains strategy semantics without duplicating runtime strategy logic in UI code.

## Engine boundary

`frontend/src/kline/` contains the unified chart engine used by teaching, review, and backtest flows.

Core engine responsibilities:

- normalize 1m/5m bars
- render Heikin-Ashi or normal OHLC candles
- render MA and VWAP overlays
- support single-bar stepping and playback
- enforce hidden-future reveal cutoff for teaching/replay

## Compatibility scope

This branch uses a clean single-format DB contract:

- Market source format: `live_extended` JSON only.
- DB name: `tang_strategy_live_extended.db`.
- Existing legacy DB/schema files are not used by runtime.

## Repository conventions

- Keep DB rebuild and import paths in `backend/scripts`.
- Keep strategy JSON in `strategies/json`.
- Keep teaching/lesson runtime assets in `content/`.
- Keep historical static artifacts outside active documentation and active runtime docs.
- Keep `docs/` flat; do not create nested documentation folders.
