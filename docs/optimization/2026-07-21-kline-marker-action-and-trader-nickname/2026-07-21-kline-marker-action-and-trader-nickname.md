# Optimization Batch · 2026-07-21

> Record-only intake. This file does not authorize implementation.
>
> Place this file at:
> `docs/optimization/2026-07-21-kline-marker-action-and-trader-nickname/2026-07-21-kline-marker-action-and-trader-nickname.md`
> Put evidence images in the sibling `screenshots/` folder and link them as `./screenshots/<name>.png`.
>
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. A draft, failed/incomplete record, explicit no-commit instruction, or unclear path ownership prevents that commit. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | K-Line Point Markers: Display Buy/Sell instead of Call/Put | Review / K-Line Chart UI | recorded | none | 箭头与颜色已区分 Call/Put，文本改标 Buy/Sell 显示买卖动作 |
| OPT-002 | Trader Display Name / Nickname Mapping (`vordinkkk` → `vordin`) | Review / Trader Registry | recorded | none | 界面显示英文昵称 `vordinkkk`；DB/registry 仍以 `trader_id: vordin`（沃德哥）保存与映射 |

## Visual Reference

- Live K-line marker screenshot: [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png)
  - Visible labels: `vordin PUT`, `vordin CALL`, `vordin CALL ×2` (green up / red down triangles already encode direction).
  - No BUY/SELL action text; nickname shown as raw `trader_id` (`vordin`) rather than English nickname `vordinkkk`.
- Interactive mockup (current vs proposed): [`mockups/kline-marker-buysell-nickname.html`](./mockups/kline-marker-buysell-nickname.html)
- Live marker label contract today (source): `frontend/src/features/review/tradeRecords.js` builds `marker_label` as `` `${trader_id} ${CALL|PUT}` `` (with optional `×N` aggregation). Direction owns triangle shape + color; action is not shown on the label.

## OPT-001 K-Line Point Markers: Display Buy/Sell Action

- Source evidence: User K-line screenshot [`screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png`](./screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png) plus instruction (2026-07-21): 虽然用不同颜色区分了 call 和 put，但是没有区分 sell 和 buy；K 线展示不要用文字写 call/put（箭头方向和颜色已区分），改写 buy 和 sell，一眼看到该时间点做了什么操作。
- Current friction: Chart point markers currently render text like `vordin CALL` / `vordin PUT` (see screenshot). Option type is already encoded by:
  - **Color** (CALL green / PUT red per direction tokens)
  - **Arrow direction** (up triangle vs down triangle)
  So repeating CALL/PUT in the label wastes the only short text slot and fails to show **buy vs sell** at that timestamp.
- Desired outcome: On the K-line chart marker label, render **BUY** or **SELL** (from event action such as `buy_open` / `sell_close`) instead of CALL/PUT text. Keep shape + color owned by option direction so CALL/PUT remain visually distinct without words.
- Boundary that must not change:
  - Underlying event structures keep both option type (CALL/PUT) and action (buy/sell open/close).
  - Only K-line **point text rendering** (and the pure annotation builder that feeds it) is in scope for this item.
  - Trade **cards** may continue to show CALL/PUT badges unless a separate OPT changes them.
- Lifecycle status: recorded

## OPT-002 Trader Display Name / Nickname Mapping

- Source evidence: Same K-line screenshot shows marker prefixes as raw `vordin` (not `vordinkkk`). User instruction (2026-07-21): 只显示沃德哥的英文昵称 `vordinkkk`，但在数据库保存的时候需要知道沃德哥指向的是他。 Live registry today: `content/traders/index.json` has `trader_id: "vordin"`, `display_name: "沃德哥"`.
- Current friction: Markers (and related UI) use raw `trader_id` `vordin` / Chinese `沃德哥` rather than the preferred English nickname. User wants **`vordinkkk`** on the product surface, while persistence continues to identify the same person as the canonical 沃德哥 / `vordin` record.
- Desired outcome:
  - UI surfaces (at least K-line markers; trader chips/cards as natural follow-through) show **`vordinkkk`**.
  - Save path / DB / registry continue to bind that person to **`trader_id: vordin`** (沃德哥), without inventing a second identity or breaking existing day files keyed by `vordin`.
- Boundary that must not change:
  - Canonical `trader_id` slug format and relational integrity (`vordin`, `tang`, …).
  - Existing historical trade-group rows that already store `trader_id: "vordin"`.
  - Exact registry field shape (reuse `display_name` vs add nickname) is **not frozen here** — plan time decides the minimal mapping mechanism.
- Lifecycle status: recorded
