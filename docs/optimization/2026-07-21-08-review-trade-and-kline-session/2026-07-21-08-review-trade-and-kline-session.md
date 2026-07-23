# Optimization Batch · 2026-07-21

> Optimization intake batch. This file does not authorize implementation.
>
> **Session-consolidated batch.** All 2026-07-21 Review trade-panel / K-line friction from this optimization-record session lives here. Earlier same-day split batches are `superseded` (see below).
>
> 2026-07-21: User instruction converting this document to a prop plan promoted **OPT-003…006** only. OPT-001/002 remain completed under the earlier plan. 2026-07-21: user activated matching-revision `v3` plan, then full-execution closed OPT-003…006 via completed plan `a76b836…`.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Trade cards: points only (drop $ / %) | Review / Trade Cards | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md) | 只保留交易时间点位 |
| OPT-002 | K-line markers: BUY/SELL + nickname `vordinkkk` | Review / K-line + trader display | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md) | 方向靠颜色箭头；UI 昵称映射 `vordin` |
| OPT-003 | Trade tools: remove Eligibility segment | Review / Trade tools | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md) | 取消 Display / Reported / Calculated 整行 |
| OPT-004 | K-line 5m switch: first-paint viewport glitch | Review / Kline Engine | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md) | 点 5m 先坏图，滚轮后才正常 |
| OPT-005 | Group focus span + legs/events timeline UI | Review / Cards ↔ Chart | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md) | 点卡片框整段交易；legs 紧凑时间线，可点单笔（方向已认可） |
| OPT-006 | Data page Market days: progressive rail stretched ugly | Data / Market days | completed | [completed plan](../../exec-plans/completed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md) | 宽面板里被拉满的 QQQ/SPY、最近/按月 不伦不类 |

## Visual Reference

| Evidence | Path |
| --- | --- |
| Trade cards (amount / profit noise context) | [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png) |
| K-line markers live (`vordin CALL/PUT`) | [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png) |
| Eligibility row to remove | [`screenshots/2026-07-21-trade-tools-eligibility-remove.png`](./screenshots/2026-07-21-trade-tools-eligibility-remove.png) |
| 5m switch broken first paint | [`screenshots/2026-07-21-kline-5m-switch-initial-viewport.png`](./screenshots/2026-07-21-kline-5m-switch-initial-viewport.png) |
| Group select zooms first event only | [`screenshots/2026-07-21-trade-group-select-first-event-only.png`](./screenshots/2026-07-21-trade-group-select-first-event-only.png) |
| Legs/events current expanded UI | [`screenshots/2026-07-21-trade-legs-events-current-ui.png`](./screenshots/2026-07-21-trade-legs-events-current-ui.png) |
| Data Market days stretched controls | [`screenshots/2026-07-21-data-market-days-stretched-controls.png`](./screenshots/2026-07-21-data-market-days-stretched-controls.png) |
| **Session mock (all UI items)** | [`mockups/review-trade-and-kline-session.html`](./mockups/review-trade-and-kline-session.html) |

## Supersedes (this session)

| Previous batch | Status |
| --- | --- |
| [`../2026-07-21-04-trade-card-simplify-points-only/`](../2026-07-21-04-trade-card-simplify-points-only/2026-07-21-04-trade-card-simplify-points-only.md) | superseded → OPT-001 |
| [`../2026-07-21-05-kline-marker-action-and-trader-nickname/`](../2026-07-21-05-kline-marker-action-and-trader-nickname/2026-07-21-05-kline-marker-action-and-trader-nickname.md) | superseded → OPT-002 |
| [`../2026-07-21-06-trade-points-and-kline-marker-labels/`](../2026-07-21-06-trade-points-and-kline-marker-labels/2026-07-21-06-trade-points-and-kline-marker-labels.md) | superseded → OPT-001 + OPT-002 (partial merge) |
| [`../2026-07-21-07-kline-5m-switch-viewport-glitch/`](../2026-07-21-07-kline-5m-switch-viewport-glitch/2026-07-21-07-kline-5m-switch-viewport-glitch.md) | superseded → OPT-004 |

---

## OPT-001 Trade cards: points only

