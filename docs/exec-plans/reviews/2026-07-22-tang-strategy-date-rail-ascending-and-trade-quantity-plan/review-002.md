# Review 002 — Tang Strategy Date Rail Ascending And Trade Quantity

- Review target: `docs/exec-plans/proposed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md`
- Review target revision: `v2-review-foldback-2026-07-22`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-22-date-rail-quantity-r2`
- Plan author ID: `grok-plan-author-2026-07-22-date-rail-quantity`
- Independence declaration: `attested`
- Evidence method: `Independent repository inspection of the exact v2 plan and v1-to-v2 revision diff, review-001, lifecycle surfaces, source OPT scope locks, all five visual/mock evidence files with recomputed hashes, canonical QQQ 2026-07-17 quantity chains, current shared frontend code paths and test seams, and the 64-test frontend baseline. Exact reviewed plan SHA-256: 67ae3c064402afcc0471bb2a772b4b3e2ba6caaeac4997fad04b2d60689c4f22. Repository HEAD: 17ebee5c2eb5086b72656cc97999d42e993c46ad.`
- Verdict: approve
- Confidence: high

## Scope Checked

- Exact Proposed revision `v2-review-foldback-2026-07-22`, with `design-review` as the next gate and no activation or implementation evidence
- The append-only `review-001: revise/high` P1 and every v2 foldback change against the v1 review target
- Plan SHA-256 and all five visual/mock evidence hashes (the v2 evidence table is §1.3 after the new §1.2 foldback map)
- `projectProgressiveDateRail`, newest-N membership, newest-first month inventory, and Review/Data/Static progressive consumers
- `buildTradeRecordAnnotations`, same-side same-bar grouping, `groupTimelineEvents`, timeline rendering, canonical 150/12 fixtures, and existing pure test seams
- Success criteria, mandatory N-carriers, frozen implementation manifest, phase entry/exit gates, lifecycle authority, and unrelated-change protection
- Frontend-only scope exclusions for content, tracked SQLite, backend/API, seed market data, provider/broker, Pages, publication, and remote actions

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | No design defect found in the exact v2 revision. | — |

## Verified Strengths / Closures

- **review-001 P1 is fully closed.** The v2 plan permits deriving a null `sell_close` only when every prior quantity-bearing `buy_open`, `buy_add`, and `sell_partial` on the leg has a finite valid quantity. It defines “prior” by validated event/sequence order, preserves a numeric raw close as-is, and fails closed for incomplete or over-closed chains.
- Marker completeness is now exact: `*QTY` is emitted on both `marker_label` and `title` only when every contributor in the existing same-trader, same-direction, same-action-side, same-bar group has a known raw or derived quantity; mixed known/unknown groups omit the suffix on both fields.
- The contradictory “multi-bar sum” carrier language is removed. Scope locks, success criteria, and `N-Marker-qty` consistently require a **same-side, same-bar sum** without changing the grouping-key family.
- Phase 0 explicitly freezes the three required adversarial pure fixtures: known open plus null `buy_add`, null prior `sell_partial`, and mixed known/unknown same-bar contributors. The 150/12 positive cases, raw-preferred case, unknown-open case, and over-partial case remain mandatory through `N-Qty-derive`, `N-Marker-qty`, and `N-Timeline-qty`.
- The exact plan SHA-256 is `67ae3c064402afcc0471bb2a772b4b3e2ba6caaeac4997fad04b2d60689c4f22` at inspected HEAD `17ebee5c2eb5086b72656cc97999d42e993c46ad`. All four screenshot hashes and the mock hash match the plan's evidence table.
- Live code still supports the design: `projectProgressiveDateRail` projects newest-first arrays that can be reversed only after newest-N/month membership selection; `buildTradeRecordAnnotations` performs the locked same-bar grouping and owns label/title construction; `groupTimelineEvents` and `TraderTradeList` provide the shared derived-quantity consumption seam.
- The canonical QQQ `2026-07-17` source groups independently confirm PUT `150 -> null close` and CALL `70 - (12+12+22+12) -> null close`, yielding the frozen 150 and 12 derivation oracles without source mutation.
- Review, Data, and Static remain opted into the shared progressive rail; Review and Static share annotation and timeline helpers. The current frontend baseline passes 64/64 tests, confirming the pre-implementation seams remain intact.
- The manifest is executable and bounded to shared frontend presentation helpers, consumers, tests, lifecycle evidence, and untracked screenshots. Phase gates require all mandatory N-carriers, builds, visual receipts, implementation commit evidence, and an independent implementation review before closeout.
- Authority wording remains fail-closed: this approval does not activate the plan; activation requires a separate explicit instruction; implementation requires a later explicit start/execute instruction; no content/DB, backend, provider/broker, Pages, publication, push, PR, merge, or other remote authority is granted.

## Unverified Items

- Product implementation, updated N-carriers, normal/static builds, V1–V3 visual receipts, implementation commit, and implementation review were not executed because this is a design review of a Proposed plan.
- The repository's Python lifecycle and harness checks could not be executed because no Python interpreter was resolvable in the inspected environment. Canonical lifecycle files and links were inspected directly, the plan remained Proposed at the exact target revision before this artifact was written, the frontend 64/64 baseline passed, and the worktree diff check was clean.
- Direct lifecycle reconciliation files are intentionally outside this task because the user required writing only `review-002.md`; this review does not update, activate, or implement the plan.

## Verdict Rationale

Revision v2 correctly and completely folds the sole review-001 P1 into the formula, grouped-marker semantics, success criteria, mandatory carrier matrix, and Phase 0 fixture freeze. The changes introduce no conflicting requirement or scope expansion, and the current shared frontend code paths provide the exact pure seams the plan names.

The plan is executable as written, has no P1 finding, remains bounded to frontend presentation, and preserves all governance and remote-authority gates. An `approve` verdict with high confidence is therefore warranted. This review is append-only evidence for the exact v2 revision; it does not activate or execute the plan.
