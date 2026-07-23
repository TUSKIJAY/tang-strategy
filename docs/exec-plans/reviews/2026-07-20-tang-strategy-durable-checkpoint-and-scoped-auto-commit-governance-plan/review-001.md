# Review 001 — Tang Strategy Durable Checkpoint And Scoped Auto-Commit Governance

- Review target: `docs/exec-plans/proposed/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan.md`
- Review target revision: `v1-proposal-2026-07-20`
- Review type: design
- Reviewer ID: `grok-build-design-reviewer-2026-07-20-durable-checkpoint-r1`
- Plan author ID: `codex-plan-author-2026-07-20-durable-checkpoint`
- Independence declaration: `attested`
- Evidence method: Independent read of exact revision `v1-proposal-2026-07-20` at SHA-256 `0e93eaabcdd323f5d3d6094f978aa71f722370d23c674c99bcdea64a06c3d62e`; live re-check of `docs/operating-modes.md` section map and constrained plan keys, `scripts/check-operating-modes.py` `PLAN_KEYS`/`REVIEW_KEYS`, `.harness/config.json`, `.github/workflows/project-harness.yml` harness job structure, current branch/HEAD `codex/project-harness@115d2cfee1d7e408b5ecd4465db73064c0d717b5`, multi-product dirty worktree, OPT screenshot sizes under `docs/optimization/`, completed-plan multi-commit reconciliation history, and governed/operating-modes checkers green for this Proposed surface. This reviewer context did not draft the plan. No implementation, data write, provider/broker, stage/commit/push, PR, merge, Pages, or remote administration was performed.
- Verdict: revise
- Confidence: high

## Scope Checked

