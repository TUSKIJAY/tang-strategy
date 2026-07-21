# Implementation Review 001 — Tang Strategy Trade Points And K-line Marker Labels

- Review target: `docs/exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review target commit: `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`
- Review type: implementation
- Reviewer ID: `independent-impl-reviewer-2026-07-21-trade-points-marker-labels-001`
- Plan author ID: `grok-plan-author-2026-07-21-trade-points-kline-labels`
- Packet author ID: `grok-executor-2026-07-21-trade-points-marker-labels`
- Independence declaration: `attested` (reviewer did not author the implementation)
- Evidence method: exact Git ref/log identity for product commit; plan §2.2–§3.1 and packet-001 re-read; live source inspection of `tradeRecords.js`, `TraderTradeList.jsx`, `tradeRecords.test.js`, `content/traders/index.json`; dual-surface registry/day-file/projection-path proof; structural suite carrier inventory (54 tests incl. N-Marker-label / N-Action-map / N-Card-time-range / N-Card-source); direct vision inspection of V1–V3 (and V2b) PNGs under `output/playwright/trade-points-marker-labels-20260721/`; receipts.json; authority boundary check
- Verdict: accept
- Confidence: high

## Scope Checked

- Product commit identity: branch `codex/project-harness` HEAD and `refs/heads/codex/project-harness` are `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`; reflog parent is Phase-0 baseline `554be376aef7f74dd2db49c18498459f657102d5`; commit subject is `feat: trade points reading path and BUY/SELL marker labels`. Packet product commit hash **matches** the inspected tree tip.
- Plan §3.1 manifest surfaces present and carrying the frozen contracts:
  1. `frontend/src/features/review/tradeRecords.js` — `tradeEventActionSide`, `groupEventTimeRange`, `buildTradeRecordAnnotations` with display_name + BUY/SELL for **both** `marker_label` and `title`, action-side grouping, no `void traders`
  2. `frontend/src/features/review/TraderTradeList.jsx` — outcome/fees removed from reading path; meta uses pure `groupEventTimeRange`; CALL/PUT chrome retained
  3. `frontend/src/features/review/tradeRecords.test.js` — **N-Marker-label**, **N-Action-map**, **N-Card-time-range**, **N-Card-source** present and assert shipped helpers
  4. `content/traders/index.json` — `vordin.display_name === "vordinkkk"`; `trader_id` remains `vordin`
  5. `data/sqlite/tang_strategy_live_extended.db` — in product manifest via candidate projection path (see dual-surface)
  6. Additive evidence harness `scripts/verify-trade-points-marker-labels.mjs` (not a product contract expansion)
- Dual-surface nickname:
  - JSON: live `content/traders/index.json` has `trader_id: "vordin"`, `display_name: "vordinkkk"`
  - Day files keep `trader_id: "vordin"` (spot-checked `content/trades/2026-07-17.json` and multi-day grep); no day-file rewrite of trader identity
  - Projection path frozen: `PUT /api/admin/traders` → `handle_trader_registry_admin_write(..., after_replace=_sync_trade_projection)` → candidate project + integrity/FK + atomic promote; `replace_trade_repository` inserts `traders.display_name` from registry; view `v_trade_group_performance` joins `traders.display_name`
  - Runtime paint proof: interactive V1 and static V3 screenshots (acceptance DB copy of tracked SQLite) show chip/card name `vordinkkk`, not `沃德哥` / raw `vordin`
- N-* carriers: suite inventory is 29 (`tradeRecords.test.js`) + 18 (`reviewWorkspace.test.js`) + 7 (`traderRegistry.test.js`) = **54** tests; the four required carriers are present and drive shipped helpers:
  - **N-Action-map** — exact four-action map; empty/unknown omit; no `?`; same-bar BUY≠SELL; same-side ×N
  - **N-Marker-label** — display_name + BUY/SELL on label **and** title; ×N label-only; no CALL/PUT; vordinkkk nickname; fallback to trader_id
  - **N-Card-time-range** — multi-leg out-of-order min/max; incomplete ignored; zero/one/two-or-more labels
  - **N-Card-source** — source scan: consumes `groupEventTimeRange`; no `outcomeLabel` / `return_pct` / fees span; CALL/PUT chrome retained
- Card reading path: `TraderTradeList.jsx` has no `outcomeLabel`, `fees`, `return_pct`, `reported_outcome`, or `calculated_outcome` rendering; expanded rows are time · action · qty @ premium only
- Marker builders: neither `marker_label` nor `title` include CALL/PUT; direction remains shape/color/direction fields only
- Visual matrix (direct vision):
  - **V1** `v1-interactive-cards-qqq-2026-07-17.png` — `vordinkkk` cards; meta `QQQ · 2026-07-17 · 09:42 → 10:43`; expanded legs without fees/outcome %/$; CALL/PUT chrome retained
  - **V2** `v2-interactive-markers-qqq-2026-07-17.png` — visible labels `vordinkkk BUY`, `vordinkkk SELL`, `vordinkkk SELL ×2`; no CALL/PUT in marker text
  - **V2b** `v2b-after-card-click.png` — hover title vocabulary `vordinkkk SELL` (no raw action / CALL / PUT)
  - **V3** `v3-static-review-qqq-2026-07-17.png` — static parity: same card subtraction + `vordinkkk`
  - `receipts.json` records V1–V3 **PASS** with matching snippets
- Authority: packet and plan claim local commits only; no push, PR, merge, Pages, provider/broker, or remote action asserted. This review writes **only** this review artifact.

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | — | — |

## Verdict Rationale

The product commit `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145` matches packet-001 and the current branch tip. Live sources implement every §2.2 success criterion inside the §3.1 manifest: points-only card meta via pure cross-leg time range, fees/outcome removed from the reading path, CALL/PUT chrome retained, marker **label and title** both using display_name + BUY/SELL with fail-closed four-action map and action-side grouping, and `vordin` UI nickname `vordinkkk` without day-file or `trader_id` rewrites. The four mandatory N-* carriers exist in `tradeRecords.test.js` and assert the shipped helpers; suite size matches packet **54/54**. Screenshots and receipts cover V1–V3 (plus V2b tooltip) for QQQ `2026-07-17`. Dual-surface registry is satisfied by live JSON + atomic projection path + runtime paint evidence; day files still key on `vordin`. No authority overreach (push/remote/Pages) is claimed.

Verdict: **accept/high**.

This accept does not authorize push, PR, merge, Pages, provider/broker, further product mutation, plan migration to completed, or PROGRESS/HANDOFF updates. Closeout remains a separate lifecycle step under existing operating-modes rules.
