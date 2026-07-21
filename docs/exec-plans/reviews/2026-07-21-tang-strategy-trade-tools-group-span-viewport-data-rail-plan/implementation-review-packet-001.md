# Implementation Review Packet 001 — Tang Strategy Trade Tools, Group Span, Viewport, And Data Rail

- Plan target: `docs/exec-plans/completed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md`
- Plan revision: `v3-review-foldback-2026-07-21`
- Packet date: 2026-07-21
- Author ID: `grok-executor-2026-07-21-trade-tools-group-span-viewport-data-rail`
- Status: frozen
- Product implementation commit: `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`
- Execution authority: goal OBJECTIVE 交给你全权负责执行active plan / `user-instruction:2026-07-21-execute-trade-tools-group-span-viewport-data-rail-plan`

## Implementation Manifest

1. `frontend/src/features/review/TraderFilters.jsx` — Eligibility tools chrome removed; Download/Traders retained
2. `frontend/src/features/review/tradeRecords.js` — `canonicalizeTradeToolsFilters`; forced display-only filter/displayable/export; `groupBarSpan`, `groupCardMeta`, `groupTimelineEvents`, `eventFocusPayload`, `tradeEventActionLabel`
3. `frontend/src/features/review/TraderTradeList.jsx` — meta span + `N pts`; compact BUY/SELL/PART timeline; `onEventFocus`
4. `frontend/src/pages/ReviewPage.jsx` — blue band + fitRange group-select (no post-fit center); event-row focus
5. `frontend/src/pages/StaticReviewsApp.jsx` — Review parity for group-select + event focus
6. `frontend/src/kline/kline-engine.js` — TF switch resets `zoomScale=1`; public `getViewportDebug()`
7. `frontend/src/kline/UnifiedKlineEngine.jsx` — ref + container `__klineEngine` seam for Playwright
8. `frontend/src/pages/DashboardPage.jsx` — host class exactly `data-market-days-rail`
9. `frontend/src/styles.css` — timeline styles; density scoped under `.data-market-days-rail` (≤420px); Eligibility tools CSS removed
10. `frontend/src/features/review/tradeRecords.test.js` — all **N-*** carriers
11. `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs` — **B-TF-first-paint**, **B-Group-span**, **B-Data-rail-layout**, V1–V6

Out of scope (unchanged): backend, tracked SQLite, content day JSON, OPT-001/002, Admin editor eligibility flags, provider/Pages/remote.

## Verification Evidence Digest

### N-* carriers (`npm run test:trade-records`)

- Result: **61 / 61 pass** (0 fail)
- Log: scratch `test-trade-records.log`
- Covers:
  - **N-Eligibility-removed-source** — tools strip has no Eligibility/Display/Reported/Calculated; Admin editor flags remain
  - **N-Eligibility-default** — canonicalize + filter + displayable + export for omitted/display/reported/calculated; non-display group excluded; `display_only: true`
  - **N-Group-span** — min/max indices; multi vs single; incomplete ignored
  - **N-Card-meta** — span + `N pts` = complete-timed count
  - **N-Timeline-source** — BUY/SELL/PART rows; no fees
  - **N-Event-focus** — single-bar payload distinct from group span; Review/Static blue + no center:true
  - **N-Data-rail-source** — host class + scoped CSS ≤420px

### B-* carriers (mandatory Playwright)

- Runner: `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs`
- Receipts: `output/playwright/trade-tools-group-span-20260721122508/receipts.json` (untracked)
- Log: scratch `playwright-b-carriers.log`
- **B-TF-first-paint** PASS — QQQ 2026-07-17 desktop; 1m→5m and 5m→1m; first completed `render()` via toolbar click; `zoomScale===1`; zero wheel
- **B-Group-span** PASS — Review multi-event select → blue band → event-row single-bar → card restore; Static parity receipt `B-Group-span-static`
- **B-Data-rail-layout** PASS — Data host ≤420px; Review `.dr-sidebar` ticker `flex-grow:1`; narrow V6 usable

### Builds and harness

- `npm run build` — exit 0
- `VITE_STATIC_REVIEWS=true npm run build:static-reviews` — exit 0
- `python3 scripts/check-project-harness.py --root . --profile auto` — `passed: true`
- `git diff --check` on task paths — exit 0
- Log: scratch `builds-harness.log`

### V1–V6 screenshots (untracked)

Directory: `output/playwright/trade-tools-group-span-20260721122508/`

| # | File | Coverage |
| --- | --- | --- |
| V1 | `v1-review-tools-timeline.png` | No Eligibility; timeline BUY/SELL/PART; meta span + N pts |
| V2 | `v2-review-group-span-band.png` | Full span fit; blue multi-bar band |
| V3 | `v3-data-market-days-rail.png` | Compact Data rail under host class |
| V4 | `v4-review-tf-5m-first-paint.png` | Supplemental 5m first-paint visual |
| V5 | `v5-review-sidebar-desktop.png` | Review sidebar intentional stretch |
| V6 | `v6-review-sidebar-narrow.png` | Narrow 390×844 usable |

## Phase 0 baseline

- Authority: `user-instruction:2026-07-21-execute-trade-tools-group-span-viewport-data-rail-plan`
- HEAD at freeze: `e4ccb671a2234c0cddaec09e3260af8b71262a14`
- §1.3 evidence hashes: all MATCH plan table
- trade-records baseline: 54 pass → post 61 pass
- Frozen multi-event group: `tg_20260717_vordin_qqq_002`
- Frozen TF fixture: QQQ `2026-07-17` desktop `1672x941`
- Frozen narrow: `390x844`
- Scratch: `phase0-freeze.txt`

## Authority boundary

- Local commits only
- No push, PR, merge, Pages, provider/broker, DB/content day-file, or remote action
- Untracked `output/` evidence trees preserved unstaged
