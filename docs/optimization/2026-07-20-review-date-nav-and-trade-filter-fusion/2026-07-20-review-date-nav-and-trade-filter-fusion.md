# Optimization Batch · 2026-07-20 Review Date Navigation And Trade-Filter Fusion

> Promoted by explicit user request to the review-only proposed plan [`Tang Strategy Review Date Navigation And Trader Filter Fusion`](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md). This file and the proposed plan do not authorize implementation.
>
> Place this file at:
> `docs/optimization/2026-07-20-review-date-nav-and-trade-filter-fusion/2026-07-20-review-date-nav-and-trade-filter-fusion.md`
> Evidence images live in `./screenshots/`. Interactive HTML mockups live in `./mockups/` and are the locked visual proposal for later plan promotion.
>
> A finalized record is eligible for an `opt-record` durable checkpoint only under separate local Git authority and the exact scope/safety rules in `docs/operating-modes.md` §9. This record alone grants no checkpoint, implementation, commit, push, data, or remote authority.

- Checkpoint authority: none
- Checkpoint authority mode: none
- Checkpoint authority kinds: none

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Replace Review exhaustive date-chip rail with progressive 最近 / 按月 navigation | Review left column / `DateRail` | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md) | User locked **scheme A**; only Review in v1 scope |
| OPT-002 | Fuse Review trade-filter/list chrome with upper Review context controls | Review left column / trade panel | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md) | Style consistency + date authority, not a light/dark color patch |
| OPT-003 | Keep outer shell trader-nav label readable under capability badge | App shell / `Layout` nav | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md) | Acceptance regression after terminal-ui plan: CJK label wraps vertically |
| OPT-004 | Direction-only color on trade points (CALL vs PUT); uniform name text | Review trade list + chart markers | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md) | Names never red; identity by full name text |
| OPT-005 | Replace ☑+Focus with **B · Chip multi-select** trader filter | Review trade filter | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md) | **User locked 2026-07-20**; scale drawer+search when many |

## Relationship To Prior Work

- Prior completed batch [`2026-07-20-trader-workspace-nav-and-registry`](../2026-07-20-trader-workspace-nav-and-registry/2026-07-20-trader-workspace-nav-and-registry.md) delivered terminal-first tokens, peer trader nav (no orange CTA), add-trader, and a first pass of trade-panel token migration under completed plan `2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan`.
- User acceptance on 2026-07-20 showed residual friction that plan did **not** close:
  1. Date rail is still exhaustive flat chips (`MM-DD` for every historical day) — unreadable as inventory grows.
  2. Trade Eligibility / Focus / Download / cards still read as a bolted-on form module under Strategy (and the current Ext K / Rescan / Backtest row), and still re-mirror ticker/date.
  3. Outer `交易记录 / 点位管理` label + long role badge still crush CJK into one-character-per-line wrap.
- Superseded Data coverage draft [`2026-07-20-data-coverage-presentation`](../2026-07-20-data-coverage-presentation/2026-07-20-data-coverage-presentation.md) explored progressive market-day presentation for Data; user later deprioritized it. **This batch re-opens progressive date navigation only for Review**, not Data/Admin/Static unless a later intake expands scope.
- User explicitly rejected a “make selects darker” misread: the ask is **UI style consistency** and **date/data filtering IA**, not surface lightness alone.

## Visual Reference

### Live acceptance evidence (current friction)

1. Data page + broken bottom trader nav wrap: [`./screenshots/2026-07-20-data-sidebar-trader-nav-wrap.png`](./screenshots/2026-07-20-data-sidebar-trader-nav-wrap.png) · SHA-256 `4a52d56c44375e5a0e64d56b7979027520d708afd89438b9f6d4cd89fc99d6c6`
2. Review left column trade-filter crop (current): [`./screenshots/2026-07-20-review-trade-filter-current.png`](./screenshots/2026-07-20-review-trade-filter-current.png) · SHA-256 `4e5e0f4af36f69c2c748d4c6c6909a1558e4cf257f827fef5e194ada354933e1`
3. Trade list + chart markers CALL/PUT same trader-blue (direction only by shape): [`./screenshots/2026-07-20-trade-call-put-trader-color.png`](./screenshots/2026-07-20-trade-call-put-trader-color.png) · SHA-256 `dda2d9256a738ebc320d7752243ca98816ebb19a818fc03bbec2348317cf50cb`

### Evidence method (user-confirmed)

