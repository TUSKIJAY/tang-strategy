# 交付物评审意见

- Review target: `docs/exec-plans/proposed/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`
- Review target revision: `v2-proposed-2026-08-16`
- Review target commit: `fa0739ffa1534227c6ef5f96b4efa1af193f39d9`
- Review type: design
- Reviewer ID: `codex-design-review-01a00adc`
- Plan author ID: `codex-root-01a00adc`
- Independence declaration: attested
- Evidence method: 对照 review-001 的四项修订要求, 核对 v2 的 scanner 收束合同、observed-bar 计数、annotation 基线比较、renderer provenance 门设与 circuit 恢复顺序
- Verdict: approve
- Confidence: high

**审核对象**: `2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`

## 整体判断

**裁决**: approve

**置信度**: high

## 总体评价

Revision `v2-proposed-2026-08-16` 已把 review-001 的两个严重问题和两个中等问题转化为可执行门设、测试和收据要求. Scanner 不再把任意输入结束当作 session end, 而是要求配置时段从开始到收盘前一分钟连续且 probe 字段有效. 部分、缺根、盘中和无 early-close 日历证明的输入明确保持 `pending`. `_activation_observed_bars` 改为显式的有效 probe 计数, 并有 `8/8`、`0/8`、不完整输入及正常激活的合成测试要求.

Renderer 与 data publication 的证据也已分离. 新设计通过显式 `--expected-renderer-sha`, 在同一恢复路径内用浏览器前后 provenance 检查包围 SPY/QQQ capture, 然后在第一条 Discord 日报前写入冗余校验的 renderer receipt. 该 receipt 分别记录 data commit/workflow 和 renderer commit/workflow, 不会改写原事务的 `pages_verified` 证据.

## 问题清单

### 严重问题

- 无.

### 中等问题

- 无.

### 轻微问题

1. **实施时应保持无显式 renderer SHA 的恢复路径为 fail closed**
   - 位置: Phase 2 和 Phase 4.
   - 改进建议: `--expected-renderer-sha` 可保持对无未完事务的既有 cron 命令兼容, 但进入既有 `pages_verified` 恢复分支时若缺少该参数, 必须在 capture 和 Discord 前停止. 这是 v2 已建立的"显式 expected renderer"不变式的直接实现要求, 不需要再次修订方案.

## 未验证项

- Scanner 的完整时段判定和 probe 计数: 尚未实施. -- 按 Phase 1 的正反例测试和 Phase 2 的 2026-08-14 实际 payload 比较验证.
- Renderer provenance bracket 与恢复 receipt: 尚未实施. -- 测试 mismatch 在 capture/delivery 前停止, match 时 receipt 先于发送持久化且截图 hash 一致.
- 生产 circuit 恢复结果: 尚未执行. -- 用绑定当前 open-circuit checksum 的 reset receipt 恢复, 并在成功后精确读回 circuit、renderer receipt 和全部 Discord IDs.

## 裁决理由

Review-001 的四项问题均已有明确的输入合同、负例、基线对比和持久收据, 可在实施验收中客观判定. Circuit 必须先用当前 checksum 绑定的人工收据 reset, 因为 open circuit 会禁止生产恢复进入; reset 本身不发送日报. 随后的 expected-renderer gate 和 provenance bracket 位于 capture 与任何 Discord 日报之前, 只有匹配时才生成并持久化 renderer receipt, 再进入幂等 delivery. 不匹配会在日报发送前失败并重新打开 circuit. 该顺序在不改写原数据事务证据的前提下满足 fail-closed 恢复, 因此裁决为 approve.
