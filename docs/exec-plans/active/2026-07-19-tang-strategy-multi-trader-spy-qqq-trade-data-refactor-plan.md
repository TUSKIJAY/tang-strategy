# Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor

- Lifecycle schema: `operating-modes-v1`
- Status: Active
- Plan slug: `2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan`
- Revision: `v5-round-3-review-foldback-2026-07-19`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Design reviews: ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-001.md@revise@v2-dual-review-loop-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-002.md@revise@v2-dual-review-loop-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-003.md@approve@v3-round-1-review-foldback-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-004.md@revise@v3-round-1-review-foldback-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-005.md@revise@v4-round-2-review-foldback-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-006.md@approve@v4-round-2-review-foldback-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-007.md@approve@v5-round-3-review-foldback-2026-07-19, ../reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/review-008.md@approve@v5-round-3-review-foldback-2026-07-19
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-19-start-dual-review-loop-through-active`
- Current phase: phase-5
- Phase state: complete
- Phase entry gate: `phase-5-start`
- Next gate: `phase-6-authorization`
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Owner: Codex
- Created: 2026-07-19
- Scope authority: implementation start authorized for Phase 0-4 local/offline work and Phase 5 offline work; the current user instructions separately authorize real TradingView provider runs for the required macOS/Windows Phase 5 receipts and one plan-scoped stage/commit/push of `codex/project-harness` to transfer the blocked Phase 5 checkpoint to Windows; IB access, tracked DB promotion, Phase 6 cutover, PR, merge, Pages publication, and other remote changes remain unauthorized

## 1. Context And Evidence

### 1.1 Current repository facts

The current implementation is a Tang-specific SPY overlay on top of a market-review runtime:

- `backend/app/services/tang_trades.py` reads optional `content/trader-trades/<YYYY-MM-DD>.json` files at request/export time and defaults missing expiry to the trade date.
- `backend/app/main.py` and `backend/scripts/export_static_reviews.py` expose that payload as `tang_trades`; `backend/scripts/recover_historical_market_days.py` consumes the same static payload field during recovery acceptance. The trade data is not normalized into SQLite and cannot be joined directly to market bars for cross-trader analysis.
- The tracked SQLite schema in `backend/app/db.py` contains tickers, logical market days, 1m/5m bars, strategies, and teaching assets, but no trader, trade-group, leg, event, outcome, analysis-run, or market-dataset tables.
- The tracked runtime currently contains 46 SPY market days and no QQQ market day. The 20 tracked legacy trade JSON files are all date-scoped Tang records.
- Both TV and IB day adapters already accept `--symbol`, but their descriptions/default flow remain SPY-specific and import one symbol immediately unless `--skip-import` is supplied.
- `backend/app/services/importer.py` and `backend/scripts/rebuild_live_extended_db.py` discover only `SPY_` and `SPX_` market seeds, so accepting `--symbol QQQ` at the adapter does not establish an end-to-end QQQ contract.
- The Pages workflow fixes `TANG_STATIC_REVIEW_TICKER=SPY`; the daily runbook, Tang overlay, frontend labels/marker styles, and validation commands are SPY/Tang-specific. The normative `docs/operating-modes.md` Local Update Gate and carrier map also reference Tang-specific JSON and `load_tang_trades`.
- The current static hash route already includes ticker, date, and session (`#<ticker>-<date>-extended`). That existing link shape must remain stable.

### 1.2 Confirmed product decisions

The requirements discussion established these binding design decisions:

1. SPY and QQQ are peer supported underlyings and must be freely switchable in both interactive and static review views.
2. A daily SPY/QQQ update is an atomic pair: publish both newly accepted days or publish neither. Partial freshness is not an accepted normal result.
3. Every trader is modeled identically. Tang is migrated as `trader_id: tang`; no Tang-only runtime or API contract remains after cutover.
4. Phase 1 ingestion remains manual normalization from user-provided text/screenshots. The repository and Pages store only normalized public fields, never raw screenshots or chat transcripts.
5. Reviewable daily JSON is canonical; SQLite is a rebuildable, query-optimized projection for runtime, Pages, exports, and Agent analysis.
6. The trade hierarchy is `trader -> trade_group -> trade_leg -> trade_event`. IDs are generated once, persisted, and never recomputed from mutable time/strike/note fields.
7. First-version trading scope is long-premium, single-leg, intraday options. Missing expiry defaults to that New York trade date as 0DTE and records `rule_default`; no overnight positions, short-premium statistics, spreads, or option-bar history are included.
8. Time uses the IANA zone `America/New_York`. Canonical JSON includes an explicit UTC offset and time precision; SQLite materializes UTC timestamps for joins. No fixed `UTC-4` assumption is legal.
9. SPY/QQQ underlying 1m/5m bars are stored. Individual option K-lines, Greeks, order book, and quote history are not stored.
10. Display eligibility, reported-result eligibility, and calculated-result eligibility are independent. An incomplete but verified point may display while remaining excluded from calculated performance.
11. Explicit trader-reported returns remain valid reported facts even without exit fill/quantity. They must not be converted into fabricated option prices or dollar P&L.
12. Unknown fees are `null`, never zero. Gross calculations may exist without fees; net calculations require explicitly known fees. Reported and calculated outcomes remain separate and conflicts remain visible.
13. Group-level performance is the default public statistic; leg-level results remain available for drilldown. Adds and partial closes use weighted-average long-premium cost.
14. Records are `active`, `voided`, or `superseded`; published records are not physically deleted. Normalization review is `pending` or `verified`. Formal Pages exports include only `verified + active` records.
15. The first visit shows all active traders with stable colors and distinct CALL/PUT shapes. Filtering/focus is session-only. No new trader-filter `localStorage` persistence or share-URL filter parameters are built.
16. Downloads follow the current trader/ticker/date filters and include a full normalized JSON export plus `trade_groups.csv`, `trade_legs.csv`, and `trade_events.csv`. K-lines, HTML, PDF, screenshots, and raw chat are not part of this export.
17. Historical Tang JSON is migrated once. Clear return percentages and approximate/explicit exit times may be conservatively extracted, while the original note is preserved and the extraction is labeled `legacy_rule_extract`. Ambiguous prose is not inferred.
18. The public trade payload, registered read/admin routes, static export, frontend consumers, Pages workflow, AGENTS/runbook, normative operating-mode contract, and default daily entry switch together in Phase 6. Phase 5 may add internal QQQ seed discovery, import/rebuild, and pair-orchestrator capability for candidate/testing use while the default SPY/Tang daily path stays unchanged. There is no public dual write and no runtime compatibility period for the old `tang_trades` response shape.
19. Historical normalized content and existing Pages ticker/date links are compatibility requirements even though the old API payload name is removed.
20. `main` remains untouched until a separately authorized merge. This proposal and its reviews grant no push, PR, merge, activation, implementation, provider, DB, or publication authority.

