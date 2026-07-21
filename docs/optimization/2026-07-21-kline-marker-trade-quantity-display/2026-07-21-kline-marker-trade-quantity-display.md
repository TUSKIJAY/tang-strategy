# Optimization Batch · 2026-07-21 K-line Marker Trade Quantity Display

> Record-only intake. This file does not authorize implementation, plan promotion, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-21-kline-marker-trade-quantity-display/2026-07-21-kline-marker-trade-quantity-display.md`
> Evidence images live in `./screenshots/`.
>
> Mode entered: 2026-07-21 by user instruction `这里可以把交易的数量加上，而不是写一个*2`.
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | K-line marker labels should display trade quantity instead of count `×N` | Review / Static K-line markers (`tradeRecords.js` + `kline-engine`) | recorded | none | User 反馈：K 线标注不应写 `×2`，而应加交易数量 |

## Visual Reference

| File | Surface | Observed issue |
| --- | --- | --- |
| [`./screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png) | K-line trade markers | `vordinkkk SELL ×2` displays transaction count `×2` rather than contract/share quantity |

## Scope Lock (user-confirmed 2026-07-21)

| Decision | Lock |
| --- | --- |
| Friction | Current marker aggregation displays event count `×N` (e.g., `vordinkkk SELL ×2`) when multiple events land on the same bar |
| Multi-event quantity | Sum event `quantity` fields for same-bar aggregated events when quantity is available; format as `${displayName} ${actionSide}*${totalQuantity}` (e.g., `vordinkkk SELL*24`) |
| Single-event quantity | Also include quantity when present for single events (e.g., `vordinkkk BUY*70`) |
| Missing quantity fallback | If `quantity` is unknown (`null` / missing), omit the quantity suffix entirely (e.g., `vordinkkk SELL`) |

## OPT-001 K-line Marker Labels Should Display Trade Quantity

- Source evidence:
  - User feedback screenshot: [`./screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png)
  - User instruction (2026-07-21): 「这里可以把交易的数量加上，而不是写一个*2」
  - User Scope Lock (2026-07-21): 「1、显示为数量总和 vordinkkk SELL*24 2、同样带上数量 如 vordinkkk BUY*70 3、仅显示 vordinkkk SELL（省略数量后缀）」
- Current friction:
  - `buildTradeRecordAnnotations` appends `×${count}` when multiple events group on a bar (e.g. `vordinkkk SELL ×2`)
  - Single events do not display quantity (e.g. `vordinkkk BUY` without 70)
- Desired outcome:
  - Replace event count `×N` with actual trade quantity suffix `*QTY` (e.g. `vordinkkk SELL*24`, `vordinkkk BUY*70`)
  - If `quantity` is unknown (`null`), omit quantity suffix entirely (`vordinkkk SELL`)
  - Keep marker labels clean and readable across Review and Static pages
- Lifecycle status: recorded
