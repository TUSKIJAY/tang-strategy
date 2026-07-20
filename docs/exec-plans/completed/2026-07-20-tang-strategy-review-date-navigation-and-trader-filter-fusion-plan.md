# Tang Strategy Review Date Navigation And Trader Filter Fusion

- Lifecycle schema: `operating-modes-v2`
- Status: Completed
- Plan slug: `2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan`
- Revision: `v2-review-foldback-2026-07-20`
- Plan author ID: `codex-plan-author-2026-07-20-review-date-filter-fusion`
- Design reviews: ../reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/review-002.md@approve@v2-review-foldback-2026-07-20
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-21-repair-review-date-filter-checkpoints-and-activate`
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: ../reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/implementation-review-001.md@accept
- Final disposition: Completed
- Verified implementation commit: 064550c1c22ae78911ea20c348bf2e476dd788ca
- Lifecycle reconciliation commit: none
- Implementation start evidence: `user-instruction:2026-07-21-execute-review-date-filter-fusion-plan`
- Current work unit: none
- Work state: none
- Blocker evidence: none
- Implementation reviews: ../reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/implementation-review-001.md@accept@064550c1c22ae78911ea20c348bf2e476dd788ca
- Latest implementation verdict: accept
- Checkpoint authority: `user-instruction:2026-07-21-repair-review-date-filter-checkpoints-and-activate`
- Checkpoint authority mode: standing
- Checkpoint authority kinds: design-review,proposal-revision,activation-recording,implementation-start,phase-exit,implementation-review,completed-migration
- Expected checkpoint kind: completed-migration
- Owner: Codex
- Created: 2026-07-20
- Optimization source: `docs/optimization/2026-07-20-review-date-nav-and-trade-filter-fusion/2026-07-20-review-date-nav-and-trade-filter-fusion.md`
- Proposal baseline: `codex/project-harness@45ca9cb231ef459b7d03bad246d762ed1139bf86`
- Scope authority: local implementation, verification, independent review, and completed-migration under `user-instruction:2026-07-21-execute-review-date-filter-fusion-plan` (goal 全权执行active plan); push/PR/merge/Pages/provider/broker/tracked-DB/canonical-content/remote remain unauthorized

## 1. Context And Evidence

### 1.1 Proposal provenance

This plan promotes the user-named optimization batch `2026-07-20-review-date-nav-and-trade-filter-fusion` into one governed Coding Mode Lane 3 proposal. It covers OPT-001 through OPT-005 as one Review usability contract while retaining the prior completed Terminal UI/Trader Registry implementation as the product baseline.

The proposal was drafted from the live repository at `codex/project-harness@45ca9cb231ef459b7d03bad246d762ed1139bf86`. The worktree already contained the uncommitted optimization record, its three screenshots, its locked HTML mockup, updates to `PROGRESS.md`, `HANDOFF.md`, and `docs/optimization/index.md`, plus unrelated `.playwright-cli/` and `output/` artifacts. All of those existing changes remain user-owned. This plan may reference the optimization assets but may not sweep unrelated artifacts into a later manifest or checkpoint.

The following proposal evidence was re-hashed locally and matches the optimization record:

| Evidence | SHA-256 | Role |
| --- | --- | --- |
| `docs/optimization/2026-07-20-review-date-nav-and-trade-filter-fusion/mockups/review-left-column.html` | `ff5d71ffa87bb65127f0bcf05d421e07c211678cff19473f9f88672337233c50` | Sole locked visual proposal for date IA, fused controls, direction colors, and B Chip scaling |
| `screenshots/2026-07-20-data-sidebar-trader-nav-wrap.png` | `4a52d56c44375e5a0e64d56b7979027520d708afd89438b9f6d4cd89fc99d6c6` | Current shell trader-nav CJK wrapping failure |
| `screenshots/2026-07-20-review-trade-filter-current.png` | `4e5e0f4af36f69c2c748d4c6c6909a1558e4cf257f827fef5e194ada354933e1` | Current Review left-column chrome and duplicate-context friction |
| `screenshots/2026-07-20-trade-call-put-trader-color.png` | `dda2d9256a738ebc320d7752243ca98816ebb19a818fc03bbec2348317cf50cb` | Current trader-owned hue makes CALL and PUT difficult to scan |

### 1.2 Current repository facts

- `ReviewContextPanel.jsx` owns shared ticker tabs and an exhaustive month-grouped `DateRail`. `DashboardPage`, interactive `ReviewPage`, `StaticReviewsApp`, `AdminTradersPage`, and `TraderPointEditor` all reuse this component, so an unconditional DateRail rewrite would violate the Review-only scope.
- `reviewWorkspace.js` already owns normalized day inventory, ticker switching, day resolution, and `groupDatesByMonth`. The progressive browser must remain a projection of that real inventory and must continue to call the existing workspace selection path.
- `TraderFilters.jsx` currently mirrors ticker/date, renders one checkbox plus a separate Focus button per available trader, and stores both `traderIds` and `focusedTraderId`.
- `tradeRecords.js` lets `focusedTraderId` override the selected trader set in filtering/export and colors chart markers by registry trader color. `ReviewPage`, `StaticReviewsApp`, and `AdminTradersPage` all reconcile that shared focus state.
- `TraderTradeList.jsx` paints direction triangles with `--trader-color` and renders trader name plus direction in one strong text run. CALL and PUT for the same trader therefore share a hue.
- Interactive Review renders Ext K, Rescan, and Backtest in the left-column context actions. Static Review renders Ext K there. Backtest is already a peer destination in the global app navigation.
- `Layout.jsx` gives the trader workspace a long inline capability string. On the expanded sidebar this competes with `交易记录 / 点位管理` and can collapse the CJK label into one-character-per-line wrapping.
- The app currently uses `Space Grotesk` and `Newsreader` in shared chrome even though the locked optimization requires Microsoft YaHei / 微软雅黑 for product UI text and reserves monospace for dates, times, and codes.

### 1.3 Lane 3 classification

The work is frontend-only but not bounded Lane 2 maintenance. It changes shared filter state, Review/Static/Admin consumers, chart annotation presentation, shared navigation typography, responsive behavior, and acceptance across interactive and static modes. These cross-component and multi-phase contracts require a reviewed Lane 3 plan. No backend, API, schema, canonical content, tracked SQLite, market-data, provider, broker, exporter, workflow, or publication change is required.

### 1.4 `review-001` foldback

Independent design `review-001` returned `revise/high` against exact revision `v1-proposal-2026-07-20` at content SHA-256 `e8073198d00ed6356dbbe2737dc507a790b846af925c55b67a602f8fa034a9be`. Revision `v2-review-foldback-2026-07-20` closes all four medium findings and both non-blocking observations without changing the user-locked product direction:

- month browsing now has a complete state machine: entering `按月` opens the selected day’s owning month; previous/next changes only the browsed month and never silently changes the workspace day; a browsed month may legitimately contain no pressed chip while the topbar remains the truthful selected-date output;
- registry trader hue is forbidden from shared trade chips/cards, including border, active ring, name, and direction glyph channels; only CALL/PUT direction carries hue on those surfaces;
- interactive and Static utility disclosures now have the exact visible label `Review 工具`, mount point, contents, ARIA state, Escape/focus-return behavior, and Backtest exclusion;
- list/marker/export synchronization means trader-ID **set membership** equality; the existing alphabetically sorted export `trader_ids` sequence remains unchanged;
- the mockup’s free-form jump row is explicitly comparison-only and cannot land in v1;
- the opt-in API is fixed as `dateNavigation="progressive"`, with `dateNavigation="exhaustive"` as the default.

`review-001` remains append-only evidence for v1 and cannot approve this revision. No eligible design-review checkpoint, activation, implementation, or Git/data/remote authority is created by this foldback.

## 2. Objective And Success Criteria

### 2.1 Objective

Make the Review left column scale with date history and trader count while reading as one terminal-family surface: progressive recent/month browsing, one B Chip visibility authority, no duplicate day mirror, compact trade controls, direction-owned CALL/PUT color, readable shell navigation, and the locked Microsoft YaHei product typography.

### 2.2 Success criteria

1. Interactive Review defaults to `最近` and displays exactly the newest 12 real market days for the selected ticker as `MM-DD` chips with no month bar.
2. `按月` displays exactly one selected existing month, renders that month as the sole month identity, and labels its real market-day chips as `DD` only.
3. On initialization, deep-link restoration, or external workspace restoration, a valid selected day older than the newest 12 opens in `按月` on its owning month and is visually pressed. Later explicit month prev/next browsing never changes that selected workspace day; the browsed month may show no pressed chip while the read-only topbar date stays truthful. Ticker switching continues through the existing workspace contract and opens the resolved current/latest day.
4. Dashboard, Admin, TraderPointEditor, and Static Review retain the existing exhaustive DateRail. No shared default changes silently.
5. Review trader visibility is controlled only by B Chip multi-select. Focus buttons, focused override behavior, and `focusedTraderId` reconciliation/export paths are removed from the live shared filter contract.
6. With 1–6 day-available traders, chips render inline and wrap. With 7 or more, the rail renders a selection summary and an `编辑` disclosure drawer with case-insensitive search over display name and trader ID, `全选`, `清空`, and the same chip buttons.
7. Empty trader selection is legal and yields an empty trade list, no trade markers, and exports whose trader selection is empty. It does not crash or silently reselect within the same ticker/date context.
8. A real context change preserves the intersection with newly available traders; when that intersection is empty it selects all traders available in the new context. Registry-only traders with no displayable group never appear.
9. The same trader-ID set membership drives interactive Review list, chart trade markers, and export. UI state remains availability/registry ordered, while exported `trader_ids` retain the existing alphabetical sort; tests compare canonicalized sets rather than raw sequence order. Static Review and Admin inspection use the same focus-free selection semantics without receiving the progressive Review DateRail.
10. The Review trade block no longer repeats resolved ticker/date. Strategy and Eligibility share field geometry; chip/filter/export/list controls share one compact terminal vocabulary.
11. Ext K and Rescan remain available under a right-side topbar disclosure button visibly labeled `Review 工具`, not in the left column. Interactive contains Ext K + Rescan only; Static contains Ext K only. Both expose `aria-expanded`/`aria-controls`; Escape closes and returns focus to the trigger. Backtest never enters either disclosure and remains reachable through global navigation.
12. CALL uses exact semantic color `#6F9F7A`; PUT uses exact semantic color `#E06B66` on chart marker fill/label and list direction glyph/word/optional rail. Up/down shape and the literal CALL/PUT word remain non-color cues.
13. Trader names use the default primary text color in chips, list cards, and chart labels. Shared Review/Static/Admin trade chips/cards must not use registry trader hue for names, borders, active rings, backgrounds, or direction glyphs; CALL/PUT is the only hue channel on these trade surfaces. Registry color remains stored and editable for explicitly excluded non-trade-list uses.
14. Expanded trader-workspace navigation shows `交易记录 / 点位管理` without per-character vertical wrap, uses the short visible capability chip `可编辑` or `只读`, and keeps the full role sentence in `title` and accessible name. Collapsed navigation remains icon-only with a complete accessible name.
15. Shared product UI text uses `"Microsoft YaHei", "微软雅黑", "PingFang SC", "Noto Sans SC", sans-serif`; only timestamps, market-day chips, prices, and technical codes use the existing monospace stack.
16. Desktop `1672x941` and narrow `820x1180` browser acceptance passes for interactive Review and Static Review, plus shell checks on Data and Admin. No horizontal overflow, clipped drawer, unreachable control, lost focus indicator, or inaccessible selected state is accepted.
17. Existing normalized trade payloads, eligibility modes, group expansion/drilldown, download formats, Review assembly, workspace hashes, auth roles, K-line interaction, static read-only behavior, tracked DB, canonical content, exporter, and Pages workflow remain unchanged.

