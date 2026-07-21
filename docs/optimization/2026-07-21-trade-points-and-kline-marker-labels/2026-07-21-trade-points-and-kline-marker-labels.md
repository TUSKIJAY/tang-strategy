# Optimization Batch · 2026-07-21

> Record-only intake. This file does not authorize implementation.
>
> Place this file at:
> `docs/optimization/2026-07-21-trade-points-and-kline-marker-labels/2026-07-21-trade-points-and-kline-marker-labels.md`
> Put evidence images in the sibling `screenshots/` folder and link them as `./screenshots/<name>.png`.
>
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. A draft, failed/incomplete record, explicit no-commit instruction, or unclear path ownership prevents that commit. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Trade Card Simplification: Points Only | Review / Trade Cards UI | recorded | none | 做减法：去掉金额与盈收比例，只保留交易时间点位 |
| OPT-002 | K-Line Markers: BUY/SELL + Nickname `vordinkkk` | Review / K-Line + Trader display | recorded | none | 标签改 BUY/SELL；UI 昵称 `vordinkkk` → 保存 `trader_id: vordin` |

## Visual Reference

- Trade cards screenshot: [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png)
- K-line markers screenshot: [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png)
  - Live labels: `vordin PUT` / `vordin CALL` / `vordin CALL ×2`
- Combined interactive mockup: [`mockups/trade-points-and-kline-labels.html`](./mockups/trade-points-and-kline-labels.html)

## Supersedes

This batch merges two earlier same-day record-only batches:

- [`../2026-07-21-trade-card-simplify-points-only/2026-07-21-trade-card-simplify-points-only.md`](../2026-07-21-trade-card-simplify-points-only/2026-07-21-trade-card-simplify-points-only.md) → `superseded`
- [`../2026-07-21-kline-marker-action-and-trader-nickname/2026-07-21-kline-marker-action-and-trader-nickname.md`](../2026-07-21-kline-marker-action-and-trader-nickname/2026-07-21-kline-marker-action-and-trader-nickname.md) → `superseded`

## OPT-001 Trade Card Simplification (Points Only)

- Source evidence: [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png). User: 做减法，不需要展示金额和盈收比例，只需要展示交易时间点位。
- Current friction: Cards / expanded legs still surface `$` amounts and profit ratios (or outcome % / PnL-style noise), pulling attention away from **when** a point occurred and **at what price**.
- Desired outcome: Presentation-only subtraction — primary reading path is **timestamps + price points**. Drop amount ($) and profit rate (%) from the card UI.
- Boundary that must not change: Schema / API / reported·calculated outcome fields may remain in data; Review / Static / Admin shared card family; CALL/PUT direction chrome and Eligibility/Download chrome are not part of this subtraction unless a later OPT says so.
- Lifecycle status: recorded

## OPT-002 K-Line Markers: BUY/SELL + Nickname Mapping

- Source evidence: [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png) plus user instruction: 颜色与箭头已区分 call/put，不必再写 call/put 文字；改写 buy/sell 以便一眼看到该时间点的操作；界面只显示英文昵称 `vordinkkk`，数据库仍知 沃德哥 → `vordin`。
- Current friction:
  1. Marker text is `` `{trader_id} {CALL|PUT}` `` (e.g. `vordin CALL ×2`). Direction is already encoded by color + triangle shape, so the text slot does not show buy vs sell.
  2. Markers use raw `trader_id` `vordin` (and chips/cards use Chinese `沃德哥`) rather than preferred English nickname `vordinkkk`.
- Desired outcome:
  1. Marker labels render **BUY** / **SELL** from event action; shape+color still own CALL/PUT.
  2. UI shows **`vordinkkk`**; persistence keeps **`trader_id: vordin`** (沃德哥) without a second identity.
- Boundary that must not change: Event option type + action fields; canonical `trader_id` slug and existing day files keyed by `vordin`; registry field shape (`display_name` vs nickname) frozen at plan time. Card CALL/PUT badges may remain unless OPT-001 scope expands.
- Live source contract: `frontend/src/features/review/tradeRecords.js` builds `marker_label` as `` `${trader_id} ${CALL|PUT}` `` with optional `×N`.
- Lifecycle status: recorded
