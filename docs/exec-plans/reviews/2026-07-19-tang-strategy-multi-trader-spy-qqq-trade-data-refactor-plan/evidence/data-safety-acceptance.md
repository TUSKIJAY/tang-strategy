# Multi-Trader Data-Safety Acceptance

## Phase 0 Baseline

- Captured: `2026-07-19`
- Repository: `/Users/neowang/Code/tang-strategy-github`
- Branch: `codex/project-harness`
- HEAD: `25ba77fd9947c504f68cab1c7700d9f5c84d62b4`
- Plan revision: `v5-round-3-review-foldback-2026-07-19`
- Scope: read-only tracked-DB identity, schema, logical-key, count, digest, manifest, and authority freeze
- Result: pass

### Authority freeze

- Allowed in the current instruction: local/offline Phase 0-4 work and Phase 5 offline implementation/tests within the exact plan surface.
- Not authorized: stage, commit, push, PR, merge, Pages publication, hosted verification, provider calls, IB/Gateway access, tracked-DB promotion, Phase 6 removals, or cutover.
- All database work before a separately authorized Phase 6 promotion must use temporary/candidate SQLite copies and remain fail-closed.
- The exact Phase 0 manifest revalidation found no required implementation path outside the reviewed surface.

### Tracked DB identity and validation

Path: `data/sqlite/tang_strategy_live_extended.db`

| Field | Baseline |
| --- | --- |
| Device | `16777233` |
| Inode | `58618000` |
| Size | `12251136` bytes |
| mtime ns | `1784379720383232304` |
| Byte SHA-256 | `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` |
| Logical SHA-256 | `f7ca32e4d621056983c5c2bdae17f78277b8e53a26c12684b34164e30c170a34` |
| Schema SHA-256 | `5bed3527539ec900b8128489dd2e1ed655f0c4f7ea0f2017c73cd9fc93bfb095` |
| `PRAGMA integrity_check` | `ok` |
| `PRAGMA foreign_key_check` | zero rows |
| Sidecars | none observed by `capture_database_token` |

The tracked DB SHA-256 was checked again after the API/static capture against a temporary DB copy and remained `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`.

### Current DDL

```sql
CREATE INDEX idx_market_days_ticker_date ON market_days(ticker, trade_date);
CREATE INDEX idx_strategies_active ON strategies(active, name, version);

CREATE TABLE bars_1m (
    market_day_id INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    ts TEXT,
    time TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    vwap REAL,
    ha_open REAL,
    ha_high REAL,
    ha_low REAL,
    ha_close REAL,
    m5 REAL,
    m10 REAL,
    m20 REAL,
    m30 REAL,
    m50 REAL,
    m60 REAL,
    m120 REAL,
    m200 REAL,
    m250 REAL,
    PRIMARY KEY (market_day_id, idx),
    FOREIGN KEY (market_day_id) REFERENCES market_days(id) ON DELETE CASCADE
);

CREATE TABLE bars_5m (
    market_day_id INTEGER NOT NULL,
    idx INTEGER NOT NULL,
    ts TEXT,
    time TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    vwap REAL,
    ha_open REAL,
    ha_high REAL,
    ha_low REAL,
    ha_close REAL,
    m5 REAL,
    m10 REAL,
    m20 REAL,
    m30 REAL,
    m50 REAL,
    m60 REAL,
    m120 REAL,
    m200 REAL,
    m250 REAL,
    PRIMARY KEY (market_day_id, idx),
    FOREIGN KEY (market_day_id) REFERENCES market_days(id) ON DELETE CASCADE
);

CREATE TABLE market_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    trade_date TEXT NOT NULL,
    session_mode TEXT NOT NULL DEFAULT 'rth',
    source TEXT,
    title TEXT,
    bar_count_1m INTEGER NOT NULL DEFAULT 0,
    bar_count_5m INTEGER NOT NULL DEFAULT 0,
    imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    meta_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(ticker, trade_date, session_mode)
);

CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE strategies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    source_type TEXT NOT NULL DEFAULT 'json',
    json_body TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE teaching_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT 'default',
    slug TEXT NOT NULL,
    json_body TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_type, version, slug)
);

CREATE TABLE tickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT,
    asset_type TEXT NOT NULL DEFAULT 'equity',
    enabled INTEGER NOT NULL DEFAULT 1
);
```

### Row counts and preservation digests

| Surface | Count or SHA-256 |
| --- | --- |
| `tickers` | `1` |
| `market_days` | `46` |
| `bars_1m` | `43425` |
| `bars_5m` | `8821` |
| `strategies` | `11` |
| `teaching_assets` | `3` |
| Ordered logical `bars_1m` digest | `99c508b49bc1139c5bc995ee7cf650a175329c26aca7cdc8c604e6cf6fc2fc8e` |
| Ordered logical `bars_5m` digest | `d62a7429832e9aa64467c7a1e91a5796242ab53eb7e043f9a70ffbccb9ab3be1` |
| Strategy table digest | `7c03ad9aa6b48161ab96d02b1c354fbe9f6393d26f0fe452b2b0d33534cb689a` |
| Teaching table digest | `9ab2647fc700050a0676f416feb12554c3d6c426545fecf1990fb1ce1921fadb` |

