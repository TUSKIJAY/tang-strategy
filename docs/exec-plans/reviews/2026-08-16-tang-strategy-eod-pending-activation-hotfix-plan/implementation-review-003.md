# 交付物评审意见

- Review target: `docs/exec-plans/active/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md`
- Review target revision: `v3-active-amendment-2026-08-16`
- Review type: implementation
- Reviewer ID: `codex-implementation-reviewer-01a00adc`
- Plan author ID: `codex-root-01a00adc`
- Independence declaration: attested
- Evidence method: 审查周末恢复路由 correction commit `a2914323bdb7e89cf88fb82d77ff689b0730b872`, 复核与 authority config commit `deb23838e22ba01c01f9a55dbec515904b498a59` 的路径分区, 运行边界及全量测试, 并对三个日期解析分支做独立反例验证
- Verdict: accept
- Confidence: high

**审核对象**: 计划第 10 节 Recovery-Date Routing Correction; runner implementation commit `a2914323bdb7e89cf88fb82d77ff689b0730b872`

## 整体判断

**裁决**: accept

**置信度**: high

## 总体评价

该 correction 只调整显式恢复命令的 run/lease trade date 来源. `--expected-renderer-sha` 存在时, `resolve_production_trade_date()` 通过 `active_transaction_trade_date()` 读取唯一未完事务的 `trade_date`; 无 active transaction 时立即返回 `expected_renderer_sha_unused`, 不调用 current completed-session resolver. 这使 2026-08-14 周五事务可在 2026-08-16 周日进入既有恢复器, 而不会在事务发现之前被 `not_completed_nyse_session` 截断.

无 expected renderer SHA 时的固定 cron 路径仍只调用 `resolve_current_completed_nyse_session(utc_now())`. 它不读 active transaction date, 也没有 previous-session fallback. 事务唯一性、manifest 校验和 ambiguity 拒绝继续由原 `_active_transactions()` 实现; correction 没有创建第二套目录遍历或放宽终态规则. Commit diff 仅修改 `runner/production.py`、`runner/tang_publish.py` 和 `tests/test_runner.py`; hosted capture、delivery、receipt、Discord 幂等及交易数据路径都未改动.

## 问题清单

### 严重问题

- 无.

### 中等问题

- 无.

### 轻微问题

- 无.

## 未验证项

- 新 runner commit 的 runtime authority rebind: `a291432` 尚需按 v3 已批准顺序替换 enable receipt runner fields, 并创建唯一 hash-only config descendant. -- 在 circuit reset 前验证 receipt 字段保留、code tree digest、commit count/path partition、cron disable/re-enable 和 runtime production evidence.
- 第二次生产恢复尚未执行. -- 完成 rebind 后再生成绑定当前 open-circuit digest 的 reset receipt, 执行精确 expected renderer SHA 命令, 并读回 renderer receipt、manifest stage、circuit 和全部 Discord IDs.

## 裁决理由

独立运行 `tests.test_runner` + `tests.test_production` 共 40/40, runner 全量 224/224. 额外反例证明: 显式 SHA 在 current-session resolver 返回空的条件下仍解析为 active transaction 的 `2026-08-14`; 显式 SHA 且无 active transaction 产生 `expected_renderer_sha_unused` 并且 current-session resolver 零调用; 无 SHA 时只调用 current-session resolver, active transaction helper 零调用. 当前实际状态读回为单一 active transaction, `trade_date=2026-08-14`, `stage=pages_verified`, `delivered_message_ids={}`; circuit 为 `open`, last failure 为 `recovery_trade_date_unresolved`, 与 correction 的输入前提一致.

新 helper 直接复用 `_active_transactions()`, 因此多个未完事务、非法 manifest 和不可恢复 stage 仍由原安全边界处理. Capture/delivery/idempotency 实现未变, 固定 cron 也没有获得 prior-session fallback. 该 correction 实现范围与第 10 节一致, 未发现需要返工的问题, 因此裁决为 accept.
