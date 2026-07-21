# Tang Strategy Trade Points And K-line Marker Labels

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan`
- Revision: `v2-review-foldback-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-trade-points-kline-labels`
- Design reviews: ../reviews/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan/review-001.md@revise@v1-proposal-2026-07-21
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
- Optimization source: `docs/optimization/2026-07-21-trade-points-and-kline-marker-labels/2026-07-21-trade-points-and-kline-marker-labels.md` (user-named; superseded pointer) with authoritative detail in session batch OPT-001/OPT-002 `docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md`
- Proposal baseline: `codex/project-harness@6c62c2b1ff8314da36a5f2dad57a81451c720edb`
- Scope authority: review-only; this proposed plan does not authorize activation, implementation, push, PR, merge, Pages, provider/broker, publication, or any remote action. A later authorized implementation of this revision may perform **one local governed registry display_name mutation** only through the frozen atomic content→SQLite projection path in §3.1 / §3.3 (no provider, publication, or remote authority).

## 1. Context And Evidence

### 1.1 Proposal provenance

用户点名 optimization 文档 `docs/optimization/2026-07-21-trade-points-and-kline-marker-labels/` 并要求 **转换成 prop plan**。该文件本身是 session 合并后的 `superseded` 指针（OPT-001 + OPT-002）；权威正文与证据已并入 session 批次：

| 来源 | OPT | 摩擦点 |
| --- | --- | --- |
| Named batch (superseded pointer) + session | **OPT-001** | 交易卡片 / expanded legs 仍展示金额、盈收 %、fees 等噪声；用户要做减法，只留时间点位 |
| Named batch (superseded pointer) + session | **OPT-002** | K 线 marker 文字重复 CALL/PUT（形状+颜色已表达方向）；显示 raw `trader_id` / 中文 `沃德哥`，而非英文昵称 `vordinkkk`；缺少 BUY/SELL |

同一 session 的 OPT-003…006（Eligibility 移除、5m 视口、group span+timeline、Data rail 拉伸）**不在本计划范围**，保持 `recorded`，避免把相邻观察扩成大杂烩。

相关已完成边界（本计划不得回退）：

- Trade panel visual polish（Eligibility / Download / card chrome）— completed
- Trade card density under `.dr-sidebar` — completed
- Direction colors CALL/PUT tokens — completed fusion plan

### 1.2 Review foldback closure map

#### review-001 closure (v1 → v2)

Independent `review-001` returned `revise/high` against exact revision `v1-proposal-2026-07-21`. Revision `v2-review-foldback-2026-07-21` folds every finding:

| Severity | Finding (summary) | V2 closure |
| --- | --- | --- |
| P1 | JSON-only `content/traders/index.json` edit forbids tracked SQLite update and would drift from DB-first projection (`PUT /api/admin/traders` → `handle_trader_registry_admin_write` + `_sync_trade_projection`) | §1.4 Nickname + §3.1 + §3.3 freeze **one existing atomic registry-write + candidate trade projection** route. Manifest includes both `content/traders/index.json` and `data/sqlite/tang_strategy_live_extended.db`. Prove both surfaces resolve `vordin → vordinkkk`; fail closed leaves current DB unchanged. Local governed mutation only; no provider/publication/remote. |
| P2 | Card first→last meta not executable; `N-Card-source` source scan can pass without correct cross-leg chronology | §1.4 + §2.2 + §2.4 freeze pure helper `groupEventTimeRange` over **all legs’ complete `occurred_at`** (chronological min/max, independent of array order). Exact zero / one / two-or-more renderings. Node pure tests cover multi-leg, out-of-order fixtures, incomplete times. Source scan limited to negative outcome/fees pins. |
| P2 | Only `marker_label` changed; tooltip `title` still raw `trader_id CALL action`; action fallback fixture-dependent while schema has four actions | §1.4 + §2.2 + §2.4 freeze **all user-visible annotation text** (`marker_label` **and** `title`) to display-name + BUY/SELL vocabulary. Explicit map of all four schema actions; unrecognized/empty → **omit** marker (fail closed, no `?`). Node cases for four actions, missing/unknown, same-bar BUY/SELL separation, same-side `×N`, display-name fallback, absence of CALL/PUT and unnecessary raw id from both fields. |

`review-001` is append-only prior-revision evidence and **cannot approve v2**. Next gate is independent design review of exact revision `v2-review-foldback-2026-07-21`.

### 1.3 Visual evidence

| 证据 | 路径 | SHA-256 | 作用 |
| --- | --- | --- | --- |
| Live cards amount/profit noise | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-card-amount-profit-subtraction.png` | `fb446df9d39de6e3890b573c06338aca4267646330ea341b8813da96b937db90` | OPT-001 现状 |
| Live markers CALL/PUT + trader_id | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png` | `610e3d74216adf869626310e65a48de4127632f3f48c44256510874483a33559` | OPT-002 现状 |
| Named-batch locked mock | `docs/optimization/2026-07-21-trade-points-and-kline-marker-labels/mockups/trade-points-and-kline-labels.html` | `e5bb2a0557700868ffbabf64ffa3dba4d4a28f2176fa76a127d58e6a740a67e9` | 本计划 UI 方向（cards + markers） |
| Session mock (superset) | `docs/optimization/2026-07-21-review-trade-and-kline-session/mockups/review-trade-and-kline-session.html` | `f2cbec2cf0ae1ee2f292583c40c693adb766a911a4e5f872d9250828d680de6a` | 上下文；仅 OPT-001/002 切片对本计划有约束力 |

Named-batch mock 与 session 截图字节一致（同名 PNG 哈希相同）。

### 1.4 Current repository facts

**Trade cards (`TraderTradeList.jsx`):**

- Meta line uses `outcomeLabel(group)` → `reported X% · calculated Y%` (or subset / `result unknown`).
- Expanded legs render `time | action | qty @ premium | fees {value|?}`.
- Trader title uses `trader.display_name || trader_id` (live `vordin` → `沃德哥`).
- CALL/PUT direction pill and glyph remain direction-owned.
- Backend chronology is guaranteed **within each leg**, not as a pre-sorted cross-leg group array.

**Markers (`tradeRecords.js` `buildTradeRecordAnnotations`):**

- `marker_label: \`${group.trader_id} ${direction}\`` then optional ` ×N`.
- `title: \`${group.trader_id} ${direction} ${event.action}\`` — user-visible in K-line annotation tooltip via `UnifiedKlineEngine` / engine (`title` field).
- `void traders` — registry display names are intentionally unused for labels today.
- Shape/color already direction-owned (`triangle_up`/`triangle_down`, `--direction-call` / `--direction-put`).
- Live contract tests pin `marker_label === 'alice CALL ×2'`.

