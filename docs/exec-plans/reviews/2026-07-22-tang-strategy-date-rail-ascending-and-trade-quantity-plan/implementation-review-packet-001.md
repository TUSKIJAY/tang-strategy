# Implementation Review Packet 001 — Tang Strategy Date Rail Ascending And Trade Quantity

- Plan target: `docs/exec-plans/active/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md`
- Plan revision: `v2-review-foldback-2026-07-22`
- Packet date: 2026-07-22
- Author ID: `kimi-executor-2026-07-22-date-rail-quantity`
- Status: frozen
- Product implementation commit: `da12e1b03715be3de75fcafd8d47aa1a35554942`
- Execution authority: goal OBJECTIVE 你来全权负责执行这个plan / `user-instruction:2026-07-22-execute-date-rail-ascending-and-trade-quantity-plan`

## Implementation Manifest

1. `frontend/src/features/review/reviewWorkspace.js` — `projectProgressiveDateRail` reverses only the projected `dates` array (最近 newest-N slice and 按月 `datesInMonth` filter) so chips render ascending; `datesForTicker` / `recentDatesForTicker` / `listMonthsForTicker` / `stepBrowsedMonth` / `groupDatesByMonth` keep newest-first inventory; `PROGRESSIVE_RECENT_LIMIT` membership and meta strings unchanged
2. `frontend/src/features/review/tradeRecords.js` — new pure helpers `deriveCloseQuantity(leg, closeEvent)` (completeness rule: every prior `buy_open`/`buy_add`/`sell_partial` qty finite, sequence-ordered "prior", over-partial → null, no-opening → null) and `eventDisplayQuantity(leg, event)` (raw numeric preferred, null `sell_close` falls back to derivation); `groupTimelineEvents` rows expose the effective quantity; `buildTradeRecordAnnotations` tracks per-event quantity and emits `*QTY` on **both** `marker_label` and `title` only when every same-side same-bar contributor is known (sums multi-event groups); `×N` suffix path removed
3. `frontend/src/features/review/TraderTradeList.jsx` — unchanged: `row.quantity ?? '?'` already consumes the derived field (manifest item 3 "only if needed" → not needed)
4. `frontend/src/features/review/tradeRecords.test.js` — updated `×N` pins to `*QTY` (marker-color test, N-Action-map, N-Marker-label); new **N-Qty-derive** (PUT 150 / CALL 12 live-mirror chains, raw-preferred, unknown-open, over-partial, adversarial null `buy_add`, adversarial null prior `sell_partial`, sequence-order "prior", no-opening), **N-Marker-qty** (no `×`; `*QTY` label+title; same-bar sums 24/34; derived closes 150/12; mixed known/unknown same-bar omits suffix on both; direction shape/color/anchor unchanged; no CALL/PUT text), **N-Timeline-qty** (derived 150 @ 0.15 / 12 @ 5.5 rows; unsafe chains stay null; raw close passthrough; no `derived` chrome in list source)
5. `frontend/src/features/review/reviewWorkspace.test.js` — new **N-Date-asc** (recent + month projection strictly ascending; selected latest day is last chip) and **N-Date-membership** (recent set = newest-12; meta counts unchanged; inventory helpers + month bar semantics stay newest-first); existing progressive assertions retained
6. `frontend/scripts/playwright/date-rail-ascending-trade-quantity-acceptance.mjs` — new tracked runner with DOM oracles (chip `title` order strictly ascending for 最近 + 按月; pressed chip = selected day; timeline text contains `SELL 150 @ 0.15` and `SELL 12 @ 5.5`) + V1–V3 screenshots
7. `scripts/verify-trade-points-marker-labels.mjs` — comment-only: stale `×N ok` note updated to `*QTY` vocabulary

Not required: `reviewWorkspace.fixtures.js` (manifest item 6) — adversarial fixtures are test-local in `tradeRecords.test.js`; existing fixtures untouched.

Out of scope (unchanged): `content/trades/**`, tracked SQLite, seed market data, backend APIs, Pages workflows, provider/broker, marker shape/color/anchor ownership, action→BUY/SELL map, grouping key family, month switcher UX, Admin editor, selection-band/fitRange contracts.

## Verification Evidence Digest

### N-* carriers (`npm run test:trade-records`)

