# Tang Strategy Trade Data Contract

- Contract version: `trade-records-v1`
- Canonical trader schema: `traders-v1`
- Canonical daily schema: `trades-day-v1`
- Canonical timezone: `America/New_York`
- Supported underlyings: `SPY`, `QQQ`
- V1 position scope: single-leg long-premium intraday options

This contract freezes the normalized source, response, eligibility, privacy, and export shapes before backend or UI cutover. Canonical JSON is reviewable source data. SQLite is a rebuildable projection. The Phase 6 public switch replaces `tang_trades` with `trade_records`; no phase may emit both members as a compatibility layer.

## 1. Canonical Files

`content/traders/index.json` contains exactly:

| Field | Type | Semantics |
| --- | --- | --- |
| `schema_version` | string | Exact value `traders-v1`. |
| `traders` | array | Stable trader registry sorted by `sort_order`, then `trader_id`. |

Each trader contains `trader_id`, `display_name`, `color`, `active`, and `sort_order`. `trader_id` is an immutable lowercase slug. Display fields may change without changing references. Referenced traders may be deactivated but not silently removed. Colors are six-digit hex values and must remain distinct.

Each `content/trades/YYYY-MM-DD.json` contains exactly:

| Field | Type | Semantics |
| --- | --- | --- |
| `schema_version` | string | Exact value `trades-day-v1`. |
| `trade_date` | ISO date | New York trade date and filename identity. |
| `timezone` | string | Exact value `America/New_York`. |
| `trade_groups` | array | All traders and both supported underlyings for this date. |
| `note_contexts` | array | Day-level context that is not a trade or fabricated trade event. |

The machine-readable schemas are `content/schemas/traders.schema.json` and `content/schemas/trades-day.schema.json`. The Python validator is authoritative for cross-file ID uniqueness, IANA offset checks, eligibility, and behavioral invariants that JSON Schema cannot express alone.

## 2. Stable Identity And Hierarchy

The hierarchy is `trader -> trade_group -> trade_leg -> trade_event`. IDs are persisted facts:

- group: `tg_20260718_tang_spy_001`;
- leg: `<trade_group_id>_l1`;
- event: `<leg_id>_e1`, `<leg_id>_e2`, and so on;
- day context: `ctx_20260718_tang_spy_001`.

Legacy migration assigns IDs from date, trader, ticker, and immutable source order. New records receive IDs once at normalization time. Time, strike, premium, quantity, result, display name, color, and note edits never recompute an existing ID. Duplicate IDs anywhere in the repository reject the complete validation/import operation; existing IDs are never silently renumbered.

V1 validates exactly one `option` leg with `position_side: long`; the group direction and leg `option_type` must both be `CALL` or both be `PUT`. Event sequence starts at 1, is contiguous, begins with `buy_open`, and then permits `buy_add`, `sell_partial`, and `sell_close` in chronological order.

## 3. Time, Defaults, And Nulls

- Known event time uses ISO-8601 with an explicit offset plus `time_precision: exact|minute|approximate` and `time_incomplete: false`.
- The validator converts the timestamp to `America/New_York`, requires the daily date to match, and compares the supplied offset to installed IANA rules. Fixed UTC-4 is forbidden.
- An explicitly incomplete point uses `occurred_at: null`, `time_precision: null`, and `time_incomplete: true`. No host-local interpretation is allowed.
- Missing expiry becomes the New York `trade_date` with `expiry_provenance: rule_default`; V1 is 0DTE only.
- Contract multiplier may default to `100` only with `contract_multiplier_provenance: rule_default`.
- Unknown strike, premium, quantity, fees, exit, reported result, or calculated result is `null`. Unknown fees are never converted to zero.
- `fact_provenance` distinguishes `user_provided`, `legacy_preserved`, `legacy_rule_extract`, `rule_default`, and `unknown` facts.

## 4. Status, Review, And Eligibility

`status` is `active`, `voided`, or `superseded`; records are not physically deleted. `review_status` is `pending` or `verified`.

The three eligibility flags are independent:

