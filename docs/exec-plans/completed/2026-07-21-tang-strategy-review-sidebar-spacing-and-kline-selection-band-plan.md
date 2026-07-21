# Tang Strategy Review Sidebar Spacing And K-line Selection Band

- Lifecycle schema: `operating-modes-v1`
- Status: Completed
- Plan slug: `2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan`
- Revision: `v2-review-foldback-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-sidebar-spacing-selection-band`
- Design reviews: ../reviews/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan/review-001.md@revise@v1-proposal-2026-07-21, ../reviews/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan/review-002.md@approve@v2-review-foldback-2026-07-21
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: user-instruction:2026-07-21-activate-sidebar-spacing-and-kline-selection-band-plan
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: ../reviews/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan/implementation-review-001.md@accept
- Final disposition: Completed
- Verified implementation commit: 5f36d29a44fb12aee2319ae147303cc970d83193
- Lifecycle reconciliation commit: none
- Owner: Grok
- Created: 2026-07-21
- Optimization source: `docs/optimization/2026-07-21-review-sidebar-spacing-and-kline-selection-band/2026-07-21-review-sidebar-spacing-and-kline-selection-band.md` OPT-001 + OPT-002
- Proposal baseline: `codex/project-harness@652092bd4577eeb004b2d4eda4c9452b8dd98f83`
- Scope authority: full local execution under `user-instruction:2026-07-21-execute-sidebar-spacing-and-kline-selection-band-plan` (goal OBJECTIVE 这个active plan交给你全权负责执行). Matching design approval `review-002: approve/high`. Implementation review `implementation-review-001: accept/high`. Product commit `5f36d29a44fb12aee2319ae147303cc970d83193`. No push/PR/merge/Pages/provider/broker/DB/content day-file/remote.
- Local commit: task-scoped default; does not authorize implementation start, push, or remote action

## 1. Context And Evidence

### 1.1 Proposal provenance

用户在 2026-07-21 完成 OPT batch record closeout 后，于本会话明确要求：**根据该 OPT 生成 prop plan → codex 独立 design review → 按 review 迭代直到 approve → 将 prop plan 迁移到 active**。

| OPT | Title | 本计划 | 备注 |
| --- | --- | --- | --- |
| **OPT-001** | Sidebar Trade tools / trader cards / strategy detail stack needs gaps | **In scope** | ≈20px inter-block gaps + 交易者/策略讲解 captions + hairline dividers; Traders-row dedupe |
| **OPT-002** | Trader select blue K-line band overlay is too loud | **In scope** | Cancel blue selection band entirely; no replacement cue; keep click-to-locate / fitRange; marker labels unchanged |

Only these two OPTs from batch `2026-07-21-review-sidebar-spacing-and-kline-selection-band` are promoted. Adjacent session OPTs and completed plans stay closed.

相关已完成边界（不得回退）：

- Trade Tools / Group Span / Viewport / Data Rail — introduced multi-bar **blue** group band + span-fit + event-row focus; OPT-002 is post-ship **visual cancellation** of that band, not a reopening of span-fit / TF / Data rail contracts.
- Trade panel visual polish — tools strip + short Download chrome; OPT-001 removes the **visible** Download entry from Review/Static stack only.
- Trade points + marker labels — card points-only + marker `display_name BUY|SELL` must remain.
- Data progressive nav + card density — density under `.dr-sidebar` retained for **in-card** metrics; this plan adds **inter-block** rhythm only.

### 1.2 Review foldback closure map

#### review-001 closure (v1 → v2)

Independent `review-001` returned `revise/high` against exact revision `v1-proposal-2026-07-21` (plan SHA-256 `411e8887b6586f94fcdc7e2a7c637bef6fb2cd68e284ea2c92c0e643bef96819` at HEAD `93191ef38e7c75d77920739f0c8faf4e93613426`). Revision `v2-review-foldback-2026-07-21` folds the sole P1 finding:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | Mandatory B-* carriers were abstract; tracked group-span runner still requires non-empty blue highlight and uses highlight storage as span oracle; that runner path was absent from the modify manifest | §2.4 + §3.1 freeze **replacement** tracked runner `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs` as the **only** mandatory browser carrier for this plan’s B-Sidebar-layout / B-Group-band-cancel / B-Event-focus-cancel. Historical completed-plan runner `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs` is **out of this plan’s modify set** (append-only historical evidence for the completed group-span plan; this plan does not re-run it as an exit gate). Independent oracles: pure `groupBarSpan(group, bars1m)` and `eventFocusPayload(event, bars1m)` (or fixture-precomputed start/end indices) — **never** stored highlight ranges. After group/event select: `getHighlightRanges()` must be empty/`[]`; viewport from `getViewportDebug()` must contain the independent expected indices; no post-fit recenter. Layout: measured ≈20px separation between explicit tools / traders / signals block wrappers with captions, hairlines, and Download absence on Review **and** Static. Screenshots V1–V3 remain supplemental. |

