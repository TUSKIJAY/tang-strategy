# Tang Strategy Data Progressive Navigation And Trade Card Density

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan`
- Revision: `v2-review-foldback-2026-07-21`
- Plan author ID: `codex-plan-author-2026-07-21-data-nav-trade-density`
- Design reviews: ../reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/review-001.md@revise@v1-proposal-2026-07-21, ../reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/review-002.md@revise@v2-review-foldback-2026-07-21
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
- Scope authority: review-only; this proposed plan does not authorize implementation, activation, commit, push, data mutation, or remote actions. `review-001` targets only v1; v2 requires a new matching-revision design review before any activation.

## 1. Context And Evidence

### 1.1 Proposal provenance

本计划整合两份 2026-07-21 用户验收反馈的优化记录，提升为一个受治理的 Coding Mode Lane 3 提案：

| 优化记录 | OPT ID | 摩擦点 |
| --- | --- | --- |
| [`2026-07-21-data-page-progressive-date-nav`](../../optimization/2026-07-21-data-page-progressive-date-nav/2026-07-21-data-page-progressive-date-nav.md) | OPT-001 | Data 页面仍使用 exhaustive 月分组日期芯片，而 Review 已切换为 progressive 最近/按月 导航，两页体验不一致 |
| [`2026-07-21-review-trade-panel-type-scale`](../../optimization/2026-07-21-review-trade-panel-type-scale/2026-07-21-review-trade-panel-type-scale.md) | OPT-001 | 现实交易者点位卡片（trader name + CALL/PUT + meta）字号过大，与 Review 左栏其他密度不统一 |

两项优化均为纯前端、CSS/prop 层面的改动，不涉及后端、数据库、内容、API、发布流程或市场数据管线，且彼此无依赖冲突，适合合并为一个计划以减少治理开销。

提案基于 `codex/project-harness@6eee7e3b9993f57c51d710d40fc988eb15b489ce` 的工作树状态起草。`review-001` lifecycle package 记录在 `406f3c401a8478edaf166e22dd88d493f7003862`。

### 1.2 `review-001` foldback closure map

Independent `review-001` returned `revise/high` against frozen revision `v1-proposal-2026-07-21`. Revision `v2-review-foldback-2026-07-21` folds every finding into the operative contract:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | Closeout jumped `proposed/` → `completed/` with no independent implementation review; single-commit wording collapsed implementation / review / closeout | §4 Phases 2–4 and §5 require Active verification → independent implementation review (`accept`) → separately authorized Completed migration; commit/push authority stay separate |
| P1 | Two-file scope omitted contract-test / comment reconciliation; missing `npm run test:trade-records` and static build | §3.1 manifest and §4 Phases 0–2 include `ReviewContextPanel.jsx` (comment-only), `reviewWorkspace.test.js`, `npm run test:trade-records`, normal build, and `VITE_STATIC_REVIEWS=true npm run build:static-reviews` |
| P2 | Global `.trade-*` CSS would change Admin `TraderTradeList` outside OPT scope | §2.2 / §3 / §4 WU-B freeze density overrides under `.dr-sidebar` only; Admin remains on unscoped defaults |
| P2 | 11px/12px and visual exit deferred to subjective judgment; no screenshot matrix | §2.3 freezes exact px/gap/padding tokens and a desktop+narrow Review/Static/Data matrix |
| P3 | Final contract link `../operating-modes.md` was broken | Final link is [`../../operating-modes.md`](../../operating-modes.md) |

`review-001` is append-only v1 evidence and cannot approve v2. Next gate is an independent design review of exact revision `v2-review-foldback-2026-07-21`.

### 1.3 Visual evidence

| 证据 | 位置 | 作用 |
| --- | --- | --- |
| Data 页面 exhaustive 多月芯片轨道 | `docs/optimization/2026-07-21-data-page-progressive-date-nav/screenshots/2026-07-21-data-market-days-exhaustive-rail.png` | 展示当前 Data 页面日期选择使用 exhaustive 模式，所有月份的日期芯片全部平铺 |
| Tang 点位卡片字号过大 | `docs/optimization/2026-07-21-review-trade-panel-type-scale/screenshots/2026-07-21-review-trade-panel-tang-large-type.png` | Tang CALL 卡片标题/meta 与周围 Review 元素对比明显偏大 |
| 沃德哥多点位卡片同样过大 | `docs/optimization/2026-07-21-review-trade-panel-type-scale/screenshots/2026-07-21-review-trade-panel-vordin-large-type.png` | 多交易者场景下列表整体偏粗糙 |

### 1.4 Current repository facts

**Data 页面日期导航：**

- `ReviewContextPanel.jsx` 接受 `dateNavigation` 属性并透传给 `DateRail`。`DateRail` 默认 `dateNavigation='exhaustive'`；当值为 `'progressive'` 时渲染最近/按月交互。
- 文件头注释仍写 “Progressive mode is opt-in via dateNavigation="progressive" (Review only).” — Data 接入 progressive 后必须把该注释改成真实消费者集合。
- `ReviewPage.jsx` 传递 `dateNavigation="progressive"`；`DashboardPage.jsx` **未传递** `dateNavigation`，因此继承 exhaustive。
- `StaticReviewsApp`、`AdminTradersPage`、`TraderPointEditor` 同样未传递，均使用 exhaustive。

**合约测试（必须纳入 manifest）：**

- `frontend/src/features/review/reviewWorkspace.test.js` 当前断言：
  - only `ReviewPage` opts into progressive；`DashboardPage` / Admin / editor / Static 均 `doesNotMatch(/dateNavigation=/)`
  - `.dr-sidebar .trade-record-list { gap: 8px; }`
- Data progressive 与 gap 6px 落地后，这些断言必须同步改写，否则 Phase 1 无法通过 `npm run test:trade-records`。

**交易者点位卡片排版（`frontend/src/styles.css`）：**

- 全局：`.trade-record-list { gap: 10px; }`、`.trade-group-summary { padding: 12px; gap: 10px; }`、`.trade-trader-name` 仅 `font-weight: 700`（继承 ~16px）。
- Sidebar 覆盖：`.dr-sidebar .trade-record-list { gap: 8px; }`、`.dr-sidebar .trade-group-summary { padding: 10px; }`。
- `AdminTradersPage` 渲染同一 `TraderTradeList`，**不在** `.dr-sidebar` 内；因此密度修正必须只写 `.dr-sidebar …` 选择器，避免 Admin 检查列表被顺带改成终端密度。
- Interactive Review 与 Static Review 均使用 `.dr-sidebar`，因此 scoped 选择器覆盖 OPT 记录的 Review + Static parity 范围。

**密度差距（核心问题）：**

| 维度 | `.dr-signal-card` | 当前 `.dr-sidebar` 点位卡 | 目标（冻结） |
| --- | --- | --- | --- |
| 主文字 font-size | 12px | ~16px（继承） | **12px** |
| 辅助文字 font-size | 11px | ~16px / small | **11px** |
| summary padding | 8px | 10px (sidebar) | **6px 8px** |
| 列表 gap | 6px (signal margin) | 8px (sidebar) | **6px** |

### 1.5 Lane 3 classification

两项改动均为前端 UI，但涉及共享组件 `ReviewContextPanel` 的 progressive 消费者集合变更、共享 CSS 级联边界、以及既有 source-contract 测试更新。归类为需 design review 的 Lane 3 计划。无后端、API、DB、内容、market-data、provider/broker、发布或 Git 远程变更。

## 2. Objective And Success Criteria

### 2.1 Objective

让 Data 页面的日期选择体验与 Review 一致（progressive 最近/按月导航），同时将 Review/Static 左栏 **现实交易者点位** 卡片的字号和密度降至与信号卡片/日期芯片同一视觉家族，消除左栏中的排版断层。Admin 点位列表与 Admin/Static DateRail 保持现状，除非后续单独 OPT/计划扩展。

### 2.2 Success criteria

**WU-A Data Progressive DateRail：**

1. `DashboardPage` 向 `ReviewContextPanel` 传递 `dateNavigation="progressive"`。
2. Data 页面默认展示「最近」标签页与最近 12 个市场日芯片；可切换「按月」浏览；行为与 Review progressive 合约一致（初始化选中最新日、按月浏览不因 chip 选择重置 browseMode、切换 ticker 走 workspace 合约）。
3. 共享默认值 `dateNavigation='exhaustive'` 不改变。
4. `AdminTradersPage`、`TraderPointEditor`、`StaticReviewsApp` 保持 exhaustive（不出现 `dateNavigation=` prop）。
5. `ReviewContextPanel.jsx` 顶部注释改为反映真实 opt-in 消费者：至少 **Review + Data**；不得再写 “Review only”。
6. `reviewWorkspace.test.js` 改写 progressive 消费者断言：`ReviewPage` 与 `DashboardPage` 均匹配 `dateNavigation="progressive"`；Admin / editor / Static 仍不得匹配。

**WU-B Trade Card Type Scale（仅 `.dr-sidebar`）：**

7. 下列 **exact** 值写入 `frontend/src/styles.css` 的 `.dr-sidebar` 作用域（可并入既有 sidebar trade 覆盖块）。**禁止**修改未加 `.dr-sidebar` 前缀的全局 `.trade-record-list` / `.trade-group-card` / `.trade-group-summary` / `.trade-trader-name` / `.trade-drilldown-toggle` 字号或 padding，以免 Admin 继承终端密度：

| Selector | Exact property values |
| --- | --- |
| `.dr-sidebar .trade-record-list` | `gap: 6px;` |
| `.dr-sidebar .trade-group-card` | `font-size: 12px;` |
| `.dr-sidebar .trade-group-summary` | `padding: 6px 8px; gap: 8px; font-size: 12px;` |
| `.dr-sidebar .trade-trader-name` | `font-size: 12px; font-weight: 700;` |
| `.dr-sidebar .trade-group-summary small` | `font-size: 11px;` |
| `.dr-sidebar .trade-drilldown-toggle` | `font-size: 11px;` |

8. CALL/PUT 方向颜色 token 不变（`--direction-call: #6F9F7A`、`--direction-put: #E06B66`）。
9. 卡片选中/活跃态、legs/events 展开内容、Eligibility/B chips/Download 合约与语义不变。
10. Interactive Review 与 Static Review（共享 `.dr-sidebar`）自动获得相同密度；Admin `TraderTradeList` 视觉保持当前全局默认。
11. `reviewWorkspace.test.js` 将 `.dr-sidebar .trade-record-list { gap: 8px; }` 断言更新为 `gap: 6px`，并增加至少一条对 `.dr-sidebar .trade-trader-name` / `.dr-sidebar .trade-group-summary` 12px 作用域的 source 合约匹配；不得要求全局未 scoped 选择器出现 12px 字号。

