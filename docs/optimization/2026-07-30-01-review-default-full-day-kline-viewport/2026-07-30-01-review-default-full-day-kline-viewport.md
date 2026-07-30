# Optimization Batch · 2026-07-30 Review Default Full-Day K-Line Viewport

> Record-only intake. This file does not authorize product implementation, plan promotion, activation, push, data mutation, publication, or remote action.
>
> Evidence images live in `./screenshots/`. The user-provided target shows the desired default full-day composition; it is an acceptance reference, not proof that the current runtime already behaves this way.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Open Review with the complete current-day K-line session in view | Review + Static Review shared K-line viewport | completed | [completed plan](../../exec-plans/completed/2026-07-30-tang-strategy-default-full-day-kline-viewport-plan.md) | `implementation-review-001: accept/high`; product commit `f667867c3e511d2eaaf77f673c96f3e7ed1f70e2` |

## Scope Lock

| Topic | Lock |
| --- | --- |
| User-visible problem | Opening the page currently shows only part of the selected day's candles, as captured in [`current-default-partial-day-kline.png`](./screenshots/current-default-partial-day-kline.png). |
| Target state | The initial chart composition should match [`target-default-full-day-kline.png`](./screenshots/target-default-full-day-kline.png): all candles belonging to the currently displayed day/session are visible across the chart on first paint. |
| Default behavior | No manual `- Zoom`, wheel zoom, drag, or other corrective action is required to see the entire displayed day after a Review or Static Review payload loads. The existing `Overview` action is part of the current defect: user runtime confirmation shows that clicking it produces the same partial-day composition as Figure 1. |
| Actual-session truth | Fit the bars that actually exist in the current display dataset. A normal 1m RTH session may contain 390 bars and a normal 5m session 78 bars, but early closes, extended-session mode, and incomplete source data must use their truthful available counts rather than fabricated fixed counts. |
| Context reload | Changing ticker, date, strategy payload, session projection, or timeframe must establish a deterministic viewport. The default Review/Static state should remain full-day unless the user has explicitly moved or zoomed the current view; the exact interaction-reset policy requires implementation review. |
| Surface parity | Interactive Review and Static Review should not disagree about the same payload's default viewport. Prefer the shared K-line engine contract over page-local workarounds. |
| Controls | Existing zoom, pan, Follow, playback, annotation focus, trade-group `fitRange`, and signal/event locate actions remain available after initial fit. The record does not remove manual navigation. |
| Teaching boundary | Teaching replay intentionally owns a reveal cutoff and follow behavior. It is outside this target unless a later plan proves a safe shared-engine change and preserves replay semantics. |
| Data boundary | No market-data, strategy, annotation, trade-content, DB, API, publication, or provider change is requested. This is a viewport/default-presentation issue only. |

## Visual Evidence

| File | Role | SHA-256 | Size | Dimensions |
| --- | --- | --- | ---: | ---: |
| [`current-default-partial-day-kline.png`](./screenshots/current-default-partial-day-kline.png) | User-provided current-state evidence: first paint exposes only the latest portion of the day; later runtime confirmation established that clicking `Overview` reproduces this same view | `d07750ee597f3e44981f6cc51e0c28ebcc93bb5a8f8c54d392e8503be69ffba4` | 625,254 bytes | 2769×1619 |
| [`target-default-full-day-kline.png`](./screenshots/target-default-full-day-kline.png) | User-provided target: the full displayed day is visible at once | `3864e84f82286edfa82274e594d25875e7945839fc0c7a02527407669ed26aa9` | 358,807 bytes | 2079×1050 |

## Current Code Anchors (read-only evidence)

