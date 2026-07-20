# Review 001 — Tang Strategy Review Date Navigation And Trader Filter Fusion

- Review target: `docs/exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`
- Review target revision: `v1-proposal-2026-07-20`
- Review type: design
- Reviewer ID: `grok-build-design-reviewer-2026-07-20-review-date-filter-fusion-r1`
- Plan author ID: `codex-plan-author-2026-07-20-review-date-filter-fusion`
- Independence declaration: `attested`
- Evidence method: Independent worktree inspection of exact revision `v1-proposal-2026-07-20` (plan content SHA-256 `e8073198d00ed6356dbbe2737dc507a790b846af925c55b67a602f8fa034a9be`) against live HEAD `45ca9cb231ef459b7d03bad246d762ed1139bf86`, source optimization batch + sole locked mockup + three screenshot hashes, `ReviewContextPanel.jsx` / `reviewWorkspace.js` / `TraderFilters.jsx` / `tradeRecords.js` / `TraderTradeList.jsx` / `ReviewPage.jsx` / `StaticReviewsApp.jsx` / `AdminTradersPage.jsx` / `Layout.jsx` / `styles.css`, protected DB/registry/publisher/exporter hashes, and `docs/operating-modes.md` Proposed design-review contract. No eligible `plan-proposal` durable checkpoint existed at review time; content identity is the plan SHA-256 above. No implementation, browser acceptance, data write, provider/broker, stage/commit/push, PR, merge, Pages, or remote administration was performed.
- Verdict: revise
- Confidence: high
- Review target commit: `45ca9cb231ef459b7d03bad246d762ed1139bf86`

## Scope Checked

- Plan objective, success criteria, non-goals, and single-plan bundling of OPT-001 through OPT-005
- Live repository evidence claimed in §1.1–1.2 against current HEAD, optimization record, mockup, and protected hashes
- Progressive DateRail opt-in contract vs shared exhaustive DateRail callers
- B Chip multi-select, `focusedTraderId` removal carriers, empty-selection and context reconciliation
- Direction-color identity contract vs live list/chart/registry-color CSS channels
- Ext K / Rescan / Backtest relocation and shell label / YaHei typography contracts
- Candidate file surface, phases 0–5, verification matrix, rollback, and authority boundaries
- Authority/lifecycle wording against `docs/operating-modes.md` (review-only; no activation/implementation)

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Medium | §2.2 #3 / §3.1 | Success criterion language says the selected day is always programmatically and visually present, but §3.1 only freezes initialization/restoration mode selection and defines month state as presentation-only. Interactive `按月` prev/next while the selected day is outside the displayed month, and manual switches from `最近` to `按月`, are underspecified. | Freeze an explicit month-navigation state machine: (1) entering `按月` opens the owning month of the current selection; (2) prev/next either keep selection and allow a non-pressed chip rail with topbar date still truthful, or refuse leaving the selected month — pick one; (3) rewrite criterion #3 so it either applies only to deep-link/restoration or states the true global invariant with matching fixtures. |
| Medium | §3.4 / §2.2 #12–13 | Plan maps CALL/PUT exact colors to chart markers and list glyph/word/optional rail and requires default name text, but live `TraderTradeList` / `.trade-group-card` still drive card left border, active ring, and direction triangles through registry `--trader-color`. The plan does not forbid that residual identity-color channel on shared trade surfaces. | Add a negative contract: Review/Static/Admin shared trade list/card chrome must not use registry trader hue for borders, active rings, chips, or direction glyphs; direction owns the only hue channel; remove or neutralize `--trader-color` style binding on those surfaces; keep registry color for non-Review uses such as Admin registry editing. |
| Medium | §3.3 / Phase 3 | Ext K/Rescan leave the left column and move to a “compact topbar utility disclosure,” but visible label, mount point, required disclosure vs inline controls, and Escape/outside-click rules are soft (“only if … without weakening native focus”). Static Ext K parity is stated without the same minimum IA. | Freeze minimum IA: interactive header disclosure button with stable visible label, `aria-expanded`/`aria-controls`, containing existing Ext K switch + Rescan only; Static equivalent with Ext K only; Escape closes and returns focus; outside-click optional but must not trap focus; Backtest must not enter the disclosure. |
| Medium | §3.2 / §2.2 #9 / Phase 2 verification | Plan requires selection order reconciled to availability/registry order so list, chart, and export cannot disagree, while live `exportSelectionFromFilters` alphabetically sorts `trader_ids`. “Exact equality of selected trader IDs” is therefore ambiguous between set equality and sequence equality. | Freeze comparator semantics: prefer set equality and retain the existing alphabetical export sort contract, or explicitly change export to registry order and update fixtures. Do not leave both implications live. |
| Non-blocking | §2.3 / mockup | Sole mockup still renders a free-form `跳转` row while the plan correctly makes free-form jump a v1 non-goal. Implementers may copy the mockup control by accident. | Add one explicit non-implementation note that mockup jump UI is comparison-only and must not land in v1. |
| Non-blocking | §3.1 / Phase 0 | Progressive DateRail is “explicit opt-in” without a named prop/API (`variant`, `navigationMode`, or equivalent). | Name the candidate prop in v2 or Phase 0 freeze so `ReviewContextPanel`/`DateRail` API and caller inventory stay deterministic. |

