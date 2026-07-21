# Implementation Review Packet 001 — Tang Strategy Review Sidebar Spacing And K-line Selection Band

- Plan target: `docs/exec-plans/completed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md`
- Plan revision: `v2-review-foldback-2026-07-21`
- Packet date: 2026-07-21
- Author ID: `kimi-executor-2026-07-21-sidebar-spacing-selection-band`
- Status: frozen
- Product implementation commit: `5f36d29a44fb12aee2319ae147303cc970d83193`
- Execution authority: goal OBJECTIVE 这个active plan交给你全权负责执行 / `user-instruction:2026-07-21-execute-sidebar-spacing-and-kline-selection-band-plan`

## Implementation Manifest

1. `frontend/src/features/review/TraderFilters.jsx` — `Trade tools` title head removed; optional `exportControls` slot retained (renders head row only when provided; Admin keeps Download)
2. `frontend/src/pages/ReviewPage.jsx` — `TradeExportControls` unmounted from sidebar stack; group/event select clear highlights (`setHighlightRanges(null)`) with fitRange locate retained (0.2/4 group, 0.35/8 event)
3. `frontend/src/pages/StaticReviewsApp.jsx` — full parity with Review for both OPT items
4. `frontend/src/features/review/TraderTradeList.jsx` — `交易者 · Trades` caption as first grid child of `.trade-record-list`
5. `frontend/src/features/review/ReviewSignalList.jsx` — new `.dr-signal-stack` wrapper section + `策略讲解 · Signals` caption (cards and empty state inside)
6. `frontend/src/styles.css` — `.dr-sidebar .dr-signal-list` flex column `gap: 20px`; shared `.stack-caption` + `::after` hairline; `.trade-tools-title` ruleset removed; in-block density pins unchanged
7. `frontend/src/features/review/tradeRecords.js` — doc comment only: `eventFocusPayload` `style` retained for pure tests, unused by live Review/Static trade select after OPT-002; pure oracles untouched
8. `frontend/src/features/review/tradeRecords.test.js` — new **N-Sidebar-source**, **N-Highlight-source**, **N-Span-oracle**; **N-Event-focus** updated to the post-cancel contract; **N-Export-pure** / **N-Marker-regression** retained
9. `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs` — new tracked runner: **B-Sidebar-layout**, **B-Group-band-cancel**, **B-Event-focus-cancel** (Review + Static each) + V1–V3

Not required: `frontend/src/pages/AdminTradersPage.jsx` (§3.1 item 9) — Admin Download composition unchanged because the optional slot was kept. Out of modify set honored: historical `trade-tools-group-span-viewport-data-rail-acceptance.mjs` untouched.

Out of scope (unchanged): backend, API, tracked SQLite, seed, content day files, Pages workflow, provider/broker, progressive DateRail IA, App shell nav, marker vocabulary, in-card density pins, TF/viewport/Data-rail contracts, export payload semantics, Admin visuals.

## Verification Evidence Digest

### N-* carriers (`npm run test:trade-records`)

- Result: **64 / 64 pass** (0 fail; baseline was 61, +3 new carriers)
- **N-Sidebar-source** — Review/Static sources do not mount `TradeExportControls`; `TraderFilters` has no `Trade tools`/`trade-tools-title`; captions/class markers present (`交易者 · Trades`, `策略讲解 · Signals`, `.dr-signal-stack`); 20px gap rule + hairline in `styles.css`; Admin still mounts Download
- **N-Highlight-source** — `selectTradeGroup` / `focusTradeEvent` bodies on both surfaces: `setHighlightRanges(null)`, no painted range object, no `style: 'blue'`, fitRange with frozen padding pairs
- **N-Span-oracle** — frozen fixture group `tg_20260717_vordin_qqq_002` on synthetic RTH 390-bar series: span `[12, 31]` (09:42→10:01), frozen event row 1 `…_l1_e2` → bar `20`; runner constants cross-checked identical
- **N-Event-focus** — single-bar payload distinct from group span; pure `style` field retained for tests only
- **N-Export-pure** / **N-Marker-regression** / **N-Download-source** — existing pure export/marker/download-chrome tests all green

### B-* carriers (mandatory Playwright)

- Runner: `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs`
- Receipts: `output/playwright/review-sidebar-spacing-selection-band-20260721151606/receipts.json` (untracked)
- **B-Sidebar-layout** PASS (Review + Static) — measured gaps exactly `20px`/`20px`; captions 交易者/策略讲解 with `1px solid` hairlines; `toolsTitleCount=0`, `toolsHeadCount=0`, `downloadCount=0`; single Traders label
- **B-Group-band-cancel** PASS (Review + Static) — after frozen group click: `getHighlightRanges()` length `0`; viewport `[8, 35]` contains independent expected span `[12, 31]`; window stable across settle (no post-fit recenter)
- **B-Event-focus-cancel** PASS (Review + Static) — after frozen event-row click: highlights `0`; bar `20` inside viewport `[12, 28]`; window `17 ≤ 120` (not full-day)
- Empty-highlight rule and independent-oracle rule honored throughout (highlight storage never read as expectation)

### Builds and harness

- `npm run build` — exit 0
- `VITE_STATIC_REVIEWS=true npm run build:static-reviews` — exit 0
- `python3 scripts/check-project-harness.py --root . --profile auto` — `passed: true`, `errors: []`
- `git diff --check` on task paths — clean

### V1–V3 screenshots (untracked)

Directory: `output/playwright/review-sidebar-spacing-selection-band-20260721151606/`

| # | File | Coverage |
| --- | --- | --- |
| V1 | `v1-review-sidebar-mid-stack.png` | Review sidebar: 20px gaps, 交易者/策略讲解 captions + hairlines, single Traders row, no Trade tools title, no Download |
| V2 | `v2-review-chart-after-group-select.png` | Review chart after group select: span fitted (09:38–10:03 window), no blue band, marker labels readable |
| V3 | `v3-static-sidebar-and-chart-after-group-select.png` | Static parity: same spacing/captions + post-select chart without band |

## Phase 0 baseline

- Authority: `user-instruction:2026-07-21-execute-sidebar-spacing-and-kline-selection-band-plan`
- HEAD at freeze: `0462fb3329e1462f36754a649a70aebf3255ae42`
- §1.3 evidence hashes: all 3 MATCH plan table
- test:trade-records baseline: 61 pass → post 64 pass
- Frozen fixture: QQQ `2026-07-17` RTH 1m (390 bars 09:30–15:59), desktop `1672x941`
- Frozen group: `tg_20260717_vordin_qqq_002`; oracle span `[12, 31]`; frozen event row `1` (`tg_20260717_vordin_qqq_002_l1_e2`, 09:50 PART) → bar `20`
- Admin Download approach: default §3.1 — optional `exportControls` slot kept; Review/Static omit; Admin unchanged
- CSS/wrapper freeze: `.dr-sidebar .dr-signal-list` flex column `gap: 20px`; three explicit wrappers (`.trade-filter-panel`, `.trade-record-list`, `.dr-signal-stack`); shared `.stack-caption`
- Phase 0 note: `output/phase0-sidebar-spacing-oracle/phase-0-baseline.md` (untracked)

## Authority boundary

- Local commits only
- No push, PR, merge, Pages, provider/broker, DB/content day-file, or remote action
- Untracked `output/` evidence trees preserved unstaged