### 2.3 Non-goals

- No Data/Admin/TraderPointEditor/Static progressive date browser, calendar grid, or app-wide date-coverage redesign.
- No free-form date jump in v1. Month navigation already reaches every owned day; adding a jump parser and validation surface requires a later optimization or plan revision.
- The `跳转` row visible in the sole HTML mockup is comparison-only proposal material. Implementers must not copy, hide, disable, or otherwise ship that control in v1.
- No new ticker, fabricated session, weekday-only calendar logic, backend date endpoint, or market-data fetch.
- No new focus-equivalent single-trader shortcut under another name. A one-chip selection is the single-trader view.
- No A Segment implementation; it remains rejected comparison material in the mockup.
- No registry schema or color removal. Existing trader colors may remain available for Admin or other non-Review uses.
- No K-line engine rewrite. The existing explicit annotation color input remains the chart rendering boundary.
- No Backtest behavior redesign, new route, new API, or contextual deep-link contract.
- No auth, canonical data, DB, provider, broker, exporter, workflow, publication, hosted, or remote change.

## 3. Target Contracts

### 3.1 Interactive Review date-navigation contract

- `ReviewContextPanel` and `DateRail` use one named string prop: `dateNavigation="exhaustive" | "progressive"`. The default is exact `dateNavigation="exhaustive"`; no boolean alias or implicit caller detection is allowed.
- `ReviewPage` is the only v1 caller that passes `dateNavigation="progressive"`. Dashboard, Admin, TraderPointEditor, and Static Review omit the prop and retain exhaustive behavior.
- Recent limit is the locked integer `12`, matching the sole mockup. Days are deduplicated, real inventory entries for the selected ticker, sorted newest first.
- `最近` has no month bar. Its chips are `MM-DD`; metadata is `显示最近 N · 全库 <ticker> M`, where `N <= 12` and `M` is the ticker inventory count.
- `按月` exposes previous/next controls over existing months only, ordered newest to oldest. The month label is `YYYY-MM`; day chips are `DD`; metadata is `本月交易日 K · 全库 <ticker> M`.
- Mode controls form one labeled selection group with programmatic current state. Date chips retain full `aria-label="<ticker> <YYYY-MM-DD>"`, `aria-pressed`, and title values.
- Presentation state is exactly `{ browseMode: "recent" | "month", browsedMonth: "YYYY-MM" | "" }`; selected workspace day remains the existing authoritative `value` prop.
- Initialization/external restoration with a selected day inside the recent 12 sets `browseMode="recent"`; a valid older selected day sets `browseMode="month"` and `browsedMonth` to its owning month; no selected day uses recent mode and the newest existing month as the latent month value.
- Every explicit transition into `按月` resets `browsedMonth` to the current selected day’s owning month, or the newest existing month if there is no valid selection. It does not select a new day.
- Month previous/next changes only `browsedMonth`. If the selected workspace day is outside the browsed month, every visible day chip has `aria-pressed="false"`; the topbar continues to show the unchanged selected date. This no-pressed state is valid browsing, not an error or implicit selection.
- Explicit transition into `最近` changes only `browseMode`. If an older selected day is outside the recent 12, Recent also shows no pressed chip and keeps the topbar date unchanged.
- Selecting a day chip is the only browser action that changes the workspace day. It invokes the existing `selectWorkspaceDay` path, preserves the current browse mode, and in month mode keeps `browsedMonth` equal to the selected chip’s month.
- Ticker switching continues through existing `switchTicker` behavior, resolves the ticker’s current/latest real day, and reinitializes progressive presentation from that resolved selection. The UI never selects a value absent from normalized workspace inventory.
- `browseMode` and `browsedMonth` are presentation-only and must not enter hashes, API parameters, backend payloads, local storage, or canonical data.