| Area | Current anchor |
| --- | --- |
| Default bar budget | `frontend/src/kline/kline-engine.js:803-807` derives a width-based default window and caps 1m at 96 bars and 5m at 72 bars. |
| First-paint state | `frontend/src/kline/kline-engine.js:787-790` resets to `zoomScale = 1` and follow mode; `:819-835` resolves that state as a tail window ending at the current/latest bar. |
| Data load | `frontend/src/kline/kline-engine.js:2697-2716` loads a new payload, resolves the latest index, and resets the viewport to the default width-based window. |
| React adapter | `frontend/src/kline/UnifiedKlineEngine.jsx:62-74` loads the payload and places the current index at the final bar without fitting the full dataset. |
| Misaligned Overview contract | The toolbar describes `Overview` as “Fit the full day into view” at `frontend/src/kline/kline-engine.js:1035`, but `overview()` at `:2666-2677` explicitly resets to the same default latest-bar window instead of fitting all bars. |
| Shared consumers | Review and Static Review both expose the shared engine's `overview()` path (`frontend/src/pages/ReviewPage.jsx:253-257`; `frontend/src/pages/StaticReviewsApp.jsx:224-228`). |
| Acceptance gap | No focused viewport test currently asserts that Review/Static first paint covers the full available day. |

## User Runtime Confirmation

- Confirmed on 2026-07-30 after the initial record was created.
- Action: click the existing `Overview` control in the current page.
- Observed result: the chart returns to the same partial-day/tail-window composition shown in Figure 1.
- Interpretation: `Overview` is not merely failing to fix the default view; its current reset behavior is the direct reproducible path to that view, matching the read-only `overview()` implementation at `frontend/src/kline/kline-engine.js:2666-2677`.
- Required correction if later implemented: both initial Review/Static first paint and the `Overview` reset destination must be the complete truthful day shown by Figure 2.

## OPT-001 Default Full-Day K-Line Viewport

- Source evidence:
  - Current and target screenshots in the Visual Evidence table.
  - Current shared-engine anchors in the table above.
- Current friction:
  - The first chart view is optimized for candle width, so a normal 1m session exposes only the latest slice of the day rather than the complete session shape.
  - Users must manually zoom out to understand the day's high-level trajectory, turning a basic review prerequisite into repeated interaction.
  - User runtime confirmation shows that clicking `Overview` actively returns the chart to Figure 1's partial default window, despite its full-day accessibility/title contract.
- Desired outcome:
  - Review and Static Review first paint show every available candle in the current displayed day/session.
  - The chart automatically fits the complete visible price/volume range and retains all truthful annotations and moving-average overlays.
  - Manual focus actions may temporarily zoom to a trade/signal range, while the full-day overview action returns to the complete day.
  - The behavior is deterministic for 1m and 5m data and for truthful non-standard session lengths.
- Acceptance direction:
  - For a normal 390-bar 1m payload, first-paint viewport debug evidence reports `start = 0`, `end = 389`, and `count = 390`.
  - For a normal 78-bar 5m payload, the corresponding default reports `start = 0`, `end = 77`, and `count = 78`.
  - A short or early-close payload fits its actual first and last bar without padding with invented bars.
  - Review and Static Review produce the same initial viewport for the same payload.
  - Triggering `Overview` after a manual zoom or range focus restores the entire displayed day.
  - Teaching replay keeps its cutoff/follow contract and existing manual navigation remains usable.
- Boundary that must not change:
  - Do not change chart data, session filtering, signals, trade markers, strategies, storage, backend/API behavior, or publication flow.
  - Do not treat this record as implementation or plan authority.
- Lifecycle status: `completed`; [Tang Strategy Default Full-Day K-Line Viewport](../../exec-plans/completed/2026-07-30-tang-strategy-default-full-day-kline-viewport-plan.md) revision `v1-active-2026-07-30` is Completed with independent `implementation-review-001: accept/high` and verified implementation commit `f667867c3e511d2eaaf77f673c96f3e7ed1f70e2`. The user explicitly skipped a separate design-review round for this bounded plan; the user's later `执行这个plan` instruction authorized full local execution.

## Explicit Non-Authorization

This OPT batch records one user-visible viewport requirement and its evidence. Its linked plan reached `Completed` disposition under an explicit user execution instruction and an independent accepted implementation review; neither this record nor the completed plan authorizes DB/data mutation, push, PR, merge, Pages, provider/broker access, hosted verification, or any remote action.
