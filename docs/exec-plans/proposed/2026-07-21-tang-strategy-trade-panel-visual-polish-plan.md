# Tang Strategy Trade Panel Visual Polish

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-trade-panel-visual-polish-plan`
- Revision: `v2-review-foldback-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-trade-panel-polish`
- Design reviews: docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-001.md@revise@v1-proposal-2026-07-21, docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-002.md@revise@v2-review-foldback-2026-07-21
- Latest design verdict: revise
- Review independence: attested
- Activation evidence: none
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: plan-revision
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Owner: Grok
- Created: 2026-07-21
- Optimization source: `docs/optimization/2026-07-21-review-trade-panel-visual-polish/2026-07-21-review-trade-panel-visual-polish.md`
- Proposal baseline: `codex/project-harness@34179ea6947bb1345c17c42a1e4d3a1482b8d85d`
- Scope authority: review-only; this proposed plan does not authorize implementation, activation, Git stage/commit/push, data/DB, provider/broker, Pages, or remote actions

## 1. Context And Evidence

### 1.1 Proposal provenance

用户在 2026-07-21 开启 optimization record mode，对 Review 左栏点位工具区（Eligibility / trader chips / Download / group cards）验收反馈「还是太丑了」，并迭代 HTML mock。Mock 方向获认可后，用户明确要求 **生成 prop plan**。

| 优化记录 | OPT ID | 摩擦点 |
| --- | --- | --- |
| [`2026-07-21-review-trade-panel-visual-polish`](../../optimization/2026-07-21-review-trade-panel-visual-polish/2026-07-21-review-trade-panel-visual-polish.md) | OPT-001 | 点位工具仍是套在侧栏里的表单模块；全宽 `Download JSON + 3 CSV`；卡片信息层级不清。字号密度计划已完成，但未解决 chrome / IA |

相关已完成计划（边界保留）：

- Date nav + B chip + direction colors: completed `2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan`
- Type/density only under `.dr-sidebar`: completed `2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan`

本计划是 **视觉 / 布局 polish**，不改 eligibility enum、B-chip 选择权威、export 文件内容、方向色 token 或数据契约。

### 1.2 Review foldback closure map

#### review-001 closure (v1 → v2)

Independent `review-001` returned `revise/high` against frozen revision `v1-proposal-2026-07-21`. Revision `v2-review-foldback-2026-07-21` folds every finding into the operative contract:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | Custom Eligibility segments can pass screenshots while regressing single-select keyboard/state semantics; mock uses plain buttons | §1.3 + §2.2 criterion 2 freeze accessible single-selection: native radio inputs in a labelled fieldset (preferred) **or** a complete `radiogroup`/`radio` with exactly one selected and standard arrow-key focus/selection. §2.2 criterion 8 + §4 Phase 0 require a deterministic interaction receipt for `display` / `reported` / `calculated`, `onChange`/filtered results, on shared surfaces |
| P2 | Drawer language left open to Phase 0; `tradeRecords.test.js` optional; QQQ fixture never enters `>=7` path | §1.3 freezes English drawer chrome **Edit / Select all / Clear** plus search/empty-state wording in this revision (not Phase 0). §3.1 makes `tradeRecords.test.js` mandatory. §2.2 criterion 4 + §4 require a deterministic synthetic `>=7` trader case (summary, open/close, search, select-all, clear) while preserving `TRADER_CHIP_INLINE_MAX = 6` |
| P2 | Unscoped “must not contain `Download JSON + 3 CSV`” fails against docs/mock evidence; no four-file UI receipt after relocate | §2.2 criterion 3 scopes the negative assertion to **production** frontend control/consumer sources listed in §3.1; docs/OPT/mock/plan remain exempt. §2.2 criterion 8 + §4 require a focused UI/browser receipt that clicks short **Download**, proves JSON + 3 CSV filenames from the filtered selection, and confirms Review / Static / Admin share the same payload/groups/filters contract with **no** second Admin-header CTA |

`review-001` is append-only v1 evidence and **cannot approve v2**. Next gate is independent design review of exact revision `v2-review-foldback-2026-07-21`.

### 1.3 Visual evidence

| 证据 | 位置 | 作用 |
| --- | --- | --- |
| Live Review trade tools + cards | `docs/optimization/2026-07-21-review-trade-panel-visual-polish/screenshots/2026-07-21-review-trade-panel-current.png` · SHA-256 `ce00fef17e4fd58a73b5c8de7415041bdc95aa651c6865e78f41347635db3765` | 当前 form-card 摩擦 |
| Locked design mock | `docs/optimization/2026-07-21-review-trade-panel-visual-polish/mockups/trade-panel-v2.html` · SHA-256 `ddea8609c48c9f19c1d27f1f0d51ae5c1b5fa80ab3a0bcc5e67408c943d6e9bc` | 目标布局与 chrome 语汇（visual only; a11y contract is §1.3/§2.2, not the mock’s plain buttons） |

### 1.4 User scope locks (from optimization foldback + review-001)

| Decision | Lock |
| --- | --- |
| Visual direction | Mock v2 terminal tool strip + clearer cards **accepted** |
| Product chrome language | **Keep original English** for Eligibility / Display·Reported·Calculated / Download / Show legs/events / Verified — do not Chinese-translate product chrome |
| Eligibility UI | Compact **segmented** control: **Display** / **Reported** / **Calculated** (short form of live options; enum values unchanged) |
| Eligibility a11y (review-001 P1) | **Accessible single-selection only.** Prefer native radio inputs inside a labelled fieldset, styled as segments. Acceptable alternative: complete `role="radiogroup"` with `role="radio"` items, exactly one selected, `aria-checked`/`aria-labelledby` (or equivalent), and standard arrow-key focus/selection. **Forbidden:** plain uncoordinated buttons that only look like segments (as in the locked visual mock). |
| Eligibility label | **Eligibility** |
| Export UI | Corner/short **Download** only — remove full-width `Download JSON + 3 CSV` and any hover/title carrying that long string **in production control/consumer sources** |
| Export payload | Unchanged JSON + 3 CSV files under the hood |
| Trader scale | ≤6 inline B chips; ≥7 summary + Edit drawer (existing contract); `TRADER_CHIP_INLINE_MAX = 6` unchanged |
| Drawer chrome language (review-001 P2) | **Frozen English** on all three surfaces: **Edit**, **Select all**, **Clear**; search label **Search traders**; search placeholder **Name or ID**; empty match **No matching traders**. Do not leave language to Phase 0. |
| Surface scope | **Review + Static + Admin aligned** via shared components |
| Prior locks retained | B chip multi-select; CALL/PUT direction colors only; name text never red; day-available traders only; no ticker/date mirror in filter panel |

Rejected: Chinese label trials（显示/已报/计算；可见点位/手填收益/系统核算）for product chrome. Rejected for drawer actions: keep live Chinese `编辑/全选/清空` as the ship target (tests that pin those strings must move to the frozen English set).

### 1.5 Current repository facts

- Shared components: `TraderFilters.jsx`, `TradeExportControls.jsx`, `TraderTradeList.jsx`.
- Consumers:
  - `ReviewPage.jsx` / `StaticReviewsApp.jsx`: filters + export + list inside `.dr-sidebar`
  - `AdminTradersPage.jsx`: export currently in **page header**; filters + list below context (not `.dr-sidebar`)
- `TraderFilters`: native `<select>` for Eligibility (`Display` / `Reported stats` / `Calculated stats`); B chips or summary+`编辑` drawer with Chinese search/actions.
- `TradeExportControls`: button text `Download JSON + 3 CSV`.
- `TraderTradeList`: summary grid + `trade-review-badge` + separate `Show legs/events` toggle; density already frozen under `.dr-sidebar` only.
- Contract tests in `reviewWorkspace.test.js` pin some `.trade-filter-panel` / `.dr-sidebar` CSS shapes; `tradeRecords.test.js` pins Chinese drawer copy (`编辑`/`全选`/`清空`) and `TRADER_CHIP_INLINE_MAX = 6`. Any chrome restructure **must** update those assertions.
- Live QQQ `2026-07-17` has too few traders to enter the `>=7` drawer path; visual matrix cannot alone prove drawer behavior.

### 1.6 Lane 3 classification

Shared Review/Static/Admin trade chrome, source-contract tests, and multi-surface composition. Classified Coding Mode **Lane 3** (proposed Exec Plan). No backend, API, DB, content, market-data, provider/broker, or Pages workflow changes.

## 2. Objective And Success Criteria

### 2.1 Objective

将共享 trade tools + group cards 从「表单模块」收成与终端 context 同平面的工具条布局，并在 **Review、Static、Admin** 上对齐，同时保持英文产品文案与既有 filter/export 数据语义。

### 2.2 Success criteria

1. **Layout — no form card nest:** `.trade-filter-panel` no longer reads as a heavy bordered form slab against the sidebar; tools share the terminal surface language (padding/gaps/borders match mock intent). Exact CSS tokens frozen in Phase 0 baseline notes may refine mock numbers but must not reintroduce a double-box form look.
2. **Eligibility (visual + a11y + behavior):** native select replaced by a three-segment control with visible labels **Display**, **Reported**, **Calculated** bound to enum values `display` / `reported` / `calculated`. Row label remains **Eligibility**. Selection is **single-select only** under the §1.4 accessible contract (native fieldset/radio preferred, or complete radiogroup). Selecting a segment updates filters exactly as today’s select. A deterministic component or browser receipt must exercise all three values, assert selected state, and prove `onChange`/filtered group results change accordingly on the shared control path used by Review/Static/Admin.
3. **Download (label + production-scoped ban + four-file receipt):** control label is **Download** (icon allowed). **Production frontend sources** under §3.1 items 1–7 **must not** contain the substring `Download JSON + 3 CSV` (including `title` / `aria-label`). Historical docs, OPT record, mock, and this plan **remain exempt**. Click still builds and downloads the same JSON + 3 CSV set. A focused UI/browser receipt must click the short control and prove the four filenames are still emitted from the filtered selection; Review, Static, and Admin must share the same payload/groups/filters contract with **no** second Admin-header Download CTA.
4. **Traders:** existing B-chip multi-select preserved; ≤6 inline; ≥7 summary + **Edit** drawer with **Search traders** / **Select all** / **Clear** / **No matching traders** (frozen English, §1.4). `TRADER_CHIP_INLINE_MAX = 6` unchanged. `tradeRecords.test.js` **must** be updated: replace Chinese drawer pins with the frozen English strings and add a **mandatory** deterministic synthetic case with ≥7 traders covering summary, open/close, search, select-all, and clear. V1–V3 screenshots alone are insufficient for the drawer path.
5. **Cards:** group card hierarchy matches mock intent:
   - left direction rail + triangle glyph
   - title row: trader name (default text color) + CALL/PUT pill (direction color only)
   - meta line: underlying · date · result
   - status as compact indicator (dot or equivalent), not a bulky grey badge block
   - **Show legs/events** / **Hide legs/events** English drilldown, collapsible
6. **Surfaces:** Review, Static, and Admin all render the polished shared tools + cards. Admin header must not retain a separate full-width long Download CTA; Admin uses the same short Download control in the shared tools strip.
7. **Contracts unchanged:** eligibility filtering, trader set membership, export payload contents, direction color tokens, progressive DateRail consumers, and density px table under `.dr-sidebar` from the completed density plan remain valid unless a listed CSS rule is intentionally superseded for chrome structure (document any supersession in the phase evidence).
8. **Tests/builds/receipts:** `npm run test:trade-records` green (including mandatory Eligibility interaction, short Download production-source contracts, English drawer pins, and synthetic `>=7` case); normal + static Vite builds green; harness auto green; Download four-file UI/browser receipt recorded in phase evidence.
9. **Screenshots:** §2.3 matrix captured under `output/` (untracked). Screenshots prove visual chrome only; they do not replace criteria 2–4 behavioral receipts.

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review trade tools + cards | desktop `1672x941` | QQQ `2026-07-17` | Eligibility segments; short Download; 沃德哥 chip; ≥1 PUT + ≥1 CALL card hierarchy; one expanded Show legs/events |
| V2 | Static Review trade tools + cards | desktop `1672x941` | QQQ `2026-07-17` | Same shared chrome language as V1 (static shell) |
| V3 | Admin traders workspace tools + cards | desktop `1672x941` | QQQ `2026-07-17` | Shared tools strip (no header long Download); cards aligned; filters functional |

Compare against OPT live screenshot and mock `trade-panel-v2.html`. Drawer `>=7` coverage is **test-only** (synthetic fixture), not required in V1–V3.

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/TraderFilters.jsx` — accessible Eligibility segment UI; tools head layout; optional export slot composition; trader row structure; frozen English drawer chrome.
2. `frontend/src/features/review/TradeExportControls.jsx` — short **Download** label only; keep download behavior; no long-string title/aria-label.
3. `frontend/src/features/review/TraderTradeList.jsx` — card markup hierarchy (rail, title, meta, status, drilldown).
4. `frontend/src/styles.css` — shared trade filter/export/card chrome styles; keep prior direction tokens; reconcile with existing `.dr-sidebar` density rules so Review/Static stay dense and Admin also uses the polished structure (Admin may use the same shared classes; do not invent a third skin).
5. `frontend/src/pages/ReviewPage.jsx` — compose export into tools strip if needed (remove sibling full-width export placement).
6. `frontend/src/pages/StaticReviewsApp.jsx` — same composition as Review for shared strip.
7. `frontend/src/pages/AdminTradersPage.jsx` — remove header long Download placement; use shared strip composition.
8. `frontend/src/features/review/reviewWorkspace.test.js` — update CSS/source contracts that pin old filter-panel/export shapes.
9. `frontend/src/features/review/tradeRecords.test.js` — **mandatory:** short **Download** production-source contracts; accessible Eligibility source/behavior contracts; English drawer string pins replacing `编辑`/`全选`/`清空`; synthetic `>=7` trader interaction coverage; keep `TRADER_CHIP_INLINE_MAX = 6`.

