# Tang Strategy Trade Points And K-line Marker Labels

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan`
- Revision: `v1-proposal-2026-07-21`
- Plan author ID: `grok-plan-author-2026-07-21-trade-points-kline-labels`
- Design reviews: none
- Latest design verdict: none
- Review independence: none
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
- Scope authority: review-only; this proposed plan does not authorize activation, implementation, push, PR, merge, Pages, provider/broker, tracked-DB mutation beyond the single frozen registry display_name edit listed in §3.1, or any remote action

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

### 1.2 Visual evidence

| 证据 | 路径 | SHA-256 | 作用 |
| --- | --- | --- | --- |
| Live cards amount/profit noise | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-trade-card-amount-profit-subtraction.png` | `fb446df9d39de6e3890b573c06338aca4267646330ea341b8813da96b937db90` | OPT-001 现状 |
| Live markers CALL/PUT + trader_id | `docs/optimization/2026-07-21-review-trade-and-kline-session/screenshots/2026-07-21-kline-marker-buysell-trader-nickname.png` | `610e3d74216adf869626310e65a48de4127632f3f48c44256510874483a33559` | OPT-002 现状 |
| Named-batch locked mock | `docs/optimization/2026-07-21-trade-points-and-kline-marker-labels/mockups/trade-points-and-kline-labels.html` | `e5bb2a0557700868ffbabf64ffa3dba4d4a28f2176fa76a127d58e6a740a67e9` | 本计划 UI 方向（cards + markers） |
| Session mock (superset) | `docs/optimization/2026-07-21-review-trade-and-kline-session/mockups/review-trade-and-kline-session.html` | `f2cbec2cf0ae1ee2f292583c40c693adb766a911a4e5f872d9250828d680de6a` | 上下文；仅 OPT-001/002 切片对本计划有约束力 |

Named-batch mock 与 session 截图字节一致（同名 PNG 哈希相同）。

### 1.3 Current repository facts

**Trade cards (`TraderTradeList.jsx`):**

- Meta line uses `outcomeLabel(group)` → `reported X% · calculated Y%` (or subset / `result unknown`).
- Expanded legs render `time | action | qty @ premium | fees {value|?}`.
- Trader title uses `trader.display_name || trader_id` (live `vordin` → `沃德哥`).
- CALL/PUT direction pill and glyph remain direction-owned.

**Markers (`tradeRecords.js` `buildTradeRecordAnnotations`):**

- `marker_label: \`${group.trader_id} ${direction}\`` then optional ` ×N`.
- `void traders` — registry display names are intentionally unused for labels today.
- Shape/color already direction-owned (`triangle_up`/`triangle_down`, `--direction-call` / `--direction-put`).
- Live contract tests pin `marker_label === 'alice CALL ×2'`.

**Registry (`content/traders/index.json`):**

- `trader_id: "vordin"`, `display_name: "沃德哥"`.
- Day files and trade groups keep `trader_id: "vordin"`; no rename of stable id.

**Event actions (live QQQ/SPY day files):** `buy_open`, `sell_partial`, `sell_close` (lowercase snake).

### 1.4 User scope locks