| Flag | Meaning |
| --- | --- |
| `display_eligible` | The normalized point may appear in an interactive chart/list. |
| `reported_stats_eligible` | An explicit normalized trader-reported result exists. |
| `calculated_stats_eligible` | Complete fills support the declared calculation and the position is fully closed. |

Voided/superseded records set all eligibility flags false. Formal static/Pages export later selects only `active + verified`; that publication filter does not reinterpret source facts.

`reported_outcome` and `calculated_outcome` remain separate objects. A reported return never creates missing premium, quantity, fee, or dollar P&L. V1 calculated results use weighted-average long-premium cost across adds and partial closes. Gross fields may exist when fees are unknown; net P&L remains `null` unless every included event fee is explicitly known, including explicit zero.

If reported and calculated return percentages differ after two-decimal display rounding, both remain visible and `result_conflict` is `true`. Statistics never blend the reported and calculated series.

## 5. SQLite Projection And Agent Queries

`market_days` keeps the stable logical `(ticker, trade_date, session_mode)` identity. Each accepted day has exactly one active `market_datasets` row; the partial unique index prevents more than one, and candidate acceptance rejects zero. Candidate bars use `(dataset_id, idx)` and never select a provider snapshot directly from a trade record.

Canonical source facts project into `traders`, `trade_groups`, `trade_legs`, `trade_events`, `trade_outcomes`, and `trade_note_contexts`. `occurred_at_utc` is a normalized projection of the offset-bearing canonical fact. `reported` outcome rows remain normalized source facts; `calculated` outcome rows are derived only from calculation-eligible complete fills. `analysis_runs` and `trade_market_context` are disposable/versioned derived data tied to the exact event and dataset; Agent analysis never overwrites canonical facts or reported results.

Stable read-only query surfaces are:

- `v_active_market_datasets` for the one current provider snapshot per logical day;
- `v_trade_group_performance` for trader/ticker/date/direction/status and separate reported/calculated result filters;
- `v_trade_event_facts` for ordered fill/time facts;
- `v_trade_market_context` for versioned event-to-bar analysis lineage.

Examples:

```sql
SELECT trader_id, trade_date, direction, reported_return_pct, calculated_return_pct
FROM v_trade_group_performance
WHERE underlying='SPY' AND status='active' AND review_status='verified'
ORDER BY trade_date, trade_group_id;
```

Result-class and completeness filters use the explicit outcome/eligibility columns rather than note parsing:

```sql
SELECT trade_group_id, trader_id, reported_return_pct
FROM v_trade_group_performance
WHERE underlying='SPY'
  AND reported_stats_eligible=1
  AND reported_return_pct>0;

SELECT trade_group_id, calculated_stats_eligible
FROM v_trade_group_performance
WHERE underlying='SPY' AND calculated_stats_eligible=0;
```

```sql
SELECT event_id, occurred_at_utc, premium, quantity, fees
FROM v_trade_event_facts
WHERE trader_id='tang' AND underlying='SPY'
  AND trade_date BETWEEN '2026-06-01' AND '2026-06-30'
ORDER BY occurred_at_utc, event_id;
```

```sql
SELECT analysis_run_id, algorithm_version, event_id, dataset_id, timeframe, bar_idx, relation
FROM v_trade_market_context
WHERE trader_id='tang' AND underlying='SPY' AND trade_date='2026-07-17';
```

SQLite nulls preserve the canonical meaning above: an unknown premium, quantity, fee, result, or bar association remains `NULL`; it is never converted to zero. In particular, gross and net results remain distinct, and net P&L stays `NULL` when any included fee is unknown.

## 6. Frozen `trade_records` Response

The new member is switched into assemble/static output only in the Phase 6 atomic cutover. Its exact top-level table is:

| Field | Type | Required content |
| --- | --- | --- |
| `schema_version` | string | Exact value `trade-records-v1`. |
| `ticker` | `SPY|QQQ` | Selected underlying. |
| `trade_date` | ISO date | Selected New York date. |
| `traders` | array | Public registry slice: active traders plus any referenced inactive trader. |
| `trade_groups` | array | Filtered public nested groups, legs, events, notes, and outcomes. |
| `note_contexts` | array | Filtered normalized day contexts. |
| `counts` | object | Exact count keys below. |
| `export_metadata` | object | Exact selection and four download names below. |