**Lifecycle / evidence (later phases, separate authority):**

10. Optimization record + `docs/optimization/index.md` status/lifecycle links.
11. `PROGRESS.md` / `HANDOFF.md` state blocks.
12. Plan file location + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + roadmap as lifecycle transitions require.
13. Implementation review packet + screenshots under `output/` (screenshots untracked).

**Out of manifest / must not change:**

- Backend, API, tracked DB, seed, content, Pages workflow, daily runbook, provider/broker paths.
- Eligibility enum values and filter semantics in `tradeRecords.js` (except pure UI wiring).
- Export file formats/contents from `buildTradeRecordDownloads`.
- B-chip set-membership authority; `TRADER_CHIP_INLINE_MAX` threshold behavior.
- Direction color tokens `--direction-call` / `--direction-put`.
- Progressive DateRail / Data page work (already completed).
- Unrelated dirty paths (existing frontend dirty files outside this manifest, `output/`, etc.) — preserve; do not stage into plan commits without authority.

**Production-source scope for the long-Download ban (review-001 P2):**

Negative substring scans apply only to the production paths in items 1–7 above (and any new production helper those files import under `frontend/src/`). Exempt: `docs/**`, mockups, optimization records, exec plans, reviews, and other non-runtime evidence.

### 3.2 Behavioral invariants

