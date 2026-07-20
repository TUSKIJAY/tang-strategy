# Phase 3 Durable Checkpoint Checker Evidence

- Baseline: `c38430b`
- Authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Work unit: `phase-3`

## Delivered

- Added read-only `scripts/check-durable-checkpoint.py` with exact baseline/staged preflight, postflight, and audit carriers.
- Implemented exact request/receipt keys, immutable request identity, clean/absent entry, Git blob/full SHA-256 post-images, exact operations/paths, and unchanged unrelated dirty tuples.
- Implemented detached/merge/rebase/cherry-pick/branch/HEAD/index guards and exact-path scope checks for all eleven kinds.
- Implemented generated-output, credential-path, added-line secret/PEM, UTF-8/binary, per-file, live OPT screenshot, and 26,214,400-byte aggregate gates.
- Implemented exact seven-trailer postflight, outcome matrix, legacy-tolerated audit, malformed present-trailer failure, v2 expected-kind claims, and one-shot/standing authority enforcement.
- Added OPT template authority triplet defaults so new records can opt in explicitly without inheriting Git authority.

The checker contains no Git mutation path. Tests perform Git writes only inside isolated temporary fixture repositories to prove the read-only checker against real index/commit objects.

## Adversarial Matrix

The 35 fixtures cover clean success; staged/pre-dirty/create/detached/operation-in-progress/branch/HEAD/blob/post-image/operation mismatches; secret/generated/binary gates; harmless token/placeholders; exact 1,688,940-byte live screenshot pass; 5,242,881 screenshot, 1,048,577 text, and 26,214,401 aggregate rejection; unchanged/changed unrelated tuples; valid/missing/malformed trailers; legacy history; invalid kind/outcome; one-shot reuse; standing kind escape; missing v2 expected checkpoint; all eleven scope kinds; and before/after read-only status equality.

## Verification

| Check | Result |
| --- | --- |
| `python scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated` | pass: 0 current checkpoints, 0 errors; v1 history tolerated |
| `python -m unittest scripts.tests.test_durable_checkpoint` | pass: 35 tests |
| `python scripts/check-project-harness.py --root . --profile governed` | pass |
| `python scripts/check-operating-modes.py --root .` | pass |
| `python scripts/check-startup-doc-budget.py` | pass; no hard limit |
| `git diff --check` | pass |

Phase 3 exit gate is satisfied. Harness/config/workflow composition remains Phase 4 scope.