**Registry and projection:**

- Canonical registry file: `content/traders/index.json` — live `trader_id: "vordin"`, `display_name: "沃德哥"`.
- Admin path: `PUT /api/admin/traders` → `handle_trader_registry_admin_write(..., after_replace=_sync_trade_projection)`.
- `_sync_trade_projection` candidate-projects the complete normalized trade repository, then atomically promotes tracked SQLite on success.
- Tracked DB stores trader display names in `traders`; views such as `v_trade_group_performance` expose them. Day files keep `trader_id: "vordin"`.

**Event actions (schema enum):** exactly `buy_open`, `buy_add`, `sell_partial`, `sell_close` (`content/schemas/trades-day.schema.json`). Live QQQ/SPY days currently exercise `buy_open`, `sell_partial`, `sell_close`.

### 1.5 User scope locks (v2; supersedes ambiguous v1 bullets)

| Decision | Lock |
| --- | --- |
| Card reading path | **Presentation subtraction only** — timestamps + price points; no `$` amounts, no return/PnL `%`, no fees on the card UI path |
| Card CALL/PUT | **Keep** direction pill / glyph / rail (direction remains visual) |
| Card meta time range | Pure helper over **all complete `occurred_at` across every leg** (chronological min/max; array order irrelevant). Render: **0** known → `underlying · trade_date`; **1** known → `underlying · trade_date · HH:MM`; **≥2** known → `underlying · trade_date · HH:MM → HH:MM`. Incomplete times ignored for the range |
| Expanded legs | Keep compact rows: `TIME · ACTION · QTY @ PREMIUM`; **drop fees / PnL**. Action may stay schema action or uppercased; do **not** redesign into OPT-005 timeline table / row-click chart nav |
| User-visible annotation text | **`marker_label` and `title`** both use `` `${displayName} ${BUY\|SELL}` `` (+ ` ×N` only on `marker_label` when grouped). **Never** put CALL/PUT in either field. Shape/color remain direction-owned |
| BUY/SELL derivation | **Exact** schema map only: `buy_open`/`buy_add` → **BUY**; `sell_partial`/`sell_close` → **SELL**. Empty or any other action → **omit** that event’s marker (fail closed). No `?` label |
| Marker grouping | Group key includes action side: `bar_index|trader_id|direction|action_side`. BUY and SELL on the same bar stay separate; same-side multiples keep ` ×N` on `marker_label` |
| Nickname / registry write | UI name for `vordin` is **`vordinkkk`**. **`trader_id` remains `vordin`**. No day-file rewrite. Mutation uses **existing atomic registry write + candidate SQLite trade projection** so **both** canonical JSON and tracked DB resolve `vordin → vordinkkk` |
| Surfaces | Shared `TraderTradeList` + `buildTradeRecordAnnotations` consumers: **Review + Static + Admin** (+ editor chart markers if they call the same builder) |
| Language | Product chrome English remains as in polish plan; this plan does not re-translate Eligibility/Download |

