# Optimization Batch · 2026-07-21

> Record-only intake. This file does not authorize implementation.
>
> **Session-consolidated batch.** All 2026-07-21 Review trade-panel / K-line friction from this optimization-record session lives here. Earlier same-day split batches are `superseded` (see below).
>
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Trade cards: points only (drop $ / %) | Review / Trade Cards | recorded | none | 只保留交易时间点位 |
| OPT-002 | K-line markers: BUY/SELL + nickname `vordinkkk` | Review / K-line + trader display | recorded | none | 方向靠颜色箭头；UI 昵称映射 `vordin` |
| OPT-003 | Trade tools: remove Eligibility segment | Review / Trade tools | recorded | none | 取消 Display / Reported / Calculated 整行 |
| OPT-004 | K-line 5m switch: first-paint viewport glitch | Review / Kline Engine | recorded | none | 点 5m 先坏图，滚轮后才正常 |

## Visual Reference

| Evidence | Path |
| --- | --- |
| Trade cards (amount / profit noise context) | [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png) |
| K-line markers live (`vordin CALL/PUT`) | [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png) |
| Eligibility row to remove | [`screenshots/2026-07-21-trade-tools-eligibility-remove.png`](./screenshots/2026-07-21-trade-tools-eligibility-remove.png) |
| 5m switch broken first paint | [`screenshots/2026-07-21-kline-5m-switch-initial-viewport.png`](./screenshots/2026-07-21-kline-5m-switch-initial-viewport.png) |
| **Session mock (all UI items)** | [`mockups/review-trade-and-kline-session.html`](./mockups/review-trade-and-kline-session.html) |

## Supersedes (this session)

| Previous batch | Status |
| --- | --- |
| [`../2026-07-21-trade-card-simplify-points-only/`](../2026-07-21-trade-card-simplify-points-only/2026-07-21-trade-card-simplify-points-only.md) | superseded → OPT-001 |
| [`../2026-07-21-kline-marker-action-and-trader-nickname/`](../2026-07-21-kline-marker-action-and-trader-nickname/2026-07-21-kline-marker-action-and-trader-nickname.md) | superseded → OPT-002 |
| [`../2026-07-21-trade-points-and-kline-marker-labels/`](../2026-07-21-trade-points-and-kline-marker-labels/2026-07-21-trade-points-and-kline-marker-labels.md) | superseded → OPT-001 + OPT-002 (partial merge) |
| [`../2026-07-21-kline-5m-switch-viewport-glitch/`](../2026-07-21-kline-5m-switch-viewport-glitch/2026-07-21-kline-5m-switch-viewport-glitch.md) | superseded → OPT-004 |

---

## OPT-001 Trade cards: points only

- Source evidence: [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png). User: 做减法，不需要金额和盈收比例，只展示交易时间点位。
- Current friction: Cards / expanded legs surface `$` amounts, fees, and profit / return % noise.
- Desired outcome: Presentation-only subtraction — **timestamps + price points** only on the card reading path.
- Boundary: Schema / API / reported·calculated fields may remain in data; Review / Static / Admin shared cards; presentation only.
- Lifecycle status: recorded

## OPT-002 K-line markers: BUY/SELL + nickname `vordinkkk`

- Source evidence: [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png). Live labels: `vordin CALL` / `vordin PUT` / `vordin CALL ×2`.
- Current friction: Marker text repeats CALL/PUT while color + triangle already encode direction; no buy vs sell; raw `trader_id` / 沃德哥 instead of preferred English nickname.
- Desired outcome:
  1. Marker text = **BUY** / **SELL** (from event action); shape+color still own CALL/PUT.
  2. UI shows **`vordinkkk`**; persistence keeps **`trader_id: vordin`** (沃德哥).
- Boundary: Event option type + action fields; canonical `trader_id`; historical day files. Card CALL/PUT badges may remain.
- Live contract note: `tradeRecords.js` builds `marker_label` as `` `${trader_id} ${CALL|PUT}` `` (+ optional `×N`).
- Lifecycle status: recorded

## OPT-003 Trade tools: remove Eligibility segment

- Source evidence: [`screenshots/2026-07-21-trade-tools-eligibility-remove.png`](./screenshots/2026-07-21-trade-tools-eligibility-remove.png) — yellow box around **Eligibility · Display / Reported / Calculated**. User: 都取消，不需要展示这部分内容。
- Current friction: Trade tools still exposes the Eligibility segmented control. User does not want this chrome on the Review trade panel surface.
- Desired outcome: **Remove** the Eligibility row (label + Display / Reported / Calculated segments) from Trade tools UI so it is not shown. Keep Download and Traders chip area unless later OPT says otherwise.
- Boundary:
  - Underlying eligibility flags on groups / admin editor forms are **not** automatically deleted from schema by this UI hide; plan time decides whether filter state hard-defaults to display-eligible only, or admin-only controls remain elsewhere.
  - Primary surface: shared Trade tools used by Review (and Static/Admin if same component).
- Live source: `frontend/src/features/review/TraderFilters.jsx` Eligibility `radiogroup`.
- Lifecycle status: recorded

## OPT-004 K-line 5m switch first-paint viewport glitch

- Source evidence: [`screenshots/2026-07-21-kline-5m-switch-initial-viewport.png`](./screenshots/2026-07-21-kline-5m-switch-initial-viewport.png). User: 点 5m 先出现该异常画面（K 线挤左、右侧空白），**滚轮后**才正常。
- Current friction: Timeframe switch to 5m does not land a correct full-window viewport on the first render; wheel path recalculates and fixes it.
- Desired outcome: First `render` after `setTimeframe('5m')` (ideally any TF switch) must show a correct viewport without wheel interaction.
- Likely surface (investigation only): `frontend/src/kline/kline-engine.js` `setTimeframe` + shared `ViewportManager.zoomScale` / `viewStart` vs 1m→5m window constants.
- Boundary: No change to bars payloads / assemble / seed contracts; not a publish/DB issue.
- Lifecycle status: recorded
