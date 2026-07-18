# Optimization Batch · 2026-07-18 Repository Audit Follow-ups

> Record-only intake. This file does not authorize implementation.

| ID | Area | Status | Independent exec plan | Proposed disposition |
| --- | --- | --- | --- | --- |
| OPT-001 | Strategy schema | recorded | yes | Decide schema authority, wire validation, then reconcile v5 |
| OPT-002 | Backend providers | recorded | yes | Confirm product need before removing or implementing stubs |
| OPT-003 | Frontend duplication/dead paths | recorded | yes | Behavioral characterization before consolidation |
| OPT-004 | Kline provenance | recorded | yes | Reconstruct source/generation contract |
| OPT-005 | Auth defaults/rate limit | recorded | yes | Security hardening plan and deployment migration |
| OPT-006 | Docker reproducibility | recorded | yes | Pin/install contract and build-context hygiene |
| OPT-007 | Tracked DB growth | recorded | yes | Compare tracked DB, LFS, release, and seed strategies |
| OPT-008 | Pine/JSON provenance | recorded | yes | Define version/source mapping and drift checks |
| OPT-009 | Branch protection | recorded | yes; remote authority | Required-check and publication-risk design |
| OPT-010 | Actions SHA pinning | recorded | yes | Pinning/renovation policy |

## OPT-001 Strategy Schema And v5 Drift

- Evidence: `strategies/strategy.schema.json` has no importer/test validation consumer; the importer explicitly skips `*schema.json`. The 2026-07-18 audit found `tang_v5_0.json` does not satisfy the schema's current required shape.
- Impact: the repository presents a contract that cannot prevent invalid strategy definitions or clarify whether schema or runtime behavior is authoritative.
- Addressed/remaining: not addressed; current work preserved all strategy JSON and schema files.
- Proposed disposition: decide schema authority, add dependency-light validation to an explicit verification lane, then update schema or v5 from behavior evidence.
- Independent exec plan: required because it changes the strategy contract and may affect scanner/runtime compatibility.
- Exclusion reason: the active plan is limited to data recovery, rebuild safety, docs truth, and harness governance.

## OPT-002 Backend Provider Stubs

- Evidence: `backend/app/providers/ibkr.py` and `polygon.py` are unreferenced stubs; tracked daily fetchers live under `backend/scripts/`.
- Impact: dead abstractions confuse ownership and imply an API that is not implemented.
- Addressed/remaining: remaining; no provider file was deleted or implemented.
- Proposed disposition: first decide whether providers should become injectable runtime adapters or be removed in favor of script-owned acquisition.
- Independent exec plan: required if behavior/import boundaries change; a narrowly approved cleanup may be sufficient if removal is proven safe.
- Exclusion reason: the user explicitly prohibited broad backend/frontend dead-code cleanup in this work.

## OPT-003 Frontend Duplication, Scanner Branches, And Orphan Chart

- Evidence: `ReviewPage.jsx` and `StaticReviewsApp.jsx` contain repeated review helpers; scanner has a separate unreachable activation path; `DailyReviewChart.jsx` has no active import; Playwright is declared without repository specs.
- Impact: fixes can drift between interactive/static modes and unreachable logic obscures the actual signal lifecycle.
- Addressed/remaining: remaining; all listed frontend assets and dependencies were preserved.
- Proposed disposition: add characterization tests for interactive/static payload equivalence and scanner outputs, then consolidate only proven duplicates and remove only proven orphans.
- Independent exec plan: required because Review/Backtest behavior and visual output are regression-sensitive.
- Exclusion reason: no dead-code implementation authority was granted.

## OPT-004 Kline Engine Provenance

- Evidence: `frontend/src/kline/kline-engine.js` is a large core file whose header references unavailable source/generation material; the engine contains optional `m500` support beyond the current DB payload.
- Impact: regeneration, upstream comparison, and review of large engine changes are difficult to reproduce.
- Addressed/remaining: docs now describe the live public contract and optional `m500`; source provenance remains unresolved.
- Proposed disposition: identify/recover the authoritative source or formally adopt the tracked file as hand-maintained, then document a repeatable update/diff procedure.
- Independent exec plan: required.
- Exclusion reason: reconstructing external provenance is not needed for the data/harness safety outcome.

