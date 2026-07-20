# Phase 1 Contract And ADR Evidence

- Baseline: `0e218fc`
- Authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Work unit: `phase-1`

## Delivered

- Appended the normative §9 Durable Checkpoint Contract without renumbering or replacing §§1–8.
- Ratified the accepted durable-checkpoint/v2 ADR and indexed it.
- Added `opt-record` eligibility guidance without converting record-only intake into Git authority.
- Updated plan/review templates with the exact future v2 additions while retaining all v1 plan keys.
- Routed commit guidance and the future audit carrier through `AGENTS.md` and `INSTRUCTIONS.md`.

The contract preserves one human/agent commit actor, a read-only checker, four independent authority dimensions, eleven checkpoint kinds, seven exclusions, exact-path/full-image scope, repository guards, size/secret/generated-output gates, seven trailers, self-reference resolution, and legacy-tolerated history semantics. The live 1,688,940-byte OPT reference remains the positive screenshot class fixture.

## Verification

| Check | Result |
| --- | --- |
| `python scripts/check-project-harness.py --root . --profile governed` | pass |
| `python scripts/check-operating-modes.py --root .` | pass under current v1 implementation |
| `python scripts/check-startup-doc-budget.py` | pass; no hard limit |
| `git diff --check` | pass |
| Live OPT screenshot | pass: 1,688,940 bytes, SHA-256 `57c34ea70bf7c6cab2c983b8feaedb6ad9be6f23fc02262ac7c97a48b156d3c5` |
| Contract/ADR manual comparison | pass against active-plan §§3–6 and Phase 1 exit criteria |

Phase 1 does not implement checker logic, v2 validation, or CI integration.
