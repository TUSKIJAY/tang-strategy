# Optimization Batch · 2026-07-21 Data Page Progressive Date Navigation

> Record-only intake. This file does not authorize implementation, plan promotion, commit, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-21-data-page-progressive-date-nav/2026-07-21-data-page-progressive-date-nav.md`
> Put evidence images in the sibling `screenshots/` folder and link them as `./screenshots/<name>.png`.
>
> A finalized record is eligible for an `opt-record` durable checkpoint only under separate local Git authority and the exact scope/safety rules in `docs/operating-modes.md` §9. Draft status or this record alone grants no checkpoint authority.
- Checkpoint authority: none
- Checkpoint authority mode: none
- Checkpoint authority kinds: none

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Align Data page Market days rail with Review progressive date navigation | Data workspace / `DashboardPage` date rail | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md) revision `v4-review-foldback-2026-07-21` | Implemented; `implementation-review-001: accept/high`; verified `74334935a09f60c23748cdf0ecce5e52c1d643be` |

## Relationship To Prior Work

- Completed Review-only progressive date navigation: [`2026-07-20-review-date-nav-and-trade-filter-fusion`](../2026-07-20-review-date-nav-and-trade-filter-fusion/2026-07-20-review-date-nav-and-trade-filter-fusion.md) → completed plan `2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan`. That plan **explicitly excluded** Data/Admin/Static progressive DateRail: only `ReviewPage` passes `dateNavigation="progressive"`; shared default remains `exhaustive`.
- Earlier same-theme draft [`2026-07-20-data-coverage-presentation`](../2026-07-20-data-coverage-presentation/2026-07-20-data-coverage-presentation.md) was **superseded** when intake shifted to trader-workspace/nav. This batch is a **new 2026-07-21 user acceptance reopen** of Data progressive date presentation after Review progressive is live—not a resurrection of the superseded draft’s research scope.
- Live technical fact (read-only): `DashboardPage` already mounts shared `ReviewContextPanel` without `dateNavigation`, so it inherits exhaustive month-grouped chips. Review passes `dateNavigation="progressive"`.

## Visual Reference

### Live acceptance evidence (current friction)

1. Data page Market days exhaustive multi-month rail (SPY selected, all 2026-07/06/05 chips visible): [`./screenshots/2026-07-21-data-market-days-exhaustive-rail.png`](./screenshots/2026-07-21-data-market-days-exhaustive-rail.png) · SHA-256 `da3b492b6eef7239e7881508d3f02903bafb52373e55b9d4af162548292edba4`

What the evidence shows:

- Data panel title remains `Market days` with QQQ/SPY ticker tabs and a full exhaustive chip grid (month labels + every `MM-DD`).
- Selected day is outlined (e.g. `07-17`); inventory already spans multiple months and will keep growing.
- User expectation after using Review: Data should present dates with the **same progressive 最近 / 按月** interaction pattern, not a second exhaustive language.

## Scope Notes (intake, not locked plan)

| Topic | Current intake note |
| --- | --- |
| Desired pattern | Match Review progressive DateRail (`最近` / `按月`, same density/chip rules) |
| Likely surface | Data / `DashboardPage` Market days panel only (unless later OPT expands) |
| Reuse | Prefer existing `dateNavigation="progressive"` opt-in on shared `DateRail` / `ReviewContextPanel` |
| Out of scope unless reopened | Admin inspection DateRail, Static Review, backend/DB/export, new calendar-grid primary UI |
| Prior plan boundary | Review plan’s “Data unchanged” was intentional for that v1; this intake asks to expand progressive to Data |

No scheme lock beyond “same as Review progressive” until the user confirms further (e.g. whether day click still opens Review for that day, month thresholds, recent limit 12).

## OPT-001 Align Data Market Days With Review Progressive Navigation

- Source evidence: live local acceptance screenshot above; user question 2026-07-21: “data页面怎么没做成和review一样的日期显示”.
- Current friction: After Review progressive ship, Data still shows exhaustive multi-month chip rails. Day inventory growth makes the Data Market days panel hard to scan and inconsistent with Review IA.
- Desired outcome: Data page date selection uses the same progressive presentation as interactive Review (最近 / 按月 browse over real workspace inventory), so users do not learn two date UIs.
- Boundary that must not change (unless a later plan explicitly expands):
  - Tracked SQLite DB / seed / content contracts
  - Pages publisher, daily runbook, provider/broker paths
  - Admin/Static DateRail behavior until separately recorded
  - No silent default flip that changes every `DateRail` caller without inventory
- Lifecycle status: recorded
- Open decisions for later promotion (not decided here):
  1. Whether Data only opts into progressive (minimal) or also renames/tightens Market days chrome copy.
  2. Whether selecting a day on Data keeps current “open Review for that day” behavior.
  3. Whether Admin should stay exhaustive as a coverage/debug surface.

## Record Mode Session

- Mode entered: 2026-07-21 by user instruction `进入opt记录模式`
- Authority: record-only; no implementation, no proposed plan, no Git stage/commit/push unless separately granted
- Ready for additional OPT items in this batch or sibling batches as user continues feedback