`review-001` is append-only prior-revision evidence and **cannot approve v2**. Next gate is independent design review of exact revision `v2-review-foldback-2026-07-21`.

### 1.3 Visual evidence

| 证据 | 路径 | SHA-256 | 作用 |
| --- | --- | --- | --- |
| Sidebar stack no gap (live) | `docs/optimization/2026-07-21-review-sidebar-spacing-and-kline-selection-band/screenshots/2026-07-21-review-sidebar-stack-no-gap.png` | `e7846e060f3f7f5049dd92edc512de39f939dab11670cfc4ac0667d969020d37` | OPT-001 friction |
| Blue selection band (live) | `docs/optimization/2026-07-21-review-sidebar-spacing-and-kline-selection-band/screenshots/2026-07-21-review-kline-selection-blue-band.png` | `a5cf3b8a4f64ab86775e16ecb00a3bfcb842c02698e87f1892772dad5b5de89d` | OPT-002 friction |
| Confirmed design mock | `docs/optimization/2026-07-21-review-sidebar-spacing-and-kline-selection-band/mock.html` | `f2386dbd46aff8c472d635aa3c53f2071ca4e2f22d6d053ffa366abf8981ce46` | Locked proposal surface (`opt001=fixed`, `opt002=none`) |

Untracked informal `output/playwright/mock-*.png` trees are **not** batch evidence and must not be staged.

### 1.4 Current repository facts

**OPT-001 — sidebar mid-stack rhythm:**

- `.dr-sidebar` hosts progressive date context, then `.dr-signal-list` with three mid-stack blocks in order:
  1. `TraderFilters` (`.trade-filter-panel`) — head shows `Trade tools` title + `exportControls` (Download);
  2. `TraderTradeList` (`.trade-record-list`) — group cards;
  3. `ReviewSignalList` — strategy signal / 策略讲解 detail.
- Shared on **Review** (`ReviewPage.jsx`) and **Static** (`StaticReviewsApp.jsx`).
- `.dr-signal-list` is a scroll column with `padding: 8px` and no stable inter-block gap between the three children.
- Density rules under `.dr-sidebar` (card font/padding/gaps) remain from completed density plan; cards themselves are not the target of new spacing.
- `TraderFilters` still renders:
  - `.trade-tools-title` text `Trade tools`;
  - optional `exportControls` slot fed by `TradeExportControls` from Review/Static.
- Admin `AdminTradersPage` also composes filters + Download but is **out of this plan’s visual stack scope** unless a shared-component change would otherwise break Admin composition (see §3.1).

**OPT-002 — blue selection band:**

- `selectTradeGroup` on Review/Static: `setHighlightRanges({ timeframe:'1m', startIndex, endIndex, style:'blue' })` then `fitRange(...)` with no post-fit center (completed group-span plan).
- `focusTradeEvent` uses `eventFocusPayload(...).style = 'blue'` and the same highlight + fitRange path for single-bar focus.
- Engine `drawHighlightRanges` paints multi-bar translucent bands for `style: 'blue'` / `red`; that paint is the loud overlay users rejected.
- Engine seams available for browser proof: `getHighlightRanges()`, `getViewportDebug()`, `fitRange`.
- Pure oracles already exported: `groupBarSpan(group, bars)`, `eventFocusPayload(event, bars, options)`.
- Historical tracked runner `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs` **requires** non-empty blue highlights and uses highlight storage as the span oracle — incompatible with OPT-002 cancel; **not** this plan’s exit carrier.
- Marker labels (`display_name` + BUY/SELL) already identify trade points on chart; user decided no replacement cue after band removal.
- Strategy signal annotations may still use blue styles for non-trade flows; those paths are **out of scope** unless they share the exact trade-group/event select sequence this plan changes.

### 1.5 User scope locks (frozen in this proposal)