### 3.2 B Chip trader-selection contract

- `traderIds` is the only trader visibility state. Remove `focusedTraderId` from `initialTradeRecordFilters`, `filterTradeGroups`, `exportSelectionFromFilters`, `reconcileTraderSelection`, and all live page state/reconciliation callers.
- `TraderFilters` removes the ticker/date mirror whenever `context` is supplied. It keeps legacy ticker/date controls only for consumers that do not supply a resolved context.
- Only `availableTraderIds` may populate Review/Static/Admin availability-driven chips. Preserve registry order and deterministic missing-registry tail behavior from `deriveAvailableTraders`.
- `visibleTraders.length <= 6` renders inline chips. `visibleTraders.length >= 7` renders a summary plus an in-flow disclosure drawer; no modal dependency or portal is added.
- Every chip is a `button` with `aria-pressed`; summary edit uses `aria-expanded` and `aria-controls`; the disclosure has a labeled search field and announced empty-search state. Closing the disclosure does not mutate selection.
- Search is case-insensitive over `display_name` and `trader_id` and only narrows the displayed chip list; it never changes selected values. `全选` selects all currently day-available traders, not only search matches. `清空` selects none.
- Summary copy includes selected count plus at most the first three selected display names, followed by an overflow count. Names use default text color.
- Selection state is reconciled to availability/registry order for stable UI summary/chip rendering. Filtering and chart annotations consume that membership set; `exportSelectionFromFilters` retains its existing unique alphabetical `trader_ids` sort. Cross-consumer equality is defined as canonical set membership equality, never raw array-sequence equality.
- Interactive Review, Static Review, and Admin inspection all adopt the focus-free shared state. Only Review receives the new fused left-column density; Admin does not receive a page redesign.
- `TraderFilters` and `TraderTradeList` must not bind registry color through inline `--trader-color` or equivalent identity-hue styles on shared trade chips/cards. Neutral border/background plus shared accent may express selection/active state; CALL/PUT semantic colors alone express direction.