- Empty trader selection continues to hide groups honestly.
- Voided/superseded eligibility flags and review_status display remain factual.
- No `git push`, PR, Pages, remote, provider/broker, or tracked DB mutation authorized by this plan text.
- Activation and implementation require separate explicit user instructions after matching-revision design `approve`.

## 4. Phases

### Phase 0 — Baseline, Implementation, And Verification

- Entry gate: matching-revision design-review `approve` on `v2-review-foldback-2026-07-21` **and** explicit user activation **and** separate implementation-start (or a single full-execution instruction that explicitly covers implementation through closeout).
- Work:

  **Baseline:**

  1. Confirm harness auto green on entry.
  2. Freeze live hashes for the nine implementation paths in §3.1 if needed for evidence.
  3. Record frozen English drawer + Eligibility a11y choice (fieldset/native radio preferred) already decided in §1.4 — do **not** reopen language in Phase 0.

  **Implementation:**

  4. Restructure `TraderFilters` into terminal tools strip: section title optional, accessible Eligibility segments (§1.4), Traders chips/drawer with frozen English chrome.
  5. Shorten `TradeExportControls` to **Download**; place control in tools head on all three surfaces; strip long copy from production sources only.
  6. Restyle/restructure `TraderTradeList` cards per §2.2.
  7. Update `styles.css` shared rules; keep density family; align Admin via shared classes.
  8. Wire Review / Static / Admin page composition; remove Admin header long Download.
  9. Update contract tests in **both** `reviewWorkspace.test.js` and `tradeRecords.test.js` (mandatory), including synthetic `>=7` and Eligibility interaction coverage.