The ordered bar digests use the current `BAR_COLUMNS` values and prefix each row with the logical `(ticker, trade_date, session_mode)` ownership through the join; database-local numeric IDs are not preservation identities.

### Exact logical market-day keys

All 46 keys are SPY extended-session keys; QQQ has zero current rows.

```text
SPY|2026-05-12|extended
SPY|2026-05-13|extended
SPY|2026-05-14|extended
SPY|2026-05-15|extended
SPY|2026-05-18|extended
SPY|2026-05-19|extended
SPY|2026-05-20|extended
SPY|2026-05-21|extended
SPY|2026-05-22|extended
SPY|2026-05-26|extended
SPY|2026-05-27|extended
SPY|2026-05-28|extended
SPY|2026-05-29|extended
SPY|2026-06-01|extended
SPY|2026-06-02|extended
SPY|2026-06-03|extended
SPY|2026-06-04|extended
SPY|2026-06-05|extended
SPY|2026-06-08|extended
SPY|2026-06-09|extended
SPY|2026-06-10|extended
SPY|2026-06-11|extended
SPY|2026-06-12|extended
SPY|2026-06-15|extended
SPY|2026-06-16|extended
SPY|2026-06-17|extended
SPY|2026-06-18|extended
SPY|2026-06-22|extended
SPY|2026-06-23|extended
SPY|2026-06-24|extended
SPY|2026-06-25|extended
SPY|2026-06-26|extended
SPY|2026-06-29|extended
SPY|2026-06-30|extended
SPY|2026-07-01|extended
SPY|2026-07-02|extended
SPY|2026-07-06|extended
SPY|2026-07-07|extended
SPY|2026-07-08|extended
SPY|2026-07-09|extended
SPY|2026-07-10|extended
SPY|2026-07-13|extended
SPY|2026-07-14|extended
SPY|2026-07-15|extended
SPY|2026-07-16|extended
SPY|2026-07-17|extended
```

SPY 2026-07-17 per-day digests:

- market day: `fb3eaf23683bdbedbc7bde90cc33c09ba4f0b1d5bcbf6dd92522bd1e12d23625`
- bars 1m: `59a02802a1e6c7b8160a5d064f2d37a362acf7d2867e6aa9d934a6aa2199859d`
- bars 5m: `aca4e275ec082213914c0a9a7c467b6bc1bfbb6e82b8f2372945564eb4585085`

### Frozen exact path manifest

Initial Phase 0 capture found 44 planned additions absent, all 42 literal Modify targets present, and all 22 exact Remove-at-cutover targets present. The four planned evidence files become present through this Phase 0 recording; that expected state transition is not an implementation-surface expansion.

Add paths:

```text
content/traders/index.json
content/schemas/traders.schema.json
content/schemas/trades-day.schema.json
content/trades/2026-05-26.json
content/trades/2026-05-27.json
content/trades/2026-05-29.json
content/trades/2026-06-02.json
content/trades/2026-06-08.json
content/trades/2026-06-15.json
content/trades/2026-06-22.json
content/trades/2026-06-23.json
content/trades/2026-06-24.json
content/trades/2026-06-25.json
content/trades/2026-06-29.json
content/trades/2026-06-30.json
content/trades/2026-07-01.json
content/trades/2026-07-02.json
content/trades/2026-07-07.json
content/trades/2026-07-08.json
content/trades/2026-07-09.json
content/trades/2026-07-15.json
content/trades/2026-07-16.json
content/trades/2026-07-17.json
docs/trade-data-contract.md
backend/app/services/trade_records.py
backend/app/services/trade_statistics.py
backend/app/services/trade_exports.py
backend/scripts/migrate_trader_trades.py
backend/scripts/update_spy_qqq_market_day.py
backend/tests/test_trade_records.py
backend/tests/test_trade_migration.py
backend/tests/test_trade_statistics.py
backend/tests/test_trade_exports.py
backend/tests/test_update_spy_qqq_market_day.py
frontend/src/features/review/TraderTradeList.jsx
frontend/src/features/review/TraderFilters.jsx
frontend/src/features/review/TradeExportControls.jsx
frontend/src/pages/AdminTradersPage.jsx
frontend/src/features/review/tradeRecords.js
frontend/src/features/review/tradeRecords.test.js
docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/legacy-migration-report.md
docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/data-safety-acceptance.md
docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/pages-link-regression.md
docs/exec-plans/reviews/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan/evidence/cross-platform-tv-acceptance.md
```

Modify paths:

