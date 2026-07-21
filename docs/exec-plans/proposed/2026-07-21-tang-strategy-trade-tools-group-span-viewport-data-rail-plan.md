# Tang Strategy Trade Tools, Group Span, Viewport, And Data Rail

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan`
- Revision: `v1-proposal-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-trade-tools-group-span-viewport-data-rail`
- Design reviews: ../reviews/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan/review-001.md@revise@v1-proposal-2026-07-21
- Latest design verdict: revise
- Review independence: attested
- Activation evidence: none
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: `plan-revision`
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Owner: Grok
- Created: 2026-07-21
- Optimization source: `docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md` session OPT-003…006
- Proposal baseline: `codex/project-harness@5f7a4cce581f1a475d5dbadd2cb8cbac33b9bfb3`
- Scope authority: review-only; this proposed plan does not authorize implementation, activation, push, or remote action
- Local commit: task-scoped default; does not authorize activation, implementation, push, or remote action

## 1. Context And Evidence

### 1.1 Proposal provenance

用户点名 session-consolidated optimization 文档
`docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md`
并要求 **转换成 prop plan**。

| OPT | Title | 本计划 | 备注 |
| --- | --- | --- | --- |
| OPT-001 | Trade cards: points only | **Out of scope** | Already completed via `2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan` |
| OPT-002 | K-line markers BUY/SELL + nickname | **Out of scope** | Same completed plan |
| **OPT-003** | Trade tools: remove Eligibility segment | **In scope** | 取消 Display / Reported / Calculated 整行 |
| **OPT-004** | K-line 5m switch first-paint viewport glitch | **In scope** | 点 5m 先坏图，滚轮后才正常 |
| **OPT-005** | Group focus span + legs/events timeline UI | **In scope** | 用户已认可方向（span fit + compact timeline） |
| **OPT-006** | Data Market days progressive rail stretched | **In scope** | 宽面板里 QQQ/SPY、最近/按月被 `flex:1` 拉满 |

同一 session 的 OPT-001/002 保持 completed 边界；本计划只承接 **OPT-003…006**，避免把已完成切片重新打开。

相关已完成边界（不得回退）：

- Trade panel visual polish — Eligibility **segments remain accessible** in that plan; this plan **removes** the Review tools Eligibility row as a deliberate product subtraction
- Trade points + marker labels — card points-only, marker `display_name BUY|SELL`, `vordin → vordinkkk`
- Data progressive nav + card density — progressive IA on Data; density under `.dr-sidebar`
- Direction colors CALL/PUT tokens — fusion plan

### 1.2 Visual evidence

| 证据 | 路径 | SHA-256 | 作用 |
| --- | --- | --- | --- |
| Eligibility row to remove | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-tools-eligibility-remove.png` | `d0a6beba6c6069fc9a39a62623c73a4a9fc6273eca75f359483d5b8fe80ee11a` | OPT-003 现状 |
| 5m switch broken first paint | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-kline-5m-switch-initial-viewport.png` | `9691ae10b41503db49ceaaf6db64880c1d934646662baf62e81f0309ad8efe08` | OPT-004 现状 |
| Group select zooms first event only | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-group-select-first-event-only.png` | `1256380599cb21a0236d59f071ac6b7759955501be8a3c1cd1dca0ae0159f7d0` | OPT-005 chart |
| Legs/events dense dump | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-legs-events-current-ui.png` | `888970a008cc039edd12a3ddf662d5ed44c9be46384a89733c4b3daa27d1b5e6` | OPT-005 list |
| Data Market days stretched | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-data-market-days-stretched-controls.png` | `39888c6db1ef1e211b21e6bf63de950ce40c597538f7ad72ae423c6aab0da0f8` | OPT-006 现状 |
| Session mock (all UI items) | `docs/optimization/2026-07-21-review-trade-and-kline-session/mockups/review-trade-and-kline-session.html` | `f2cbec2cf0ae1ee2f292583c40c693adb766a911a4e5f872d9250828d680de6a` | OPT-003…006 目标方向 |

### 1.3 Current repository facts

**OPT-003 — Eligibility on trade tools:**

