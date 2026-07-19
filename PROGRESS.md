# Progress

## Current Status

<!-- operating-modes-state:start -->
- Current plan: `2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan`
- Lifecycle status: `Active`
- Current phase: `phase-6`
- Phase state: `in-progress`
- Next gate: `phase-6-implementation-review`
<!-- operating-modes-state:end -->

2026-07-19: Phase 6 本地 cutover 与验收已完成：tracked DB 由 `76a885c2...28f8` 原子 promotion 为 `4a5bce13...2c34`，46/46 logical keys/day digests 与 `f7ca32...70a34` logical hash 保持一致；1/27/27/30/4/2 trade projection、integrity/FK、20 legacy JSON + 2 legacy code removals、`trade_records` API/static/Review/Admin/K-line/default pair carriers、旧边界回滚演练均通过。最终结果为 75 backend、11 frontend、normal/static builds、real-browser Review/Backtest/Teaching/Admin + 4 downloads、146 fixtures、governed/auto/startup/YAML/diff/secret/runtime scan 全通过。用户现已授权 plan-scoped 本地稳定提交、独立 implementation review 与 accepted closeout，计划恢复为 `phase-6:in-progress`，next gate 为 `phase-6-implementation-review`；push、PR、Pages、hosted 与 IB 仍未授权。

2026-07-19: 用户通过 `user-instruction:2026-07-19-authorize-phase6-cutover` 明确授权本地 Phase 6 tracked-DB promotion、冻结清单内 legacy removal 与正式 cutover。Phase 5 双平台 receipt exit gate 已满足，Phase 6 进入 `in-progress`；本次权限不包含新的 stage/commit/push、PR、merge、Pages、hosted、IB 或其他远端动作。

2026-07-19: 用户授权修复真实 Windows receipt 暴露的 Phase 5 portability defects。实现改为 writable binary descriptor `fsync`、仅在成功获取后释放 `msvcrt` byte lock、复用 Windows-safe directory-fsync，并为受影响测试固定 UTF-8；未放宽任何 quality/provider/candidate/rollback gate。最终 Windows CPython 3.13.11 receipt 通过：13/13 focused、80/80 backend、compileall，真实 SPY=`AMEX` 868/192 与 QQQ=`NASDAQ` 915/191，双方 RTH 390/78、零 missing/duplicate、`synthetic_padding=false`；临时候选 46 -> 47、45 non-target grandfathered days preserved、integrity/FK 通过，tracked DB hash 前后同为 `76a885c2...28f8`。macOS/Windows receipts 现均通过，Phase 5 更新为 `phase-5:complete`，next gate 为 `phase-6-authorization`；IB、tracked DB promotion、Phase 6、Pages 与 hosted 均未运行。

2026-07-19: Windows 在 `codex/project-harness@ea3c264ddebb7c6a3f3f2b537b62daec2ee6c6b6` 使用本地 CPython 3.13.11 建立 pinned runtime；依赖安装与 `America/New_York` 标准/夏令时 offset 通过，但 focused Phase 5 suite 运行 13 tests 后出现 1 failure / 4 errors。失败集中在 Windows `os.fsync` bad file descriptor 与 `msvcrt` lock timeout 清理的 permission error，发生在任何 TradingView 请求、candidate DB copy 或 accepted seed 创建之前。receipt 保留在 `%TEMP%\tang-tv-windows-receipt-ffac6bf6699e4aeabdcb4b81a3912d40`，focused log SHA-256 为 `79caf1b...7257a`。Phase 5 继续 `phase-5:blocked`，next gate 不变；未调用 IB，未进入 Phase 6。

2026-07-19: 用户明确授权 `commit and push` 当前 `codex/project-harness` branch，用于在 Windows checkout 拉取并执行尚缺的 Phase 5 pinned-runtime TradingView receipt。授权仅覆盖当前 75-path 计划内 checkpoint 的一次 stage/commit/push；不授权 PR、merge、Pages、IB、tracked DB promotion、Phase 6 或其他远端变更。Windows receipt 在真实执行并记录前仍为 `not run`，Phase 5 继续保持 `phase-5:blocked`。