## OPT-005 Default Credentials And Login Rate Limiting

- Evidence: `backend/app/settings.py` contains development fallback passwords/JWT secret; `/api/auth/login` has no rate limiter; frontend stores bearer state in local storage.
- Impact: an exposed deployment using defaults or unlimited login attempts would have weak authentication posture.
- Addressed/remaining: remaining; no credential value was read or changed in this plan.
- Proposed disposition: define environment-specific startup refusal/warnings, secret rotation, rate limiting, and browser token handling with migration/rollback.
- Independent exec plan: required and security-reviewed.
- Exclusion reason: changing authentication/deployment behavior exceeds the authorized data/docs/harness scope.

## OPT-006 Docker Reproducibility

- Evidence: frontend dependencies use floating `latest` declarations despite a lockfile, and the audit found incomplete build-context hygiene/no `.dockerignore` coverage.
- Impact: local Docker results may drift or carry unnecessary context.
- Addressed/remaining: remaining; Docker files and dependencies were not changed.
- Proposed disposition: define lockfile-first installs, pinned runtime/build images, build-context exclusions, and a reproducibility smoke check.
- Independent exec plan: required.
- Exclusion reason: Docker changes are not necessary for the current local recovery and verification.

## OPT-007 Long-Term Tracked DB Growth

- Evidence: the SQLite DB is a binary tracked runtime/Pages input and grows through full-blob Git history; the current contract intentionally retains it.
- Impact: repository clone/history size grows linearly and binary reviews remain opaque.
- Addressed/remaining: immediate data loss and rebuild safety are addressed; storage strategy remains.
- Proposed disposition: compare tracked SQLite, complete tracked seed + generated DB, LFS, release artifacts, and split/delta formats with migration and rollback costs.
- Independent exec plan: required because publication/runtime input would change.
- Exclusion reason: the user explicitly retained tracked SQLite and excluded LFS/release/full-seed migration.

## OPT-008 Pine And JSON Provenance

- Evidence: several strategy JSON `source_file` references are absent or external; Pine files have no automated consumer/synchronizer and some names/versions do not map cleanly.
- Impact: semantic drift between TradingView sources, JSON execution definitions, and docs cannot be measured reliably.
- Addressed/remaining: canonical docs ownership is clarified; provenance/synchronization remains.
- Proposed disposition: inventory source pairs, select authoritative direction, record checksums/version mapping, and add drift reporting without silently rewriting either representation.
- Independent exec plan: required.
- Exclusion reason: strategy semantics were explicitly outside the active implementation scope.

## OPT-009 Branch Protection And Publish Authority

- Evidence: `main` protection was absent in the 2026-07-18 audit; any push to `main` triggers the Pages workflow and force-pushes `gh-pages`. Project-harness checks are validation signals only.
- Impact: an accidental direct push can replace the published site without required checks or review.
- Addressed/remaining: local governed checks are improved; remote protection/environment configuration remains unchanged.
- Proposed disposition: separately decide required checks, direct-push policy, Pages environment approval, emergency path, and owner bypass behavior.
- Independent exec plan: required with explicit remote GitHub authority.
- Exclusion reason: remote settings, branch protection, and Pages approval were expressly not authorized.

## OPT-010 GitHub Actions SHA Pinning

- Evidence: workflows reference floating major action tags such as `actions/checkout@v4`, `actions/setup-python@v5`, and `actions/setup-node@v4`.
- Impact: upstream tag movement changes CI supply-chain inputs without a repository diff.
- Addressed/remaining: remaining; workflow behavior was changed only to run governed/startup checks.
- Proposed disposition: pin trusted SHAs and define an update mechanism that retains readable version annotations.
- Independent exec plan: required or combine with a separately approved CI hardening plan.
- Exclusion reason: the active plan explicitly excluded Action SHA pinning.

## Record Boundary

Every item remains `recorded`. None is approved, active, completed, or implied by the active recovery plan. Promotion to `docs/exec-plans/proposed/` requires a separate explicit user request.
