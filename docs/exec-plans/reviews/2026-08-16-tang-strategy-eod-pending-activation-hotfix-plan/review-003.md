# 交付物评审意见

- Review target: `docs/exec-plans/active/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`
- Review target revision: `v3-active-amendment-2026-08-16`
- Review target commit: `e836233d00077dace91158a2b4863fa28883ad0a`
- Review type: design
- Reviewer ID: `codex-design-review-01a00adc`
- Plan author ID: `codex-root-01a00adc`
- Independence declaration: attested
- Evidence method: 核对 runtime enable receipt 的 runner commit/tree 绑定、config-only descendant 验证、cron 生产声明与 v3 修订的操作顺序
- Verdict: approve
- Confidence: high

**审核对象**: `2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`

## 整体判断

**裁决**: approve

**置信度**: high

## 总体评价

V3 amendment 正确处理了新 runner 代码与现有生产授权绑定的冲突. 当前 runtime 不只比对 enable receipt 中的 `runner_commit` 和 `runner_sha256`, 还要求工作区 HEAD 是该 code commit 之后唯一的 `config/deployment.json` commit. 因此, 先形成经实施评审的 runner code commit, 再生成唯一 hash-only config descendant, 是与现有验证器相符的部署形状.

修订把 cron 禁用放在外部 receipt 替换和 config hash commit 之前, 避免调度任务在 receipt/config 短暂不匹配期间启动. 新 receipt 仅改 `runner_commit`、`runner_sha256`、`recorded_at`, 保留原有的生产边界、决策卡、阶段证据、job 和 channel 字段. 最终先恢复并精确核对原 cron 声明, 再运行 runtime authority 验证和 circuit recovery, 能保证任一中间门设失败时不进入 capture 或 Discord 日报发送.

## 问题清单

### 严重问题

- 无.

### 中等问题

- 无.

### 轻微问题

1. **收据字段保留比较应作为机器门设**
   - 位置: Phase 3 和第 8 节.
   - 改进建议: 在覆写 external receipt 前对 old/new 对象做排除 `runner_commit`、`runner_sha256`、`recorded_at` 后的 canonical 字节比较, 并在 config commit 前验证新 receipt 文件 hash 等于将写入 `enable_receipt_sha256` 的值. 该要求是 v3 已声明的"其余字段字节相同"和 hash-only commit 的直接验收形式, 不需要再次修订方案.

## 未验证项

- 新 runner code commit 和 tree digest: 尚未形成已评审 commit. -- 实施评审后计算 `code_tree_sha256`, 并将精确 40-hex commit 和 64-hex digest 写入替换 receipt.
- Cron 禁用与恢复 readback: 尚未执行远程状态变更. -- 保存启用态 normalized spec, 禁用后要求仅 `enabled=false`, 最终要求完整 spec 与基线相同且 `enabled=true`.
- Runtime production evidence: 需等 config-only descendant 形成且 cron 恢复后才可验证. -- 在 circuit reset 前运行完整 runtime authority readback; 任一 receipt hash、tree digest、commit count、path partition 或 cron 字段不匹配即停止.

## 裁决理由

拟议顺序为: 经独立实施评审的 runner code commit -> 禁用并核对固定 cron -> 只替换三个允许字段的 enable receipt -> 仅更新 receipt hash 的唯一 config descendant commit -> 恢复并核对完全相同的 cron -> 验证 runtime production evidence -> circuit reset -> 带 expected renderer SHA 的事务恢复. 该顺序满足现有 code-tree 和 config-only descendant 绑定, 并在任何不可逆的 Discord 日报前保持 fail closed. 计划还明确了任一禁用态读回、receipt 字段保留、config 路径分区、runtime authority 或最终 cron 读回失败时不进入后续恢复. 未发现需要在实施前修订的阻断问题, 因此裁决为 approve.
