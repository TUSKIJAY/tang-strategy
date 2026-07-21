# Tang Strategy Trade Tools, Group Span, Viewport, And Data Rail

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan`
- Revision: `v2-review-foldback-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-trade-tools-group-span-viewport-data-rail`
- Design reviews: ../reviews/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan/review-001.md@revise@v1-proposal-2026-07-21
- Latest design verdict: revise
- Review independence: attested
- Activation evidence: none
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: `design-review`
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

### 1.2 Review foldback closure map

#### review-001 closure (v1 → v2)

Independent `review-001` returned `revise/high` against exact revision `v1-proposal-2026-07-21` (plan SHA-256 `8d179e57…16b9` at HEAD `fb3eae63…eee2`). Revision `v2-review-foldback-2026-07-21` folds every finding:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | Removing Eligibility UI does not freeze one display-only authority for list / availability / export; helpers disagree on missing or stale `eligibility` | §1.4 + §2.2 + §2.4 freeze pure `canonicalizeTradeToolsFilters` (or equivalent) that **always** forces `eligibility: 'display'` before `filterTradeGroups`, `displayableTradeGroups`, and `exportSelectionFromFilters` on the shared tools path. Fixtures: omitted / `reported` / `calculated` / non-display group → identical display-only group IDs and `display_only: true` export. Admin editor group flags unchanged. |
| P1 | Span helper can pass while live `fitRange` then `scrollTo(center:true)` undoes span; `marker`/`olive` styles draw dots not bands; event-row focus and `N pts` undefined; `B-Group-span` optional | §1.4 freezes **one** Review/Static integration sequence: derive all mappable indices → `setHighlightRanges` with style **`blue`** (live multi-bar band paint) → single `fitRange` → **no** post-fit centering `scrollTo` that mutates the fitted window. Event-row focus is **required** secondary (single-bar focus, no full-day fit). `N pts` = count of complete-timed events used for the span. Mandatory **B-Group-span** asserts stored highlight start/end, visible window contains full span, single-event behavior, Review/Static parity. |
| P1 | TF first-paint carrier is optional pure-or-browser; V4 cannot prove first frame / no wheel | §2.4 freezes **only** mandatory **B-TF-first-paint** (Playwright). Exact fixture, no-wheel event log, TF click, first animation-frame boundary, assert rendered `start`/`end`/`count`/`zoomScale`/`followMode` for **1m→5m and 5m→1m**. V4 is supplemental visual only. Any tracked harness script path enters the manifest. |
| P2 | Generic `.page .panel` CSS cannot prove Review sidebar safety | §1.4 freezes explicit host class **`data-market-days-rail`** on Data only. All flex/max-width overrides scoped under it. Carriers: **N-Data-rail-source** + **B-Data-rail-layout** computed styles (Data compact + Review sidebar unchanged) + screenshots V3 (Data) / V5 (Review desktop) / V6 (Review narrow). |

`review-001` is append-only prior-revision evidence and **cannot approve v2**. Next gate is independent design review of exact revision `v2-review-foldback-2026-07-21`.

### 1.3 Visual evidence

| 证据 | 路径 | SHA-256 | 作用 |
| --- | --- | --- | --- |
| Eligibility row to remove | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-tools-eligibility-remove.png` | `d0a6beba6c6069fc9a39a62623c73a4a9fc6273eca75f359483d5b8fe80ee11a` | OPT-003 现状 |
| 5m switch broken first paint | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-kline-5m-switch-initial-viewport.png` | `9691ae10b41503db49ceaaf6db64880c1d934646662baf62e81f0309ad8efe08` | OPT-004 现状 |
| Group select zooms first event only | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-group-select-first-event-only.png` | `1256380599cb21a0236d59f071ac6b7759955501be8a3c1cd1dca0ae0159f7d0` | OPT-005 chart |
| Legs/events dense dump | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-legs-events-current-ui.png` | `888970a008cc039edd12a3ddf662d5ed44c9be46384a89733c4b3daa27d1b5e6` | OPT-005 list |
| Data Market days stretched | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-data-market-days-stretched-controls.png` | `39888c6db1ef1e211b21e6bf63de950ce40c597538f7ad72ae423c6aab0da0f8` | OPT-006 现状 |
| Session mock (all UI items) | `docs/optimization/2026-07-21-review-trade-and-kline-session/mockups/review-trade-and-kline-session.html` | `f2cbec2cf0ae1ee2f292583c40c693adb766a911a4e5f872d9250828d680de6a` | OPT-003…006 目标方向 |

