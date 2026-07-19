# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan`
- Lifecycle status: `Active`
- Current phase: `phase-5`
- Phase state: `blocked`
- Next gate: `phase-5-external-tv-receipts`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-19
- Project: `Tang Strategy`
- Harness profile: `governed`
- Proposal baseline: `codex/project-harness@25ba77fd9947c504f68cab1c7700d9f5c84d62b4` was clean before the new proposal; rerun startup commands for live Git truth
- Lifecycle: `Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor` revision `v5-round-3-review-foldback-2026-07-19` is Active at `phase-5:blocked`; Phases 0-4, the Phase 5 offline boundary, and the real macOS TradingView receipt passed, while the user explicitly deferred the required Windows receipt until the Windows checkout is prepared
- Active plan: `docs/exec-plans/active/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Authority boundary: local/offline implementation, real TradingView calls for the Phase 5 macOS/Windows receipts, and one plan-scoped stage/commit/push of `codex/project-harness` for Windows transfer are authorized; IB access, tracked DB promotion, Phase 6 cutover/removal, PR, merge, Pages publication, and other remote changes are not
- Completed operating-modes historical startup: `codex/project-harness@2454ccb7fc1c927f2a52a3bd2db7debe41998594` was that earlier plan's clean baseline; it is not the current proposal baseline
- Lifecycle: `Tang Strategy Coding And Data Update Modes` revision `v2-review-foldback-2026-07-19` is `Completed`; implementation-review-013 returned `accept` with `high` confidence and all phases are closed
- Completed plan: `docs/exec-plans/completed/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Current-plan design reviews: `review-001.md` (Kimi revise/high@v2), `review-002.md` (Grok revise/high@v2), `review-003.md` (Kimi approve/high@v3), `review-004.md` (Grok revise/high@v3), `review-005.md` (Kimi revise/high@v4), `review-006.md` (Grok approve/high@v4), `review-007.md` (Kimi approve/high@v5), `review-008.md` (Grok approve/high@v5)
- Review monitor: 10-minute current-task heartbeat `tang-dual-review-loop-monitor` reached its activation stop condition and is removed during closeout
- Completed operating-modes plan reviews: `review-001.md` (revise@v1), `review-002.md` (revise@v1), `review-003.md` (approve@v2)
- Data: tracked DB has 46 market days; recovered 2026-05-15, 2026-06-30, and 2026-07-01; 2026-07-17 remains the regression day
- Implementation boundary: implementation-review-013 accepted stable implementation commit `994f9176eb74778f346710e62ec6dabde55bae9a`; lifecycle reconciliation is recorded at `4f6f2e0937ba5580e170e32ea7fd17718b7b68e3`
- Local Git boundary: user instruction `2026-07-19-commit-and-push-branch-for-windows-phase5` authorizes one plan-scoped stage/commit for the current 75-path checkpoint
- Remote boundary: that same instruction authorizes pushing only `codex/project-harness` for Windows transfer; no PR, merge, Pages publish, branch protection, environment, or other remote change is authorized

## Resume Checklist

1. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
2. Run the full startup Git commands; do not treat the historical startup evidence above as live HEAD/worktree truth.
3. Preserve any unrelated changes and read `docs/operating-modes.md`, the current proposed multi-trader plan, and its review directory/index.
4. The multi-trader plan is Active at `phase-5:blocked`; Phase 0-4, Phase 5 offline evidence, and the real macOS TradingView receipt are complete. Pull the authorized `codex/project-harness` checkpoint on Windows and verify the exact expected HEAD before running the remaining receipt. Do not enter Phase 6 or call IB.
5. Continue only on temporary/candidate SQLite copies under the existing lock/drift contract; do not promote the tracked DB or expose new runtime routes.
6. The completed operating-modes plan remains closed; do not reuse its implementation authority for this proposal.
7. The current transfer instruction authorizes only the named checkpoint commit/push and the Windows real TradingView receipt. No PR, publish, merge, IB, tracked DB action, Phase 6, or other remote mutation is authorized.

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
| Current operating-modes re-review-r7 | `implementation-review-007`: `revise`, confidence `high`; YAML execution/scalar and multiline/raw-code remediation required |
| Phase 6 remediation-r7 | pass: 114 fixtures; PR-main and fail-closed job/step carriers; quoted conditions/modifiers/defaults/runners/duplicates rejected; folded scalar semantics and multiline/raw-code masking verified |
| Current operating-modes re-review-r8 | `implementation-review-008`: `revise`, confidence `high`; unique/direct workflow mapping/order, equivalent-YAML, and nested raw-code remediation required |
| Phase 6 remediation-r8 | pass: 133 fixtures; unique direct workflow mappings and same-job order enforced; equivalent YAML forms normalized; nested raw-code carriers fail closed |
| Current operating-modes re-review-r9 | `implementation-review-009`: `revise`, confidence `high`; branch scalar and YAML-null direct step/name remediation required |
| Phase 6 remediation-r9 | pass: 139 fixtures; branch sequences fully tokenize to strings; empty/non-scalar members and null/scalar step/name forms fail closed |
| Current operating-modes re-review-r10 | `implementation-review-010`: `revise`, confidence `high`; YAML numeric/plain mapping-indicator classification and quoted escape remediation required |
| Phase 6 remediation-r10 | pass: 143 fixtures; numeric and terminal-colon non-string forms fail closed; YAML double-quoted escapes and quoted terminal colons normalize correctly |
| Current operating-modes re-review-r11 | `implementation-review-011`: `revise`, confidence `high`; raw YAML printable-source remediation required |
| Phase 6 remediation-r11 | pass: 145 fixtures; raw YAML-forbidden controls fail closed while valid escaped scalar values remain supported |
| Current operating-modes re-review-r12 | `implementation-review-012`: `revise`, confidence `high`; Unicode raw-range contract wording and boundary fixtures require convergence |
| Phase 6 remediation-r12 | pass: 146 fixtures; YAML-compatible listed raw ranges are authoritative and Unicode boundary behavior is pinned |
| Current operating-modes re-review-r13 | `implementation-review-013`: `accept`, confidence `high`; no implementation finding remains |
| 2026-07-18 recovery-plan implementation review | `accept`, confidence `high` |
| Local page acceptance | pass: root command, `/tmp` SQLite backup, 46 days, integrity `ok`, frontend/OpenAPI HTTP 200, immediate same-port restart, occupied-port refusal, and repeated Ctrl-C cleanup |
| Tracked DB protection | SHA-256 before/after `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` |
| Multi-trader Phase 2 candidate | pass: 46 logical days -> 46 active datasets; 43,425/8,821 ordered bars; logical SHA-256 `f7ca32...70a34` unchanged; 27 groups, 30 events, 4 reported outcomes, 2 contexts; four Agent views |
| Multi-trader Phase 2 safety | pass: fresh/copy migration, at-most/exactly-one dataset, importer supersede, recovery, rebuild semantics, FK rollback, drift/corruption/live-byte protection, 60 pinned backend tests; read-only `git archive HEAD` rehearsal restored the coherent old app/DB/20-file legacy boundary with exact API/static hashes |
| Multi-trader Phase 2 compatibility | pass: API `95132b...0387`, static day `b3d14f...a44a`, 868/192/1 counts, `tang_trades` only; no route/consumer/Pages switch |
| Multi-trader Phase 3 canonical migration | pass: 21/21 pure-render exact, aggregate `f22c58...89a7e`, 20 days, 27 groups, 2 contexts, zero unaccounted, old sources preserved |
| Multi-trader Phase 3 handlers | pass: roles/filters/atomic failure-recovery/candidate projection, 65 pinned backend tests; no new registered route or current consumer switch |
| Multi-trader Phase 4 frontend | pass: 10 pure Node tests, exact current-filter group/context/count/selection download reconciliation, normal/static Vite builds, and real Chromium Review/Backtest/Teaching regression against a temporary 46-day DB; no new route/current consumer switch |
| Multi-trader Phase 5 offline | pass: 13 pair tests, 80 backend tests, compileall, exact `ts`/offset/`t` NYSE gates, pair-level contention lock, offline tracked-target refusal, absolute provider-subprocess bootstrap, SPY/QQQ exchange routing, POSIX/Windows lock branches, workflow YAML, normal/static builds, and current-code candidate preservation |
| Multi-trader Phase 5 external gate | blocked: real macOS TV pair receipt passed at exact RTH 390/78 for SPY/QQQ with temporary candidate acceptance and unchanged tracked DB; the user deferred the Windows real receipt until the Windows checkout is prepared; therefore not `phase-5-complete` and Phase 6 remains forbidden |
| Launcher diff review | `accept`, confidence `high`; final cache-cleanliness observation resolved |
| Git boundary | one plan-scoped checkpoint stage/commit/push of `codex/project-harness` is authorized for Windows transfer; no PR, publish, merge, or remote settings change is authorized |

Detailed operating-modes evidence is under `docs/exec-plans/reviews/2026-07-19-tang-strategy-coding-and-data-update-modes-plan/`.

## Known Non-Blocking Observations

- Future recovery evidence should retain manual value-level secret review; the current evidence was independently checked and is safe.
- A dedicated dual-writer contention/timeout test remains a useful test enhancement; current lock coverage and drift tests passed.
- Browser console recorded only the existing missing `favicon.ico` request (`404`); product APIs and flows returned successfully.
- The isolated backend environment emitted third-party calendar-library deprecation warnings; the 19 tests still passed.
- `actionlint` is not installed in the current shell. The dependency-free checker validated workflow paths, configured checks, exact job names, and ordering. No hosted run was authorized.

## Next Gate

Push the authorized plan-scoped checkpoint to `origin/codex/project-harness`. From the Windows checkout, pull and verify that exact HEAD, then run the same pinned-runtime real TradingView pair receipt. macOS has passed and Windows remains not run. IB, Phase 6, tracked DB promotion, legacy removal, and public/default cutover remain forbidden.

## Handoff Boundary

This file is the current resume index, not project history or an archive. Detailed commands, hashes, test matrices, and review findings remain in the completed plan evidence/review directory.
