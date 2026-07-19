# Kline Engine

`frontend/src/kline/` is the shared chart runtime for Review, Backtest, and Teaching.

## Responsibilities

- render 1m and 5m candles in normal OHLC or Heikin-Ashi mode;
- render volume, VWAP, and MA5/10/20/30/50/60/120/200/250/500 when fields are available;
- play, pause, step forward/back, change speed/timeframe, and manage viewport;
- enforce reveal cutoff so replay/teaching cannot expose future bars;
- render and navigate annotations/highlight ranges;
- emit hover, bar, annotation, playback, and viewport interactions.

The current backend SQLite schema/payload persists MA fields through `m250`; the engine accepts `m500` as an optional display field for compatible payloads.

## Payload Sources

The engine consumes the same normalized shape from two supported sources:

- interactive API: `/api/reviews/assemble` or page-composed bar payloads;
- static Pages: exported `frontend/public/reviews/days/*.json` loaded by `StaticReviewsApp`.

Required top-level fields are `meta`, `bars_1m`, and `bars_5m`. Annotation arrays and normalized `trade_records` are optional consumers layered by the page. Trade annotations use trader color independently from CALL/PUT triangle shape and may group same-bar events without losing IDs.

Bar fields include `ts`, `t`, `O/H/L/C`, `hO/hH/hL/hC`, `V`, `vw`, and available `m*` values.

## Public Behavior

- `loadData(payload)` resets chart/playback state.
- `setTimeframe("1m" | "5m")` switches frame near the visible time.
- `play()`, `pause()`, `stepForward()`, and `stepBack()` control replay.
- `setRevealCutoff(...)` hides future bars and clamps navigation.
- `scrollTo(...)`, annotation callbacks, and highlight ranges connect Review/Backtest lists to the chart.
- MA visibility and supported preferences are persisted per session where the wrapper enables it.

New active pages must wrap the existing engine. Suspected orphan chart components or duplicated page helpers are optimization intake, not authorized cleanup in the current plan.
