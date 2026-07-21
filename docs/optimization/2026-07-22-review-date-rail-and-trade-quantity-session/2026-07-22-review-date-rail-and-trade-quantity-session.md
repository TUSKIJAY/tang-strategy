# Optimization Batch · 2026-07-22 Review Date Rail And Trade Quantity Session

> Record-only intake. This file does not authorize implementation, plan promotion, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/2026-07-22-review-date-rail-and-trade-quantity-session.md`
> Evidence images live in `./screenshots/`.
>
> **Session-consolidated batch.** Combines 2026-07-21/22 Review date rail chip chronological order and trade marker/timeline quantity friction.
> Mode entered: 2026-07-22 by user instruction `把这个合并进你刚创建的opt里面`.
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Progressive date chips must sort ascending (正序) | Shared `DateRail` progressive mode (Review / Data / Static) | recorded | none | User 验收：最近 + 按月 均为倒序，要求正序 |
| OPT-002 | K-line marker labels should display trade quantity instead of count `×N` | Review / Static K-line markers (`tradeRecords.js` + `kline-engine`) | recorded | none | User 反馈：K 线标注不写 `×2`，多笔写总和 `SELL*24`，单笔写 `BUY*70` |
| OPT-003 | Derive missing closing event quantity when opening quantity is known | Review / Static trade timeline & K-line markers (`tradeRecords.js`) | recorded | none | User 反馈：开仓已知数量时，清仓不应显示 `?`，应推导剩余平仓量（150 / 12） |

## Visual Reference

| File | Area | Observed issue |
| --- | --- | --- |
| [`./screenshots/2026-07-21-date-rail-recent-desc.png`](./screenshots/2026-07-21-date-rail-recent-desc.png) | DateRail 最近 | `07-17` → `07-16` → … → `07-01` (newest first) |
| [`./screenshots/2026-07-21-date-rail-month-desc.png`](./screenshots/2026-07-21-date-rail-month-desc.png) | DateRail 按月 | `17` → `16` → … → `01` (newest first) |
| [`./screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png) | K-line markers | `vordinkkk SELL ×2` displays event count `×2` rather than contract/share quantity |
| [`./screenshots/2026-07-22-trade-close-quantity-question-mark.png`](./screenshots/2026-07-22-trade-close-quantity-question-mark.png) | Trade cards timeline | `SELL ? @ 0.15` and `SELL ? @ 5.5` display `?` for `sell_close` events despite known initial buy quantity |

## Supersedes (this session)

| Previous split batch | Status |
| --- | --- |
| [`../2026-07-21-date-rail-chip-chronological-order/`](../2026-07-21-date-rail-chip-chronological-order/2026-07-21-date-rail-chip-chronological-order.md) | superseded → OPT-001 |
| [`../2026-07-21-kline-marker-trade-quantity-display/`](../2026-07-21-kline-marker-trade-quantity-display/2026-07-21-kline-marker-trade-quantity-display.md) | superseded → OPT-002 |
| [`../2026-07-22-trade-close-quantity-derivation/`](../2026-07-22-trade-close-quantity-derivation/2026-07-22-trade-close-quantity-derivation.md) | superseded → OPT-003 |

---

## Scope Lock (user-confirmed 2026-07-22)

| Topic | Lock |
| --- | --- |
| **OPT-001 DateRail order** | **正序** = chronological ascending (earlier date on left, later on right) in both **最近** and **按月** modes across Review / Data / Static progressive rails |
| **OPT-002 Marker quantity** | Multi-event same-bar aggregation shows sum of quantity formatted as `${displayName} ${actionSide}*${totalQuantity}` (e.g. `vordinkkk SELL*24`); single events include quantity if present (e.g. `vordinkkk BUY*70`); missing quantity omits suffix (e.g. `vordinkkk SELL`) |
| **OPT-003 Closing quantity derivation** | When a leg has a known opening quantity (`BUY 150`, `BUY 70`), closing events with missing raw quantity (`quantity: null`) derive remaining quantity: `derived_qty = opening_qty - sum(prior_partial_close_qty)`. Renders as `SELL 150 @ 0.15` and `SELL 12 @ 5.5` (eliminating `?`) and feeds marker quantity `SELL*150` / `SELL*12` |

---

## OPT-001 Progressive Date Chips Must Sort Ascending (正序)

- Source evidence: [`screenshots/2026-07-21-date-rail-recent-desc.png`](./screenshots/2026-07-21-date-rail-recent-desc.png), [`screenshots/2026-07-21-date-rail-month-desc.png`](./screenshots/2026-07-21-date-rail-month-desc.png)
- Current friction: Progressive date chips render newest-first (descending) in both 最近 and 按月 modes.
- Desired outcome: Chip rows sort ascending by `trade_date` (left → right) in both modes across Review / Data / Static.
- Lifecycle status: recorded

## OPT-002 K-line Marker Labels Should Display Trade Quantity

- Source evidence: [`screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png)
- Current friction: `buildTradeRecordAnnotations` appends `×${count}` when multiple events group on a bar (e.g. `vordinkkk SELL ×2`), and single events omit quantity.
- Desired outcome: Replace event count `×N` with actual trade quantity suffix `*QTY` (`vordinkkk SELL*24`, `vordinkkk BUY*70`); omit suffix if quantity is missing (`vordinkkk SELL`).
- Lifecycle status: recorded

## OPT-003 Derive Missing Closing Event Quantity

- Source evidence: [`screenshots/2026-07-22-trade-close-quantity-question-mark.png`](./screenshots/2026-07-22-trade-close-quantity-question-mark.png)
- Current friction: Closing events with `quantity: null` render `SELL ? @ 0.15` despite known initial buy quantity.
- Desired outcome: Derive remaining position quantity for `sell_close` events when opening quantity is known (`derived_qty = opening_qty - sum(prior_partial_qty)`), eliminating `?` on timeline rows and markers.
- Lifecycle status: recorded