| Decision | Lock |
| --- | --- |
| Surface parity | **Review and Static must stay aligned** for both OPT items |
| OPT-001 friction | Trade tools → trader cards → strategy detail / 策略讲解 have almost no vertical gap |
| OPT-001 layout | ≈**20px** stable inter-block gaps between the three mid-stack blocks |
| OPT-001 captions | 交易者 (Trades) and 策略讲解 (Signals) section captions with hairline dividers on those two blocks |
| OPT-001 density | **In-block** card density, type scale, and information content **unchanged** |
| OPT-001 Traders row | Dedupe to a **single `Traders` label** + chips/drawer; remove panel title **`Trade tools`** / `TRADE TOOLS` |
| OPT-001 Download disposition (**frozen**) | **Remove** the visible Download control from the Review **and** Static trade-tools / Traders stack. **Do not relocate** it into another Review/Static chrome surface in this plan. Keep pure export helpers (`buildTradeRecordDownloads`, `exportSelectionFromFilters`, `TradeExportControls` component file) available. **Admin** may continue to render Download via the same component. Filter/export **payload semantics** unchanged. |
| OPT-002 keep | Clicking a left-side trader still **quickly locates** the trade span/point via `fitRange` (group span-fit contract retained) |
| OPT-002 band | **Cancel the blue selection band entirely — no replacement cue** (no outline, no marker substitute, no dim overlay) |
| OPT-002 event-row adjacency (**frozen**) | On Review/Static trade paths, **also cancel** highlight paint for event-row focus (`focusTradeEvent` / `eventFocusPayload` consumers must not leave a blue band/dot overlay after select). Keep event-row `fitRange` locate. Pure helper may retain a `style` field for tests, but live integration must not paint selection chrome. |
| OPT-002 markers | Marker labels (`display_name` + BUY/SELL) **unchanged** |
| Out of scope | Trade data contract; strategy assemble pipeline; progressive date rules; App shell left nav; tracked DB/content; provider/Pages; Admin visual redesign; Eligibility reintroduction; TF/viewport/Data-rail reopening |

Rejected: softer band, outline, or extra chart cue after band removal. Rejected: leaving Download disposition open to Phase 0. Rejected: expanding to Admin sidebar restyle or new export menu IA.

### 1.6 Lane 3 classification

Shared Review/Static presentation (CSS + filter chrome composition + trade-select highlight sequence) with multi-surface parity and source-contract tests. Classified Coding Mode **Lane 3** (proposed Exec Plan). No backend, API, DB, content, market-data, provider/broker, or Pages workflow changes.

## 2. Objective And Success Criteria

### 2.1 Objective

在 **Review 与 Static** 对齐的前提下：(1) 给 `.dr-sidebar` 中段 **Trade tools / 交易者卡片 / 策略讲解** 三块加上稳定间距与小节标，并去掉重复的 `Trade tools` 标题与 Review/Static Download 入口；(2) 取消交易者组选 / 事件聚焦后的蓝色 K 线选区带，保留 click-to-locate / fitRange 与 marker 标签契约。

### 2.2 Success criteria

