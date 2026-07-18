# 交付物评审意见

**审核对象**: 2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md

## 整体判断

**裁决**: approve
**置信度**: high

## 总体评价

修订后的方案已经补齐首次评审识别出的数据库安全缺口. Recovery 和 rebuild 现在共用同一套 consistent snapshot/promotion protocol: 在 shared repository DB write lock 下通过 SQLite backup API 建立基线, 记录路径 identity、主文件摘要和完整逻辑摘要, 候选工作结束后重新持锁核对 live DB, 任一漂移均拒绝晋升并保留新写入. `os.replace` 只在锁内执行, candidate/source verification connections、sidecars、same-filesystem 和 flush 条件也被纳入协议. 该设计消除了旧快照覆盖候选验证期间新状态的主要风险.

Rebuild 的 fail-closed 条件也不再局限于日期集合 superset. 方案要求 discovered files、logical keys、imported keys 和 candidate day count 一致, 对每个日期验证非空 1m/5m bars、声明计数、实际计数、索引和外键, 并独立保护 strategy slug 与 teaching key 集合. Intentional date-loss override 只放宽日期集合, 不绕过语义完整性和非市场表保护. 对 empty bars、count mismatch、non-market shrink 和 concurrent drift 的隔离测试已写入 phase gate 与 validation matrix.

规范化 digest 已固定列投影、排序、JSON 编码、`NULL`、有限浮点和 ID 排除规则; 15 项 governed surface 也已逐路径列明. Plan 审核术语统一为 `approve`. SPA/static Pages 区分、docs 删除前置、远端权限边界和无关死代码排除继续保持原有正确范围. 新增 writer lock 只覆盖防止 DB 晋升竞态所需的 repository-managed 写入口, 属于数据安全修复的必要组成, 未扩张到未授权发布、broker 或远端状态变更.

## 问题清单

### 严重问题

无.

### 中等问题

无.

### 轻微问题

无阻止执行的问题. 实现时应保持 plan 已规定的顺序: candidate 文件先 flush, `os.replace` 后再 flush parent directory, post-promotion verification 失败时在同一 shared write lock 下恢复 verified backup.

## 未验证项

- Shared write-lock 实现: 方案可执行, 但具体实现尚未产生. 应验证 startup migration、market/strategy/teaching import、fetch-triggered import 和 rebuild promotion 均经过同一锁, 并避免 nested importer 调用造成自锁或死锁.
- Consistent snapshot 与 drift token: 需要隔离测试证明 WAL/journal 状态处理、连接关闭和 live DB 二次 identity/digest 核对均发生在替换前, 且 concurrent writer case 保留新写入.
- Semantic candidate gates: 需要实际测试 empty/non-list bars、count mismatch、duplicate logical key、strategy/teaching shrink、non-finite values 和 foreign-key failure 均返回非零且原 DB 字节不变.
- 三日恢复证据: 需要 Phase 1 使用统一 digest 实现验证原 43 天不变, 三个恢复日与历史来源一致, 晋升前后 integrity 和 overlay/export reachability 通过.
- 最终 runtime/frontend/docs 验证: 2026-07-17 assemble、06-30/07-01 overlay、Review/Backtest 回归、legacy docs consumer 复核和 governed workflow contract 均需在实施后按矩阵记录结果.

## 裁决理由

首次评审的两项严重 finding 已分别通过 shared lock + consistent snapshot + pre-promotion drift token, 以及 market/non-market semantic completeness gates 解决. 两项中等 finding 已通过 exact digest contract 和 15-path governed checklist 解决, 激活术语也已统一. 修订内容给出了明确失败条件、锁内晋升边界、隔离测试和 rollback 行为, 可以指导实现并验证是否真正 fail closed. 剩余事项均属于方案已明确覆盖的实施与验证工作, 可在执行阶段按 gate 自然完成, 不再构成重新修订方案的条件, 因此裁决为 `approve`.