- Live: `frontend/src/features/review/TraderFilters.jsx` renders `fieldset.trade-eligibility-fieldset` with Display / Reported / Calculated radios.
- Default filter: `initialTradeRecordFilters` → `eligibility: 'display'` (`tradeRecords.js`).
- Pure filter helpers still branch on `filters.eligibility` / `display_only` for export selection.
- Admin group editor (`TraderPointEditor.jsx`) has a separate eligibility fieldset for group flags — **not** the tools-row segment.
- Polish-plan tests pin Eligibility radiogroup source patterns and Playwright selection behavior.

**OPT-004 — 5m first paint:**

- Engine: `frontend/src/kline/kline-engine.js` `setTimeframe(timeframe)` maps previous visible start by time, then sets `viewportManager.viewStart` and `scheduleRender()`.
- Viewport counts: `ViewportManager` uses timeframe-specific base/min/max (5m target slot width 18, min 18, max 72; 1m different).
- Symptom evidence: after clicking 5m, candles crowd left with empty right; wheel zoom path recalculates and repairs the window.
- Investigation surface only at proposal time: `setTimeframe` + `getResolvedViewCount` / `zoomScale` / first `render` after TF switch. **No bar payload / assemble / seed change.**

**OPT-005 — Group select + legs UI:**

- `ReviewPage.jsx` / `StaticReviewsApp.jsx` `selectTradeGroup(group)`:
  - Finds **first** annotation whose `trade_group_ids` includes the group id.
  - `setHighlightRanges` with `startIndex === endIndex` (single bar).
  - `fitRange` around that single index with small radius (~10–12 bars).
- Multi-event groups (open + partials + close) therefore lose group lifecycle context on chart.
- `TraderTradeList.jsx` expanded path dumps raw schema actions (`buy_open` / `sell_partial`) and qty@premium; scannability is poor.
- Pure `groupEventTimeRange(group)` already yields chronological min/max HH:MM across complete events (card meta). Event **count** is available as `knownCount` but collapsed meta does not yet show `· N pts`.
- Annotations from `buildTradeRecordAnnotations` still carry per-event bar indices — span can be derived without schema change.

**OPT-006 — Data progressive rail stretch:**

- `DashboardPage.jsx` mounts shared `ReviewContextPanel` inside wide `.page .panel`.
- Global CSS: `.ticker-tabs button { flex: 1 }` and `.date-rail-mode button { flex: 1 }` — tuned for narrow `.dr-sidebar` (~300px).
- On the wide Data card, ticker and mode segments stretch into full-width slabs; day chips stay small → broken hierarchy.
- Progressive IA (ticker → 最近/按月 → month nav → day chips) and open-Review-on-date behavior must remain.

### 1.4 User scope locks (v1)

| Decision | Lock |
| --- | --- |
| OPT-003 UI | **Remove** the Trade tools Eligibility row (label + Display/Reported/Calculated) from shared `TraderFilters` so it is **not shown** on Review / Static / Admin tools strip |
| OPT-003 filter default | Hard-default list/export filtering to **display-eligible** semantics (`eligibility: 'display'` / equivalent). Do not leave a hidden mid-session segment state that users can no longer change from this chrome |
| OPT-003 schema | Group eligibility **flags** and Admin editor eligibility controls **remain**; this is UI hide + default, not schema deletion |
| OPT-003 Download / Traders | Keep Download and Traders chip area unless a later OPT says otherwise |
| OPT-004 outcome | First `render` after `setTimeframe('5m')` (ideally any TF switch) shows a correct full-window viewport **without** requiring wheel interaction |
| OPT-004 data | No bars/assemble/seed/DB/publish changes |
| OPT-005 group select | Fit **whole event span**: min(event bar)…max(event bar) + modest padding; one zoom frames the trade lifecycle |
| OPT-005 highlight | Soft highlight **band** across the span (not only a single-marker flash) |
| OPT-005 collapsed meta | Time span + event count, e.g. `09:42 → 10:01 · 7 pts` (no $/%; aligns with completed points-only) |
| OPT-005 expanded UI | Compact timeline rows: `TIME \| ACTION \| QTY @ PX`; short actions **BUY** / **SELL** / **PART**; **no fees** |
| OPT-005 secondary nav | Optional: click a timeline row → center/highlight that event bar **without** expanding the whole day; primary group select stays span-fit |
| OPT-005 anti-pattern | Do **not** auto-fit each partial independently on group click |
| OPT-006 layout | Market days on Data feel like a **compact control strip**; ticker + mode content-sized or max-width; prefer Data-scoped surface (e.g. `.page .panel .review-context-panel`) over breaking Review sidebar stretch |
| OPT-006 IA | Progressive browse state machine, ticker isolation, open-Review-on-date **unchanged** |
| Surfaces | OPT-003/005 shared list/tools: Review + Static + Admin where the same components are used. OPT-004 engine: interactive Review (and Static if same engine). OPT-006: Data (`DashboardPage`) primary; Review sidebar density must not regress |

