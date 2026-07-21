# 交付物评审意见 — Review 002

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-data-nav-trade-density-r2`
- Plan author ID: `codex-plan-author-2026-07-21-data-nav-trade-density`
- Independence declaration: `attested`
- Evidence method: `Revision review against review-001, the current plan diff, linked OPT evidence, relevant frontend consumers and source-contract tests, operating-mode rules, governed harness output, and the user's explicit small-project efficiency boundary.`
- Verdict: revise
- Confidence: high

**审核对象**：2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md（revision `v2-review-foldback-2026-07-21`）

## 整体判断

**裁决**：revise
**置信度**：high

## 总体评价

v2 已正确关闭 `review-001` 的五项技术问题：生命周期不再从 Proposed 直跳 Completed，四文件 manifest 与现有合同测试吻合，CSS 被限定在 `.dr-sidebar`，像素值不再留给实施阶段主观决定，最终 operating-modes 链接也已修正。当前 49 项前端合同测试、operating-modes 检查、project harness 和 `git diff --check` 均通过，因此方案方向与仓库事实没有新的技术性阻断。

但本轮 foldback 把一个四文件、纯前端、可快速回滚的 UI 调整扩成了三轮重复测试/构建、六张强制截图、四个实施后阶段和额外的 closeout 用户门。这与用户已经明确提出的“小项目不要过度工程化”边界相冲突。另一个未完全闭环点是截图矩阵虽增加了 viewport，却没有冻结可复现的数据日/fixture，且 V5 仍允许在没有 trader groups 时条件性跳过。应先把流程缩回与风险相称的最小闭环，再批准实施。

## 问题清单

### 严重问题

1. **强制验收与生命周期流程超出小型 UI 改动所需**【修订引入】
   - 位置：§2.3、§4 Phase 0–4、§5
   - 问题描述：计划要求 Phase 0、Phase 1、Phase 2 重复运行同一组合同测试和两种 build；Phase 2 强制 V1–V6 六张截图；随后再拆 implementation-review packet、独立实施审和必须另行提示的 Completed migration。技术风险只涉及一处 prop、一组 scoped CSS、一条注释及合同测试，这套流程的固定成本高于改动本身。
   - 影响范围：执行者会反复构建、截图和等待授权，降低小项目迭代效率；同时把“技术正确”错误地等同于“流程越多越安全”。
   - 改进建议：保留独立 design/implementation review，但将实施压缩为“基线一次 → 四文件实现 → 一次 49 项合同测试 + normal/static build + harness → 2–3 张针对性截图 → implementation review → 有效 closeout authority 下收尾”。Admin 不受影响应主要由 scoped CSS diff/合同测试证明，不强制单独拍负向截图。

2. **视觉矩阵仍未形成可复现 fixture**【遗留未修】
   - 位置：§2.3 V2–V5、§4 Phase 2
   - 问题描述：V2/V3 只写 Tang、沃德哥或“当前 multi-point trader”，V4 要求长 display name，但没有指定确定存在这些内容的 ticker/date/fixture；V5 还写成“若当日有 trader groups”。因此同一实现可能因为选择不同日期而缺少卡片、长名称或展开项，仍不能稳定复核 `review-001` 要求的视觉闭环。
   - 影响范围：Phase 2 和独立 implementation review 可能被测试数据偶然性阻塞，或在 V5 条件不满足时带缺口通过。
   - 改进建议：若保留截图，直接固定已有证据日（例如仓库验收基准 SPY `2026-07-17`，先确认该日包含目标 groups），或提供最小稳定 fixture；删除“若当日有”式条件。更轻量的选择是只保留 Data desktop、Review desktop expanded、Review narrow 三张，并用 source-contract 测试覆盖 Static/Admin 作用域。

### 中等问题

1. **Completed migration 被无条件拆成新的用户提示**【修订引入】
   - 位置：§4 Phase 4、Authority split、§6
   - 问题描述：计划规定即使用户已经明确授权“完整执行该 plan 直到收尾”，implementation review `accept` 后仍必须再取得一次新的 completed-migration 指令。需要的是明确 closeout authority，而不是强制每次都追加一轮提示；完整执行授权与仅激活/仅实施授权应区别处理。
   - 改进建议：改为“Completed migration 需要覆盖 closeout 的明确用户授权；仅 activation 或仅 implementation-start 不足。若用户已明确委托完整执行至收尾，则无需重复询问。”Push/PR/Pages 等远程权限继续独立。

### 轻微问题

无。

## 未验证项

- 最终 12px/11px 组合的真实视觉效果：尚未实施，只能在实现后的定向截图中验证。
- Static Review 指定日期是否一定含 trader groups、长 display name 是否存在稳定样本：当前 plan 未固定 fixture。
- 本轮没有运行 normal/static production build，因为工作树只有 plan/lifecycle 文档更新；实施阶段仍需运行一次完整 build 验证。

核查资料覆盖了 plan 中的组件关系、CSS 作用域、合同测试载体、现有截图及 lifecycle 规则；实际实施视觉与运行时 build 属于后续验证范围。

## 裁决理由

v2 的技术设计已经可行，`review-001` 的代码与生命周期缺陷也基本闭环；当前不批准的原因不是要增加更多治理，而是强制流程与明确的小项目效率边界不相称，且截图验收仍缺少稳定 fixture。删减重复门和非必要截图、把 closeout authority 写成可由完整执行授权覆盖，并固定少量可复现验收样本后，即可重新送审。
