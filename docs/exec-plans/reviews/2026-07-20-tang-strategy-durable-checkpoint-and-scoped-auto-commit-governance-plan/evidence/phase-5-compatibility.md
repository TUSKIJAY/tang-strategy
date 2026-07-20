# Phase 5 Compatibility, Migration, And Bootstrap Evidence

- Baseline: `6f60927e8fdebfe783d933ec8f05326aa1527503`
- Authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Work unit: `phase-5`

## Delivered

- Made v1-to-v2 migration boundaries deterministic: Proposed only at revision or activation; Active only at phase transition.
- Required exact v1-key retention, appended v2 keys, state-table derivation, and authority defaults of `none` without a matching explicit instruction.
- Froze existing v1 Completed plans and v1 reviews without historical checkpoint or metadata backfill.
- Declared this Durable Checkpoint governance plan an unconditional v1 bootstrap subject through implementation review and closeout; its local commits never receive retroactive `Tang-*` trailers.
- Routed the normative contract and accepted ADR from `docs/README.md` and summarized migration in the execution-plan roadmap.
- Reconciled the active plan, active index, `PROGRESS.md`, and `HANDOFF.md` to the truthful Phase 6 entry state after Phases 0–5.

## Compatibility Proof

| Subject set | Result |
| --- | --- |
| Terminal UI/Trader Registry Proposed plan | passes unchanged as `operating-modes-v1` |
| Durable Checkpoint Active plan | passes as the required v1 bootstrap subject |
| Four existing Completed plans | pass unchanged under legacy-v1/v1 schemas |
| V2 fixtures | pass exact superset/state/authority/checkpoint constraints |
| Historical checkpoint audit | pass with `--legacy-tolerated`; 0 malformed checkpoints |

## Verification

| Check | Result |
| --- | --- |
| `python scripts/check-project-harness.py --root . --profile governed` | pass |
| `python scripts/check-operating-modes.py --root .` | pass; Proposed, Active, and four Completed subjects enumerated |
| `python -m unittest scripts.tests.test_operating_modes` | pass: 171 tests |
| `python -m unittest scripts.tests.test_durable_checkpoint` | pass: 35 tests |
| `python scripts/check-startup-doc-budget.py` | pass; archive advisory only, no hard limit |
| `git diff --check` | pass |

Phase 5 exit gate is satisfied. No existing plan was migrated, no historical plan or review was rewritten, and no push, PR, merge, publication, provider, broker, data, or remote action occurred.