Rejected for this plan: reopening OPT-001/002 product locks; schema version bumps; day-file rewrites; Pages/publisher; provider/broker; deleting eligibility columns from export JSON/CSV unless they already key off display_only defaults; redesigning Admin editor eligibility forms beyond shared tools strip.

### 1.5 Lane 3 classification

Cross-surface frontend work: shared trade tools/list, K-line engine viewport, Review/Static group-focus behavior, and Data progressive rail density. Classified Coding Mode **Lane 3** (proposed Exec Plan) for multi-module UX contracts and independent design review. No market-data fetch, provider/broker, Pages publication, tracked DB mutation, or content day-file rewrites.

## 2. Objective And Success Criteria

### 2.1 Objective

把 session 剩余摩擦一次收口：

1. Trade tools **不再展示** Eligibility 分段，列表默认按 display-eligible 过滤；
2. K 线 **任意 TF 切换（至少 1m→5m）首帧视口正确**，无需滚轮修复；
3. 点击交易组时图表 **框住整段事件跨度**，展开 legs 变成可扫的点位时间线，并可点单笔；
4. Data 页 Market days progressive rail 在宽面板中保持 **紧凑工具条比例**，不再被 `flex:1` 拉成横条。

### 2.2 Success criteria

1. **OPT-003 — Eligibility chrome gone:** Production sources for shared tools strip (`TraderFilters.jsx` and consumers) no longer render Eligibility / Display / Reported / Calculated segment chrome. Carrier **N-Eligibility-removed-source**.
2. **OPT-003 — Default filter:** Runtime filters hard-default to display-eligible behavior. Groups that are not display-eligible are filtered out of the Review tools list path the same way today’s `eligibility: 'display'` path works. Export selection continues to use display-only semantics unless a separate admin path explicitly differs (document if Admin list still shares the component). Carrier **N-Eligibility-default** (pure filter fixtures).
3. **OPT-003 — Schema/editor intact:** Admin `TraderPointEditor` eligibility flags remain editable; group schema fields are not deleted.
4. **OPT-004 — First-paint viewport:** After switching 1m→5m (and 5m→1m) on QQQ or SPY `2026-07-17` (or equivalent available day), the first painted frame uses a sane window width (no permanent left-crowded / right-empty glitch that only wheel fixes). Prefer pure viewport unit proof if extractable; otherwise deterministic browser receipt **B-TF-first-paint**. Carrier matrix freezes one executable path (no “test or screenshot” ambiguity).
5. **OPT-005 — Span fit:** `selectTradeGroup` (Review + Static) computes min/max bar indices across **all** annotations/events for that `trade_group_id` on the active timeframe (default 1m path as today) and calls `fitRange` on that span with modest padding. Single-event groups remain a tight window. Carrier **N-Group-span** (pure helper) + **B-Group-span** or screenshot V2 proving multi-event span (not first-bar only).
6. **OPT-005 — Highlight band:** Highlight range uses the same span (style may be `marker` band or existing multi-bar highlight API); not `start === end` unless the group has one bar only.
7. **OPT-005 — Collapsed meta:** Card meta shows time span from pure helper plus event count (`· N pts` when N≥1, exact copy frozen in implementation notes if mock uses `pts`). No $/%. Carrier **N-Card-meta**.
8. **OPT-005 — Timeline UI:** Expanded legs render compact rows `TIME | ACTION | QTY @ PX` with short actions BUY/SELL/PART (map: `buy_open`/`buy_add`→BUY, `sell_close`→SELL, `sell_partial`→PART). No fees/`?` fee noise. Carrier **N-Timeline-source** + visual V1.
9. **OPT-005 — Row click (secondary):** Clicking a timeline row centers/highlights that event without replacing primary span-fit as the group-select behavior. If implementation stages this behind a small helper, both paths stay pure-testable. Carrier **N-Event-focus** and/or browser note on V1.
10. **OPT-006 — Data density:** On Data page wide panel, ticker tabs and 最近/按月 buttons are content-sized or capped (no full-bleed stretch). Prefer scoped CSS under `.page .panel .review-context-panel` (or equivalent density variant). Review `.dr-sidebar` progressive rail must not regress to broken non-stretch or broken stretch. Carrier **N-Data-rail-source** + screenshot V3.
11. **Contracts preserved:** B-chip multi-select, Download four-file behavior, marker BUY/SELL labels, points-only cards (no outcome %), direction colors, progressive date state machine, open-Review-on-date, market-day inventory.
12. **Tests/builds:** `npm run test:trade-records` green with updated carriers; normal + static Vite builds green; `python scripts/check-project-harness.py --root . --profile auto` green; `git diff --check` clean on task paths.
13. **Screenshots:** §2.3 matrix under `output/` (untracked).

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review trade tools + expanded card | desktop `1672x941` | QQQ `2026-07-17` multi-event 沃德哥/vordinkkk PUT (or CALL) group | No Eligibility row; timeline rows BUY/SELL/PART; meta with span + count |
| V2 | Interactive Review chart after group select | desktop `1672x941` | Same multi-event group | Viewport frames full event span; highlight band; not single first bar only |
| V3 | Data Market days progressive rail | desktop `1672x941` | Any SPY/QQQ inventory | Ticker + mode compact (not full-bleed slabs); day chips hierarchy sane |
| V4 | Interactive Review after 1m→5m switch | desktop `1672x941` | SPY or QQQ `2026-07-17` | First paint after 5m is a full usable window (no wheel required) |