2026-07-19: 用户已单独授权真实 TradingView provider run。macOS pinned-runtime receipt 已通过：修复 provider 子进程绝对 `PYTHONPATH` 与 SPY=`AMEX`/QQQ=`NASDAQ` routing 后，真实 2026-07-17 pair 获得 SPY 868/192、QQQ 915/191 total bars，双方 RTH 均为 390/78 且零缺失/重复；临时候选库 46 -> 47、integrity/FK/45 grandfathered-day preservation 通过，tracked DB hash 不变。13 pair tests、80 backend tests、compileall、governed/auto checks 通过。用户明确将 Windows receipt 延期到 Windows 端准备并 `git pull` 后再执行，因此 Windows 仍为 `not run`，Phase 5 按 exit gate 保持 `phase-5:blocked`；在该时点，75 个计划内改动尚未 commit/push。IB、tracked DB promotion、Pages 与 Phase 6 仍未授权。

2026-07-19: Multi-trader Phase 5 offline acceptance 已完成并通过完成性补强：SPY/QQQ discovery/rebuild、same-provider pair orchestrator、NYSE session + exact `ts` date/offset/instant/`t` RTH 390/78 gates、pair-level concurrency lock、offline staged-input tracked-target refusal、candidate/non-shrink/drift、rollback-protected seed pair 与 POSIX/Windows lock backend 已实现。当时 12 pair tests、79 backend tests、10 Node tests、normal/static build、真实浏览器 Review/Backtest/Teaching、146 lifecycle fixtures、workflow YAML、当前代码在真实 46-day DB copy 上的 46 grandfathered-day preservation，以及只读 `git archive HEAD` 的旧 app/DB/20-file legacy 整体回滚演练均通过；在后续真实 provider 授权前，双平台 receipts 尚未运行，因此当时如实停在 `phase-5:blocked`。

2026-07-19: Multi-trader Phase 4 已完成：fixture-driven SPY/QQQ filters、all-active/multi-select/focus、trader color + CALL/PUT shape、true grouped markers、group-first reported/calculated statistics、leg/event drilldown、admin/readonly editor gate 与 current-filter JSON + 3 CSV 已实现。9 Node tests、normal/static Vite builds、65 pinned backend tests、146 lifecycle fixtures 与 harness checks 通过；Review/Static consumer、public payload、registered routes、tracked DB 与 Pages 未切换。当前进入 `phase-5:in-progress` offline pair implementation；真实 TV/IB receipts 仍需单独授权。

2026-07-19: Multi-trader Phase 3 已完成：1 trader registry + 20 canonical days 与 pure render 21/21 exact match，27 groups / 2 contexts / zero unaccounted；unregistered read/admin handlers、role/filter/atomic-write 与 explicit candidate projection 通过。65 pinned backend tests、compileall、runtime/static exact hash compatibility 与 lifecycle checks 通过；legacy sources/tracked DB/route/consumer/Pages 未切换。当前进入 `phase-4:in-progress` fixture-driven frontend work。

2026-07-19: Multi-trader Phase 2 已完成：candidate-only target schema、46 active datasets、bar re-key、old/new logical digest、trade projection、4 Agent views、import/recovery/rebuild adaptive ownership 与 rollback/drift/FK gates 已通过。60 pinned backend tests、compileall、实际 46-day candidate preservation、API/static exact hash compatibility 均通过；tracked DB SHA-256 仍为 `76a885c2...28f8`，未 promotion。当前进入 `phase-3:in-progress` canonical migration/backend handler work。

2026-07-19: Multi-trader Phase 1 已完成：`trade-records-v1` exact response/public-private contract、两份 JSON Schema、pure validator/timezone/default/stable-ID/outcome/statistics/export/classifier 已落地。34 focused + 53 complete pinned backend tests、compileall、20/27/2 deterministic classifier、API/static hash preservation 与 lifecycle checks 通过；canonical daily files、tracked DB、legacy/public payload/Pages 均未切换。当前进入 `phase-2:in-progress` candidate-only SQLite work。

2026-07-19: Multi-trader Phase 0 已完成并通过 exit gate：44 Add / 42 Modify / 22 Remove exact paths 已冻结，20 legacy files / 27 trades / 2 day notes 已逐文件哈希；tracked DB identity、DDL、46 logical keys、row counts、integrity/FK、logical/bar/non-market digests、API/static/hash route 与 workflow/runbook hashes 已写入四个 bounded evidence artifacts。governed/auto/focused checks、146 fixtures、startup budget、whitespace 全通过，tracked DB SHA-256 保持 `76a885c2...28f8`。当前已进入 `phase-1:in-progress`。

2026-07-19: 用户已发出独立 implementation-start 指令。Phase 0 entry gate 已通过：现场 branch/HEAD/worktree 与 frozen v5 dual-review approval 均核验，startup baseline 四项通过。当前正在只读冻结 manifest、tracked DB/API/static/hash-route/workflow/runbook 基线；stage/commit、provider/IB、tracked DB promotion、Phase 6、remote Git 与 Pages 仍未授权。