- Verification (one round):
  1. `cd frontend && npm run test:trade-records`
  2. `cd frontend && npm run build`
  3. `cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews`
  4. `python3 scripts/check-project-harness.py --root . --profile auto` (or `python` equivalent on Windows)
  5. Diff limited to §3.1 implementation paths (+ authorized lifecycle files only when separately staging)
  6. Capture §2.3 V1–V3 screenshots under `output/`
  7. Record Download four-file UI/browser receipt (JSON + 3 CSV filenames from filtered selection; Review/Static/Admin composition; no Admin-header CTA)
  8. Confirm Eligibility interaction receipt and synthetic `>=7` case are green inside `test:trade-records` (or equally strong browser receipts linked from phase evidence)
- Exit gate: tests + both builds + harness green; screenshots present; behavioral receipts for Eligibility, Download, and `>=7` drawer present; next gate `implementation-review`.

### Phase 1 — Independent Implementation Review

- Entry gate: Phase 0 complete; packet frozen.
- Work: write `implementation-review-packet-001.md`; obtain independent `implementation-review-001` with `accept` / `revise` / `reject`.
- If `revise`, remediate under separate remediation work unit; do not migrate to Completed.
- Exit gate: `Implementation review` metadata records accept; next gate `completed-migration`.

### Phase 2 — Closeout (Completed Migration)

