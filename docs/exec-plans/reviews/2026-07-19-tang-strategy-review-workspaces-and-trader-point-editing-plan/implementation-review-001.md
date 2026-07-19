# Implementation Review 001 — Review Workspaces And Trader Point Editing

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md`
- Review target revision: `v3-round-1-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `grok-build-external-2026-07-20-review-workspaces`
- Plan author ID: `codex-plan-author-2026-07-19-review-workspaces`
- Independence declaration: `attested`
- Evidence method: independent frozen-digest recomputation, protected-boundary hash inspection, source/contract inspection, accepted test and browser receipt assessment, and direct Grok Build vision inspection of all 19 required reference/Phase 3/Phase 4/Phase 5 PNGs
- Verdict: accept
- Confidence: high
- Reviewed frozen revision: `workspace-review-v1:3d24de3baf38cf6e13c8c7295528f22989cf67548d949e3cd98f0739d06717cd@d73502139e6d25d5e050c376e90289c70ef23ecc`
- Reviewed base HEAD: `d73502139e6d25d5e050c376e90289c70ef23ecc`

## Revision Integrity

Independent recomputation of packet §1 digests against the live worktree matched exactly. No revision drift.

| Input | Expected | Independent result |
| --- | --- | --- |
| base HEAD | `d73502139e6d25d5e050c376e90289c70ef23ecc` | match |
| 27 implementation files | `75c794e52f1ee5e92ae64c86654ecb8395cc4eb6a12a2de4d3d74c28530c8aa9` | match |
| tracked implementation diff | `e5c5faaf9018438dad6f0018091959cb7ab6639400ccfca00ffaa99fd527f7ce` | match |
| 6 untracked additions | `0506cdd36b26a740d2300965b475a7c8ddc5aea4f2da25a820a8f4b3839445ae` | match |
| accepted evidence set (63 files) | `08ef06b6e09244c2fde8b3cae9666b8e6386b4163a87db7737cd437b564e240b` | match |
| composite revision | `3d24de3baf38cf6e13c8c7295528f22989cf67548d949e3cd98f0739d06717cd` | match |

Protected-boundary hashes also matched packet §6: tracked DB `125fcc9d…05b0`, registry `cf6f3122…716c`, day `0d292b43…88fc`, Pages workflow `7fe8c2e9…0dc8`, exporter `601548fa…7996`. Phase 5 screenshot SHA-256s and the five required Phase 3 screenshot SHA-256s matched their evidence receipts. Staged changes: none. Protected content/DB/workflow paths show no `git diff` against HEAD.

Review proceeded under the frozen label with no tree substitution.

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | No blocking or non-blocking implementation findings. | — |

Acceptance history in the phase receipts records real defects that were fixed before freeze (preservation target ID wiring, direction/`option_type` sync, missing-day status, event-time known/unknown tuple, engine CSS leakage into Admin, Admin contrast, dark-sidebar trader-card contrast). None of those defects remain in the frozen implementation or the final multimodal receipts.

## Multimodal Visual Inspection Log

All 19 required images were opened with vision inspection, not filename/hash/OCR-only review.