2026-07-19: `Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor` round 4 已完成：Kimi `review-007` 与 Grok `review-008` 对 frozen v5 均返回 `approve/high`。Kimi 仅记录 Windows IANA tzdata 的非阻塞环境前置观察；Phase 0 manifest revalidation 与 Phase 5 fail-closed receipt gate 已覆盖其风险。依照用户 `2026-07-19-start-dual-review-loop-through-active` 指令，plan 已迁移到 `active/`，状态为 `phase-0:not-started`，next gate 为 `phase-0-start`。本次 activation 为 lifecycle-only；实现、provider/IB、tracked DB、commit、push、PR、merge 与 Pages 发布仍未授权、未开始。

2026-07-19: `Tang Strategy Coding And Data Update Modes` 已完成全部 Phase、12 轮 bounded remediation 与第十三轮独立 `accept`，并迁移到 `completed/`。Verified implementation commit 为 `994f9176eb74778f346710e62ec6dabde55bae9a`，lifecycle reconciliation commit 为 `4f6f2e0937ba5580e170e32ea7fd17718b7b68e3`。146/146 fixtures、focused/governed/auto、startup budget、syntax/whitespace、runtime/data zero-diff、frozen hashes、read-only DB checks 和临时 Vite build 均通过。真实 provider/IB/DB update/Tang input/push/Pages/hosted evidence仍未授权、未执行、未冒充 pass。

## Navigation

| Need | Location |
| --- | --- |
| Stable project rules | `INSTRUCTIONS.md` |
| Current resume point | `HANDOFF.md` |
| Harness configuration | `.harness/config.json` |
| Active multi-trader plan | `docs/exec-plans/active/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md` |
| Completed operating-modes plan | `docs/exec-plans/completed/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` |
| Previous completed plan | `docs/exec-plans/completed/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md` |
| Verification and reviews | `docs/exec-plans/reviews/2026-07-19-tang-strategy-coding-and-data-update-modes-plan/` |

## In Progress

- [ ] Freeze the accepted Phase 6 implementation in a local commit, obtain an independent implementation verdict, and reconcile closeout only after `accept`.

## Blocked

- [ ] None.

## To Do

- [ ] Create the authorized stable local implementation commit, request independent implementation review, and close the lifecycle only after `accept`. Push, PR, Pages, merge, and other remote actions remain separately gated.
- [ ] Record-only follow-ups remain in `docs/optimization/2026-07-18-repository-audit-followups.md`; they are not approved work.

## Completed