### 1.4 Current repository facts

**OPT-003 — Eligibility on trade tools:**

- Live: `TraderFilters.jsx` renders Eligibility fieldset (Display / Reported / Calculated).
- `initialTradeRecordFilters` → `eligibility: 'display'`.
- Live helper inconsistency (review-001): `displayableTradeGroups` defaults missing eligibility to display; `filterTradeGroups` treats missing eligibility as **no** eligibility filter; `exportSelectionFromFilters` emits `display_only: false` when eligibility is not exactly `'display'`.
- Admin `TraderPointEditor` eligibility fieldset is separate (group flags).

**OPT-004 — 5m first paint:**

- `kline-engine.js` `setTimeframe` maps previous start by time, sets `viewStart`, `scheduleRender()`.
- Viewport counts are TF-specific (5m slot width 18, min 18, max 72).
- No existing runtime K-line Node suite; engine is browser-owned.

**OPT-005 — Group select + legs UI:**

- `selectTradeGroup` finds first annotation, single-bar highlight (`style: 'marker'`), `fitRange` radius ~10–12, then `scrollTo(... center: true)`.
- Live `drawHighlightRanges`: styles `marker` and `olive` collapse to a **single top-of-chart dot**; only `red` / `blue` paint multi-bar **bands**.
- `groupEventTimeRange` yields min/max HH:MM + `knownCount` over complete events.
- Expanded legs dump raw schema actions.

**OPT-006 — Data progressive rail stretch:**

- `DashboardPage` mounts `ReviewContextPanel` in wide `.page .panel`.
- Global `.ticker-tabs button` / `.date-rail-mode button` use `flex: 1` (fine in narrow `.dr-sidebar`).

### 1.5 User scope locks (v2; supersedes ambiguous v1 bullets)

| Decision | Lock |
| --- | --- |
| OPT-003 UI | **Remove** Eligibility row from shared `TraderFilters` tools strip (Review / Static / Admin tools) |
| OPT-003 display-only authority | Pure **`canonicalizeTradeToolsFilters(filters)`** (name may vary) **always** sets `eligibility: 'display'` for shared tools consumers. **Every** list / availability / export call path uses the canonicalized object (or helpers themselves force-display). Stale `reported`/`calculated`/omitted inputs cannot widen the set. Export selection always has `display_only: true` on this path |
| OPT-003 schema | Group eligibility **flags** + Admin editor fieldset **remain** |
| OPT-003 Download / Traders | Keep |
| OPT-004 outcome | First painted frame after TF switch is a correct full-window viewport without wheel |
| OPT-004 carrier | **Mandatory B-TF-first-paint only** (no pure-or-browser fallback). Covers 1m→5m and 5m→1m |
| OPT-004 data | No bars/assemble/seed/DB/publish changes |
| OPT-005 group-select sequence | **Exact order (Review + Static identical):** (1) collect all mappable bar indices for the group on 1m (or active TF if annotations exist); (2) `setHighlightRanges({ timeframe, startIndex: min, endIndex: max, style: 'blue' })` — **`blue` is required** because it paints a real multi-bar band in live engine; do **not** use `marker`/`olive` for span; (3) one `fitRange` over that span with modest padding; (4) **forbidden** after group-select: `scrollTo` with `center: true` (or any recenter) that changes `viewStart`/`zoomScale` away from the fitted window |
| OPT-005 single-event | min===max still uses blue band + tight fitRange |
| OPT-005 event-row focus | **Required** secondary: timeline row click → single-bar highlight + center/focus that event **without** expanding to full day and **without** replacing the primary span-fit as the card-click behavior |
| OPT-005 `N pts` | Count of **complete-timed** events included in the span helper (`knownCount`); incomplete times excluded from both span and count |
| OPT-005 expanded UI | `TIME \| ACTION \| QTY @ PX`; BUY/SELL/PART; no fees |
| OPT-005 anti-pattern | No auto-fit each partial on group click |
| OPT-006 host class | Explicit **`data-market-days-rail`** (or exact string frozen in Phase 0 if renamed once) on Data host only — **not** bare `.page .panel` |
| OPT-006 CSS | All ticker/mode flex/max-width overrides under `.data-market-days-rail …` only |
| OPT-006 IA | Progressive state machine, ticker isolation, open-Review-on-date unchanged |
| Surfaces | OPT-003 tools: Review+Static+Admin. OPT-005: Review+Static parity. OPT-004: Review (+Static if same engine). OPT-006: Data host; Review sidebar must not regress |