- **HTML mockup** is the free design surface: iterate structure, chrome, and color samples here without touching the live app.
- **Live Review / product frontend** is **not** a sketchpad. Do not land sample or exploratory UI in online Review code until a promoted plan authorizes implementation.
- **Screenshots** remain first-class feedback for live runtime friction (e.g. current CALL/PUT coloring before any authorized fix).

### Locked HTML mockup (proposal evidence)

| File | Role | SHA-256 |
| --- | --- | --- |
| [`./mockups/review-left-column.html`](./mockups/review-left-column.html) | Design mockup — date nav + trade panel + direction colors + **locked B chip filter** + 8-person scale demos; not live app | `ff5d71ffa87bb65127f0bcf05d421e07c211678cff19473f9f88672337233c50` |

Open the mockup in a browser for interactive 最近 / 按月 switching. Paths are relative to this record; any copy under `output/mockups/` is scratch only.

What the evidence shows together:

- Review left column still stacks **two chrome languages**: compact terminal context (ticker tabs, date chips, Strategy, plus the current Ext K / Rescan / Backtest row) above a form-card trade block (Eligibility, Focus, Download, group cards) with redundant `SPY | YYYY-MM-DD` mirrors.
- User lock (mockup): the Review left column **does not need to display** Ext K / RTH, Rescan, or Backtest. Strategy + assembly status remain; those three actions are out of this column’s proposal surface (relocate/omit decided at plan time, not required in the locked HTML).
- Date selection remains **flat exhaustive chips** per ticker; already dense at ~46 SPY days and will not scale.
- Month identity must not be repeated: no month bar in 最近; in 按月, month bar is sole month identity and chips are day-number only.
- Outer shell trader destination still shows long capability copy inline with a multi-character Chinese label, producing vertical CJK wrap on the Data page acceptance shot.

## Scope Lock (user-confirmed 2026-07-20)

| Decision | Lock |
| --- | --- |
| Date navigation approach | **A · progressive 最近 / 按月** (not full calendar grid as primary) |
| Trade panel | Yes: remove redundant ticker/date mirror; align control vocabulary with Strategy field density and compact terminal buttons |
| Ext K / Rescan / Backtest | **Not shown** in the Review left-column proposal (user 2026-07-20); omit from locked mockup |
| UI font | **Microsoft YaHei / 微软雅黑** for product UI text; monospace only for codes/times/day chips |
| Trade point colors | **Names: one default text color** (full name already on the point; never red names). **Color only for direction**: CALL vs PUT differ (glyph + label + optional rail). Trader identity = text, not hue. |
| Trader filter UI | **Locked B · Chip multi-select** (user 2026-07-20). Drop ☑+Focus. A segment is **not** the product target (kept only as rejected/scale contrast in mockup notes). |
| Trader filter scale | Few visible traders → inline chips; many → summary + edit drawer with search / select-all / clear. Only **day-available** traders appear. |
| Surface scope | **Review only** for date-rail and trade-panel fusion in this batch |
| Data / Admin / Static `DateRail` | Unchanged unless a later intake expands scope |
| Mockup authority | Sole file [`./mockups/review-left-column.html`](./mockups/review-left-column.html); B chip effect is part of the locked proposal surface |

## OPT-001 Progressive Review Date Navigation (最近 / 按月)

- Source evidence:
  - User statements (2026-07-20): 日期 chip **平铺直叙**效果不好，记录数据多了之后看不过来；肯定走方案 A；并指出「最近」模式下再挂月份条、或按月时 chip 重复写 `07-` 属于冗余。
  - Live Review/Data date rails via shared `DateRail` in `frontend/src/features/review/ReviewContextPanel.jsx` + `groupDatesByMonth` in `reviewWorkspace.js`: every market day for the selected ticker renders as an `MM-DD` chip under every month group, with only `max-height` + scroll as density control.
  - Locked mockup: [`./mockups/review-left-column.html`](./mockups/review-left-column.html).
- Current friction:
  - **Scan failure at scale:** exhaustive chips consume the left column; strategy/trade blocks are pushed down; locating an older month is linear scroll through every day.
  - **No progressive hierarchy:** month labels group chips but do not gate how many days appear; there is no “recent window” vs “browse by month” mode.
  - **IA risk if naively layered:** stacking 最近/按月 **and** a month bar **and** `MM-DD` chips repeats the month identity.
- Desired outcome:
  - Review date browsing stays chip-based but becomes progressive and scannable as SPY/QQQ history grows.
  - One layer states one fact (see IA table below).
  - Selecting a chip still resolves the same workspace day and reloads review assembly; no fabricated dates.
