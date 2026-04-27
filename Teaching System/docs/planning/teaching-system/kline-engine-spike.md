# Kline Engine Spike

> Source checked: `dist/kline-engine/INTEGRATION.md` and current engine source references on 2026-04-24.

## Verdict

The current Kline engine is usable for the first teaching-system vertical slice. It supports the required mount, destroy, data loading, timeframe switching, playback, and decision-bar navigation flows.

It does not currently document public APIs for external future-bar masking or persistent validation highlights. Treat those as caveats, not blockers.

## Supported Public Surface

| Need | Current support | Notes |
|---|---|---|
| Mount into product page | `new KlineEngine({ container })` | Container must have real width/height. |
| Unmount / route cleanup | `destroy()` | Required before hot replacement or route exit. |
| Load case data | `loadData(json)` | Returns summary and resets viewport/playback. |
| Switch timeframe | `setTimeframe('1m' | '5m')` | Preserves current time point when possible. |
| Drive replay | `play()`, `pause()`, `togglePlayback()`, `stepForward()`, `stepBack()` | Good enough for `lab` mode. |
| Playback speed | `setSpeed(0.5 | 1 | 2 | 4)` | Invalid values fall back to 1. |
| Jump to decision bar | `scrollTo({ timeframe, barIndex, highlight, center })` | `highlight` is temporary flash. |
| Set current replay head | `setCurrentIndex(idx, { follow })` | Useful for training steps. |
| Listen to user actions | `on(...)` / `off(...)` | Includes bar, annotation, viewport, playback events. |
| HA / OHLC toggle | `setCandleType('ha' | 'normal')` | Default is HA; strategy annotations are HA-based. |
| MA visibility | mutate `engine.maVisibility` + render sync | No dedicated `setMAVisibility` yet. |

## Data Requirements

Use current processed segment JSON or `data/build_json.py` outputs. Bars should include:

- `O/H/L/C`
- `hO/hH/hL/hC`
- `V`
- `vw`
- MA fields such as `m10`, `m50`, `m200`

Warmup gaps should be `null`, not `0`.

## Teaching-System Mode Implications

`KlineView mode="mini"`:

- Prefer static/very light preview.
- Do not mount full engine many times in lists.

`KlineView mode="evidence"`:

- Can use engine with product chrome hidden by the adapter.
- Load a single segment, jump to the teaching point, show only relevant MA lines.
- Avoid dev panel and full-terminal controls.

`KlineView mode="lab"`:

- Use full playback/timeframe controls.
- One full engine instance per active case/training page.
- Reuse instance with `loadData()` when switching cases.

## Caveats To Handle Explicitly

Future hiding:

- No documented `hideFutureAfter(index)` / reveal API.
- First implementation can approximate training state with `setCurrentIndex()` and controlled playback.
- If users can still see future bars in training, add a small public engine option/API rather than mutating private renderer internals.

Persistent highlight:

- `scrollTo({ highlight: true })` creates a short flash only.
- Right-side validation items such as Trend Confirmed / MA10 Trigger / VWAP Distance need either annotations or a new public highlight API.
- Do not rely on `_scrollToHighlight` directly; it is private and time-limited.

Integration hygiene:

- Do not ship `kline-devpanel.js` in product pages.
- Use `on('data:loaded', ...)` instead of `setTimeout` as readiness.
- Call `destroy()` on unmount.
- Remember that annotations/signals are HA-based; switching to OHLC may visually shift signal meaning.

## Recommended First Spike

1. Mount one engine in a simple `KlineView mode="lab"` adapter.
2. Load `seed_01` through the case/segment mapping.
3. Call `scrollTo({ timeframe: '1m', barIndex: 31, highlight: true })`.
4. Wire `stepForward`, `stepBack`, `play`, `pause`, and `setTimeframe`.
5. Add a small adapter-level method for `showDecisionStep(step)` that calls supported APIs only.
6. Decide whether future masking and persistent highlight need engine changes after this proves the slice.
