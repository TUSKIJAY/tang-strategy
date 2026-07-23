# Tang Strategy Trade Panel Visual Polish

- Lifecycle schema: `operating-modes-v1`
- Status: Completed
- Plan slug: `2026-07-21-tang-strategy-trade-panel-visual-polish-plan`
- Revision: `v3-review-foldback-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-trade-panel-polish`
- Design reviews: ../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-001.md@revise@v1-proposal-2026-07-21, ../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-002.md@revise@v2-review-foldback-2026-07-21, ../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-003.md@approve@v3-review-foldback-2026-07-21
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: user-instruction:2026-07-21-activate-trade-panel-visual-polish-plan
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: ../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/implementation-review-001.md@accept
- Final disposition: Completed
- Verified implementation commit: 35a007efbd9db2a99967fb007adff2415f243e0b
- Lifecycle reconciliation commit: none
- Owner: Grok
- Created: 2026-07-21
- Optimization source: `docs/optimization/2026-07-21-03-review-trade-panel-visual-polish/2026-07-21-03-review-trade-panel-visual-polish.md`
- Proposal baseline: `codex/project-harness@34179ea6947bb1345c17c42a1e4d3a1482b8d85d`
- Scope authority: local implementation, verification, review, and closeout under `user-instruction:2026-07-21-execute-trade-panel-visual-polish-plan`; push/PR/merge/Pages/provider/broker/tracked-DB/canonical-content/remote remain unauthorized

## 1. Context And Evidence

### 1.1 Proposal provenance

用户在 2026-07-21 开启 optimization record mode，对 Review 左栏点位工具区（Eligibility / trader chips / Download / group cards）验收反馈「还是太丑了」，并迭代 HTML mock。Mock 方向获认可后，用户明确要求 **生成 prop plan**。

| 优化记录 | OPT ID | 摩擦点 |
| --- | --- | --- |
| [`2026-07-21-03-review-trade-panel-visual-polish`](../../optimization/2026-07-21-03-review-trade-panel-visual-polish/2026-07-21-03-review-trade-panel-visual-polish.md) | OPT-001 | 点位工具仍是套在侧栏里的表单模块；全宽 `Download JSON + 3 CSV`；卡片信息层级不清。字号密度计划已完成，但未解决 chrome / IA |

相关已完成计划（边界保留）：

- Date nav + B chip + direction colors: completed `2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan`
- Type/density only under `.dr-sidebar`: completed `2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan`

本计划是 **视觉 / 布局 polish**，不改 eligibility enum、B-chip 选择权威、export 文件内容、方向色 token 或数据契约。

### 1.2 Review foldback closure map

#### review-001 closure (v1 → v2)

Independent `review-001` returned `revise/high` against frozen revision `v1-proposal-2026-07-21`. Revision `v2-review-foldback-2026-07-21` folded every product finding:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | Custom Eligibility segments can pass screenshots while regressing single-select keyboard/state semantics; mock uses plain buttons | §1.4 + §2.2 freeze accessible single-selection: native radio inputs in a labelled fieldset (preferred) **or** a complete `radiogroup`/`radio` with exactly one selected and standard arrow-key focus/selection |
| P2 | Drawer language left open to Phase 0; tests optional; QQQ fixture never enters `>=7` path | §1.4 freezes English drawer chrome **Edit / Select all / Clear** plus search/empty-state wording; `TRADER_CHIP_INLINE_MAX = 6` preserved |
| P2 | Unscoped long-Download ban fails against docs/mock; no four-file UI receipt | §2.2 scopes the negative assertion to **production** frontend control/consumer sources; docs/OPT/mock/plan exempt; four-file UI receipt required |

#### review-002 closure (v2 → v3)

Independent `review-002` returned `revise/high` against frozen revision `v2-review-foldback-2026-07-21`. Product closures from v2 are retained. The sole remaining finding is the **verification carrier**:

