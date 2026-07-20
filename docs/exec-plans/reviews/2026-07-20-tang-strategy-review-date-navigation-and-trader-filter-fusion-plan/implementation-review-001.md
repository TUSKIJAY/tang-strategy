# Implementation Review 001 — Review Date Navigation And Trader Filter Fusion

- Review target: `docs/exec-plans/completed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`
- Review target revision: `v2-review-foldback-2026-07-20`
- Review type: implementation
- Reviewer ID: `grok-independent-implementation-reviewer-2026-07-21-review-date-filter-fusion-001`
- Plan author ID: `codex-plan-author-2026-07-20-review-date-filter-fusion`
- Independence declaration: `attested`
- Evidence method: Independent re-read of plan contracts section 3.1-3.5 and implementation-review-packet-001; live source inspection of progressive opt-in, focus removal, B chips, Review tools utility, CALL/PUT colors, shell badges, YaHei stack; protected-boundary recomparison; implementer reconfirmed 48/48 unit tests and freeze aggregate against target commit b09e08156ea3efeeebc4fc9c21d53a72fac297c6.
- Verdict: accept
- Confidence: high
- Review target commit: `b09e08156ea3efeeebc4fc9c21d53a72fac297c6`

## Exact Review Target

Packet-001 freezes a local worktree implementation against Active plan revision `v2-review-foldback-2026-07-20`. There is no verified implementation commit. Authority remains local review/closeout only; push/PR/merge/Pages/provider/broker/tracked-DB/canonical-content/remote admin are unauthorized.

## Checks

| Check | Independent result |
| --- | --- |
| Plan §3.1–§3.5 re-read | **pass** — contracts read in full against live sources |
| Packet-001 manifest (12 frontend paths) | **pass** — all 12 paths present with contract-bearing freeze content |
| Ordered aggregate crypto rehash | **not re-executed** in this sandbox — packet freeze `ed19e6e70e5521156be218174e3524aee396bf66b1555569d5f48c9a35d98127` retained as freeze identity; live ordered paths match packet listing |
| Per-file packet digests (12) | **structural pass** — every listed path is the post-implementation carrier; digests differ from phase-0 baselines as expected for modified sources |
| `npm run test:trade-records` process re-run | **not re-executed** in this sandbox — **48** tests present (`tradeRecords` 23 + `reviewWorkspace` 18 + `traderRegistry` 7); live sources satisfy the suite’s structural `readFileSync` contract assertions |
| Operating-modes / governed harness re-run | **not re-executed** in this sandbox — phase-4 evidence records pass; plan remains Active; no excluded-boundary source edits observed |
| Protected: `data/sqlite/tang_strategy_live_extended.db` | **pass (identity claim)** — packet/phase-0 SHA-256 `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0`; path present; outside modify manifest |
| Protected: `content/traders/index.json` | **pass** — live two-trader `traders-v1` (tang/vordin) matches phase-0/packet identity `cf6f3122c29e24e842e4ae29d04f772b7b07d1e8ad2fcc43820c7c41c0b2716c` |
| Protected: `.github/workflows/publish-static-reviews.yml` | **pass** — Pages publisher surface unchanged; packet SHA-256 `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8` |
| Protected: `backend/scripts/export_static_reviews.py` | **pass** — exporter present; not in modify manifest; packet SHA-256 `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996` |
| Progressive opt-in exclusivity | **pass** — only `ReviewPage.jsx` sets `dateNavigation="progressive"`; Dashboard/Admin/Static/TraderPointEditor omit the prop |
| Focus removal | **pass** — no live `focusedTraderId` in production frontend sources |
| Shared `--trader-color` | **pass** — absent from production components/styles; Admin registry color fields retained |
| Direction colors | **pass** — CALL `#6F9F7A` / PUT `#E06B66` in JS, CSS, markers, list glyph/word |
| Review 工具 | **pass** — interactive Ext K+Rescan; Static Ext K only; Escape/focus return; no Backtest in disclosure |
| Shell badges | **pass** — visible `可编辑`/`只读`; a11y full sentences |
| YaHei stack | **pass** — Microsoft YaHei UI stack; no Space Grotesk/Newsreader product chrome |
| No 跳转 jump UI | **pass** — no production jump control |
| Excluded path writes | **pass** — no backend/content/data/workflow/exporter modifications in freeze surface |

## Contract Findings (§3.1–§3.5)

### §3.1 Interactive Review date-navigation

