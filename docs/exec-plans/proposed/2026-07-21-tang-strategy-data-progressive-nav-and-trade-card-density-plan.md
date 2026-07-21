# Tang Strategy Data Progressive Navigation And Trade Card Density

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan`
- Revision: `v1-proposal-2026-07-21`
- Plan author ID: `codex-plan-author-2026-07-21-data-nav-trade-density`
- Design reviews: `../reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/review-001.md@revise@v1-proposal-2026-07-21`
- Latest design verdict: revise
- Review independence: attested
- Activation evidence: none
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: `plan-revision`
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Owner: Codex
- Created: 2026-07-21
- Optimization source: `docs/optimization/2026-07-21-data-page-progressive-date-nav/2026-07-21-data-page-progressive-date-nav.md`, `docs/optimization/2026-07-21-review-trade-panel-type-scale/2026-07-21-review-trade-panel-type-scale.md`
- Proposal baseline: `codex/project-harness@6eee7e3b9993f57c51d710d40fc988eb15b489ce`
- Scope authority: review-only; this proposed plan does not authorize implementation, commit, push, data mutation, or remote actions

## 1. Context And Evidence

### 1.1 Proposal provenance

本计划整合两份 2026-07-21 用户验收反馈的优化记录，提升为一个受治理的 Coding Mode Lane 3 提案：

| 优化记录 | OPT ID | 摩擦点 |
| --- | --- | --- |
| [`2026-07-21-data-page-progressive-date-nav`](../../optimization/2026-07-21-data-page-progressive-date-nav/2026-07-21-data-page-progressive-date-nav.md) | OPT-001 | Data 页面仍使用 exhaustive 月分组日期芯片，而 Review 已切换为 progressive 最近/按月 导航，两页体验不一致 |
| [`2026-07-21-review-trade-panel-type-scale`](../../optimization/2026-07-21-review-trade-panel-type-scale/2026-07-21-review-trade-panel-type-scale.md) | OPT-001 | 现实交易者点位卡片（trader name + CALL/PUT + meta）字号过大，与 Review 左栏其他密度不统一 |

两项优化均为纯前端、CSS/prop 层面的改动，不涉及后端、数据库、内容、API、发布流程或市场数据管线，且彼此无依赖冲突，适合合并为一个计划以减少治理开销。

提案基于 `codex/project-harness@6eee7e3b9993f57c51d710d40fc988eb15b489ce` 的工作树状态起草。

### 1.2 Visual evidence

| 证据 | 位置 | 作用 |
| --- | --- | --- |
| Data 页面 exhaustive 多月芯片轨道 | `docs/optimization/2026-07-21-data-page-progressive-date-nav/screenshots/2026-07-21-data-market-days-exhaustive-rail.png` | 展示当前 Data 页面日期选择使用 exhaustive 模式，所有月份的日期芯片全部平铺 |
| Tang 点位卡片字号过大 | `docs/optimization/2026-07-21-review-trade-panel-type-scale/screenshots/2026-07-21-review-trade-panel-tang-large-type.png` | Tang CALL 卡片标题/meta 与周围 Review 元素对比明显偏大 |
| 沃德哥多点位卡片同样过大 | `docs/optimization/2026-07-21-review-trade-panel-type-scale/screenshots/2026-07-21-review-trade-panel-vordin-large-type.png` | 多交易者场景下列表整体偏粗糙 |

### 1.3 Current repository facts

**Data 页面日期导航：**

- `ReviewContextPanel.jsx` 接受 `dateNavigation` 属性并透传给 `DateRail`。`DateRail` 默认 `dateNavigation='exhaustive'`（L36–42）；当值为 `'progressive'` 时渲染最近/按月交互（L99–185）。
- `ReviewPage.jsx` 传递 `dateNavigation="progressive"`（L516），Review 页面已是 progressive 模式。
- `DashboardPage.jsx` **未传递** `dateNavigation`（L93–98），因此继承了 exhaustive 默认值。
- 其他消费者（`StaticReviewsApp`、`AdminTradersPage`）同样未传递，均使用 exhaustive。

**交易者点位卡片排版（`frontend/src/styles.css`）：**

- `.trade-group-summary` 的 padding 为 `12px`（sidebar 下覆盖为 `10px`，L1323/1345），无显式 `font-size`，继承 body ~16px。
- `.trade-group-summary` 是一个 `<button>` 元素，受全局 `button { font: inherit; padding: 11px 14px; border-radius: 12px; }` 影响（L28–29）。
- `.trade-trader-name` 仅设置 `font-weight: 700`（L1360），无 `font-size`（继承 ~16px）。
- `.trade-drilldown-toggle` 也是 `<button>`，无显式 `font-size`，继承 body ~16px，padding `4px 7px`（L1393–1398）。
- `.trade-event` 使用 `12px ui-monospace…`（L1407），已是紧凑尺寸。
- 对比基准：`.dr-signal-card` 使用 `padding: 8px`、`.dr-signal-title` `font-size: 12px`、`.dr-signal-time`/`.dr-signal-meta` `font-size: 11px`、`.dr-signal-dir` `font-size: 10px`。

**密度差距（核心问题）：**

| 维度 | `.dr-signal-card` | `.trade-group-card` | 差距 |
| --- | --- | --- | --- |
| 主文字 font-size | 12px | ~16px（继承） | **+4px** |
| 辅助文字 font-size | 11px | ~16px / small | **+5px** |
| 卡片 padding | 8px | 12px（sidebar 10px） | +2–4px |
| 卡片间距 | 6px | 10px（sidebar 8px） | +2–4px |
| border-radius | 4px | 0px（button 继承 12px） | 不匹配 |

### 1.4 Lane 3 classification

两项改动均为前端 UI，但涉及共享组件 `ReviewContextPanel`（被多页面引用）的 DateRail 行为变更，以及影响 Review 核心交易面板的 CSS 密度调整。虽然代码量小，但改动影响面跨多个消费者和核心交互流程，归类为需 review 的 Lane 3 计划。无后端、API、DB、内容、market-data、provider/broker、发布或 Git 远程变更。

## 2. Objective And Success Criteria

### 2.1 Objective

让 Data 页面的日期选择体验与 Review 一致（progressive 最近/按月导航），同时将 Review 交易者点位卡片的字号和密度降至与信号卡片/日期芯片同一视觉家族，消除左栏中的排版断层。

### 2.2 Success criteria

**WU-A Data Progressive DateRail：**

1. Data 页面 (`DashboardPage`) 的日期选择使用 progressive 模式：默认展示「最近」标签页，展示最近 12 个市场日芯片；可切换至「按月」浏览。
2. 交互行为与 Review 页面完全一致：初始化选中最新日，按月浏览不改变已选日，切换 ticker 走 workspace 合约。
3. 其他 DateRail 消费者（`AdminTradersPage`、`TraderPointEditor`、`StaticReviewsApp`）保持 exhaustive 不变。
4. 共享默认值 `dateNavigation='exhaustive'` 不改变。

**WU-B Trade Card Type Scale：**

5. `.trade-group-card` 及其子元素（`.trade-group-summary`、`.trade-trader-name`、`.trade-drilldown-toggle`）设置显式 `font-size`（~11–12px），不再继承 body 16px。
6. `.trade-group-summary` padding 从 `12px`/`10px` 缩至 `8px`/`6px 8px`，与 signal-card 的 `8px` 对齐。
7. `.trade-drilldown-toggle`（Show legs/events）使用相同紧凑排版。
8. 卡片间距（`.trade-record-list` gap）从 `10px`/`8px` 缩至 `6px`，匹配 signal-card `margin-bottom: 6px`。
9. CALL/PUT 方向颜色不变。
10. 卡片选中/活跃态、legs/events 展开内容、导出/过滤合约不受影响。
11. Static Review 如果共用同一 CSS 则自动获得相同密度修正。

## 3. Constraints And Invariants

- 已有行为不得改变：
  - Tracked SQLite DB / seed / content 合约
  - Pages publisher、daily runbook、provider/broker 路径
  - Admin/Static DateRail 保持 exhaustive（除非后续计划单独扩展）
  - 导出 schema（trade payload / export / `trader_ids` 排序）
  - 交易者可见性 / eligibility 语义
  - CALL/PUT 方向色 token
  - 全局 `button` 基础样式不改（改动限定在 `.trade-group-*` / `.dr-sidebar` 选择器下）

- 安全/数据/兼容边界：
  - 无后端、API、DB、内容变更
  - 无 `git push`、PR、Pages、远程操作
  - 不修改 `dateNavigation` 在 `DateRail`/`ReviewContextPanel` 中的默认值

- 保持不变的路径：
  - `reviewWorkspace.js` 的 day inventory/selection 逻辑
  - `TraderFilters.jsx` 的 B Chip 选择语义
  - 图表交易标记着色和交互行为

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: 计划经 design-review 通过并由用户批准激活
- Work:
  1. 运行 `python3 scripts/check-project-harness.py --root . --profile auto` 确认 harness 绿灯
  2. `cd frontend && npm run build` 确认前端可构建
  3. 确认改动范围仅限下列文件：
     - `frontend/src/pages/DashboardPage.jsx`（一行 prop 添加）
     - `frontend/src/styles.css`（trade-group 密度 CSS 调整，限定在 `.trade-group-*` / `.dr-sidebar` 选择器下）
- Verification: harness 绿灯、前端构建成功、无 unrelated 改动
- Exit gate: 基线确认完成，范围冻结

### Phase 1 — Implementation

- Entry gate: Phase 0 退出门通过
- Work:

  **WU-A Data Progressive DateRail（1 行改动）：**

  在 `DashboardPage.jsx` 中向 `<ReviewContextPanel>` 添加 `dateNavigation="progressive"` prop，位置在 L93–98 已有 props 附近：

  ```diff
     <ReviewContextPanel
  +    dateNavigation="progressive"
  ```

  无需修改 `DateRail.jsx`、`ReviewContextPanel.jsx`、`reviewWorkspace.js` 或任何其他文件。共享组件已完整支持 progressive 模式。

  **WU-B Trade Card Type Scale（CSS 调整，在 `frontend/src/styles.css` 中）：**

  在已有的 `.dr-sidebar` 和 `.trade-group-*` 选择器区域调整排版密度，不改动全局 `button` reset：

  ```css
  /* ── 紧凑化交易者点位卡片 ── */

  /* 卡片间距：从 10px/8px → 6px */
  .trade-record-list { gap: 6px; }
  .dr-sidebar .trade-record-list { gap: 6px; }

  /* 卡片主体密度 */
  .trade-group-card {
    font-size: 12px;         /* 显式设置，防止继承 body 16px */
  }

  /* Summary button 密度 */
  .trade-group-summary {
    padding: 8px;            /* 从 12px 缩小，匹配 signal-card */
    gap: 8px;                /* 从 10px 缩小 */
  }
  .dr-sidebar .trade-group-summary {
    padding: 6px 8px;        /* sidebar 下进一步紧凑 */
  }

  /* 交易者名称 */
  .trade-trader-name {
    font-weight: 700;
    font-size: 12px;         /* 从继承 ~16px → 12px，匹配 signal-title */
  }

  /* Drilldown toggle (Show legs/events) */
  .trade-drilldown-toggle {
    font-size: 11px;         /* 从继承 ~16px → 11px */
  }
  ```

  > 注意：最终像素值由验收时的视觉效果决定，上述为初始方案。如果 12px trader name 仍偏大，可统一至 11px。`.trade-group-card` 上设置 `font-size: 12px` 使所有子元素默认继承此值，然后按需微调个别元素。

- Verification:
  1. `cd frontend && npm run build` 构建成功
  2. 本地 `npm run dev` 验证：
     - Data 页面：日期选择器显示「最近」标签页，展示最近 12 个市场日芯片；切换「按月」后以月为单位浏览
     - Review 页面：progressive DateRail 行为不变
     - Admin 页面：DateRail 仍为 exhaustive
     - Review 左栏：交易者点位卡片字号与信号卡片/日期芯片视觉统一，无断层
     - CALL/PUT 颜色不变
     - 卡片选中/展开/导出功能正常
  3. harness check 绿灯
- Exit gate: 全部验证通过

### Phase 2 — Closeout

- Entry gate: Phase 1 退出门通过
- Work:
  1. 更新两份优化记录的 Status 为 `completed`，补充 Lifecycle link 指向本计划
  2. 更新 `docs/optimization/index.md` 索引
  3. 更新 `PROGRESS.md` 和 `HANDOFF.md`
  4. 将本计划从 `proposed/` 移至 `completed/`
  5. 更新 `docs/exec-plans/proposed/index.md` 和 `docs/exec-plans/completed/index.md`
- Verification: 所有索引文件一致、无遗留 TODO
- Exit gate: lifecycle 收尾完成

## 5. Evidence And Commit Plan

- Baseline commands:
  - `python3 scripts/check-project-harness.py --root . --profile auto`
  - `cd frontend && npm run build`
- Focused checks:
  - `npm run dev` 本地验证 Data/Review/Admin 三页面日期导航行为
  - 目视对比交易者点位卡片排版与信号卡片密度
- Full checks:
  - `python3 scripts/check-project-harness.py --root . --profile auto`
  - `cd frontend && npm run build`
- Expected state/handoff updates:
  - `PROGRESS.md`: 更新当前工作项
  - `HANDOFF.md`: 更新最新续接点
  - Optimization records: 更新 lifecycle status
- Commit boundaries:
  - 单次 scoped local commit 包含：`DashboardPage.jsx`、`styles.css`、lifecycle 文档
  - 不包含后端、DB、内容、或不相关的用户文件

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/`
- Required verdict: `approve` on revision `v1-proposal-2026-07-21`
- Required user approval: yes — 用户必须明确批准才能从 proposed → active
- Activation is a separate lifecycle change before implementation.
- Implementation start requires a later explicit start/execute instruction after activation recording.

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