Rejected: reopening OPT-001/002; schema bumps; day-file rewrites; Pages/provider/broker; rubber-stamp pure defaults that leave export wide-open; `marker`/`olive` as span band; optional TF carrier wording; generic `.page .panel` density selector as the sole scope.

### 1.6 Lane 3 classification

Cross-surface frontend work: shared trade tools/list, K-line engine viewport + highlight, Review/Static group-focus, Data progressive rail density, and mandatory Playwright carriers. Classified Coding Mode **Lane 3**. No market-data fetch, provider/broker, Pages, tracked DB, or content day-file rewrites.

## 2. Objective And Success Criteria

### 2.1 Objective

把 session 剩余摩擦一次收口：

1. Trade tools **不再展示** Eligibility；list/availability/export **统一** display-only；
2. K 线 TF 切换 **首帧**视口正确（强制浏览器 carrier）；
3. 点击交易组 **框住整段** + 真实 multi-bar band；展开为可扫时间线并可点单笔；
4. Data Market days 使用 **显式 host class** 紧凑布局，Review 侧栏不回归。

### 2.2 Success criteria

1. **OPT-003 chrome gone:** Shared tools strip sources have no Eligibility / Display / Reported / Calculated segment. **N-Eligibility-removed-source**.
2. **OPT-003 canonical display-only:** After canonicalization, `filterTradeGroups`, `displayableTradeGroups`, and `exportSelectionFromFilters` produce the same display-eligible group ID set for inputs with eligibility omitted, `'display'`, `'reported'`, or `'calculated'`, and export always has `display_only: true`. Non-display-eligible groups never appear. **N-Eligibility-default** fixtures cover all four inputs + at least one non-display group.
3. **OPT-003 schema/editor intact:** Admin editor eligibility flags remain.
4. **OPT-004 first-paint:** **B-TF-first-paint** green for 1m→5m and 5m→1m with no wheel events; asserts post-first-frame viewport metrics (visible start/end/count, zoomScale, followMode) are sane (no permanent left-crowd empty-right that only wheel repairs). V4 screenshot supplemental only.
5. **OPT-005 span + band:** Pure **N-Group-span** computes min/max indices over all mappable complete events. Live select sequence matches §1.5. Highlight stored as blue multi-bar band. **B-Group-span** mandatory.
6. **OPT-005 meta:** Span label + `· N pts` with N = complete-timed event count. **N-Card-meta**.
7. **OPT-005 timeline:** Compact BUY/SELL/PART rows, no fees. **N-Timeline-source** + V1.
8. **OPT-005 event focus:** Required row-click path; pure **N-Event-focus** + exercised in **B-Group-span** or a dedicated browser step on the same receipt.
9. **OPT-006 density:** Host class present on Data only; computed layout proves compact Data controls and unchanged Review sidebar flex growth. **N-Data-rail-source** + **B-Data-rail-layout** + V3/V5/V6.
10. **Contracts preserved:** B-chip, Download four-file payload shape, marker BUY/SELL, points-only cards, direction colors, progressive date IA, open-Review-on-date.
11. **Tests/builds:** `npm run test:trade-records` green for all **N-\***; all **B-\*** receipts green under `output/`; normal + static builds; harness auto; `git diff --check` on task paths.
12. **Screenshots:** §2.3 under `output/` (untracked).

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review tools + expanded card | desktop `1672x941` | QQQ `2026-07-17` multi-event vordin/vordinkkk group | No Eligibility; timeline BUY/SELL/PART; meta span + N pts |
| V2 | Interactive Review chart after group select | desktop `1672x941` | Same multi-event group | Full span fit; **blue multi-bar band** (not top-dot only) |
| V3 | Data Market days progressive rail | desktop `1672x941` | Any SPY/QQQ inventory | Compact ticker/mode under `data-market-days-rail` |
| V4 | Review after 1m→5m | desktop `1672x941` | SPY or QQQ `2026-07-17` | Supplemental first-paint visual (does not replace **B-TF-first-paint**) |
| V5 | Review sidebar progressive rail | desktop `1672x941` | Same | Sidebar stretch still intentional / not broken by Data overrides |
| V6 | Review sidebar progressive rail | narrow `390x844` (or plan Phase-0 frozen narrow) | Same | Narrow sidebar still usable |