| Severity | Finding (summary) | V3 closure |
| --- | --- | --- |
| P1 | V2 assigned real Eligibility and synthetic `>=7` drawer **interactions** to plain Node `test:trade-records` (no JSX/DOM/React renderer) while also allowing “equally strong browser receipts,” so the exit gate was either infeasible or satisfiable by weak source-regex evidence | §2.4 freezes **one executable carrier matrix** with no test-or-browser fallback. **N-\*** carriers run under existing Node `npm run test:trade-records` (pure functions + source text only). **B-\*** carriers are **mandatory** deterministic Playwright/browser receipts using named fixture injection (route-intercepted in-memory payload). Criteria 2/4/8 and Phase 0 verification name the **same** carriers. This plan does **not** add jsdom/Testing Library or expand frontend product dependencies for a component harness |

`review-001` and `review-002` are append-only prior-revision evidence and **cannot approve v3**. Matching-revision `review-003` now approves exact revision `v3-review-foldback-2026-07-21`; the current next gate is `activation-recording`.

### 1.3 Visual evidence

| 证据 | 位置 | 作用 |
| --- | --- | --- |
| Live Review trade tools + cards | `docs/optimization/2026-07-21-03-review-trade-panel-visual-polish/screenshots/2026-07-21-review-trade-panel-current.png` · SHA-256 `ce00fef17e4fd58a73b5c8de7415041bdc95aa651c6865e78f41347635db3765` | 当前 form-card 摩擦 |
| Locked design mock | `docs/optimization/2026-07-21-03-review-trade-panel-visual-polish/mockups/trade-panel-v2.html` · SHA-256 `ddea8609c48c9f19c1d27f1f0d51ae5c1b5fa80ab3a0bcc5e67408c943d6e9bc` | 目标布局与 chrome 语汇（visual only; a11y contract is §1.4/§2.2, not the mock’s plain buttons） |

### 1.4 User scope locks (from optimization foldback + review-001; retained in v3)

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
| Verification carriers (review-002 P1) | Exactly the matrix in §2.4 — Node for pure/source; Playwright for real interactions; **no** alternative fallbacks |

Rejected: Chinese label trials（显示/已报/计算；可见点位/手填收益/系统核算）for product chrome. Rejected for drawer actions: keep live Chinese `编辑/全选/清空` as the ship target (tests that pin those strings must move to the frozen English set). Rejected: assigning click/focus/type interactions to plain Node `test:trade-records`, or “test **or** browser” ambiguity.

### 1.5 Current repository facts

- Shared components: `TraderFilters.jsx`, `TradeExportControls.jsx`, `TraderTradeList.jsx`.
- Consumers:
  - `ReviewPage.jsx` / `StaticReviewsApp.jsx`: filters + export + list inside `.dr-sidebar`
  - `AdminTradersPage.jsx`: export currently in **page header**; filters + list below context (not `.dr-sidebar`)
- `TraderFilters`: native `<select>` for Eligibility (`Display` / `Reported stats` / `Calculated stats`); B chips or summary+`编辑` drawer with Chinese search/actions.
- `TradeExportControls`: button text `Download JSON + 3 CSV`.
- `TraderTradeList`: summary grid + `trade-review-badge` + separate `Show legs/events` toggle; density already frozen under `.dr-sidebar` only.
- `npm run test:trade-records` is plain Node `--test` over `tradeRecords.test.js`, `reviewWorkspace.test.js`, and `traderRegistry.test.js`. Current tests read React sources as text and exercise pure helpers; there is **no** JSX transform, DOM, React renderer, jsdom, or Testing Library in this suite.
- `playwright` is already a frontend dependency and is the interaction carrier for this plan (no new product test stack).
- Contract tests pin some `.trade-filter-panel` / `.dr-sidebar` CSS shapes and Chinese drawer copy (`编辑`/`全选`/`清空`) plus `TRADER_CHIP_INLINE_MAX = 6`.
- Live QQQ `2026-07-17` has too few traders to enter the `>=7` drawer path; visual matrix cannot alone prove drawer behavior. Synthetic scale uses **browser fixture injection only** and must not write canonical content or tracked SQLite.

### 1.6 Lane 3 classification