## Verdict Rationale

**Verdict: `revise` / confidence `high`.**

The proposal is directionally correct, evidence-backed, and mostly implementable. Independent inspection confirms:

1. **Provenance and evidence are real.** Optimization batch is `promoted-to-proposed`; mockup SHA-256 `ff5d71ffa87bb65127f0bcf05d421e07c211678cff19473f9f88672337233c50` and the three friction screenshot hashes match on-disk files; live HEAD is `45ca9cb231ef459b7d03bad246d762ed1139bf86` as claimed; protected hashes for tracked DB `125fcc9d...05b0`, registry `cf6f3122...716c`, Pages publisher `7fe8c2e9...0dc8`, and static exporter `601548fa...7996` match §3.6 exactly.
2. **Current UI friction matches the plan.** Shared `DateRail` is exhaustive for every caller; interactive Review still stacks Ext K / Rescan / Backtest in the left column; `TraderFilters` still mirrors ticker/date and uses checkbox + Focus with `focusedTraderId` override in filter/export/reconcile; list/chart direction presentation still uses registry trader color; shell trader destination still renders long capability copy next to `交易记录 / 点位管理`; product chrome still imports Space Grotesk / Newsreader.
3. **User-locked product decisions are correctly carried.** Progressive 最近/按月 with N=12; B Chip multi-select with inline `<=6` and summary/drawer `>=7`; no Focus; empty selection legal; Static/Data/Admin/TraderPointEditor keep exhaustive DateRail; CALL `#6F9F7A` / PUT `#E06B66`; names default text color; Microsoft YaHei UI stack; no backend/DB/content/exporter/workflow change.
4. **Phase structure, verification matrix, rollback, and authority ledger are coherent** with `docs/operating-modes.md`. Design approval still cannot activate or implement; activation and implementation remain separate user instructions; Git/data/remote remain unauthorized.
5. **No blocking false contract was found** against live validators or protected runtime boundaries. The defects are implementable-contract gaps that would freeze ambiguous Phase 0/1/3 acceptance if approved as-is.

The required foldback is contract precision, not product direction. Medium findings on month-navigation visibility, residual registry-color list chrome, topbar utility IA, and export ID equality semantics must be closed in a new stable revision before matching-revision design approval. Non-blocking notes on mockup jump and progressive prop naming should be folded in the same revision when cheap.

**After foldback, re-review the new stable revision.** Approval of `v1-proposal-2026-07-20` does not qualify. This review does not activate, implement, stage, commit, push, write canonical data, or grant any remote/publication authority. No eligible `plan-proposal` durable checkpoint existed for this revision; the `Review target commit` field records the claimed proposal baseline HEAD, while plan content identity for this inspection is SHA-256 `e8073198d00ed6356dbbe2737dc507a790b846af925c55b67a602f8fa034a9be`. A later qualifying matching-revision review should target an eligible checkpoint commit under separate local Git authority.

## Unverified By Design-Review Boundary

- Browser/desktop-narrow progressive rail, drawer, and topbar utility execution
- Computed Microsoft YaHei fallback rendering on non-Windows hosts
- Simulated 7/8-trader fixture injection without canonical writes
- Any sibling concurrent review output
- Hosted Pages, provider/broker, and tracked content mutation behavior
