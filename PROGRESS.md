# Progress

## Current Status

2026-07-18: governed harness、三日数据恢复、rebuild fail-closed、文档真理化、授权旧输出清理、全量验证与独立实施验收均已在本地完成。最终独立 verdict 为 `accept` (`high` confidence)。tracked DB 为 46 天, 原 43 天与 strategies/teaching hashes 不变。plan 已移动到 completed。工作树保持未 stage/未 commit; 未 push、publish、merge、创建 PR 或修改任何远端设置。

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

## Historical Redirects

Long-term history remains in Git, completed execution plans, decisions, and evidence. This file retains only current lifecycle truth and bounded outcomes.
