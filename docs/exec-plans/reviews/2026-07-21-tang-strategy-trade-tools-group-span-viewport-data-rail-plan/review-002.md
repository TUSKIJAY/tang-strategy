# 交付物评审意见

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-tools-group-span-viewport-data-rail-r2`
- Plan author ID: `grok-plan-author-2026-07-21-trade-tools-group-span-viewport-data-rail`
- Independence declaration: `attested`
- Evidence method: `Independent inspection of review-001, exact v2 plan, OPT source, all six visual-evidence files, live shared filter/list/availability/export consumers, Review/Static group selection, event timeline helpers, K-line timeframe/viewport/highlight rendering, Data/Review rail composition and CSS, and lifecycle surfaces. All six evidence SHA-256 values matched. Pre-reconciliation exact reviewed plan SHA-256: 513e44fe5cac5314a1907eaf832ded0b26dc45be0cef592c55262ce0bafa737b. Repository HEAD: 156df37d9f6b1f972f9c748e237412d1a4db7dba.`
- Verdict: revise
- Confidence: high

**审核对象**: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md` exact revision `v2-review-foldback-2026-07-21`

## 整体判断

**裁决**: revise

**置信度**: high

## 总体评价

V2 已完成 `review-001` 的两项核心设计收口。共享 Trade tools 路径被锁定为 display-only, 遗留的 omitted / `reported` / `calculated` 输入不得放大 list, availability 或 export 集合。交易组选择也已锁定为全事件索引聚合, `blue` multi-bar band, 单次 `fitRange`, 以及禁止后续居中操作覆盖拟合视口。实时渲染源证明 `blue` 会绘制实体多柱带, 不是 `marker` / `olive` 的顶部点。

V2 仍未将全部 `review-001` 查找项收口为唯一可执行合同。时间周期首帧 carrier 没有固定可判定的 oracle, 必须执行的 event-row 浏览器验证在 carrier 矩阵中又被标成 optional, Data rail 则同时允许延后改名且未覆盖原始问题中的 month bar 拉伸。这些缺口会让实现在未证明首帧正确, 未接通 event-row focus, 或仍保留宽屏 month bar 的情况下通过现有文字门禁。

## 审核范围

- `review-001` 四项 finding 与 V2 closure map 的逐项对照
- Review, Static, Admin 的 list, availability, filter state 与四文件 export 路径
- Review / Static `selectTradeGroup`, 组时间范围, 事件映射, band 样式, `fitRange` 与居中路径
- K-line `setTimeframe`, 视口计数, `zoomScale`, `followMode`, render scheduling 与 highlight 绘制
- Data `DashboardPage` 宿主组合, 共享 progressive rail 和 Review sidebar CSS cascade
- 证据 SHA-256, Proposed lifecycle metadata, indexes 与权限边界

## 问题清单

### 严重问题

1. **首帧视口 carrier 缺少确定性 oracle**
   - 位置: §1.2 TF closure, §1.5 OPT-004 carrier, §2.2 criterion 4, §2.4 `B-TF-first-paint`, Phase 0 WU-C
   - 问题描述: V2 已选定必须的浏览器 carrier, 但其成功判据仍是 viewport metrics “sane” 和“没有只能通过 wheel 修复的左挤右空”。计划未锁定精确 ticker/day, 初始可视窗口, 首个已完成 engine render 的观测边界, 两个方向的期望 `start` / `end` / `count` / `zoomScale` / `followMode`, 也没有锁定左右空槽或 slot occupancy 阈值。不同实现可以对“sane”做不同解释, 屏幕图 V4 又被正确地限定为补充证据, 因此无法弥补该缺口。
   - 影响范围: `setTimeframe` 可以仍在首帧保留错误 `zoomScale` 或 `viewStart`, 而 carrier 只记录后续稳定状态或用主观条件判定通过。
   - 改进建议: 在下一修订中固定唯一 fixture 和初始视口, 将帧边界定义为 timeframe click 后首个完成的 engine `render()`, 并对 1m→5m 与 5m→1m 列出可计算的期望值或公式。必须包含 slot occupancy / 右侧空槽上限和零 wheel 事件断言, 所需的观测 seam 与 tracked runner 路径应在批准前进入 exact manifest。

