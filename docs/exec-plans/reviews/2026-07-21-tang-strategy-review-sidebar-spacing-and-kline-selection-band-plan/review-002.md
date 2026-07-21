# Review 002 — Tang Strategy Review Sidebar Spacing And K-line Selection Band

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-sidebar-spacing-selection-band-r2`
- Plan author ID: `grok-plan-author-2026-07-21-sidebar-spacing-selection-band`
- Independence declaration: `attested`
- Evidence method: `Independent repository inspection of the exact v2 plan, review-001 foldback, source OPT locks, recomputed plan/mock/screenshot hashes, Review/Static/Admin component composition, group/event focus oracles, chart highlight and viewport seams, historical browser runner assertions, lifecycle surfaces, phase gates, and authority boundaries. Exact pre-reconciliation plan SHA-256: 145fd3e999b71340ca6889be5e90b8522383eaa23c34deac5bf596c8fef18eaf. Repository HEAD: f704dfd32a9bea19a80a800282afac383e015d7b.`
- Verdict: approve
- Confidence: high

## Scope Checked

- Full proposed revision `v2-review-foldback-2026-07-21`, especially §1.2 closure map, §2.4 carrier matrix, §3.1 item 8 replacement runner, Phase 0/1 entry and exit gates, and §6 review/activation separation
- Append-only `review-001` P1 and each claimed v2 closure: replacement tracked runner, independent span/event oracles, empty highlight storage after group/event focus, and exclusion of the historical group-span runner from this plan's exit gate
- Source OPT-001 and OPT-002 locks: Review/Static parity, approximately 20px inter-block rhythm, 交易者/策略讲解 captions and hairlines, single Traders label, Review/Static Download removal without relocation, complete selection-band cancellation, retained `fitRange`, and unchanged marker labels
- Recomputed SHA-256 values for the exact pre-reconciliation plan, confirmed mock, sidebar friction screenshot, and blue-band friction screenshot
- Live `TraderFilters`, `TraderTradeList`, `ReviewSignalList`, `ReviewPage`, `StaticReviewsApp`, and Admin composition paths
- Live `groupBarSpan` and `eventFocusPayload` pure oracles, marker annotation contract, engine `setHighlightRanges` / `getHighlightRanges` / `fitRange` / `getViewportDebug` seams, and the historical runner's blue-band dependency
- Proposed/reviews indexes, exec-plan roadmap, `PROGRESS.md`, `HANDOFF.md`, unrelated-worktree protection, and Lane 3 authority rules

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | No blocking or advisory design finding remains in exact revision v2. | — |

## Verified Closures

- The exact pre-reconciliation plan hash matches `145fd3e999b71340ca6889be5e90b8522383eaa23c34deac5bf596c8fef18eaf` at the supplied repository HEAD.
- The confirmed mock and two tracked screenshots match their listed SHA-256 values: `f2386dbd46aff8c472d635aa3c53f2071ca4e2f22d6d053ffa366abf8981ce46`, `e7846e060f3f7f5049dd92edc512de39f939dab11670cfc4ac0667d969020d37`, and `a5cf3b8a4f64ab86775e16ecb00a3bfcb842c02698e87f1892772dad5b5de89d`.
- Review-001's P1 is fully closed. §2.4 and §3.1 item 8 freeze `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs` as the sole mandatory browser carrier for this plan's layout, group-band cancellation, event-focus cancellation, and visual receipts.
- The replacement carrier uses deterministic expected indices from `groupBarSpan` / `eventFocusPayload` or fixture-precomputed constants. The plan explicitly forbids deriving the expected span or event bar from highlight storage.
- Group select and event-row focus both require `getHighlightRanges()` to be empty after interaction, while `getViewportDebug()` must independently prove containment of the expected group span or event bar. Group selection retains the no-post-fit-recenter invariant; event focus additionally rejects a full-day viewport.
- The historical `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs` still requires blue highlight storage in live source, matching the plan's repository fact. V2 places it outside the modify set and explicitly removes it from Phase 1 exit authority, so its completed-plan assertions cannot contradict this plan's gate.
- The live component graph supports the frozen implementation path. Review and Static both pass `TradeExportControls` through the optional `TraderFilters` slot and compose the same filters, trader-list, and signal-list sequence. Admin has a separate composition path that can retain Download without reintroducing it on Review/Static.
- The live chart paths support selection-paint cancellation without losing location behavior: group selection derives a pure span and calls `fitRange`; event focus derives a pure single-bar payload and calls `fitRange`; the engine exposes independent highlight-state and viewport-debug seams.
- OPT-001 and OPT-002 locks remain intact. No backend, API, DB, content, provider/broker, Pages, marker-vocabulary, export-payload, timeframe, Data-rail, or adjacent completed-plan scope was added.
- Phase 0 requires Active status plus a separate implementation-start instruction. Phase 1 requires Phase 0 exit and continuing implementation authority. A matching design approval only advances the Proposed plan to the `activation-recording` gate; it does not activate or execute the plan.

## Unverified Items

- Product implementation, browser receipts, rendered spacing, empty painted bands, and final viewport behavior remain unverified because this artifact is a design review. The plan makes each item a mandatory implementation exit carrier rather than treating design inspection as execution evidence.
- The exact fixture event-row index and pure-oracle constants are intentionally frozen during authorized Phase 0. Their executability is supported by the named QQQ multi-event group and existing pure/runtime seams, but their resulting values are not claimed as implementation evidence here.

## Verdict Rationale

Revision v2 preserves the user-confirmed product locks and closes the only P1 from review-001 without weakening verification. It replaces the incompatible historical carrier with an exact tracked path, separates expected span/event indices from highlight storage, requires empty highlight state after both affected interactions, and independently proves retained `fitRange` behavior through viewport containment. The three-block layout gate is likewise measurable on Review and Static, with screenshots remaining supplemental.

The implementation manifest names the live integration, styling, pure-test, and browser-runner surfaces while preserving Admin compatibility and excluding backend, data, publication, and adjacent feature scope. Phase entry gates and lifecycle wording keep design approval, activation, and implementation authority distinct. The plan is executable with no residual P1 or new design hole, so the verdict is `approve` with high confidence. This review does not activate or implement the plan and grants no code, content, DB, provider, broker, publication, push, or remote authority.
