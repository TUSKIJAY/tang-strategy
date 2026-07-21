# Optimization Batch · 2026-07-21

> Record-only intake. This file does not authorize implementation.
>
> Place this file at:
> `docs/optimization/2026-07-21-kline-5m-switch-viewport-glitch/2026-07-21-kline-5m-switch-viewport-glitch.md`
> Put evidence images in the sibling `screenshots/` folder and link them as `./screenshots/<name>.png`.
>
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. A draft, failed/incomplete record, explicit no-commit instruction, or unclear path ownership prevents that commit. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | K-line 5m switch: initial viewport wrong until mouse wheel | Review / Kline Engine | recorded | none | 点 5m 首帧左侧挤一撮 K 线 + 右侧大片空白；滚轮后才正常 |

## Visual Reference

- User screenshot (5m selected, broken first paint): [`screenshots/2026-07-21-kline-5m-switch-initial-viewport.png`](./screenshots/2026-07-21-kline-5m-switch-initial-viewport.png)
  - Toolbar shows **5m** active; header `tf=5m`.
  - Candles + volume clustered on the **far left**; most of the plot area empty.
  - Y-axis span looks over-wide for the visible cluster (~686.78–693.52).

## OPT-001 K-line 5m Switch Initial Viewport Glitch

- Source evidence: User screenshot above + instruction (2026-07-21): 点击 K 线引擎 **5m** 按钮后先显示该异常画面，**滑动鼠标滚轮后**才正常显示。
- Current friction:
  1. User switches from default **1m** to **5m** via toolbar.
  2. First paint after switch is wrong: bars do not fill the chart window (left cluster + empty right).
  3. A mouse-wheel zoom/pan event forces a correct viewport recalculation and the chart looks normal.
  4. This makes 5m review unusable until the user “jiggles” the wheel — easy to miss and confuses density/time reading.
- Desired outcome: Switching to **5m** (and ideally any timeframe switch) must land on a correct, full-window viewport on the **first** `render` after `setTimeframe`, with no requirement to scroll the wheel.
- Likely code surface (investigation notes only, not a fix):
  - `frontend/src/kline/kline-engine.js` · `UnifiedKlineEngine` / engine `setTimeframe()` (~2956+): maps prior 1m window start into 5m, reuses shared `viewportManager.zoomScale`, sets `viewStart` / follow mode, then `scheduleRender()`.
  - `ViewportManager.getResolvedViewCount` / `getVisibleWindow` / `applyZoom`: wheel path recalculates `zoomScale` + window; switch path may leave 1m-era `zoomScale` or a mismatched `viewStart`/`count` until wheel fires.
  - 5m window constants differ from 1m (`getWindowBarCount` / `getViewLimits`: 5m slot 18, min 18, max 72 vs 1m 14 / 24 / 96).
- Boundary that must not change:
  - Data payloads (`bars_1m` / `bars_5m`), assemble API, or market-day seed contracts.
  - Replay / reveal-cutoff semantics unless proven necessary for the viewport fix.
  - Do not treat this as a Pages/publish or DB issue.
- Lifecycle status: recorded