Rejected for this plan: Eligibility removal (OPT-003), 5m first-paint fix (OPT-004), group span-fit + timeline redesign (OPT-005), Data progressive rail density (OPT-006), schema version bumps, Pages/publisher, provider/broker, day-file rewrites, JSON-only registry edit that leaves SQLite stale, tooltip left on raw `trader_id`/CALL/PUT/`buy_open` text.

### 1.6 Lane 3 classification

Shared Review/Static/Admin presentation + pure annotation/time helpers + **one local governed registry display_name mutation** through the existing atomic content→SQLite projection path. Classified Coding Mode **Lane 3** (proposed Exec Plan). No market-data fetch, provider/broker, Pages publication, or day JSON rewrites. No new backend API; reuse the existing admin registry write / projection machinery (callable via the admin PUT path or the same service functions offline under implementation authority).

## 2. Objective And Success Criteria

### 2.1 Objective

把 Review 交易卡片读路径收成「时间 + 点位」，并把 K 线 trade-record **所有用户可见标注文字**（chart label 与 hover title）从「trader_id + CALL/PUT + raw action」换成「display_name + BUY/SELL」，同时通过 **原子 registry 写入 + candidate SQLite projection** 把 `vordin` 的 UI 名更新为 `vordinkkk`，且不改 `trader_id`、不改 day JSON 结构、不改方向形状/颜色语义。

### 2.2 Success criteria

1. **Cards — no $ / % / fees on reading path:** For every group rendered by `TraderTradeList` on Review/Static/Admin:
   - collapsed meta does **not** contain `$`, `%`, `reported`, `calculated`, `net`, or `return` outcome strings;
   - expanded event rows do **not** render fees or PnL;
   - rows still show time (HH:MM from `occurred_at`), action, and `quantity @ premium` (unknown quantity/premium may stay `?`).
2. **Cards — direction retained:** CALL/PUT pill + glyph + direction rail classes remain.
3. **Cards — executable time-range meta:** A pure exported helper (name may be `groupEventTimeRange` or equivalent) computes chronological min/max of complete `occurred_at` across **all legs**. Rendering matches §1.5 zero / one / two-or-more rules. Proven by **N-Card-time-range**, not by JSX string presence alone.
4. **Markers — label and title shape:** `buildTradeRecordAnnotations` produces both `marker_label` and `title` matching `` `${displayName} ${BUY|SELL}` `` (with optional ` ×N` only on `marker_label`), where `displayName = trader.display_name || trader_id`.
5. **Markers — no CALL/PUT / raw direction words in user-visible text:** Neither `marker_label` nor `title` contains `CALL` or `PUT`. Direction remains only in `direction` / shape / color fields.
6. **Markers — traders map used:** Stop `void traders`; resolve display name from the traders list / registry map.
7. **Markers — fail-closed actions:** Only the four schema actions emit markers; unknown/empty actions are omitted. Proven by **N-Action-map** including missing/unknown cases.
8. **Nickname dual surface:** After authorized implementation, **both**:
   - `content/traders/index.json` has `vordin.display_name === "vordinkkk"`;
   - tracked SQLite `traders` (and any view used for display that reads trader display name, e.g. join to `traders` / `v_trade_group_performance`) resolves `vordin` → `vordinkkk`.
   `trader_id` in content trades remains `vordin`. Mutation used the atomic registry-write + projection path; a failed projection leaves the **current** tracked DB unchanged.