```text
README.md
backend/README.md
backend/app/db.py
backend/app/main.py
backend/app/settings.py
backend/app/services/bar_utils.py
backend/app/services/db_safety.py
backend/app/services/importer.py
backend/scripts/fetch_tv_live_extended_day.py
backend/scripts/fetch_ib_live_extended_day.py
backend/scripts/rebuild_live_extended_db.py
backend/scripts/export_static_reviews.py
backend/scripts/recover_historical_market_days.py
backend/tests/test_db_safety.py
backend/tests/test_rebuild_live_extended_db.py
frontend/package.json
frontend/src/main.jsx
frontend/src/components/Layout.jsx
frontend/src/api/client.js
frontend/src/pages/ReviewPage.jsx
frontend/src/pages/StaticReviewsApp.jsx
frontend/src/kline/kline-engine.js
frontend/src/styles.css
.github/workflows/project-harness.yml
.github/workflows/publish-static-reviews.yml
.harness/config.json
AGENTS.md
INSTRUCTIONS.md
docs/README.md
docs/architecture.md
docs/kline-engine.md
docs/roadmap.md
docs/daily-publish-runbook.md
docs/operating-modes.md
docs/exec-plans/proposed/index.md
docs/exec-plans/active/index.md
docs/exec-plans/completed/index.md
docs/exec-plans/reviews/index.md
docs/exec-plans/roadmap.md
PROGRESS.md
HANDOFF.md
data/sqlite/tang_strategy_live_extended.db
```

The plan's self-reference resolves to `docs/exec-plans/active/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`. Existing reviews `review-001.md` through `review-008.md` remain append-only and are not implementation edit targets.

Remove-at-cutover paths:

```text
backend/app/services/tang_trades.py
frontend/src/features/review/TangTradeList.jsx
content/trader-trades/2026-05-26.json
content/trader-trades/2026-05-27.json
content/trader-trades/2026-05-29.json
content/trader-trades/2026-06-02.json
content/trader-trades/2026-06-08.json
content/trader-trades/2026-06-15.json
content/trader-trades/2026-06-22.json
content/trader-trades/2026-06-23.json
content/trader-trades/2026-06-24.json
content/trader-trades/2026-06-25.json
content/trader-trades/2026-06-29.json
content/trader-trades/2026-06-30.json
content/trader-trades/2026-07-01.json
content/trader-trades/2026-07-02.json
content/trader-trades/2026-07-07.json
content/trader-trades/2026-07-08.json
content/trader-trades/2026-07-09.json
content/trader-trades/2026-07-15.json
content/trader-trades/2026-07-16.json
content/trader-trades/2026-07-17.json
```

Phase 6 removal and tracked-DB promotion remain explicitly unauthorized.

### Phase 0 verification

| Check | Result |
| --- | --- |
| `python3 scripts/check-project-harness.py --root . --profile auto` | pass |
| `python3 scripts/check-project-harness.py --root . --profile governed` | pass |
| `python3 scripts/check-operating-modes.py --root .` | pass before and after Phase 0 start transition |
| `python3 -m unittest scripts.tests.test_operating_modes` | pass: 146 tests |
| `python3 scripts/check-startup-doc-budget.py` | pass; no archive required and no hard limit exceeded |
| `git diff --check` | pass |
| SQLite integrity/foreign keys | pass / zero rows |
| API/static capture using system `python3` | not passed: `ModuleNotFoundError: fastapi` |
| API/static capture using `backend/.venv/bin/python` and a temporary DB copy | pass |
| Tracked DB hash preservation during capture | pass; before equals after |

The missing global FastAPI package is an environment-selection observation, not a repository regression and not reported as a pass.

Phase 0 exit gate is closed. Phase 1 began only after the final governed/auto/focused checks, 146 fixtures, SQLite integrity/FK/hash recheck, startup budget, `git diff --check`, and exact Git status all passed.

## Phase 1 Acceptance

| Check | Result |
| --- | --- |
| Trade-focused backend suite | pass: 34 tests |
| Complete pinned backend suite | pass: 53 tests; dependency deprecation warnings only |
| Backend compileall | pass |
| Trader/day schema JSON parse | pass |
| Pure SPY/QQQ, DST/standard, approximate/incomplete time, 0DTE default, null-fee, status/eligibility, outcome-conflict fixtures | pass |
| Weighted adds/partial closes and reported/calculated separation | pass |
| Deterministic public JSON and three CSVs with reconciled foreign keys | pass |
| Recursive raw-evidence forbidden fields and public/private allowlists | pass |
| Complete legacy classifier | pass: 20 files, 27 trades, 2 contexts, 4 reported returns, 3 approximate exits, 1 review flag |
| Canonical trader registry/day files written | no; intentionally deferred |
| Tracked DB/legacy JSON/current runtime/Pages workflow/runbook diff | zero |
| Tracked DB SHA-256 | unchanged: `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` |
| Governed/focused lifecycle checks after remediation | pass |

The first lifecycle check in this phase correctly rejected an Active-index evidence link to a phase artifact. The row was restored to the constrained latest qualifying design review (`review-008`), after which governed and focused checks passed. Phase evidence remains in this bounded directory rather than replacing the required index review carrier.

Phase 1 exit gate is closed without changing the current `tang_trades` payload or creating canonical migrated content.