- Locked IA rules (from mockup):

  | Layer | Responsibility |
  | --- | --- |
  | Ticker tabs | Select underlying (SPY / QQQ) |
  | 最近 / 按月 | Select **browse strategy**, not the day |
  | Month bar (`‹ YYYY-MM ›`) | **Only in 按月** — sole month identity |
  | Chips | Select day — `MM-DD` in 最近 (may span months); **day number only** in 按月 |
  | Optional 跳转 row | Tool to jump to a trading day; available in both modes; not bound into the month bar |
  | Topbar 日期 stat | Read-only current result, not a third filter |

- Mode behavior:
  - **最近 (default):** no month bar; show newest N trading days as `MM-DD` chips; meta e.g. `显示最近 N · 全库 ticker M`. Default N proposal: **12–20** (exact N fixed at plan time).
  - **按月:** month bar is the only month identity; chips show `DD` only for days in that month; meta e.g. `本月交易日 K · 全库 M`.
  - **跳转:** optional explicit jump control on its own row; validates against real market days for the selected ticker; does not invent sessions.
- Acceptance direction:
  - At ≥46 SPY days, default 最近 view fits without feeling like a full-history dump; 按月 can reach any owned month without listing every historical chip at once.
  - No simultaneous double month identity (no month bar in 最近; no `MM-` prefix on chips in 按月).
  - Workspace contract unchanged: chip/jump → valid `{ticker, trade_date}` → existing `selectWorkspaceDay` / review reload path.
  - Keyboard and `aria-*` states remain programmatic for mode, month, and selected day.
- Boundary that must not change:
  - actual NYSE/trading calendar ownership remains backend/data; UI only lists days that already exist in workspace inventory;
  - no silent ticker substitution; no fabricated missing QQQ/SPY days;
  - Data / Admin / Static keep current `DateRail` unless scope is expanded by a new decision;
  - no provider/broker, DB schema, publication, or remote action from this item.
- Lifecycle status: promoted-to-proposed

## OPT-002 Fuse Review Trade-Filter/List With Upper Context Chrome

- Source evidence:
  - User statements (2026-07-20): 不是浅色问题，而是 **UI 风格一致性** 以及 **日期数据筛选**；交易区按“去掉重复 mirror + 对齐 Strategy/按钮语汇”做；并确认 mockup 方向。
  - Current crop: [`./screenshots/2026-07-20-review-trade-filter-current.png`](./screenshots/2026-07-20-review-trade-filter-current.png).
  - Prior pink-box crop still informative: [`../2026-07-20-trader-workspace-nav-and-registry/screenshots/2026-07-20-review-trade-filter-panel.png`](../2026-07-20-trader-workspace-nav-and-registry/screenshots/2026-07-20-review-trade-filter-panel.png).
  - Implementation: `TraderFilters.jsx`, `TradeExportControls.jsx`, `TraderTradeList.jsx` composed under Review left column after `ReviewContextPanel` in `ReviewPage.jsx` / `StaticReviewsApp.jsx`; shared styles under `.trade-filter-panel` / `.trade-group-card` in `frontend/src/styles.css`.
  - Target visual: trade block section of [`./mockups/review-left-column.html`](./mockups/review-left-column.html).
- Current friction:
  - **Two chrome systems in one column:** date/strategy use compact terminal field + button rows; Eligibility / Focus / Download / cards still feel like a nested form/card stack.
  - **Duplicate date authority:** trade panel re-renders readonly `SPY | YYYY-MM-DD` mirrors even though ticker tabs + date rail (and topbar 日期) already own that context — amplifies “which control filters the day?” confusion.
  - **Not primarily a color complaint:** even after terminal tokens, spacing, label hierarchy, control geometry, and nested borders still diverge from the upper Review chrome.
- Desired outcome:
  - From ticker → date → strategy → eligibility/focus → list, the Review left column reads as **one continuous Daily Review surface**.
  - Date is selected only in the progressive rail (OPT-001); trade filters operate **inside** the resolved day (eligibility, trader multi-select, focus, export, drilldown).
  - Eligibility uses the same field density as Strategy; Focus / Download use compact terminal button language; list cards share terminal density without a second product skin.
  - Left column under Strategy does **not** include Ext K / RTH, Rescan, or Backtest controls (user-confirmed for the locked mockup).
- Acceptance direction:
  - Side-by-side with Strategy, Eligibility/Focus/Download share geometry, type scale, and active language; no Ext K / Rescan / Backtest row in the left column proposal.
  - No ticker/date mirror inside the trade filter when `context` is already supplied by Review workspace chrome.
  - Availability-driven trader visibility, eligibility modes, selection reconciliation, export of current selection, and group expand/collapse contracts remain unless a separate plan revises them.
  - Static Review that reuses the same components either inherits the fused Review density or is explicitly listed as an exception at plan time (batch default: follow shared components only where Review mounts them; do not restyle Admin lightly as a second brand in this batch).