Shared Review/Static/Admin trade chrome, source-contract tests, and multi-surface composition. Classified Coding Mode **Lane 3** (proposed Exec Plan). No backend, API, DB, content, market-data, provider/broker, or Pages workflow changes. No new frontend unit-test harness dependencies.

## 2. Objective And Success Criteria

### 2.1 Objective

将共享 trade tools + group cards 从「表单模块」收成与终端 context 同平面的工具条布局，并在 **Review、Static、Admin** 上对齐，同时保持英文产品文案与既有 filter/export 数据语义。

### 2.2 Success criteria

1. **Layout — no form card nest:** `.trade-filter-panel` no longer reads as a heavy bordered form slab against the sidebar; tools share the terminal surface language (padding/gaps/borders match mock intent). Exact CSS tokens frozen in Phase 0 baseline notes may refine mock numbers but must not reintroduce a double-box form look. Proven by V1–V3 screenshots (§2.3).
2. **Eligibility (visual + a11y + behavior):** native select replaced by a three-segment control with visible labels **Display**, **Reported**, **Calculated** bound to enum values `display` / `reported` / `calculated`. Row label remains **Eligibility**. Selection is **single-select only** under the §1.4 accessible contract (native fieldset/radio preferred, or complete radiogroup). Selecting a segment updates filters exactly as today’s select.
   - **Source/a11y structure:** carrier **N-Eligibility-source**
   - **Real selection/focus/filter behavior:** carrier **B-Eligibility-interaction** (not Node)
3. **Download (label + production-scoped ban + four-file receipt):** control label is **Download** (icon allowed). **Production frontend sources** under §3.1 items 1–7 **must not** contain the substring `Download JSON + 3 CSV` (including `title` / `aria-label`). Historical docs, OPT record, mock, and this plan **remain exempt**. Click still builds and downloads the same JSON + 3 CSV set.
   - **Production-source ban + short label:** carrier **N-Download-source**
   - **Four-file click receipt + three-surface composition:** carrier **B-Download-four-file**
4. **Traders:** existing B-chip multi-select preserved; ≤6 inline; ≥7 summary + **Edit** drawer with **Search traders** / **Select all** / **Clear** / **No matching traders** (frozen English, §1.4). `TRADER_CHIP_INLINE_MAX = 6` unchanged.
   - **English string pins + threshold constant + source shape:** carrier **N-Drawer-source**
   - **Real synthetic `>=7` open/close/search/select-all/clear:** carrier **B-Drawer-scale** (not Node). V1–V3 screenshots alone are insufficient for the drawer path.
5. **Cards:** group card hierarchy matches mock intent:
   - left direction rail + triangle glyph
   - title row: trader name (default text color) + CALL/PUT pill (direction color only)
   - meta line: underlying · date · result
   - status as compact indicator (dot or equivalent), not a bulky grey badge block
   - **Show legs/events** / **Hide legs/events** English drilldown, collapsible
   Proven by V1–V3 plus any existing Node card source pins retained/updated under **N-Card-source**.
6. **Surfaces:** Review, Static, and Admin all render the polished shared tools + cards. Admin header must not retain a separate full-width long Download CTA; Admin uses the same short Download control in the shared tools strip. Composition proven by V1–V3 + **B-Download-four-file** / shared strip presence checks in browser receipts.
7. **Contracts unchanged:** eligibility filtering, trader set membership, export payload contents, direction color tokens, progressive DateRail consumers, and density px table under `.dr-sidebar` from the completed density plan remain valid unless a listed CSS rule is intentionally superseded for chrome structure (document any supersession in the phase evidence). Pure filter/export behavior remains under existing Node pure-function tests (**N-Pure-filter-export**).
8. **Tests/builds/receipts (same named carriers as §2.4):** `npm run test:trade-records` green for **all N-\*** carriers; **all B-\*** Playwright receipts green and recorded under `output/` (untracked); normal + static Vite builds green; harness auto green. **No** “equally strong alternative” substitutions.
9. **Screenshots:** §2.3 matrix captured under `output/` (untracked). Screenshots prove visual chrome only; they do **not** replace **B-\*** interaction carriers.

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review trade tools + cards | desktop `1672x941` | QQQ `2026-07-17` | Eligibility segments; short Download; 沃德哥 chip; ≥1 PUT + ≥1 CALL card hierarchy; one expanded Show legs/events |
| V2 | Static Review trade tools + cards | desktop `1672x941` | QQQ `2026-07-17` | Same shared chrome language as V1 (static shell) |
| V3 | Admin traders workspace tools + cards | desktop `1672x941` | QQQ `2026-07-17` | Shared tools strip (no header long Download); cards aligned; filters functional |