| Decision | Lock |
| --- | --- |
| Card reading path | **Presentation subtraction only** — timestamps + price points; no `$` amounts, no return/PnL `%`, no fees on the card UI path |
| Card CALL/PUT | **Keep** direction pill / glyph / rail (direction remains visual) |
| Card meta | `underlying · trade_date · first_event_time → last_event_time` when both ends exist; otherwise `underlying · trade_date` (no outcome %) |
| Expanded legs | Keep compact rows: `TIME · ACTION · QTY @ PREMIUM`; **drop fees / PnL**. Action may stay schema action or uppercased; do **not** redesign into OPT-005 timeline table / row-click chart nav |
| Marker text | **`{display_name} BUY|SELL`** (+ optional ` ×N`); **never** put CALL/PUT in `marker_label` |
| Marker shape/color | Unchanged — CALL/PUT still own triangle direction and hue |
| BUY/SELL derivation | From `event.action`: any action whose first token (split on `_`) is `buy` → **BUY**; first token `sell` → **SELL**. Unknown/empty → **omit marker** (same as incomplete time) or label `?` only if an event still has complete time — freeze as **omit incomplete action** for empty, and **`?` for non buy/sell first token** only if such events appear in fixtures (current live set is buy_*/sell_* only) |
| Marker grouping | Group key must include action side so BUY and SELL on the same bar do not collapse: `bar_index|trader_id|direction|action_side`. Same-side multiples keep ` ×N` |
| Nickname | UI display name for `vordin` is **`vordinkkk`** via registry `display_name` only. **`trader_id` remains `vordin`**. No day-file rewrite |
| Surfaces | Shared `TraderTradeList` + `buildTradeRecordAnnotations` consumers: **Review + Static + Admin** (+ editor chart markers if they call the same builder) |
| Language | Product chrome English remains as in polish plan; this plan does not re-translate Eligibility/Download |

Rejected for this plan: Eligibility removal (OPT-003), 5m first-paint fix (OPT-004), group span-fit + timeline redesign (OPT-005), Data progressive rail density (OPT-006), backend/API/schema version bumps, Pages/publisher, provider/broker, tracked SQLite rebuild.

### 1.5 Lane 3 classification

Shared Review/Static/Admin presentation + pure annotation builder contract tests + one registry display_name string. Classified Coding Mode **Lane 3** (proposed Exec Plan) because it changes multi-surface shared contracts and must not silently alter export/filter semantics. No market-data, DB rebuild, Pages, or provider work.

## 2. Objective And Success Criteria

### 2.1 Objective

把 Review 交易卡片读路径收成「时间 + 点位」，并把 K 线 trade-record marker 文字从「trader_id + CALL/PUT」换成「display_name + BUY/SELL」，同时用 registry 把 `vordin` 的 UI 名显示为 `vordinkkk`，且不改 `trader_id`、不改 day JSON 结构、不改方向形状/颜色语义。

### 2.2 Success criteria

1. **Cards — no $ / % / fees on reading path:** For every group rendered by `TraderTradeList` on Review/Static/Admin:
   - collapsed meta does **not** contain `$`, `%`, `reported`, `calculated`, `net`, or `return` outcome strings;
   - expanded event rows do **not** render fees or PnL;
   - rows still show time (HH:MM from `occurred_at`), action, and `quantity @ premium` (unknowns may stay `?`).
2. **Cards — direction retained:** CALL/PUT pill + glyph + direction rail classes remain.
3. **Cards — time span meta:** When a group has ≥1 complete event times, meta includes first→last `HH:MM → HH:MM` (local slice of `occurred_at` as today). Empty legs keep `underlying · trade_date` only.
4. **Markers — label shape:** `buildTradeRecordAnnotations` produces `marker_label` matching `` `${displayName} ${BUY|SELL}` `` with optional ` ×N`, where `displayName = trader.display_name || trader_id`.
5. **Markers — no CALL/PUT in label:** Production annotation builder path must not put `CALL` or `PUT` inside `marker_label` (direction remains in `direction` / shape / color fields).
6. **Markers — traders map used:** Stop `void traders`; resolve display name from the traders list / registry map.
7. **Nickname:** After implementation, registry shows `vordin.display_name === "vordinkkk"`; chips/cards/markers that use `display_name` show `vordinkkk` for that trader. `trader_id` in content trades remains `vordin`.
8. **Grouping:** BUY and SELL events on the same bar index for the same trader/direction are **separate** markers; same BUY (or same SELL) multiples may group with ` ×N`.
9. **Contracts preserved:** Eligibility filtering, B-chip selection, export download contents (`buildTradeRecordDownloads` columns may still include return/fees fields — export is not the card reading path), density CSS, Eligibility/Download chrome from polish plan, direction color tokens.
10. **Tests/builds:** `npm run test:trade-records` green with updated marker contracts; normal + static Vite builds green; `python scripts/check-project-harness.py --root . --profile auto` green; `git diff --check` clean on task paths.
11. **Screenshots:** §2.3 matrix under `output/` (untracked).