2. **必须的 event-row focus 在 carrier 矩阵中仍是 optional**
   - 位置: §1.5 OPT-005 event-row focus, §2.2 criteria 8/11, §2.4 `N-Event-focus` 和 `B-Group-span`, §3.1 items 2–5, Phase 1 WU-B
   - 问题描述: 用户锁和 success criterion 将 timeline row click 定义为 required, 但 `B-Group-span` 行明确写着“optional event-row focus step”。`N-Event-focus` 只能证明纯 payload, 不能证明 `TraderTradeList` 的 row callback 已连接到 Review / Static 引擎, 也不能证明单柱聚焦不会替换 card click 的主 span-fit 行为。现有文字允许在跳过真实 row click 的情况下宣告 WU-B 通过。
   - 影响范围: 实现可以交付 timeline 外观和纯函数, 但留下无响应的行点击或错误的全日拟合。
   - 改进建议: 删除 optional 文字, 将 event-row click 固定为必须的 `B-Group-span` 步骤或同一 receipt 中的单独必须 carrier。该步骤应断言指定 event ID, 单柱 highlight start/end, 可见窗口包含且聚焦该柱, 未扩展至全日, 以及随后再次 card click 恢复原 primary span-fit。Review 和 Static 均需证明接线。

### 中等问题

1. **Data host 名称与宽屏 month bar 验收仍未唯一化**
   - 位置: §1.2 Data closure, §1.5 OPT-006 host/CSS locks, §2.2 criterion 9, §2.4 `N-Data-rail-source` / `B-Data-rail-layout`, §3.1 items 8–10
   - 问题描述: 计划的大多数位置固定 `data-market-days-rail`, 但§1.5 仍允许在 Phase 0 “rename once”, 与 exact source carrier 及 manifest 矛盾。同时 `B-Data-rail-layout` 只强制 ticker/mode button 不全宽和 Review sidebar flex 不变。实时 CSS 中 `.date-rail-month-identity { flex: 1; }`, 原始 OPT 也明确把 month navigation 横跨整个 Data card 列为问题。如果实现只将 ticker/mode button 设为内容宽度而不限制整个 progressive rail 或 month bar, 现有计算布局 carrier 仍可通过。
   - 改进建议: 在计划中只保留 `data-market-days-rail` 一个 host 名称, 指定其挂载在 Data `Market days` panel 内的唯一 wrapper, 且所有 Data-only 尺寸规则必须以该 host 为祖先。将整个 progressive rail 或其 ticker, mode, month bar 的可计算 max-width/flex 期望写入 `B-Data-rail-layout`, 同时保留 Review desktop/narrow 中的 `flex-grow: 1` 与实际可用性断言。

### 轻微问题

- None.

## 已验证项

- 六个视觉证据 SHA-256 与计划列值完全一致。
- 评审前 exact v2 计划 SHA-256 为 `513e44fe5cac5314a1907eaf832ded0b26dc45be0cef592c55262ce0bafa737b`, 且当时 HEAD 为 `156df37d9f6b1f972f9c748e237412d1a4db7dba`。
- Display-only authority 的输入集, 消费者范围, export `display_only: true`, 以及 Admin editor eligibility 边界已被 V2 明确锁定。
- Group select 的全组索引, `blue` multi-bar band, 单次 `fitRange`, 禁止后续居中, 单事件行为和 complete-timed `N pts` 定义已被锁定。
- 权限边界仍为评审与直接 lifecycle reconciliation, 不授权 activation, implementation, content/DB, provider/broker, publication, push 或 remote action。

## 未验证项

- 产品实现和运行时验收未执行, 因为它们超出当前设计评审权限。
- TF 切换首帧, event-row focus 接线和 Data month bar 密度无法在 V2 当前 oracle 下被确定性验收; 需先完成本评审的计划修订。

## 裁决理由

V2 的产品方向、display-only 边界、blue band 样式和主要权限隔离是可行的, 不需要推倒重设, 因此不适用 `reject`。但三个遗留缺口都直接影响上一轮 finding 是否真正关闭, 且可以使未达到用户效果的实现通过现有 carrier 文字。所需改动是有界的合同收口, 因此裁决为 `revise` 且置信度为 `high`。下一 gate 为 `plan-revision`; 本评审不激活计划, 不授权任何产品实现或远程操作。
