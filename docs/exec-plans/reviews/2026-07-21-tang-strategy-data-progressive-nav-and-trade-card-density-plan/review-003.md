# 交付物评审意见 — Review 003

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`
- Review target revision: `v3-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-data-nav-trade-density-r3`
- Plan author ID: `codex-plan-author-2026-07-21-data-nav-trade-density`
- Independence declaration: `attested`
- Evidence method: `Revision review against review-002, the v3 plan diff, canonical 2026-07-17 trade content, Review ticker filtering contracts, current frontend source-contract tests, operating-mode rules, and governed harness output.`
- Verdict: revise
- Confidence: high

**审核对象**：2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md（revision `v3-review-foldback-2026-07-21`）

## 整体判断

**裁决**：revise
**置信度**：high

## 总体评价

v3 已按 `review-002` 做了实质性的减法：实施流程压缩为一次基线/实现/验证、一轮独立 implementation review 和 closeout；测试与 build 不再重复运行；截图由六张降为三张；Admin/Static 作用域主要交给 scoped CSS 与合同测试证明；完整执行授权也可以覆盖 closeout。以上三项 `review-002` 结论均已正确闭环，没有重新引入技术范围扩张。

当前仍不能批准，原因集中在一个可执行性错误：计划把三张截图都固定为 SPY `2026-07-17`，同时要求 Review 截图出现 Tang + 沃德哥。仓库 canonical content 显示该日 Tang group 的 underlying 是 SPY，而沃德哥两组 underlying 均为 QQQ；`filterTradeGroups` 和 `deriveAvailableTraders` 都按当前 payload ticker 过滤，因此 SPY Review 不会显示沃德哥。该 fixture 无法按计划完成。

此外，送审草稿曾把 lifecycle 从 v1 升为 v2，导致既有 `review-001` / `review-002` 被错误要求补写 `Review target commit`，并使当前 harness 失败。按照仓库“小型本地 UI 计划走最简有效生命周期”的硬约束，本次只做 review-state reconciliation：v3 保持 `operating-modes-v1`，没有修改方案正文，也没有引入 checkpoint 链。

## 问题清单

### 严重问题

1. **固定截图 fixture 与 ticker 过滤合同冲突**【修订引入】
   - 位置：§1.2 `review-002` closure、§2.3 V2/V3、§4 Phase 0 verification、§5 Focused checks
   - 问题描述：v3 声称 SPY `2026-07-17` 已确认包含 Tang + 沃德哥 groups，并要求同一 SPY Review 截图同时覆盖两者。实际 `content/trades/2026-07-17.json` 中 Tang 是 SPY，沃德哥两组是 QQQ；`filterTradeGroups` 要求 `group.underlying === filters.ticker`，`deriveAvailableTraders` 也以 payload ticker 限定 displayable groups。
   - 影响范围：V2 无法出现沃德哥，V3 也无法用计划所写 fixture 验证沃德哥卡片；Phase 0 的截图 exit gate 因数据条件不可能满足而被永久阻塞。
   - 改进建议：保持三张截图即可，但按真实 ticker 拆分 fixture。例如 V1=Data SPY `2026-07-17` desktop，V2=Review QQQ `2026-07-17` desktop（沃德哥多卡 + expanded），V3=Review SPY `2026-07-17` narrow（Tang，无横向溢出）；或者对调 V2/V3。不要再声称单个 SPY workspace 同时包含两个 ticker 的 groups。

### 中等问题

无。

### 轻微问题

1. **“长 display name 可 wrap”没有现成样本**【遗留未修】
   - 位置：§2.3 V3
   - 问题描述：canonical registry 中 `Tang` 与 `沃德哥` 都不是足以稳定触发换行的长名称；当前固定 fixture 不能证明实际 wrap 分支。
   - 改进建议：对这个小改动不必新增 synthetic fixture。将验收改为“narrow viewport 无横向溢出、现有名称与 meta 可读”，长名称换行可由 CSS 结构/后续回归覆盖。

## 未验证项

- 12px/11px 最终视觉效果：尚未实施，需在修正后的三张截图中验证。
- normal/static build：本轮仅审核 plan 文档，未实施代码；在一次性 Phase 0 exit verification 中运行即可。
- Review QQQ `2026-07-17` 的最终页面投影仍需实施阶段浏览器验证；canonical content 与过滤代码已确认该 fixture 具备两组沃德哥数据。

核查资料覆盖了本轮修订涉及的 lifecycle、fixture 数据、ticker 过滤合同、前端测试载体和验收边界；实际渲染效果属于实施后验证范围。

## 裁决理由

v3 已成功解决 `review-002` 的过度工程化问题，剩余阻断不是流程偏好，而是一个明确且局部的 fixture 事实错误。修正三张截图的 ticker/date 分配并删除无法由现有数据证明的长名称 wrap 要求后，方案即可再次送审；无需增加阶段、截图数量、checkpoint 或其他治理。
