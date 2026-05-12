# Planning Hub

This file is the only active planning document under `docs/`.

## Current planning status (2026-05-06)

- Data foundation is complete with `live_extended` only.
- Runtime database is `data/sqlite/tang_strategy_live_extended.db`.
- Review, Teaching, and Backtest share the assembled payload and kline engine.
- Documentation is flat under `docs/`; historical nested planning folders are removed from active docs.

## Active decisions

1. Continue DB-first flow end-to-end; no per-day static HTML for daily review.
2. Keep strategy semantics in `strategies/json/*.json`.
3. Put product direction and module workflow in `roadmap.md`.
4. Put runtime structure and API/data boundaries in `architecture.md`.
5. Use `teaching-system.md` as source-of-truth for MA50/MA200/VWAP teaching language.
6. Avoid page-specific chart implementations; use the shared kline engine.

## Historical Plan Summary

### Kline Engine v2

- Goal: isolate a reusable chart engine for teaching, review, and backtest.
- Delivered: Canvas chart rendering, timeframe switching, playback, MA/VWAP overlays, annotation support, hover state, reveal cutoff, and single-bar stepping.
- Result: engine is now the shared frontend chart contract.

### Teaching System

- Goal: replace static teaching pages with structured cases, checkpoints, and runtime replay.
- Delivered: case assets, checkpoint-driven teaching copy, replay drill behavior, MA/VWAP value legend, and shared engine integration.
- Remaining concern: keep lesson wording aligned with actual strategy JSON and assembled payload fields.

### Strategy Rule Sync

- Goal: avoid teaching MA50, MA200, or VWAP as mechanical support/resistance.
- Decision: a key level is meaningful only when recent price action has tested and reacted to it.
- Future schema candidates:
  - `key_level_validated`
  - `prior_reaction_ok`
  - `role_swap`
  - `reverse_retest_failed`
  - `narrow_range`
  - `weakening`
  - `density_blocked`

### Data Foundation

- Goal: stop mixing `proceed`, `live`, and `live_extended` datasets.
- Decision: use only `live_extended`.
- Result: seed JSON imports into one clean SQLite database and runtime reads only that DB.

## Open Workstream

- Minor planning cleanup: keep only one source of truth for each area in root docs.
- Add compact case-review checklist to `teaching-system.md`.
- Monitor whether hidden-future cutoff and replay metrics should be normalized across front-end consumers.
- Add a daily fetch/import runbook once Polygon or IBKR ingestion is finalized.

## Documentation Policy

- Do not create subdirectories under `docs/`.
- Summarize historical plan details here instead of storing nested plan files.
- Keep evidence-heavy artifacts out of active docs unless they are needed for current implementation.