Compare against OPT live screenshot and mock `trade-panel-v2.html`. Drawer `>=7` coverage is **B-Drawer-scale only** (synthetic injected fixture), not required in V1–V3.

### 2.4 Frozen verification carrier matrix (review-002)

| Carrier ID | Tool | What it may prove | What it must not claim |
| --- | --- | --- | --- |
| **N-Pure-filter-export** | Node `npm run test:trade-records` | Pure helpers: eligibility filtering, trader summary, export payload builders, thresholds (`TRADER_CHIP_INLINE_MAX = 6`) | Click, focus, keyboard, drawer open, typed search, download dialogs |
| **N-Eligibility-source** | Node source inspection in `tradeRecords.test.js` / related files | Accessible markup contracts in source (fieldset/radio **or** radiogroup/radio patterns; labels Display/Reported/Calculated; enum value wiring) | That a user can actually change selection or that filtered DOM updates |
| **N-Download-source** | Node source inspection | Short label **Download**; production §3.1 items 1–7 contain no `Download JSON + 3 CSV` (title/aria-label included) | That clicking emits four files |
| **N-Drawer-source** | Node source inspection | Frozen English strings **Edit / Select all / Clear / Search traders / Name or ID / No matching traders**; threshold constants; drawer structure markers | That drawer opens, search filters, or select-all/clear run |
| **N-Card-source** | Node source inspection (existing/updated) | Card hierarchy class/source contracts (rail, direction pill, status indicator, Show/Hide legs copy) | Visual polish judgment (use V1–V3) |
| **B-Eligibility-interaction** | Playwright against running local UI | Select each of `display` / `reported` / `calculated`; assert selected/checked state; assert filtered group set changes accordingly on the shared control path | Source-text-only proofs |
| **B-Drawer-scale** | Playwright with **named fixture injection** | Synthetic **≥7** day-available traders via route-intercepted **in-memory** payload (or equivalent non-canonical injection). Prove summary row, open/close **Edit**, search hit/miss, **Select all**, **Clear**. Must **not** write `content/` or tracked SQLite | Live QQQ day alone; Node string match alone |
| **B-Download-four-file** | Playwright | Click short **Download**; prove JSON + 3 CSV filenames from filtered selection; Review + Static + Admin share composition with **no** Admin-header second CTA | Repo-wide docs/mock scans |
| **V1–V3** | Screenshots | Visual chrome alignment | Interaction semantics |

**Fixture-injection method (named):** `route-intercepted-in-memory-payload` — Playwright `page.route` (or equivalent) fulfills trader/day availability responses with a deterministic synthetic ≥7-trader payload for **B-Drawer-scale** only. Injection is ephemeral, session-local, and never commits seed/content/DB changes.

**Hard rule:** Every acceptance bullet that requires click, focus, keyboard, drawer open, typed search, select-all/clear, or download emission names a **B-\*** carrier. Every pure-function or production-source string/threshold pin names an **N-\*** carrier. Phase 0 verification lists both sets; exit requires both sets.

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
8. `frontend/src/features/review/reviewWorkspace.test.js` — update CSS/source contracts that pin old filter-panel/export shapes (**N-\*** only).
9. `frontend/src/features/review/tradeRecords.test.js` — **mandatory N-\*** only: short **Download** production-source contracts; Eligibility **source** a11y pattern pins; English drawer string pins replacing `编辑`/`全选`/`清空`; `TRADER_CHIP_INLINE_MAX = 6` and related pure/summary fixtures. **Must not** claim to click segments or drive the drawer.