9. **Grouping:** BUY and SELL events on the same bar index for the same trader/direction are **separate** markers; same BUY (or same SELL) multiples may group with ` ×N` on `marker_label`.
10. **Contracts preserved:** Eligibility filtering, B-chip selection, export download contents (`buildTradeRecordDownloads` columns may still include return/fees fields — export is not the card reading path), density CSS, Eligibility/Download chrome from polish plan, direction color tokens, market-day / strategy / teaching / bar / non-target trade facts in the projected DB.
11. **Tests/builds:** `npm run test:trade-records` green with updated marker/time/action contracts; normal + static Vite builds green; `python scripts/check-project-harness.py --root . --profile auto` green; SQLite integrity + foreign-key checks green after the registry projection; `git diff --check` clean on task paths.
12. **Screenshots:** §2.3 matrix under `output/` (untracked).

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review trade cards | desktop `1672x941` | QQQ `2026-07-17` | vordinkkk card(s); meta without %/$; time span or single time when events exist; ≥1 expanded legs without fees |
| V2 | Interactive Review K-line markers | desktop `1672x941` | QQQ `2026-07-17` | Visible marker text `vordinkkk BUY` and/or `vordinkkk SELL` (×N ok); no `CALL`/`PUT` in marker text; hover title uses same BUY/SELL vocabulary (no raw `buy_open` / CALL / PUT) |
| V3 | Static Review (shared list + chart if present) | desktop `1672x941` | QQQ `2026-07-17` | Same card subtraction + marker label language as V1/V2 |

Compare against §1.3 live screenshots and named-batch mock.

### 2.4 Frozen verification carrier matrix

| Carrier ID | Tool | Proves | Must not claim |
| --- | --- | --- | --- |
| **N-Marker-label** | Node `npm run test:trade-records` | Pure `buildTradeRecordAnnotations`: display_name + BUY/SELL on **both** `marker_label` and `title`; ×N on label; no CALL/PUT in either; BUY≠SELL grouping; display-name fallback; no raw `vordin` when display_name present | Browser paint |
| **N-Action-map** | Node same suite | Exact map of `buy_open`/`buy_add`→BUY and `sell_partial`/`sell_close`→SELL; empty/unknown omit; no `?` path | UI |
| **N-Card-time-range** | Node pure helper tests | Cross-leg min/max; multi-leg; deliberately out-of-order arrays; incomplete times ignored; zero/one/two-or-more results | JSX aesthetics |
| **N-Card-source** | Node source inspection of `TraderTradeList.jsx` | Negative only: no outcome `%` / fees span on the card reading path; consumes the pure time-range helper | Time-range correctness (use **N-Card-time-range**) |
| **N-Registry-dual** | Implementation evidence + focused checks | Canonical JSON **and** tracked SQLite resolve `vordin → vordinkkk`; integrity/FK pass; non-target inventory preserved | Day-file rewrites; remote/provider |
| **N-Pure-filter-export** | Existing pure tests | Eligibility/export unchanged | Marker visuals |
| **V1–V3** | Screenshots under `output/` | Visual acceptance including tooltip vocabulary on V2 where hover is captured or noted | Interaction beyond paint |

