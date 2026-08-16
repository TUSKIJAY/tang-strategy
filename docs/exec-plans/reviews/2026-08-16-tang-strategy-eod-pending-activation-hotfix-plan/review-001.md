# 交付物评审意见

- Review target: `docs/exec-plans/proposed/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`
- Review target revision: `v1-proposed-2026-08-16`
- Review target commit: `b228fa9`
- Review type: design
- Reviewer ID: `codex-design-review-01a00adc`
- Plan author ID: `codex-root-01a00adc`
- Independence declaration: attested
- Evidence method: 对照已提交方案、共享 scanner 调用面、RTH 窗口过滤逻辑、生产事务恢复器、Pages 验收器与 Discord 幂等交付路径进行静态核对
- Verdict: revise
- Confidence: high

**审核对象**: `2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`

## 整体判断

**裁决**: revise

**置信度**: high

## 总体评价

方案正确抓住了当前故障的两个真实边界: QQQ 2026-08-14 的 390 根 RTH 数据完整, 15:59 启动但没有后续观察根; 原生产事务已到 `pages_verified`, 且日报的 `delivered_message_ids` 为空. 保留启动证据、不降低 hosted acceptance、不重跑数据、不创建第二事务和逐件记录 Discord ID 的方向合理.

当前 revision 仍有两个执行正确性缺口. 第一, 共享 `scanSignals()` 接收任意 bar 数组, 方案却把"输入结束"直接等同为 `session_end`; 这会在部分输入、缺根或未收盘数据上把未知状态错误收束为过期. 第二, 现有恢复器在 `pages_verified` 阶段不再核验当前 Pages provenance; 方案的外部前后检查无法把新 renderer commit 与不可逆的截图及发送动作绑定. 这两点需要在激活前修订.

## 问题清单

### 严重问题

1. **输入结束不能无条件声明为 session end**
   - 位置: 第 2 节 In scope, 第 3 节的 `_expiry_kind=session_end` 不变式, Phase 1.
   - 问题描述: `scanSignals()` 同时被 Review、Static Review 和 Backtest 调用, 其入口只接收 `bars1m/bars5m/strategy`, 没有"该交易日已完整收盘"的证明. `reviewPayloadForWindow(..., 'rth')` 只过滤 09:30-16:00, 不会证明最后一根是 15:59, 也不会证明中间无缺根. 因此"最后一根输入 bar"可能只是截断点, 不是 session end.
   - 影响范围: 部分数据可把原本应保持 `pending` 的启动标成 `expired`, 从而掩盖数据不完整, 并使 hosted acceptance 错误通过.
   - 改进建议: 把收束门设写入方案和测试. 可选做法是仅在调用者传入经验证的 `window_complete=true` 时收束, 或由 scanner 验证最后一根与 strategy session end 匹配且必要的完整性门设通过. 部分输入必须新增回归测试, 并保持 `pending`; 只有经证明的收盘边界才可产生 `_expiry_kind=session_end`.

2. **新 renderer commit 未与恢复期间的截图和发送操作 fail-closed 绑定**
   - 位置: 第 3 节 hosted acceptance 不变式, Phase 3、Phase 4, 第 5 节的恢复证据.
   - 问题描述: 原事务的 `commit_sha`、`workflow_run_id` 和 `hosted_provenance_sha` 全部绑定数据 commit `6f9a87c...`. 现有 `_process_manifest()` 在 `stage=pages_verified` 时直接调用 hosted capture 和 Discord delivery, 不再读取或比对 live `build-manifest.json`. hosted capture 收据中的 `commit_sha` 只是调用者传入的原事务 commit, 不是页面自证的 renderer commit. 命令前检查与命令后检查之间仍存在 Pages 变化窗口; 后检查只能在发送后发现不一致, 不能让不可逆发送 fail closed.
   - 影响范围: 无法按方案声称"截图来自已验证 hotfix renderer". 极端情况下, 可以使用与前检查不同的 Pages 部署生成截图和文案并发送.
   - 改进建议: 在方案中引入可持久、可测试的 renderer provenance 门设. 恢复路径必须在同一个发送前路径内读取 Pages provenance, 要求它等于 hotfix commit, 并把该 SHA 写入 capture/receipt; 不匹配时在第一条 Discord 日报发送前停止. 原数据 commit 和 workflow 字段继续保留, 但新 renderer 证据必须使用独立字段或独立签名恢复收据, 不得冒充原事务 commit. 若这需要修改 publisher runner, 必须把对应源码、测试、部署边界和回滚方式加入 task-owned scope.

### 中等问题

1. **`_activation_observed_bars` 的计数语义未锁定**
   - 位置: 第 2、3 节与 Phase 1 测试矩阵.
   - 问题描述: 方案要求"实际可用的后续 bar", 但未规定是按数组 index 差、处理过的 in-session bar 数, 还是有效 activation probe 数计数. index 差在缺根、包含非交易时段 bar 或跨日数组时不真实.
   - 改进建议: 把定义固定为"启动后已处理的同一交易窗口内 bar 数", 通过 pending 状态显式累计, 普通过期为 `8/8`, 15:59 同 bar 收束为 `0/8`. 增加带非交易时段 bar 或 index 间隙的测试, 防止把 index 差当作观察数.

2. **既有 lifecycle 保持检查需要可机器比对的基线**
   - 位置: 第 3 节第一条不变式, Phase 2.
   - 问题描述: Phase 2 只写"所有更早 outcome 不变", 没有指定比较字段和基线产物. 新元数据是允许的, 因此完整 JSON 直比会失败, 人工目测则不足以支撑 byte-semantic 不变声明.
   - 改进建议: 在修改前保存 2026-08-14 SPY/QQQ annotation 基线摘要, 对除新增 `_activation_observed_bars` 和 `_expiry_kind` 之外的既有 setup/activated/expired 字段做排序后比较. 只允许新增 QQQ 15:59 的 expired outcome 及其明确元数据.

### 轻微问题

1. **恢复收据名称应区分 data publication 与 renderer deployment**
   - 位置: Phase 3、Phase 4 及第 5 节 Evidence And Commit Plan.
   - 改进建议: 收据和 closeout 文案中分别命名 `data_commit_sha/data_workflow_run_id` 与 `renderer_commit_sha/renderer_workflow_run_id`, 避免将 hotfix Pages 证据写回原事务字段或把两个 workflow 合并声称.

## 未验证项

- 2026-08-14 实际新 scanner 输出: 尚未实施, 无法验证 QQQ 15:59 是否为 `0/8` 且更早 lifecycle 保持不变. -- 按修订后 Phase 2 的字段级基线比较验证.
- Pages hotfix workflow 与 live provenance: 尚未推送, 无可用的新 workflow 和 live SHA. -- 发布后用独立 renderer 收据验证.
- Discord 当前最后 20 条消息: 本次设计评审未执行外部读取. -- 发送前执行方案规定的有界检查, 由现有 receipt key、Bot author 和完整 body 对账停止重复交付.

## 裁决理由

修复 scanner 本身的方向可行, Discord 的有界预检、逐件记录和精确 ID 读回也与现有幂等实现一致. 但部分输入被误判为 session end 会改变未知与过期的核心语义, 而外部 provenance 前后检查不能在不可逆发送前绑定新 renderer. 两者都属于执行正确性问题, 不适合留到实施阶段自然解决. 因此对 revision `v1-proposed-2026-08-16` 裁决为 revise; 方案补全完整窗口门设、明确 observed-bar 计数、增加可执行的 renderer provenance 绑定后, 可重新送审.