1. **`design/references/2026-07-19-review-ui-reference-v1.png`** — Canonical dark trading-terminal reference: header “Daily Review”, QQQ selected with date chips Jul 17/14/10, left stack STRATEGY / SESSION / ELIGIBILITY / TRADER FILTER / TRADE GROUPS / SIGNAL TIMELINE, large right chart “KLINE ENGINE V2” with full generic toolbar, PUT/CALL markers, volume pane, and “SQLite review · Static Mode” footer. This is visual direction only.
2. **`output/playwright/review-workspaces-phase3-20260720/01-time-contract-before-save.png`** — Admin editor on light cream host: QQQ form selected, trader 沃德哥, event `buy_open` with `occurred_at=2026-07-17T09:42-04:00`, precision `minute`, `time_incomplete` unchecked, provenance `user_provided`, green preservation summary, enabled save, and reused dark engine preview. The known-time tuple is visibly complete before save.
3. **`output/playwright/review-workspaces-phase3-20260720/02-time-contract-after-save.png`** — Same Admin form after save: green success “已保存，服务端校验与投影完成。”, preservation count delta 0, known-time fields retained, and dark preview still present. Save feedback is visible and non-destructive to form state.
4. **`output/playwright/review-workspaces-phase3-20260720/03-server-validation-failure.png`** — Same form with invalid offset `2026-07-17T09:42-05:00`; red server error says the offset does not match America/New_York rules; unsaved input remains visible. Server-authoritative fail-closed UX is visible.
5. **`output/playwright/review-workspaces-phase3-20260720/05-readonly-capability.png`** — Readonly shell badge and capability explanation; inspection/export present; no editor form, save action, or registry mutation block. Mutation authority is visually absent.
6. **`output/playwright/review-workspaces-phase3-20260720/06-admin-contrast-fixed.png`** — Light Admin form text is readable on cream rather than white-on-white; dark engine preview is isolated inside the candidate-preview container; Tang group, Events, Normalization, and registry sections have clear contrast.
7. **`output/playwright/review-workspaces-phase4-20260720/01-static-spy-default.png`** — Static Daily Review with SPY selected, SPY-only date rail, Tang Focus, Tang CALL VERIFIED, one engine-owned toolbar including Overview, no login/admin/save chrome, and SPY 2026-07-17 chart.
8. **`output/playwright/review-workspaces-phase4-20260720/02-static-qqq-same-date.png`** — QQQ selected on the same date; rail contains only 07-17/07-14/07-10; only 沃德哥 Focus; PUT and CALL groups are VERIFIED; engine shows QQQ chart. Same-date switch and availability reconciliation are visible.
9. **`output/playwright/review-workspaces-phase4-20260720/03-static-legacy-link-no-trader.png`** — QQQ 2026-07-14 selected with neutral no-trader message and dashed no-normalized-trades state; no fabricated trader; engine still renders QQQ bars/signals. Honest legacy no-trader behavior is visible.
10. **`output/playwright/review-workspaces-phase5-20260720/01-data-desktop.png`** — Data page reports 2 tickers, 49 market days, and 11 strategies; SPY tab active with an SPY-only date rail grouped by month. No mixed ticker date list is visible.
11. **`output/playwright/review-workspaces-phase5-20260720/02-review-spy-desktop.png`** — Interactive dark Review with SPY selected, SPY-only rail, Tang Focus and CALL group, single engine toolbar with Overview, no outer duplicate toolbar, and SPY 2026-07-17 context. Direction aligns with the reference while preserving authenticated shell navigation.
12. **`output/playwright/review-workspaces-phase5-20260720/03-review-qqq-keyboard-recovered.png`** — QQQ selected after keyboard recovery, three-date QQQ rail, 沃德哥 Focus, both QQQ PUT/CALL cards, QQQ 2026-07-17 chart/export context, and automatic assembly status. SPY↔QQQ reconciliation is visible.
13. **`output/playwright/review-workspaces-phase5-20260720/04-admin-desktop.png`** — Admin desktop shows capability-labeled inspection, partitioned SPY/QQQ rails, public Tang CALL inspection, and the form-driven trader-point editor with its own non-mixed ticker/date context. Raw JSON is not the primary workflow.
14. **`output/playwright/review-workspaces-phase5-20260720/05-backtest-desktop.png`** — Backtest shows Run latest 10 days, 44 total signals, labeled ticker/date results, and one unified engine with Overview; page actions do not duplicate 1m/5m/Play controls.
15. **`output/playwright/review-workspaces-phase5-20260720/06-teaching-desktop.png`** — Teaching shows Rules 7, Cases 6, Training groups 3, page-specific Back/Advance/Reveal full day, one unified engine with Overview, and no page-level Play/Pause duplicate.
16. **`output/playwright/review-workspaces-phase5-20260720/07-review-narrow.png`** — Narrow Review uses a single-column chart→tabs→dates→business context→trader→groups→signals stack, retains QQQ context, and has no horizontal clipping.
17. **`output/playwright/review-workspaces-phase5-20260720/08-admin-narrow-validation.png`** — Narrow Admin retains focus/input for `2026-07-17T09:42` and shows a red explicit-offset validation alert; preservation remains visible and no save succeeds. Client validation and input retention are visible.
18. **`output/playwright/review-workspaces-phase5-20260720/09-readonly-desktop.png`** — Readonly desktop shows inspect/export only, SPY Tang CALL, no editor/save/registry blocks, and a readonly badge. Capability separation matches the Phase 3 receipt.
19. **`output/playwright/review-workspaces-phase5-20260720/10-static-narrow.png`** — Narrow Static places the chart first, then QQQ tabs and three-date rail, 沃德哥 only, groups and signal stream; Overview appears once, auth/mutation chrome is absent, and no horizontal overflow is visible.