1. **Inter-block gaps (OPT-001):** Between the three mid-stack blocks inside `.dr-sidebar .dr-signal-list` (filters panel, trade list, signal list), vertical separation is stable ≈**20px** (±2px measured on desktop fixture). In-block card gaps/type scale from the density plan remain valid.
2. **Section captions (OPT-001):** Trader list block shows caption **交易者** (with English subtitle/meta **Trades** allowed as in mock) and a hairline divider. Strategy detail block shows caption **策略讲解** (Signals) and a hairline divider. Filters/tools block has **no** `Trade tools` / `TRADE TOOLS` title.
3. **Traders-row dedupe (OPT-001):** Review/Static tools row is a single `Traders` label + chips/drawer only. Production sources for Review/Static composition paths do **not** render `Trade tools` as a visible panel title.
4. **Download disposition (OPT-001):** Review and Static **do not** mount `TradeExportControls` / Download in the sidebar trade-tools stack. Admin may still mount Download. Pure export builders remain importable and covered by existing Node pure tests. No new Review “tools menu” export entry in this plan.
5. **Group select band cancel (OPT-002):** After left-side trader/group select on Review and Static, chart **must not** show a blue (or any color) translucent multi-bar selection band. Sequence is: derive span → **clear or skip** selection highlight paint → single `fitRange` for the group span → **no** post-fit centering `scrollTo` that mutates the fitted window (retain completed group-span non-recenter invariant).
6. **Event-row focus paint cancel (OPT-002):** After timeline event-row click, chart **must not** paint a blue selection band/dot overlay; `fitRange` still centers/focuses the event bar. Marker labels remain the only trade-point callouts.
7. **Locate retained:** Group select still brings the full mapped group span into view via `fitRange` with the same padding contract as the completed group-span plan (`paddingRatio: 0.2`, `minPadding: 4` unless Phase 0 records an equivalent frozen pair). Event-row keeps its tighter fit (`paddingRatio: 0.35`, `minPadding: 8` or equivalent frozen pair).
8. **Marker contract unchanged:** `buildTradeRecordAnnotations` still emits `display_name` + BUY/SELL labels; no redesign of marker chrome.
9. **Surface parity:** Review and Static share the same spacing, caption, title/Download removal, and highlight-cancel behavior.
10. **Tests/builds/receipts:** All **N-*** carriers green under `npm run test:trade-records`; all **B-*** / **V-*** carriers green and recorded under untracked `output/`; normal + static Vite builds green; harness auto green.

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review sidebar mid-stack | desktop `1672x941` | SPY or QQQ `2026-07-17` | ≈20px gaps; 交易者 / 策略讲解 captions + hairlines; no `Trade tools` title; no Download in stack |
| V2 | Interactive Review chart after group select | desktop `1672x941` | SPY `2026-07-17` preferred (matches OPT blue-band screenshot) | Group locate/fitRange; **no** blue band; markers still readable |
| V3 | Static Review sidebar + group select | desktop `1672x941` | Same day as V1/V2 | Parity with V1/V2 on spacing and band cancel |

Compare against §1.3 live screenshots and `mock.html` proposal state.

### 2.4 Frozen verification carrier matrix

| Carrier ID | Tool | Proves | Must not claim |
| --- | --- | --- | --- |
| **N-Sidebar-source** | Node `npm run test:trade-records` (source inspection) | Review/Static production sources: no mounted `TradeExportControls` in sidebar stack; no visible `Trade tools` title string in `TraderFilters` head; caption/class markers present for 交易者 / 策略讲解 (or shared section-caption components) | Measured px gaps; browser paint |
| **N-Highlight-source** | Node source inspection of Review/Static select paths | `selectTradeGroup` / `focusTradeEvent` do not call `setHighlightRanges` with `style: 'blue'` (or any paint style) for trade group/event select; they either skip highlight or clear via `setHighlightRanges(null)` / `[]` before/after fitRange; fitRange still present | Engine canvas pixels |
| **N-Marker-regression** | Existing/updated pure marker tests | Marker label contract still holds after any shared edits | Band paint |
| **N-Export-pure** | Existing pure download tests | `buildTradeRecordDownloads` / selection helpers still work; Admin may still import `TradeExportControls` | Review/Static Download UI presence |
| **N-Span-oracle** | Node pure tests on `groupBarSpan` / `eventFocusPayload` | Deterministic expected start/end indices for the frozen multi-event fixture group (and one named event) used by B-* carriers | That browser paint is empty |
| **B-Sidebar-layout** | Tracked Playwright runner §3.1 item 8 | On Review **and** Static desktop `1672x941`: measure bounding-box vertical gap between the three explicit mid-stack wrappers (tools/filters, traders list, signals list) ≈20px (±2px); captions 交易者 / 策略讲解 and hairlines present; Download control **absent** in `.dr-sidebar` trade stack | Export payload bytes; Admin-only layout |
| **B-Group-band-cancel** | Same tracked runner | Deterministic fixture group click: `getHighlightRanges()` empty; independent expected span from pure oracle (precomputed or injected via page.evaluate of known indices); `getViewportDebug()` window contains `[expectedStart, expectedEnd]`; no post-fit recenter that shrinks/moves off the span | Using highlight storage as the expected span |
| **B-Event-focus-cancel** | Same tracked runner | Named timeline event-row click: `getHighlightRanges()` empty; independent single-bar expected index; focused bar inside `getViewportDebug()` window; window not full-day (`end-start+1 ≤ 120` on 1m) | Full-day fit; highlight-as-oracle |
| **V1–V3** | Screenshots from same runner under `output/` | Visual acceptance vs mock | Interaction semantics alone |

**Tracked runner (mandatory, review-001):** `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs`

