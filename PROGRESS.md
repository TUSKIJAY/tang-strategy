# Progress

## Current Status

2026-07-19: 本地验收报告返工已完成。启动器允许 TIME_WAIT 后立即重用端口，同时仍拒绝真实监听者；cleanup 会在关闭自身进程组和删除临时目录期间忽略后续信号。相同端口连续启动、连续 Ctrl-C、HTTP 200、46 天临时 DB、`integrity_check=ok` 及 tracked DB SHA-256 不变均已实测。completed/reviews 索引已回写 `a70be643...`，CI harness job 已接入 `bash -n`。本地 diff 未 stage/未 commit；未 fetch、rebuild、push、publish、创建 PR 或修改远端设置。

## Navigation

| Need | Location |
| --- | --- |
| Stable project rules | `INSTRUCTIONS.md` |
| Current resume point | `HANDOFF.md` |
| Harness configuration | `.harness/config.json` |
| Completed execution plan | `docs/exec-plans/completed/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md` |
| Verification and reviews | `docs/exec-plans/reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/` |

## In Progress

- [ ] None.

## Blocked

- [ ] None.

## To Do

- [ ] Maintainer reviews the complete local unstaged/untracked diff.
- [ ] Any future stage, commit, push, PR, Pages publish, merge, branch protection, environment approval, or remote configuration requires separate authority.
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