Compare against §1.2 live screenshots and session mock.

### 2.4 Frozen verification carrier matrix

| Carrier ID | Tool | Proves | Must not claim |
| --- | --- | --- | --- |
| **N-Eligibility-removed-source** | Node `test:trade-records` source inspection | Shared `TraderFilters` production source has no Eligibility segment chrome / Display·Reported·Calculated tools-row | Admin editor fieldset deletion |
| **N-Eligibility-default** | Node pure filter tests | Default / tools path filters as display-eligible; non-display groups excluded | Browser click |
| **N-Group-span** | Node pure helper | min/max bar (or time→index) across all group events; single vs multi-event; incomplete times ignored | Canvas paint |
| **N-Card-meta** | Node pure + list source | Span label + event count formatting; no $/% | Layout beauty |
| **N-Timeline-source** | Node source inspection | Compact row structure; BUY/SELL/PART map; no fees on expand path | Click-to-chart |
| **N-Event-focus** | Node pure helper (optional if staged) | Event→bar focus input shape without full-day fit | Playwright |
| **N-Data-rail-source** | Node source/CSS inspection | Data-scoped max-width / flex overrides; Review `.dr-sidebar` stretch rules still intentional | Pixel-perfect Data aesthetics alone |
| **N-TF-viewport** | Node pure viewport helper **if** logic is extractable without canvas; else omit and rely on **B-TF-first-paint** only | Correct post-switch count/viewStart invariants | Browser |
| **B-TF-first-paint** | Playwright (or deterministic engine harness) | 1m→5m first frame usable; optional 5m→1m | Source regex |
| **B-Group-span** | Playwright **or** V2 screenshot + pure **N-Group-span** with explicit dual requirement | Multi-event group select frames span | First-annotation-only path |
| **V1–V4** | Screenshots under `output/` | Visual acceptance | Interaction beyond paint unless paired with B-\* |

