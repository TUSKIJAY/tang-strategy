# Optimization Batch · 2026-07-22 Review Date Rail And Trade Quantity Session

> Record-only intake until promoted. This file does not by itself authorize implementation, activation, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/2026-07-22-review-date-rail-and-trade-quantity-session.md`
> Evidence images live in `./screenshots/`. Design mock: [`./mock.html`](./mock.html).
>
> **Session-consolidated batch.** Combines 2026-07-21/22 Review date rail chip chronological order and trade marker/timeline quantity friction.
> Mode entered: 2026-07-22 by user instruction `把这个合并进你刚创建的opt里面`.
> Promoted: 2026-07-22 by user instruction `升级成prop plan` → proposed plan below.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Progressive date chips must sort ascending (正序) | Shared progressive `DateRail` (Review / Data / Static) | completed | [completed plan](../../exec-plans/completed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md) | User 验收：最近 + 按月 均为倒序，要求正序 |
| OPT-002 | K-line marker labels should display trade quantity instead of count `×N` | Review / Static K-line markers (`tradeRecords.js` → `kline-engine`) | completed | [completed plan](../../exec-plans/completed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md) | User：不写 `×2`；同 bar 写数量总和 `SELL*24`；单笔 `BUY*70` |
| OPT-003 | Derive missing closing event quantity when opening quantity is known | Review / Static timeline + markers (`tradeRecords.js` / list render) | completed | [completed plan](../../exec-plans/completed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md) | User：开仓已知时清仓不写 `?`，推导剩余量（fixture `150` / `12`） |

## Scope Lock (user-confirmed 2026-07-22)

| Topic | Lock |
| --- | --- |
| **OPT-001 DateRail order** | **正序** = chronological ascending (earlier date on the left, later on the right) in both **最近** and **按月** modes across Review / Data / Static progressive rails. |
| **OPT-001 recent membership** | **最近** still means the newest `N` inventory dates (`PROGRESSIVE_RECENT_LIMIT`, currently 12). Membership is unchanged; only the chip **render order** flips to ascending within that set (selected latest day moves from first chip to last chip). |
| **OPT-001 month inventory** | **按月** chip order is ascending within the browsed month. Month switcher (`‹ YYYY-MM ›`), newest-first month inventory, ticker tabs, footer meta counts, and selection authority stay unchanged. |
| **OPT-002 Marker quantity text** | Same-bar multi-event aggregation shows sum of quantities as `${displayName} ${actionSide}*${totalQuantity}` (e.g. `vordinkkk SELL*24`). Single events with known quantity append the same `*QTY` form (e.g. `vordinkkk BUY*70`). If quantity is still unknown after OPT-003 derivation, **omit the suffix** (e.g. `vordinkkk SELL`). Replace event-count `×N` entirely — do not show both. |
| **OPT-002 label surface** | Apply the quantity suffix to user-visible marker text fields that currently carry the side label (`marker_label`, and `title` if it shares the same vocabulary). Do **not** reintroduce CALL/PUT text, raw `trader_id` when `display_name` exists, or raw schema actions (`buy_open` / `sell_partial` / …). |
| **OPT-002 shape/color contract (unchanged)** | Marker **shape and color remain direction-owned** from the completed trade-points plan: CALL → `triangle_up` / call color; PUT → `triangle_down` / put color; anchors stay direction-based. Quantity work is **label text only** — not action-side shape (BUY bottom / SELL top is not the product contract). |
| **OPT-003 Closing quantity derivation** | Per **leg**, when opening quantity is known and a `sell_close` (or equivalent close) event has `quantity: null`, derive remaining size: `derived_qty = opening_qty − Σ(prior partial close qty on that leg)`. Example fixture (QQQ `2026-07-17` vordin): PUT `150 − 0 = 150` → `SELL 150 @ 0.15` / marker `SELL*150`; CALL `70 − (12+12+22+12) = 12` → `SELL 12 @ 5.5` / marker `SELL*12`. |
| **OPT-003 fallback** | If opening quantity is unknown, or prior partials sum to more than opening, keep `?` (timeline) / omit marker quantity suffix. Do not invent quantity. |
| **OPT-003 render-only** | Derivation is a **presentation/read-path** concern. Do **not** rewrite day JSON, content trades files, DB rows, or provenance fields (`quantity: "unknown"` may remain on source). |
| **OPT-003 UI chrome** | No product requirement for a visible `derived` badge/pill on timeline rows. If a design mock shows such a pill, it is pedagogical only unless a later user lock adds it. |
| **Surfaces** | Review interactive and Static Reviews stay aligned for all three OPTs. Shared progressive date projection and shared trade-record pure helpers are preferred over page-local forks. |
| **Out of scope unless reopened** | Schema/API changes; provider/broker; tracked DB rebuild rules; Pages publish; Admin point editor UX; month-nav inventory reordering; selection/fitRange/highlight contracts; changing marker shape/color ownership. |

## Design mock (proposal surface)

| File | Role | Notes |
| --- | --- | --- |
| [`./mock.html`](./mock.html) | Self-contained Current vs Proposed for OPT-001…003 | Visual aid for the proposed plan. Open in a browser from this folder. Mock data is illustrative (anchors QQQ `2026-07-17` vordin cases); not live app output. Marker shape/legend corrected to direction-owned (commit `f408871`). |

## Visual Reference (live friction)

| File | Area | Observed issue |
| --- | --- | --- |
| [`./screenshots/2026-07-21-date-rail-recent-desc.png`](./screenshots/2026-07-21-date-rail-recent-desc.png) | DateRail 最近 | `07-17` → `07-16` → … → `07-01` (newest first) |
| [`./screenshots/2026-07-21-date-rail-month-desc.png`](./screenshots/2026-07-21-date-rail-month-desc.png) | DateRail 按月 | `17` → `16` → … → `01` (newest first) |
| [`./screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png) | K-line markers | `vordinkkk SELL ×2` shows event count; singles omit quantity |
| [`./screenshots/2026-07-22-trade-close-quantity-question-mark.png`](./screenshots/2026-07-22-trade-close-quantity-question-mark.png) | Trade cards timeline | `SELL ? @ 0.15` / `SELL ? @ 5.5` despite known open qty |

