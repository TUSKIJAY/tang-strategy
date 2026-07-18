# 交付物评审意见

**审核对象**: implementation-acceptance.md

## 整体判断

**裁决**: accept
**置信度**: high

## 总体评价

本地实现与 active plan 的核心数据安全合同一致. 独立复算确认 tracked DB 从基线 43 天增加为 46 天, 新增集合严格等于 `SPY|2026-05-15|extended`、`SPY|2026-06-30|extended` 和 `SPY|2026-07-01|extended`. 原 43 天 digest map 无 mismatch, strategies 与 teaching table hashes 未变化. 三个历史来源日的 ID 4/33/34 没有被复用, 当前 candidate/live ID 为 44/45/46, 且 source/current 的 market-day、1m 和 5m normalized hashes 分别一致. 当前 DB 的 integrity、foreign keys、三日 bar counts、2026-07-17 assemble 及 06-30/07-01 Tang overlays 均通过独立只读或临时副本复核.

Rebuild 已从 delete-first 改为 candidate-first. Seed discovery、非空和有限数值检查、manifest/candidate key 一致性、实际/声明/seed bar counts、integrity/foreign keys、market-day superset、strategy slug superset、teaching key superset 和 live drift token 均在 promotion 前验证. `--allow-date-loss` 只放宽 market-day subset rule. 使用当前 46-day DB 的 SQLite 临时 backup 和仓库真实 6-day seed 复跑默认 rebuild, 结果为非零拒绝, 完整列出 40 个 missing logical days, before/after byte SHA-256 相同, 副本仍为 46 天且 integrity/foreign keys 正常. 15 个 focused safety tests 与完整 19-test suite 均通过; frontend production build、compile、governed checker、startup budget 和 structural validation 也得到复核.

共享 write lock 覆盖 `init_db`, market/strategy/teaching importer, recovery snapshot/promotion 和 rebuild promotion. Candidate 使用相邻路径, SQLite backup snapshot, path/byte/logical token、sidecar gate、same-filesystem `os.replace`, file/directory flush 和 post-validation rollback. 删除项严格限于已授权的旧 `docs/` 生成物及零字节 `.codex`; 当前 publisher workflow 未改变, provider stubs、frontend scanner/chart assets、browser dependency、seed model 与 tracked DB 均保留. Governed indexes、roadmap、`PROGRESS.md` 和 `HANDOFF.md` 已同步到 Phase 7 pending acceptance. Index 无 staged 内容, branch/HEAD 仍为 `codex/project-harness@8c6851d`, 本地 `main` 与 `origin/main` 仍同指 `c262ba0`, 没有发现远端或 market-facing effect.

## 问题清单

### 严重问题

无.

### 中等问题

无.

### 轻微问题

- **Evidence redaction 对未来来源值仍依赖人工复核**
  - 位置: `backend/scripts/recover_historical_market_days.py:35`, `backend/scripts/recover_historical_market_days.py:223`, `backend/scripts/recover_historical_market_days.py:266`; `evidence/data-recovery-evidence.json:32`, `:141`, `:250`, `:350`.
  - 问题描述: 当前 evidence 已检查, 未包含 password、credential、authentication token、account data 或 private configuration. 现有 sanitizer 使用 provenance key allowlist 和敏感 key fragment 递归脱敏, 但顶层 `source` / `title` / resolved path 以及普通 key 下的字符串值不做内容扫描. 若未来历史 DB 把 credential 放入 URL、`authorization` 等未命中 key, 自动脱敏不能单独保证安全.
  - 改进建议: 当前交付无需返工, 因为已落盘 artifact 内容安全. 后续复用 recovery helper 时应继续执行 evidence 人工扫描; 若该脚本成为常规路径, 再补充常见 authorization key 和 URL/value-level secret detection, 或只输出更窄的结构化 provenance.

- **共享锁缺少显式 contention test**
  - 位置: `backend/tests/test_db_safety.py:22`, `backend/app/services/db_safety.py:89`.
  - 问题描述: 当前测试覆盖 consistent snapshot、source drift、ID-independent hash 和 rollback, rebuild 测试也证明 drift 拒绝. Lock implementation 和 writer call sites 已逐项核对, 但 suite 没有单独启动两个 writer 证明第二个 writer 在 lock release 前阻塞或 timeout.
  - 改进建议: 作为后续测试增强, 可增加临时 DB 上的双进程 contention/timeout case. 当前代码路径已使用同一 adjacent lock, 该缺口不影响本次 acceptance.

## 未验证项

- 真实远端状态: 远端 mutation 未获授权, 因此未访问或运行 hosted workflow. 本地无 staged files, 无 feature remote-tracking ref, Pages workflow 无 diff, `main` / `origin/main` 本地 refs 未移动; 这些是当前 no-remote-effect 的可验证边界.
- Hosted workflow specialized lint/run: 当前环境没有对应专用 lint/runtime. Workflow 修改仅增加 governed checker 和 startup budget 两个本地已通过步骤, 现有 job names、ordering 和 backend/frontend jobs 保持一致.
- Browser regression 独立重放: 本次未再次驱动完整浏览器 UI. 已核对 2026-07-18 evidence, 并在临时 46-day DB 上独立复跑 2026-07-17 assemble 与 06-30/07-01 overlays; frontend production build通过.
- Crash-at-instruction durability: `fsync` 和 atomic replace/rollback 顺序经代码审查与 failure tests 验证, 但未进行进程 kill、断电或文件系统故障注入.

## 裁决理由

Acceptance 的关键声明均得到代码、独立 DB digest、隔离 rebuild、完整测试和 repository state 的交叉支持. 数据恢复只新增批准的三个逻辑日, 默认 rebuild 对日期和非市场数据 fail closed, writer drift 不会覆盖新状态, 删除/保留与权限边界符合 active plan. 剩余事项是未来 sanitizer hardening、lock contention coverage、hosted validation 和故障注入, 不构成本轮实现偏差或数据正确性缺口. 因此任务完成度高, 遗留风险可控, 裁决为 `accept`.