## Phase 2 Candidate SQLite Acceptance

Phase 2 used only temporary candidate databases. The tracked DB was opened through the existing consistent-snapshot/read-only token path and was never promoted or replaced.

### Actual 46-day candidate preservation

| Invariant | Before | Candidate | Result |
| --- | --- | --- | --- |
| Logical market DB SHA-256 | `f7ca32e4d621056983c5c2bdae17f78277b8e53a26c12684b34164e30c170a34` | same | pass |
| Market days / active datasets | `46` / n/a | `46` / `46` | pass |
| 1m / 5m ordered bars | `43,425` / `8,821` | `43,425` / `8,821` | pass |
| All logical day hashes | 46 captured old-owner rows | 46 active-dataset rows | all identical |
| Strategies SHA-256 | `7c03ad9aa6b48161ab96d02b1c354fbe9f6393d26f0fe452b2b0d33534cb689a` | same | pass |
| Teaching SHA-256 | `9ab2647fc700050a0676f416feb12554c3d6c426545fecf1990fb1ce1921fadb` | same | pass |
| SQLite integrity / FK failures | `ok` / `0` | `ok` / `0` | pass |
| Active-dataset count failures | n/a | `0` | pass |
| Candidate schema SHA-256 | n/a | `efa524d24e682ed9bb2f534d32bb1c3ec4363690ac94c896121b3b8b49ed15ef` | recorded |

Bootstrap provenance is stored in one `market_datasets` row per existing logical day. `bars_1m` and `bars_5m` use `(dataset_id, idx)` in the candidate while `day_sha256` and `logical_database_sha256` hash the same ordered `BAR_COLUMNS` values under the stable logical market-day key. The partial unique index enforces at most one active dataset and candidate validation enforces exactly one.

### Normalized projection and Agent surfaces

The pure 20-file legacy fixture was projected into the actual 46-day candidate:

| Table | Rows |
| --- | ---: |
| `traders` | 1 |
| `trade_groups` | 27 |
| `trade_legs` | 27 |
| `trade_events` | 30 |
| `trade_outcomes` | 4 reported, 0 calculated |
| `trade_note_contexts` | 2 |

The four reported outcomes remain `[50.0, 40.0, 40.0, 30.0]`; no premium, quantity, fee, or calculated result was inferred from legacy text. Agent queries passed through `v_active_market_datasets`, `v_trade_group_performance`, `v_trade_event_facts`, and `v_trade_market_context` for trader/ticker/date/direction/reported-result and analysis-run/dataset lineage filters.

### Failure, ownership, and compatibility matrix

| Check | Result |
| --- | --- |
| Fresh target DB schema | pass |
| Old-owner to dataset-owner migration | pass with identical logical/day hashes |
| Duplicate active dataset | rejected by partial unique index |
| Zero active dataset | rejected by exactly-one candidate validator |
| Invalid foreign key during migration | transaction rejected; live bytes unchanged |
| Duplicate stable trade ID | rejected by repository validator/PK path |
| Concurrent live drift | candidate acceptance rejected; concurrent live write preserved |
| Corrupt candidate | existing fail-closed rebuild fixture rejected; live bytes unchanged |
| Target importer repeated day | old dataset superseded; exactly one new active owner |
| Recovery old-owner source to target candidate | pass at 868/192 with identical day hashes |
| Rebuild semantic count validation on target ownership | pass |
| Complete pinned backend suite | pass: 60 tests; dependency deprecation warnings only |
| Backend compileall / `git diff --check` | pass / pass |