## Code / data anchors (read-only evidence)

| Area | Anchor |
| --- | --- |
| Date order (newest-first) | `frontend/src/features/review/reviewWorkspace.js` — `datesForTicker` (`.sort().reverse()`), `projectProgressiveDateRail` |
| Marker `×N` | `frontend/src/features/review/tradeRecords.js` — `buildTradeRecordAnnotations` (`marker_label` + `×${count}`) |
| Timeline `?` | `frontend/src/features/review/TraderTradeList.jsx` — `row.quantity ?? '?'` |
| Fixture day | `content/trades/2026-07-17.json` — `tg_20260717_vordin_qqq_001` (PUT 150 / close null), `tg_20260717_vordin_qqq_002` (CALL 70 + partials + close null) |

## Supersedes (this session)

Split batches were consolidated into this folder then **removed** (git `514f8f4`) so they no longer exist on disk. Pointers below are historical only — do not expect relative links to resolve.

| Prior split batch (removed) | Folded into |
| --- | --- |
| `docs/optimization/2026-07-21-date-rail-chip-chronological-order/` | OPT-001 |
| `docs/optimization/2026-07-21-kline-marker-trade-quantity-display/` | OPT-002 |
| `docs/optimization/2026-07-22-trade-close-quantity-derivation/` | OPT-003 |

## Relationship To Prior Work

- Progressive DateRail (最近 / 按月) shipped via completed date-nav and Data progressive plans; OPT-001 is **chip order only** on that rail, not a reopen of progressive membership or month chrome.
- Marker vocabulary `display_name` + BUY/SELL (direction owns shape/color; same-bar `×N`) shipped via completed trade-points / marker-labels plan; OPT-002 replaces **count `×N` with quantity `*QTY`** on that label surface.
- Points-only cards and compact timeline already omit amount/profit; OPT-003 fills **missing close quantity on the read path** when open qty is known.

---

## OPT-001 Progressive Date Chips Must Sort Ascending (正序)

- Source evidence: [`screenshots/2026-07-21-date-rail-recent-desc.png`](./screenshots/2026-07-21-date-rail-recent-desc.png), [`screenshots/2026-07-21-date-rail-month-desc.png`](./screenshots/2026-07-21-date-rail-month-desc.png)
- Current friction: Progressive date chips render newest-first (descending) in both 最近 and 按月 modes (`datesForTicker` reverse order projected as-is).
- Desired outcome: Chip rows render ascending by `trade_date` (left → right) in both modes across Review / Data / Static. For 最近, keep the same newest-`N` set and only reverse display order.
- Boundary that must not change:
  - Recent-window membership rule and limit; month switcher / newest-first month list; ticker selection; which day is selected; footer meta semantics; non-progressive rails if any remain; no Data/Review workspace contract rewrite beyond chip order.
