# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-19-tang-strategy-coding-and-data-update-modes-plan`
- Lifecycle status: `Active`
- Current phase: `phase-6`
- Phase state: `in-progress`
- Next gate: `phase-6-re-review-r7`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-19
- Project: `Tang Strategy`
- Harness profile: `governed`
- Startup Git evidence: this proposal began from `codex/project-harness@2454ccb7fc1c927f2a52a3bd2db7debe41998594` with a clean worktree/index; rerun the startup commands for live branch/HEAD/status truth
- Lifecycle: `Tang Strategy Coding And Data Update Modes` revision `v2-review-foldback-2026-07-19` is `Active` at `phase-6:in-progress`; remediation-r6 passed bounded verification and fresh independent re-review-r7 is next
- Active plan: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Design reviews: `review-001.md` (revise@v1), `review-002.md` (revise@v1), `review-003.md` (approve@v2)
- Data: tracked DB has 46 market days; recovered 2026-05-15, 2026-06-30, and 2026-07-01; 2026-07-17 remains the regression day
- Implementation boundary: remediation-r6 closes only the implementation-review-006 direct-workflow and operative-Markdown findings; runtime/data/provider/publisher/remote surfaces remain frozen
- Local Git boundary: after a lifecycle transition or Phase exit passes verification and state reconciliation, create one conventional commit containing only that boundary's plan-scoped paths
- Remote boundary: no push, PR, merge, Pages publish, branch protection, environment, or other remote change is authorized

## Resume Checklist

1. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
2. Run the full startup Git commands; do not treat the historical startup evidence above as live HEAD/worktree truth.
3. Preserve any unrelated changes and read `docs/operating-modes.md` plus the active plan execution record.
4. Phase 5 is complete and committed at `28629a59a2eb7d0fdce362e2754d8476b7f4aa8e`; do not recreate that boundary commit.
5. Remediation-r6 is verified; commit that scoped boundary and request fresh independent re-review-r7. Phase 6 requires a qualifying `accept` before completed disposition and lifecycle reconciliation.
6. At each verified lifecycle/Phase boundary, inspect the diff and use the plan's standing authority to stage only scoped paths and create one local conventional commit. Do not push, open a PR, publish, merge, or change remote settings without separate authority.

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
| Phase 0 manifest and authority freeze | pass: four planned additions absent as expected, all existing targets present, read-only hashes captured, no extra path or authority required |
| Phase 1 constrained formats | pass: one normative contract, accepted decision, exact metadata/review/index/roadmap/state-block formats, and carrier inventory |
| Phase 2 lifecycle checker | pass: current focused/composed checks plus 26 temporary-Git Coding/lifecycle fixtures; minimal profile excluded; read-only proof passed |
| Phase 3 Data Update mapping | pass: 19 carrier rows mapped; 18/19 backend tests passed and one calendar prerequisite is explicitly unavailable/not passed; real-run receipts deferred |
| Phase 4 harness/CI integration | pass: config/workflow canonical ordering, 29 fixtures, external roots/profiles, unchanged three job names, and unchanged Pages workflow |
| Phase 5 compatibility closeout | pass: 35 fixtures; 19/19 pinned backend tests; compileall; frontend build; DB integrity/FK; exact trigger/runbook/adapter/rebuild/publisher text |
| Current operating-modes implementation review | `revise`, confidence `high`; remediation required before re-review |
| Phase 6 remediation | pass: 49 fixtures; constrained lifecycle false-pass closed; raw source/prose scanning removed; focused/composed/native/hash verification green |
| Current operating-modes re-review | `implementation-review-002`: `revise`, confidence `high`; optional evidence and gate-prefix remediation required |
| Phase 6 remediation-r2 | pass: 55 fixtures; truthful optional evidence accepted; bogus links rejected; all five Proposed gate prefixes covered |
| Current operating-modes re-review-r3 | `implementation-review-003`: `revise`, confidence `high`; Completed/metadata/Plan-cell remediation required |
| Phase 6 remediation-r3 | pass: 62 fixtures; Completed requires accept; review metadata combinations and exact fixed-row grammar fail closed |
| Current operating-modes re-review-r4 | `implementation-review-004`: `revise`, confidence `high`; Active evidence/table-tokenizer remediation required |
| Phase 6 remediation-r4 | pass: 67 fixtures; Active evidence non-empty; exact table tokenizer and canonical sentinels fail closed |
| Current operating-modes re-review-r5 | `implementation-review-005`: `revise`, confidence `high`; carrier/index/block/review-metadata remediation required |
| Phase 6 remediation-r5 | pass: 79 fixtures; operative carriers, exact index/block grammar, and all-revision structured review metadata fail closed |
| Current operating-modes re-review-r6 | `implementation-review-006`: `revise`, confidence `high`; runnable-workflow and operative-Markdown remediation required |
| Phase 6 remediation-r6 | pass: 96 fixtures; unconditional direct workflow carriers and operative lifecycle/router Markdown fail closed |
| 2026-07-18 recovery-plan implementation review | `accept`, confidence `high` |
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

Commit the verified remediation-r6 boundary and request fresh qualifying independent implementation re-review-r7. Runtime, provider, DB mutation, publication, and remote actions remain unauthorized.

## Handoff Boundary

This file is the current resume index, not project history or an archive. Detailed commands, hashes, test matrices, and review findings remain in the completed plan evidence/review directory.
