# Tang Strategy Product Roadmap

Last updated: 2026-07-18

This file owns product/module direction. Execution-plan state belongs in [`exec-plans/roadmap.md`](./exec-plans/roadmap.md).

## Current Baseline

- one tracked `live_extended` SQLite runtime and Pages export input;
- TradingView-first daily acquisition with hard quality gates and IB fallback-only policy;
- candidate-first, fail-closed, atomic rebuild;
- interactive FastAPI/React mode and static Vite/JSON Pages mode;
- shared kline engine for Review, Backtest, and Teaching;
- known regression day: SPY 2026-07-17.

## Daily Review

- list days through `GET /api/market-days`;
- assemble through `/api/reviews/assemble?market_day_id=<id>&strategy_id=<id>`;
- render 1m/5m bars, strategy metadata, browser-generated annotations, and Tang trade overlays;
- preserve replay and hidden-future behavior in the shared engine.

## Backtest

- load selected strategy JSON and recent-day 1m/5m bars through the API;
- run the browser-side signal lifecycle across the selected day set;
- render results and annotations through the shared engine;
- keep result semantics aligned with Review scanner/lifecycle behavior.

## Teaching

- teach from `content/teaching/checkpoints.json`, `content/cases/index.json`, and `content/rules/compiled/index.json`;
- use the same bars, indicators, reveal cutoff, and replay controls as Review/Backtest;
- keep MA/VWAP language conditional on observed price validation, not mechanical permission.

## Kline Engine

- remain the only chart implementation for active pages;
- support 1m/5m, OHLC/Heikin-Ashi, MA/VWAP visibility, playback, stepping, reveal cutoff, annotations, and viewport events;
- accept both API-assembled payloads and static exported day JSON.

## Next Product Milestones

1. Compare v4.4 Slope, Activation, Wick, v4.8.4 Hybrid VWAP, and v5 behavior with explicit regression evidence.
2. Expand validated teaching cases for role swap, weakening, failed retest, and dense target-space examples.
3. Normalize Review/Backtest scanner and metric behavior where audit evidence shows drift.
4. Improve reproducible provenance for the large kline engine and strategy JSON/Pine relationships.
5. Evaluate a long-term tracked-DB growth strategy through a separate governed plan.

Items 3-5 are direction only. Their implementation requires an independently reviewed and explicitly activated exec plan.