- Proposal provenance, Lane 3 justification, and independence from Terminal UI product plan
- Authority model vs auto-commit language vs read-only checker non-goal
- Eleven checkpoint kinds, seven exclusions, fail-closed staging rules, trailer contract
- Proposed `operating-modes-v2` field package vs live v1 constrained keys/checker grammar
- Change manifest, phases 0–6, CI/harness integration, bootstrap/migration, rollback
- Live evidence of OPT screenshot sizes, existing `operating-modes.md` §8, workflow job/step carriers, and current dual Proposed state

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| blocking | §2.1–2.2, §3, §5, §6, Phase 3, non-goals | The plan simultaneously promises “scoped local auto-commit”, specifies an automatic commit actor’s abort/unstage/trailer duties (§5), and forbids a workflow engine while limiting the new tool to a **read-only** checker. It never freezes **who** may run `git add`/`git commit`, under what durable authority token, with what agent/human procedure, or how preflight inputs (kind, manifest, authority reference) are supplied. Without that, implementers cannot know whether “checkpoint” is a policy document, an agent playbook, or a future write-capable tool. | Freeze a single execution model in operative contract language: e.g. (A) agent/human performs exactly one scoped commit under explicit or standing durable Git authority; checker only preflights/postflights/audits; or (B) a named write tool is in scope (then remove the “no workflow engine / read-only only” non-goal and define its authority gates). Freeze `Tang-Authority` value grammar and how standing plan-scoped commit authority is recorded/verified. Remove or redefine “auto-commit” so it cannot be read as unattended Git mutation. |
| blocking | §5.6 size gate vs §4.1 `opt-record` | Staged files default to a **1 MB governance** size fail. Live OPT evidence already exceeds that: `docs/optimization/2026-07-19-01-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png` is **1,688,940 bytes**. Several other current OPT PNGs are 260–470 KB; a multi-file OPT batch can exceed 1 MB even when no single file does, depending on whether the gate is per-file or aggregate. As written, `opt-record` cannot commit the real optimization surface this repo already uses. | Make size policy kind-aware and evidence-based: freeze per-file vs aggregate; raise/exempt tracked screenshot binaries under `docs/optimization/**/screenshots/`; keep tight limits for Markdown/scripts; add fixtures that pass the actual reference PNG and fail only true outliers/secrets. |
| blocking | Phase 3 audit + Phase 4 CI | CI is told to run the checkpoint checker after operating-modes fixtures, but audit semantics on **pre-v2, trailer-less history** are not frozen. Phase 3 only says audit “should pass with no checkpoint history **or** report existing trailer-less commits.” If audit is hard-fail on missing trailers, every PR on current history fails. If it only reports, CI must not treat report-only gaps as red without an explicit rule. | Freeze CI mode and exit policy: e.g. PR/governed default runs `audit --legacy-tolerated` (or equivalent) that **warns** on pre-policy commits and **fails** only malformed/present-but-invalid trailers or post-policy gaps; hard historical completeness is out of scope. Pin the exact command(s) in `.harness/config.json` and the harness job `run` scalar. |
| medium | §8.2 / Phase 1 “Add §8 / §9” vs live `docs/operating-modes.md` | Live contract already ends with **§8 Data Update Verification Carrier Map**. The plan’s section numbers collide and would force a silent renumber or overwrite during Phase 1. | Specify exact insertion points without collision (e.g. new §9 Durable Checkpoint, §10 v2 Schema, renumber only if explicitly planned; never reuse §8). |
| medium | §7.2 / §7.3 / Phase 2 constrained keys | Live checker `PLAN_KEYS` use space-separated titles (`Current phase`, `Implementation review`, `Lifecycle reconciliation commit`). V2 examples use hyphenated keys (`Implementation-start-evidence`, `Current-work-unit`, `Review-target-commit`) and place `Review-target-commit` on **plan** metadata as well as reviews. “Strict superset” is also contradicted by “change `Implementation review` to list format” if the v1 key is removed/renamed. | Freeze exact operative key strings, allowed values, which keys are plan-only vs review-only, dual-schema required-key sets, and migration rules (keep v1 keys; add new keys; or versioned replacement with explicit checker branches). Do not put review-target commit on plan metadata. Define checkable grammar for `Verified-implementation-checkpoint` (or drop it in favor of trailers only). |
| medium | §4.1 checkpoint scopes vs real lifecycle products | Several scopes under-capture files this repo already co-edits in one lifecycle product: `design-review` omits plan/index/state updates on `approve` (Terminal UI `review-002` path updates plan metadata + derived surfaces); `proposal-revision` omits reviews index/roadmap/state; `plan-proposal` omits optional PROGRESS narrative while exclusion #5 forbids orphan PROGRESS edits. Implementers will either form incomplete commits or routinely hit same-file/exclusion aborts. | For each of the 11 kinds, freeze a **minimum required path set** and an **allowed optional path set** derived from real v1 products (proposal, design review approve/revise, activation, phase-exit, completed-migration). Require index/roadmap/state reconciliation in scope whenever the product mutates them; keep exclusion #5 only for true orphan derived-surface edits. |
| medium | §7.1–7.2 work-unit model | Adds `Current-work-unit` / `Work-state` for remediation but does not define interaction with existing `Current phase` / `Phase state` / gate tokens, nor invariants for Active remediation (e.g. can `Current phase=phase-6` while `Current-work-unit=remediation-2`?). | Add a small state machine: legal combinations, gate-token prefixes, what “phase-exit” vs `remediation-complete` means when both fields exist, and which fields remain authoritative for index rows. |
| medium | §5.4 same-file ambiguity | Requires abort on interleaved same-file edits but defines no decidable rule for an actor or preflight checker (dirty-before-start? hash mismatch vs expected post-image? forbid any pre-dirty path in manifest?). Without a rule, fixtures cannot be written and agents will guess. | Freeze a fail-closed algorithm: e.g. if a manifest path is dirty in the pre-checkpoint baseline, abort unless the path’s entire post-image is byte-identical to a declared expected blob or was created by this work unit from a clean baseline recorded at work-unit start. Explicitly forbid `git add -p`. |
| medium | Success criterion 6 vs enforcement | Checker validates trailers when present, but the plan does not say when a **missing** expected checkpoint after a lifecycle product is hard-fail vs advisory. Without that, governance documents policy without teeth after “implementation complete.” | Define audit obligations by mode: postflight after an authorized checkpoint is hard-fail on trailer/scope errors; repository audit is soft on pre-policy history; optional Active-plan “expected latest checkpoint kind” checks only when a plan opts into v2 and claims a phase-exit/complete product. |
| non-blocking | §5.6 secret glob `*token*` | Over-broad relative to governance tokens, plan trailers, and harmless filenames; under-specified exclusion. | Replace with an allow/deny path list plus content heuristics, and pin fixtures for false-positive paths. |
| non-blocking | Phase 5 bootstrap vs Phase 6 closeout | Bootstrap says this plan’s own checkpoints stay on v1 and do not use the new rules; Phase 6 still mentions `Tang-Checkpoint: completed-migration` if v2 is “already operational.” Bootstrap boundary should not depend on a race with partial rollout. | State unconditionally that **this plan’s entire lifecycle**, including completed-migration, uses the v1 commit pattern; trailer-identified completed migration applies only to post-governance plans. |
| non-blocking | §1.2 / dirty worktree claims | Correct that multi-product dirt exists and Terminal UI is Proposed with approve/high / `activation-recording`. Independent of design quality, Phase 0 same-file overlap with currently dirty `docs/exec-plans/proposed/index.md`, `reviews/index.md`, `roadmap.md`, `PROGRESS.md`, `HANDOFF.md`, optimization SOP/templates, etc. is almost certain once this plan edits those shared surfaces. | Treat concurrent Terminal UI + optimization dirt as a first-class Phase 0 risk: either require those products to be committed/scoped first, or freeze disjoint edit protocols for shared indexes before implementation-start. |

