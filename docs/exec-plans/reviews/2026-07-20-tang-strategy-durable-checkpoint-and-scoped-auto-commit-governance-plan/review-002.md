# Review 002 — Tang Strategy Durable Checkpoint And Scoped Local Commit Governance

- Review target: `docs/exec-plans/proposed/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan.md`
- Review target revision: `v2-review-foldback-2026-07-20`
- Review type: design
- Reviewer ID: `grok-build-design-reviewer-2026-07-20-durable-checkpoint-r2`
- Plan author ID: `codex-plan-author-2026-07-20-durable-checkpoint`
- Independence declaration: `attested`
- Evidence method: Independent re-read of exact revision `v2-review-foldback-2026-07-20` at SHA-256 `46e6b3fb2276c9838d289b6b070fa9d3d426a478fd65e71888f2ae0690050702`; closure check of every `review-001` finding against operative v2 sections; live re-check of reference OPT PNG byte size and SHA-256, `docs/operating-modes.md` ending at §8, `scripts/check-operating-modes.py` space-separated `PLAN_KEYS`, harness workflow three-job structure, dual Proposed index rows, and `check-operating-modes.py --root .` green. This reviewer context did not draft the v2 foldback. No implementation, data write, provider/broker, stage/commit/push, PR, merge, Pages, or remote administration was performed.
- Verdict: approve
- Confidence: high

## Scope Checked

- Frozen v2 identity, title rename vs stable slug, and foldback provenance (§1.1 / §1.5)
- Every `review-001` blocking/medium/non-blocking finding against operative v2 contracts
- Execution model, authority grammar, request/receipt CLI, size gates, legacy CI policy
- Eleven-kind real lifecycle scopes, exclusions, same-file algorithm, enforcement modes
- Exact v2 key superset, work-unit state machine, change manifest, phases 0–6, bootstrap/rollback
- Live repository anchors for OPT evidence, section map, and current dual-proposed state

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | — | — |

## Prior Finding Closures

Independently re-verified against operative v2 text and live evidence:

1. **Blocking — commit actor / auto-commit / read-only contradiction (review-001).** Closed. Title and operative language are **Scoped Local Commit**; historical slug may retain `auto-commit` without granting authority. §§3.2–3.3 and §5.1 freeze a single human/agent commit actor, exact `user-instruction:<token>` authority grammar, one-shot/standing rules, and `checkpoint-request-v1` inputs. The checker is explicitly read-only and never stages/commits. Exact CLI carriers for baseline/staged preflight, postflight, and audit are pinned.

2. **Blocking — 1 MB gate vs live OPT screenshots (review-001).** Closed. §5.6 is kind-aware: text 1,048,576 bytes; OPT screenshots under `docs/optimization/<opt>/screenshots/*.(png|jpg|jpeg|webp)` for `opt-record`/`plan-proposal` only at 5,242,880 bytes; aggregate 26,214,400 bytes. Live reference PNG is required positive fixture at **1,688,940** bytes and SHA-256 `57c34ea70bf7c6cab2c983b8feaedb6ad9be6f23fc02262ac7c97a48b156d3c5` (independently recomputed match). Rejection thresholds 5,242,881 / 1,048,577 / 26,214,401 are fixture-pinned.

3. **Blocking — CI audit on pre-v2 trailer-less history (review-001).** Closed. §6.4 and Phases 3–4 freeze exact `python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated`, warn/exit-0 on pre-opt-in trailer-less history, hard-fail on partial/malformed present trailers, bad authority use, and v2 expected-kind gaps. Placement is the existing `Harness structure` job immediately after operating-modes fixture tests; three job names and Pages publisher remain untouched.

4. **Medium — live §8 numbering collision (review-001).** Closed. Implementation must append `## 9. Durable Checkpoint Contract` and `## 10. operating-modes-v2 Schema And Work-Unit State Machine` after the complete existing §8; §§1–8 are not renumbered or reused.

5. **Medium — v2 constrained key grammar / review-target on plan (review-001).** Closed. §7.2 retains all seventeen exact live space-separated v1 keys, appends ten space-separated additions, forbids hyphenated aliases, keeps `Implementation review` as accept-pointer, forces `Lifecycle reconciliation commit: none` on v2, and never places `Review target commit` on plan metadata. §7.3 makes it the final review-only key for v2 reviews.

