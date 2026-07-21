# Implementation Review Packet 001 — Tang Strategy Trade Points And K-line Marker Labels

- Plan target: `docs/exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`
- Plan revision: `v2-review-foldback-2026-07-21`
- Packet date: 2026-07-21
- Author ID: `grok-executor-2026-07-21-trade-points-marker-labels`
- Status: frozen
- Product implementation commit: `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`
- Execution authority: goal OBJECTIVE accept-active-plan-until-complete / `user-instruction:2026-07-21-execute-trade-points-and-kline-marker-labels-plan`

## Implementation Manifest

1. `frontend/src/features/review/tradeRecords.js` — `tradeEventActionSide`, `groupEventTimeRange`, `buildTradeRecordAnnotations` display_name + BUY/SELL label+title, action-side grouping
2. `frontend/src/features/review/TraderTradeList.jsx` — outcome/fees subtraction; meta uses pure time-range helper; CALL/PUT chrome retained
3. `frontend/src/features/review/tradeRecords.test.js` — **N-Marker-label**, **N-Action-map**, **N-Card-time-range**, **N-Card-source**
4. `content/traders/index.json` — `vordin.display_name = vordinkkk` via atomic write path
5. `data/sqlite/tang_strategy_live_extended.db` — candidate projection promote only
6. `scripts/verify-trade-points-marker-labels.mjs` — deterministic V1–V3 screenshot harness

Out of scope (unchanged by design): day trade JSON, Eligibility/Download chrome, density CSS, OPT-003…006, provider/Pages/remote.

## Verification Evidence Digest

### N-* carriers (`npm run test:trade-records`)

- Result: **54 / 54 pass** (0 fail)
- Log: scratch `test-trade-records.log`
- Covers:
  - **N-Marker-label** — display_name + BUY/SELL on `marker_label` and `title`; ×N label-only; no CALL/PUT; vordinkkk nickname; fallback to trader_id
  - **N-Action-map** — four schema actions; empty/unknown omit; same-bar BUY≠SELL; same-side ×N
  - **N-Card-time-range** — multi-leg out-of-order min/max; incomplete ignored; zero/one/two-or-more labels
  - **N-Card-source** — no outcomeLabel/return_pct/fees span; consumes `groupEventTimeRange`; CALL/PUT chrome retained
  - Existing pure filter/export contracts remain green

### N-Registry-dual

- Path: `handle_trader_registry_admin_write(..., after_replace=_sync_trade_projection)`
- JSON: `vordin.display_name === "vordinkkk"`
- SQLite `traders` + `v_trade_group_performance`: `vordin → vordinkkk`
- integrity_check=ok; foreign_key_check=[]
- Counts unchanged: traders=2, trade_groups=33, trade_legs=33, trade_events=46, market_days=49, strategies=11
- Day files keep `trader_id: vordin`
- Receipt: scratch `n-registry-dual.md`

### Builds and harness

- `npm run build` — exit 0
- `VITE_STATIC_REVIEWS=true npm run build:static-reviews` — exit 0
- `python scripts/check-project-harness.py --root . --profile auto` — `passed: true`
- `python scripts/check-operating-modes.py --root .` — `passed: true`
- Log: scratch `builds-harness.log`

### V1–V3 screenshots (untracked)

Directory: `output/playwright/trade-points-marker-labels-20260721/`

| # | File | Coverage |
| --- | --- | --- |
| V1 | `v1-interactive-cards-qqq-2026-07-17.png` | Interactive cards: `vordinkkk`, time span `09:42 → 10:43`, expanded legs without fees/outcome %/$ |
| V2 | `v2-interactive-markers-qqq-2026-07-17.png` | After zoom-out: visible labels `vordinkkk BUY`, `vordinkkk SELL`, `vordinkkk SELL ×2`; no CALL/PUT in marker text |
| V3 | `v3-static-review-qqq-2026-07-17.png` | Static parity: same card subtraction + `vordinkkk` |

Receipt: `output/playwright/trade-points-marker-labels-20260721/receipts.json`

## Phase 0 baseline

- HEAD at freeze: `554be376aef7f74dd2db49c18498459f657102d5`
- §1.3 evidence hashes: all MATCH
- Pre-mutation vordin: `沃德哥` on JSON+DB; integrity/FK ok
- Scratch: `phase0/baseline.md`

## Authority boundary

- Local commits only
- No push, PR, merge, Pages, provider/broker, or remote action
- Untracked `output/local-acceptance/` and prior polish Playwright trees preserved unstaged