### 3.3 Review chrome and utility ownership

- The interactive Review left column contains ticker, progressive date navigation, Strategy, assembly status, Eligibility, trader chips, export, trade groups, and signals as one continuous density system.
- Remove the redundant `trade-context-mirror` subtree from the resolved-context branch. Date authority remains the workspace rail and the topbar date remains read-only output.
- Mount one right-side utility slot in `.dr-topbar` immediately after the strategy badge. Its trigger has the stable visible label `Review 工具`, `aria-expanded`, and `aria-controls` pointing to one disclosure panel.
- Interactive Review’s disclosure contains exactly the existing Ext K switch followed by Rescan. Static Review’s equivalent disclosure contains exactly Ext K. Backtest is forbidden from both because global primary navigation owns that destination.
- Escape from any open disclosure closes it and returns focus to its trigger. Tabbing may enter and leave controls without a focus trap. Outside-click close is optional; if implemented, it must not steal focus or create a second close contract. Closing never changes Ext K state or invokes Rescan.
- Existing Ext K storage/handler semantics and interactive Rescan handler semantics remain unchanged. Static remains mutation-free and exposes no Rescan.
- The left column must contain none of the visible labels `Ext K`, `RTH`, `Rescan`, or `Backtest` after the move.
- Strategy and Eligibility use the same label, select height, border, typography, active/focus, and spacing vocabulary. Export remains one action and keeps the existing JSON + three CSV content contract.

### 3.4 Direction-color and identity contract

| Semantic | Exact color | Required non-color cue | Consumers |
| --- | --- | --- | --- |
| CALL | `#6F9F7A` | `triangle_up` plus literal `CALL` | chart annotations, list glyph/word/optional rail |
| PUT | `#E06B66` | `triangle_down` plus literal `PUT` | chart annotations, list glyph/word/optional rail |
| Trader identity | default `--text-primary` | full display name text | chip, list, chart marker label |

- `buildTradeRecordAnnotations` maps direction to the exact marker color; it does not consult registry color for Review trade annotations.
- `TraderTradeList` separates trader-name and direction spans so direction color cannot leak into the name. Remove the live card-level `style={{ '--trader-color': ... }}` binding: card border/background/active ring are neutral or shared-accent state, and direction glyph/word/optional rail use only the CALL/PUT semantic color.
- Shared B Chips likewise use neutral/shared-accent selected state and default name text; registry color must not reappear as chip border, fill, ring, or name color in Review, Static Review, or Admin inspection.
- The K-line engine continues to receive `marker_color` and `marker_shape`; no renderer contract, hit-testing, grouping, or annotation selection behavior changes.
- Source-contract tests pin the same exact CALL/PUT values in JS and CSS, assert absence of shared trade-card/chip registry-hue bindings, and preserve registry color in the Admin registry editor contract.