Tracked DB SHA-256 before and after every actual-candidate run remained `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. No candidate was promoted, no canonical daily file was written, and no provider, IB, remote Git, workflow, Pages, or hosted action ran.

Phase 2 exit gate is closed. Phase 3 may write only the planned canonical registry/daily content and general backend contract while the current public `tang_trades` member remains unchanged until the separately authorized Phase 6 boundary.

## Phase 3 Canonical And Backend-Handler Acceptance

| Check | Result |
| --- | --- |
| Registry + canonical documents | pass: 1 registry + 20 daily files |
| Pure render parity / aggregate SHA-256 | 21/21 exact / `f22c5866cea04f39ec772b7542f75f06b1537bcae860668773dd7dd2da589a7e` |
| Source reconciliation | pass: 27 groups, 2 contexts, zero unaccounted, all notes preserved |
| Extraction boundary | pass: 4 reported outcomes, 3 approximate exits, 1 review row, zero position-size promotion |
| Rerun idempotency | pass; default migration command reports `wrote_canonical=false` |
| Read-handler roles/filters | pass: readonly/admin, trader, ticker, exact/range date, status, review, eligibility |
| Representative results | pass: 2026-07-17, 2026-06-08 reported set, 2026-05-29 context-only day |
| Admin authorization | readonly write rejected; admin accepted |
| Atomic write failure/recovery | forced replacement failure preserved original bytes and removed candidate temp file; success fsynced and replaced |
| Candidate SQLite projection | pass: 1/27/27/30/4/2 rows; duplicate rerun rejected and rolled back |
| Route registration | none; private handlers only |
| Existing API/static | exact Phase 0 hashes and `tang_trades`-only shape preserved |
| Complete pinned backend suite / compileall | pass: 65 tests / pass; dependency deprecation warnings only |
| Governed/auto/operating-mode/startup/diff checks | pass |

Tracked DB SHA-256 remains `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`; legacy JSON, Pages workflow, daily runbook, AGENTS, and normative operating modes remain unchanged. No provider, IB, tracked DB promotion, Phase 6, remote Git, or Pages action ran.

Phase 3 exit gate is closed. Phase 4 may build fixture-driven frontend/admin/statistics/download components, but it may not register the new routes or wire existing Review/Static consumers to the new public member.

## Phase 4 Fixture-Driven Frontend Acceptance

| Check | Result |
| --- | --- |
| Pure frontend suite | pass: 10 dependency-free `node --test` tests |
| Filters | pass: SPY/QQQ availability, all-active default, multi-select/focus, empty selection, status/review/eligibility, reload reset |
| Markers | pass: fixed trader color independent from CALL/PUT triangle shape; same-bar trader/direction events coalesce into one grouped marker |
| Statistics | pass: group-first reported and calculated series remain separate |
| Admin/editor authorization | pass: only `admin` enables frozen-contract editors; readonly/anonymous reject |
| Drilldown and downloads | pass: group -> leg -> event UI; current-filter JSON plus three CSVs; exact selection metadata, group/context/count synchronization, row/FK reconciliation, and private/raw field rejection |
| K-line compatibility | existing `tang_trade` branch retained; additive `trade_record` renderer accepts explicit color/shape; `UnifiedKlineEngine.jsx` and `DailyReviewChart.jsx` untouched |
| Production/static Vite builds | pass: 1,751 modules transformed in each mode |
| Local real-browser regression | pass against a temporary 46-day DB snapshot: SPY 2026-07-17 Review assembled with Tang trade plus 1m/5m/Step; latest-10-day Backtest returned 43 signals and exercised Step/5m; Teaching loaded 7 rules / 6 cases / 3 groups and exercised advance/5m/full-day reveal; only the existing `favicon.ico` 404 appeared |
| Complete pinned backend suite / compileall | pass: 65 tests / pass |
| Governed/auto/operating-mode/startup/diff checks | pass: includes 146 operating-mode fixtures |

The preview components are parsed by the build but are not rendered by a route. `ReviewPage.jsx` and `StaticReviewsApp.jsx` remain on their existing payload and Tang components, and no new backend route is registered. Generated `frontend/dist` was ignored and moved intact to `/tmp/tang-phase4-dist.mmdVLC/dist` after verification.

Tracked DB SHA-256 remains `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. No provider, IB, tracked DB promotion, default/public consumer cutover, remote Git, workflow, Pages, or hosted action ran.

Phase 4 exit gate is closed. Phase 5 may implement and test internal SPY/QQQ candidate/pair capability offline. Real TV/IB calls still require separate authorization, and missing platform receipts cannot be treated as a pass.

## Phase 5 Offline Pair Acceptance

### Internal implementation and refusal matrix

| Check | Result |
| --- | --- |
| Seed discovery/import/rebuild | pass: SPY, QQQ, and existing SPX formats; same-date SPY/QQQ rebuild fixture |
| Pair fetch boundary | pass: both tickers staged with import disabled; SPY-pass/QQQ-fail and QQQ-pass/SPY-fail leave accepted seeds/DB untouched |
| Pair identity | pass: exact SPY+QQQ, same NYSE date, `extended` session, and same provider; date/session/provider mismatches reject |
| Calendar and quality | pass: non-session dates reject; claimed RTH counts must equal the NYSE schedule and every bar `ts` must resolve to the declared New York date, correct offset/instant, matching `t`, and exact ordered RTH schedule (390/78 for the regular-day fixture); missing/duplicate/synthetic/date/offset/display-time mutations reject |
| Candidate contract | pass: target-schema migration, exactly one active dataset, non-empty 1m/5m pair, strategy/teaching value preservation, exact market-key superset, grandfathered day hashes |
| Rollback matrix | pass: candidate failure, tracked-DB drift, and second-seed replacement failure all preserve the correct prior/concurrent state |
| Full pair success | pass: one same-provider candidate and both seed files accepted together in temporary fixtures |
| Pair concurrency and offline CLI boundary | pass: one pair-level cross-platform file lock spans seed/DB acceptance; a concurrent pair run times out before writes; `--staged-payload-dir` refuses the tracked DB or accepted-seed defaults and requires explicit temporary targets |
| Cross-platform local lock carrier | pass: POSIX `flock` and dependency-free Windows `msvcrt` one-byte nonblocking-lock branches; Windows directory fsync uses the documented Python portability fallback |
| Focused/full suites | pass: 13 pair tests; 13 rebuild tests; 11 DB-safety tests; 80 complete pinned backend tests; compileall |