### 1.3 Round-1 design-review foldback

Kimi `review-001` and Grok `review-002` independently returned `revise` against frozen revision `v2-dual-review-loop-2026-07-19`. This revision folds every blocking finding and the material non-blocking clarifications into the canonical plan:

- adds the missed recovery consumer, normative operating-mode contract, chart marker files, rebuild fixture, and runnable frontend pure-test carriers to the exact file surface;
- defines the 46 existing SPY-only days as legal grandfathered history, makes pair atomicity prospective for newly accepted pair updates, and defines ticker-specific UI/static-manifest behavior without synthetic QQQ backfill;
- moves the public `tang_trades` -> `trade_records` switch and all interactive/static consumers into one Phase 6 cutover boundary;
- constrains legacy percentage extraction with explicit allow/deny rules and complete 27-trade/2-context reconciliation;
- defines dataset/bar keys, exactly-one-active enforcement, and market-day-to-active-dataset resolution;
- keeps Phase 5 blocked, rather than complete, if either cross-platform receipt is missing; and
- removes ambiguous Git-commit wording from the Phase 0 exit gate.

### 1.4 Round-2 design-review foldback

Round 2 independently produced Kimi `review-003: approve` and Grok `review-004: revise` against frozen v3. This revision closes the remaining blocking manifest gap and all round-2 clarifications:

- adds `bar_utils.py`, `db_safety.py`, and `test_db_safety.py`, and requires old/new-schema logical bar digests plus active-dataset count resolution;
- scopes switch-together wording to the public/default daily boundary while keeping Phase 5 internal QQQ candidate capability legal;
- names the two source records precisely as day-level note entries: one beside trades and one on a trades-empty day;
- removes non-live `DailyReviewChart.jsx` from the marker change surface after verifying Review/Static use `UnifiedKlineEngine` and `kline-engine.js`; and
- makes the frontend pure-test command applicable only from Phase 4 onward.

### 1.5 Round-3 design-review foldback

Round 3 independently produced Kimi `review-005: revise` and Grok `review-006: approve` against frozen v4. This revision closes Kimi's remaining exact-manifest documentation gap:

- adds the root `README.md`, `backend/README.md`, and `docs/kline-engine.md` carriers to the exact Modify surface;
- binds the backend seed-contract wording to the Phase 5 internal QQQ generalization without changing the default SPY/Tang daily entry; and
- binds the root content-layout and K-line overlay-contract wording to the Phase 6 multi-trader cutover.

### 1.6 Why Lane 3 is mandatory

This work changes the tracked SQLite schema, candidate migration, source/provenance model, API/static payload contract, frontend behavior, market-data orchestration, Pages workflow, daily runbook, and historical data shape. It is cross-contract, broad, and difficult to roll back after publication, so `docs/operating-modes.md` requires a reviewed Lane 3 Exec Plan.

## 2. Objective And Success Criteria

### 2.1 Objective

Replace the Tang/SPY-specific overlay with one normalized multi-trader trade-data system that supports SPY and QQQ end to end, preserves reviewable source data, projects it safely into the tracked SQLite runtime, exposes stable Agent-readable joins to underlying market context, and publishes a read-only multi-trader Pages experience.

### 2.2 Success criteria

- A single canonical daily file can represent all verified and pending SPY/QQQ trade groups for every configured trader.
- All 20 legacy Tang files migrate without losing a date, trade point, note, explicit strike, expiry, action, source, or reason type.
- Every migrated/new group, leg, and event has a stable persisted ID and valid New York/UTC time representation.
- The tracked DB candidate retains every pre-migration market day, strategy, teaching asset, and bar value while adding the normalized trade and dataset projections.
- Agent queries can filter by trader, SPY/QQQ, date, direction, event time, result class, completeness, and market context without parsing JSON notes.
- Interactive review and Pages can switch SPY/QQQ and display multiple traders together with stable identity/color/shape semantics.
- The 46 pre-cutover SPY-only days remain legal and link-stable without fabricated QQQ backfill; pair atomicity governs only dates newly accepted through the pair orchestrator.
- Public statistics never mix reported and calculated outcomes, never treat unknown fees as zero, and never include records whose corresponding eligibility flag is false.
- For every date processed through the pair orchestrator, static export and daily publication accept both SPY and QQQ or leave the prior accepted state intact; grandfathered SPY-only dates remain exportable.
- Existing `#<ticker>-<date>-extended` links continue to resolve after the payload migration.
- Windows and macOS TV pair-update receipts pass the same pinned dependency, NYSE-calendar, timezone, quality, candidate, and no-partial-write tests before the default daily runbook changes.
- All old `tang_trades` code paths and legacy JSON inputs are removed only after every consumer and migration invariant passes; no hidden compatibility adapter or dual-write path remains.