## Contract And Behavior Review

| Contract | Independent assessment |
| --- | --- |
| `occurred_at` paired with `time_incomplete` / `time_precision` / provenance | Backend `trade_records.py` enforces known versus unknown tuples; frontend `applyOccurredAt` and `validateGroupForm` mirror them; Phase 3 images show the known-time tuple before save and invalid-offset failure. |
| Complete canonical day merge and untouched preservation | `mergeGroupIntoDay` / `preservationDiff` carry untouched groups and fail closed; the Phase 3 save receipt preserves other groups/context with the intended `+1` delta on a temporary copy only. |
| Public projection not used as write base | Admin editor loads `Api.adminTradeDay` / `Api.adminTraders`; backend coverage pins the public `trade-records-v1` projection as not write-valid `trades-day-v1`. |
| Admin-only canonical reads and existing atomic PUT | `GET/PUT /api/admin/traders` and `/api/admin/trade-records` remain behind `require_admin`; no new write-verb surface was introduced; Phase 3 records readonly 403 responses. |
| Overview reset and single control ownership | Engine owns `data-action="overview"` with viewport reset; Review/Static outer controls are removed; Backtest/Teaching toolbars retain only page-specific actions. |
| Static legacy hashes and no mutation/auth | Shared workspace hash contract remains; Static has no login/admin/save path; Phase 4 images cover SPY default, QQQ same-date, and legacy no-trader day. |
| Accessibility | Tabs use `role=tab`/`aria-selected`; dates use `aria-pressed`; Ext K uses `role=switch`/`aria-checked`; loading uses live status; errors use alerts; Phase 5 provides keyboard/focus/recovery receipts. |
| Workspace ticker/date partitioning | Pure `reviewWorkspace.js` implements SPY-preferring default, ticker-scoped rails, and same-date retention; Data/Review/Admin/Static images show no mixed ticker rail. |

Desktop Review versus the reference: authenticated shell navigation adds left width but preserves the compact dark-terminal direction, ticker parent, ticker-scoped dates, business context, and single engine-owned toolbar. Visual direction was not treated as behavior or accessibility proof.

## Verification Evidence Assessment

- Backend **78/78**, frontend **38/38**, lifecycle **146/146**, normal and static builds, and harness/governed/auto/operating/budget receipts are coherent with the frozen sources and images.
- Desktop `1672×941` and narrow `820×1180` matrices cover Data, Review SPY/QQQ, Admin, readonly, Backtest, Teaching, Static, validation, keyboard/recovery, loading, and alert behavior.
- Console classification is truthful: positive sessions retain only the existing favicon 404; negative sessions retain the intentionally injected 400/500 receipts.
- Acceptance history records found defects, fixes, and reruns rather than inventing a clean first pass.
- Grok did not independently complete the full test suites during this review session; confidence remains high because digests, source contracts, protected hashes, phase screenshot hashes, and all 19 vision inspections converge without contradiction.

## Authority And Boundary Review

- The worktree is intentionally dirty/uncommitted; the review target is the frozen digest, not an inferred commit.
- Tracked DB, canonical registry/day content, Pages workflow, and exporter hashes are unchanged; protected paths have no working-tree diff.
- Successful mutation acceptance used only temporary content/DB copies.
- No evidence shows unauthorized stage/commit, push, PR, merge, Pages, hosted verification, provider, or broker action.
- The review packet correctly recorded implementation verdict `none` before this external review.

## Required Follow-up

No remediation is required. The lifecycle may proceed to truthful closeout under the plan’s Phase 6 exit rules.

This `accept` does not authorize Git stage/commit, push, PR, merge, Pages publication, hosted verification, provider/broker access, or tracked DB/canonical content mutation without separate explicit user authority.
