# 交付物复审意见

**审核对象**：`docs/exec-plans/active/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md` 的 implementation/acceptance，remediation stable commit `b9dc84d00ff6a61ca6b6063352d8ed2ad6d31055`，parent `f92e273b0153eefac14e5c54f94926a2bd4e707e`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v5-round-3-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-multi-trader-r2`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: independent exact remediation commit/parent comparison, source and regression inspection, isolated temporary content/database backup-cleanup fault injection, pinned local backend/frontend/lifecycle verification, tracked-database integrity and digest inspection, and authority-boundary review
- Verdict: accept
- Confidence: high

## 整体判断

**裁决**：accept  
**置信度**：high

## 范围与证据

指定 stable commit 与指定 parent 精确相连。`f92e273b0153eefac14e5c54f94926a2bd4e707e..b9dc84d00ff6a61ca6b6063352d8ed2ad6d31055` 的 exact diff 为 9 paths、154 insertions、16 deletions。实现改动限于 `backend/app/main.py`，回归改动限于 `backend/tests/test_trade_records.py`；其余变动为状态、计划、上一份评审、索引和数据安全证据的同步。补救范围没有触及 tracked SQLite、provider、IB/Gateway、workflow、Pages 或其他远端发布路径。

`backend/app/main.py:328-369` 现在明确区分 promotion 前失败与 promotion 后清理失败：candidate promotion 和 post-validation 完成后先设置 `promoted = True`；verified backup 删除异常被转换为 `cleanup_warnings`，请求保持成功，已提交的新 content 和新 DB 不再被拆开；只有 promotion 前失败仍执行 candidate/backup 清理并允许上层恢复旧 content。该处理符合上一份 implementation review 要求的两种相干终态。

`backend/tests/test_trade_records.py:230-286` 使用临时 content tree 和临时 tracked-DB 副本，经实际管理员写入入口与 `_sync_trade_projection` 完整调用链，专门对 `.trade-sync-*.backup.db` 清理注入 `PermissionError`。测试同时断言新 note 存在于 canonical JSON 与 SQLite、返回一条 cleanup warning，并保留一份 verified backup，覆盖了原缺陷的触发位置和可观察结果。

独立重放同一故障注入得到：`error=None`、content 为 candidate、新 DB 为 candidate、`content_db_equal=True`、一条预期 cleanup warning、`retained_backup_count=1`。因此被上一份评审复现的 old-content/new-DB 组合未再出现，结果为 new-content/new-DB 成功态；同时，既有 promotion 前异常路径仍由后端全量测试覆盖为 old-content/old-DB 失败态。

验证通过：新增定点回归 1/1、后端全量 76/76、后端编译、前端 trade-record 契约 11/11、普通构建、静态构建、lifecycle fixtures 146/146、governed/auto harness、operating-modes、startup budget、launcher 语法及 diff 检查。Tracked SQLite 的 SHA-256 为 `4a5bce13a4d9da31850ad1b04e616c58ce55b614bc88dbb8ecc04466f7442c34`，`integrity_check` 为 `ok`，foreign-key check 无返回行。

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | 上一份评审的 post-promotion cleanup coherence blocker 已修复并由完整链路回归及独立故障注入关闭。 | — |

## 未验证项

- Hosted checks、Pages publication、hosted URL、push、PR 和 merge 未执行；当前 authority 未开放这些动作，因此不能计为 pass。
- IB/Gateway fallback 未执行；补救提交没有进入 broker-facing 边界，当前 review 也不授予该权限。
- 新的 macOS/Windows provider receipt 未生成；补救 diff 不含 market-data/provider 改动，既有 Phase 5 receipt 仅作为历史证据，没有被表述为新验证。
- 完整 real-browser Review/Backtest/Teaching/Admin 点击矩阵未重新执行；本次补救针对后端写入相干性，前端契约测试及普通/静态构建已通过。

## 裁决理由

上一份评审要求修复的唯一严重问题已在指定 remediation commit 内闭环：promotion 成功后的备份清理失败不再向 content writer 传播为事务失败，而是保留 verified backup 并返回可观测 warning。独立临时副本重放证明 content 与 DB 同时保持新状态，新增完整调用链回归固定该行为，全量验证未发现回归，tracked DB 未漂移，且没有发生未授权的 provider、broker 或远端动作。因此 implementation/acceptance 裁决为 `accept`，不再需要 `revise`；未发现需要 `reject` 的方案方向或边界问题。