- Entry gate: Phase 1 `accept` **and** closeout authority (full-execution grant covering closeout satisfies this; bare activation or bare implementation-start alone does not).
- Work: migrate plan to `completed/`; reconcile indexes/roadmap/optimization/state blocks; link verified implementation commit.
- Exit gate: lifecycle `Completed`; next gate `closed`.

## 5. Evidence And Commit Plan

- Baseline commands: harness auto; frontend trade-records tests; optional read-only screenshot of current UI.
- Focused checks: §4 Phase 0 verification list (including production-scoped Download ban, Eligibility a11y/behavior, synthetic `>=7`, four-file receipt).
- Full checks: same for this frontend-only plan; no backend suite required unless a future revision expands scope.
- Expected state/handoff updates on activation, phase exits, and closeout only (plus this proposal-revision reconciliation).
- Local commits: only under separate durable-checkpoint / user commit authority — this proposal grants none.
- Push/PR/Pages/provider/broker/DB: never authorized by this plan alone.

## 6. Authority Boundary

| Action | Authorized by this proposal? |
| --- | --- |
| Independent design review of exact v2 | Yes (next gate) |
| Activation | No — needs explicit user instruction after matching-revision `approve` |
| Implementation | No — needs implementation-start (or full-execution) after activation |
| Git stage/commit | No |
| Push / PR / merge / Pages | No |
| Provider / broker / tracked DB / content | No |

## 7. References

- Operating modes: [`docs/operating-modes.md`](../../operating-modes.md)
- Optimization batch: [`docs/optimization/2026-07-21-review-trade-panel-visual-polish/2026-07-21-review-trade-panel-visual-polish.md`](../../optimization/2026-07-21-review-trade-panel-visual-polish/2026-07-21-review-trade-panel-visual-polish.md)
- Mock: [`docs/optimization/2026-07-21-review-trade-panel-visual-polish/mockups/trade-panel-v2.html`](../../optimization/2026-07-21-review-trade-panel-visual-polish/mockups/trade-panel-v2.html)
- Design review (v1, append-only): [`docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-001.md`](../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-001.md)
- Prior completed density plan: [`docs/exec-plans/completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`](../completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md)
- Prior completed filter fusion: [`docs/exec-plans/completed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`](../completed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md)
