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
| OPT-001 | Sidebar Trade tools / trader cards / strategy detail stack needs gaps | Review + Static `.dr-sidebar` mid-stack | recorded | none | User: tools → 交易者 → 策略讲解 三段贴死 · 2026-07-21 mock 方案已确认 |
| OPT-002 | Trader select blue K-line band overlay is too loud | Review + Static K-line group/select highlight | recorded | none | Keep point jump; 2026-07-21 决策：直接取消蓝色带，不加替代提示 |

## Scope Lock (user-confirmed 2026-07-21)

| Decision | Lock |
| --- | --- |
| Surface parity | **Review and Static must stay aligned** for both OPT items |
| OPT-001 friction | Explicit example: **Trade tools** → **trader cards** → **strategy detail / 策略讲解** have almost no vertical gap |
| OPT-002 keep | Clicking a left-side trader still **quickly locates** the trade point on the chart |
| OPT-002 friction | The **blue translucent vertical band** that covers K bars after select is too ugly |
| OPT-001 lock (mock 2026-07-21) | ≈20px inter-block gaps + 交易者/策略讲解 section captions with hairline dividers; trader filter row deduped to a single `Traders` label — `TRADE TOOLS` panel title and Download button removed |
| OPT-002 lock (mock 2026-07-21) | **Cancel the highlight band entirely — no replacement cue**; keep click-to-locate / fitRange; marker labels unchanged |
| Out of scope unless reopened | Filter/export semantics (see OPT-001 boundary for the Download-entry exception); trade data contract; strategy assembly; tracked DB/content; provider/Pages; Admin unless later expanded |

## Mock Review Decision (user, 2026-07-21)

- Mock: [`./mock.html`](./mock.html) — 自包含对比页，可切换当前态/方案态；打开默认展示已确认方案态。
- OPT-001: **方案确认** — Trade tools / trader cards / strategy detail 三块之间稳定间距（≈20px）+ 交易者/策略讲解小节标与分隔线；块内卡片密度、字号不动；Review 与 Static 保持对齐。
- OPT-001 同日迭代: trader 筛选块文字去重 — 移除 `TRADE TOOLS` 面板标题与 Download 按钮，只留单个 `Traders` 标签 + trader chip。注意 Download 属 export 入口（原 OPT-001 boundary 含 filter/export），实现评审需确认导出入口去向。
- OPT-002: 蓝色带、锚点 marker、细描边三方案均被否决；**直接取消选区高亮**，不加替代视觉提示 — 交易点已由 marker 标签（display_name + BUY/SELL）标出，无需额外提醒。保留点击定位 / fitRange；marker 标签契约不变。
- 留待实现评审：drilldown 单行事件聚焦 `eventFocusPayload`（`frontend/src/features/review/tradeRecords.js:339`）同样返回 `style: 'blue'`，是否一并取消在实现评审时确认。

## Relationship To Prior Work

- Recent completed group-span / viewport work: [`2026-07-21-review-trade-and-kline-session`](../2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md) OPT-003…006 → completed plan `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan` (introduced multi-bar blue selection band + span-fit). OPT-002 is post-ship acceptance friction on that band visual, not a reopening of the whole plan.
- Trade panel polish / density: completed plans under trade-panel visual polish and data progressive + card density. OPT-001 is residual **inter-block rhythm** between tools, trader list, and strategy signal list after those density passes.

## Visual Reference

### Design mock (proposal surface)

| File | Role | SHA-256 | Size |
| --- | --- | --- | --- |
| [`./mock.html`](./mock.html) | Self-contained current-vs-proposal toggle; default = confirmed proposal (`opt001=fixed`, `opt002=none`) | `f2386dbd46aff8c472d635aa3c53f2071ca4e2f22d6d053ffa366abf8981ce46` | 38,036 bytes |

Open the mock in a browser. Paths are relative to this record. Mock K-line data is synthetic; not live app output.

### OPT-001 — sidebar stack no gap (live friction)

- [`./screenshots/2026-07-21-review-sidebar-stack-no-gap.png`](./screenshots/2026-07-21-review-sidebar-stack-no-gap.png)
- SHA-256: `e7846e060f3f7f5049dd92edc512de39f939dab11670cfc4ac0667d969020d37`
- Size: 101,372 bytes
- Fixture: SPY Review sidebar — Trade tools, Tang trader card, and strategy detail cards (e.g. 普通 PUT 启动观察流程) stacked with no breathing room.

### OPT-002 — blue selection band (live friction)

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
  - Stable, visible vertical separation (≈20px) between those three stacks on **Review and Static**, with small section captions (交易者 · Trades / 策略讲解 · Signals) and hairline dividers on the latter two.
  - Trader filter row deduped (mock 2026-07-21): a single `Traders` label + chips; the `TRADE TOOLS` panel title and the Download button are removed.
  - Keep recent card density / type scale; do not undo information content.
- Boundary that must not change:
  - Progressive date rules; trade payload shape; strategy assemble pipeline; App shell left nav.
  - Filter/export semantics stay unchanged, **except** the visible Download entry in this stack, which the user asked to remove (mock 2026-07-21). Its final disposition — removed outright vs relocated (e.g. into the Review 工具 menu) — is **open for implementation review**.
- Lifecycle status: recorded

## OPT-002 Trader Select Blue K-line Band Overlay Is Too Loud

- Source evidence: blue-band screenshot above; user 2026-07-21 live acceptance after click-locate on left trader.
- Current friction:
  - Selecting a trader group correctly locates the chart to the trade point, but a **semi-transparent blue vertical band** cloaks the K bars around the span.
  - The band is the dominant visual and reads as a dirty overlay rather than a subtle focus cue.
- Desired outcome:
  - Preserve fast point location / focus after left-side trader select.
  - **Remove the blue band entirely, with no replacement cue** (mock decision 2026-07-21: the trade point is already identified by the marker label `display_name` + BUY/SELL, so no extra highlight is needed); do not paint any overlay over the chart.
  - **Review and Static** stay aligned.
- Boundary that must not change:
  - Marker labels (display_name + BUY/SELL); trade data; group-select focus target; timeframe/viewport contracts beyond the highlight chrome; no provider/DB/content mutation.
- Lifecycle status: recorded

## Record Closeout (2026-07-21)

- Intake complete for OPT-001 and OPT-002; mock decisions folded into Scope Lock, Desired outcome, and index.
- Independent re-check after mock foldback: content aligned (pass); residual process items closed by committing `mock.html` + revised record + index.
- Untracked `output/playwright/mock-*.png` trees are informal mock captures only — **not** batch evidence; do not stage.
- Status remains `recorded` for both OPTs. Next lifecycle step requires an **explicit user request** in a new session to draft a proposed plan from this batch (OPT-001 + OPT-002). That request is not granted by this closeout.

## Explicit Non-Authorization

This batch does **not** authorize:

- source-code implementation;
- proposed plan drafting (needs a separate user request in a later session);
- activation, push, PR, merge, Pages, provider/broker, or any remote action.
