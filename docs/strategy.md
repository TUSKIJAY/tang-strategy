# Tang Strategy — Version Guide (Docs)

This page summarizes all strategy versions currently used by the Tang Strategy workspace.

## Canonical execution model

All versions use the same engine contract in this repo:

- 1m/5m dual-frame logic.
- Heikin-Ashi base candles for signal computation.
- MA5/10/20/30/50/60/120/200 + VWAP support filters.
- JSON strategy definitions are authoritative (`strategies/json/*.json`).

## Version index

| Version | Role |
|---|---|
| `tang_v1`, `tang_v2` | Baseline MA10-first generation. Useful for historical comparison. |
| `tang_v3`, `tang_v3_3_1_flame` | Early upgrades with stronger context checks. |
| `tang_v3_5_1_full` | Full v3 family profile; used for richer replay baselines. |
| `tang_v4_4_slope` | Core modern strategy baseline: stronger slope/alignment gates and stateful flow. |
| `tang_v4_4_activation` | Setup + delayed confirmation split to reduce early entries. |
| `tang_v4_4_activation_wick` | Activation variant with wick-breakout support. |
| `tang_v4_5`, `tang_v5_0` | Forward compatibility branch for tuning and migration work. |

## Operational recommendation

- Use `tang_v4_4_slope` for day-to-day review/backtest.
- Run Activation/Wick side-by-side when comparing entry timing sensitivity.
- Keep older versions for drift analysis and rollback scenarios.

## Implementation notes

- Keep strategy identifiers stable where possible to avoid scanner regressions.
- Prefer explicit config-driven behavior in JSON over custom frontend logic.
- For one-line verification, run the known day (SPY 2026-04-22) through:
  - review assemble API,
  - strategy selector,
  - backtest panel.
