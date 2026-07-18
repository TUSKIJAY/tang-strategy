# Historical Planning Summary

This file preserves a compact pointer to planning that predates the governed lifecycle. It is not an active plan, decision log, roadmap, or current-state owner.

## Historical Outcomes

- The project converged on one `live_extended` SQLite runtime instead of mixing previous seed/DB formats.
- Review, Backtest, and Teaching converged on shared bar payloads and the unified kline engine.
- Kline Engine v2 delivered canvas rendering, timeframe switching, replay, MA/VWAP overlays, annotation support, reveal cutoff, and single-bar stepping.
- Teaching content moved into structured cases, compiled rules, and checkpoints.
- The current daily contract became TradingView-first with IB fallback only after documented hard-gate failure.
- The current static publisher became a Vite SPA plus exported JSON on `gh-pages`; standalone per-day HTML is retired.

## Current Authority Redirects

- product/module direction: [`roadmap.md`](./roadmap.md);
- runtime/data/API design: [`architecture.md`](./architecture.md);
- active execution plan: [`exec-plans/active/index.md`](./exec-plans/active/index.md);
- durable decisions: [`decisions/index.md`](./decisions/index.md);
- current lifecycle truth: [`../PROGRESS.md`](../PROGRESS.md);
- latest resume point: [`../HANDOFF.md`](../HANDOFF.md).

Historical summaries and open ideas do not authorize implementation.