- Owns **B-Sidebar-layout**, **B-Group-band-cancel**, **B-Event-focus-cancel**, and V1–V3 screenshots.
- Receipts under untracked `output/playwright/review-sidebar-spacing-selection-band-<timestamp>/`.
- Fixture: Interactive Review + Static; prefer **SPY `2026-07-17`** for band screenshot parity, or **QQQ `2026-07-17`** multi-event group `tg_20260717_vordin_qqq_002` when multi-event timeline is required. Phase 0 freezes the exact group id + event row index and records the pure-oracle expected indices in the runner constants.
- **Independent oracle rule:** expected span/event indices come from pure `groupBarSpan` / `eventFocusPayload` (Node **N-Span-oracle** and/or runner constants computed from the same helpers offline). **Forbidden:** reading `getHighlightRanges()` to define the expected range.
- **Empty highlight rule:** after group select and after event focus, `getHighlightRanges()` length is `0` (or engine-equivalent clear).
- Historical `trade-tools-group-span-viewport-data-rail-acceptance.mjs` is **not** a Phase 1 exit carrier for this plan.

**Hard rule:** Missing any mandatory **B-*** receipt fails Phase 1 exit. Source-only proofs cannot substitute for band-cancel or gap measurement.

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/TraderFilters.jsx` — remove `Trade tools` title head; stop rendering `exportControls` in the Review/Static tools stack (prop may remain for Admin backward-compat **or** Admin can pass null and mount Download beside filters itself — pick one approach in Phase 0 and document; default: keep optional `exportControls` slot but Review/Static pass `null` / omit).
2. `frontend/src/pages/ReviewPage.jsx` — stop passing `TradeExportControls` into `TraderFilters`; cancel group/event highlight paint while keeping fitRange locate sequences.
3. `frontend/src/pages/StaticReviewsApp.jsx` — same composition and highlight-cancel as Review.
4. `frontend/src/features/review/TraderTradeList.jsx` and/or `ReviewSignalList.jsx` — add section captions + hairline structure for 交易者 / 策略讲解 if not introduced via wrapper in the list column; ensure three mid-stack blocks have stable, queryable wrappers for gap measurement.
5. `frontend/src/styles.css` — inter-block gap ≈20px under `.dr-sidebar .dr-signal-list` (or equivalent scoped selectors); caption + hairline styles; ensure density in-card rules remain.
6. `frontend/src/features/review/tradeRecords.js` — only if needed for eventFocusPayload comments/defaults; **do not** change marker label builder contracts. Optional: document that `style: 'blue'` is unused by Review/Static trade select after this plan. Pure `groupBarSpan` / `eventFocusPayload` remain the independent span/event oracles.
7. `frontend/src/features/review/tradeRecords.test.js` and/or `reviewWorkspace.test.js` — **N-Sidebar-source**, **N-Highlight-source**, **N-Span-oracle**, retain **N-Export-pure** / **N-Marker-regression**.
8. `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs` — **new** tracked Playwright runner implementing **B-Sidebar-layout**, **B-Group-band-cancel**, **B-Event-focus-cancel**, and V1–V3. Uses independent oracles and empty-highlight assertions as frozen in §2.4. Does **not** reintroduce blue-band expectations.

**May touch only if required for Admin composition safety:**

9. `frontend/src/pages/AdminTradersPage.jsx` — only if removing default export slot behavior would hide Admin Download; restore Admin Download placement without reintroducing Review/Static Download.

**Explicitly out of modify set (historical only):**

10. `frontend/scripts/playwright/trade-tools-group-span-viewport-data-rail-acceptance.mjs` — completed-plan historical runner; **not** this plan’s Phase 1 exit gate; do not treat its blue-highlight asserts as still authoritative for OPT-002.

**Lifecycle / evidence (separate authority per phase):**

11. Optimization record + `docs/optimization/index.md` status/lifecycle links.
12. `PROGRESS.md` / `HANDOFF.md` state blocks.
13. Plan file + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + roadmap.
14. Screenshots / Playwright receipts under `output/` (untracked).

**Out of manifest / must not change:**

- Backend, API, tracked DB, seed, content day files, Pages workflow, daily runbook, provider/broker.
- Progressive DateRail IA; App shell left nav.
- Marker label/title vocabulary; direction colors; card density px table for in-card elements (except intentional inter-block gap rules documented in phase evidence).
- TF first-paint / Data `data-market-days-rail` contracts from the completed group-span plan (product code paths remain; only trade selection **paint** is cancelled).
- Export file formats/columns from pure builders.
- New product dependencies or test harnesses beyond existing Node suite + Playwright.

### 3.2 Unrelated dirty paths to preserve

Untracked `output/playwright/**` and other `output/**` trees are user/evidence-owned. Do not stage, delete, or mix them into lifecycle commits.

### 3.3 Safety / data boundaries

- Frontend presentation only. No DB rebuild, no content mutation, no provider fetch, no Pages publish, no push/PR/remote.
- Fail closed on authority: activation and implementation each require their own explicit user instruction beyond this proposal text (this user session already chains **approve → activate** after matching design approve; it does **not** start Phase 0 implementation).

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: plan Active + explicit implementation-start / execute instruction (not granted by proposal or by activation alone).
- Work:
  - Record HEAD baseline and re-hash §1.3 evidence.
  - Confirm green `npm run test:trade-records` and current group-select sequence on Review/Static.
  - Freeze exact fixture group id + event-row index for B-* carriers; compute and record pure-oracle expected indices via `groupBarSpan` / `eventFocusPayload` into the new tracked runner constants.
  - Choose Admin Download composition approach (§3.1 items 1/9) and write it into phase evidence.
  - Freeze exact CSS selector / wrapper plan for 20px gaps and caption classes without undoing density pins.
  - Scaffold or outline the new tracked runner path (item 8) so Phase 1 implements against a known file.
- Verification: manifest paths listed including the new runner; no backend/DB paths; OPT-001/002 only; independent oracle constants non-empty.
- Exit gate: `phase-0-exit` with baseline note under reviews evidence or untracked `output/`.

### Phase 1 — Implementation (OPT-001 + OPT-002)

- Entry gate: `phase-0-exit` complete + implementation still authorized.
- Work:
  - Apply spacing, captions, Traders-row dedupe, Review/Static Download removal.
  - Cancel group + event highlight paint; keep fitRange locate; keep markers.
  - Implement/update Node carriers including **N-Span-oracle**.
  - Implement tracked runner §3.1 item 8; run **B-Sidebar-layout**, **B-Group-band-cancel**, **B-Event-focus-cancel**; capture V1–V3.
- Verification: all §2.2 criteria; all §2.4 carriers via the frozen runner path; normal + static builds; harness auto; `git diff --check` on task paths.
- Exit gate: `phase-1-exit` with implementation commit SHA + receipts.

### Phase 2 — Implementation Review And Closeout

- Entry gate: `phase-1-exit`.
- Work: implementation-review packet + independent implementation review; migrate plan to `completed/` on accept; update OPT statuses to `completed` with lifecycle links; reconcile indexes/state.
- Verification: matching-revision `accept` (medium/high); operating-modes + harness green.
- Exit gate: `closeout-complete` / next gate `closed`.

## 5. Evidence And Commit Plan

- Baseline commands: `npm run test:trade-records`; `python scripts/check-operating-modes.py --root .`; `python scripts/check-project-harness.py --root . --profile auto`; `git diff --check`.
- Focused checks: §2.4 N-* / B-* carriers; Review/Static builds (`npm run build`, static build as used by prior plans).
- Full checks: harness auto; optional local acceptance only if browser environment available.
- Expected state/handoff updates: each lifecycle transition updates `PROGRESS.md` / `HANDOFF.md` operating-modes-state blocks and indexes.
- Task-owned commit paths (proposal package): this plan file; `docs/exec-plans/proposed/index.md`; `docs/exec-plans/reviews/index.md`; `docs/exec-plans/roadmap.md`; OPT record + `docs/optimization/index.md`; `PROGRESS.md`; `HANDOFF.md`.
- No-commit condition: user opt-out, draft failure, or inseparable unrelated dirty paths.

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan/`
- Required verdict: independent design review with `Review type: design`, `Independence declaration: attested`, `Reviewer ID` ≠ plan author ID, and matching-revision **`Verdict: approve`** (confidence medium or high).
- Required user approval for activation: this session’s user instruction chains **approve → migrate to active** after matching-revision approve. Activation is lifecycle-only (Status Active, phase-0 not-started, next gate `phase-0-start`); it does **not** start implementation.
- Implementation start requires a later explicit execute/start instruction after activation.
- Creating or revising this durable plan is committed locally by default; no separate commit-authority metadata is required.

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