**Browser evidence (Phase 0 verification outputs; untracked under `output/`, not product source):**

10. Playwright receipt notes/scripts or session artifacts sufficient to re-run **B-Eligibility-interaction**, **B-Drawer-scale**, and **B-Download-four-file** deterministically. Scripts, if committed later under separate authority, must remain frontend-only and must not expand into backend/DB/content. Default for this plan: record receipts under `output/playwright/trade-panel-polish-<timestamp>/` without requiring a new CI job.

**Lifecycle / evidence (later phases, separate authority):**

11. Optimization record + `docs/optimization/index.md` status/lifecycle links.
12. `PROGRESS.md` / `HANDOFF.md` state blocks.
13. Plan file location + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + roadmap as lifecycle transitions require.
14. Implementation review packet + screenshots under `output/` (screenshots untracked).

**Out of manifest / must not change:**

- Backend, API, tracked DB, seed, content, Pages workflow, daily runbook, provider/broker paths.
- Eligibility enum values and filter semantics in `tradeRecords.js` (except pure UI wiring).
- Export file formats/contents from `buildTradeRecordDownloads`.
- B-chip set-membership authority; `TRADER_CHIP_INLINE_MAX` threshold behavior.
- Direction color tokens `--direction-call` / `--direction-put`.
- Progressive DateRail / Data page work (already completed).
- Adding jsdom, Testing Library, or a second unit-test framework to satisfy interactions (use Playwright **B-\*** carriers instead).
- Unrelated dirty paths (existing frontend dirty files outside this manifest, `output/`, `.playwright-cli/`, etc.) — preserve; do not stage into plan commits without authority.

**Production-source scope for the long-Download ban (review-001 P2):**

Negative substring scans apply only to the production paths in items 1–7 above (and any new production helper those files import under `frontend/src/`). Exempt: `docs/**`, mockups, optimization records, exec plans, reviews, and other non-runtime evidence.

### 3.2 Behavioral invariants

- Empty trader selection continues to hide groups honestly.
- Voided/superseded eligibility flags and review_status display remain factual.
- Synthetic ≥7 trader payloads exist only inside **B-Drawer-scale** injection; they never mutate canonical content or tracked SQLite.
- No `git push`, PR, Pages, remote, provider/broker, or tracked DB mutation authorized by this plan text.
- Activation and implementation require separate explicit user instructions after matching-revision design `approve`.

## 4. Phases

### Phase 0 — Baseline, Implementation, And Verification

- Entry gate: matching-revision design-review `approve` on `v3-review-foldback-2026-07-21` **and** explicit user activation **and** separate implementation-start (or a single full-execution instruction that explicitly covers implementation through closeout).
- Work:

  **Baseline:**

  1. Confirm harness auto green on entry.
  2. Freeze live hashes for the nine implementation paths in §3.1 items 1–9 if needed for evidence.
  3. Record frozen English drawer + Eligibility a11y choice (fieldset/native radio preferred) already decided in §1.4 — do **not** reopen language in Phase 0.
  4. Record the §2.4 carrier matrix as the only exit-gate verification contract (no fallback wording).

  **Implementation:**

  5. Restructure `TraderFilters` into terminal tools strip: section title optional, accessible Eligibility segments (§1.4), Traders chips/drawer with frozen English chrome.
  6. Shorten `TradeExportControls` to **Download**; place control in tools head on all three surfaces; strip long copy from production sources only.
  7. Restyle/restructure `TraderTradeList` cards per §2.2.
  8. Update `styles.css` shared rules; keep density family; align Admin via shared classes.
  9. Wire Review / Static / Admin page composition; remove Admin header long Download.
  10. Update **N-\*** contract tests in `reviewWorkspace.test.js` and `tradeRecords.test.js` (source/pure only).

