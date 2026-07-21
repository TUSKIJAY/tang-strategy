# Optimization Batch · 2026-07-21 Date Rail Chip Chronological Order

> Record-only intake. This file does not authorize implementation, plan promotion, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-21-date-rail-chip-chronological-order/2026-07-21-date-rail-chip-chronological-order.md`
> Evidence images live in `./screenshots/`.
>
> Mode entered: 2026-07-21 by user instruction `进入opt记录模式`.
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Progressive date chips must sort ascending (正序) | Shared `DateRail` progressive mode (Review / Data / Static) | recorded | none | User 验收：最近 + 按月 均为倒序，要求正序 |

## Visual Reference

| File | Mode | Observed order (L→R) |
| --- | --- | --- |
| [`./screenshots/2026-07-21-date-rail-recent-desc.png`](./screenshots/2026-07-21-date-rail-recent-desc.png) | 最近 | `07-17` → `07-16` → … → `07-01` (newest first) |
| [`./screenshots/2026-07-21-date-rail-month-desc.png`](./screenshots/2026-07-21-date-rail-month-desc.png) | 按月 · 2026-07 | `17` → `16` → … → `01` (newest first) |

## Scope Lock (user-confirmed 2026-07-21)

| Decision | Lock |
| --- | --- |
| Friction | Progressive date chips render **descending** (newest on the left) in both **最近** and **按月** |
| Desired order | **正序** = chronological ascending (earlier date on the left, later on the right) |
| Modes in scope | **最近** and **按月** both |
| Surface parity | Shared progressive `DateRail` — keep **Review / Data / Static** aligned (same component projection) |
| Window semantics | 最近 still means “most recent N trading days”; only the **display sort** of that window flips to ascending |
| Out of scope unless reopened | Ticker tabs; progressive vs exhaustive mode choice; recent N limit; month-bar identity rules; data/API inventory order beyond chip presentation |

## Relationship To Prior Work

- Progressive 最近 / 按月 IA was locked and shipped under [`2026-07-20-review-date-nav-and-trade-filter-fusion`](../2026-07-20-review-date-nav-and-trade-filter-fusion/2026-07-20-review-date-nav-and-trade-filter-fusion.md) OPT-001 and Data parity plans. Those plans fixed density, month identity, and chip labels (`MM-DD` vs day-only) but did **not** lock left-to-right sort as ascending.
- Current projection source: `frontend/src/features/review/reviewWorkspace.js` — `datesForTicker` ends with `.sort().reverse()` (newest-first), then `projectProgressiveDateRail` slices that order for 最近 / 按月 chips.

## OPT-001 Progressive Date Chips Must Sort Ascending (正序)

- Source evidence:
  - Live acceptance screenshots (QQQ progressive rail): [`./screenshots/2026-07-21-date-rail-recent-desc.png`](./screenshots/2026-07-21-date-rail-recent-desc.png), [`./screenshots/2026-07-21-date-rail-month-desc.png`](./screenshots/2026-07-21-date-rail-month-desc.png)
  - User instruction (2026-07-21): 「日期应该按照正序排列」with both 最近 and 按月 captures
- Current friction:
  - **最近**: chips read right-to-left in calendar time (`07-17` first, then older days)
  - **按月**: within the browsed month, day chips also newest-first (`17` … `01`)
  - Feels like reverse reading order for a calendar-like day strip
- Desired outcome:
  - Chip rows sort **ascending by `trade_date`** left → right in both modes
  - Example 最近 window of newest 12: still those 12 days, but L→R ≈ `07-01` … `07-17` (not `07-17` … `07-01`)
  - Example 按月 2026-07: L→R ≈ `01` `02` … `17`
  - Default selection / “latest day” behavior unchanged unless later specified; only visual order changes
  - Review / Data / Static progressive rails stay consistent
- Boundary that must not change:
  - Progressive modes (最近 / 按月), month bar only in 按月, chip label formats, recent N window size policy, ticker parent context, exhaustive DateRail consumers not in progressive mode (unless they share the same sort helper and parity is intentional)
- Lifecycle status: recorded