### 2.3 Frozen visual acceptance matrix

| # | Surface | Viewport | Fixture | Required coverage |
| --- | --- | --- | --- | --- |
| V1 | Interactive Review trade cards | desktop `1672x941` | QQQ `2026-07-17` | 沃德哥→vordinkkk card(s); meta without %/$; ≥1 expanded legs without fees |
| V2 | Interactive Review K-line markers | desktop `1672x941` | QQQ `2026-07-17` | Visible marker text `vordinkkk BUY` and/or `vordinkkk SELL` (×N ok); no `CALL`/`PUT` in marker text |
| V3 | Static Review (shared list + chart if present) | desktop `1672x941` | QQQ `2026-07-17` | Same card subtraction + marker label language as V1/V2 |

Compare against §1.2 live screenshots and named-batch mock.

### 2.4 Frozen verification carrier matrix

| Carrier ID | Tool | Proves | Must not claim |
| --- | --- | --- | --- |
| **N-Marker-label** | Node `npm run test:trade-records` | Pure `buildTradeRecordAnnotations`: display_name + BUY/SELL; ×N; no CALL/PUT in label; BUY≠SELL grouping | Browser paint |
| **N-Action-map** | Node same suite | `buy_open`→BUY, `sell_partial`/`sell_close`→SELL (and any exported pure helper) | UI |
| **N-Card-source** | Node source inspection of `TraderTradeList.jsx` | No `outcomeLabel` % path on card; no fees span in legs; meta uses time span helper | Visual polish judgment |
| **N-Registry-vordin** | Node or trivial file assert in tests / phase evidence | `content/traders/index.json` has `vordin` → `vordinkkk`; `trader_id` still `vordin` | Day-file rewrites |
| **N-Pure-filter-export** | Existing pure tests | Eligibility/export unchanged | Marker visuals |
| **V1–V3** | Screenshots under `output/` | Visual acceptance | Interaction semantics beyond paint |

No mandatory Playwright matrix for this plan: acceptance is pure-function + source contracts + three screenshots. If implementation review later demands a click receipt, add it as a foldback rather than inventing ceremony now.

## 3. Constraints And Invariants

### 3.1 Frozen implementation manifest (exact paths)

**Modify (implementation):**

1. `frontend/src/features/review/tradeRecords.js` — marker label uses display_name + BUY/SELL; action-side grouping; export pure helper(s) as needed; **do not** change filter/export column semantics except if a shared helper rename is required (keep download fields).
2. `frontend/src/features/review/TraderTradeList.jsx` — remove outcome % meta and fees row; add first→last time span meta; keep CALL/PUT chrome and Show/Hide legs.
3. `frontend/src/features/review/tradeRecords.test.js` — update marker label expectations; add action mapping + grouping cases; pin card source contracts if asserted here (or in `reviewWorkspace.test.js`).
4. `frontend/src/features/review/reviewWorkspace.test.js` — only if existing source pins reference outcome/fees/marker strings that this plan changes.
5. `content/traders/index.json` — **only** change `vordin.display_name` from `沃德哥` to `vordinkkk`. No other registry fields; no trade day files.

**Lifecycle / evidence (this proposal package and later transitions):**

6. Optimization records + `docs/optimization/index.md` status/lifecycle links for promoted OPT-001/002 surfaces.
7. `PROGRESS.md` / `HANDOFF.md` state blocks.
8. Plan file + `docs/exec-plans/{proposed,active,completed,reviews}/index.md` + `docs/exec-plans/roadmap.md` as lifecycle requires.
9. Screenshots under `output/` (untracked; do not sweep into commits).

**Out of manifest / must not change:**