### Actual 46-day DB-copy acceptance

The completion audit reran current code against `/tmp/tang-phase5-current.N9HN1F/live.db`, copied byte-for-byte from the tracked DB. The pair was the clearly labeled offline synthetic TradingView fixture for NYSE session 2026-05-11; it is not provider evidence and was never written under tracked seed/data paths.

| Invariant | Result |
| --- | --- |
| Baseline byte/logical SHA-256 | `76a885c2...28f8` / `f7ca32e4...70a34` |
| Candidate byte SHA-256 | `1503359defd0b276f9ee8806e934c70ce6e2317cc9f7c10d62e96121f9ea3d05` |
| Market days | 46 baseline -> 48 candidate (46 grandfathered SPY keys + SPY/QQQ fixture pair) |
| Grandfathered day hashes | 46/46 preserved |
| Pair bars | SPY 390/78; QQQ 390/78 |
| Integrity / FK / active datasets | `ok` / zero / exactly one per day |
| Cleanup warnings | none |

The current complete pinned backend suite passed at 80 tests after the real-provider subprocess-bootstrap and SPY/QQQ exchange-routing repairs; frontend pure tests passed at 10; both normal and static builds passed at 1,751 transformed modules. The real-browser Review/Backtest/Teaching regression passed against a temporary tracked-DB snapshot. The 146 operating-mode fixtures, governed/auto checks, startup budget, compileall, YAML parsing, and `git diff --check` also passed.

Tracked DB SHA-256 remains `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. The public API hash remains `95132bc6...0387` with 868/192/1 and `tang_trades` only. No provider, IB, tracked DB promotion, public/default cutover, stage/commit, remote Git, workflow run, Pages, or hosted action ran.

Phase 5 offline work and both real TradingView receipts are accepted. The first Windows pinned-runtime attempt at `codex/project-harness@ea3c264ddebb7c6a3f3f2b537b62daec2ee6c6b6` correctly failed before provider access and exposed Windows descriptor, lock-release, directory-fsync, and default-encoding defects. After the user authorized in-manifest fixes, the unchanged 13 focused tests passed, all 80 backend tests and compileall passed, and the real pair receipt accepted SPY 868/192 plus QQQ 915/191 with exact RTH 390/78, zero missing/duplicate RTH minutes, and no synthetic padding. The temporary candidate contains 47 days, preserves all 45 non-target grandfathered days, reports integrity `ok` and zero FK failures, and hashes to `b2ed0567648113800dd2966e394633330603e61f9c4fd928b621b645aa36a5ff`. Tracked DB before/after remained `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. The receipt remains under `C:\Users\LENOVO\AppData\Local\Temp\tang-tv-windows-receipt-ffac6bf6699e4aeabdcb4b81a3912d40`; no IB, repository seed, tracked DB, Pages, hosted, or Phase 6 action occurred.

## Phase 0-5 Completion Audit

The final local/offline audit treated completion as unproven and remapped the reviewed plan to current-state evidence after the timestamp, pair-contention, export-selection, and browser-evidence repairs:

| Reviewed requirement | Current authoritative evidence | Audit result |
| --- | --- | --- |
| Exact implementation surface | `git status --porcelain=v1 -uall` contains 75 changed/untracked paths; every path is in the frozen Add/Modify/lifecycle/review surface and all eight design reviews remain append-only | pass |
| Stage/commit boundary | `git diff --cached --name-only` contains zero paths; HEAD remains `25ba77fd9947c504f68cab1c7700d9f5c84d62b4` | pass |
| Canonical schemas and validators | Complete pinned backend suite covers exact keys, SPY/QQQ, IANA offset rules, defaults/provenance, statuses, eligibility, outcomes, raw-field rejection, and deterministic payload/export behavior | pass |
| Legacy migration | 20 files / 27 groups / 2 contexts reconcile with zero unaccounted rows and 21/21 exact deterministic renders | pass |
| Candidate SQLite and Agent queries | Current tests cover 46 active datasets, identical grandfathered bar facts, rollback/drift/FK gates, separate result filters, completeness eligibility, event facts, and analysis-run/dataset lineage | pass |
| Backend cutover boundary | New read/admin handlers remain unregistered; current assemble/static payload remains `tang_trades` only with exact API/static baseline hashes | pass |
| Frontend fixture contract | 10 Node tests plus normal/static builds cover asymmetric history, filters/focus, markers, statistics, admin role, drilldown, exact-filter JSON/CSV selection and FK/context/count reconciliation | pass |
| Existing browser behavior | Real Chromium Review/Backtest/Teaching regression passed against the temporary tracked-DB snapshot; all observed product/API requests returned success | pass |
| Pair quality and atomicity | 13 pair tests cover both one-sided fetch failures, identity/calendar/actual-timestamp mutations, candidate failure, DB drift, seed rollback, pair contention, tracked-target refusal, absolute provider-subprocess bootstrap, SPY/QQQ exchange routing, and complete pair success | pass |
| Actual 46-day-copy acceptance | Current code promoted only `/tmp/tang-phase5-current.N9HN1F/live.db`: 46 -> 48, all 46 grandfathered day hashes preserved, SPY/QQQ 390/78, integrity `ok`, zero FK rows | pass, offline fixture only |
| Public/static compatibility | SPY day hash remains `b3d14fd0...a44a`; QQQ fixture export is ticker-specific; both expose only the current member and existing hash-route shape | pass, local only |
| Tracked DB preservation | Before/current SHA-256 is `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`; integrity `ok`, zero FK rows | pass |
| Coherent pre-cutover rollback boundary | A read-only `git archive HEAD` rehearsal under `/tmp/tang-precutover-rollback.ZcsySr` restored the old application, unchanged tracked-DB bytes, all 20 legacy trade files, no canonical registry/days, and matching API/static output (`95132bc6...0387` / `b3d14fd0...a44a`, 868/192/1, `tang_trades` only) | pass, temporary rehearsal only |
| macOS and Windows real TV receipts | Both real pinned-runtime receipts passed with exact RTH 390/78 for SPY/QQQ, same-date/session/provider identity, temporary 46 -> 47 candidate acceptance, grandfathered preservation, integrity/FK, and unchanged tracked DB; the Windows receipt includes the initial fail-closed portability finding and verified remediation | macOS pass / Windows pass |
| IB, hosted workflow, Pages, Phase 6 | No authorized TV hard failure opened IB; remote/publication/cutover authority is absent | not run / forbidden |