### 2.3 Non-goals

- Discord/group-chat ingestion, OCR storage, or automated collection of raw evidence.
- Option quote/K-line/Greeks/order-book storage or option MFE/MAE reconstruction.
- Multi-leg spreads, short premium, overnight positions, portfolio/risk management, broker execution, or account P&L.
- User accounts, cloud-synchronized preferences, filter persistence, or shareable trader-filter links.
- PDF/HTML/K-line export.
- Any `main`, `gh-pages`, remote repository, branch-protection, environment, provider-credential, or broker mutation under proposal/review authority.

## 3. Target Contracts

### 3.1 Canonical repository data

Add a versioned, reviewable contract:

```text
content/traders/index.json
content/trades/YYYY-MM-DD.json
content/schemas/traders.schema.json
content/schemas/trades-day.schema.json
```

`content/traders/index.json` owns immutable `trader_id` plus editable `display_name`, `color`, `active`, and `sort_order`. A trader may be deactivated but not silently deleted while referenced.

Each daily trade file owns:

- `schema_version` and New York `trade_date`;
- all traders and both underlyings for that date through `trade_groups`;
- group status/review/eligibility fields;
- one or more legs and ordered events, although first-version validation permits exactly one long-premium leg;
- reported and calculated outcomes as separate structures;
- normalized notes and provenance labels, never raw evidence;
- migration metadata for legacy records.

IDs use persisted readable forms such as `tg_20260718_tang_spy_001`, `<group>_l1`, and `<leg>_e1`. Editing time, strike, quantity, result, or notes does not change an assigned ID. ID uniqueness is repository-wide and validation fails closed on reuse.

### 3.2 Required and optional fact semantics

Every verified displayable group requires `trade_group_id`, `trader_id`, `underlying`, `trade_date`, CALL/PUT direction, at least one entry event with an `occurred_at` value or an explicitly incomplete point time, `status`, `review_status`, and the three eligibility flags.

Option strike, premium, quantity, fees, and explicit exit are nullable facts. Null means unknown. Defaults require a companion source such as `rule_default`; they must not be indistinguishable from user-provided values.

An event stores:

- persisted `event_id`, parent leg ID, action (`buy_open`, `buy_add`, `sell_partial`, or `sell_close`), and sequence;
- `occurred_at` as ISO-8601 with the actual offset resolved through `America/New_York` plus `time_precision` (`exact`, `minute`, or `approximate`);
- optional premium, quantity, fees, normalized note, and fact provenance.

The canonical parser validates the offset against the installed IANA timezone rules for the event date and materializes UTC in SQLite. Updating future timezone legislation must require tzdata/runtime acceptance, not a schema edit or a fixed-offset rewrite.

### 3.3 Outcome and eligibility contract

- `display_eligible` controls chart/list display.
- `reported_stats_eligible` requires an explicit normalized reported return or P&L fact.
- `calculated_stats_eligible` requires the facts needed for the applicable formula and a fully closed group.
- `reported_outcome` and `calculated_outcome` are never overwritten by one another.
- If both returns exist and differ beyond declared two-decimal display rounding, preserve both and set `result_conflict: true`; do not choose a winner automatically.
- Weighted-average entry cost is used for adds and partial closes. Contract multiplier is explicit and defaults to 100 only with `rule_default` provenance.
- Gross return/P&L may be calculated from complete fills. Net fields remain null unless every included fee is explicitly known, including an explicit zero.
- Partial-open groups display current events but do not enter completed-trade win rate or completed calculated return statistics.
- Public summary defaults to group level. Leg/event tables and export files retain the lower-level facts.

### 3.4 SQLite and Agent analysis contract

The target relational model separates facts, provider snapshots, and derived analysis:

```text
traders
  -> trade_groups
       -> trade_legs
            -> trade_events
       -> trade_outcomes

market_days
  -> market_datasets
       -> bars_1m / bars_5m

analysis_runs
  -> trade_market_context
```

Required properties:

- `market_days` remains the stable logical `(ticker, trade_date, session_mode)` identity.
- `market_datasets` records provider, venue, source/fetcher revision, imported time, checksum, quality summary, and active/superseded state. Exactly one active dataset serves a logical market day.
- Existing 46 SPY days receive a candidate-built bootstrap dataset without changing their logical market-day identity or bar values.
- `bars_1m` and `bars_5m` reference `dataset_id`, use `(dataset_id, idx)` as their ordered identity, and no longer own an independent market-day foreign key. A partial unique index allows at most one active dataset per `market_day_id`; candidate validation requires exactly one active dataset for every accepted market day before promotion.
- Assemble/export accepts the stable `market_day_id`, resolves its one active dataset, and then reads bars by `dataset_id`; zero or multiple active datasets fail closed. A trade group references the logical market day, while event-to-bar association is resolved from UTC time and recorded in versioned `trade_market_context` rows tied to `analysis_runs` and the exact dataset.
- Source trade facts are not overwritten by Agent computations. Analysis rows record algorithm/version and can be discarded/rebuilt.
- Read-only views provide stable, documented query surfaces for group performance, event facts, current active market dataset, and event market context.
- Required indexes cover trader/ticker/date, group/leg/event ancestry, UTC event time, active dataset lookup, review/status/eligibility filters, and analysis run/dataset linkage.

The implementation must document example Agent queries, null semantics, and which columns are facts versus reported results versus calculated/derived results.

### 3.5 API, Pages, and export contract