### 2.4 Frozen verification carrier matrix (v2 — no fallbacks)

| Carrier ID | Tool | Proves | Must not claim |
| --- | --- | --- | --- |
| **N-Eligibility-removed-source** | Node source | Tools strip has no Eligibility chrome | Admin editor deletion |
| **N-Eligibility-default** | Node pure | Canonicalize + filter + displayable + export for omitted/display/reported/calculated; non-display group excluded; `display_only: true` | Browser |
| **N-Group-span** | Node pure | min/max indices; multi vs single; incomplete ignored | Canvas |
| **N-Card-meta** | Node pure + source | Span + `N pts` = complete-timed count; no $/% | Beauty |
| **N-Timeline-source** | Node source | Row structure; BUY/SELL/PART; no fees | Click chart |
| **N-Event-focus** | Node pure | Event→single-bar focus payload; distinct from group span-fit | Playwright alone |
| **N-Data-rail-source** | Node source/CSS | Host class `data-market-days-rail`; overrides scoped under it; no bare `.page .panel` sole selector | Computed layout |
| **B-TF-first-paint** | **Mandatory** Playwright | 1m→5m and 5m→1m; no wheel; first rAF after switch; assert viewport start/end/count/zoomScale/followMode sane | V4 alone; source regex |
| **B-Group-span** | **Mandatory** Playwright | Multi-event: highlight start/end match span; visible window contains full span; single-event tight; Review **and** Static; no post-fit center undo; optional event-row focus step | V2 alone |
| **B-Data-rail-layout** | **Mandatory** Playwright (or equivalent computed-style harness) | Data host: ticker/mode buttons not full-bleed flex-grown; Review `.dr-sidebar` controls retain expected flex/growth | Screenshot alone |
| **V1–V6** | Screenshots | Visual acceptance | Interaction semantics |

