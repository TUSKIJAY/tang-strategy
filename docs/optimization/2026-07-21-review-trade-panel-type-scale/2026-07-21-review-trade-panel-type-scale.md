# Optimization Batch · 2026-07-21 Review Trade Panel Type Scale

> Record-only intake. This file does not authorize implementation, plan promotion, commit, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-21-review-trade-panel-type-scale/2026-07-21-review-trade-panel-type-scale.md`
> Put evidence images in the sibling `screenshots/` folder and link them as `./screenshots/<name>.png`.
>
> A finalized record is eligible for an `opt-record` durable checkpoint only under separate local Git authority and the exact scope/safety rules in `docs/operating-modes.md` §9. Draft status or this record alone grants no checkpoint authority.

- Checkpoint authority: none
- Checkpoint authority mode: none
- Checkpoint authority kinds: none

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Reduce **现实交易者点位** list/card type scale to match Review density | Review left column / `TraderTradeList` group cards | promoted-to-proposed | [plan](../../exec-plans/proposed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md) revision `v2-review-foldback-2026-07-21` | User clarified 2026-07-21: 是现实交易者点位这部分，不是整块 filter/export; `review-002: revise/high` keeps scoped CSS but requests lighter acceptance |

## Relationship To Prior Work

- Completed plan `2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan` set CALL/PUT direction colors and B-chip visibility on the Review trade surface. Residual acceptance now targets **type scale of the real trader point cards**, not a second pass on date rail or chip filter semantics.
- Prior batch [`2026-07-20-review-date-nav-and-trade-filter-fusion`](../2026-07-20-review-date-nav-and-trade-filter-fusion/2026-07-20-review-date-nav-and-trade-filter-fusion.md) OPT-004 (direction colors) and OPT-002 (panel fusion) are related context; this intake is specifically **typography/density** of the point list.
- Sibling same-day intake [`2026-07-21-data-page-progressive-date-nav`](../2026-07-21-data-page-progressive-date-nav/2026-07-21-data-page-progressive-date-nav.md) is separate.

## Clarification Log

| When | Correction |
| --- | --- |
| First write | Intake initially described Download JSON + full trade-panel chrome as oversized. |
| User correction 2026-07-21 | **「是现实交易者点位这部分的字体过大」** — scope is the real trader **points** block (group cards: name + CALL/PUT + meta), not Eligibility / B chips / Download as the primary ask. |

## Visual Reference

### Live acceptance evidence (current friction)

1. Tang point card oversized title/meta: [`./screenshots/2026-07-21-review-trade-panel-tang-large-type.png`](./screenshots/2026-07-21-review-trade-panel-tang-large-type.png) · SHA-256 `5f4d9c0b7d48721a3401f2351f4d3f3924f1e13efd83dbf91fb618fdfb918f53`
2. 沃德哥 multi-point cards same scale: [`./screenshots/2026-07-21-review-trade-panel-vordin-large-type.png`](./screenshots/2026-07-21-review-trade-panel-vordin-large-type.png) · SHA-256 `de1a6e3df677ce7fe74c143b3a9b01ce0e0993761fb816be769d0d23c198f920`

What the evidence shows (after user clarification):

- Target rows are the **trade group / point cards**: e.g. `Tang CALL`, `沃德哥 PUT`, `沃德哥 CALL`, with meta `SPY|QQQ 2026-07-17 · result unknown` and `Show legs/events`.
- These titles read much larger than surrounding Review left-column chrome (date chips ~10–11px, status lines ~11–12px) and feel like a second, coarser UI embedded in the list.
- CALL green / PUT red direction coloring is fine and is **not** the complaint.
- Crops also show Eligibility / B chip / Download above the list; those may share large button inheritance, but the **recorded user intent** is the **现实交易者点位** list itself—do not expand OPT-001 to export/filter chrome without a new user ask.

## Technical Notes (read-only, not a fix)

Likely component surface:

| Piece | Role |
| --- | --- |
| `TraderTradeList.jsx` | Renders `.trade-group-card` / `.trade-trader-name` / direction word |
| `.trade-group-summary` | Card header is a `<button>` → inherits global button type (~body 16px) + padding |
| `.trade-trader-name` | `font-weight: 700` only; **no compact `font-size`** |
| Global `button` | `font: inherit`, padding `11px 14px` — paper-scale, not terminal density |

Contrast: strategy signal cards (`.dr-signal-card` / `.dr-tang-*`) already use ~11–12px mono-ish density. Point cards should feel in that family, not page-button family.

## Scope Notes (intake, not locked plan)

| Topic | Current intake note |
| --- | --- |
| Desired outcome | 现实交易者点位 cards: title + direction + meta + drilldown toggle use Review compact type (~11–12px), no “heading-sized” trader names |
| In scope | Interactive Review point list (`TraderTradeList` / related shared card CSS); Static parity if same component |
| Explicitly out of OPT-001 unless reopened | Eligibility control, B chips, Download JSON export chrome, date rail, chart markers, shell nav, Data page |
| Keep | CALL/PUT colors; card selection/active behavior; legs/events content; export/filter contracts |

## OPT-001 Reduce 现实交易者点位 Card Type Scale

- Source evidence: two live crops above; initial ask “字体太大…和页面其他地方统一”; **clarified** to 现实交易者点位 only.
- Current friction: Point card titles and body type are too large relative to the rest of the Review left column, so the list looks abrupt/out of scale.
- Desired outcome: Point cards match the density of other Review list/control text; still readable, still show full trader name + direction + day meta, just not oversized.
- Boundary that must not change (unless a later plan expands):
  - Trade payload / export schema
  - Trader visibility / eligibility semantics
  - Direction color tokens
  - Tracked DB / content / Pages / provider paths
- Lifecycle status: recorded
- Open decisions for later promotion (not decided here):
  1. CSS only under `.dr-sidebar .trade-group-*` vs shared component defaults (Admin inspection list).
  2. Exact px targets vs “match `.dr-signal-card` / date-rail density.”
  3. Whether `Show legs/events` and drilldown body need the same pass (likely yes as part of the card).

## Record Mode Session

- Mode: optimization record (user-enabled 2026-07-21)
- Authority: record-only; no implementation from this file
- Scope correction applied same day after user clarification
