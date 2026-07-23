# Phase 0 Baseline — date-rail ascending + trade quantity plan

- Plan: `docs/exec-plans/active/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md` @ `v2-review-foldback-2026-07-22`
- Baseline HEAD: `4f508782006d3ed8d46ce3c05b8c478247fe1241` (branch `codex/project-harness`, ahead 8, only untracked `output/` trees — preserved)
- Baseline `npm run test:trade-records`: **64/64 green**
- Implementation-start authority: user instruction "你来全权负责执行这个plan" (2026-07-22)

## OPT-001 approach decision (frozen)

Projection-only chip-order flip in `projectProgressiveDateRail` (`reviewWorkspace.js`):
reverse only the projected `dates` array for both 最近 and 按月 modes after the
newest-first slice/filter. `datesForTicker`, `recentDatesForTicker`,
`listMonthsForTicker`, `stepBrowsedMonth`, and `groupDatesByMonth` keep
newest-first inventory semantics untouched; meta strings and
`PROGRESSIVE_RECENT_LIMIT` membership unchanged. No deeper `datesForTicker`
change — the pure split is exactly "inventory newest-first, chip projection
ascending".

## Pure fixture freeze (N-Qty-derive / N-Marker-qty / N-Timeline-qty)

Test-local fixtures in `tradeRecords.test.js` mirroring `content/trades/2026-07-17.json`:

1. QQQ vordin PUT `tg_20260717_vordin_qqq_001`: open 150, `sell_close` null → derived **150**.
2. QQQ vordin CALL `tg_20260717_vordin_qqq_002`: open 70, partials 12+12+22+12, `sell_close` null → derived **12**.
3. Raw numeric close preferred even with incomplete prior chain.
4. Unknown open (null qty) → unknown.
5. Over-partial sum > open → unknown.
6. Adversarial: known open + null `buy_add` → unknown.
7. Adversarial: null prior `sell_partial` → unknown.
8. Adversarial: same-bar mixed known/unknown contributor quantities → omit `*QTY` on label + title.

Live content cross-checked 2026-07-22: `tg_20260717_vordin_qqq_001` open 150 / close null;
`tg_20260717_vordin_qqq_002` open 70, partials 12/12/22/12, close null. Matches §1.4.

## Scope check

Manifest paths only: `frontend/src/features/review/{reviewWorkspace.js, tradeRecords.js,
TraderTradeList.jsx, tradeRecords.test.js, reviewWorkspace.test.js, reviewWorkspace.fixtures.js}`.
No `content/trades/**`, DB, backend, or provider paths touched.