- Lifecycle status: completed → [completed plan](../../exec-plans/completed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md) revision `v2-review-foldback-2026-07-22`; `implementation-review-001: accept/high`; product commit `da12e1b03715be3de75fcafd8d47aa1a35554942`

## OPT-002 K-line Marker Labels Should Display Trade Quantity

- Source evidence: [`screenshots/2026-07-21-kline-marker-quantity-desc.png`](./screenshots/2026-07-21-kline-marker-quantity-desc.png)
- Current friction: `buildTradeRecordAnnotations` appends `×${count}` when multiple same-side events group on a bar (e.g. `vordinkkk SELL ×2`); single events omit quantity even when `event.quantity` is known.
- Desired outcome: Replace event count `×N` with quantity suffix `*QTY` (sum when aggregated; e.g. `vordinkkk SELL*24`, `vordinkkk BUY*70`). Omit suffix when quantity remains unknown. Consume OPT-003 derived qty when present so close markers can show `SELL*150` / `SELL*12`.
- Boundary that must not change:
  - Direction-owned marker shape/color/anchor; grouping key family (bar + trader + direction + action side); BUY/SELL vocabulary; display_name preference; fitRange / selection-band contracts; no CALL/PUT text regression on labels.
- Lifecycle status: completed → [completed plan](../../exec-plans/completed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md) revision `v2-review-foldback-2026-07-22`; `implementation-review-001: accept/high`; product commit `da12e1b03715be3de75fcafd8d47aa1a35554942`

## OPT-003 Derive Missing Closing Event Quantity

- Source evidence: [`screenshots/2026-07-22-trade-close-quantity-question-mark.png`](./screenshots/2026-07-22-trade-close-quantity-question-mark.png); day file `content/trades/2026-07-17.json` groups `tg_20260717_vordin_qqq_001` / `_002`
- Current friction: Closing events with `quantity: null` render `SELL ? @ …` on the expanded timeline even when the leg’s opening quantity and prior partials are known.
- Desired outcome: On the read path, derive remaining close quantity when open qty is known (`derived = open − Σ prior partials`); show concrete numbers on timeline rows and feed the same qty into OPT-002 marker labels. Keep `?` / omit-suffix when derivation is unsafe.
- Boundary that must not change:
  - Source day JSON / DB facts and provenance; schema validation allowing null quantity; Admin editing semantics; no automatic backfill write; no requirement for a product `derived` pill.
- Lifecycle status: completed → [completed plan](../../exec-plans/completed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md) revision `v2-review-foldback-2026-07-22`; `implementation-review-001: accept/high`; product commit `da12e1b03715be3de75fcafd8d47aa1a35554942`

## Record / promotion history

- 2026-07-22: User instruction `你来全权负责执行这个plan` → execution `user-instruction:2026-07-22-execute-date-rail-ascending-and-trade-quantity-plan`. OPT-001…003 implemented (product commit `da12e1b03715be3de75fcafd8d47aa1a35554942`); independent `implementation-review-001: accept/high`; plan migrated to `completed/`; all three OPTs `completed`; next gate `closed`. No push/PR/merge/Pages/provider/broker/remote.
- 2026-07-22: Independent acceptance; Scope Lock foldback; mock direction-legend fix `f408871`.
- 2026-07-22: User instruction `把prop plan迁移到active吧` → activation `user-instruction:2026-07-22-activate-date-rail-ascending-and-trade-quantity-plan`. Plan Active at `phase-0:not-started`; next gate `phase-0-start`. Does not start Phase 0 or authorize implementation/remote.
- 2026-07-22: Independent design `review-002: approve/high` on exact `v2-review-foldback-2026-07-22`. Next gate `activation-recording` (approve does not activate). No activation/implementation/remote authority.
- 2026-07-22: Folded `review-001: revise/high` into Proposed revision `v2-review-foldback-2026-07-22` (qty completeness + same-bar marker rules). Next gate independent `design-review` of exact v2. No activation/implementation/remote authority.
- 2026-07-22: User instruction `升级成prop plan` promoted OPT-001…003 to Proposed plan `docs/exec-plans/proposed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md` revision `v1-proposal-2026-07-22`. Next gate independent `design-review`. No activation, implementation, content/DB mutation, push, PR, merge, Pages, or remote authority.