- Backend, API routes, tracked SQLite, seed market data, Pages workflows, daily runbook, provider/broker.
- `content/trades/*.json` day payloads (no trader_id renames, no field deletes).
- Eligibility UI, Download four-file behavior, B-chip threshold, direction color tokens, density px table under `.dr-sidebar`.
- OPT-003…006 work items.
- Kline engine timeframe/viewport code (OPT-004).

### 3.2 Unrelated dirty paths to preserve

At proposal time, untracked `output/local-acceptance/` and `output/playwright/trade-panel-polish-20260721/` are user/evidence-owned. Do not stage, delete, or mix them into this lifecycle commit.

### 3.3 Safety / data boundaries

- Registry edit is display metadata only; projection/admin PUT already treat `display_name` as mutable UI label.
- No `--allow-date-loss`, no DB promote, no content trade mutation.
- Export CSV/JSON may still contain return/fees columns for analysis; card UI is the subtraction surface.

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: plan Active + explicit implementation-start instruction (not granted by this proposal).
- Work: confirm HEAD baseline; re-hash §1.2 evidence; note current green `test:trade-records` marker pins; freeze visual fixture **QQQ `2026-07-17`**.
- Verification: list §3.1 paths; confirm no OPT-003…006 leakage in branch plan text.
- Exit gate: `phase-0-exit` with baseline note in phase evidence (may live in plan appendix or untracked `output/`).

### Phase 1 — Implementation

- Entry gate: `phase-0-exit`.
- Work: implement §2.2 items 1–8 on manifest paths 1–5 only.
- Verification: **N-*** carriers green; normal + static builds; harness auto; V1–V3 screenshots captured under `output/`.
- Exit gate: `phase-1-exit`.

### Phase 2 — Closeout Package

- Entry gate: `phase-1-exit`.
- Work: implementation-review packet (screenshots + command receipts); independent implementation review; on `accept`, migrate plan to `completed/` under separate closeout authority rules in operating-modes; back-link OPT records to completed plan.
- Verification: implementation review `accept`; indexes/roadmap/state blocks agree.
- Exit gate: `closed` after completed migration.

## 5. Evidence And Commit Plan

- Baseline commands: `python scripts/check-operating-modes.py --root .`; `python scripts/check-project-harness.py --root . --profile auto`
- Focused checks (implementation): `cd frontend && npm run test:trade-records`; `npm run build`; `npm run build:static-reviews` (or project’s static script as used by prior plans)
- Full checks: harness auto; `git diff --check` on staged paths
- Expected state/handoff updates: Proposed now; Active only after matching design approve + user activation instruction
- Task-owned commit paths for **this proposal step**:
  - `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`
  - `docs/exec-plans/proposed/index.md`
  - `docs/exec-plans/roadmap.md`
  - `docs/optimization/index.md`
  - `docs/optimization/2026-07-21-trade-points-and-kline-marker-labels/2026-07-21-trade-points-and-kline-marker-labels.md`
  - `docs/optimization/2026-07-21-review-trade-and-kline-session/2026-07-21-review-trade-and-kline-session.md`
  - `docs/optimization/2026-07-21-trade-card-simplify-points-only/2026-07-21-trade-card-simplify-points-only.md` (if present and still linked)
  - `docs/optimization/2026-07-21-kline-marker-action-and-trader-nickname/2026-07-21-kline-marker-action-and-trader-nickname.md` (if present and still linked)
  - `PROGRESS.md`
  - `HANDOFF.md`
- No-commit condition: none for a complete proposal package

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan/`
- Required design verdict: `approve` on **exact** revision `v1-proposal-2026-07-21` (or a later foldback revision id)
- Required user approval for activation: explicit instruction after matching approve (e.g. move prop plan to active)
- Activation is a separate lifecycle change before implementation
- Implementation start requires a later explicit start/execute instruction after activation recording
- Creating this durable plan is committed locally by default under `docs/operating-modes.md` §2; no push/PR/remote authority

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
