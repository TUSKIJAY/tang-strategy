# Durable Checkpoint And operating-modes-v2 Governance

- Status: Accepted
- Date: 2026-07-20
- Scope: repository lifecycle products, scoped local Git checkpoints, and dual-schema lifecycle validation
- Supersedes: ad-hoc lifecycle commit packaging and self-referential reconciliation-SHA follow-ups for future v2 subjects

## Decision

Tang Strategy adopts the normative durable-checkpoint contract in `docs/operating-modes.md` and a future-facing `operating-modes-v2` constrained schema. A human or coding agent remains the only Git mutation actor; the checkpoint checker is read-only. Underlying work, lifecycle transition, local checkpoint, and remote/publication authority are separate.

Exactly eleven checkpoint kinds and seven exclusions define eligible work products. Checkpoint requests use full-file clean-entry ownership, literal paths, complete post-images, safety/size/secret gates, required Git trailers, and baseline/staged/postflight evidence. Pre-v2 trailer-less history remains advisory under `--legacy-tolerated`; malformed present trailers and v2 checkpoint claims fail closed.

V2 retains every exact v1 plan key, adds structured work-unit/review/checkpoint fields, and resolves commit self-reference through Git trailers plus later review target SHAs. Existing v1 Completed plans remain frozen. Proposed/Active v1 plans migrate only at documented future transitions. The governance plan that introduces the contract remains v1 for its entire lifecycle.

## Consequences

- Completed lifecycle products can be locally checkpointed without sweeping unrelated dirt.
- No green check or lifecycle verdict implicitly grants Git or remote authority.
- Future v2 plan/review state is more explicit and mechanically fail-closed.
- The checker, harness, CI carrier, fixtures, and migration policy must remain aligned with the normative contract.