### 2.3 Frozen visual acceptance matrix

Phase 2 必须产生可复现截图（建议目录 `output/playwright/data-nav-trade-density-phase2-<YYYYMMDD>/`，未跟踪产物不得 sweep 进 commit）。对比基线为 §1.3 三张 OPT 截图。

| # | Surface | Viewport | Required coverage |
| --- | --- | --- | --- |
| V1 | Data Market days | desktop `1672x941` | progressive「最近」默认可见；可切换「按月」；不再铺满全部历史月芯片网格 |
| V2 | Review 现实交易者点位 | desktop `1672x941` | Tang 单卡标题/方向/meta 密度；选中态；与 signal/date chrome 无字号断层 |
| V3 | Review 现实交易者点位 | desktop `1672x941` | 沃德哥（或当前 multi-point trader）多卡；至少一个 expanded `Show legs/events` 状态 |
| V4 | Review 现实交易者点位 | narrow `820x1180` | 长 display name 可 wrap、无横向溢出、卡片仍可读 |
| V5 | Static Review 左栏 | desktop `1672x941` | 同一 `.dr-sidebar` 点位卡密度与 interactive 一致（若当日有 trader groups） |
| V6 | Admin traders inspection list | desktop `1672x941` | **负向验收**：Admin 列表**不得**出现本计划的 12px/6px sidebar 密度（保持实现前默认体量） |

