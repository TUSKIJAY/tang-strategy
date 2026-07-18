# Progress

## Current Status

2026-07-19: `Tang Strategy Coding And Data Update Modes` revision `v2-review-foldback-2026-07-19` 已在 `review-003: approve` 后依据用户明确指令完成 lifecycle activation recording。plan 已从 `proposed/` 移入 `active/`，当前为 `phase-0:not-started`，activation evidence 已记录；本次 activation 不构成 implementation start。next gate 为单独明确的 start/execute instruction 才可进入 Phase 0。用户另行授予本 plan 的 standing local commit authority：每个 lifecycle transition 或 Phase exit 在验证与状态同步通过后，自动形成一个仅含该边界 scoped files 的本地 conventional commit；这不是逐次小改动 commit，也不授予 push/PR/merge/publish 等远端权限。未实施 mode/checker/CI/runtime/data 变更，未 fetch、rebuild、push、publish、创建 PR 或修改远端设置；实时 Git 状态必须由启动命令获取。

## Navigation

| Need | Location |
| --- | --- |
| Stable project rules | `INSTRUCTIONS.md` |
| Current resume point | `HANDOFF.md` |
| Harness configuration | `.harness/config.json` |
| Active operating-modes plan | `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` |
| Completed execution plan | `docs/exec-plans/completed/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md` |
| Verification and reviews | `docs/exec-plans/reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/` |

## In Progress

- [ ] Active operating-modes plan is at `phase-0:not-started`; awaiting a separate explicit start/execute instruction; no implementation has started.

## Blocked

- [ ] None.

## To Do

- [ ] Do not start Phase 0 without a separate explicit start/execute instruction for this active plan.
- [ ] At each verified lifecycle/Phase boundary, use the plan's standing authority for one scoped local commit; push, PR, Pages publish, merge, branch protection, environment approval, and remote configuration still require separate authority.
- [ ] Record-only follow-ups remain in `docs/optimization/2026-07-18-repository-audit-followups.md`; they are not approved work.

## Completed

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