**Hard rule:** Every interaction/canvas/computed-layout claim names a **B-\*** carrier. Every pure/source claim names an **N-\*** carrier. No “test or browser” wording.

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/TraderFilters.jsx` — remove Eligibility fieldset; keep Download / Traders.
2. `frontend/src/features/review/tradeRecords.js` — `canonicalizeTradeToolsFilters` (or equivalent) forced display; pure group bar-span helper; short action labels; event-focus payload; card meta count helper; ensure filter/displayable/export consume canonical display-only.
3. `frontend/src/features/review/TraderTradeList.jsx` — meta span+N pts; timeline UI; required row-click callback prop.
4. `frontend/src/pages/ReviewPage.jsx` — group-select sequence §1.5; wire event-row focus; pass canonicalized filters into list/export.
5. `frontend/src/pages/StaticReviewsApp.jsx` — same as Review for group-select + filters.
6. `frontend/src/pages/AdminTradersPage.jsx` — tools path uses canonical display-only; no Eligibility tools chrome if shared component.
7. `frontend/src/kline/kline-engine.js` — TF first-paint fix in `setTimeframe` / viewport helpers only as required. Highlight **band** for trade span uses existing `blue` style (no requirement to re-enable olive multi-bar teaching bands).
8. `frontend/src/styles.css` — timeline styles; **only** `.data-market-days-rail …` density overrides; cleanup unused Eligibility tools styles if unreferenced.
9. `frontend/src/pages/DashboardPage.jsx` — add host class `data-market-days-rail` on the Market days progressive rail wrapper.
10. `frontend/src/features/review/ReviewContextPanel.jsx` — only if a density prop is required (prefer host class on Dashboard).
11. `frontend/src/features/review/tradeRecords.test.js` and/or `reviewWorkspace.test.js` — all **N-\*** carriers; remove obsolete Eligibility tools chrome pins.
12. Playwright (or committed frontend harness scripts under `frontend/` if added) for **B-TF-first-paint**, **B-Group-span**, **B-Data-rail-layout**. Default receipts under `output/playwright/trade-tools-group-span-<timestamp>/` (untracked). If a tracked runner script is added, list its exact path in Phase 0 evidence.

**Lifecycle / evidence:**

13. Optimization batch + `docs/optimization/index.md`.
14. `PROGRESS.md` / `HANDOFF.md`.
15. Plan + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + roadmap.
16. Screenshots under `output/` (untracked).

**Out of manifest:**

- Backend, tracked SQLite, content day JSON, seed, Pages, runbook, provider/broker.
- OPT-001/002 locks; Admin editor eligibility form fields; progressive date state machine; direction tokens; B-chip threshold; Download payload columns.
- Unrelated `output/` trees.

### 3.2 Unrelated dirty paths to preserve

Untracked `output/local-acceptance/`, `output/playwright/*` evidence trees — preserve; do not stage.

### 3.3 Safety / data boundaries

- Presentation / engine / layout only.
- No `--allow-date-loss`, provider fetch, Pages, push/PR/remote, DB projection, content registry mutation.
- Activation and implementation require separate explicit user instructions after matching-revision design `approve`.

### 3.4 Behavioral invariants

- Empty trader selection still hides groups.
- Group eligibility flags remain factual in data.
- Single-event groups get tight blue band + fitRange.
- TF switch must not leave zoomScale/followMode repairable only by wheel.
- Data density must not break ticker tablist / mode group ARIA roles.
- Teaching/setup highlight styles (`olive` dot behavior) must not be silently broken for non-trade ranges unless an explicit supersession is documented in phase evidence.

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: plan Active + explicit implementation-start / full-execution — **not** granted by this proposal.
- Work: HEAD baseline; re-hash §1.3 evidence; record trade-records baseline count; freeze QQQ `2026-07-17` multi-event group id for V1/V2/B-Group-span; freeze SPY or QQQ day for B-TF-first-paint; freeze narrow viewport for V6; confirm `blue` band paint path.
- Verification: §3.1 paths; no OPT-001/002 reopen; no DB/content paths.
- Exit gate: `phase-0-exit`.

### Phase 1 — Implementation

- Entry gate: `phase-0-exit`.
- Work units:
  1. **WU-A OPT-003:** Remove chrome; canonicalize display-only; **N-Eligibility-*** green.
  2. **WU-B OPT-005:** Span helper; blue band; fitRange-only sequence; timeline; event focus; **N-\*** + **B-Group-span**.
  3. **WU-C OPT-004:** Engine first-paint; **B-TF-first-paint** both directions.
  4. **WU-D OPT-006:** `data-market-days-rail` + scoped CSS; **N-Data-rail-source** + **B-Data-rail-layout**.
- Verification: all carriers; builds; harness; V1–V6.
- Exit gate: `phase-1-exit`. Missing any **B-\*** fails exit.

### Phase 2 — Closeout Package

- Entry gate: `phase-1-exit`.
- Work: implementation-review packet; independent implementation review; on `accept`, completed migration + OPT back-links.
- Exit gate: `closed` after completed migration.

## 5. Evidence And Commit Plan

- Baseline commands: operating-modes checker; lifecycle unittest; harness auto
- Focused checks (implementation): `npm run test:trade-records`; normal + static builds; **B-\*** under `output/`; V1–V6
- Expected state now: Proposed **v2** awaiting independent design review of exact `v2-review-foldback-2026-07-21`
- Task-owned commit paths for **this foldback**:
  - `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md`
  - `docs/exec-plans/proposed/index.md`
  - `docs/exec-plans/roadmap.md`
  - `docs/exec-plans/reviews/index.md` (verdict remains review-001 revise until review-002)
  - `PROGRESS.md`
  - `HANDOFF.md`
- No-commit condition: none for a complete foldback package

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan/`
- Required verdict: independent design-review `approve` on exact revision `v2-review-foldback-2026-07-21` (or a later foldback)
- `review-001` remains append-only and cannot approve v2
- Activation requires matching-revision approve **plus** explicit user activation instruction
- Implementation requires later explicit start/execute after activation

### 6.1 Authority boundary (now)

| Action | Authorized now? |
| --- | --- |
| Independent design review of exact v2 | Yes (reviewer, not plan author) |
| Lifecycle activation | No |
| Implementation | No |
| Push / PR / merge / Pages | No |
| Provider / broker / DB / content day files | No |

## 7. References

- Operating modes: [`docs/operating-modes.md`](../../operating-modes.md)
- Optimization source: [`docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md`](../../optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md)
- Design review-001 (v1): [`../reviews/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan/review-001.md`](../reviews/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan/review-001.md)
- Completed OPT-001/002 plan: [`docs/exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`](../completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md)
- Completed polish plan: [`docs/exec-plans/completed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md`](../completed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md)
- Completed Data progressive nav: [`docs/exec-plans/completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`](../completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md)

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
