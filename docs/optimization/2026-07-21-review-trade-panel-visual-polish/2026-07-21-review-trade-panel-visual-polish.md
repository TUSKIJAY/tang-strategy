# Optimization Batch · 2026-07-21 Review Trade Panel Visual Polish

> Record-only intake. This file does not authorize implementation, plan promotion, commit, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-21-review-trade-panel-visual-polish/2026-07-21-review-trade-panel-visual-polish.md`
> Evidence images live in `./screenshots/`. Interactive HTML mockups live in `./mockups/`.
>
> A finalized record is eligible for an `opt-record` durable checkpoint only under separate local Git authority and the exact scope/safety rules in `docs/operating-modes.md` §9. Draft status or this record alone grants no checkpoint authority.

- Checkpoint authority: none
- Checkpoint authority mode: none
- Checkpoint authority kinds: none

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Polish shared trade tools + group cards (Review / Static / Admin) | Shared trade filter/export/list chrome | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md) revision `v1-proposal-2026-07-21` | Mock accepted; still no implementation authority |

## Relationship To Prior Work

- Completed filter fusion + progressive date nav: [`2026-07-20-review-date-nav-and-trade-filter-fusion`](../2026-07-20-review-date-nav-and-trade-filter-fusion/2026-07-20-review-date-nav-and-trade-filter-fusion.md) → completed plan `2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan`. Locked **B chip**, direction colors, YaHei, no ticker/date mirror; shipped density later under Data progressive + trade-card density plan.
- Completed type/density pass: [`2026-07-21-review-trade-panel-type-scale`](../2026-07-21-review-trade-panel-type-scale/2026-07-21-review-trade-panel-type-scale.md) → completed plan `2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan`. Reduced `.dr-sidebar` card type to 12/11px; **did not** redesign tool chrome IA.
- User acceptance 2026-07-21 after density ship: the Eligibility / trader chip / Download / cards block is **still ugly** as a bolted form module. This batch is visual/IA polish of that shared chrome.

## Visual Reference

### Live acceptance evidence (current friction)

1. Review left trade tools + two 沃德哥 cards (QQQ): [`./screenshots/2026-07-21-review-trade-panel-current.png`](./screenshots/2026-07-21-review-trade-panel-current.png) · SHA-256 `ce00fef17e4fd58a73b5c8de7415041bdc95aa651c6865e78f41347635db3765` · 18,733 bytes

What the evidence shows:

- Hint line, then form-like **Eligibility** native select, strong-outline **沃德哥** chip, full-width **Download JSON + 3 CSV**, then group cards with VERIFIED badge and **Show legs/events**.
- English chrome next to Chinese product UI; boxed filter panel still reads as a second language under Strategy/date.

### Design mockup (proposal surface)

| File | Role | SHA-256 |
| --- | --- | --- |
| [`./mockups/trade-panel-v2.html`](./mockups/trade-panel-v2.html) | Side-by-side current feel vs proposed v2 + English chrome lock; interactive Eligibility/traders/legs; not live app | `ddea8609c48c9f19c1d27f1f0d51ae5c1b5fa80ab3a0bcc5e67408c943d6e9bc` |

Open the mockup in a browser. Paths are relative to this record.

## Scope Lock (user-confirmed 2026-07-21 foldback)

| Decision | Lock |
| --- | --- |
| Mock visual direction | **Accepted** — terminal tool strip + clearer cards is the target look |
| Product chrome language | **Keep original English** for controls that are English in live UI — do not Chinese-translate Eligibility / Display / Reported / Calculated / Download / Show legs/events / Verified |
| Eligibility product labels | **Display** / **Reported** / **Calculated** (segment short form of live `Display` / `Reported stats` / `Calculated stats`) |
| Eligibility enum values | Unchanged machine values: `display` / `reported` / `calculated` |
| Eligibility row label | **Eligibility** |
| Label mapping | Display → `display_eligible`; Reported → `reported_stats_eligible`; Calculated → `calculated_stats_eligible` |
| Export control | Corner **Download** (icon + short English) — **no** full-width `Download JSON + 3 CSV`, **no** hover/title with that long string |
| Export payload | Unchanged (still JSON + 3 CSV files under the hood); presentation only |
| Drilldown copy | **Show legs/events** / **Hide legs/events** (English, as live) |
| Trader filter scale | **≤6** visible traders → inline pills; **≥7** → summary + Edit drawer. Same B-chip contract |
| Surface scope | **Review + Static + Admin aligned** in one batch (shared `TraderFilters` / export / list chrome) |
| Keep prior locks | B chip multi-select; CALL/PUT direction color only; name text never red; day-available traders only; no redundant ticker/date mirror |
| Chinese allowed | Existing Chinese product strings only (e.g. hint `提示 · 7 进场…`, trader display names like 沃德哥) — not a wholesale chrome translation |
| Out of scope unless reopened | Backend/DB schema; export file formats/contents; progressive date rules; new statistics semantics |

### Rejected label candidates

| Candidate | Why not |
| --- | --- |
| 显示 / 已报 / 计算 | User: not intuitive; later superseded by keep-English rule |
| 可见点位 / 手填收益 / 系统核算 | User foldback: mock had translated English chrome; keep original English |
| Full-width / hover `Download JSON + 3 CSV` | User: remove long copy; short **Download** only |

## OPT-001 Polish Shared Trade Tools + Cards

- Source evidence: live screenshot above; user 2026-07-21 mock request + foldback locks above.
- Current friction:
  - Filter block is still a bordered form card under the terminal context column.
  - Loud full-width download CTA and English labels fight the terminal density language.
  - Cards pack name / direction / meta / badge / drill without clear visual hierarchy (type density alone was not enough).
  - English chrome mixed with form-card layout still feels bolted on (translation is not the fix).
- Desired outcome:
  - Same data and filter authority, calmer terminal-native chrome on **Review, Static, and Admin**.
  - Eligibility as compact segmented control with **English** Display/Reported/Calculated; export as corner **Download**; cards with direction rail, name+dir pill, meta line, status dot, collapsible legs; keep live English microcopy.
  - Trader chips keep existing scale behavior (inline vs drawer).
- Boundary that must not change (unless a later plan explicitly expands):
  - Tracked SQLite / content / Pages publisher / provider paths
  - B chip selection model and eligibility enum values (`display` / `reported` / `calculated`)
  - Export payload contents (JSON + 3 CSV), only presentation of the control
  - Direction color semantics from completed fusion plan
- Lifecycle status: promoted-to-proposed
- Mock proposal: [`./mockups/trade-panel-v2.html`](./mockups/trade-panel-v2.html)
- Proposed plan: [`docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md`](../../exec-plans/proposed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md) revision `v1-proposal-2026-07-21`; next gate `design-review`

## Record Mode Session

- Mode entered: 2026-07-21 by user instruction `开启opt记录模式`
- This batch opened: 2026-07-21 on user paste of Review trade-panel screenshot + mock request
- Foldback locked: 2026-07-21 (mock accepted; English chrome kept; Download shortened; scale/surface)
- Promoted: 2026-07-21 by user instruction `生成prop plan` → Proposed plan only; no activation, implementation, Git, data, or remote authority
- Next: independent design review of exact revision `v1-proposal-2026-07-21`
