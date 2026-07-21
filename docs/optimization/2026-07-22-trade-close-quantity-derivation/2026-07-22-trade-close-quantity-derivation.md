# Optimization Batch · 2026-07-22 Trade Close Quantity Derivation

> Record-only intake. This file does not authorize implementation, plan promotion, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-22-trade-close-quantity-derivation/2026-07-22-trade-close-quantity-derivation.md`
> Evidence images live in `./screenshots/`.
>
> Mode entered: 2026-07-22 by user instruction `这种开头交易就显示了总数，结尾的时候自然而然就可以计算出总和，不应该出现最后显示为？的情况`.
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Derive missing closing event quantity when opening quantity is known | Review / Static trade timeline & K-line markers (`tradeRecords.js`) | recorded | none | User 反馈：开仓已填数量时，清仓事件不应显示 `?`，应按初始量 - 部分平仓量推导剩余数量 |

## Visual Reference

| File | Surface | Observed issue |
| --- | --- | --- |
| [`./screenshots/2026-07-22-trade-close-quantity-question-mark.png`](./screenshots/2026-07-22-trade-close-quantity-question-mark.png) | Trade cards timeline | `SELL ? @ 0.15` and `SELL ? @ 5.5` display `?` for `sell_close` events despite known initial buy quantity (150 and 70) |

## Scope Lock (user-confirmed 2026-07-22)

| Decision | Lock |
| --- | --- |
| Friction | When closing events (`sell_close`) have `quantity: null` in raw data, UI displays `?` on trade cards (e.g. `SELL ? @ 0.15`) and loses quantity in markers |
| Inferred quantity rule | When a leg has a known opening quantity (e.g. `BUY 150` or `BUY 70`), calculate remaining position for closing events: `derived_qty = opening_qty - sum(prior_partial_close_qty)` |
| Card & Marker parity | Use derived quantity for timeline display (`SELL 150 @ 0.15`, `SELL 12 @ 5.5`) and marker quantity suffix (`SELL*150`, `SELL*12`) |
| Edge case handling | If opening quantity is missing or invalid, fallback to displaying `?` (or omit marker quantity suffix) |

## OPT-001 Derive Missing Closing Event Quantity

- Source evidence:
  - User feedback screenshot: [`./screenshots/2026-07-22-trade-close-quantity-question-mark.png`](./screenshots/2026-07-22-trade-close-quantity-question-mark.png)
  - User instruction (2026-07-22): 「这种开头交易就显示了总数，结尾的时候自然而然就可以计算出总和，不应该出现最后显示为？的情况」
- Current friction:
  - `groupTimelineEvents` passes raw `event.quantity` (null), rendering `SELL ? @ 0.15`
  - Prevents trade cards and K-line markers from displaying complete trade size when raw chat log omitted explicit closing contract count
- Desired outcome:
  - Pure helper derives `quantity` for `sell_close` when opening position `quantity` is known
  - Eliminates `?` on closing events for trades with known opening sizes across Review and Static surfaces
- Lifecycle status: recorded