### 3.5 Shell label and typography contract

- `Layout.jsx` renders visible capability copy as `可编辑` for admin and `只读` otherwise. The accessible name/title retains `管理员可编辑` or `只读检查，编辑需要管理员`.
- Expanded sidebar geometry gives the destination label an intentional non-shrinking text row and a short separate badge. At normal expanded width it remains one line; at the narrow acceptance viewport it may truncate as one line with the full title, but it may not stack one CJK character per line.
- Collapsed mode hides label/badge visually while keeping the full accessible name on the button.
- Shared CSS defines one UI stack beginning with Microsoft YaHei/微软雅黑 and one monospace stack. Editorial serif and Latin-only product-chrome overrides are removed from application headings/navigation/controls; code/date/time/price carriers retain monospace.

### 3.6 Protected invariants

- Tracked SQLite proposal baseline SHA-256: `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0`.
- Canonical trader registry proposal baseline SHA-256: `cf6f3122c29e24e842e4ae29d04f772b7b07d1e8ad2fcc43820c7c41c0b2716c`.
- Pages publisher proposal baseline SHA-256: `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8`.
- Static exporter proposal baseline SHA-256: `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996`.
- Phase 0 must recapture current hashes and counts instead of assuming these proposal-time values remain current.
- Backend/API/schema/content/data/workflow/exporter/runbook/provider/broker paths are excluded. Any need to modify one is a hard stop for plan revision.

## 4. Planned File Surface

Phase 0 must freeze an exact Add/Modify/Delete manifest. The candidate surface below is an upper bound, not authority to modify every file.

### 4.1 Candidate source modifications

- `frontend/src/features/review/ReviewContextPanel.jsx`
- `frontend/src/features/review/reviewWorkspace.js`
- `frontend/src/features/review/reviewWorkspace.test.js`
- `frontend/src/features/review/TraderFilters.jsx`
- `frontend/src/features/review/tradeRecords.js`
- `frontend/src/features/review/tradeRecords.test.js`
- `frontend/src/features/review/TraderTradeList.jsx`
- `frontend/src/features/review/TradeExportControls.jsx` only if semantic grouping or compact action copy requires it
- `frontend/src/pages/ReviewPage.jsx`
- `frontend/src/pages/StaticReviewsApp.jsx`
- `frontend/src/pages/AdminTradersPage.jsx` only for removal of obsolete shared focus state
- `frontend/src/components/Layout.jsx`
- `frontend/src/styles.css`

### 4.2 Candidate documentation and lifecycle modifications

- `docs/architecture.md` for final shared Review date/filter ownership
- `docs/kline-engine.md` for final direction-color annotation semantics
- this plan and its future evidence/review artifacts under `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/`
- the four lifecycle indexes, `docs/exec-plans/roadmap.md`, `PROGRESS.md`, `HANDOFF.md`, and the source optimization/index when a lifecycle transition materially changes them

### 4.3 Explicitly excluded source paths

- `backend/**`
- `content/**`
- `data/**`
- `strategies/**`
- `frontend/src/api/**`
- `frontend/src/kline/**`
- `backend/scripts/export_static_reviews.py`
- `.github/workflows/**`
- `docs/daily-publish-runbook.md`
- `frontend/public/reviews/**`, `frontend/dist/**`, `.playwright-cli/**`, and `output/**`

There are no planned production-source additions or removals. If implementation requires a new component/helper file, Phase 0 must name it in the exact manifest before source work begins; otherwise stop for plan revision.

## 5. Phased Execution Plan

### Phase 0 — Baseline, Exact Manifest, And Contract Freeze

- Entry gate: matching-revision independent design review returns `approve`, the user separately authorizes activation, the plan is moved to `active/` at `phase-0:not-started`, and a later explicit implementation-start instruction opens Phase 0. Proposal approval alone is insufficient.
- Work:
  - recapture branch/HEAD/status, candidate file hashes, protected hashes/counts, current frontend test totals, current builds, and current browser behavior;
  - freeze the exact Add/Modify/Delete manifest and prove excluded paths are not needed;
  - freeze constants and API: `dateNavigation="exhaustive" | "progressive"`, recent limit `12`, inline threshold `<=6`, summary threshold `>=7`, CALL `#6F9F7A`, PUT `#E06B66`, visible utility label `Review 工具`, and the UI/mono font stacks;
  - archive before-state screenshots for interactive Review recent inventory, current trade filter/list/markers, Static Review, Data/Admin shell label, expanded/collapsed desktop, and narrow viewport;
  - record current `focusedTraderId`, registry `--trader-color`, shared card/chip, export-sort, Ext K/Rescan/Backtest, and DateRail caller inventories so removal/opt-in/compatibility behavior can be proven complete.
- Verification: governed/auto/direct lifecycle checks, frontend tests, normal/static builds, `git diff --check`, protected hash/count capture, and browser before-state matrix.
- Exit gate: exact manifest and deterministic contract fixtures are frozen in Phase 0 evidence; any backend/data/publisher/engine requirement causes `phase-0:blocked` and plan revision.

