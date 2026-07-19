# Review 002 — Tang Strategy Review Workspaces And Trader Point Editing

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md`
- Review target revision: `v2-review-loop-baseline-2026-07-19`
- Review type: design
- Reviewer ID: `grok-build-0.2.103-round-1`
- Plan author ID: `codex-plan-author-2026-07-19-review-workspaces`
- Independence declaration: `attested`
- Evidence method: Frozen plan SHA-256 `c90406702862991511c68fb10d33e94b9a20a8b5430399bcaddd9d77101acc17` inspected on live worktree; cross-checked optimization intake, visual reference SHA/dims, `docs/operating-modes.md`, AGENTS/INSTRUCTIONS/PROGRESS/HANDOFF, frontend pages/filters/engine, backend trade-record routes/public projection/atomic write path, tracked DB counts/hash, and `content/trades` multi-ticker day shape. No implementation run, browser acceptance, or hosted verification performed.
- Verdict: revise
- Confidence: high

## Scope Checked

- Current-evidence accuracy, lifecycle metadata, and authority boundaries of frozen revision `v2-review-loop-baseline-2026-07-19`.
- Admin load/edit/save viability against the public projection, canonical multi-ticker day-file shape, existing admin PUT boundary, candidate projection, and rollback behavior.
- Workspace ticker/date authority, availability-driven trader filtering, chart-control ownership, interactive/static parity, accessibility evidence, planned file surface, phase gates, and rollback.

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Blocking | Plan §1.1, §2.3, §3.4, Phase 0/3 | The plan claims the current public read plus admin PUT contract is sufficient, but `GET /api/trade-records` is a public projection even for admin: it reduces full `normalization` to `normalization_method`, so a GET-derived document is not write-valid. Canonical day files are date-keyed and may contain multiple underlyings (for example `content/trades/2026-07-17.json` contains SPY and QQQ); a ticker-filtered public GET therefore cannot safely seed the complete day PUT. A scoped editor could drop other tickers, traders, groups, or contexts while still passing schema/projection coherence checks. | Declare the public projection read-only and never a write base. Add a durable admin-only canonical registry/day read path (or another separately reviewed full-document mechanism) that returns a write-valid complete day including normalization and every underlying/trader/context. Require candidate construction to start from that full day, merge only the scoped edit, and PUT the complete multi-ticker day. Update the non-goal, Phase 0/3 file surface, route/role tests, and preservation receipts accordingly. |
| Non-blocking | Plan §3.1/§3.3 and `TraderFilters` integration | Ticker/date are declared authoritative at workspace level, but the plan does not explicitly retire or lock any independent ticker/date selectors that remain inside trader filtering. | Remove those selectors or render read-only mirrors derived solely from the workspace; add a pure fixture proving child filter state cannot diverge from the resolved workspace day. |
| Non-blocking | Plan §2.2(9), §3.4, Phase 3 | “Inspect groups and events against the selected chart” and “preview ... marker/list effect” are not resolved to an implementation boundary: embedded engine preview, Review deep-link, or list-only preview would satisfy different portions of the wording. | Freeze the preview boundary in the plan and align the success criterion and Phase 3 exit receipt. Prefer reuse of `UnifiedKlineEngine` rather than a second chart implementation if preview remains in Admin. |
| Non-blocking | Phase 1/5 verification | The browser matrix covers accessibility, but pure tests do not explicitly pin accessible names/selected-state semantics for new tabs, date rail, and overview action. | Add focused pure/component fixtures for labels and selected/disabled state where the repository test stack permits; keep browser keyboard/focus evidence as the final gate. |

## Verdict Rationale

The workspace model, stale-selection rules, control-ownership split, static boundaries, phase structure, rollback posture, and proposal authority are otherwise coherent and close to implementable. The admin editor's safe read base is nevertheless part of the core write contract, not an implementation detail: the current public payload is lossy and the canonical PUT replaces a complete cross-ticker day. Until the plan specifies an authenticated, write-valid full-day load path and proves preservation of untouched records, implementation can produce silent canonical data loss while remaining content/DB coherent. The appropriate verdict is **revise**, not reject, because the correction is bounded and does not require changing the database, publisher, or authorization model.
