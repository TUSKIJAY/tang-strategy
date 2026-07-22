# Review 001 — Tang Strategy Date Rail Ascending And Trade Quantity

- Review target: `docs/exec-plans/proposed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md`
- Review target revision: `v1-proposal-2026-07-22`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-22-date-rail-quantity-r1`
- Plan author ID: `grok-plan-author-2026-07-22-date-rail-quantity`
- Independence declaration: `attested`
- Evidence method: `Independent repository inspection of the exact plan, source OPT batch and all OPT-001…003 scope locks, four visual-evidence screenshots and design mock with recomputed hashes, canonical QQQ 2026-07-17 vordin groups, live progressive DateRail projection and consumers, marker/timeline helpers and tests, trade-event validation/order contracts, exact modify manifest, lifecycle surfaces, and authority boundaries. All five §1.2 evidence SHA-256 values matched. The current frontend baseline passed 64/64 tests. Exact reviewed plan SHA-256: edce9b64a163178661c8da8eaa037e45092683c4c44ac71f2a4ca07d9e446138. Repository HEAD: 384497334ebd46b1bd73c49f406168f8ba4777a2.`
- Verdict: revise
- Confidence: high

## Scope Checked

- Exact proposed revision `v1-proposal-2026-07-22`, including metadata, objectives, success criteria, frozen carriers, manifest, phase gates, and non-goals
- Source batch OPT-001…003, promotion links, Scope Lock, mock, four live-friction screenshots, and canonical 150/12 fixtures
- `datesForTicker`, `projectProgressiveDateRail`, recent membership, month inventory/navigation, and Review/Data/Static progressive consumers
- `buildTradeRecordAnnotations`, its same-bar grouping key and `×N` path, `groupTimelineEvents`, `TraderTradeList`, and the Admin preview's shared-helper consumption
- Existing Node test seams, trade-event sequence/quantity validation, render-only boundaries, and source-write exclusions
- Proposed/reviews indexes, exec-plan roadmap, OPT index/back-links, `PROGRESS.md`, `HANDOFF.md`, unrelated worktree protection, and Lane 3 authority wording

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | §1.4 `OPT-003 derivation` / `fallback`; §2.2 criteria 4–7; §2.4 `N-Qty-derive`, `N-Marker-qty`, and `N-Timeline-qty`; Phase 0 fixture freeze | The fail-closed quantity oracle is incomplete. The formula defines opening quantity as the sum of *known* `buy_open`/`buy_add` values and subtracts only *known* prior partials, while fallback covers only an unknown opening or a known partial sum greater than opening. It does not state that any unknown prior position-changing quantity makes the remaining position unknowable. An implementation can therefore ignore a null `buy_add` or null prior `sell_partial`, emit a fabricated derived close, and still pass the frozen 150/12, all-open-unknown, and over-partial fixtures. Marker aggregation has the same completeness gap when a same-bar group mixes known and unknown effective quantities. In addition, `N-Marker-qty` says “multi-bar sum,” contradicting the locked same-side, same-bar grouping key. | Freeze one completeness rule: derive a null close only when every prior quantity-bearing `buy_open`, `buy_add`, and `sell_partial` on that leg has a finite valid quantity; otherwise return unknown, while preserving an explicitly numeric close as-is. For a grouped marker, emit `*QTY` only when every contributing event has a known raw/derived quantity; otherwise omit the suffix from both `marker_label` and `title`. Define “prior” by the validated event/sequence order, change “multi-bar sum” to “same-side, same-bar sum,” and add adversarial pure fixtures for known open + unknown add, unknown prior partial, and mixed known/unknown same-bar aggregation alongside the existing 150/12, raw-preferred, unknown-open, and over-partial cases. |

## Verified Strengths / Closures

- The exact plan SHA-256 is `edce9b64a163178661c8da8eaa037e45092683c4c44ac71f2a4ca07d9e446138` at inspected HEAD `384497334ebd46b1bd73c49f406168f8ba4777a2`.
- All four screenshot hashes and the mock hash match §1.2. The screenshots independently show newest-first recent/month chips, `×2` marker labels, and the two null close quantities described by the plan.
- The source OPT record and optimization index promote exactly OPT-001…003 and preserve the same locks: ascending chip paint with newest-N membership unchanged, `*QTY` marker vocabulary, and render-only close derivation.
- Live date code matches the plan: `datesForTicker` is newest-first; `projectProgressiveDateRail` currently projects that order for recent and month chips; `listMonthsForTicker` and `stepBrowsedMonth` rely on newest-first month inventory. A projection-only ascending transform is feasible without changing membership or month navigation.
- Review, Data, and Static explicitly opt into the shared progressive `ReviewContextPanel`; the Admin editor remains on the exhaustive default. The date carrier and manifest can prove shared-surface behavior without CSS or backend changes.
- Live marker code groups by `bar_index|trader_id|direction|action_side`, keeps direction-owned shape/color/anchor, and appends `×N` only after grouping. The proposed helper/test surface can replace that label path with quantity aggregation on both `marker_label` and `title` without changing the grouping key.
- Live timeline code passes raw `event.quantity`, and `TraderTradeList` already renders `row.quantity ?? '?'`. The canonical PUT and CALL groups contain the exact numeric chains required for derived 150 and 12, so the intended positive oracle is executable.
- The exact production/test manifest is bounded to shared frontend helpers and tests, with optional JSX consumption only if necessary. It excludes content/day JSON, tracked SQLite, backend/API, market-data seeds, provider/broker, Pages, and remote actions.
- Lifecycle surfaces were consistent before this review: the plan is Proposed at `design-review`, its design-review metadata is empty, indexes and OPT links point to the proposed revision, and no activation or implementation evidence exists.
- Authority wording is correct: an approval would not activate; activation would not start implementation; publication, push, PR, merge, provider/broker access, content mutation, and DB changes remain unauthorized.

## Unverified Items

- Product implementation, normal/static builds, V1–V3 screenshots, and implementation review were not executed because this is a design review of a Proposed plan.
- The repository's Python lifecycle/harness checks could not be executed in this PowerShell environment because no Python interpreter is available on PATH. Their governing files and current lifecycle surfaces were inspected directly; the frontend baseline independently passed 64/64 tests.
- The revised incomplete-chain and mixed-known/unknown quantity oracles remain unverified until the plan author folds this finding into a new stable revision.

## Verdict Rationale

The plan is well bounded and its date-order, marker-label, positive derivation, safety, lifecycle, and authority designs align with the current repository. The required code paths and positive 150/12 fixtures exist, and no backend, content, DB, provider, or publication expansion is needed.

Approval is blocked because the current derivation and aggregation carriers can certify false precision whenever only part of a position-changing quantity chain is known. That conflicts with the plan's own safe-fallback and “do not invent” locks. The contradictory “multi-bar sum” phrase further leaves the aggregation oracle ambiguous against the frozen same-bar key. These are bounded formula and fixture corrections rather than a fundamental design failure, so `revise` with high confidence is appropriate. This review does not activate or implement the plan and grants no product, content, DB, provider/broker, publication, push, or remote authority.