- Boundary that must not change:
  - availability-driven trader visibility, filter reconciliation, export contents, normalized trade payload contracts;
  - no auth bypass; no data write from Review filters; no publication/provider changes.
- Lifecycle status: promoted-to-proposed

## OPT-003 Shell Trader-Nav Label / Capability Density

- Source evidence:
  - Acceptance screenshot: [`./screenshots/2026-07-20-data-sidebar-trader-nav-wrap.png`](./screenshots/2026-07-20-data-sidebar-trader-nav-wrap.png).
  - `Layout.jsx` peer `NavItem` for admin destination uses long capability string `只读检查，编辑需要管理员` inline with label `交易记录 / 点位管理`.
- Current friction:
  - Long nowrap badge + flex row shrink forces CJK label to wrap one character per line — looks broken and fails peer-nav polish from the prior terminal-ui plan.
- Desired outcome:
  - Expanded rail shows a single-line (or intentional two-line stack) Chinese label with a **short** capability chip (`只读` / `可编辑`); full permission sentence stays in `title` / `aria-label` only.
  - Collapsed icon-only mode keeps a complete accessible name.
- Acceptance direction:
  - Data/Review/any page with expanded shell: trader destination label does not vertical-wrap per character; capability cue remains understandable without a second button skin.
- Boundary that must not change:
  - admin-only mutation, readonly inspection, route set, auth/session;
  - no return of orange filled CTA as destination chrome.
- Lifecycle status: promoted-to-proposed
- Note: small local CSS/structure experiments may already exist in a dirty worktree from acceptance debugging; they do **not** change this record’s status and are not authorized as the completed implementation of this batch.

## OPT-004 Dual Color For Direction And Trader

- Source evidence:
  - User statement (2026-07-20): 交易者点位信息 CALL/PUT 要用不同颜色区别；不同交易者也要用不同颜色区分. Not everything needs HTML mockup — screenshot feedback is enough.
  - Live crop: [`./screenshots/2026-07-20-trade-call-put-trader-color.png`](./screenshots/2026-07-20-trade-call-put-trader-color.png).
  - Current contract (multi-trader plan): `marker_color` is **trader-owned**; CALL/PUT differ only by `triangle_up` / `triangle_down`. List cards also paint the direction triangle with `var(--trader-color)`, so one trader’s CALL and PUT look the same hue (only shape differs). Chart labels inherit that same trader fill via `_annoColor(..., marker_color)`.
- Current friction:
  - On the chart, `vordin CALL` and `vordin PUT` both read as the same blue family — hard to scan direction at a glance.
  - On the list, 沃德哥 PUT and CALL share the same blue border/triangle family.
  - When multiple traders appear, registry colors already differ, but direction still lacks an independent color channel.
- Desired outcome (user-locked simplification):
  | Channel | Carries | Visual |
  | --- | --- | --- |
  | **Name** | which trader | **Same default text color for everyone**; full display name is enough |
  | **Direction** | CALL vs PUT | **Only place color is used**: triangle + CALL/PUT word (+ optional left rail) |
  - **Hard taboo:** never paint a person’s name red.
  - Do **not** use registry trader hue on name text; multi-trader scenes rely on readable full names.
  - Shape up/down remains a secondary cue.
  - Sample only in mockup until plan-authorized implementation.
- Acceptance direction:
  - Same trader’s CALL and PUT are immediately separable by color on both list and chart.
  - Two traders are separable by **full display name text** (not by name color).
  - Color is not the only cue for direction: triangle up/down + CALL/PUT word remain.
- Boundary that must not change:
  - registry color storage/schema may still exist for other uses; this item does not require name text to use registry hue;
  - availability/filter/export contracts; no fabricated outcomes.
- Lifecycle status: promoted-to-proposed
- Evidence form: acceptance **screenshot** for current friction; direction-color **sample in mockup HTML** until plan-authorized implementation. Do not prototype this on live Review.

## OPT-005 Trader Filter · Locked B Chip Multi-Select

- Source evidence:
  - User (2026-07-20): ☑ + Focus feels redundant; asked for better patterns; compared A segment vs B chip in mockup including **8-person scale** demos; concluded B is stronger (esp. with search); explicit **「opt锁定B效果」**.
  - Mockup: [`./mockups/review-left-column.html`](./mockups/review-left-column.html) — left-rail B chips (interactive), notes contrast vs legacy ☑+Focus and A segment, scale section B 收纳 (summary + edit + search).
  - Live today: `TraderFilters.jsx` checkbox multi-select + separate Focus button; `filterTradeGroups` honors both `traderIds` and `focusedTraderId`.