6. **Medium — checkpoint scopes too narrow (review-001).** Closed. §4.1 defines minimum reconciliation sets and allowed optional staged sets for all eleven kinds using real plan/index/roadmap/state/PROGRESS/HANDOFF products; unchanged required surfaces are inspected not forced; out-of-set staging fails closed.

7. **Medium — phase/remediation state machine (review-001).** Closed. §7.4 freezes legal `Current phase`/`Phase state` vs `Current work unit`/`Work state` combinations, gate prefixes, blocker iff-rule, sequential remediation numbering, primary-only `phase-exit`, remediation-only `remediation-complete`, and Active-index derivation from primary phase fields.

8. **Medium — same-file ambiguity undecidable (review-001).** Closed. §5.4 requires clean/absent manifest paths at work-unit entry, exact baseline blobs and full post-images, forbids `git add -p`/hunk split/absorb, and treats concurrent Terminal UI/optimization dirty shared paths as Phase 0 blockers under separate ownership.

9. **Medium — missing-checkpoint enforcement (review-001).** Closed. §6.4 separates hard staged/postflight/v2-claim failures from advisory pre-v2 history; `Expected checkpoint kind` is mandatory only under stated v2 claim conditions.

10. **Non-blocking — over-broad `*token*` secret glob (review-001).** Closed. §5.6 uses exact deny paths, added-line heuristics with placeholder allowlist, and false-positive fixtures for harmless `token` filenames and `gate-token` prose.

11. **Non-blocking — bootstrap race (review-001).** Closed. Phase 5–6 and rollback state unconditionally that this plan’s entire lifecycle, including completed migration, uses the v1 pattern only; it never claims `Tang-Checkpoint: completed-migration` for itself.

12. **Non-blocking — concurrent dirty shared surfaces (review-001).** Closed as a design risk treatment: Phase 0 entry requires shared manifest paths clean/absent after owning products resolve them; wait is allowed, absorb/stash/split is not.

## Verdict Rationale

**Verdict: `approve` / confidence `high`.**

V2 is a complete, implementable foldback of `review-001`. No blocking or medium contract gap remains for design approval of this exact revision.

**Current-contract coherence against live evidence:**

- Plan identity: title `Tang Strategy Durable Checkpoint And Scoped Local Commit Governance`, slug retained for link stability, revision `v2-review-foldback-2026-07-20`, SHA-256 `46e6b3fb…0702`.
- OPT reference PNG live size/hash match the plan’s required fixture values exactly.
- Live `docs/operating-modes.md` still ends at §8 Data Update Verification Carrier Map; append-only §§9–10 is the correct insertion strategy.
- Live checker still uses space-separated plan keys; v2’s literal superset strategy is coherent with `PLAN_KEYS`.
- Harness workflow still has exactly three named jobs; the planned single added `run` scalar is compatible with the constrained CI carrier rules.
- Focus plan remains Terminal UI Proposed / `activation-recording`; this governance plan remains an independent second Proposed surface.

**Residual non-blocking implementation freezes (do not reopen design):**

- Request fields name both Git blob IDs and content SHA-256; Phase 3 should freeze one canonical encoding per operation in fixtures (for example, `baseline_blob` as `git rev-parse <head>:<path>` OID and `post_sha256` as staged blob OID or content hash consistently) without changing the fail-closed rules.
- OPT standing-authority headers are required by §3.3; Phase 1 must pin the exact OPT constrained key list/order in the record template and durable-checkpoint fixtures even though the operating-modes plan-key checker does not own OPT documents today.

**Authority boundary:** This matching-revision design `approve` does **not** activate the plan, start implementation, stage/commit/push, write canonical data, open PR/merge, publish Pages, or grant provider/broker/remote authority. After this review, the next legal user action for this plan is an explicit activation instruction that must stop at `phase-0:not-started`; implementation requires a later explicit start instruction. Standing or one-shot local commit authority for later phases remains a separate user grant. Concurrent Terminal UI activation remains a separate authority chain.

## Unverified By Design-Review Boundary

- Any future implementation of `check-durable-checkpoint.py` or dual-schema checker behavior
- Real agent/human commit procedure UX under standing authority
- Concurrent Terminal UI activation interaction beyond the documented Phase 0 block/wait rule
- Hosted CI execution of the future legacy-tolerated audit step