- Phase 1 `docs/trade-data-contract.md` must freeze the minimum `trade_records` response table before any backend/UI work: `schema_version`, selected `ticker`/`trade_date`, trader registry slice, nested groups/legs/events/outcomes, normalized note contexts, eligibility/count summaries, and export metadata. Raw evidence is forbidden.
- Replace the old `tang_trades` response member with `trade_records` only in the Phase 6 atomic cutover that also switches interactive/static consumers and recovery acceptance. No earlier phase changes the existing assemble/static member or emits both members.
- Interactive read APIs support trader, ticker, date range, status/review, and eligibility filters.
- Admin-token endpoints validate and write trader configuration and canonical daily JSON through candidate/temp-file validation plus atomic replacement; Pages remains read-only.
- Static export emits only `verified + active` records and includes all configured tickers requested by the pair contract.
- Existing date/ticker hash URLs remain unchanged. Trader filters are UI state only and are not persisted or added to the URL.
- JSON download preserves the selected normalized hierarchy and export metadata. CSV download produces three flat files with stable foreign keys: groups, legs, and events.
- Downloads include only the current trader/ticker/date selection and contain no bars or raw evidence.

### 3.6 SPY/QQQ atomic market update contract

The current one-symbol adapters remain internal provider primitives. A tracked pair orchestrator becomes the documented daily entry:

1. resolve one completed NYSE session;
2. capture Git and tracked-DB baseline;
3. fetch both SPY and QQQ from TradingView into a unique temporary staging directory with import disabled;
4. validate each payload and the pair-level same-date/session/source/quality contract;
5. build/import both into one candidate DB and promote only after both assemble with non-empty 1m/5m bars and all existing integrity/non-shrink/drift gates pass;
6. replace canonical accepted seed outputs only as one rollback-protected pair boundary;
7. on any TV hard failure, leave the accepted pair and DB unchanged, report the named failing ticker/gate, and request IB only then;
8. if IB fallback is authorized, fetch and validate the complete pair from IB rather than silently publishing a mixed-provider pair.

Default automation never uses `--allow-date-loss`. A pair run must not leave a new SPY with an old QQQ or vice versa in the tracked DB, static manifest, or hosted Pages.

The current 46 SPY-only dates are grandfathered history. QQQ begins with the first date successfully accepted through the pair orchestrator; this plan does not silently backfill or suppress older SPY days. The static manifest may therefore contain older SPY-only entries plus paired entries for newer accepted dates. The ticker selector offers both underlyings after QQQ exists, while each ticker owns its available-date list; switching to a ticker without the current date selects that ticker's latest available date and updates the existing hash route with a visible date change. No missing QQQ day is synthesized.

Cross-platform evidence is a default-switch gate. If either Windows or macOS receipt is missing or fails, Phase 5 remains `Blocked`; the current SPY/Tang runbook, workflow, operating-mode carrier text, and public payload stay unchanged, and Phase 6 cannot start.

## 4. Historical Migration And Cutover

### 4.1 One-shot legacy migration

The migration reads every tracked `content/trader-trades/*.json`, emits the corresponding `content/trades/<date>.json`, and assigns `trader_id: tang`.

For each legacy item it must preserve the original date, ticker/symbol, time, side, strike, expiry, action, source, reason type, and note. The extraction allowlist is limited to explicit signed returns attached to result verbs, such as `反馈 +50%`, `14:07 附近 +40% 出清`, or `+30% 止盈出场`. Bare `N% 仓位` is position size and must never become a return; ambiguous phrases such as `40% 结束` remain unparsed and receive a review flag unless a later reviewed exact rule is added. The original note remains unchanged, extracted fields carry `normalization_method: legacy_rule_extract`, and approximate language sets `time_precision: approximate`.

Migration acceptance requires a machine-readable report containing:

- all 20 source paths and target paths;
- source/target trade-group counts per date;
- source/target no-trade notes per date;
- a field-level preservation result for every source trade;
- extracted reported return/time facts and unparsed-review cases;
- a row for every one of the 27 trades and both day-level note entries, including the 2026-05-26 notes-with-trades record and the 2026-05-29 trades-empty record, with the matched allowlist rule or exact non-extraction reason;
- deterministic IDs and repeat-run idempotency;
- zero unaccounted source records.

### 4.2 Candidate-only SQLite migration

No first run may apply destructive DDL directly to the tracked DB. The implementation must:

1. acquire the existing shared DB write lock;
2. make a consistent candidate copy of the tracked DB;
3. apply schema/data migration to the candidate;
4. import and validate canonical traders/trades;
5. backfill one active market dataset per existing market day and re-key bars without changing their ordered values;
6. compare pre/post logical market-day keys, non-market keys, bar counts and ordered bar-field digests, strategy/teaching bodies, integrity, foreign keys, and trade migration counts;
7. reject current-DB drift before promotion;
8. create a recoverable backup and atomically promote only after every invariant passes.

Any mismatch leaves tracked DB bytes unchanged and reports the exact invariant. The rollback test must restore the pre-migration DB and old application commit as one coherent boundary; rolling back only code or only DB is not accepted.

### 4.3 Full cutover

The old JSON files, `backend/app/services/tang_trades.py`, `TangTradeList.jsx`, old `tang_trades` fields/counts, SPY-only workflow variables, and Tang-only runbook instructions are removed only in the Phase 6 atomic cutover after new services/components, migrations, exports, URLs, and rollback have passed independently. That same boundary switches `main.py`, static export, Review/Static consumers, marker rendering, recovery acceptance, Pages workflow, AGENTS/runbook, and the normative operating-mode contract. No earlier phase changes the public member and no adapter keeps emitting the old shape after cutover.

## 5. Exact Planned File Surface

