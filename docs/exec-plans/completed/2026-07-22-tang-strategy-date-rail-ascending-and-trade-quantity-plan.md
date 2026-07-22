# Tang Strategy Date Rail Ascending And Trade Quantity

- Lifecycle schema: `operating-modes-v1`
- Status: Completed
- Plan slug: `2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan`
- Revision: `v2-review-foldback-2026-07-22`
- Plan author ID: `grok-plan-author-2026-07-22-date-rail-quantity`
- Design reviews: ../reviews/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan/review-001.md@revise@v1-proposal-2026-07-22, ../reviews/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan/review-002.md@approve@v2-review-foldback-2026-07-22
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: user-instruction:2026-07-22-activate-date-rail-ascending-and-trade-quantity-plan
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: ../reviews/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan/implementation-review-001.md@accept
- Final disposition: Completed
- Verified implementation commit: da12e1b03715be3de75fcafd8d47aa1a35554942
- Lifecycle reconciliation commit: none
- Owner: Grok
- Created: 2026-07-22
- Optimization source: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/2026-07-22-review-date-rail-and-trade-quantity-session.md` OPT-001 + OPT-002 + OPT-003
- Proposal baseline: `codex/project-harness@f40887100a7b4f832c59da32ac1607dc47b05854`
- Scope authority: full local execution under `user-instruction:2026-07-22-execute-date-rail-ascending-and-trade-quantity-plan` (goal OBJECTIVE 你来全权负责执行这个plan). Matching design approval `review-002: approve/high`. Implementation review `implementation-review-001: accept/high`. Product commit `da12e1b03715be3de75fcafd8d47aa1a35554942`. No push/PR/merge/Pages/provider/broker/DB/content day-file/remote.
- Local commit: task-scoped default; does not authorize implementation start, push, or remote action

## 1. Context And Evidence

### 1.1 Proposal provenance

用户在 2026-07-22 完成 session OPT 验收（OPT 文档 foldback + mock direction-legend 修正）后，明确要求 **升级成 prop plan**。本计划一次晋升 session 批次全部三条 OPT：

| OPT | Title | 本计划 |
| --- | --- | --- |
| **OPT-001** | Progressive date chips must sort ascending (正序) | **In scope** |
| **OPT-002** | K-line marker labels show trade quantity instead of `×N` | **In scope** |
| **OPT-003** | Derive missing closing event quantity when open qty known | **In scope** |

相关已完成边界（不得回退）：

- Progressive DateRail (最近 / 按月) membership、month inventory newest-first、footer meta — completed date-nav + Data progressive plans.
- Marker vocabulary `display_name` + BUY/SELL；shape/color/anchor **direction-owned** (CALL up / PUT down); same-bar grouping key `bar|trader|direction|action_side` — completed trade-points / marker-labels plan. OPT-002 **replaces count `×N` with quantity `*QTY`** on that label surface only.
- Compact timeline `TIME | ACTION | QTY @ PX` with `?` for null — completed points-only / panel density work. OPT-003 fills **missing close qty on the read path** only.

### 1.2 Review foldback closure map

#### review-001 closure (v1 → v2)

Independent `review-001` returned `revise/high` against exact revision `v1-proposal-2026-07-22` (plan SHA-256 `edce9b64a163178661c8da8eaa037e45092683c4c44ac71f2a4ca07d9e446138` at HEAD `384497334ebd46b1bd73c49f406168f8ba4777a2`). Revision `v2-review-foldback-2026-07-22` folds the sole P1 finding:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | Fail-closed qty oracle incomplete: formula summed only *known* opens/partials and fallback covered only unknown open or over-partial sum; null `buy_add` / null prior `sell_partial` could still fabricate a derived close. Marker aggregation had the same mixed-known/unknown gap. Carrier text said “multi-bar sum,” contradicting same-side same-bar grouping. | §1.4 **OPT-003 completeness**: derive a null `sell_close` only when **every** prior quantity-bearing `buy_open`, `buy_add`, and `sell_partial` on that leg has a finite valid quantity; any unknown prior position-changing qty → unknown (timeline `?`, omit marker suffix). Opening qty = sum of **all** those open/add quantities only after completeness passes. “Prior” = validated event/sequence order on the leg before the close event. Numeric raw close still preferred as-is. §1.4 **OPT-002 marker completeness**: for a same-side same-bar group, emit `*QTY` on `marker_label` **and** `title` only when **every** contributing event has a known raw or derived quantity; otherwise omit suffix on both. §2.2 / §2.4: replace “multi-bar sum” with **same-side, same-bar sum**; expand **N-Qty-derive** / **N-Marker-qty** / **N-Timeline-qty** and Phase 0 fixtures to include adversarial cases: known open + unknown add → unknown; unknown prior partial → unknown; mixed known/unknown same-bar aggregation → omit `*QTY`; keep 150/12, raw-preferred, unknown-open, and over-partial. |

`review-001` is append-only prior-revision evidence and **cannot approve v2**. Next gate is independent design review of exact revision `v2-review-foldback-2026-07-22`.

### 1.3 Visual evidence

| 证据 | 路径 | SHA-256 | 作用 |
| --- | --- | --- | --- |
| DateRail 最近倒序 | `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/screenshots/2026-07-21-date-rail-recent-desc.png` | `41e89858444978159bfd1b88fd4a7f6870d32b83de8127ca92035dab1eb3f649` | OPT-001 |
| DateRail 按月倒序 | `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/screenshots/2026-07-21-date-rail-month-desc.png` | `e54d13943d3a9dbb7bc0b581ed185a2579f50ae01c65c30edf79587c5eb66c44` | OPT-001 |
| Marker `×N` | `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/screenshots/2026-07-21-kline-marker-quantity-desc.png` | `f45a860bfdcff764cbe870220b68776df1f2046f6d08434fbd0e40929d798480` | OPT-002 |
| Timeline `SELL ?` | `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/screenshots/2026-07-22-trade-close-quantity-question-mark.png` | `157a48331cd07f67f1c3848f89c5df2f0d44e5bbb9022cecefd665e5ec08334f` | OPT-003 |
| Design mock | `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/mock.html` | `0363492762fee72cc63adaa97f4797c22925a57758c7942fb52391d3fa0a1640` | Current vs Proposed for OPT-001…003 |

Mock is illustrative; **OPT Scope Lock + this plan** are authoritative over any residual mock pedagogy (e.g. teaching-only `derived` pill).

### 1.4 Current repository facts

**OPT-001 — progressive chips newest-first:**

- `datesForTicker` sorts ascending then `.reverse()` → newest-first inventory.
- `projectProgressiveDateRail` uses that order as chip `dates` for both 最近 (`slice(0, recentLimit)`) and 按月 (`datesInMonth`).
- Month list / switcher rely on newest-first month inventory (`listMonthsForTicker` / `stepBrowsedMonth`); that inventory order is **out of chip-order scope**.
- Progressive consumers: Review, Data (`DashboardPage`), Static (`dateNavigation="progressive"`). Admin/editor stay exhaustive.

**OPT-002 — marker count suffix:**

- `buildTradeRecordAnnotations` builds `marker_label` / `title` as `${displayName} ${BUY|SELL}`; after same-side grouping, `marker_label` becomes `… ×${count}` when `count > 1`; singles omit quantity.
- Shape/color/anchor remain direction-owned; grouping key unchanged.

**OPT-003 — timeline null quantity:**

- `groupTimelineEvents` passes raw `event.quantity`.
- `TraderTradeList.jsx` renders `{row.quantity ?? '?'} @ {row.premium ?? '?'}`.
- Live fixture `content/trades/2026-07-17.json`:
  - `tg_20260717_vordin_qqq_001` PUT: open `150`, `sell_close` `null` → expected derived **150**.
  - `tg_20260717_vordin_qqq_002` CALL: open `70`, partials `12+12+22+12`, `sell_close` `null` → expected derived **12**.

### 1.5 User scope locks (frozen)

| Topic | Lock |
| --- | --- |
| **OPT-001 order** | Chip rows **ascending** by `trade_date` (earlier left, later right) in **最近** and **按月** on Review / Data / Static progressive rails |
| **OPT-001 recent membership** | 最近 still = newest `N` dates (`PROGRESSIVE_RECENT_LIMIT`, 12). Membership set unchanged; **only display order** flips to ascending within that set |
| **OPT-001 month chrome** | Month switcher, newest-first month inventory, ticker tabs, selection authority, footer meta semantics unchanged |
| **OPT-002 quantity text** | Same-side **same-bar** multi-event aggregation shows sum: `` `${displayName} ${actionSide}*${totalQuantity}` `` (e.g. `vordinkkk SELL*24`). Single event with known qty: `… BUY*70`. Unknown after derivation **or incomplete group**: **omit suffix** (`… SELL`). Replace `×N` entirely — never both |
| **OPT-002 marker completeness** | For a grouped marker (same `bar\|trader\|direction\|action_side`), emit `*QTY` on **both** `marker_label` and `title` only when **every** contributing event has a known raw or derived quantity; if any contributing qty is unknown, omit the suffix from both fields |
| **OPT-002 surfaces** | Apply quantity form to **both** `marker_label` and `title` on the merged annotation object (post-group). No CALL/PUT text; no raw `trader_id` when `display_name` exists; no raw schema actions |
| **OPT-002 shape/color** | Unchanged direction-owned contract |
| **OPT-003 derivation** | Per **leg**, for `sell_close` with `quantity: null`: only when the **completeness rule** passes, `derived = opening_qty − Σ(prior sell_partial quantities on that leg before this event)`. Opening qty = sum of all `buy_open` + `buy_add` quantities on the leg (every such event must be known). “Prior” = events earlier in the validated event/sequence order on that leg. Example: PUT 150; CALL 12 |
| **OPT-003 completeness** | Derive a null close **only** when every prior quantity-bearing `buy_open`, `buy_add`, and `sell_partial` on that leg has a finite valid numeric quantity. Any unknown among those prior position-changing quantities → remaining position is unknowable → return unknown. Do **not** sum only the known subset and invent a close |
| **OPT-003 raw preferred** | If close event already has a numeric `quantity`, use it as-is (no overwrite), even if prior chain is incomplete |
| **OPT-003 fallback** | Unknown open, unknown prior add/partial, incomplete open/add/partial chain, **or** known prior partials sum **>** opening → keep timeline `?` and omit marker qty suffix. Do not invent |
| **OPT-003 render-only** | Presentation/read path only. **No** day JSON / content / DB / provenance rewrite |
| **OPT-003 chrome** | No product `derived` pill/badge |
| **Surfaces** | Review + Static aligned; prefer shared pure helpers (`reviewWorkspace` / `tradeRecords`) over page forks |
| **Out of scope** | Schema/API; provider/broker; DB rebuild; Pages; Admin editor UX redesign; month inventory reordering; fitRange/highlight contracts; marker shape redesign |

### 1.6 Lane 3 classification

Shared progressive date projection + shared trade-record pure helpers + Review/Static list/marker consumers. Coding Mode **Lane 3** (proposed Exec Plan). Frontend presentation only — no backend, market-data, content day writes, provider, or Pages.

## 2. Objective And Success Criteria

### 2.1 Objective

在 **Review / Data / Static** progressive DateRail 上把交易日 chip 显示为**时间正序**（最近窗口 membership 不变）；在 **Review / Static** 上把 K 线 trade-record 标注从事件数 `×N` 改为实际数量 `*QTY`（含同 bar 求和）；在时间线与标注读路径上，当腿开仓量已知时推导 `quantity: null` 的清仓剩余量，消灭可安全推导场景下的 `?`，且不回写源数据。

### 2.2 Success criteria

1. **Date chips ascending (OPT-001):** For progressive 最近 and 按月, `projectProgressiveDateRail(...).dates` is strictly ascending by ISO `trade_date` (or equal only if duplicate keys, which inventory forbids). Selected latest day in the recent window appears as the **last** chip when it is in the set.
2. **Recent membership (OPT-001):** The recent chip **set** equals the newest `N` inventory dates (same set as today’s newest-first `slice(0, N)`). Only order differs. Meta strings still report the same counts.
3. **Month inventory unchanged (OPT-001):** `listMonthsForTicker` / `stepBrowsedMonth` / month bar still treat months newest-first; chip order **within** the browsed month is ascending.
4. **Marker quantity (OPT-002):** After implementation, `buildTradeRecordAnnotations`:
   - never emits `×` count suffixes on `marker_label`;
   - emits `*QTY` on `marker_label` and `title` when the (post-derivation) quantity for the marker is known **and** every same-side same-bar contributor is known;
   - multi same-side **same-bar** events sum quantities (e.g. two PART 12 → `SELL*24`); mixed known/unknown contributors omit suffix on both fields;
   - shape/color/anchor/grouping key family unchanged; no CALL/PUT in label text.
5. **Close derivation (OPT-003):** Pure helper(s) derive remaining close qty for the QQQ `2026-07-17` vordin cases (150 / 12) only under the completeness rule. `groupTimelineEvents` (or consumer of the helper) exposes the derived number so the list shows `SELL 150 @ 0.15` / `SELL 12 @ 5.5` without a product derived pill.
6. **Marker consumes derivation (OPT-002←003):** Close markers for those fixtures show `SELL*150` / `SELL*12` (not bare `SELL` and not `×1`).
7. **Fallback (OPT-003):** Fixtures with unknown open, unknown prior add/partial, incomplete open/add/partial chain, or over-closed partials still render timeline `?` and omit marker qty suffix.
8. **No source write:** Implementation does not modify `content/trades/**`, tracked DB, or provenance fields.
9. **Tests/builds:** `npm run test:trade-records` green with updated carriers; normal + static Vite builds green; harness auto green; `git diff --check` clean on task paths.
10. **Screenshots:** §2.3 under untracked `output/` (optional Playwright; pure carriers are mandatory).

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Review or Data progressive rail | desktop `1672x941` | QQQ recent + 按月 | Chips ascending; 最近 still newest-12 set; selected day correct |
| V2 | Review K-line markers | desktop `1672x941` | QQQ `2026-07-17` | Labels like `vordinkkk SELL*24` / `BUY*70` / derived closes; no `×N`; direction shape preserved |
| V3 | Review trade timeline | desktop `1672x941` | QQQ `2026-07-17` vordin cards | `SELL 150 @ 0.15` and `SELL 12 @ 5.5` (no `?` on those rows) |

### 2.4 Frozen verification carrier matrix

| Carrier ID | Tool | Proves | Must not claim |
| --- | --- | --- | --- |
| **N-Date-asc** | Node `reviewWorkspace.test.js` | `projectProgressiveDateRail` recent + month `dates` ascending; pressedDate still correct | Browser CSS |
| **N-Date-membership** | Node same | Recent set equals newest-N; month inventory / stepBrowsedMonth still newest-first months | Chip paint |
| **N-Qty-derive** | Node `tradeRecords.test.js` | Pure derive helper: PUT 150; CALL 12 from complete partial chain; raw close qty preferred; unknown open / over-partial / known-open+unknown-add / unknown prior partial → null/`?` path | DOM |
| **N-Marker-qty** | Node same | No `×N`; `*QTY` on label+title; **same-side same-bar** sum; omit when any contributor unknown (mixed known/unknown same-bar); direction shape fields unchanged; no CALL/PUT in text | Canvas pixels |
| **N-Timeline-qty** | Node same + list source pin if needed | Timeline rows expose derived qty for complete safe close-null cases; still `?` on incomplete-chain and other unsafe cases | Product derived pill |
| **N-Surface-source** | Node source pin | Progressive still used on Review/Data/Static; no day-file write paths introduced | Runtime DB |
| **V1–V3** | Screenshots under `output/` | Visual acceptance vs mock / live friction shots | Semantics alone |

**Hard rule:** Missing any mandatory **N-*** carrier fails Phase 1 exit. V1–V3 are required visual receipts under untracked `output/` but do not replace pure carriers.

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/reviewWorkspace.js` — progressive **chip display order** ascending in `projectProgressiveDateRail` (preferred: reverse/sort only the projected `dates` array for chip rendering). Do **not** invert month inventory semantics used by `listMonthsForTicker` / `stepBrowsedMonth` unless Phase 0 proves an equivalent pure split. Keep `PROGRESSIVE_RECENT_LIMIT` and membership = newest N.
2. `frontend/src/features/review/tradeRecords.js` — pure close-quantity derivation helper(s); wire into `groupTimelineEvents` and `buildTradeRecordAnnotations` quantity aggregation / `*QTY` label+title formatting; remove `×N` count suffix path.
3. `frontend/src/features/review/TraderTradeList.jsx` — only if needed to consume derived quantity fields (prefer pure helper already returning final display qty so JSX stays `row.quantity ?? '?'`).
4. `frontend/src/features/review/tradeRecords.test.js` — **N-Qty-derive**, **N-Marker-qty**, **N-Timeline-qty** (update existing `×N` pins to `*QTY`).
5. `frontend/src/features/review/reviewWorkspace.test.js` — **N-Date-asc**, **N-Date-membership** (update order assertions; keep membership/meta).
6. `frontend/src/features/review/reviewWorkspace.fixtures.js` — only if pure tests need partial-chain fixtures (test fixtures only; not content day files).

**Lifecycle / evidence (separate authority per phase):**

7. Optimization record + `docs/optimization/index.md` status/lifecycle links.
8. `PROGRESS.md` / `HANDOFF.md` state blocks.
9. Plan file + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + `docs/exec-plans/roadmap.md`.
10. Screenshots under `output/` (untracked; do not stage).

**Out of manifest / must not change:**

- `content/trades/**`, tracked SQLite, seed market data, backend APIs, Pages workflows, provider/broker.
- Marker shape/color/anchor ownership; action→BUY/SELL map; grouping key family.
- Month switcher UX / newest-first month list product behavior.
- Admin point editor redesign; selection-band / fitRange contracts.
- New product dependencies beyond existing Node test suite (+ optional ad-hoc screenshots).

### 3.2 Unrelated dirty paths to preserve

Untracked `output/**` trees are evidence-owned. Do not stage or delete them as part of this plan.

### 3.3 Safety / data boundaries

- Frontend presentation only. No DB rebuild, no content mutation, no provider fetch, no Pages publish, no push/PR/remote.
- Fail closed on authority: activation and implementation each require their own explicit user instruction beyond this proposal.

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: plan Active + explicit implementation-start / execute instruction (not granted by proposal or by activation alone).
- Work:
  - Record HEAD baseline; re-hash §1.2 evidence if needed.
  - Confirm green `npm run test:trade-records` baseline.
  - Freeze pure fixture objects for N-Qty-derive / N-Marker-qty / N-Timeline-qty: (1) QQQ `2026-07-17` vordin PUT 150 and CALL 12 complete chains (mirror `content/trades/2026-07-17.json` or load via existing test helpers); (2) raw numeric close preferred; (3) unknown open → unknown; (4) over-partial sum > open → unknown; (5) **adversarial** known open + null `buy_add` → unknown; (6) **adversarial** null prior `sell_partial` → unknown; (7) **adversarial** same-bar mixed known/unknown contributor quantities → omit `*QTY` on label+title.
  - Confirm projection-only date reverse strategy vs any deeper `datesForTicker` change; document chosen approach in phase evidence.
- Verification: manifest paths only; OPT-001…003 only; no content/DB paths.
- Exit gate: `phase-0-exit` with baseline note under reviews evidence or untracked `output/`.

### Phase 1 — Implementation (OPT-001 + OPT-002 + OPT-003)

- Entry gate: `phase-0-exit` + implementation still authorized.
- Work:
  - Ascending chip projection for progressive rails.
  - Derive close qty pure helper; timeline + marker wiring; `*QTY` replaces `×N`.
  - Update all **N-*** carriers; capture V1–V3 under `output/`.
- Verification: all §2.2 criteria; all §2.4 N-carriers; normal + static builds; harness auto; `git diff --check` on task paths.
- Exit gate: `phase-1-exit` with implementation commit SHA + receipts.

### Phase 2 — Implementation Review And Closeout

- Entry gate: `phase-1-exit`.
- Work: implementation-review packet + independent implementation review; on accept migrate plan to `completed/`; OPT statuses → `completed` with lifecycle links; reconcile indexes/state.
- Verification: matching accept review; indexes unique; PROGRESS/HANDOFF state blocks match Completed/`closed`.
- Exit gate: `closed`.

## 5. Evidence And Commit Plan

- Baseline commands: `cd frontend && npm run test:trade-records`; `python scripts/check-operating-modes.py --root .`; `python scripts/check-project-harness.py --root . --profile auto`
- Focused checks: carriers in §2.4; normal + static Vite builds after Phase 1
- Full checks: harness auto; `git diff --check` on task-owned paths
- Expected state/handoff updates: each lifecycle transition updates PROGRESS/HANDOFF operating-modes-state blocks
- Task-owned commit paths (proposal package): this plan + proposed/reviews/exec roadmap indexes + OPT record/index + PROGRESS + HANDOFF
- No-commit condition: draft failure, user opt-out, or unclean ownership vs unrelated dirty paths

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan/`
- Matching design approval: independent `review-002: approve/high` on exact revision `v2-review-foldback-2026-07-22`
- Activation recording: `user-instruction:2026-07-22-activate-date-rail-ascending-and-trade-quantity-plan` (user: 把prop plan迁移到active吧) — plan migrated `proposed/` → `active/` at `phase-0:not-started`
- This activation does **not** start Phase 0 and does **not** authorize product implementation
- Implementation start requires a later explicit start/execute instruction after this activation recording
- Local activation commit only; no push/PR/merge/Pages/provider/broker

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