**Hard rule:** Do not assign real DOM TF-switch or canvas paint proofs to plain Node `test:trade-records` unless a pure helper is extracted. Prefer one named carrier per claim (no “test or browser” fallback wording).

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/TraderFilters.jsx` — remove Eligibility fieldset/segment from tools strip; keep Download slot / Traders chrome.
2. `frontend/src/features/review/tradeRecords.js` — keep/display-default eligibility filter semantics; pure helpers for group event span (bar indices), short action labels, optional event-focus payload; card meta count if co-located.
3. `frontend/src/features/review/TraderTradeList.jsx` — collapsed meta span+count; compact timeline expand UI; optional row click callback.
4. `frontend/src/pages/ReviewPage.jsx` — `selectTradeGroup` span-fit + highlight band; wire event-row focus if present.
5. `frontend/src/pages/StaticReviewsApp.jsx` — same group-select / list wiring as Review for parity.
6. `frontend/src/kline/kline-engine.js` — fix `setTimeframe` / viewport first-paint (and only supporting viewport helpers in the same file as required).
7. `frontend/src/styles.css` — timeline row styles; Data-scoped progressive rail density (`.page .panel .review-context-panel` or equivalent); remove unused Eligibility tools styles only if unreferenced.
8. `frontend/src/pages/DashboardPage.jsx` — only if a density className wrapper is needed on the panel / context host.
9. `frontend/src/features/review/ReviewContextPanel.jsx` — only if a surface density prop/class is required (prefer CSS-only).
10. `frontend/src/features/review/tradeRecords.test.js` and/or `reviewWorkspace.test.js` — **N-\*** carriers; update/remove polish-plan pins that required Eligibility tools chrome.
11. Optional Playwright session artifacts under `output/playwright/…` (untracked) for **B-\*** carriers.

**Lifecycle / evidence (this proposal package and later transitions):**

12. Optimization session batch + `docs/optimization/index.md` status/lifecycle links for OPT-003…006.
13. `PROGRESS.md` / `HANDOFF.md` state blocks.
14. Plan file + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + `docs/exec-plans/roadmap.md` as lifecycle requires.
15. Screenshots under `output/` (untracked; do not stage).

**Out of manifest / must not change:**

- Backend APIs, tracked SQLite, content day JSON, seed market-data, Pages workflows, daily runbook, provider/broker.
- OPT-001/002 completed product locks (points-only cards, marker BUY/SELL + display_name).
- Eligibility **schema fields** on groups; Admin editor eligibility form (unless sharing accidental breakage — preserve).
- Progressive date state machine semantics and market-day inventory.
- Direction color tokens; B-chip threshold; Download four-file payload shape.
- Unrelated dirty / untracked `output/` trees — preserve; do not stage.

### 3.2 Unrelated dirty paths to preserve

Untracked evidence trees under `output/local-acceptance/`, `output/playwright/trade-panel-polish-20260721/`, `output/playwright/trade-points-marker-labels-20260721/` (and any newer session dumps) are user/evidence-owned. Do not stage, delete, or mix into this lifecycle commit.

### 3.3 Safety / data boundaries

- Presentation / engine / layout only.
- No `--allow-date-loss`. No provider fetch. No Pages publish. No push/PR/remote.
- No candidate DB projection. No content registry mutation.
- Activation and implementation require separate explicit user instructions after matching-revision design `approve`.

### 3.4 Behavioral invariants

- Empty trader selection continues to hide groups honestly.
- Voided/superseded group flags remain factual in data even if tools Eligibility chrome is gone.
- Single-event groups still get a sensible tight fitRange (not empty span).
- TF switch must not leave follow-mode or zoomScale in a state that only wheel can repair.
- Data rail density changes must not break keyboard/ARIA roles on ticker tabs or mode group.

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: plan Active + explicit implementation-start (or full-execution) instruction — **not** granted by this proposal.
- Work:
  1. Confirm HEAD baseline; re-hash §1.2 evidence.
  2. Record green `npm run test:trade-records` count and which polish-plan Eligibility pins must be rewritten.
  3. Freeze visual fixtures: QQQ `2026-07-17` multi-event group for V1/V2; Data inventory for V3; SPY or QQQ for V4 TF switch.
  4. Note investigation hypothesis for OPT-004 (viewStart/zoomScale/getResolvedViewCount after 1m→5m) without expanding into bar pipeline work.
- Verification: list §3.1 paths; confirm OPT-001/002 not reopened; confirm no DB/content paths in manifest.
- Exit gate: `phase-0-exit` with baseline note (plan appendix or untracked `output/`).

### Phase 1 — Implementation

- Entry gate: `phase-0-exit`.
- Work units (may land as one commit under full-execution authority; split only if rollback boundary requires):
  1. **WU-A OPT-003:** Remove Eligibility tools chrome; hard-default display filter; update **N-Eligibility-*** tests; drop obsolete B-Eligibility interaction requirement from this plan’s exit (polish-plan history remains append-only).
  2. **WU-B OPT-005:** Pure span helper; `selectTradeGroup` span-fit + band; timeline UI + meta count; optional row focus; Review/Static parity.
  3. **WU-C OPT-004:** Engine first-paint TF viewport fix; **B-TF-first-paint** or pure **N-TF-viewport**.
  4. **WU-D OPT-006:** Data-scoped rail density CSS (+ wrapper class if needed); protect Review sidebar.
- Verification: all §2.4 carriers applicable; normal + static builds; harness auto; V1–V4 screenshots.
- Exit gate: `phase-1-exit`.

### Phase 2 — Closeout Package

- Entry gate: `phase-1-exit`.
- Work: implementation-review packet; independent implementation review; on `accept`, migrate plan to `completed/` under operating-modes closeout rules; back-link OPT-003…006 to completed plan.
- Verification: implementation review `accept`; indexes/roadmap/state blocks agree.
- Exit gate: `closed` after completed migration.

## 5. Evidence And Commit Plan

- Baseline commands: `python scripts/check-operating-modes.py --root .`; `python -m unittest scripts.tests.test_operating_modes`; `python scripts/check-project-harness.py --root . --profile auto`
- Focused checks (implementation): `cd frontend && npm run test:trade-records`; normal + static builds; **B-\*** receipts under `output/`; V1–V4 screenshots
- Full checks: harness auto; `git diff --check` on staged paths
- Expected state/handoff updates: Proposed now at v1 awaiting independent design review; Active only after matching design approve + user activation instruction
- Task-owned commit paths for **this proposal step**:
  - `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md`
  - `docs/exec-plans/proposed/index.md`
  - `docs/exec-plans/roadmap.md`
  - `docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md`
  - `docs/optimization/index.md`
  - `PROGRESS.md`
  - `HANDOFF.md`
- No-commit condition: none for a complete proposal package

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan/`
- Required verdict: independent design-review `approve` on exact revision `v1-proposal-2026-07-21` (or a later foldback revision)
- Required user approval: explicit activation instruction after matching-revision approve
- Activation is a separate lifecycle change before implementation
- Implementation start requires a later explicit start/execute instruction after activation recording
- Creating this durable plan is committed locally by default; no separate commit-authority metadata is required

### 6.1 Authority boundary (now)

| Action | Authorized now? |
| --- | --- |
| Independent design review of exact v1 | Yes (reviewer, not implementer) |
| Lifecycle activation Proposed → Active | No — needs matching approve + user activation instruction |
| Phase 0 start / implementation | No |
| Push / PR / merge / Pages | No |
| Provider / broker / tracked DB / content day files | No |

## 7. References

- Operating modes: [`docs/operating-modes.md`](../../operating-modes.md)
- Optimization source: [`docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md`](../../optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md)
- Completed OPT-001/002 plan: [`docs/exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`](../completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md)
- Completed polish plan (Eligibility history): [`docs/exec-plans/completed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md`](../completed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md)
- Completed Data progressive nav: [`docs/exec-plans/completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`](../completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md)

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