Phase 0 must revalidate this manifest against the post-review repository. A required path outside it triggers a plan revision and renewed design review before edits.

### 5.1 Add

- `content/traders/index.json`
- `content/schemas/traders.schema.json`
- `content/schemas/trades-day.schema.json`
- `content/trades/2026-05-26.json`
- `content/trades/2026-05-27.json`
- `content/trades/2026-05-29.json`
- `content/trades/2026-06-02.json`
- `content/trades/2026-06-08.json`
- `content/trades/2026-06-15.json`
- `content/trades/2026-06-22.json`
- `content/trades/2026-06-23.json`
- `content/trades/2026-06-24.json`
- `content/trades/2026-06-25.json`
- `content/trades/2026-06-29.json`
- `content/trades/2026-06-30.json`
- `content/trades/2026-07-01.json`
- `content/trades/2026-07-02.json`
- `content/trades/2026-07-07.json`
- `content/trades/2026-07-08.json`
- `content/trades/2026-07-09.json`
- `content/trades/2026-07-15.json`
- `content/trades/2026-07-16.json`
- `content/trades/2026-07-17.json`
- `docs/trade-data-contract.md`
- `backend/app/services/trade_records.py`
- `backend/app/services/trade_statistics.py`
- `backend/app/services/trade_exports.py`
- `backend/scripts/migrate_trader_trades.py`
- `backend/scripts/update_spy_qqq_market_day.py`
- `backend/tests/test_trade_records.py`
- `backend/tests/test_trade_migration.py`
- `backend/tests/test_trade_statistics.py`
- `backend/tests/test_trade_exports.py`
- `backend/tests/test_update_spy_qqq_market_day.py`
- `frontend/src/features/review/TraderTradeList.jsx`
- `frontend/src/features/review/TraderFilters.jsx`
- `frontend/src/features/review/TradeExportControls.jsx`
- `frontend/src/pages/AdminTradersPage.jsx`
- `frontend/src/features/review/tradeRecords.js`
- `frontend/src/features/review/tradeRecords.test.js`
- `docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/legacy-migration-report.md`
- `docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/data-safety-acceptance.md`
- `docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/pages-link-regression.md`
- `docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/cross-platform-tv-acceptance.md`

### 5.2 Modify

- `README.md`
- `backend/README.md`
- `backend/app/db.py`
- `backend/app/main.py`
- `backend/app/settings.py`
- `backend/app/services/bar_utils.py`
- `backend/app/services/db_safety.py`
- `backend/app/services/importer.py`
- `backend/scripts/fetch_tv_live_extended_day.py`
- `backend/scripts/fetch_ib_live_extended_day.py`
- `backend/scripts/rebuild_live_extended_db.py`
- `backend/scripts/export_static_reviews.py`
- `backend/scripts/recover_historical_market_days.py`
- `backend/tests/test_db_safety.py`
- `backend/tests/test_rebuild_live_extended_db.py`
- `frontend/package.json`
- `frontend/src/main.jsx`
- `frontend/src/components/Layout.jsx`
- `frontend/src/api/client.js`
- `frontend/src/pages/ReviewPage.jsx`
- `frontend/src/pages/StaticReviewsApp.jsx`
- `frontend/src/kline/kline-engine.js`
- `frontend/src/styles.css`
- `.github/workflows/project-harness.yml`
- `.github/workflows/publish-static-reviews.yml`
- `.harness/config.json`
- `AGENTS.md`
- `INSTRUCTIONS.md`
- `docs/README.md`
- `docs/architecture.md`
- `docs/kline-engine.md`
- `docs/roadmap.md`
- `docs/daily-publish-runbook.md`
- `docs/operating-modes.md`
- `docs/exec-plans/proposed/index.md`
- `docs/exec-plans/active/index.md`
- `docs/exec-plans/completed/index.md`
- `docs/exec-plans/reviews/index.md`
- `docs/exec-plans/roadmap.md`
- `PROGRESS.md`
- `HANDOFF.md`
- `data/sqlite/tang_strategy_live_extended.db` only through the candidate migration/promotion gate in an authorized implementation phase
- this plan and its review/evidence artifacts as lifecycle truth changes

### 5.3 Remove at verified cutover

- `backend/app/services/tang_trades.py`
- `frontend/src/features/review/TangTradeList.jsx`
- all 20 tracked `content/trader-trades/<YYYY-MM-DD>.json` files listed by the Phase 0 manifest

Generated `frontend/public/reviews`, `frontend/dist`, provider diagnostics, temporary candidates, and backups remain untracked/outside governed docs except for the bounded Markdown acceptance summaries named above.

## 6. Phased Execution Plan

### Phase 0 — Baseline, Manifest, And Authority Freeze

- Entry gate: `phase-0-start` after a matching-revision Kimi/Grok design review chain returns the required verdict, the user separately activates the plan, and the user separately instructs implementation start.
- Work:
  - re-run the startup contract and capture branch/HEAD/status, tracked DB identity/hash, table DDL, row counts, logical key sets, bar digests, content inventory, API/static payload samples, Pages manifest/link samples, and workflow/runbook hashes;
  - inventory every planned add/modify/remove path and all 20 legacy files;
  - record Windows evidence as user-reported until a reproducible receipt exists; do not label it a fresh pass;
  - freeze remote/provider/DB authority and stop if the implementation needs an unlisted path or broader contract.
- Verification:
  - governed/focused/auto operating-mode checks and startup budget;
  - SQLite integrity/foreign-key checks and read-only logical digests;
  - current SPY 2026-07-17 assemble/static/hash-route capture;
  - `git diff --check` and exact status classification.
- Exit gate: `phase-0-complete` only when the manifest and preservation matrix are recorded as evidence without runtime/data/provider/publisher mutation; this wording grants no Git commit authority.