- Source evidence: [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png). User: 做减法，不需要金额和盈收比例，只展示交易时间点位。
- Current friction: Cards / expanded legs surface `$` amounts, fees, and profit / return % noise.
- Desired outcome: Presentation-only subtraction — **timestamps + price points** only on the card reading path.
- Boundary: Schema / API / reported·calculated fields may remain in data; Review / Static / Admin shared cards; presentation only.
- Lifecycle status: completed → [`2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan`](../../exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md) revision `v2-review-foldback-2026-07-21`; `implementation-review-001: accept/high`; verified `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`

## OPT-002 K-line markers: BUY/SELL + nickname `vordinkkk`

- Source evidence: [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png). Live labels: `vordin CALL` / `vordin PUT` / `vordin CALL ×2`.
- Current friction: Marker text repeats CALL/PUT while color + triangle already encode direction; no buy vs sell; raw `trader_id` / 沃德哥 instead of preferred English nickname.
- Desired outcome:
  1. Marker text = **BUY** / **SELL** (from event action); shape+color still own CALL/PUT.
  2. UI shows **`vordinkkk`**; persistence keeps **`trader_id: vordin`** (沃德哥).
- Boundary: Event option type + action fields; canonical `trader_id`; historical day files. Card CALL/PUT badges may remain.
- Live contract note: shipped `tradeRecords.js` builds `marker_label` / `title` as `` `${displayName} ${BUY|SELL}` `` (+ optional `×N` on label only).
- Lifecycle status: completed → [`2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan`](../../exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md) revision `v2-review-foldback-2026-07-21`; `implementation-review-001: accept/high`; verified `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`

## OPT-003 Trade tools: remove Eligibility segment

- Source evidence: [`screenshots/2026-07-21-trade-tools-eligibility-remove.png`](./screenshots/2026-07-21-trade-tools-eligibility-remove.png) — yellow box around **Eligibility · Display / Reported / Calculated**. User: 都取消，不需要展示这部分内容。
- Current friction: Trade tools still exposes the Eligibility segmented control. User does not want this chrome on the Review trade panel surface.
- Desired outcome: **Remove** the Eligibility row (label + Display / Reported / Calculated segments) from Trade tools UI so it is not shown. Keep Download and Traders chip area unless later OPT says otherwise.
- Boundary:
  - Underlying eligibility flags on groups / admin editor forms are **not** automatically deleted from schema by this UI hide; plan time decides whether filter state hard-defaults to display-eligible only, or admin-only controls remain elsewhere.
  - Primary surface: shared Trade tools used by Review (and Static/Admin if same component).
- Live source: `frontend/src/features/review/TraderFilters.jsx` Eligibility `radiogroup`.
- Lifecycle status: completed → plan `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan` revision `v3-review-foldback-2026-07-21`; product commit `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`; next gate `closed`.

## OPT-004 K-line 5m switch first-paint viewport glitch

- Source evidence: [`screenshots/2026-07-21-kline-5m-switch-initial-viewport.png`](./screenshots/2026-07-21-kline-5m-switch-initial-viewport.png). User: 点 5m 先出现该异常画面（K 线挤左、右侧空白），**滚轮后**才正常。
- Current friction: Timeframe switch to 5m does not land a correct full-window viewport on the first render; wheel path recalculates and fixes it.
- Desired outcome: First `render` after `setTimeframe('5m')` (ideally any TF switch) must show a correct viewport without wheel interaction.
- Likely surface (investigation only): `frontend/src/kline/kline-engine.js` `setTimeframe` + shared `ViewportManager.zoomScale` / `viewStart` vs 1m→5m window constants.
- Boundary: No change to bars payloads / assemble / seed contracts; not a publish/DB issue.
- Lifecycle status: completed → plan `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan` revision `v3-review-foldback-2026-07-21`; product commit `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`; next gate `closed`.

## OPT-005 Group focus span + legs/events timeline UI

- Source evidence:
  - Chart after selecting 沃德哥 PUT: [`screenshots/2026-07-21-trade-group-select-first-event-only.png`](./screenshots/2026-07-21-trade-group-select-first-event-only.png) — viewport zooms a **single** bar near first event; other events of the same group not framed as a span.
  - Expanded legs: [`screenshots/2026-07-21-trade-legs-events-current-ui.png`](./screenshots/2026-07-21-trade-legs-events-current-ui.png) — dense unaligned text (`buy_open` / `sell_partial` / `fees ?` glued together); user: 效果不行，需要优化 UI.
  - User question: 点 PUT 框只会放大第一笔，后面交易如何体现？每笔都单独放大又浪费空间。