### Phase 1 — Progressive Interactive Review Date Navigation

- Entry gate: Phase 0 exit is recorded and Phase 1 is separately started under valid implementation authority.
- Work:
  - add pure recent/month/selected-month projection helpers over normalized workspace inventory;
  - implement exact `dateNavigation="progressive"` with the frozen `browseMode` / `browsedMonth` state machine and mode/month/selection accessibility;
  - opt in only `ReviewPage`; preserve default `dateNavigation="exhaustive"` behavior for Dashboard, Admin, TraderPointEditor, and Static Review;
  - implement old-day restoration, manual Recent/Month switches, month-only browsing with a valid no-pressed state, and ticker-switch reconciliation without route/API/data changes;
  - assert that the mockup-only `跳转` row has no production control, handler, or hidden placeholder.
- Verification:
  - pure fixtures for 0, 1, 11, 12, 13, and 46+ days; cross-month recent windows; missing ticker; oldest/newest month; old selected day; entering Month; prev/next without selection mutation; no-pressed browsed month; entering Recent with an older selection; ticker switch; and no fabricated dates;
  - source/behavior assertions that only interactive Review passes `dateNavigation="progressive"`, every omitted caller remains exhaustive, and no jump UI lands;
  - browser keyboard and screen-reader-state checks in desktop/narrow Review.
- Exit gate: every real Review day is reachable without exhaustive default rendering, and every non-Review DateRail consumer is byte/behavior compatible at its boundary.

### Phase 2 — B Chip Selection And Focus Removal

- Entry gate: Phase 1 exit is recorded and Phase 2 is separately started.
- Work:
  - remove `focusedTraderId` from shared filter initialization, filtering, export, reconciliation, and Review/Static/Admin page state;
  - replace checkbox+Focus UI with button chips;
  - implement deterministic inline and >=7 summary/disclosure states, search, select all, clear, summary copy, and accessible state;
  - preserve day-availability, context-change selection reconciliation, eligibility modes, alphabetically sorted export `trader_ids`, export contents, and empty selection;
  - remove registry-hue bindings from shared chips/cards and use neutral/shared-accent selection chrome plus direction-only CALL/PUT hue.
- Verification:
  - 0/1/2/4/6/7/8 trader fixtures; all/subset/one/empty; search hit/miss/case; select-all/clear; closing/reopening; context intersection/no-intersection; registry-only exclusion;
  - canonical set-membership equality of selected trader IDs consumed by list, annotations, and export, plus an independent fixture preserving alphabetical export order;
  - repository scan proves no live `focusedTraderId`, Focus button, checkbox+Focus pair, alternative single-trader override, or shared trade-card/chip `--trader-color` identity binding remains.
- Exit gate: one B Chip state is the sole trader visibility authority across interactive Review, Static Review, and Admin inspection.

### Phase 3 — Fused Review Chrome, Direction Colors, Shell Label, And Typography

- Entry gate: Phase 2 exit is recorded and Phase 3 is separately started.
- Work:
  - remove resolved-context ticker/date mirror and align Strategy, Eligibility, chip, export, list, and focus states to the locked mockup density;
  - mount exact `Review 工具` disclosures after the topbar strategy badge: interactive Ext K + Rescan only, Static Ext K only, with ARIA state and Escape/focus return; remove Review-local Backtest duplication while preserving global navigation;
  - map chart/list direction presentation to exact CALL/PUT colors and split trader name from direction styling;
  - shorten the visible shell capability badge while retaining full accessible copy;
  - apply the locked Microsoft YaHei UI stack and preserve monospace only for technical carriers.
- Verification:
  - source assertions for absent left-column mirror/tool labels, exact utility contents/mount point/ARIA/Escape behavior, Backtest exclusion, and unchanged handler/storage ownership;
  - chart/list fixtures for same-trader CALL+PUT, two-trader same-direction, grouped markers, exact color values, shape labels, and default name color;
  - shell expanded/collapsed and screen-reader-name assertions for admin/readonly roles;
  - computed-style/font checks across Data, Review, Static, Backtest, Teaching, Admin, and Login without page IA changes.
- Exit gate: the implementation matches the sole mockup on named surfaces, every excluded behavior remains unchanged, and no person's name receives direction red.

### Phase 4 — Integrated Interactive, Static, Accessibility, And Regression Acceptance

- Entry gate: Phase 3 exit is recorded and Phase 4 is separately started.
- Work:
  - run interactive Review against SPY 2026-07-17 and `tang-v4-4-slope-4-4` with non-empty 1m/5m bars;
  - exercise newest/old-month date selection, SPY/QQQ switching, 2-person and simulated 8-person availability, selection/export/marker synchronization, empty selection, eligibility changes, group drilldown, Ext K, Rescan, global Backtest navigation, and route restoration;
  - exercise Static Review current and legacy hashes with its legacy DateRail, shared B Chips/direction semantics, Ext K, downloads, and no admin/API mutation;
  - inspect Data/Admin shell label and product typography without changing their DateRail or page contracts;
  - capture desktop `1672x941` and narrow `820x1180` screenshots plus console/network/overflow/accessibility receipts.
