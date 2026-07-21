# Review 002 — Tang Strategy Trade Panel Visual Polish

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-panel-polish-r2`
- Plan author ID: `grok-plan-author-2026-07-21-trade-panel-polish`
- Independence declaration: `attested`
- Evidence method: `Independent revision review of the v2 closure map and full plan against review-001, current React component and consumer sources, the Node test command and dependency surface, source-inspection test carriers, QQQ fixture, linked OPT evidence, lifecycle indexes/state files, governed harness output, and the 49-test frontend baseline.`
- Verdict: revise
- Confidence: high

## Scope Checked

- Every `review-001` finding and its claimed v2 closure
- Eligibility, drawer, Download, card, and three-consumer acceptance contracts
- Exact implementation/test manifest and executable verification carriers
- Proposal-revision lifecycle/index/source-record reconciliation
- Activation, implementation, Git, data, publication, and remote boundaries

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | §2.2 criteria 2, 4, and 8; §3.1 item 9; §4 Phase 0 items 9 and verification 8 | V2 closes the product requirements from `review-001`, but assigns real Eligibility and `>=7` drawer interaction to `tradeRecords.test.js`. The configured command is plain Node `--test`; the repository has no JSX transform, DOM, React renderer, jsdom, or Testing Library, and the current tests read React sources as text. Within the frozen nine-file manifest, that suite can prove pure filter/summary functions and static source strings, but it cannot click the segmented control, open/close the drawer, type a search, or activate Select all/Clear. The plan simultaneously says those tests are mandatory and allows “equally strong browser receipts,” leaving the exit gate either infeasible or satisfiable by weak regex evidence. | Freeze one executable carrier matrix. Keep `tradeRecords.test.js` mandatory for pure filter/export behavior, English string/threshold/source invariants, and any genuinely importable non-JSX helper. Put actual Eligibility selection/focus and synthetic `>=7` drawer open/search/select-all/clear behavior in a deterministic Playwright/browser receipt with a named fixture-injection method (for example route-intercepted in-memory payload), or explicitly expand the manifest and dependencies for a real component-test harness. Remove the current test-or-browser fallback and make criteria 2/4/8 plus Phase 0 name the same carriers. |

## Review Reconciliation Observation

The incoming proposal-revision edits placed explanatory prose in the constrained Proposed and Reviews index verdict cells, so the initial governed/auto harness failed before review with two fixed-row verdict mismatches. The review-only reconciliation restores the canonical row grammar while preserving the v2 plan body and source-record changes; this mechanical correction is not implementation or plan remediation.

## Verified Closures And Strengths

- V2 fully closes the substance of all three `review-001` findings: accessible single-selection semantics are frozen; English drawer copy and the six-trader threshold are fixed; the long Download ban is production-scoped; and a four-file UI receipt is required.
- The exact production surface remains the same nine frontend paths, with backend, DB, content, provider, broker, and publication paths excluded.
- The QQQ `2026-07-17` visual fixture remains valid for real PUT/CALL card coverage, and the plan correctly avoids pretending it covers the synthetic `>=7` state.
- The current product baseline remains green at 49/49 frontend tests. The initial harness failure is confined to the incoming constrained index prose described above, not product code.
- Matching-revision approval is still separated from activation and implementation authority.

## Verdict Rationale

The revised product contract is now technically sound, but the verification contract is not yet executable as written. A small subtractive foldback that assigns source/pure-function assertions to the existing Node suite and real interactions to one deterministic browser carrier will make the exit gate unambiguous without adding process or changing product scope. This review does not activate, implement, remediate, push, publish, access data/providers/brokers, or authorize remote action.