## Verdict Rationale

**Verdict: `revise` / confidence `high`.**

The proposal correctly identifies a real governance gap: multi-product dirty worktrees, ad-hoc reconciliation commits, and no durable local-commit contract. Lane 3 routing, independence from the Terminal UI product plan, four-way authority separation, read-only checker non-goal (as a non-goal), v1 freeze, and dual-schema intent are directionally sound. The eleven-kind catalog and fail-closed staging instincts are a good backbone.

It is **not yet implementable as a governing contract** for this exact revision because three blocking gaps remain:

1. **Execution model** — “auto-commit” duties without a named commit actor or authority grammar, while the only new tool is read-only.
2. **OPT reality** — 1 MB gate is incompatible with live optimization screenshots (reference PNG ≈ 1.69 MB).
3. **CI/history policy** — trailer audit on legacy history is not fail-closed-safe for PR/governed carriers.

Medium items (section renumber collision with live §8, v2 constrained key grammar vs live `PLAN_KEYS`, under-scoped checkpoint manifests vs real lifecycle file sets, work-unit vs phase state machine, same-file algorithm, missing-checkpoint enforcement) would produce checker/fixture churn or routine aborts if left to implementation judgment.

**Live evidence anchors used:**

- Plan SHA-256 `0e93eaab…d62e`, revision `v1-proposal-2026-07-20`, author `codex-plan-author-2026-07-20-durable-checkpoint`
- `docs/operating-modes.md` sections 1–8; constrained keys enforced in `scripts/check-operating-modes.py`
- Harness workflow still three jobs (`Harness structure`, `Backend checks`, `Frontend build`); Pages publisher out of manifest — good
- Current focus state remains Terminal UI Proposed / `activation-recording`; this plan is a second Proposed with `design-review` — correct for multi-proposal discovery via indexes
- OPT reference screenshot 1,688,940 bytes under the path cited above

**Authority boundary:** This design `revise` does **not** activate or implement the plan, does not authorize foldback by itself beyond recording the review, and grants no Git/data/remote authority. A new revision must retarget a fresh matching-revision design review; this `review-001` cannot approve a later foldback.

## Unverified By Design-Review Boundary

- Any future implementation of `check-durable-checkpoint.py` or dual-schema checker behavior
- Real agent commit procedure UX under standing authority
- Concurrent Terminal UI activation interaction beyond documented risk
- Hosted CI run of a future checkpoint step