- Current friction:
  - Two controls for overlapping “who is visible” authority.
  - Focus is a single-trader shortcut that multi-select already covers when few traders.
- **Locked product effect (B):**
  1. **One control:** trader visibility = **toggle chips** only. **No Focus button.** No checkbox+Focus pair.
  2. **Multi-select:** any subset of day-available traders; empty selection → empty list/markers/export for traders (fail closed on selection, not crash).
  3. **Default:** all traders that have displayable groups for the resolved ticker/date (availability-driven), same spirit as today’s default multi-select of available traders.
  4. **Few traders (guideline ≤3–4 visible):** chips render **inline** in the Review left column under Eligibility.
  5. **Many traders (guideline ≥7, or when inline chips crowd the rail):** collapse to **summary** (“N 人已选 · names…”) + **编辑** opens drawer with **search**, **全选**, **清空**, and chip list.
  6. **Mid range (4–6):** prefer inline chips if they fit; otherwise start summary early — plan may pick exact threshold.
  7. **Only day-available traders** appear as chips (existing availability contract); not the full registry census.
  8. **Export / list / chart markers** all consume the **same selected chip set** (replaces focusedTraderId path; plan should remove or hard-deprecate Focus).
  9. **Names on chips** use default text color (aligned with OPT-004 name rule).
- Rejected for product target:
  - **A · Segment** (`全部 | person…`) — fine for all-vs-one only; weak for arbitrary subsets; 8-way segment anti-pattern. May remain in mockup as contrast only.
  - **Legacy ☑ + Focus** — redundant; do not reintroduce.
- Acceptance direction (when implemented under a plan):
  - Review left column shows B chips (or scaled summary+drawer), never Focus.
  - Toggling chips updates trade list + chart trade markers + export selection together.
  - With 8 simulated available traders, UI remains usable via summary+drawer+search (mockup scale demo is the visual bar).
- Boundary that must not change:
  - availability-driven visibility; eligibility modes; admin mutation gates; no live coding from this record alone.
- Lifecycle status: promoted-to-proposed
- User lock timestamp: 2026-07-20 · `opt锁定B效果`

## How The Items Nest

```
OPT-001  Review progressive date navigation (最近 / 按月, no month redundancy)
OPT-002  Review trade-filter/list fusion (one chrome; date authority only in rail)
OPT-003  Outer shell trader-nav label density (peer polish / CJK wrap)
OPT-004  Trade point color: direction CALL/PUT only; uniform name text
OPT-005  Trader filter: locked B chip multi-select (no Focus)
```

Mockup is the free design surface for 001/002/004/005. Live Review must not be used as a sketchpad.

## Planning Decisions Captured (for a future Exec Plan)

1. Scope = **Review only** for DateRail progressive modes + trade-panel fusion + trader filter B.
2. Visual authority for left-column IA = sole mockup [`./mockups/review-left-column.html`](./mockups/review-left-column.html).
3. Default date mode = **最近**; N fixed at plan time (candidate 12–20).
4. Trade panel drops context mirrors when workspace chrome already shows ticker/date.
5. Review left column proposal omits Ext K / RTH, Rescan, and Backtest; plan later decides whether those actions move, remain elsewhere, or stay product-accessible by other means — not required in this column.
6. UI typeface is **Microsoft YaHei（微软雅黑）** app-wide for readable product text; keep a mono stack only for timestamps, day chips, and technical codes.
7. Trade markers/list: **uniform name color**; **CALL vs PUT** own the color channel; identity by full name text; never red names.
8. **Trader filter locked to B Chip multi-select** (user 2026-07-20). Drop Focus. Few → inline chips; many → summary + edit drawer (search / select-all / clear). Day-available only. Selected chip set drives list, markers, and export.
9. A segment is **not** the implementation target.
10. Do not reopen app-wide paper-vs-terminal color debate; stay inside current terminal token family and fix **control vocabulary / IA**.
11. No implementation, Git, data, or remote authority from this record alone.

## Promotion Boundary

This batch is **promoted-to-proposed** under the user's explicit 2026-07-20 request. The canonical review-only plan is [`2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`](../../exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md). A separately authorized eligible plan checkpoint, matching independent design review, explicit activation, and a later implementation-start instruction are still required before code can land as the authorized solution. Local mockups and screenshots remain proposal evidence, not proof of implementation.
