# Phase 2 — Engine Ownership And Interactive Data/Review Workspaces

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Status: implementation complete; browser acceptance matrix pending (this document is finalized with its results)

## 1. Implemented surface

| Path | Change |
| --- | --- |
| `frontend/src/kline/kline-engine.js` | Engine-owned `Overview` toolbar action (`data-action="overview"`, `aria-label`, native-button keyboard reachability) dispatching to a new engine `overview()` that clears replay reveal/cutoffs/highlights and returns to the latest bar — identical semantics to the former wrapper-level implementation |
| `frontend/src/kline/UnifiedKlineEngine.jsx` | `overview()` now delegates to the single engine owner |
| `frontend/src/features/review/ReviewContextPanel.jsx` | New shared `TickerTabs` (`role=tablist/tab`, `aria-selected`), `DateRail` (month-grouped, ticker-scoped, `aria-pressed`), and `ReviewContextPanel` composition |
| `frontend/src/pages/ReviewPage.jsx` | Workspace panel in the sidebar (tabs + rail + Strategy + Ext K/RTH + Rescan + Backtest + assembly status); entire bottom control bar removed; SPY-preferred default resolution; TraderFilters on readonly context mirrors + availability-driven rendering with context/same-context reconciliation; distinct `rescan()` (in-place recompute) and `openBacktest()` (navigation) |
| `frontend/src/pages/DashboardPage.jsx` | Flat first-20 mixed list replaced by ticker tabs + ticker-scoped date rail; date click selects the day and navigates to Review |
| `frontend/src/pages/BacktestPage.jsx` | Removed page-level Back/Step/Play-Pause/Overview duplicates; `Run latest 10 days` and result selection retained |
| `frontend/src/pages/TeachingPage.jsx` | Removed page-level Play/Pause duplicate; cutoff step/reveal controls retained |
| `frontend/src/main.jsx` | Passes `onNavigate` to Dashboard and Review |
| `frontend/src/styles.css` | `dr-app--no-upload` two-row grid (static keeps its three-row layout), context-panel/tab/rail styles (dark sidebar variant + neutral base) |
| `frontend/src/features/review/reviewWorkspace.test.js` | +3 tests: engine single-owner overview, no page duplicates + distinct Rescan/Backtest + wiring pins, panel aria contract |

Deliberately unchanged in this phase: `StaticReviewsApp.jsx` (Phase 4 parity), `AdminTradersPage.jsx` and the TraderFilters legacy select branch (Phase 3), backend, tracked DB, workflows.

## 2. Verification matrix (plan Phase 2)

| Required proof | Carrier | Result |
| --- | --- | --- |
| Pure transition tests | `reviewWorkspace.test.js` (13 tests) + `tradeRecords.test.js` (18) | pass 31/31 |
| Normal Vite build | `npm run build` | pass |
| Static build unaffected | `VITE_STATIC_REVIEWS=true npm run build:static-reviews` | pass |
| Source-level single-owner assertion | source pins: exactly one `data-action="overview"`; no `dr-upload-bar`/page-level `setTimeframe`/`stepBack`/`stepForward`/`togglePlayback` in Review; no generic replay duplicates in Backtest/Teaching | pass |
| Rescan/Backtest distinction | source pins: `rescan()` in-place vs `onNavigate('backtest')` | pass (browser receipt below) |
| Real-browser Data→Review navigation | pending agent matrix | pending |
| Review context switching (SPY↔QQQ same-date/newest) | pending agent matrix | pending |
| Trader availability + neutral empty state | pending agent matrix | pending |
| Strategy/session behavior | pending agent matrix | pending |
| Backtest/Teaching engine regression | pending agent matrix | pending |
| Engine Overview resets view | pending agent matrix | pending |

## 3. Browser acceptance receipts

API smoke (acceptance stack, temporary DB copy, 2026-07-19): `/api/reviews/assemble` returns non-empty payloads for both tickers on 2026-07-17 — SPY `868` 1m / `192` 5m bars with 1 tang group, QQQ `915` 1m / `191` 5m bars with 2 vordin groups.

Browser matrix (`output/phase-2-acceptance-20260719/`: 11 screenshots, `results.json`, `console-log.json` `[]`, `SHA256SUMS.txt`): **24/24 assertions PASS** in the final run against the current working tree, with zero console errors/warnings/failed requests. Coverage: Data tabs with SPY-default and 46 SPY-only rail dates; QQQ rail exactly `2026-07-10/14/17`; Data→Review reconciliation to QQQ 2026-07-14; fresh Review default SPY 2026-07-17; zero `.dr-upload-bar`; exactly one visible engine `button[data-action="overview"]`; QQQ same-date switch to 2026-07-17; readonly ticker/date mirrors; vordin-only trader rendering on QQQ 2026-07-17 with Tang absent; SPY 2026-05-29 neutral empty state (`role=status`, zero checkboxes); Rescan recomputes in place (instrumented `loadData` bump, no navigation); Backtest navigates to the Backtest page; Backtest results render with engine-only generic toolbar (page toolbar keeps only `Run latest 10 days`); Teaching cutoff advance/reveal with no page Play/Pause; engine Overview resets a signal-zoomed viewport to exactly the initial window (viewport payloads deep-equal, canvas byte-identical). Note: Ext K/Strategy controls render in the context panel with unchanged moved handlers; they were present in captures but not separately click-driven in this matrix.

Round-1 FAIL and fix: the first run failed `Engine Overview resets view to full day` — the initial implementation copied the legacy wrapper semantics (cursor jump only). The fix (`viewportManager.reset()` + follow-latest in `kline-engine.js overview()`) landed mid-run; the agent re-ran the full matrix against the fixed tree, and all reported screenshots/results are from that final 24/24 run. 31/31 pure tests and both builds were re-verified after the fix, and the new semantics are pinned by source test.

## 4. Exit gate statement

`phase-2:complete` is satisfied: each visible control has one owner and one rendering location (engine toolbar for chart-generic controls, Review context panel for business context, page-specific actions retained), no interactive list interleaves tickers (Data rail and Review rail are ticker-scoped), and chart/signals/trades/exports reconcile after SPY↔QQQ switching (same-date preservation, availability reconciliation, readonly mirrors). Evidence: this file plus `output/phase-2-acceptance-20260719/SHA256SUMS.txt`.
