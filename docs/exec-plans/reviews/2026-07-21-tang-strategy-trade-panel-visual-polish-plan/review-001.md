# Review 001 — Tang Strategy Trade Panel Visual Polish

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md`
- Review target revision: `v1-proposal-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-panel-polish-r1`
- Plan author ID: `grok-plan-author-2026-07-21-trade-panel-polish`
- Independence declaration: `attested`
- Evidence method: `Independent read-only inspection of the plan, startup and operating-mode contracts, linked OPT record, live screenshot and locked HTML mock, current shared components and all three consumers, CSS and test carriers, the QQQ 2026-07-17 fixture, governed harness output, and the 49-test frontend baseline.`
- Verdict: revise
- Confidence: high

## Scope Checked

- User-confirmed visual, language, trader-scale, and three-surface locks
- Current `TraderFilters`, `TradeExportControls`, and `TraderTradeList` behavior
- Review, Static, and Admin composition plus shared/scoped CSS contracts
- QQQ `2026-07-17` PUT/CALL fixture suitability
- Verification, accessibility, lifecycle, and authority boundaries

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | §2.2 criteria 2 and 8–9; §2.3; §4 Phase 0 verification | Replacing the native Eligibility `<select>` with a custom segmented control removes built-in single-select keyboard/state semantics, but the plan freezes only labels and enum wiring. The current 49-test suite tests pure data and source text; the three screenshots cannot prove focus, keyboard operation, programmatic selected state, or that each segment actually changes the filtered set. The locked mock itself uses three plain buttons under `role="group"`, so copying it literally would satisfy the visual criteria while regressing the control contract. | Freeze an accessible single-selection contract: native radio inputs in a labelled fieldset, or a complete `radiogroup`/`radio` implementation with one selected item and standard arrow-key focus/selection. Add a deterministic component/interaction receipt (or an equally strong browser receipt) that exercises `display`, `reported`, and `calculated`, verifies `onChange`/filtered results, and covers the shared control on the required surfaces. |
| P2 | §1.3 trader-scale lock; §2.2 criterion 4; §3.1 item 9; §4 Phase 0 baseline item 3 | The accepted direction says `>=7 summary + Edit`, and the mock uses English `Edit`, but the plan reopens the language decision during implementation and makes `tradeRecords.test.js` conditional. Current source and tests explicitly pin Chinese `编辑/全选/清空`, while the real QQQ fixture exposes too few traders to enter the drawer path, so V1–V3 cannot catch an inconsistent or broken `>=7` state. | Resolve the language in the plan revision instead of Phase 0; for the stated English-chrome direction, freeze `Edit / Select all / Clear` (plus the associated search/empty-state wording) across all three consumers. Make the test-file update mandatory and add a deterministic synthetic `>=7` trader case covering summary, open/close, search, select-all, and clear while preserving `TRADER_CHIP_INLINE_MAX = 6`. |
| P2 | §2.2 criterion 3; §2.3; §4 Phase 0 verification | “Source must not contain `Download JSON + 3 CSV`” is unscoped and therefore impossible as a repository-wide gate: the plan, OPT record, and locked mock intentionally retain the historical string as evidence. At the same time, existing tests validate `buildTradeRecordDownloads`, not the rendered button or its four-click download wiring after the control is moved into `TraderFilters`; the screenshot matrix proves only the short label. | Scope the negative text assertion to production frontend control/consumer sources and keep historical docs/mock exempt. Add a focused UI/browser receipt that clicks the short control, proves the JSON plus three CSV filenames are still emitted from the filtered selection, and confirms Review, Static, and Admin pass the same payload/groups/filters contract without a second Admin-header CTA. |

## Verified Strengths

- The OPT screenshot and both declared SHA-256 values match the repository artifacts.
- Current source confirms the stated three shared components, consumer locations, Admin header export placement, scoped `.dr-sidebar` density rules, six-trader threshold, and existing long Download copy.
- QQQ `2026-07-17` contains real `vordin` PUT and CALL groups, so the frozen visual card fixture is valid.
- The nine implementation paths cover the known production and source-contract surface without expanding into backend, DB, content, provider, or publication code.
- Baseline checks passed: governed/auto harness and all 49 frontend `test:trade-records` tests.

## Verdict Rationale

The visual direction, exact production surface, data invariants, fixture, and lifecycle/authority wording are substantially sound. Revision is required because the plan can currently pass its stated screenshots and source tests while shipping a keyboard-inaccessible Eligibility control, leaving the accepted drawer language unresolved, and failing to prove that the relocated Download control still emits all four files. These are bounded plan corrections; they do not justify implementation, activation, push, publication, data, provider, broker, or remote action.