### Phase 1 — Canonical Contracts And Pure Validation

- Entry gate: `phase-1-start` after verified Phase 0 closeout.
- Work:
  - add trader/day JSON schemas and `docs/trade-data-contract.md`;
  - freeze the exact `trade_records` API/static response field table, nesting, count keys, null semantics, and public/private allowlists before consumer work;
  - implement pure loaders/validators, stable-ID checks, IANA time/offset validation, fact/default provenance, statuses, eligibility, outcome separation, and deterministic export shapes;
  - implement conservative allowlisted legacy-note extraction and explicit position-size/ambiguous deny rules as a pure tested transformation without writing canonical or tracked DB data yet;
  - define public/private field allowlists so raw evidence cannot leak into JSON, DB, API, CSV, or Pages.
- Verification:
  - valid/invalid schema fixtures across traders, SPY/QQQ, DST/standard time, approximate times, default 0DTE, null fees, adds/partial closes, reported/calculated conflict, void/supersede, and eligibility;
  - round-trip and deterministic-ID tests;
  - raw-evidence forbidden-field tests plus allowlisted return extraction, `N% 仓位` rejection, `40% 结束` review-flag, and complete 27-trade/2-context classification fixtures;
  - no tracked DB, legacy JSON, Pages workflow, or runtime payload diff.
- Exit gate: `phase-1-complete` after the schemas, exact response field table, pure validators, and complete legacy-note classification pass independently of migration.

### Phase 2 — Candidate SQLite Schema, Projection, And Agent Views

- Entry gate: `phase-2-start` after verified Phase 1 closeout.
- Work:
  - implement traders, trade facts/outcomes, logical market-day datasets, analysis runs/context, foreign keys, indexes, and read-only Agent views;
  - re-key bars to `(dataset_id, idx)`, update `bar_tuple_from_seed`, importer/recovery inserts, rebuild semantic counts, and all active bar SELECT helpers to resolve datasets from stable market-day IDs;
  - update `db_safety` and its tests so pre-migration digests read bars by `market_day_id`, post-migration digests read the one active `dataset_id`, and both hash the identical ordered `BAR_COLUMNS` values keyed by logical market day; enforce at-most-one active dataset with a partial unique index and exactly one through candidate validation;
  - build candidate-copy migration and rollback primitives under the existing DB write lock/drift contract;
  - backfill dataset provenance from current market-day source/meta without changing logical day identity or ordered bar facts;
  - import normalized trade fixtures into candidate DB and calculate only eligible results.
- Verification:
  - fresh DB and 46-day candidate-copy migration tests;
  - before/after logical market-day, ordered bar-field digest, strategy, teaching, and non-market preservation matrix across old/new bar ownership schemas;
  - transaction rollback, duplicate ID, invalid FK, concurrent drift, candidate corruption, and byte-unchanged-on-failure tests;
  - Agent view queries for trader/ticker/date/direction/result/market-context filters;
  - exact reported/calculated/gross/net and weighted-cost tests.
- Exit gate: `phase-2-complete` only after candidate safety and Agent-query acceptance pass without promoting the tracked DB.

### Phase 3 — Historical Canonical Migration And General Backend Contract

- Entry gate: `phase-3-start` after verified Phase 2 closeout.
- Work:
  - generate and review all 20 canonical daily files plus trader registry from legacy Tang data;
  - produce the migration report and reconcile every source item;
  - implement general read/admin service handlers, authorization rules, and SQLite import/projection, but do not register the new public routes until the Phase 6 atomic cutover;
  - keep the existing assemble/static `tang_trades` member and all existing consumers unchanged; exercise the new contract through focused service/handler tests only until the Phase 6 atomic cutover;
  - keep old source files until the full cutover gate and do not dual write canonical sources.
- Verification:
  - zero-unaccounted-record migration report, idempotent rerun, exact note preservation, extraction review list;
  - service-handler auth/role/filter/status/eligibility tests without exposed new routes;
  - atomic admin-write failure/recovery tests;
  - focused new-API tests for SPY 2026-07-17 and representative reported-return/no-trade days with expected migrated records, while the existing assemble/static payload remains byte/shape compatible;
  - no tracked DB promotion yet.
- Exit gate: `phase-3-complete` after canonical content and the new backend contract are reviewable, all legacy parity tests pass, and no existing assemble/static consumer has switched.

### Phase 4 — Multi-Trader Frontend, Admin, Statistics, And Downloads

- Entry gate: `phase-4-start` after verified Phase 3 closeout.
- Work:
  - build general trade-record rendering, filters, admin, statistics, and downloads against frozen fixtures without registering live admin/read routes or wiring the existing Review/Static pages to the new public member yet;
  - add SPY/QQQ selector, all-active-trader default, multi-select/focus, fixed colors, CALL/PUT shapes, grouped-marker behavior, group-first statistics, and leg/event drilldown;
  - generalize the live annotation renderer in `kline-engine.js` to accept explicit trader color plus independent CALL/PUT shape while preserving existing Tang markers until cutover; the existing `UnifiedKlineEngine.jsx` pass-through already preserves arbitrary annotation fields and remains untouched, while `DailyReviewChart.jsx` remains untouched because no current Review/Static page imports it;
  - implement admin-only trader settings and validated daily-record editing against the frozen service contract; live backend wiring is part of Phase 6;
  - add current-filter JSON and three-CSV downloads without filter persistence or URL parameters;
  - preserve strategy scanning, 1m/5m display, extended-K toggle, Backtest, and Teaching behavior.
