# Phase 4 Harness And CI Integration Evidence

- Baseline: `ad6aff1`
- Authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Work unit: `phase-4`

## Delivered

- Added exact `python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated` to `.harness/config.json` immediately after operating-mode fixtures.
- Added the same exact direct `run` scalar to the existing `Harness structure` job immediately after operating-mode fixtures.
- Added the checker to the governed artifact set and composed a real legacy-tolerated audit from `scripts/check-project-harness.py`; minimal profile remains excluded.
- Extended constrained workflow/config fixtures to require the command and adjacency, including external-root governed and minimal-profile behavior.

## Boundary Proof

| Boundary | Evidence |
| --- | --- |
| CI job display names | unchanged: `Harness structure`, `Backend checks`, `Frontend build` |
| Workflow change | exactly one named audit step/direct run scalar in the existing harness job |
| Runner/trigger | unchanged |
| Pages publisher | unchanged SHA-256 `baaf5ad092bf35d29a6a33ba9083c82768bcb6c4c80169d83fdcf5c8370d5b37` |
| Current legacy history | composed audit pass: 0 malformed checkpoints, 0 errors |

## Verification

| Check | Result |
| --- | --- |
| `python scripts/check-project-harness.py --root . --profile governed` | pass; durable audit composed |
| `python scripts/check-operating-modes.py --root .` | pass; exact config/workflow ordering present |
| `python -m unittest scripts.tests.test_operating_modes` | pass: 171 tests |
| `python -m unittest scripts.tests.test_durable_checkpoint` | pass: 35 tests |
| `python scripts/check-startup-doc-budget.py` | pass; no hard limit |
| `git diff --check` | pass |

Phase 4 exit gate is satisfied. No hosted workflow run, push, PR, or Pages action was performed or authorized.