`counts` contains exactly:

- `trade_groups_total`;
- `display_eligible_groups`;
- `reported_stats_eligible_groups`;
- `calculated_stats_eligible_groups`;
- `note_contexts_total`.

Each public trader contains exactly `trader_id`, `display_name`, `color`, `active`, and `sort_order`.

Each public group contains:

```text
trade_group_id
trader_id
underlying
trade_date
direction
status
review_status
display_eligible
reported_stats_eligible
calculated_stats_eligible
supersedes_trade_group_id
legs
reported_outcome
calculated_outcome
result_conflict
notes
normalization_method
```

Each public leg contains the canonical `leg_id`, instrument/position/option type, strike, expiry and provenance, contract multiplier and provenance, plus ordered events. Each event contains the canonical ID, sequence, action, offset-bearing time facts, optional premium/quantity/fees/note, and fact-provenance labels. Private migration location fields are not public.

Each public note context contains `context_id`, `trader_id`, `underlying`, `trade_date`, `text`, `status`, `review_status`, and `normalization_method`.

`export_metadata` contains:

| Field | Semantics |
| --- | --- |
| `selection` | Exact ticker, date, sorted trader IDs, statuses, review statuses, and `display_only` flag used for this payload. |
| `json_filename` | `trade_records_<ticker>_<date>.json`. |
| `csv_filenames` | Exactly `trade_groups.csv`, `trade_legs.csv`, and `trade_events.csv`. |
| `includes_bars` | Always `false`. |
| `raw_evidence_included` | Always `false`. |

Interactive read services may filter trader, ticker, date range, status, review status, and eligibility. Admin services later validate trader/day canonical files in a temporary candidate and atomically replace only after success. Phase 3 service handlers stay unregistered until the Phase 6 switch.

## 7. Public And Private Allowlists

Public JSON and CSV are allowlist-built. They may contain normalized notes and provenance labels; they may not contain raw screenshots, attachment blobs, chat transcripts/exports, Discord exports, base64 images, or generic raw evidence/message fields.

Canonical-private normalization fields are limited to `method`, `source`, `source_path`, `source_index`, and `review_flags`. Public output exposes only `normalization_method`; source path/index and review-process metadata remain outside the public response and downloads.

Forbidden raw-evidence field names reject canonical validation recursively rather than being silently dropped. This prevents a private field from leaking later through a broad serializer.

## 8. Deterministic Downloads

Downloads apply the current trader/ticker/date filters. The JSON download is the complete public `trade-records-v1` payload serialized deterministically. CSV outputs are:

- `trade_groups.csv`: one group row with reported/calculated return columns kept separate;
- `trade_legs.csv`: one leg row keyed by `trade_group_id`;
- `trade_events.csv`: one event row keyed by both `leg_id` and `trade_group_id`.

Null CSV facts are empty cells. Booleans are lowercase `true`/`false`. The bundle includes no K-lines, HTML, PDF, screenshots, raw chat, or private migration fields. Leg/event foreign keys and row counts must reconcile to the selected JSON hierarchy.

## 9. Legacy Rule Extraction Boundary

Phase 1 extraction is a pure transformation and writes no canonical daily file or tracked DB row.

- Only an explicitly signed percentage next to a result verb such as feedback, take-profit, clear, stop, or exit may become `reported_outcome.return_pct`.
- A nearest preceding `HH:MM 附近` attached to the allowlisted result becomes an approximate exit-time event.
- Bare `N% 仓位` is position size and is never a return.
- Unsigned `40% 结束` is not extracted and receives `ambiguous_exit_percentage` for review.
- The original note is preserved exactly; extraction records `legacy_rule_extract` and never fabricates a premium, quantity, fee, option price, or dollar P&L.

The complete acceptance set is 20 source files, 27 trade rows, and two day-level note contexts. Phase 3 must reconcile every row to a canonical target before any cutover.