- Verification:
  - add a dependency-free `node --test` script and run pure-function tests for filtering, markers, statistics, eligibility, and exports;
  - production/static builds;
  - admin versus readonly authorization checks;
  - fixture-level proof that reload resets the trader filter, ticker/date availability follows the asymmetric-history contract, and existing hash routes remain stable;
  - downloaded JSON/CSV row/foreign-key reconciliation and raw-evidence absence.
- Exit gate: `phase-4-complete` after the new components and pure contracts pass without changing the default interactive/static payload consumer or performing remote publication.

### Phase 5 — Atomic SPY/QQQ Data Update Acceptance

- Entry gate: `phase-5-start` after verified Phase 4 closeout and a separate explicit provider-run authorization for any real TV/IB call; offline implementation/tests may proceed without provider access.
- Work:
  - generalize seed discovery/import/rebuild to QQQ;
  - add the atomic pair orchestrator and pair-level quality/candidate/rollback contract;
  - update `test_rebuild_live_extended_db.py` refusal/superset fixtures for QQQ without weakening date/non-market preservation;
  - update `backend/README.md` to document QQQ as an accepted internal/candidate seed while keeping the default SPY/Tang daily entry unchanged until Phase 6;
  - keep static export, Pages workflow, AGENTS, runbook, operating modes, and the public payload unchanged while gathering pair receipts;
  - retain TV-first/IB-exception ordering and forbid partial or mixed-provider pair publication.
- Verification:
  - offline fixtures for SPY pass/QQQ fail, QQQ pass/SPY fail, date/session/provider mismatch, candidate failure, tracked-DB drift, seed replacement failure, and full pair success;
  - same-date SPY/QQQ candidate and pair-orchestrator checks plus existing SPY hash-link baseline preservation;
  - Windows and macOS pinned-runtime TV receipts recorded separately; missing platform evidence remains not-run, never pass;
  - IB pair path only if separately authorized after a named TV hard failure;
  - Pages workflow syntax/build locally; no push or hosted claim.
- Exit gate: `phase-5-complete` only after both platform receipts and all pair atomicity checks pass. Missing/failing platform evidence sets Phase 5 to `Blocked`, keeps the current default contract unchanged, and forbids Phase 6 entry.

Execution evidence: macOS and Windows pinned-runtime TradingView receipts both passed for 2026-07-17. The Windows receipt required in-manifest portability fixes for writable file fsync, acquired-only `msvcrt` unlock, Windows-safe directory fsync reuse, and explicit UTF-8 test reads; the unchanged 13 focused tests and 80-test backend suite then passed. The real Windows pair accepted `AMEX:SPY` and `NASDAQ:QQQ` with exact RTH 390/78, zero missing/duplicate RTH minutes, no synthetic padding, a 46 -> 47 temporary candidate preserving 45 non-target grandfathered days, integrity `ok`, zero foreign-key failures, and unchanged tracked DB bytes. Phase 5 is complete; Phase 6 remains unauthorized and has not started.

### Phase 6 — Full Cutover, Tracked Candidate Promotion, And Closeout

- Entry gate: `phase-6-start` after verified Phase 5 closeout and separate explicit authority to promote the candidate tracked DB and perform the declared legacy removals. This is not publication authority.
- Work:
  - take a recoverable pre-cutover DB/content backup outside tracked output;
  - atomically promote the verified candidate DB;
  - in one rollback-coherent boundary, register the new read/admin routes and switch backend assemble, static export, Review/Static/Admin pages, marker rendering, recovery acceptance, manifest/workflow, AGENTS/runbook, root `README.md`, `docs/kline-engine.md`, and `docs/operating-modes.md` from Tang/SPY-specific contracts to `trade_records` and the governed pair path;
  - remove all old Tang JSON/code/payload consumers and prove no dual-write/compatibility path remains;
  - run the complete backend/frontend/harness/data/link/migration/rollback acceptance matrix;
  - reconcile lifecycle evidence and request independent implementation review;
  - keep the plan Active until a qualifying implementation `accept`; only then move to Completed.
- Verification:
  - all repository verification commands;
  - DB integrity/FK, 46 grandfathered SPY days, paired new-date preservation, bar digests, trade counts, Agent views, migrations, API, static export, local browser Review/Backtest/Teaching, JSON/CSV downloads, and backup restore rehearsal;
  - public payload proof that no intermediate build exposes backend `trade_records` to old frontend consumers or emits both public members;
  - secrets/raw-evidence scan and generated-output cleanliness;
  - exact diff showing removal of all `tang_trades` runtime fields/consumers and legacy source files;
  - final independent implementation review against a stable commit;
  - no remote/Pages/hosted pass unless separately authorized and actually observed.
- Exit gate: `phase-6-complete` and lifecycle closeout only after independent `accept`; otherwise remain Active with the exact finding/blocker.

## 7. Data-Safety And Rollback Matrix

| Failure | Required behavior |
| --- | --- |
| Invalid trader/day JSON | Reject before DB or canonical file replacement; report path/field. |
| Legacy migration ambiguity | Preserve note, leave structured field null, mark review required. |
| Percent phrase denotes position size or ambiguous exit text | Do not populate reported return; record the deny/review reason in the migration report. |
| Stable ID collision | Reject entire daily import/migration; do not auto-renumber existing IDs. |
| Timezone/offset mismatch | Reject event; do not silently reinterpret host-local time. |
| One ticker fetch/quality failure | Reject the pair; accepted seeds, DB, static manifest, and Pages remain on prior pair. |
| Grandfathered SPY-only date lacks QQQ | Keep the SPY entry/link; do not synthesize QQQ or treat historical asymmetry as a failed new pair. |
| Provider/date/session mismatch | Reject the pair and report both dataset identities. |
| Candidate loses a market/non-market key or bar value | Reject promotion; tracked DB bytes remain unchanged. |
| Current DB changes during candidate work | Reject on drift token; rebuild from a fresh baseline. |
| Trade result lacks required facts | Keep nullable fact, set eligibility false; never fabricate result. |
| Unknown fee | Gross may exist; net remains null. |
| Reported/calculated conflict | Preserve both, set conflict flag, exclude any combined metric. |
| Admin write fails validation or atomic replace | Preserve previous canonical file; return an actionable error. |
| Static/build/link regression | Stop before legacy removal, DB promotion, commit, or publication. |
| macOS or Windows TV acceptance missing | Mark Phase 5 Blocked, keep the current default contract unchanged, and do not enter cutover. |
| Atomic public payload cutover fails | Restore the coherent pre-cutover code/DB/content boundary; never leave new backend payloads wired to old consumers. |
| Rollback rehearsal fails | Stop cutover; do not remove legacy inputs or promote the candidate. |