Therefore the Phase 5 exit gate is satisfied and the phase is complete. This does not authorize Phase 6, tracked-DB promotion, legacy removal, public/default cutover, Git publication, Pages, or hosted verification.

## Phase 6 Tracked Promotion, Legacy Removal, And Local Cutover Acceptance

The user instruction `user-instruction:2026-07-19-authorize-phase6-cutover` authorized the local tracked-DB promotion, the exact declared legacy removals, and the formal runtime/static/default cutover. It did not authorize another stage/commit/push, PR, merge, Pages publication, hosted verification, or IB access.

### Recoverable boundary and rollback rehearsal

- Recovery root: `/tmp/tang-phase6-precutover.im4S4p`.
- Byte-for-byte pre-cutover DB: `tang_strategy_live_extended.pre-cutover.db`, SHA-256 `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`.
- SQLite-consistent promotion backup: `tang_strategy_live_extended.atomic-promotion-backup.db`, byte SHA-256 `566025ca4c036c4e73c14e9fbf39de11585f4b1684a137dc44f689275ab865e1`; its logical market SHA-256 is the same `f7ca32e4d621056983c5c2bdae17f78277b8e53a26c12684b34164e30c170a34` as the byte-for-byte backup and promoted DB.
- Pre-cutover repository archive: `repository-head.tar`, SHA-256 `372aec0d7c74b2837ffcd9f9dffef5ac5930cecd2a06144e6140d3c853e32d33`.
- The recovery root retains all 20 removed legacy JSON files and the generated browser/static artifacts used for local acceptance.
- The isolated restore under `rollback-rehearsal/` used the archived old application, restored DB, and restored 20-file legacy directory. The old exporter produced 46 days; `days/spy-2026-07-17-extended.json` contained four old Tang overlay rows, contained `tang_trades`, did not contain `trade_records`, and the restored DB passed integrity/FK with the exact pre-cutover byte hash.

### Candidate and atomic tracked promotion

| Invariant | Result |
| --- | --- |
| Candidate byte SHA-256 | `4a5bce13a4d9da31850ad1b04e616c58ce55b614bc88dbb8ecc04466f7442c34` |
| Pre/promoted logical market SHA-256 | `f7ca32e4d621056983c5c2bdae17f78277b8e53a26c12684b34164e30c170a34` / identical |
| Tracked DB byte SHA-256 | `76a885c2...28f8` -> `4a5bce13...2c34` |
| Market keys and day digests | 46 -> 46; exact key sets; 0/46 digest mismatches |
| Market datasets / active owners | 46 / exactly one per day |
| Bars | 43,425 1m / 8,821 5m |
| Trade projection | 1 trader / 27 groups / 27 legs / 30 events / 4 outcomes / 2 contexts |
| Agent views | active datasets 46 / group performance 27 / event facts 30 / context rows 0 before any analysis run |
| SQLite integrity / FK | `ok` / zero rows |
| Promotion behavior | adjacent verified backup + compare-and-swap; candidate consumed; post-validation passed |

The tracked DB intentionally remains the 46 grandfathered SPY-only market-day set. No QQQ market day was fabricated or copied from the Phase 5 receipt; the first future authorized daily pair acceptance will add SPY and QQQ together through the governed pair orchestrator.

### Atomic consumer/default cutover and removals