- [x] 2026-07-19 - Completed authorized local Phase 6 promotion/removal/cutover and acceptance: target tracked DB, exact 22 removals, normalized public/default consumers, rollback restore, 75 backend tests, 11 frontend tests, both builds, real-browser Review/Backtest/Teaching/Admin/downloads, and full governed/data/link scans passed.
- [x] 2026-07-19 - Completed Multi-trader Phase 0 with exact manifest, DB/API/static/route/boundary hashes, 20/27/2 legacy inventory, cross-platform timezone prerequisite assessment, and unchanged tracked DB bytes.
- [x] 2026-07-19 - Completed Multi-trader Phase 1 with frozen canonical/public/export contracts, 34 focused and 53 complete backend tests, deterministic 20/27/2 classification, and zero runtime/data/publication diff.
- [x] 2026-07-19 - Completed Multi-trader Phase 2 with a 46-day candidate-only target schema migration, exact old/new logical preservation, normalized trade projection, Agent views, rollback/drift/FK gates, 60 pinned backend tests, and unchanged tracked DB/API/static hashes.
- [x] 2026-07-19 - Completed Multi-trader Phase 3 with an exact 21-document canonical migration, zero-unaccounted 27/2 parity, private read/admin handlers, atomic writes, candidate projection, 65 pinned backend tests, and unchanged legacy/runtime/data/publication boundaries.
- [x] 2026-07-19 - Completed Multi-trader Phase 4 with 9 pure Node tests, normal/static builds, fixture-only multi-trader rendering/admin/statistics/download contracts, generalized K-line color/shape markers, and no current consumer/route/publication switch.
- [x] 2026-07-19 - Completed the authorized Phase 5 offline boundary and completion audit, then passed the real macOS TV receipt after provider-subprocess and ticker/exchange routing hardening; current totals are 13 pair tests, 80 backend tests, 10 frontend tests, real-browser acceptance, actual candidate preservation, local SPY/QQQ static export, and truthful Windows-receipt gating.
- [x] 2026-07-19 - Completed Phase 5 after real Windows surfaced and verified portability fixes; both macOS/Windows TV receipts now pass exact SPY/QQQ RTH 390/78, candidate/integrity/FK/grandfathered preservation, and tracked-DB byte protection.
- [x] 2026-07-19 - Completed the Coding/Data Update operating-modes plan with 146 fixtures, accepted independent implementation review, frozen runtime/data/provider/publisher boundaries, and lifecycle reconciliation commit `4f6f2e0937ba5580e170e32ea7fd17718b7b68e3`.
- [x] 2026-07-19 - Completed Phase 5 with 35 fixtures, contract-text enforcement, 19/19 pinned backend tests, compileall, frontend build, DB integrity, and explicit deferred real-run evidence.
- [x] 2026-07-19 - Completed Phase 4 config/CI integration, exact command ordering enforcement, 29 fixtures, unchanged job names, and zero Pages workflow diff.
- [x] 2026-07-19 - Completed Phase 3 Data Update carrier map, existing-test/runbook/publisher compatibility inspection, and explicit future-run evidence boundaries.
- [x] 2026-07-19 - Completed Phase 2 legacy metadata migration, compact routers, focused read-only checker, governed external-root composition, and 26 Coding/lifecycle fixtures.
- [x] 2026-07-19 - Completed Phase 1 single authority contract, accepted decision, constrained plan/review/index/roadmap/state-block formats, and fixture-carrier attestation.
- [x] 2026-07-19 - Completed Phase 0 baseline, exact manifest revalidation, authority freeze, read-only contract/hash capture, governed checker, startup budget, and no-runtime/data/provider/publisher mutation proof.

- [x] 2026-07-18 - Confirmed the clean startup baseline at `codex/project-harness@8c6851d8f469e7a84471cd2900b00b3d9dcbdf07`; `main` and `origin/main` remained at `c262ba0`.
- [x] 2026-07-18 - Installed the missing governed harness artifacts without overwriting pre-existing startup/state files; plan review advanced from `review-001: revise` to `review-002: approve` before activation.
- [x] 2026-07-18 - Recovered SPY 2026-05-15, 2026-06-30, and 2026-07-01 from named historical DBs through a verified candidate and drift-checked atomic promotion; 43 -> 46 days.
- [x] 2026-07-18 - Added shared DB write locking, consistent snapshots, identity/byte/logical drift tokens, rollback-protected promotion, and candidate-first rebuild with date/non-market superset gates.
- [x] 2026-07-18 - Added 15 focused DB/rebuild safety tests and passed the complete 19-test backend suite plus compile checks in an isolated pinned environment.
- [x] 2026-07-18 - Corrected startup/product/architecture/data/publication docs, expanded governed local/PR checks, and recorded excluded audit follow-ups without implementing them.
- [x] 2026-07-18 - Deleted only the authorized stale tracked publication outputs under `docs/` plus zero-byte `.codex`; active Pages remains DB -> `frontend/public/reviews` -> `frontend/dist` -> `gh-pages`.
- [x] 2026-07-18 - Passed frontend production build and real-browser Review/Backtest regression for SPY 2026-07-17 using a temporary SQLite backup of the 46-day DB.
- [x] 2026-07-18 - Passed governed checker, structural validator (`100/100`), startup-document budget, lifecycle links, database integrity/foreign keys, and whitespace checks.
- [x] 2026-07-18 - Independent implementation review returned `accept` with `high` confidence; plan moved to completed with no commit or remote action.
- [x] 2026-07-18 - Standardized local page acceptance from the repository root with a consistent `/tmp` DB snapshot, fail-closed port checks, owned process-group cleanup, configurable Vite API proxy, HTTP 200 checks, and tracked-DB hash preservation. Existing 8000/5173 services were closed only after explicit follow-up authorization.
- [x] 2026-07-18 - Independent launcher diff review returned `accept` with `high` confidence; its sole cache-cleanliness observation was resolved before final status capture.
- [x] 2026-07-19 - Closed the acceptance-report rework items: TIME_WAIT-safe port probing, signal-safe cleanup, committed-plan lifecycle indexes, and CI-enforced launcher syntax checking.

## Historical Redirects

Long-term history remains in Git, completed execution plans, decisions, and evidence. This file retains only current lifecycle truth and bounded outcomes.