实施时不得以“看起来差不多”替代上述矩阵；像素 token 以 §2.2 表为准，不得在实现阶段改回主观 11/12 二选一。

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/pages/DashboardPage.jsx` — add `dateNavigation="progressive"` only.
2. `frontend/src/styles.css` — add/replace **only** the `.dr-sidebar` density rules listed in §2.2 table; no global `button` reset changes.
3. `frontend/src/features/review/ReviewContextPanel.jsx` — comment-only reconciliation of progressive consumer wording (no behavioral default change).
4. `frontend/src/features/review/reviewWorkspace.test.js` — update progressive consumer + density source contracts as in §2.2.

**Lifecycle / evidence (later phases, separate authority):**

5. Optimization records + `docs/optimization/index.md` status/lifecycle links.
6. `PROGRESS.md` / `HANDOFF.md` state blocks.
7. Plan file location + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + roadmap as lifecycle transitions require.
8. Implementation-review packet / evidence under `docs/exec-plans/reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/`.

**Out of manifest / must not change:**

- Backend, API, tracked DB, seed, content, Pages workflow, daily runbook, provider/broker paths.
- `DateRail` / `ReviewContextPanel` default `dateNavigation='exhaustive'`.
- Admin / Static / editor DateRail exhaustive behavior.
- Trade payload / export schema / eligibility / B-chip semantics / direction color tokens.
- Global unscoped `.trade-*` layout used by Admin, except incidental cascade from shared class names that this plan deliberately does **not** restyle.
- Unrelated dirty paths (`.playwright-cli/`, `output/`, etc.).

### 3.2 Behavioral invariants

- `reviewWorkspace.js` day inventory/selection pure helpers unchanged unless a test-only import path already covers them (no production logic change expected).
- `TraderFilters.jsx` B Chip 选择语义不变。
- 图表交易标记着色和交互行为不变。
- 无 `git push`、PR、Pages、远程操作；本文件不授予任何 commit 权限。

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: matching-revision design-review `approve` on `v2-review-foldback-2026-07-21` **and** explicit user activation recording to Active at `phase-0:not-started`, followed by a separate implementation-start instruction.
- Work:
  1. Run `python3 scripts/check-project-harness.py --root . --profile auto`.
  2. Run `cd frontend && npm run test:trade-records`.
  3. Run `cd frontend && npm run build`.
  4. Run `cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews`.
  5. Freeze §3.1 manifest paths present; capture before hashes for the four implementation files; record that Admin CSS remains unscoped defaults.
  6. Optional: capture before screenshots for V1–V6 if not already covered by OPT evidence.
- Verification: harness green; contract tests green; both builds green; manifest exact; no unrelated edits.
- Exit gate: baseline receipt recorded; next gate `phase-1-start`.

### Phase 1 — Implementation (WU-A + WU-B + contracts)

- Entry gate: Phase 0 complete.
- Work:

  **WU-A Data Progressive DateRail：**

  In `DashboardPage.jsx`, add the progressive prop next to the existing `ReviewContextPanel` props:

  ```diff
     <ReviewContextPanel
  +    dateNavigation="progressive"
  ```

  In `ReviewContextPanel.jsx`, update the file-header comment only, for example:

  ```text
  // Progressive mode is opt-in via dateNavigation="progressive"
  // (currently Review + Data; default remains exhaustive for Admin/Static/editor).
  ```

  Do **not** change the default parameter `dateNavigation = 'exhaustive'`.

  **WU-B Trade Card Type Scale：**

  In `frontend/src/styles.css`, within the existing Review sidebar trade overrides region (near current `.dr-sidebar .trade-record-list` / `.trade-group-summary` rules), set exactly the §2.2 selector table. Replace the current sidebar `gap: 8px` / `padding: 10px` overrides with the frozen values. Do not restyle unscoped global trade rules.

  **Contract tests：**

  Update `reviewWorkspace.test.js` so that:

  - progressive opt-in assertions expect **both** Review and Dashboard;
  - Admin / editor / Static still have no `dateNavigation=`;
  - `.dr-sidebar .trade-record-list` expects `gap: 6px`;
  - at least one assertion pins `.dr-sidebar` scoped 12px trader-name / summary density.

- Verification:
  1. `cd frontend && npm run test:trade-records` green.
  2. `cd frontend && npm run build` green.
  3. `cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews` green.
  4. Diff limited to the four implementation files in §3.1.
- Exit gate: implementation complete and contract/build green; next gate `phase-2-start`.

### Phase 2 — Integrated Acceptance

- Entry gate: Phase 1 complete.
- Work:
  1. Local interactive stack verification:
     - Data: progressive 最近/按月；与 Review 行为一致。
     - Review: progressive 不变；点位卡密度符合 §2.2。
     - Admin: DateRail exhaustive；点位列表**保持**默认体量（V6）。
     - Static: DateRail exhaustive；`.dr-sidebar` 点位卡密度与 Review 一致（V5）。
  2. Capture V1–V6 screenshot matrix from §2.3; note console errors must be zero on exercised paths.
  3. Re-run harness auto profile + both builds + `npm run test:trade-records`.
  4. Write phase evidence under `docs/exec-plans/reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/evidence/`.
- Verification: matrix complete; contracts/builds/harness green; no DB/content/workflow drift.
- Exit gate: acceptance receipt recorded; next gate `implementation-review-packet`.

### Phase 3 — Independent Implementation Review

- Entry gate: Phase 2 complete; implementation-review packet frozen (manifest hashes, commands, evidence paths, authority boundary).
- Work:
  1. Package exact review target (implementation commit or frozen digest + paths) in `implementation-review-packet-001.md`.
  2. Obtain independent `implementation-review-001` with verdict `accept` / `revise` / `reject`.
  3. If `revise`, open a remediation work unit; do **not** migrate to Completed.
- Verification: matching independent `accept` on the frozen implementation target.
- Exit gate: `Implementation review` metadata records `…/implementation-review-001.md@accept`; next gate `completed-migration` **only after separate user authority**.

### Phase 4 — Completed Migration (separately authorized)

- Entry gate: Phase 3 `accept` **and** a new explicit user instruction authorizing completed-migration lifecycle edits (implementation-start / phase authority does **not** imply this).
- Work:
  1. Move plan file from `active/` → `completed/` (source of truth after activation is `active/`, never jump from `proposed/`).
  2. Reconcile proposed/active/completed/reviews indexes, roadmap, and the two state blocks.
  3. Mark both optimization batches `completed` with lifecycle link to this plan; update `docs/optimization/index.md`.
  4. Record `Final disposition: Completed`, verified implementation commit, and any lifecycle reconciliation commit per operating-modes rules.
- Verification: indexes/state blocks consistent; harness/operating-modes checks green for Completed invariants.
- Exit gate: next gate `closed`.

**Authority split (normative):**

| Action | Authority required |
| --- | --- |
| Design review of v2 | independent reviewer; no activation |
| Activation recording | explicit user activate instruction |
| Phase 0–3 implementation & verification | explicit implementation-start after Active |
| Local scoped commits (if any) | separate Git/checkpoint authority; never implied |
| Push / PR / merge / Pages / data / remote | never granted by this plan text |
| Completed migration | separate explicit user instruction after implementation-review `accept` |

## 5. Evidence And Commit Plan

- Baseline / per-phase commands (all required where listed in phases):
  - `python3 scripts/check-project-harness.py --root . --profile auto`
  - `cd frontend && npm run test:trade-records`
  - `cd frontend && npm run build`
  - `cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews`
- Focused checks:
  - Interactive Data/Review/Admin/Static progressive vs exhaustive behavior
  - V1–V6 screenshot matrix against OPT baselines
- Expected state/handoff updates:
  - `PROGRESS.md` / `HANDOFF.md` at each lifecycle transition
  - Optimization records at Completed migration only
- Commit boundaries (if/when separately authorized):
  - Implementation-phase commit(s): only the four §3.1 implementation files (+ phase evidence if required by standing checkpoint rules)
  - Implementation-review / remediation commits: review packet + remediation only
  - Completed-migration commit: lifecycle indexes/state/OPT status only after `accept` + migration authority
  - **Forbidden:** one commit that collapses product implementation + independent review verdict + Completed migration
  - **Forbidden:** push/PR/Pages from any phase of this plan without new remote authority

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan/`
- Append-only v1 evidence: `review-001.md@revise@v1-proposal-2026-07-21`
- Required next design verdict: independent `approve` on exact revision `v2-review-foldback-2026-07-21` (as `review-002` or later)
- Required user approval for activation: yes — matching-revision approve does **not** activate
- Activation is a separate lifecycle change: Proposed → Active at `phase-0:not-started` only
- Implementation start requires a later explicit start/execute instruction after activation recording
- Completed migration requires implementation-review `accept` **and** a further explicit user instruction

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
