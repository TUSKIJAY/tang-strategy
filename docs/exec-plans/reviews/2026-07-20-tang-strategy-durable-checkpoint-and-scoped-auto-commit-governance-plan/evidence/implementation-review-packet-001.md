# Durable Checkpoint Implementation Review Packet 001

- Plan: `2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan`
- Revision: `v2-review-foldback-2026-07-20`
- Plan author ID: `codex-plan-author-2026-07-20-durable-checkpoint`
- Bootstrap schema: `operating-modes-v1`
- Implementation baseline: `ff4d309c8013b204cd52db294edc0659944a3dc1`
- Frozen implementation commit: `b5c51429387c9ee3b16ccafd762f5c65c1a0df8a`
- Authority: `user-instruction:2026-07-20-execute-durable-checkpoint-governance-plan`
- Local commit authority: `user-instruction:2026-07-20-standing-durable-checkpoint-plan-local-commits`
- Remote authority: `none`

## Review Request

Independently inspect the frozen implementation and repository evidence. Verify that the plan's Phase 0–6 scope is complete, the checker remains read-only, v1 compatibility is preserved, v2 checkpoint/review chains fail closed, CI integration is bounded, and no runtime/data/publication/remote boundary changed. Return exactly one verdict: `accept`, `revise`, or `reject`.

## Frozen Manifest

The following SHA-256 values are from commit `b5c5142` and cover all 28 files changed from the clean implementation baseline `ff4d309`.

| SHA-256 | Path |
| --- | --- |
| `bfadf45dd3bd6b3ffe5a2cab13096bab3860268a22488fa98a54e9c70339559c` | `.github/workflows/project-harness.yml` |
| `728ce60323a6273d87a775d53331aa04e986f4bf23f2ea69a36417a336a257e0` | `.harness/config.json` |
| `c65313627a3729faf2720645b255088357ef01439cfe5e5f59f4d8acc9dff0ba` | `AGENTS.md` |
| `26f8b68015b189cd7e3cebbfd57b1a6db1385912ed6a4e919f1e0672ecdc5db8` | `HANDOFF.md` |
| `b93e1d35f799ba0f42d5845f032f1b25a8fc6b24abc520bcfc3f6710cd1186dc` | `INSTRUCTIONS.md` |
| `ebdfbfc90a87ffc16dab05242cd22c5dd261fc158f4f7acd945ca70057db3b9b` | `PROGRESS.md` |
| `8eea46b886d91dd095fd6233cd793b2daab8a0b8827b4aef5bb415345e9b89ff` | `docs/README.md` |
| `d05a8b989f0590806f1ec621690cfe7322f08cf7b76992cd6ed6b3e83c00ec38` | `docs/decisions/2026-07-20-durable-checkpoint-governance.md` |
| `c6b126723cbc32ab250abe1ee4c5049b4174e8e4ef272537e1fefd4fb9909111` | `docs/decisions/index.md` |
| `7461e8a82a4f0c2634c34b32c35fedf810a2539dabdaebf14779643ea8093be9` | active plan |
| `89481157cbfdd81c7c98bb1b62aa4f678fd9faf9d6070c611930aa34fe436204` | `docs/exec-plans/active/index.md` |
| `257ea5c4649457805503844be9624b7d8cd216e85b29f657b600ee00116ccd3b` | `docs/exec-plans/plan-template.md` |
| `cbb15591a175a6e5385fead8489ef24c960b5a7518cdf477eddfd97ffe6c1dd3` | `evidence/phase-0-baseline.md` |
| `e03fc00d30a5229009edce7c75c1b9387e87ce355488477e901787ff6773ecc0` | `evidence/phase-1-contract-and-adr.md` |
| `602ae7de2daa4683d8bd764352409c6efc4e0807a279ee7597f1f865b94e0e9a` | `evidence/phase-2-v2-schema.md` |
| `98b8f885756f5f6ba04e48223c5219021bbffe3c256417022191340ddb137934` | `evidence/phase-3-checker.md` |
| `c8a7af5838eee2eec5e3030f3d40af0a00c6f0c6e68eb3c78bf6d6c52e5a387d` | `evidence/phase-4-integration.md` |
| `08745efaf0befae0a0afa76600cf730ddf840ac99d402c2d6d6a8fa5b6a429cb` | `evidence/phase-5-compatibility.md` |
| `7090ac89080bea180e873e3b7315d560b8c291d998d3945ace77f6b76db56ad0` | `docs/exec-plans/reviews/review-template.md` |
| `b19380d9d7aec31365b15f3dace681415c8db4c3a382f35ce4ea37d5c475d935` | `docs/exec-plans/roadmap.md` |
| `2f8af0a7249d5b528913403c5bc097a62973f968e8d5f2dfb2170456ddc66c35` | `docs/operating-modes.md` |
| `4a8cca264df2585e1b8a51492fac28445837afb5dd0b1d2a2a7aeafe0698f077` | `docs/optimization/SOP.md` |
| `500fa88dd49fc49609535a506eafb7ead4590d69ad8b78c6544d8a91ae2b2f75` | `docs/optimization/record-template.md` |
| `ff60dc0d6af60bf02f82ceb062b958ef14e351f4c58c9107ef05954af0020c71` | `scripts/check-durable-checkpoint.py` |
| `04fa3f04e973b46f05b8f7c366afc8dacb15892b611bde633af356ce62581943` | `scripts/check-operating-modes.py` |
| `5481c14507cd70462f3c0263e201a4fa4e9298a3cc56c34a99a340ac7971493b` | `scripts/check-project-harness.py` |
| `021f06ee6d06a26b903b8851d117da62b97a65cb7844f94b66ea17995739592f` | `scripts/tests/test_durable_checkpoint.py` |
| `3be90b6900271fd456cd09861e6bbe990bdc9c2b76bf803408a0b6fe0852fd02` | `scripts/tests/test_operating_modes.py` |

