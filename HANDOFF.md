# Handoff

## Current Snapshot

- Last updated: 2026-07-18
- Project: `Tang Strategy`
- Branch/HEAD: `codex/project-harness@8c6851d8f469e7a84471cd2900b00b3d9dcbdf07`
- Harness profile: `governed`
- Lifecycle: local plan completed after independent `accept` (`high` confidence)
- Data: tracked DB has 46 market days; recovered 2026-05-15, 2026-06-30, and 2026-07-01; 2026-07-17 remains the regression day
- Git state: complete local diff is unstaged/uncommitted; `main` and `origin/main` remain at `c262ba0`
- Remote boundary: no push, PR, merge, Pages publish, branch protection, environment, or other remote change

## Resume Checklist

1. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
2. Run `git status --short --branch` and preserve the complete local diff.
3. Read the completed plan, evidence reports, and `implementation-review-001.md`.
4. Review the diff. Do not stage, commit, push, or open a PR without a new explicit request.
5. If future work starts, route it through the governed lifecycle and keep record-only optimization items non-authorizing.

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
| Independent review | `accept`, confidence `high` |
| Git boundary | no staged files, commit, push, PR, publish, merge, or remote settings change |

Detailed evidence is under `docs/exec-plans/reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/`.

## Known Non-Blocking Observations

- Future recovery evidence should retain manual value-level secret review; the current evidence was independently checked and is safe.
- A dedicated dual-writer contention/timeout test remains a useful test enhancement; current lock coverage and drift tests passed.
- Browser console recorded only the existing missing `favicon.ico` request (`404`); product APIs and flows returned successfully.
- The isolated backend environment emitted third-party calendar-library deprecation warnings; the 19 tests still passed.
- `actionlint` is not installed in the current shell. The dependency-free checker validated workflow paths, configured checks, exact job names, and ordering. No hosted run was authorized.

## Next Gate

Maintainer review of the local unstaged diff. Any Git closeout or remote action requires a new explicit request.

## Handoff Boundary

This file is the current resume index, not project history or an archive. Detailed commands, hashes, test matrices, and review findings remain in the completed plan evidence/review directory.