- Verification: full frontend suite, normal/static builds, backend compileall as compatibility evidence, governed/auto/direct lifecycle checks, startup budget, SQLite integrity/foreign keys, protected hashes/counts, scope scan, and `git diff --check`.
- Exit gate: the complete acceptance matrix passes or the plan records a named blocker/remediation path; isolated success cannot be reported as full acceptance.

### Phase 5 — Documentation, Frozen Review Packet, And Closeout Gate

- Entry gate: Phase 4 exit is recorded and Phase 5 is separately started.
- Work:
  - update architecture/K-line docs with verified implementation truth only;
  - freeze exact implementation manifest, hashes, test totals, browser evidence, protected boundaries, known observations, and authority statement in an implementation-review packet;
  - obtain independent implementation review against the exact eligible checkpoint target;
  - if verdict is `revise`, open only the authorized structured remediation unit; if `accept`, reconcile lifecycle surfaces and move to Completed through the separately governed closeout transition.
- Verification: independent reviewer re-runs proportionate tests and directly inspects required screenshots/source evidence; final lifecycle and durable-checkpoint audits pass.
- Exit gate: an `accept` implementation review and truthful Completed reconciliation. A green local matrix without independent `accept` is not closeout.

## 6. Safety, Compatibility, And Rollback Matrix

| Risk | Fail-closed gate | Rollback boundary |
| --- | --- | --- |
| Shared DateRail changes Data/Admin/Static | Explicit opt-in prop plus caller inventory and regression screenshots | Revert progressive variant/caller opt-in; keep default exhaustive rail |
| Browsed month and selected day become ambiguous | State-machine fixtures require entry to owning month, month-only browse, valid no-pressed state, and truthful topbar | Restore `browseMode`/`browsedMonth` presentation state without changing workspace selection |
| Month/day UI fabricates sessions | Every chip must be drawn from normalized inventory; no free-form jump | Remove invalid projection; never patch data or calendar |
| Focus survives as hidden override | Repository carrier scan plus list/marker/export equality fixtures | Remove remaining override and reconcile to `traderIds` only |
| Empty selection silently becomes all | Same-context empty fixtures and browser check | Restore fail-closed empty selection; only real context change may select all on empty intersection |
| Many-trader drawer clips or traps focus | 7/8-person desktop+narrow keyboard matrix | Fall back to in-flow disclosure, not modal/portal |
| Direction color leaks into a name | Separated DOM spans, computed styles, chart screenshot, exact source fixtures | Restore primary name color and direction-only semantic selectors |
| Registry identity hue survives on shared chips/cards | Source scan plus computed border/ring/glyph checks across Review/Static/Admin | Remove `--trader-color` bindings; restore neutral/shared-accent state chrome and direction-only hue |
| Registry color/schema is accidentally removed | Protected content hash and source diff | Revert schema/data changes; Review presentation does not own registry storage |
| Ext K/Rescan behavior or disclosure focus is lost during relocation | Exact `Review 工具` contents, ARIA/Escape/focus-return assertions, handler/storage checks, and browser receipts | Restore frozen disclosure wiring without returning controls to left column or adding Backtest |
| Export order is confused with selection equality | Canonical set comparison plus independent alphabetical-order fixture | Keep UI ordering local and preserve existing sorted export contract |
| Backtest becomes unreachable | Global nav browser route check | Restore existing peer-nav destination; do not add a second local route |
| Font change harms codes/prices/dates | Computed UI/mono carrier matrix | Narrow typography selectors while retaining locked UI stack |
| Canonical data, DB, backend, engine, exporter, or workflow drifts | Phase 0/post-phase hashes, path scan, SQLite checks | Stop; restore only authorized source changes; require plan revision for broader scope |
| Unrelated dirty artifacts enter manifest | Baseline status tuple and literal path-set inspection | Do not reset/stash/restore; omit unrelated `.playwright-cli/` and `output/` paths |

## 7. Verification And Evidence Plan

### 7.1 Required recurring checks

```bash
python3 scripts/check-project-harness.py --root . --profile governed
python3 scripts/check-project-harness.py --root . --profile auto
python3 scripts/check-operating-modes.py --root .
python3 -m unittest scripts.tests.test_operating_modes
python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated
python3 scripts/check-startup-doc-budget.py
cd frontend && npm run test:trade-records
cd frontend && npm run build
cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews
cd backend && PYTHONPATH=. python3 -m compileall -q app scripts tests
git diff --check
```

The full backend suite is required only if implementation evidence shows a backend-adjacent compatibility risk; no backend source change is planned. Any pre-existing environment failure must be reproduced and classified truthfully rather than reported as a pass.

### 7.2 Plan-specific deterministic matrix

