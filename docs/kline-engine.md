# Kline Engine

The kline engine is the shared chart runtime for Review, Teaching, and Backtest.

## Responsibilities

- Render 1m and 5m candles.
- Support Heikin-Ashi and normal OHLC display modes.
- Render volume, MA5/10/20/30/50/60/120/200, and VWAP.
- Provide play, pause, single-bar forward/back, speed control, and timeframe switching.
- Enforce reveal cutoff so teaching and replay flows do not show future bars.
- Emit interaction events for hover, bar click, annotation click, playback, and viewport changes.

## Payload Contract

The engine consumes normalized payloads produced by backend assemble APIs.

Required top-level fields:

- `meta`
- `bars_1m`
- `bars_5m`

Bar fields:

- `ts`, `t`
- `O`, `H`, `L`, `C`
- `hO`, `hH`, `hL`, `hC`
- `V`
- `vw`
- `m5`, `m10`, `m20`, `m30`, `m50`, `m60`, `m120`, `m200`

Optional annotation fields:

- `bar_index`
- `timeframe`
- `title`
- `body`
- `style`
- `anchor_side`

## Public Behavior

- `loadData(payload)` resets playback and viewport.
- `setTimeframe("1m" | "5m")` switches chart frame while preserving the closest visible time.
- `play()`, `pause()`, `stepForward()`, and `stepBack()` control replay.
- `setRevealCutoff(...)` hides future bars and clamps playback.
- MA/VWAP visibility is shared with toolbar state and persisted where supported by the frontend wrapper.

## Integration Rule

New pages should wrap the existing engine instead of reimplementing chart rendering. If a page needs a new chart behavior, add it to the shared engine API and then consume it from each page.