- Result: **69 / 69 pass** (0 fail; baseline was 64, +5 new carriers)
- **N-Date-asc** — recent projection `2026-06-14 … 2026-07-10` strictly ascending with pressed latest day last; month projection `2026-06-01 … 2026-06-15` strictly ascending
- **N-Date-membership** — recent chip set equals newest-12 inventory (`datesForTicker` slice); meta `显示最近 12 · 全库 SPY 25` / `本月交易日 15 · 全库 SPY 25` unchanged; `listMonthsForTicker` `['2026-07','2026-06']` and `stepBrowsedMonth` older/newer semantics unchanged
- **N-Qty-derive** — PUT leg null close → 150; CALL leg null close → 12 (70 − 58); raw close 5 preferred with incomplete prior chain; unknown open / over-partial (16 > 10) / null `buy_add` / null prior `sell_partial` / no-opening → null; "prior" follows sequence order (post-close null add does not block)
- **N-Marker-qty** — no `×` on any label/title; `vordinkkk BUY*150` / `SELL*150` (derived), `BUY*70`, same-bar `SELL*24` (12+12) and `SELL*34` (22+12), derived close `SELL*12`; mixed known/unknown same-bar pair → bare `vordinkkk SELL` on both fields; PUT triangle_down/top/`#E06B66`, CALL triangle_up/bottom/`#6F9F7A`; no CALL/PUT text
- **N-Timeline-qty** — `groupTimelineEvents` exposes derived 150 (premium 0.15) and 12 (premium 5.5); unsafe chain rows stay null; raw close 5 passthrough; `TraderTradeList.jsx` still renders `row.quantity ?? '?'` with no `derived` chrome

### V1–V3 (Playwright, mandatory receipts)

- Runner: `frontend/scripts/playwright/date-rail-ascending-trade-quantity-acceptance.mjs` — ALL PASS
- Receipts: `output/playwright/date-rail-qty-20260722023705/receipts.json` (untracked)
- **V1-recent** PASS — QQQ rail chips `2026-07-02 … 2026-07-20` strictly ascending (DOM titles), pressed chip `2026-07-17`; screenshot `v1a-rail-recent-ascending.png`
- **V1-month** PASS — 按月 chips strictly ascending; screenshot `v1b-rail-month-ascending.png`
- **V2** PASS — QQQ `2026-07-17` markers `vordinkkk SELL*150` / `SELL*24` / `SELL*34` / `SELL*12` / `BUY*150` / `BUY*70`, no `×N`, direction shapes preserved; screenshot `v2-kline-marker-qty-labels.png`
- **V3** PASS — expanded vordin cards show `SELL 150 @ 0.15` and `SELL 12 @ 5.5` (no `?` on those rows); screenshot `v3-timeline-derived-close-qty.png`

### Builds and harness

- `npm run build` — exit 0
- `VITE_STATIC_REVIEWS=true npm run build:static-reviews` — exit 0
- `python scripts/check-project-harness.py --root . --profile auto` — `passed: true`, `errors: []`
- `python scripts/check-operating-modes.py --root .` — `passed: true`, `errors: []`
- `git diff --check` on task paths — clean

## Phase 0 baseline

- Authority: `user-instruction:2026-07-22-execute-date-rail-ascending-and-trade-quantity-plan`
- HEAD at freeze: `4f508782006d3ed8d46ce3c05b8c478247fe1241` (branch `codex/project-harness`; only untracked `output/` trees dirty — preserved)
- test:trade-records baseline: 64 pass → post 69 pass
- OPT-001 approach freeze: projection-only `dates` reverse inside `projectProgressiveDateRail`; no deeper `datesForTicker` change
- Fixture freeze: test-local live-mirror legs for QQQ `2026-07-17` vordin PUT 150 / CALL 12 chains (cross-checked against `content/trades/2026-07-17.json` on 2026-07-22) + raw-preferred, unknown-open, over-partial, null-`buy_add`, null-prior-`sell_partial`, mixed same-bar adversarial cases
- Phase 0 note: `output/date-rail-ascending-trade-quantity-20260722/phase-0-baseline.md` (untracked)

## Authority boundary

- Local commits only
- No push, PR, merge, Pages, provider/broker, DB/content day-file, or remote action
- Untracked `output/` evidence trees preserved unstaged