## Phase Evidence Index

| Phase | Evidence | Exit result |
| --- | --- | --- |
| 0 | `evidence/phase-0-baseline.md` | clean baseline, ownership and scope frozen |
| 1 | `evidence/phase-1-contract-and-adr.md` | normative contract, ADR, templates accepted locally |
| 2 | `evidence/phase-2-v2-schema.md` | dual-schema/state-machine fixtures pass |
| 3 | `evidence/phase-3-checker.md` | read-only preflight/postflight/audit and safety fixtures pass |
| 4 | `evidence/phase-4-integration.md` | governed harness and bounded CI integration pass |
| 5 | `evidence/phase-5-compatibility.md` | deterministic migration and v1 bootstrap compatibility pass |

## Verification Matrix

| Check | Result |
| --- | --- |
| governed harness + composed audit | pass |
| direct operating-modes checker | pass; Proposed v1, Active bootstrap v1, four Completed legacy/v1 subjects |
| operating-modes fixtures | 171/171 pass |
| durable-checkpoint fixtures | 38/38 pass, including review target strict-ancestry cases |
| startup document budget | pass; advisory only, no hard limit |
| frontend contract tests | 38/38 pass |
| frontend normal/static builds | pass; generated `frontend/dist` removed afterward |
| SQLite read-only integrity/FK | `ok`; 0 foreign-key rows |
| tracked DB SHA-256 | `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` |
| protected Terminal UI plan/reviews and four Completed plans | byte-exact vs `ff4d309` |
| runtime/data/content/publisher/runbook | byte-exact vs `ff4d309`; no scoped diff |
| `git diff --check` | pass |

## Environment Observation

The complete backend suite is outside this governance-only plan's required matrix and all backend/runtime files are byte-exact. It was nevertheless run as an extra smoke check. On Windows, 77/78 tests pass; `test_post_promotion_backup_cleanup_failure_keeps_content_and_db_coherent` errors during `TemporaryDirectory` teardown because `live.db` remains locked. The same teardown-only result reproduces under system Python 3.14 and a clean temporary Python 3.12.12 environment with pinned repository dependencies. Assertions before teardown do not fail. WSL without repository dependencies is not counted. This is recorded as a pre-existing, unrelated portability observation and was not modified under this plan.

## Authority And Boundary Confirmation

- All eight implementation commits are local on `codex/project-harness`; no push occurred.
- The first commit `ff4d309` contains only separately authorized pre-existing governance products; implementation comparison starts from that clean boundary.
- This bootstrap plan remains v1 and has no retroactive `Tang-*` trailers.
- No push, PR, merge, Pages publication, hosted check, provider/broker action, tracked data/content write, or remote administration occurred or is authorized.