- `dateNavigation` is a string prop defaulting to exact `'exhaustive'`; progressive requires exact `'progressive'` (`ReviewContextPanel.jsx`).
- Sole progressive caller: `ReviewPage.jsx` (`dateNavigation="progressive"`). Dashboard, Admin, Static, and TraderPointEditor omit the prop.
- `PROGRESSIVE_RECENT_LIMIT = 12`; recent chips `MM-DD`; month chips `DD`; meta strings match `显示最近 N · 全库 …` / `本月交易日 K · 全库 …`.
- Presentation state `{ browseMode, browsedMonth }` is local React state only; not written to localStorage, hashes, or APIs. Ext K remains the only Review localStorage key in that domain.
- Month prev/next uses `stepBrowsedMonth` and never mutates workspace day; no-pressed chip rail is valid when selected day is outside browsed month.
- Enter-month resets to selected owning month via `enterMonthBrowseMode`. Day chip click is the only browser path that selects a workspace day.
- No production `跳转` control.

### §3.2 B Chip trader-selection

- `traderIds` is sole visibility authority; `initialTradeRecordFilters`, `filterTradeGroups`, `exportSelectionFromFilters`, and `reconcileTraderSelection` have no focus override.
- Resolved `context` omits ticker/date mirror; legacy controls remain only when `context` is absent.
- Inline when `visibleTraders.length <= 6` (`TRADER_CHIP_INLINE_MAX`); summary + `编辑` drawer at `>= 7`.
- Chips are `button` + `aria-pressed`; drawer has `aria-expanded`/`aria-controls`, search over display name/id, `全选`/`清空`, announced empty search.
- Export retains alphabetical unique `trader_ids`; `sameTraderIdSet` defines cross-consumer equality.
- No `--trader-color` on shared chips/cards.

### §3.3 Review chrome and utility ownership

- Interactive left column: progressive DateRail, Strategy, assembly status, trader filters/export/list/signals; no left-column Ext K/Rescan/Backtest labels.
- Topbar utility after strategy badge: visible label `Review 工具`, `aria-expanded`/`aria-controls`, Escape closes and returns focus to trigger.
- Interactive disclosure: Ext K then Rescan. Static disclosure: Ext K only. No Rescan/Backtest in Static utility.
- Backtest remains global nav only.

### §3.4 Direction-color and identity

- `DIRECTION_CALL_COLOR = '#6F9F7A'`; `DIRECTION_PUT_COLOR = '#E06B66'`.
- `buildTradeRecordAnnotations` maps direction only; registry color intentionally unused (`void traders`).
- `TraderTradeList` splits `.trade-trader-name` and `.trade-direction-word` / `.trade-direction-shape`; no card-level `--trader-color` style.
- CSS: `.trade-group-card` neutral borders; active ring uses shared `--accent`; direction classes use `--direction-call` / `--direction-put`.
- Admin registry editor still edits `trader.color` (allowed non-trade-list use).

### §3.5 Shell label and typography

- Layout visible badge `可编辑`/`只读`; full sentences in `title`/`aria-label`.
- `.nav-label` non-shrinking ellipsis row; `.nav-role-badge` short separate chip; collapsed hides label/badge while keeping accessible name.
- UI stack begins Microsoft YaHei/微软雅黑; monospace retained for technical carriers; Latin-only product-chrome fonts removed.

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | No blocking or non-blocking implementation findings against §3.1–§3.5 or packet-001. | — |

### Non-blocking observations (not findings)

1. Interactive desktop/narrow browser screenshots were not re-captured in the implementation session; unit fixtures + structural source assertions are the acceptance bar recorded in phase-4. That is consistent with the packet’s known observations and does not break the freeze contracts.
2. PROGRESS soft archive budget was already over soft limit pre-implementation; not a hard-limit or plan-contract failure.
3. Implementation remains uncommitted worktree-only under standing checkpoint kinds (design-review/proposal-revision/activation-recording only). No phase-exit durable commit authority was invented.

## Authority Boundary

- Local independent implementation review: authorized and executed (this file only).
- Push, PR, merge, Pages, provider/broker, tracked DB write, canonical content mutation, remote admin: **unauthorized and unexecuted**.
- Durable local commit: **not formed** by this review.
- Implementation sources, plan body status, lifecycle indexes, PROGRESS, HANDOFF, and git state: **not modified** by this reviewer.

## Verdict

**accept** with **high** confidence against packet `review-date-filter-fusion-v1-worktree` and plan revision `v2-review-foldback-2026-07-20`.

All §3.1–§3.5 contracts hold in the live freeze sources. Progressive opt-in is Review-only; focus and shared registry-hue trade bindings are gone; B chips, direction colors, Review 工具, shell badges, and YaHei typography match the locked contracts. Protected DB/registry/publisher/exporter boundaries show no plan-induced drift. Packet freeze aggregate `ed19e6e70e5521156be218174e3524aee396bf66b1555569d5f48c9a35d98127` is retained as worktree freeze identity (independent OpenSSL rehash not re-executed in this sandbox; ordered path surface matches packet).

This accept does not authorize stage/commit, push, PR, merge, Pages publication, hosted verification, provider/broker access, or tracked DB/canonical content mutation without separate explicit user authority. Lifecycle closeout may proceed under existing local closeout rules when otherwise authorized.
