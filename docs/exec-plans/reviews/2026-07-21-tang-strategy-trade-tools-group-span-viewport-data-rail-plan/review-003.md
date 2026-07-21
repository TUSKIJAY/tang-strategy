# 交付物评审意见

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md`
- Review target revision: `v3-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-tools-group-span-viewport-data-rail-r3`
- Plan author ID: `grok-plan-author-2026-07-21-trade-tools-group-span-viewport-data-rail`
- Independence declaration: `attested`
- Evidence method: `Independent inspection of review-001, review-002, the exact v3 plan, all six visual-evidence files with recomputed SHA-256 values, live K-line timeframe/viewport/render/highlight sources, Review and Static group-selection paths, event-list composition, Data and Review rail composition/CSS, the canonical QQQ 2026-07-17 multi-event fixture, frontend test/dependency surfaces, and lifecycle checks. All six listed evidence SHA-256 values matched. Pre-reconciliation exact reviewed plan SHA-256: 14dfeba9f9c4d123aa3fa26fdf1d7c488944929bc8cc291853d1739af42b34a9. Repository HEAD: b3abc2620f9771b91ba741d261e30e81553c071f.`
- Verdict: approve
- Confidence: high

**审核对象**: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md` exact revision `v3-review-foldback-2026-07-21`

## 整体判断

**裁决**: approve

**置信度**: high

## 总体评价

V3 将 `review-002` 的三个遗留项全部收口为唯一、可执行的合同。时间周期首帧 carrier 固定 QQQ `2026-07-17`、Interactive Review、桌面 `1672x941`、1m 默认起点、点击后的首个完成 `render()` 和零 wheel/pinch/keyboard zoom, 并以实时 viewport 方法可计算 `count`、`start`、右侧 occupancy 和 `followMode`, 不再允许主观的 “sane viewport” 或截图替代。

交易组路径将 timeline event-row click、单柱 focus、非全日视口和 card re-click 恢复整组 span-fit 写入同一个强制 browser receipt, 且要求 Review 与 Static 同时通过。Data 路径只允许精确宿主 `data-market-days-rail`, progressive rail、ticker、mode、month bar/identity 均受 `420px` 上限约束, 同时保留 Review `.dr-sidebar` 的桌面 flex 行为和窄屏可用性。此前 display-only、blue band、单次 `fitRange` 和禁止 post-fit recenter 的合同均未回退。

## 问题清单

### 严重问题

- None.

### 中等问题

- None.

### 轻微问题

- None.

## 已验证项

- `review-002` 的 TF finding 已关闭: `zoomScale` 固定重置为 `1`; `count` 由 destination `getWindowBarCount(chartWidth, timeframe)` 经 `getViewLimits` clamp 得出; `start` 固定为 previous visible start 按时间映射后 clamp 到 `[0, maxStart]`; 右侧空槽不超过一个目标 slot; `followMode === (start >= maxStart)`. `getViewportDebug()` 和 tracked runner 路径均进入 exact manifest, 两个切换方向均为强制步骤。
- `review-002` 的 event-row finding 已关闭: `B-Group-span` 不含 optional/fallback 文字, 顺序固定为整组 span select、命名 event row 单柱 focus、同 card 恢复 primary span-fit, 并覆盖 Review、Static 和 single-event 路径。
- `review-002` 的 Data finding 已关闭: host 名称不可改, wrapper 挂载位置唯一, Data-only CSS 必须位于该祖先下, `B-Data-rail-layout` 明确覆盖 ticker、mode、month bar/identity 和整个 progressive rail 的 `420px` 上限, 并验证 Review desktop/narrow 不回归。
- 六份视觉证据的 SHA-256 与计划列值一致。Canonical QQQ `2026-07-17` 含两个真实多事件 `vordin` group, 其中一个包含六个完整时间事件, 可执行整组与命名 event-row carrier。
- 实时源与计划问题陈述一致: 当前 TF 切换保留旧 zoom state, group select 在 `fitRange` 后执行 center scroll, `blue` 绘制实体 band, Data month identity 使用 `flex: 1`. V3 的修改 manifest 覆盖对应 frontend、engine、CSS、page、test 和 tracked runner 路径。
- Matching-revision approval 仍与 activation、implementation、content/DB、provider/broker、publication、push 和 remote action 分离。

## 未验证项

- 产品实现、运行时 browser receipt、构建和视觉验收尚未执行, 因为它们属于后续 activation 与 implementation 权限。Phase 1 必须实际通过全部 `N-*`、`B-*` 和 V1-V6 carrier 才能退出。

## 裁决理由

Exact revision `v3-review-foldback-2026-07-21` 已将 prior findings 转换为固定输入、确定公式、明确观察边界、强制交互顺序和精确 CSS 宿主约束。每项需要运行时证明的 claim 都有 mandatory `B-*` carrier, source/pure claim 则有对应 `N-*` carrier, 且缺失任一 browser receipt 会阻止 Phase 1 exit。方案可执行、验证边界闭合、权限范围保持不变, 因此裁决为 `approve` 且置信度为 `high`。下一 gate 为 `activation-recording`; 本评审不激活计划, 不授权产品实现或远程操作。
