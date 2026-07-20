# Phase 0 Baseline, Dirty Ownership, And Scope Freeze

- Plan: `2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan`
- Revision: `v2-review-foldback-2026-07-20`
- Lifecycle schema for this plan: `operating-modes-v1`
- Implementation-start evidence: `user-instruction:2026-07-20-execute-durable-checkpoint-governance-plan`
- Standing local commit authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Branch: `codex/project-harness`
- Baseline HEAD: `ff4d309c8013b204cd52db294edc0659944a3dc1`
- Baseline index: empty
- Baseline worktree: clean
- Unrelated dirty tuples: none

## Pre-Baseline Ownership Resolution

The pre-existing worktree was classified before Phase 0. Its OPT reorganization, Review Workspace evidence corrections, Terminal UI proposal/reviews, Durable Checkpoint proposal/reviews/activation, and shared lifecycle state were existing governance products, not Phase 0 implementation. The user separately authorized an exact-path local checkpoint for those products. They were verified and committed locally as `ff4d309c8013b204cd52db294edc0659944a3dc1`; no push occurred. This removed every shared/ambiguous manifest collision without stash, reset, partial staging, or adopting pre-dirty content into this plan.

## Frozen Manifest Baseline

| Operation | Path | Baseline SHA-256 / state |
| --- | --- | --- |
| modify | `AGENTS.md` | `a3a5dcd9c2ac19d29707431b1973149e240a755bd73c65059dbe7721a448fa81` |
| modify | `INSTRUCTIONS.md` | `671339389db9f1adf4264591dcec5f61e7086e1372c42cc0a1794c9216227e3a` |
| modify | `.github/workflows/project-harness.yml` | `506dbad475be16069e8a18aec7dd4d015bf391510719d05ca09f544468a62e00` |
| modify | `.harness/config.json` | `89ab9724bb2b3574081d8d47fffd275028dc72e77446fd5e8587bc4318786ee8` |
| modify | `docs/README.md` | `98c036ea89d0ed4b2a180fa4af16e3efc3c446230e1fefd13132a78280f0f7ea` |
| create | `docs/decisions/2026-07-20-durable-checkpoint-governance.md` | absent |
| modify | `docs/decisions/index.md` | `b2e34ffb687ed9113bec8aefcd86608127021d0e4d9c289a8b58f5296c7d1a34` |
| modify | `docs/exec-plans/active/index.md` | `fefe45613f26e901aa944235b9d509609292de86084c50fd9c9c2619d6caee8c` |
| modify | `docs/exec-plans/completed/index.md` | `88fef66feee791b573b16dd40cd55a0ad484a6af73e070cf0617e01623cb806e` |
| modify | `docs/exec-plans/plan-template.md` | `c6eb0d3d8d888c3c01a6182b8175e83c519f3ce841e85eae71360d113840b238` |
| modify | `docs/exec-plans/proposed/index.md` | `df9198878321fce53b68062181dfa8a94151e4f759b1ee5210a4f23af36c84b6` |
| modify | `docs/exec-plans/reviews/index.md` | `eb8ee4fd4b32e8ced9545cd90f978fe64e91ad188d509bcfd1bc8660e606c8a5` |
| modify | `docs/exec-plans/reviews/review-template.md` | `3aa9fc5e1e7a216e59fb6dfdafcbb035f1165f1bb47d09d754de0d404c185142` |
| modify | `docs/exec-plans/roadmap.md` | `afc983bbf04ba83366c5c69bec99160856f2d26bb3aee82f56d87af893386e02` |
| modify | `docs/operating-modes.md` | `e7752521cce0966a420a76a0a1e89f43813ec01eaf22bfe302651809c8989426` |
| modify | `docs/optimization/SOP.md` | `207d808e01218041fa2c030cb38bce3a5e4e03d12f48686765955aa569a7354b` |
| modify | `docs/optimization/record-template.md` | `f7a5a70da796e8b49f9cd2d994b86bb8b1bb1e9a17ea4049b176db62d2721d99` |
| create | `scripts/check-durable-checkpoint.py` | absent |
| modify | `scripts/check-operating-modes.py` | `255fda69620bc23a451e2ae6db51c6132aa302d42ea948aea2ef915889ae531b` |
| modify | `scripts/check-project-harness.py` | `16523445802a23ecc2abe75dcfc76c2b62c0734540ed88ec81d9e40d9652b6e1` |
| create | `scripts/tests/test_durable_checkpoint.py` | absent |
| modify | `scripts/tests/test_operating_modes.py` | `1231e889f56fddbf98b21a14636f2a4d55d5042583b0750a12d8ff8ae959e421` |

The active plan, lifecycle indexes, roadmap, `PROGRESS.md`, and `HANDOFF.md` were also clean at entry. They remain lifecycle reconciliation surfaces and are not adopted from a pre-dirty state.

## Verification

| Check | Result |
| --- | --- |
| `python scripts/check-project-harness.py --root . --profile governed` | pass |
| `python scripts/check-operating-modes.py --root .` | pass |
| `python scripts/check-startup-doc-budget.py` | pass; `PROGRESS.md` archive advisory only, no hard limit |
| `git diff --check` | pass |
| Same-file clean/absent rule | pass for every frozen manifest path |
| Staged files at entry | none |
| Dirty ownership classification | complete; no residual dirty path |

Phase 0 exit gate is satisfied. This evidence is the only Phase 0 bootstrap deliverable and is governed by the separately granted v1 standing local commit authority.
