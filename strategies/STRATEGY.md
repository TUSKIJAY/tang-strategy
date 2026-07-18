# Tang Strategy Version Guide

This document is the single strategy canon for all review, backtest, and teaching flows. All runtime systems should treat this as the source of truth for signal intent.

## Runtime model (shared by every version)

- Primary barframes: 1m execution, 5m context.
- Candle base: Heikin-Ashi OHLC (`hO/hH/hL/hC`) for trend and signal logic.
- Strategy/runtime MA set: SMA5/10/20/30/50/60/120/200/250 and VWAP. The chart engine can also render optional `m500` values when a payload supplies them.
- No per-day HTML strategy files: strategy behavior is loaded from `strategies/json/*.json` and consumed through API-assembled payloads.
- Output shape for signals is expected to remain stable by `id`, `timeframe`, `bar_index`, and `direction` for UI compatibility.

## Strategy version history

### Tang v1
- First-generation, strict trend-following baseline.
- Core behavior: reject/support around MA10 with minimal filters.
- Typical use: quick structure checks and baseline signal coverage.
- Limitation: fewer context constraints for sideways and high-volatility days.

### Tang v2
- Expands v1 with stronger trend confirmation and cleaner score markers.
- Adds improved filtering so signal quality is less noisy at the same setup frequency.
- Typical use: first “production-lean” baseline in DB-fed backtesting.

### Tang v3
- Adds explicit multi-condition handling and better trend-quality checks.
- Introduces broader context around MA spacing and candle quality, not only MA10 touch events.
- Typical use: stronger noise rejection while preserving v1/v2 behavior.

### Tang v3.3.1 Flame
- Focuses on high-confidence micro-setup qualification.
- Keeps v3 structure but tightens reversal/invalid checks and timing behavior.
- Typical use: intraday sessions where false-break signals are frequent.

### Tang v3.5.1 Full
- Full-feature set before v4 migration.
- Adds richer execution-state modeling and more explicit rule blocks for scanners.
- Typical use: deeper replay analysis and strategy comparison against historical batches.

### Tang v4.4 Slope
- Major architecture update in a single strategy revision.
- Key additions:
  - 5m MA10/20/30 direction checks for higher-timeframe alignment.
  - 1m MA10 slope checks as an entry-quality gate.
  - Stateful hold/entry lock with cooldown windows and strong-signal flags.
- This is the current core baseline for most experiments.

### Tang v4.4 Activation
- Derivative of v4.4 Slope.
- Distinguishes `setup` and `signal` lifecycle:
  - setup: identifies candidate, no position state change.
  - signal: confirmed only when follow-through condition appears within the activation window.
- Adds better control of execution timing, reducing over-trading.

### Tang v4.4 Activation Wick
- Variant of Activation with wick-confirmation path.
- Keeps setup/activation split while allowing breakout confirmation through wick when close does not yet confirm.
- Useful for fast expansion days where strict close-only confirmation is too late.

### Tang v4.5 (if enabled in repo)
- Transitional variant after v4.4 with incremental parameter tuning and cleaner annotations.
- Recommended for comparative benchmarks only unless intentionally migrating from v4.4.

### Tang v4.8.4 Hybrid VWAP
- Hybrid v4-family definition exported by the current Pages strategy-family filter.
- Keeps the versioned JSON contract and adds VWAP-oriented hybrid context for comparative review.
- Treat as an explicit comparison target; do not silently replace the v4.4 Slope baseline.

### Tang v5.0
- Current forward-compatibility branch.
- Focus on rule clarity, schema safety, and easier scanner mapping.
- Recommended target branch when adding new rule families.

## How to choose a version in practice

- Default for replay/backtest: start with `tang_v4_4_slope`, then compare with v4.4 Activation and Wick.
- Use earlier versions only for regression context and behavior tracing.
- Prefer newer versions for live-like DB workflows and teaching content alignment.

## Version governance

- Strategy updates should be additive and versioned (`tang_vX_Y` pattern), never overwrite existing files.
- Keep compatibility by preserving existing `signals[].id` and top-level schema fields.
- Any semantic change should be reflected in:
  1. strategy JSON,
  2. `strategies/strategy.schema.json` (if schema additions are needed),
  3. docs + changelog notes.

## Related docs

- Architecture and data flow: `docs/architecture.md`
- Review and backtest workflow: `docs/roadmap.md`
- Teaching content mapping: `docs/teaching-system.md`
- Shared chart engine: `docs/kline-engine.md`