- Current friction:
  1. `selectTradeGroup` resolves **one** annotation (first matching `trade_group_id`) and `fitRange` around that single bar — multi-event groups (open + closes / partials) lose group context on chart.
  2. Expanded legs/events is a raw dump: hard to scan, wastes vertical space when many partials, shows fees/`?` noise (conflicts with OPT-001 subtraction).
- **Design direction (recommended, locked for mock):**
  1. **Group select → fit the whole event span** of that group: `min(event bar) … max(event bar)` + modest padding. One zoom frames the trade lifecycle without “one zoom per event”.
  2. Soft highlight band across that span (not only a single marker flash).
  3. Collapsed card meta: **time span + event count** e.g. `09:42 → 10:01 · 7 pts` (no $/%).
  4. Expanded **timeline UI** (compact table rows): `TIME | ACTION | QTY @ PX` — short actions (`BUY` / `SELL` / `PART`), **no fees** (OPT-001).
  5. **Optional secondary navigation**: click a timeline row → center/highlight that event bar *without* expanding the whole day; primary group select stays span-fit.
  6. Do **not** auto-fit each partial independently on group click (space waste / jarring).
- Desired outcome: Selecting a group shows “this trade’s window”; expanded legs are a scannable point timeline; multi-event groups remain honest without one-bar tunnel vision or full-day noise.
- Boundary:
  - Live path today: `ReviewPage.jsx` `selectTradeGroup` + `TraderTradeList.jsx` expand block; annotations from `buildTradeRecordAnnotations`.
  - No schema change required for UI; span is derived from existing leg events’ timestamps / bar indices.
  - Admin editor forms out of scope unless they share the same list component.
- User foldback (2026-07-21): 方向认可（“可以的”）— span fit + compact timeline locked for mock.
- Lifecycle status: completed → plan `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan` revision `v3-review-foldback-2026-07-21`; product commit `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`; next gate `closed`.

## OPT-006 Data page Market days: progressive rail stretched / incongruous

- Source evidence: [`screenshots/2026-07-21-data-market-days-stretched-controls.png`](./screenshots/2026-07-21-data-market-days-stretched-controls.png). User: Data 页 Market days 显示太奇怪，像把不合适的控件强行拉升，搞得不伦不类。
- Current friction:
  1. Data page reuses Review progressive `ReviewContextPanel` inside a **wide** panel (`DashboardPage` → `.panel`).
  2. Shared CSS gives ticker tabs and mode buttons `flex: 1` (designed for **narrow** `.dr-sidebar` rail ~300px).
  3. On the wide Data card, **QQQ / SPY** and **最近 / 按月** stretch into full-width “progress bar” slabs; month nav also spans the full card — controls look forced, not native to a dashboard panel.
  4. Day chips remain small, so hierarchy feels broken (giant mode bars + tiny day pills).
- Desired outcome: Market days on Data should feel like a **compact control strip** (or well-proportioned panel content), not stretched Review-sidebar chrome. Progressive IA (ticker → 最近/按月 → month nav → day chips) can stay; **layout density / max width / flex growth** must match the wide surface.
- Design direction (for mock; plan freezes exact CSS):
  1. Ticker + mode segments **content-sized or max-width** (no full-bleed `flex: 1` on wide panel).
  2. Optional: wrap progressive rail in a left-aligned column (`max-width: ~360–420px`) so it reads like a tool, not a stretched banner.
  3. Day chips keep compact mono pills; meta line stays secondary.
  4. Prefer Data-scoped surface class (e.g. `.page .panel .review-context-panel` / density variant) over breaking Review sidebar where stretch is intentional.
- Likely surface: `DashboardPage.jsx` + `ReviewContextPanel.jsx` + `styles.css` (`.ticker-tabs button { flex: 1 }`, `.date-rail-mode button { flex: 1 }`).
- Boundary: No change to market-day inventory, ticker isolation, progressive browse state machine, or open-Review-on-date behavior unless plan expands; presentation/layout only.
- Lifecycle status: completed → plan `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan` revision `v3-review-foldback-2026-07-21`; product commit `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`; next gate `closed`.
