# Optimization Batch · 2026-07-21 Review Sidebar Spacing And K-line Selection Band

> Record-only intake. This file does not authorize implementation, plan promotion, push, data mutation, or remote actions.
>
> Place this file at:
> `docs/optimization/2026-07-21-review-sidebar-spacing-and-kline-selection-band/2026-07-21-review-sidebar-spacing-and-kline-selection-band.md`
> Evidence images live in `./screenshots/`.
>
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Sidebar Trade tools / trader cards / strategy detail stack needs gaps | Review + Static `.dr-sidebar` mid-stack | recorded | none | User: tools → 交易者 → 策略讲解 三段贴死 |
| OPT-002 | Trader select blue K-line band overlay is too loud | Review + Static K-line group/select highlight | recorded | none | Keep point jump; remove/soften blue band |

## Scope Lock (user-confirmed 2026-07-21)

| Decision | Lock |
| --- | --- |
| Surface parity | **Review and Static must stay aligned** for both OPT items |
| OPT-001 friction | Explicit example: **Trade tools** → **trader cards** → **strategy detail / 策略讲解** have almost no vertical gap |
| OPT-002 keep | Clicking a left-side trader still **quickly locates** the trade point on the chart |
| OPT-002 friction | The **blue translucent vertical band** that covers K bars after select is too ugly |
| Out of scope unless reopened | Filter/export semantics; trade data contract; strategy assembly; tracked DB/content; provider/Pages; Admin unless later expanded |

## Relationship To Prior Work

- Recent completed group-span / viewport work: [`2026-07-21-review-trade-and-kline-session`](../2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md) OPT-003…006 → completed plan `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan` (introduced multi-bar blue selection band + span-fit). OPT-002 is post-ship acceptance friction on that band visual, not a reopening of the whole plan.
- Trade panel polish / density: completed plans under trade-panel visual polish and data progressive + card density. OPT-001 is residual **inter-block rhythm** between tools, trader list, and strategy signal list after those density passes.

## Visual Reference

### OPT-001 — sidebar stack no gap

- [`./screenshots/2026-07-21-review-sidebar-stack-no-gap.png`](./screenshots/2026-07-21-review-sidebar-stack-no-gap.png)
- SHA-256: `e7846e060f3f7f5049dd92edc512de39f939dab11670cfc4ac0667d969020d37`
- Size: 101,372 bytes
- Fixture: SPY Review sidebar — Trade tools, Tang trader card, and strategy detail cards (e.g. 普通 PUT 启动观察流程) stacked with no breathing room.

### OPT-002 — blue selection band

- [`./screenshots/2026-07-21-review-kline-selection-blue-band.png`](./screenshots/2026-07-21-review-kline-selection-blue-band.png)
- SHA-256: `a5cf3b8a4f64ab86775e16ecb00a3bfcb842c02698e87f1892772dad5b5de89d`
- Size: 214,397 bytes
- Fixture: SPY `2026-07-17` Review — left Tang group selected; chart jumps near Tang BUY while a tall translucent blue vertical band covers the selection span.

## OPT-001 Sidebar Trade Tools / Trader Cards / Strategy Detail Stack Needs Gaps

- Source evidence: sidebar stack screenshot above; user 2026-07-21 live acceptance; explicit example that Trade tools, 交易者, and 策略详细讲解 have no gap.
- Current friction:
  - Mid-stack blocks in `.dr-sidebar` (Trade tools chrome, trader group cards, strategy/signal detail list) sit edge-to-edge.
  - Users cannot scan a clear “tools → real trades → strategy narrative” hierarchy; the column looks cramped and unfinished.
- Desired outcome:
  - Stable, visible vertical separation between those three stacks on **Review and Static**.
  - Keep recent card density / type scale; do not undo information content.
- Boundary that must not change:
  - Filter/export authority and semantics; progressive date rules; trade payload shape; strategy assemble pipeline; App shell left nav.
- Lifecycle status: recorded

## OPT-002 Trader Select Blue K-line Band Overlay Is Too Loud

- Source evidence: blue-band screenshot above; user 2026-07-21 live acceptance after click-locate on left trader.
- Current friction:
  - Selecting a trader group correctly locates the chart to the trade point, but a **semi-transparent blue vertical band** cloaks the K bars around the span.
  - The band is the dominant visual and reads as a dirty overlay rather than a subtle focus cue.
- Desired outcome:
  - Preserve fast point location / focus after left-side trader select.
  - Remove the blue band or replace it with a lighter, non-covering cue that does not paint a large blue slab over the chart.
  - **Review and Static** stay aligned.
- Boundary that must not change:
  - Marker labels (display_name + BUY/SELL); trade data; group-select focus target; timeframe/viewport contracts beyond the highlight chrome; no provider/DB/content mutation.
- Lifecycle status: recorded

## Explicit Non-Authorization

This batch does **not** authorize:

- source-code implementation;
- proposed plan drafting (needs a separate user request);
- activation, push, PR, merge, Pages, provider/broker, or any remote action.
