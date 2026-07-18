# Progress

## Current Status

<!-- operating-modes-state:start -->
- Current plan: `2026-07-19-tang-strategy-coding-and-data-update-modes-plan`
- Lifecycle status: `Active`
- Current phase: `phase-6`
- Phase state: `in-progress`
- Next gate: `phase-6-remediation`
<!-- operating-modes-state:end -->

2026-07-19: Phase 5 boundary commit `28629a59a2eb7d0fdce362e2754d8476b7f4aa8e` 后的独立实施评审 `implementation-review-001` 返回 `revise`、置信度 `high`。当前为 `phase-6:in-progress`，next gate 为 `phase-6-remediation`：修复 constrained lifecycle false-pass、review/index 对账和 focused checker 越界扫描问题，再进行全套复验与新一轮独立评审。真实 provider/IB/DB update/Tang input/push/Pages/hosted evidence仍未授权、未执行、未冒充 pass。

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

- [ ] Active operating-modes plan is at `phase-6:in-progress`; remediate `implementation-review-001` findings and obtain a fresh qualifying implementation review.

## Blocked

- [ ] None.

## To Do

- [ ] Keep remediation limited to the recorded implementation-review findings, then rerun focused/composed/native verification and request a fresh independent review.
- [ ] At each verified lifecycle/Phase boundary, use the plan's standing authority for one scoped local commit; push, PR, Pages publish, merge, branch protection, environment approval, and remote configuration still require separate authority.
- [ ] Record-only follow-ups remain in `docs/optimization/2026-07-18-repository-audit-followups.md`; they are not approved work.

## Completed

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