- Verification (one round; same named carriers):
  1. **N-\***: `cd frontend && npm run test:trade-records` (must cover N-Pure-filter-export, N-Eligibility-source, N-Download-source, N-Drawer-source, N-Card-source as applicable)
  2. `cd frontend && npm run build`
  3. `cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews`
  4. `python3 scripts/check-project-harness.py --root . --profile auto` (or `python` equivalent on Windows)
  5. Diff limited to §3.1 implementation paths (+ authorized lifecycle files only when separately staging)
  6. Capture §2.3 V1–V3 screenshots under `output/`
  7. **B-Eligibility-interaction** receipt under `output/playwright/trade-panel-polish-*/`
  8. **B-Drawer-scale** receipt using `route-intercepted-in-memory-payload` under the same output dir
  9. **B-Download-four-file** receipt (JSON + 3 CSV filenames; Review/Static/Admin composition; no Admin-header CTA)
- Exit gate: all **N-\*** and **B-\*** carriers green; both builds + harness green; screenshots present; next gate `implementation-review`. Missing any **B-\*** carrier fails the exit gate (source-regex is not a substitute).

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
- Focused checks: §4 Phase 0 verification list — **N-\*** Node suite + **B-\*** Playwright receipts + V1–V3.
- Full checks: same for this frontend-only plan; no backend suite required unless a future revision expands scope.
- Expected state/handoff updates on activation, phase exits, and closeout only (plus this proposal-revision reconciliation).
- Local commits: product implementation `35a007efbd9db2a99967fb007adff2415f243e0b`; deterministic browser acceptance script `680981f`.
- Push/PR/Pages/provider/broker/DB: never authorized by this plan alone.

## 6. Authority Boundary

| Action | Authorized now? |
| --- | --- |
| Independent design review of exact v3 | Completed by `review-003: approve/high` |
| Lifecycle activation recording (Proposed → Active at `phase-0:not-started`) | Yes — consumed by `user-instruction:2026-07-21-activate-trade-panel-visual-polish-plan` |
| Phase 0 start / implementation | Completed under full-execution instruction |
| Git stage/commit | Completed for task-owned local paths |
| Push / PR / merge / Pages | No |
| Provider / broker / tracked DB / content | No |

### 6.1 Activation record

- Instruction: user message authorizing move of the approved prop plan to active (`user-instruction:2026-07-21-activate-trade-panel-visual-polish-plan`)
- Matching-revision design approval: `review-003: approve/high` on exact `v3-review-foldback-2026-07-21`
- Result: plan lives at `docs/exec-plans/active/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md`; state `phase-0:not-started`; next gate `phase-0-start`
- Non-authorization: this activation does not start Phase 0 and does not grant implementation, Git stage/commit/push, data/DB, provider/broker, Pages, hosted, or other remote actions

### 6.2 Execution and closeout record

- Full-execution instruction: `user-instruction:2026-07-21-execute-trade-panel-visual-polish-plan`
- Product implementation: `35a007efbd9db2a99967fb007adff2415f243e0b`
- Reproducible browser acceptance: `680981f`
- Independent implementation review: `implementation-review-001: accept/high`
- Result: all phases closed; plan migrated to `completed/`; next gate `closed`

## 7. References

- Operating modes: [`docs/operating-modes.md`](../../operating-modes.md)
- Optimization batch: [`docs/optimization/2026-07-21-03-review-trade-panel-visual-polish/2026-07-21-03-review-trade-panel-visual-polish.md`](../../optimization/2026-07-21-03-review-trade-panel-visual-polish/2026-07-21-03-review-trade-panel-visual-polish.md)
- Mock: [`docs/optimization/2026-07-21-03-review-trade-panel-visual-polish/mockups/trade-panel-v2.html`](../../optimization/2026-07-21-03-review-trade-panel-visual-polish/mockups/trade-panel-v2.html)
- Design review (v1, append-only): [`docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-001.md`](../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-001.md)
- Design review (v2, append-only): [`docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-002.md`](../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-002.md)
- Design review (v3, approved): [`docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-003.md`](../reviews/2026-07-21-tang-strategy-trade-panel-visual-polish-plan/review-003.md)
- Prior completed density plan: [`docs/exec-plans/completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`](../completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md)
- Prior completed filter fusion: [`docs/exec-plans/completed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`](../completed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md)