## 8. Verification And Evidence Plan

### 8.1 Baseline and recurring repository checks

```bash
git status --short --branch
python3 scripts/check-project-harness.py --root . --profile governed
python3 scripts/check-operating-modes.py --root .
python3 -m unittest scripts.tests.test_operating_modes
python3 scripts/check-startup-doc-budget.py
cd backend && PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'
cd backend && PYTHONPATH=. python3 -m compileall -q app scripts tests
cd frontend && npm run build
git diff --check
```

### 8.2 Plan-specific acceptance

- from Phase 4 onward, `cd frontend && npm run test:trade-records`;
- schema/validator/migration/statistics/export/pair-orchestrator focused suites named in the planned file surface;
- SQLite `integrity_check`, `foreign_key_check`, pre/post logical key and ordered-value digests;
- exact source-to-target legacy record reconciliation for 20 files, 27 trades, and 2 day-level note entries, distinguishing the notes-with-trades and trades-empty dates and including allow/deny extraction reasons;
- SPY 2026-07-17 `tang-v4-4-slope-4-4` assemble plus representative reported-return, no-trade-note, approximate-exit, voided, and incomplete records;
- local static export/build proving grandfathered SPY-only history plus same-date paired SPY/QQQ entries using temporary generated directories;
- real-browser Review/Backtest/Teaching regression through `scripts/start-local-acceptance.sh` against a temporary/candidate DB;
- Windows/macOS TV pair receipts with pinned versions and named quality results;
- existing Pages hash route regression and current-filter JSON/CSV reconciliation;
- rollback rehearsal restoring the old application/DB/content boundary.

Optional or unavailable checks must be recorded as `not run` with reason. No offline fixture may be reported as a real provider, broker, push, Pages, or hosted pass.

### 8.3 Evidence artifacts

- `evidence/legacy-migration-report.md`
- `evidence/data-safety-acceptance.md`
- `evidence/pages-link-regression.md`
- `evidence/cross-platform-tv-acceptance.md`
- phase execution records and final independent implementation review under the plan review directory

Detailed command output belongs in bounded evidence artifacts, not `PROGRESS.md` or `HANDOFF.md`.

## 9. Commit, Remote, And Publication Boundaries

- This proposal authorizes only the proposal and required lifecycle/index/state reconciliation files.
- Design reviews do not authorize activation or implementation.
- The user instruction `2026-07-19-start-dual-review-loop-through-active` authorizes this bounded review/foldback loop and contingent lifecycle activation only after matching-revision dual approval; implementation still requires another explicit start/execute instruction.
- The user instruction `2026-07-19-commit-and-push-branch-for-windows-phase5` authorizes exactly one plan-scoped stage/commit and push of `codex/project-harness` so the Windows checkout can run the outstanding Phase 5 receipt.
- That transfer authority does not authorize a PR, merge, tracked DB mutation/promotion, Phase 6, IB/Gateway access, Pages publication, hosted verification, branch protection, environment, or any other remote setting change. The separately authorized real TradingView receipt boundary remains fail-closed and platform-specific.
- `main` and `gh-pages` remain untouched. All work stays on `codex/project-harness` unless the user separately changes that boundary.

## 10. Design Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/`
- Review rounds: each round freezes one exact plan revision and dispatches Kimi Code and Grok Build independently against that same revision. Neither reviewer may read the other review before both outputs for the round are captured.
- Artifact sequence: reviews use the next monotonic `review-<NNN>.md` names, preserve reviewer identity and round/revision evidence, and remain append-only. Codex records each model's stdout into its own constrained review artifact without changing the reviewer verdict.
- Reviewer contract: each reviewer must independently read current repository evidence, name the exact plan revision, use the constrained review metadata, cite `file:line` evidence, distinguish blocking/non-blocking findings, and remain read-only.
- Foldback rule: if either reviewer returns `revise` or `reject`, Codex verifies the findings against repository evidence, preserves both reviews, updates the plan, assigns a new revision, reconciles lifecycle state, and begins another dual review round on that new revision.
- Required verdict: activation requires the latest Kimi and Grok design reviews both to be `approve` and both to target the exact current plan revision. Earlier verdicts remain preserved but cannot qualify a later revision.
- Progress monitor: after the first-round dispatch, attach a 10-minute heartbeat to the current Codex task. It may inspect reviewer process/log status and resume completed work, but it must not modify the plan before both same-round outputs are captured. Remove the heartbeat when the loop reaches Active or a genuine user decision/blocker stops it.
- Required user approval: the user's explicit `2026-07-19` instruction to use same-revision dual reviews and proceed until Active is the contingent activation instruction for this loop. It grants activation recording only after the required dual approval; review approval does not grant implementation.
- Activation is a separate lifecycle change before implementation.
- Implementation start requires a later explicit start/execute instruction after activation recording.

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
