# Review 002 — Tang Strategy Review Date Navigation And Trader Filter Fusion

- Review target: `docs/exec-plans/proposed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`
- Review target revision: `v2-review-foldback-2026-07-20`
- Review type: design
- Reviewer ID: `grok-build-design-reviewer-2026-07-21-review-date-filter-fusion-r2`
- Plan author ID: `codex-plan-author-2026-07-20-review-date-filter-fusion`
- Independence declaration: `attested`
- Evidence method: Independent re-read of exact revision `v2-review-foldback-2026-07-20` (plan content SHA-256 `37c20e383ecaebe03ea3fbd78f90e9678514e434946a0f9cbf3717f600abb8d9`) against live HEAD `45ca9cb231ef459b7d03bad246d762ed1139bf86`; closure check of every `review-001` medium and non-blocking finding against operative v2 sections §1.4 / §2.2 / §2.3 / §3.1–3.4 / Phases 0–3 / §6 / §7.2; live re-check of shared `DateRail` callers, `focusedTraderId` carriers, `--trader-color` card/chip bindings, Ext K/Rescan/Backtest placement, protected DB/registry/publisher/exporter hashes, sole mockup jump row, and `docs/operating-modes.md` Proposed activation-recording gate. No eligible `proposal-revision` durable checkpoint existed at review time; content identity is the plan SHA-256 above. No implementation, browser acceptance, data write, provider/broker, stage/commit/push, PR, merge, Pages, or remote administration was performed.
- Verdict: approve
- Confidence: high
- Review target commit: `45ca9cb231ef459b7d03bad246d762ed1139bf86`

## Scope Checked

- Frozen v2 identity and foldback provenance (§1.4) against claimed v1 SHA and revision id
- Every `review-001` medium/non-blocking finding against operative v2 contracts
- Objective, success criteria, non-goals, progressive date API, B Chip, direction-color, utility, shell/typography, and protected boundaries
- File surface, phases 0–5, verification matrix, rollback, authority/activation gates
- Live repository evidence that pre-implementation friction still matches the proposal surface

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | — | — |

## Prior Finding Closures

Independently re-verified against live code and operative v2 text:

1. **Medium — month-nav selected-day visibility (review-001).** Closed. Criterion #3 is limited to init/restoration pressed state plus truthful topbar during later browse. §3.1 freezes presentation state `{ browseMode, browsedMonth }`, entry into `按月` at the selected day’s owning month, prev/next that never mutates workspace day, and a valid no-pressed chip rail when browsed month ≠ selected day. Phase 1/§7.2 fixtures cover enter-month, no-pressed browse, and Recent-with-old-selection.

2. **Medium — residual registry identity hue on shared trade surfaces (review-001).** Closed. Criteria #12–13 and §3.2/§3.4 forbid registry hue on shared chip/card name, border, active ring, background, and direction glyphs; require removal of live `style={{ '--trader-color': ... }}` card binding; keep CALL/PUT as the only hue channel; preserve registry color only for excluded non-trade-list uses such as Admin registry editing. Phase 2 scan and §6 rollback row cover residual `--trader-color`.

3. **Medium — Ext K/Rescan topbar utility IA (review-001).** Closed. Criterion #11 and §3.3 freeze right-side `.dr-topbar` mount immediately after the strategy badge, exact visible label `Review 工具`, interactive Ext K + Rescan only, Static Ext K only, `aria-expanded`/`aria-controls`, Escape close with focus return, no focus trap, optional outside-click that must not steal focus, and Backtest exclusion from both disclosures.

4. **Medium — list/chart/export ID equality semantics (review-001).** Closed. Criterion #9 and §3.2 define cross-consumer equality as canonical trader-ID **set membership**; UI remains availability/registry ordered; `exportSelectionFromFilters` retains unique alphabetical `trader_ids`; Phase 2/§7.2 require set comparison plus an independent alphabetical-export fixture.

5. **Non-blocking — mockup jump row (review-001).** Closed. §2.3 states the mockup `跳转` row is comparison-only and must not be copied, hidden, disabled, or shipped in v1; Phase 1 asserts no production jump control/handler/placeholder.

6. **Non-blocking — progressive prop naming (review-001).** Closed. §3.1 freezes `dateNavigation="exhaustive" | "progressive"` with exact default `exhaustive`, forbids boolean aliases and implicit caller detection, and limits progressive opt-in to `ReviewPage`.

## Verdict Rationale

**Verdict: `approve` / confidence `high`.**

V2 is a complete, implementable foldback of `review-001`. No blocking or medium contract gap remains for design approval of this exact revision.

**Current-contract coherence against live evidence:**

1. **Protected baselines still match.** Tracked SQLite `125fcc9d...05b0`, registry `cf6f3122...716c`, Pages publisher `7fe8c2e9...0dc8`, static exporter `601548fa...7996`, and sole mockup `ff5d71ff...3c50` all match §1.1/§3.6.
2. **Live UI friction still matches the plan surface.** Shared `DateRail` remains exhaustive; interactive Review still hosts Ext K / Rescan / Backtest in the left column; `focusedTraderId` and checkbox+Focus remain; list/card still bind `--trader-color`; shell capability copy is still long-form; product chrome still uses Space Grotesk / Newsreader.
3. **User-locked product decisions remain intact.** Progressive 最近/按月 with N=12; B Chip multi-select with `<=6` inline and `>=7` summary/drawer; no Focus; empty selection legal; Static/Data/Admin/TraderPointEditor keep exhaustive DateRail; CALL `#6F9F7A` / PUT `#E06B66`; YaHei UI stack; no backend/DB/content/exporter/workflow change.
4. **Phase structure, verification matrix, rollback, and authority ledger remain coherent** with `docs/operating-modes.md`. §8–9 correctly state that `review-001` cannot approve v2, that matching-revision approve does not activate or implement, and that activation and implementation-start remain separate user instructions.
5. **No new medium/blocking defect was introduced by the foldback.** The month state machine, identity-color negative contract, utility IA, and set-equality/export-order split are mutually consistent and fixture-backed in Phases 1–3 and §7.2.

**Residual non-blocking implementation freezes (do not reopen design):**

- Outside-click close for `Review 工具` remains optional; if implemented, it must obey the existing “no second close contract / no focus steal” rule already frozen in §3.3.
- Optional list direction rail may use CALL/PUT semantic color only; Phase 0 may freeze whether the rail is present without reopening name/color identity rules.

**Authority boundary:** This matching-revision design `approve` does **not** activate the plan, start implementation, stage/commit/push, write canonical data, open PR/merge, publish Pages, or grant provider/broker/remote authority. No eligible `proposal-revision` durable checkpoint existed for this revision; the `Review target commit` field records the claimed proposal baseline HEAD, while plan content identity for this inspection is SHA-256 `37c20e383ecaebe03ea3fbd78f90e9678514e434946a0f9cbf3717f600abb8d9`. After this review, the next legal user action is an explicit activation instruction that must stop at `phase-0:not-started`; implementation requires a later explicit start instruction. Local durable checkpoints, if later authorized, must follow `docs/operating-modes.md` §9–10 and cannot reuse prior Terminal UI or governance authority.

## Unverified By Design-Review Boundary

- Browser/desktop-narrow progressive rail, drawer, and `Review 工具` execution
- Computed Microsoft YaHei fallback rendering on non-Windows hosts
- Simulated 7/8-trader fixture injection without canonical writes
- Eligible `proposal-revision` / `design-review` durable checkpoint ancestry
- Hosted Pages, provider/broker, and tracked content mutation behavior