No mandatory Playwright matrix for this plan: acceptance is pure-function + dual-surface registry evidence + three screenshots. If implementation review later demands a browser tooltip receipt, add it as a foldback rather than inventing ceremony now.

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/tradeRecords.js` — action map helper; marker `marker_label` + `title` use display_name + BUY/SELL; action-side grouping; pure `groupEventTimeRange` (or equivalent) for card meta; **do not** change filter/export column semantics except shared pure helpers.
2. `frontend/src/features/review/TraderTradeList.jsx` — remove outcome % meta and fees row; render meta via pure time-range helper; keep CALL/PUT chrome and Show/Hide legs.
3. `frontend/src/features/review/tradeRecords.test.js` — **N-Marker-label**, **N-Action-map**, **N-Card-time-range** (and card source negatives if co-located).
4. `frontend/src/features/review/reviewWorkspace.test.js` — only if existing source pins reference outcome/fees/marker strings that this plan changes.
5. `content/traders/index.json` — `vordin.display_name` becomes `vordinkkk` **only as the product of the atomic registry-write path** (not a lone hand-edit that skips projection). No other registry fields; no trade day files.
6. `data/sqlite/tang_strategy_live_extended.db` — updated **only** via the existing candidate-first trade projection that runs after successful registry replace (`_sync_trade_projection` / same machinery as admin PUT). Failure leaves the current DB file unchanged.

**Implementation write path (frozen):**

7. Use the repository’s existing atomic route: full-registry validation → atomic replace of `content/traders/index.json` → candidate project complete normalized trade repository → integrity/FK + non-shrink gates → atomic promote of tracked SQLite. Prefer calling the same service entry used by `PUT /api/admin/traders` (`handle_trader_registry_admin_write` with `after_replace=_sync_trade_projection`), either through a local admin-authenticated request or an offline invocation of those functions under implementation authority. **Forbidden:** editing only the JSON file, or hand-editing the SQLite blob without the candidate/promote path.

**Lifecycle / evidence (this revision package and later transitions):**

8. Optimization records + `docs/optimization/index.md` status/lifecycle links for promoted OPT-001/002 surfaces.
9. `PROGRESS.md` / `HANDOFF.md` state blocks.
10. Plan file + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + `docs/exec-plans/roadmap.md` as lifecycle requires.
11. Screenshots under `output/` (untracked; do not sweep into commits).

**Out of manifest / must not change:**

- New backend APIs, schema enum changes, seed market-data history, Pages workflows, daily runbook, provider/broker.
- `content/trades/*.json` day payloads (no trader_id renames, no field deletes).
- Eligibility UI, Download four-file behavior, B-chip threshold, direction color tokens, density px table under `.dr-sidebar`.
- OPT-003…006 work items.
- Kline engine timeframe/viewport code (OPT-004) — tooltip **text content** is fixed by annotation builder fields; do not rework engine layout for this plan.

### 3.2 Unrelated dirty paths to preserve

Untracked `output/local-acceptance/` and `output/playwright/trade-panel-polish-20260721/` are user/evidence-owned. Do not stage, delete, or mix them into this lifecycle commit.

### 3.3 Safety / data boundaries

- Registry mutation is **display metadata only** (`display_name`), applied through the **existing** atomic content + projection path.
- Candidate-first: validate full registry + trade repository; preserve market-day, strategy, teaching, bar, dataset, and non-target trade facts; integrity + foreign-key pass required; projection failure rolls back / leaves current tracked DB unchanged.
- No `--allow-date-loss`. No provider fetch. No Pages publish. No push/PR/remote.
- Export CSV/JSON may still contain return/fees columns for analysis; card UI is the subtraction surface.

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: plan Active + explicit implementation-start instruction (not granted by this proposal).
- Work: confirm HEAD baseline; re-hash §1.3 evidence; note current green `test:trade-records` marker pins; freeze visual fixture **QQQ `2026-07-17`**; record current SQLite integrity/FK and `vordin` display name in both JSON and DB.
- Verification: list §3.1 paths; confirm atomic write path is the only registry mutation route; confirm no OPT-003…006 leakage.
- Exit gate: `phase-0-exit` with baseline note in phase evidence (may live in plan appendix or untracked `output/`).

### Phase 1 — Implementation

- Entry gate: `phase-0-exit`.
- Work: implement §2.2 items 1–10 on manifest paths 1–6 using the frozen write path in §3.1 item 7.
- Verification: **N-*** carriers green including **N-Registry-dual**; normal + static builds; harness auto; SQLite integrity/FK; V1–V3 screenshots under `output/`.
- Exit gate: `phase-1-exit`.

### Phase 2 — Closeout Package

- Entry gate: `phase-1-exit`.
- Work: implementation-review packet (screenshots + command receipts + dual-surface registry proof); independent implementation review; on `accept`, migrate plan to `completed/` under separate closeout authority rules in operating-modes; back-link OPT records to completed plan.
- Verification: implementation review `accept`; indexes/roadmap/state blocks agree.
- Exit gate: `closed` after completed migration.

## 5. Evidence And Commit Plan

- Baseline commands: `python scripts/check-operating-modes.py --root .`; `python scripts/check-project-harness.py --root . --profile auto`
- Focused checks (implementation): `cd frontend && npm run test:trade-records`; `npm run build`; static build as used by prior plans; SQLite integrity/FK after projection; prove JSON + DB `vordin → vordinkkk`
- Full checks: harness auto; `git diff --check` on staged paths
- Expected state/handoff updates: Proposed now at v2 awaiting matching design review; Active only after matching design approve + user activation instruction
- Task-owned commit paths for **this plan-revision step**:
  - `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`
  - `docs/exec-plans/proposed/index.md`
  - `docs/exec-plans/roadmap.md`
  - `docs/exec-plans/reviews/index.md`
  - `PROGRESS.md`
  - `HANDOFF.md`
- No-commit condition: none for a complete revision package

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan/`
- Required design verdict: `approve` on **exact** revision `v2-review-foldback-2026-07-21` (or a later foldback revision id)
- `review-001` remains append-only evidence against v1 and **cannot** approve v2
- Required user approval for activation: explicit instruction after matching approve (e.g. move prop plan to active)
- Activation is a separate lifecycle change before implementation
- Implementation start requires a later explicit start/execute instruction after activation recording
- Revising this durable plan is committed locally by default under `docs/operating-modes.md` §2; no push/PR/remote authority

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
