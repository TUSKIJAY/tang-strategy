# Tang Strategy Roadmap

Last updated: 2026-05-06

## Current baseline

- Data source: `live_extended` JSON only.
- Runtime database: `data/sqlite/tang_strategy_live_extended.db`.
- Shared runtime payload: one assembled backend payload drives Review, Teaching, and Backtest.
- Shared chart engine: one frontend kline engine handles replay, single-bar stepping, MA/VWAP overlays, and hidden-future cutoff.
- Removed workflow: per-day static Daily Review HTML generation.

## Completed

- Live-extended data was imported into a clean SQLite database.
- Daily Review became API-first through `/api/reviews/market-days` and `/api/reviews/assemble`.
- Backtest now replays the same assembled review payload used by the Review page.
- Teaching and Backtest pages were moved onto the unified kline engine.
- Legacy static review and teaching directories were removed from the active runtime.
- Documentation was flattened so `docs/` has no nested structure.

## Daily Review

- Page role: inspect one market day, replay bars, review strategy signals, and collect session stats.
- Data path: SQLite -> backend assemble API -> frontend review page.
- Required endpoints:
  - `GET /api/reviews/market-days`
  - `GET /api/reviews/assemble?day_id=<id>`
- Payload must include 1m bars, 5m bars, session metadata, strategy annotations, and indicator fields.
- Known verification target: `SPY 2026-04-22`.

## Backtest

- Page role: replay a selected day and strategy through the browser-side signal lifecycle.
- Source of truth: `/api/reviews/assemble`, not detached JSON snapshots.
- Inputs: market day, ticker/session metadata, selected strategy, bars, and annotations.
- Outputs: signal sequence, completion/invalidations, timing windows, and aggregate metrics.
- Non-goal: restoring old standalone Python batch backtest as the primary workflow.

## Teaching System

- Page role: teach the same market mechanics used by Review and Backtest.
- Content source: `content/teaching/checkpoints.json`, `content/cases/index.json`, and `content/rules/compiled/index.json`.
- Runtime rule: teaching copy can explain strategy semantics, but execution behavior should remain config-driven through strategy JSON and backend payloads.
- Near-term work: improve MA50/MA200/VWAP validation language and add case notes for role-swap and weakening patterns.

## Kline Engine

- Used by Review, Teaching, and Backtest.
- Required capabilities:
  - 1m/5m timeframe switching
  - play, pause, step forward, step back
  - reveal cutoff for teaching/replay
  - MA5/10/20/30/50/60/120/200 and VWAP visibility
  - Heikin-Ashi and normal OHLC display modes
- New chart consumers must use this engine instead of page-specific chart implementations.

## Next Milestones

1. Harden importer and daily fetch workflow for Polygon/IBKR generated JSON.
2. Add strategy comparison UX for `tang_v4_4_slope`, activation, and wick variants.
3. Expand teaching cases with validated key-level examples.
4. Normalize replay statistics across Review and Backtest.
5. Add operational smoke checks for `SPY 2026-04-22` after backend/frontend changes.

## Acceptance Criteria

- `docs/` stays flat.
- Runtime docs mention only the live-extended DB path.
- Review, Teaching, and Backtest can consume the same assembled payload shape.
- No active workflow depends on static daily review HTML.
