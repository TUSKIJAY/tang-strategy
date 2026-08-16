# 交付物评审意见

- Review target: `docs/exec-plans/active/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`
- Review target revision: `v3-active-amendment-2026-08-16`
- Review type: implementation
- Reviewer ID: `codex-implementation-reviewer-01a00adc`
- Plan author ID: `codex-root-01a00adc`
- Independence declaration: attested
- Evidence method: 审查 Tang commit `551e9a1ec72a52f4b90f7778fd1bd7193e23d920` 与 runner commit `8c96984a52deaee883a2c8251d9e90f5d62d45db` 的精确 diff, 运行聚焦及全量测试, 并对 2026-08-14 hosted payload 做新旧 annotation 字段级比较
- Verdict: revise
- Confidence: high

**审核对象**: `2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`; implementation commits `551e9a1ec72a52f4b90f7778fd1bd7193e23d920` and `8c96984a52deaee883a2c8251d9e90f5d62d45db`

## 整体判断

**裁决**: revise

**置信度**: high

## 总体评价

Runner 实现与 v3 的 provenance 恢复顺序基本一致. 已完成 `pages_verified` 恢复缺少 expected renderer SHA 时在 `_process_manifest()` 之前停止; 浏览器 capture 用前后 provenance 检查包围 SPY/QQQ; 成功 workflow、data commit/workflow、renderer commit/workflow 和截图 hash 在 delivery 前写入冗余 receipt. 新 CLI 参数为可选项, 所以无恢复事务的固定 cron argv 保持兼容; 对有 `pages_verified` 事务的恢复则必须显式提供 SHA.

2026-08-14 实际基线也符合计划. 对当前 hosted SPY/QQQ 390 根 RTH payload 分别用修改前后 scanner 扫描, 剔除新增 `_activation_observed_bars` 和 `_expiry_kind` 后, SPY 无 added/removed/changed annotation; QQQ 只新增 `expired-6-389`, 即 15:59 的 `session_end` 0/8 outcome, 无既有 annotation 字段变化. 但 scanner 对"有效 probe"的判定尚未完整, 可在必需 MA10 数据缺失时仍计数并收束为 expired. 这与 active plan 的 fail-closed 完整性合同冲突, 需要最小修复后重审.

## 问题清单

### 严重问题

1. **必需 indicator 缺失仍被计为有效 probe 并可触发过期**
   - 位置: `frontend/src/features/review/scanner.js` 的 `completeSessionWindow()`、`activationProbe()` 和 pending 处理分支.
   - 问题描述: `completeSessionWindow()` 只验证 `O/H/L/C`, 但生产 Tang v4.4 Activation Wick 启用 `require_ma10_slope_still_aligned=true`, 因此当前与 lookback bar 的 `m10` 也是 activation probe 必需输入. `activationProbe()` 在 `m10` 缺失时只产生 `slopeOk=false`, 仍返回 probe 对象; 调用者因此增加 `_activation_observed_bars`. 可复现的反例是: 完整 390 个 09:30-15:59 timestamp 且 OHLC 均完整, 15:58 生成 setup, 15:59 的 `m10=null`; 当前输出是 15:59 `session_end` expired 且 observed `1/8`, 而计划要求必需 probe 数据无效时保持 `pending`.
   - 影响范围: 指标数据缺失会被表述为已真实观察, 并可让不完整数据的公开 lifecycle 从 `pending` 变成 `expired`. 普通 timeout 分支还是使用 array index 差先判断, 存在无效 OHLC probe 时可产生少于 `8/8` 的 `_expiry_kind=activation_window`, 同样违反方案的 normal timeout 不变式.
   - 改进建议: 最小修订为将 probe 的"可计数"与条件不通过分开. 当需要同向颜色时校验颜色所需字段; 当需要 MA10 slope 时校验当前及 lookback `m10`; 缺失任一必需输入时 probe 不计数. 普通 timeout 只能在 observed probe 达到 `maxWait` 时产生 `activation_window` 8/8; 完整 session 收束也必须验证 pending 后的所有必需 probe 输入. 新增"必需 MA10 缺失保持 pending"和"无效 OHLC 不产生少于 8/8 的普通 timeout"两个回归测试. 现有 2026-08-14 数据字段完整, 该修订不应改变已验证的基线差异.

### 中等问题

1. **Expected renderer SHA 未在 CLI 边界立即验证 40-hex**
   - 位置: `runner/tang_publish.py` 的 `--expected-renderer-sha` 参数与 `runner/production.py` 的 recovery 入口.
   - 问题描述: 参数存在时没有先校验为 40 位小写 hex. 非法值会进入 Pages workflow/provenance 等待, 而不是在任何外部等待前拒绝.
   - 改进建议: 在 CLI/production 信任边界使用与其他 commit SHA 相同的 40-hex 规则验证, 并增加非法值不进入 `_process_manifest()` 或 Pages 等待的测试. 当前路径仍会在 delivery 前失败, 因此这是有界失败与精确合同问题, 不是重复发送风险.

### 轻微问题

- 无.

## 未验证项

- V3 runtime rebind: enable receipt 三字段替换、hash-only `config/deployment.json` descendant、cron disable/re-enable 及 runtime authority readback 尚未执行. -- 修复后实施评审通过才按 review-003 顺序执行.
- 远程 Tang push、Pages workflow/live provenance、circuit reset 和 Discord 恢复尚未执行. -- 它们属于后续部署门设, 不用本次未执行状态否定本地 implementation review.

## 裁决理由

已验证的结果包括: frontend 聚焦测试 75/75、普通与 static build 通过; runner 聚焦测试 46/46、全量测试 220/220 通过; 2026-08-14 字段级基线只增加 QQQ 15:59 outcome; runner 的缺少 expected SHA、provenance bracket、receipt-before-delivery、data/renderer 证据分离和 cron argv 兼容均有实现证据. 但 scanner 将缺失必需 indicator 的 bar 计为有效 probe, 会把应保持未知的状态收束为 expired. 这是 active plan 明确要防止的实现缺口, 不能作为非阻断润色留到发布后. 因此对两个当前实现 commit 裁决为 revise.
