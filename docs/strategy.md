# Strategy Documentation Entry

Canonical strategy intent and version guidance lives in [`../strategies/STRATEGY.md`](../strategies/STRATEGY.md). Runtime definitions live in [`../strategies/json/`](../strategies/json/).

This docs entry is a routing summary, not a second canon. Current exported families include v3, v4, and v5; the repository also contains the active `tang_v4_8_4_hybrid_vwap` definition. Strategy behavior must remain config-driven and identifier-stable for Review/Backtest compatibility.

Regression changes should use SPY 2026-07-17 and compare the intended strategy, including `tang-v4-4-slope-4-4` as the stable baseline.