| Area | Required cases |
| --- | --- |
| Recent dates | 0/1/11/12/13/46+ days; newest-first; cross-month `MM-DD`; no month bar |
| Month dates | enter at selected owning month; prev/next changes browse only; valid no-pressed month; `YYYY-MM` sole month identity; `DD` chips; oldest/newest stop |
| Restoration | recent selected day; old valid selected day opens its month; explicit Recent with old selection; missing ticker/day fallback through existing workspace rules |
| Surface scope | Review progressive; Dashboard/Admin/TraderPointEditor/Static exhaustive unchanged |
| B Chips | 0/1/2/4/6 inline; 7/8 summary drawer; arbitrary subset; one; all; empty |
| Drawer | search name/ID/case; no hits; all; clear; reopen; keyboard; narrow overflow |
| Reconciliation | same-context empty persists; context intersection persists; empty intersection on changed context selects all available |
| Shared selection | equal canonical trader-ID membership sets for list, markers, and export; exported array remains alphabetical |
| Direction | same trader CALL+PUT; two traders; grouped marker; exact green/red; shape/word non-color cue; default name text; no registry hue on shared chip/card border/ring/glyph |
| Utilities | exact `Review 工具` trigger after strategy badge; interactive Ext K+Rescan only; Static Ext K only; ARIA/Escape/focus return; global Backtest; none in left column |
| Shell | admin/readonly, expanded/collapsed, desktop/narrow, full accessible names, no vertical CJK wrap |
| Static | current and legacy hash, exhaustive DateRail, B Chips, direction colors, downloads, no mutation/API admin path |
| Protected state | DB/content/exporter/publisher hashes and counts unchanged; SQLite integrity/FK clean |

### 7.3 Browser evidence

- Use the protected local acceptance launcher from repository root: `./scripts/start-local-acceptance.sh`.
- Interactive acceptance uses SPY 2026-07-17 with strategy `tang-v4-4-slope-4-4`, non-empty 1m/5m bars, and real normalized trader records.
- Simulated 7/8-trader scale data must be fixture-only or injected into an isolated in-memory/browser harness. It must not write canonical content or tracked SQLite.
- Capture named before/after screenshots, viewport, role, route/hash, selected date/mode/traders, console result, network mutation inspection for Static, and overflow/focus observations.

## 8. Commit, Data, Remote, And Publication Boundaries

- This Active plan is recorded at `phase-0:not-started` and remains implementation-free. The user's 2026-07-21 recovery instruction authorized only the exact local `proposal-revision`, `design-review`, and `activation-recording` checkpoints; it does not authorize product implementation, push, PR, merge, Pages publication, hosted verification, provider/broker access, tracked DB/canonical content mutation, or remote administration.
- Recovery started from a separately recorded clean baseline. The v2 declaration intentionally excludes append-only v1 `review-001`; matching-revision v2 `review-002` now targets the newly formed `proposal-revision` checkpoint `52498ad533a09b822ef3d28eee08caaadb2d8a41`.
- The repaired design chain passed before activation. This post-image records the real `activation-recording` boundary and stops at `phase-0:not-started`; no old commit was relabeled or backdated.
- Matching-revision design `approve` does not activate the plan. Activation requires a separate explicit user instruction and changes lifecycle files only.
- Activation does not start Phase 0. Implementation requires another explicit start/execute instruction after activation recording.
- Local acceptance does not grant checkpoint, push, publication, or remote authority. Any later local checkpoint must use a literal, exact manifest and valid `Tang-*` trailers; it cannot include `.playwright-cli/`, `output/`, generated Review JSON, or Vite output.
- No prior Terminal UI, Review Workspaces, governance, commit, or push authority may be reused.

## 9. Design Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/`
- Required design review target: exact revision `v2-review-foldback-2026-07-20` at an eligible `proposal-revision` checkpoint commit.
- Required reviewer: independently authored context with a different reviewer ID, direct repository evidence inspection, and the constrained v2 review metadata including `Review target commit`.
- Required verdict: `approve` for exact revision `v2-review-foldback-2026-07-20`. `review-001` is append-only `revise` evidence for v1 and cannot approve v2. Any further `revise` requires another stable plan revision and eligible `proposal-revision` checkpoint before re-review.
- Required user approval: separate explicit activation instruction after matching-revision `approve`.
- Activation is a lifecycle-only transition to `active/` with `phase-0:not-started`; it performs no source implementation.
- Implementation start requires a later explicit start/execute instruction and Phase 0 entry evidence.

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for lifecycle invariants, durable checkpoints, reviewer ancestry, transitions, authority boundaries, and closeout.


## 10. Closeout Record

- Closed: 2026-07-20T17:09:47Z
- Implementation start: `user-instruction:2026-07-21-execute-review-date-filter-fusion-plan`
- Phases 0–5 complete on local worktree freeze aggregate `ed19e6e70e5521156be218174e3524aee396bf66b1555569d5f48c9a35d98127`
- Independent implementation-review-001: accept/high (reviewer `grok-independent-implementation-reviewer-2026-07-21-review-date-filter-fusion-001`)
- Frontend unit tests 48/48; normal+static builds pass; governed/auto/operating/durable-audit/compileall/diff-check pass; protected hashes unchanged
- No push/PR/merge/Pages/provider/broker/DB/content mutation
- Durable local commit deferred: standing checkpoint authority kinds do not include phase-exit/implementation
