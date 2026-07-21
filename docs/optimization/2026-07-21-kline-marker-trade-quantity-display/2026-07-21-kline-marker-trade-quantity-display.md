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

## Scope Lock (draft)

| Decision | Lock |
| --- | --- |
| Friction | Current marker aggregation displays event count `×N` (e.g., `vordinkkk SELL ×2`) when multiple events land on the same bar |
| Desired display | Display trade quantity (e.g., contract/share quantity) instead of event count `×N` |
| Quantity aggregation | Sum event `quantity` fields for same-bar aggregated events when quantity is available |
| Fallback behavior | If quantity is unknown (`null`), omit quantity suffix or use fallback count |

## OPT-001 K-line Marker Labels Should Display Trade Quantity

- Source evidence:
  - User feedback screenshot: [`./screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png)
  - User instruction (2026-07-21): 「这里可以把交易的数量加上，而不是写一个*2」
- Current friction:
  - `buildTradeRecordAnnotations` appends `×${count}` when multiple events group on a bar (e.g. `vordinkkk SELL ×2`)
  - Does not reflect actual contract/share quantities traded (e.g. 12 + 12 = 24 contracts)
- Desired outcome:
  - Replace `×N` count suffix with actual trade quantity (e.g. `24` / `24张` / sum of quantities)
  - Keep marker labels clean and readable across Review and Static pages
- Lifecycle status: recorded