- Registered `/api/trade-records`, `/api/admin/traders`, and `/api/admin/trade-records`; assemble/static output now contains only `trade_records` and never emits the old public member.
- Review, Static, Admin, and K-line consumers use normalized trader/group/leg/event data, trader-owned color, and direction-owned marker shape. A real-browser finding that the async Admin payload initially left filters/registry empty was repaired; reload then showed Tang selected, one registry trader, and one 2026-07-17 group.
- Import/rebuild, recovery acceptance, static export, Pages workflow, project harness, AGENTS/runbook, architecture, roadmap, K-line, and operating-mode carriers now use the normalized pair-first contract.
- Exactly 22 declared removals are present: 20 legacy JSON files, `backend/app/services/tang_trades.py`, and `frontend/src/features/review/TangTradeList.jsx`; no other file is deleted.
- Runtime/normative scan returned zero `tang_trades`, `TangTradeList`, `services.tang_trades`, or old K-line branch hits. Historical provenance strings in the migration utility/tests are not runtime or compatibility consumers.
- Default-carrier scan returned zero `TANG_STATIC_TICKER`, `--ticker SPY`, or direct one-symbol TV-fetch commands in the workflow, AGENTS daily entry, and daily runbook.
- Secret scan returned zero high-risk credential patterns in the non-DB diff; no raw evidence is present in public API/static/download payloads; no untracked/generated output remains.

### Local acceptance matrix

| Check | Result |
| --- | --- |
| Pinned backend suite / compileall | pass: 75 tests / pass after promotion |
| Frontend pure suite | pass: 11 tests, including async Admin hydration regression |
| Normal/static Vite builds | pass: 1,750 modules transformed in each mode |
| API cutover | SPY 2026-07-17 at 868/192/1; keys end in `trade_records`; sorted compact SHA-256 `e0cf279a2c296f3b0b166685328e6a775953665c8fa43c000b13e3e6f4af8b08` |
| Static cutover | 46 SPY reviews, 9 strategies; day SHA-256 `154d8dd9d4a4eb592457517a2bec306a2179e6023a656585532a98abf45f3105`; 868/192/1; no old member |
| Review browser | normalized Tang CALL group and filters rendered; JSON plus three CSV downloads completed |
| Backtest browser | latest 10 days produced 43 signals and loaded unified K-line output |
| Teaching browser | 7 rules / 6 cases / 3 training groups loaded |
| Admin browser | admin-only route loaded Tang registry and 2026-07-17 normalized group after hydration repair; no save was invoked |
| Browser console | product/API requests passed; only existing `favicon.ico` 404 |
| Acceptance DB protection | tracked DB remained `4a5bce13...2c34` throughout temporary-snapshot browser run |
| Rollback rehearsal | pass against coherent old app/DB/content boundary |
| Governed/auto/operating-mode/startup | pass / pass / 146 tests / pass |
| Workflow YAML / launcher syntax / diff | pass / pass / `git diff --check` pass |

At the pre-commit acceptance checkpoint, the local Phase 6 matrix passed but the plan remained Active at `phase-6:blocked` because its exit gate required an independent implementation `accept` against a stable implementation commit. The earlier Windows-transfer authority was consumed and no new commit authority existed at that checkpoint. No push, PR, merge, workflow run, Pages publication, hosted verification, IB access, or broker action occurred.

### Phase 6 Implementation Review 001 And Remediation-r1

Stable implementation commit `f92e273b0153eefac14e5c54f94926a2bd4e707e` received `implementation-review-001: revise/high`. The reviewer and coordinator independently reproduced the same isolated failure against temporary canonical content plus a temporary tracked-DB copy: forced deletion failure for the verified `.trade-sync-*.backup.db` escaped after successful DB promotion, the admin writer restored old content, and the DB retained the new note (`content_rolled_back=true`, `db_contains_candidate=true`, `content_db_equal=false`). Repository content and the tracked DB were not used as write targets.

Remediation-r1 makes verified-backup deletion non-transactional after successful promotion. Cleanup failure now retains the verified backup, returns success with `cleanup_warnings`, and leaves both canonical content and the DB on the new coherent boundary. The new full-chain fault-injection regression and an independent temporary-copy replay produce `error=None`, new content/new DB, `content_db_equal=true`, one cleanup warning, and one retained verified backup. The complete pinned backend suite now passes 76/76 plus compileall; frontend remains 11/11 with both 1,750-module builds; 146/146 fixtures, governed/auto/startup/diff checks, and tracked DB SHA-256 `4a5bce13...2c34` pass. Independent re-review remains required before Phase 6 closeout.

### Phase 6 Independent Acceptance

`implementation-review-002` independently reviewed remediation commit `b9dc84d00ff6a61ca6b6063352d8ed2ad6d31055` and returned `accept/high`. Its isolated replay confirmed new content/new DB equality, one cleanup warning, and one retained verified backup; 1/1 focused regression, 76/76 backend, 11/11 frontend, two builds, 146/146 fixtures, compile/harness/startup/diff checks, and SQLite integrity/FK passed. The review did not run or claim hosted/Pages, IB, new provider receipts, push/PR/merge, or the complete browser matrix. Phase 6 is complete and eligible for local lifecycle closeout.
