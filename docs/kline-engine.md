# Kline Engine

`frontend/src/kline/` is the shared chart runtime for Review, Backtest, and Teaching.

## Responsibilities

- render 1m and 5m candles in normal OHLC or Heikin-Ashi mode;
- render volume, VWAP, and MA5/10/20/30/50/60/120/200/250/500 when fields are available;
- play, pause, step forward/back, change speed/timeframe, and manage viewport;
- expose one visible Overview/fit action that resets the viewport to the full current day and resumes follow at the latest visible bar;
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
- `overview()` is the single public fit/full-day action used by the toolbar and optional programmatic context/list transitions.
- MA visibility and supported preferences are persisted per session where the wrapper enables it.

## Visible Control Ownership

The engine toolbar is the only visible owner of chart-generic controls:

- timeframe: 1m/5m;
- replay: back/play/forward and speed;
- viewport: zoom, follow, Overview/fit;
- indicators: MA/VWAP visibility;
- rendering: OHLC/Heikin-Ashi, fill, and theme.

Pages may call imperative methods for business transitions or list/marker navigation, but must not render a second generic toolbar. Review and Static Review own ticker/date, strategy, Ext K/RTH, trader/eligibility/focus, export, and business actions. Backtest retains run/result selection; Teaching retains cutoff/reveal. Admin's candidate preview is one read-only `UnifiedKlineEngine`, not a second chart implementation.

## Embedding And Styling Boundary

`UnifiedKlineEngine` creates one engine instance, forwards payload/annotation changes, and exposes a narrow imperative API including `setTimeframe`, replay navigation, `scrollTo`, `fitRange`, highlight ranges, reveal cutoff, and `overview`. Consumers must reuse that wrapper instead of reaching into engine DOM state.

Dynamic theme variables are scoped to `.kline-engine`. The standalone demo may style `#demo-page`, but engine CSS must not target host-level `:root`, `html`, or `body`; embedded Review, Static, and Admin surfaces retain their own themes. Normalized trade markers keep trader color independent from CALL/PUT shape and retain grouped event/group IDs for list navigation.

New active pages must wrap the existing engine. Suspected orphan chart components or duplicated page helpers remain optimization intake, not authorized cleanup in this plan.
