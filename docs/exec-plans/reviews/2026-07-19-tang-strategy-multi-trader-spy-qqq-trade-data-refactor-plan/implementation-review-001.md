# 交付物评审意见

**审核对象**：`2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md` 的 implementation/acceptance，stable commit `f92e273b0153eefac14e5c54f94926a2bd4e707e`，parent `80f74f63f32849eddaaa99321f5f779446503458`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v5-round-3-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-multi-trader-r1`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: independent exact commit/parent comparison, frozen-surface and removal recount, pinned local backend/frontend/lifecycle verification, read-only tracked-DB inspection, runtime/default/secret/generated-output scans, source-level cutover and authority inspection, and an isolated temporary-copy rollback-coherence fault injection
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**：revise
**置信度**：high

## 总体评价

Stable commit 与指定 parent 精确匹配，工作树在评审写入前为 clean。该 commit 的 exact diff 为 59 paths，其中 22 个删除项精确对应 20 份 legacy JSON、`backend/app/services/tang_trades.py` 和 `frontend/src/features/review/TangTradeList.jsx`，未发现冻结 surface 外的实现路径。Tracked SQLite 当前为目标 schema，46 个 SPY grandfathered logical days、46 个 active datasets、43,425/8,821 bars、1/27/27/30/4/2 trade rows、logical SHA-256 `f7ca32e4...70a34`、integrity `ok` 和零 foreign-key rows 均独立复核通过。Public/default runtime 扫描未发现遗留 `tang_trades` consumer，未发现被追踪的 generated review/build 输出。

本地验证通过 75/75 backend tests、backend compile acceptance、11/11 frontend contract tests、normal/static builds、146/146 lifecycle fixtures、governed/auto/focused/startup/launcher/diff checks。API/static 单一 `trade_records` cutover、frontend/Admin/download/K-line 载体、pair-first workflow/runbook 及 Phase 5 双平台 receipt 边界与代码和 evidence artifacts 一致。Hosted workflow、Pages、IB 和新的 provider run 未执行，也未被计为 pass。

但管理员 canonical content 与 tracked DB projection 的组合写入存在可复现的 rollback-coherence 缺陷。该缺陷可在一次合法写入的后置清理失败时产生 content/DB 分叉，违反 plan Sections 3.5、6 Phase 6 和 7 对 atomic content replacement、candidate projection 及 rollback-coherent boundary 的要求，因此当前 implementation 不能接受。

## 问题清单

### 严重问题

1. **DB promotion 后的 backup 清理异常会错误触发 content rollback，造成 canonical content 与 DB projection 分叉**
   - 位置：`backend/app/main.py:351`、`backend/app/main.py:352`、`backend/app/main.py:357`、`backend/app/main.py:358`；`backend/app/services/trade_records.py:599`、`backend/app/services/trade_records.py:600`、`backend/app/services/trade_records.py:601`、`backend/app/services/trade_records.py:606`
   - 问题描述：`_sync_trade_projection()` 在 candidate 已成功 promotion 且 post-validation 已通过后设置 `promoted = True`，随后在 `finally` 中无条件删除 verified backup。若该清理操作抛出异常，异常会越过已经完成的 DB commit 返回到 `_atomic_replace_text()`；后者把 canonical JSON 恢复为旧字节，但没有恢复已经 promotion 的 DB。
   - 独立复现：在临时 content tree 和临时 tracked-DB 副本上提交一份仅修改 2026-07-17 note 的合法 daily record，并只对 promotion 后的 `.trade-sync-*.backup.db` 删除注入 `PermissionError`。实际结果为 `error=PermissionError`、`content_rolled_back=True`、`db_contains_candidate=True`、`content_db_equal=False`。复现未修改仓库 content 或 tracked DB。
   - 影响范围：管理员请求返回失败，但 canonical source 已回到旧版本，SQLite query/runtime 却保留新版本。后续 API、Pages export、Agent query、再次编辑和重建可能分别读取不同事实，且现有 count-only post-validation 无法修复该分叉。
   - 改进建议：把 promotion 成功后的 backup 清理定义为非事务性 cleanup，清理失败时保留 verified backup、返回成功并记录 warning；或者在任何需要向调用方传播的 post-promotion 异常上先用该 backup 恢复 DB 并验证，再允许 content rollback。增加 fault-injection regression，强制证明结果只能是 new content/new DB 的成功状态或 old content/old DB 的失败状态，禁止 old/new 组合。

### 中等问题

- 无。

### 轻微问题

- 无。

## 未验证项

- Hosted checks、Pages publication 和 hosted URL：当前 authority 明确未开放，未运行，不能计为 pass。后续仅能在单独授权后验证。
- IB/Gateway fallback：TV receipt 未留下需要 IB 的未解决 hard failure，且当前 review 不含 IB authority，因此未运行。
- 新的 macOS/Windows provider receipt：本轮检查了两份既有 Phase 5 receipt 的版本、quality、candidate、grandfathered preservation 和 tracked-DB boundary，但未重新发起 provider 请求。
- 完整 real-browser 点击矩阵：本轮独立运行了 frontend pure tests 和 normal/static builds，既有 evidence 中的 Review/Backtest/Teaching/Admin/download browser receipt 未重新运行。该未验证项不影响上述确定性 rollback blocker。

## 裁决理由

绝大多数迁移、cutover、数据库保存、consumer removal、pair-first workflow 和本地验证目标已达到，且未发现越权远端动作。裁决仍为 `revise`，因为一次可合理发生的文件清理异常即可在 API 报错后留下两个相互矛盾的权威数据面，直接破坏本计划要求的 fail-closed、atomic replacement 和 rollback-coherent acceptance。该问题属于边界内可修复实现缺陷，不需要推翻方案方向，因此不选择 `reject`；在修复并加入上述 fault-injection regression 前，也不满足 `accept` 标准。
