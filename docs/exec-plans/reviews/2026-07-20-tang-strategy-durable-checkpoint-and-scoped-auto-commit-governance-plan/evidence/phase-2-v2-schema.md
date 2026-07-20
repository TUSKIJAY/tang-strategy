# Phase 2 operating-modes-v2 Schema Evidence

- Baseline: `5df6159`
- Authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Work unit: `phase-2`

## Delivered

- Appended normative §10 after the complete §9 and changed the contract header to `operating-modes-v2` only after both sections existed.
- Kept all seventeen exact v1 keys and added the ten exact space-separated v2 keys in required order.
- Kept all nine review keys and added final `Review target commit` only for v2 reviews.
- Added exact schema dispatch for legacy-v1, v1, and v2 without changing v1 fixtures.
- Enforced v2 authority triplets, ordered checkpoint kinds, compatibility pointers, review target commits, blocker iff-rule, and no v2 reconciliation SHA.
- Enforced the primary/remediation state matrix, dedicated entry gates, expected checkpoint kinds, and sequential remediation numbering.

## Fixture Coverage

Positive fixtures cover Proposed, activated/not-started, primary ready/running/blocked, awaiting implementation review, remediation ready/running/blocked/complete, accepted Active, and implemented Completed states. Negative fixtures cover missing/aliased/reordered keys, missing/malformed target commits, invalid authority triplets, missing blocker evidence, phase/work cross-products, and remediation numbering. All pre-existing v1/legacy fixtures remain unchanged.

## Verification

| Check | Result |
| --- | --- |
| `python scripts/check-project-harness.py --root . --profile governed` | pass |
| `python scripts/check-operating-modes.py --root .` | pass; current v1 plans remain valid under v2 contract implementation |
| `python -m unittest scripts.tests.test_operating_modes` | pass: 167 tests |
| `python scripts/check-startup-doc-budget.py` | pass; no hard limit |
| `git diff --check` | pass |

Phase 2 exit gate is satisfied. Checkpoint preflight/postflight/audit implementation remains Phase 3 scope.
