# Handoff

## Current Snapshot

- Last updated: 2026-07-19
- Project: `Tang Strategy`
- Harness profile: `governed`
- Startup Git evidence: this proposal began from `codex/project-harness@2454ccb7fc1c927f2a52a3bd2db7debe41998594` with a clean worktree/index; rerun the startup commands for live branch/HEAD/status truth
- Lifecycle: `Tang Strategy Coding And Data Update Modes` revision `v2-review-foldback-2026-07-19` is `Active` at `phase-0:not-started`; `review-003: approve` and explicit user activation are recorded; implementation has not started
- Active plan: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Design reviews: `review-001.md` (revise@v1), `review-002.md` (revise@v1), `review-003.md` (approve@v2)
- Data: tracked DB has 46 market days; recovered 2026-05-15, 2026-06-30, and 2026-07-01; 2026-07-17 remains the regression day
- Activation boundary: activation/review/lifecycle documentation only; no mode/checker/CI/runtime/data implementation; the plan's standing local commit rule applies after boundary verification; rerun Git status for live truth
- Local Git boundary: after a lifecycle transition or Phase exit passes verification and state reconciliation, create one conventional commit containing only that boundary's plan-scoped paths
- Remote boundary: no push, PR, merge, Pages publish, branch protection, environment, or other remote change is authorized

## Resume Checklist

1. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
2. Run the full startup Git commands; do not treat the historical startup evidence above as live HEAD/worktree truth.
3. Preserve the complete local activation/lifecycle diff and read the active operating-modes plan.
4. Activation recording is complete. Next lifecycle gate is a separate explicit start/execute instruction for Phase 0.
5. Do not implement Phase 0 or later work until that instruction is given and the Phase 0 entry gate is rechecked.
6. At a verified lifecycle/Phase boundary, inspect the diff and use the plan's standing authority to stage only scoped paths and create one local conventional commit. Do not push, open a PR, publish, merge, or change remote settings without separate authority.

## Verification Evidence

| Check | Result |
| --- | --- |
| DB recovery | pass: 43 -> 46, exactly three additions, original 43-day map and non-market table hashes unchanged |
| DB integrity | pass: `integrity_check=ok`, foreign-key rows `0`, post-promotion SHA-256 `76a885c2...28f8` |
| Rebuild safety | pass: 11 rebuild tests, 4 shared safety tests, actual six-day seed refused against a 46-day temp copy with identical before/after bytes |
| Backend | pass: 19 tests and compileall |
| Frontend | pass: Vite production build, 1746 modules transformed |
| Browser | pass: 46-day dashboard; 2026-07-17 Review assembled at 868/192; 10-day Backtest returned 43 signals and opened 2026-07-17; 1m/5m and Step worked |
| Governed harness | pass: local checker, lifecycle links, startup budget, and structural validator `100/100` |
| Operating-modes proposal baseline | pass: governed audit found 21/21 harness artifacts; current checker passed despite revalidated stale lifecycle truth, demonstrating the execution-layer gap |
| Independent review | `accept`, confidence `high` |
| Local page acceptance | pass: root command, `/tmp` SQLite backup, 46 days, integrity `ok`, frontend/OpenAPI HTTP 200, immediate same-port restart, occupied-port refusal, and repeated Ctrl-C cleanup |
| Tracked DB protection | SHA-256 before/after `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` |
| Launcher diff review | `accept`, confidence `high`; final cache-cleanliness observation resolved |
| Git boundary | standing local commit authority applies only after verified lifecycle/Phase boundaries and only to exact scoped paths; no push, PR, publish, merge, or remote settings change |

Detailed evidence is under `docs/exec-plans/reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/`.

## Known Non-Blocking Observations

- Future recovery evidence should retain manual value-level secret review; the current evidence was independently checked and is safe.
- A dedicated dual-writer contention/timeout test remains a useful test enhancement; current lock coverage and drift tests passed.
- Browser console recorded only the existing missing `favicon.ico` request (`404`); product APIs and flows returned successfully.
- The isolated backend environment emitted third-party calendar-library deprecation warnings; the 19 tests still passed.
- `actionlint` is not installed in the current shell. The dependency-free checker validated workflow paths, configured checks, exact job names, and ordering. No hosted run was authorized.

## Next Gate

Separate explicit start/execute instruction for Phase 0 of the active revision `v2-review-foldback-2026-07-19`. Activation is already recorded but does not grant implementation start. Verified lifecycle/Phase closeouts use the standing scoped-local-commit authority; remote actions require separate authority.

## Handoff Boundary

This file is the current resume index, not project history or an archive. Detailed commands, hashes, test matrices, and review findings remain in the completed plan evidence/review directory.
