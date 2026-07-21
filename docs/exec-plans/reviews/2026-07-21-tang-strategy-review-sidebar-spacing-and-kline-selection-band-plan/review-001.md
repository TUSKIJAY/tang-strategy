# Review 001 — Tang Strategy Review Sidebar Spacing And K-line Selection Band

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md`
- Review target revision: `v1-proposal-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-sidebar-spacing-selection-band-r1`
- Plan author ID: `grok-plan-author-2026-07-21-sidebar-spacing-selection-band`
- Independence declaration: `attested`
- Evidence method: `Independent repository inspection of the exact plan and source OPT, recomputed plan/mock/screenshot hashes, live Review/Static/Admin composition, group/event focus paths, chart highlight and fit seams, sidebar CSS structure, current tracked browser acceptance carrier, related source tests, lifecycle surfaces, and authority contract. Exact reviewed plan SHA-256: 411e8887b6586f94fcdc7e2a7c637bef6fb2cd68e284ea2c92c0e643bef96819. Repository HEAD: 93191ef38e7c75d77920739f0c8faf4e93613426.`
- Verdict: revise
- Confidence: high

## Scope Checked

- Full proposed revision `v1-proposal-2026-07-21`, including objectives, non-goals, exact manifest, phases, verification carriers, and activation wording
- Source batch OPT-001 and OPT-002, its user-confirmed Scope Lock, later open notes, promotion status, mock decision, and adjacent completed-plan boundaries
- Review and Static `TraderFilters`, `TraderTradeList`, `ReviewSignalList`, Download composition, group selection, event-row focus, and `fitRange` parity
- `eventFocusPayload`, marker-label builder boundary, chart highlight storage/paint seam, and current browser-accessible engine diagnostics
- `.dr-signal-list`, `.trade-filter-panel`, `.trade-record-list`, and `.dr-sidebar` density rules, including the need to preserve in-block card rhythm
- Admin Download composition and the preserved pure export-helper/component boundary
- Proposed/reviews indexes, exec-plan roadmap, product roadmap, `PROGRESS.md`, `HANDOFF.md`, OPT record/index links, unrelated worktree protection, and Lane 3 authority rules

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | §2.4 `B-Sidebar-layout`, `B-Group-band-cancel`, and `B-Event-focus-cancel`; §3.1 exact manifest; Phase 1; `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs` group-span flow | The three mandatory browser carriers are specified only as abstract receipts, while the exact implementation manifest omits the tracked browser acceptance runner that owns the current Review/Static group and event sequence. That runner requires a non-empty blue range after group selection and event focus, then uses the stored highlight itself as the expected span. The planned cancellation will therefore make the tracked carrier fail, and an empty highlight removes its current oracle for proving that the retained `fitRange` window contains the intended group span or event bar. No other exact runner path or independent browser oracle is frozen for those assertions or for the three-block gap measurement. | Add the exact tracked runner path to the Modify manifest, or freeze a replacement tracked runner path and retire the contradictory assertions explicitly. Define deterministic Review and Static fixtures plus an expected group-span/event-bar oracle independent of highlight storage, such as fixture-derived bar indices or captured `fitRange` arguments. Require the runner to assert empty highlight ranges after group and event clicks, final viewport containment of the independently expected range, no post-fit recenter, and measured ≈20px separation between explicit tools/traders/signals block wrappers with captions, hairlines, and Download absence on both surfaces. Keep screenshots supplemental. |

## Verified Strengths / Closures

- The exact proposed plan hash matches `411e8887b6586f94fcdc7e2a7c637bef6fb2cd68e284ea2c92c0e643bef96819` at the supplied repository HEAD.
- The mock and both screenshots match all three listed SHA-256 values and byte sizes. No informal `output/` evidence is promoted.
- Only OPT-001 and OPT-002 are promoted. Adjacent session OPTs and completed-plan behavior remain outside this plan.
- The user-confirmed locks are preserved: Review/Static parity, ≈20px inter-block gaps, 交易者/策略讲解 captions and hairlines, one `Traders` label, unchanged in-block density, no visible `Trade tools` title, Download removed rather than relocated on Review/Static, no replacement chart cue, retained group/event `fitRange`, and unchanged marker labels.
- Download disposition is executable in the live component graph: Review and Static can omit the optional export slot while Admin retains `TradeExportControls`; pure export builders and payload semantics remain out of the visual change.
- Event-row adjacency is explicitly frozen rather than deferred: Review and Static must clear or omit trade-selection paint while retaining event `fitRange`; `eventFocusPayload.style` may remain a pure unused field.
- The production manifest includes the live layout and interaction integration points and excludes backend, API, DB, content, provider, broker, Pages, and remote scope. The finding above is limited to the missing tracked browser carrier path and oracle.
- Source-only and browser-proof boundaries are stated correctly, and the plan makes all three browser receipts mandatory rather than allowing source checks or screenshots to substitute.
- Lifecycle surfaces were internally consistent before review: Proposed at `design-review`, with matching OPT links and no activation or implementation evidence. The authority text separates design review, activation, implementation start, and remote authority.

## Unverified Items

- No product implementation, visual acceptance, or browser interaction was executed because this is a design review.
- The revised tracked carrier and its independent span/event oracle remain unverified until the plan author folds this finding into a new stable revision.

## Verdict Rationale

Revision `v1-proposal-2026-07-21` preserves the product scope and resolves the two disposition questions that could otherwise block execution: Review/Static Download is removed without relocation, and event-row blue paint is canceled with no replacement cue. The live component and interaction paths support that design.

Approval is blocked because the verification plan cannot currently close its own hard browser gate. The only tracked runner for the affected flow asserts the behavior being removed and depends on highlight storage as the fit oracle, yet that path is absent from the exact manifest. This is a bounded manifest and verification-carrier correction, so `revise` is appropriate rather than `reject`. This review does not activate or implement the plan and grants no code, content, DB, provider, broker, publication, push, or remote authority.
