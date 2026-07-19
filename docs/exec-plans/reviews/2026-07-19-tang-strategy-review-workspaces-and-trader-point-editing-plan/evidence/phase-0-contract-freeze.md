# Phase 0 — Admin Canonical Read Contract Freeze And Write-Base Proof

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Frozen at: `phase-0:in-progress`, 2026-07-19, `codex/project-harness@d73502139e6d25d5e050c376e90289c70ef23ecc`
- Purpose: freeze the exact contracts for the two planned admin-only canonical read routes, prove the public projection is not a write base, and record the multi-ticker full-day shape the editor must preserve. This document freezes contracts only; it implements nothing.

## 1. Frozen route contracts

### 1.1 `GET /api/admin/traders`

- Auth: existing `require_admin` bearer dependency (`backend/app/auth.py:67-70`). Readonly role receives 403; missing/invalid token receives the existing 401 behavior. No new role, no auth redesign.
- Response 200: the complete canonical trader registry document — exactly `{schema_version: "traders-v1", traders: [...]}` with each trader carrying exactly `TRADER_FIELDS` (`trader_id`, `display_name`, `color`, `active`, `sort_order`; `backend/app/services/trade_records.py:36-...`).
- Construction: load and validate through the existing `load_trader_registry` (`trade_records.py:165-166`, which runs `validate_trader_registry`, `:169-202`) from `settings.content_dir / "traders" / "index.json"`, and return the validated document. The response is write-valid: a client may PUT the body back to `PUT /api/admin/traders` unchanged and pass `handle_trader_registry_admin_write` validation with zero semantic diff.
- Failure: missing/invalid registry file fails closed through the existing `TradeValidationError` → HTTP 400 mapping (`backend/app/main.py` route error handling). No empty or default registry is fabricated.
- Side effects: none. The handler performs no SQLite access and no DB projection touch.

### 1.2 `GET /api/admin/trade-records?trade_date=<YYYY-MM-DD>`

- Auth: existing `require_admin` bearer dependency, identical semantics to §1.1.
- Query: exactly one required query parameter `trade_date` in ISO `YYYY-MM-DD` form; malformed input → HTTP 400.
- Response 200: the complete canonical day document for that date — exactly `{schema_version: "trades-day-v1", trade_date, timezone: "America/New_York", trade_groups, note_contexts}` (`DAY_FIELDS`, `trade_records.py:37`) containing **all** underlyings, **all** traders, **all** trade groups regardless of status/review_status/eligibility, **all** note contexts, full `normalization` blocks (`method`, `source`, `source_path`, `source_index`, `review_flags`), and full per-fact `fact_provenance`.
- Construction: load through the existing `load_trade_day` (`trade_records.py:227-232` → `validate_trade_day`, `:235-282`, which applies only the declared rule defaults of `normalize_trade_day`, `:205-224`) from `settings.content_dir / "trades" / "<trade_date>.json"`, and return the validated document. Serving the validated/normalized document — not raw file bytes — is the pinned choice: it is always write-valid and round-trip stable through `PUT /api/admin/trade-records`, and `_canonical_document` (`trade_records.py:574-575`) defines the deterministic serialization used by the write path.
- Missing date: HTTP 404 when `content/trades/<trade_date>.json` does not exist. No default, synthetic, or nearest day is fabricated — this deliberately differs from the public read, which synthesizes an empty day (`trade_records.py:451-457`).
- Failure: a stored file that fails validation fails closed through the existing `TradeValidationError` → HTTP 400 mapping; no partially valid document is served.
- Side effects: none. The handler performs no SQLite access and no DB projection touch.

### 1.3 Shared boundaries (frozen)

- Both routes are new admin-only GET handlers. The existing three routes — public `GET /api/trade-records` (`backend/app/main.py:210-236`), `PUT /api/admin/traders` (`main.py:239-249`), `PUT /api/admin/trade-records` (`main.py:252-262`) — remain byte-identical in behavior; mutation stays exclusively behind the two existing PUTs.
- No DB schema, auth-role, write-route, export (`backend/scripts/export_static_reviews.py` SHA-256 `601548fa...c47996`), or Pages workflow (`.github/workflows/publish-static-reviews.yml` SHA-256 `7fe8c2e9...c50dc8`) change. The admin reads are never exposed publicly or in static output.
- Route-registration test `test_phase_6_routes_are_registered_without_legacy_compatibility` (`backend/tests/test_trade_records.py:289`) currently pins exactly the three existing routes; Phase 3 extends it to pin exactly five (three existing + these two admin GETs). That file is inside the frozen Modify manifest.
- Kimi `review-003` non-blocking observation is folded in: the Phase 3 editor's new-group form must pin every schema-required field, including the group-level `normalization` block (`method`, `source`, `review_flags`, with optional `source_path`/`source_index`), so a new group is never saved with an implicit or partial normalization record.

## 2. Proof: public `GET /api/trade-records` is not a write-valid canonical base

Each point is independently sufficient to reject the public payload as an editor write base; Phase 3 converts this record into executable round-trip tests (public payload must fail canonical day validation; the admin day read must pass).

1. **Wrong top-level shape.** The projection emits `{schema_version: "trade-records-v1", ticker, trade_date, traders, trade_groups, note_contexts, counts, export_metadata}` (`trade_records.py:382-407`); the canonical day requires exactly `{schema_version: "trades-day-v1", trade_date, timezone, trade_groups, note_contexts}` (`DAY_FIELDS` `:37`, exact-key enforcement `:243`). `timezone` is missing and `ticker`/`traders`/`counts`/`export_metadata` are unsupported fields.
2. **Ticker filtering vs multi-ticker day.** The route requires `ticker` (`main.py:212`) and keeps only `underlying == ticker` groups/contexts (`trade_records.py:343`, `:355`). `content/trades/2026-07-17.json` mixes SPY (tang) and QQQ (vordin) records, so no single public response can reconstruct the full day file.
3. **`normalization` block dropped.** `_public_group`/`_public_context` copy only allowlisted fields and flatten `normalization.method` into `normalization_method` (`trade_records.py:929-938`); `source`, `source_path`, `source_index`, and `review_flags` are lost. The shape test asserts `"source_path" not in serialized` (`backend/tests/test_trade_records.py:484-486`).
4. **Renamed field fails validation.** `normalization_method` is not a canonical key; writing it back violates exact-key validation (`NORMALIZATION_FIELDS` `trade_records.py:83`; `_validate_normalization` `:838-856`).
5. **Defaults and synthetic days.** The read applies rule defaults (`:205-224`) and synthesizes an empty day for missing exact dates (`:451-457`); a round-trip would silently fabricate provenance (`rule_default`) and empty documents.
6. **Filter loss.** `status`/`review_status`/`trader_id`/`eligibility` filters (`:341-361`, `:470-474`) can exclude pending or non-display groups — e.g. the two `pending` vordin QQQ groups of 2026-07-14 — so a filtered read used as a write base silently deletes records.
7. **Ordering changed.** Groups are re-sorted by first-event time (`:371`) and contexts by `(trader_id, context_id)` (`:372`); canonical file order is not preserved.
8. **List envelope.** The route returns a list of per-day payloads (`main.py:221`), not one `trades-day-v1` document.

## 3. Multi-ticker full-day shape (preservation target)

Canonical trade content is date-keyed: one `content/trades/<YYYY-MM-DD>.json` file per calendar date; ticker and trader are per-record fields, not nested keys. Current repository: 22 day files; 2 registry traders (`tang` sort_order 10, `vordin` sort_order 20, both active).

Reference mixed-ticker day, `content/trades/2026-07-17.json` (SHA-256 `0d292b4329d4966a...`):

| Record | Trader | Underlying | review_status | status |
| --- | --- | --- | --- | --- |
| `tg_20260717_tang_spy_001` | tang | SPY | verified | active |
| `tg_20260717_vordin_qqq_001` | vordin | QQQ | verified | active |
| `tg_20260717_vordin_qqq_002` | vordin | QQQ | verified | active |
| `ctx_20260717_vordin_qqq_001` (note context) | vordin | QQQ | — | — |

Document key tree (enforced by `validate_trade_day` and `content/schemas/trades-day.schema.json`):

- top level: exactly `schema_version` (`trades-day-v1`), `trade_date`, `timezone` (`America/New_York`), `trade_groups`, `note_contexts`;
- group: `trade_group_id` (`tg_*`), `trader_id`, `underlying` (`SPY|QQQ`), `trade_date`, `direction` (`CALL|PUT`), `status`, `review_status`, `display_eligible`, `reported_stats_eligible`, `calculated_stats_eligible`, `supersedes_trade_group_id|null`, `legs` (exactly one), `reported_outcome|null`, `calculated_outcome|null`, `result_conflict`, `notes`, `normalization`;
- leg: `leg_id`, `instrument_type` (`option`), `position_side` (`long`), `option_type`, `strike|null`, `expiry`, `expiry_provenance`, `contract_multiplier`, `contract_multiplier_provenance`, `events` (≥1);
- event: `event_id`, `sequence`, `action`, `occurred_at|null`, `time_precision`, `time_incomplete`, `premium`, `quantity`, `fees`, `note`, `fact_provenance`;
- note context: `context_id` (`ctx_*`), `trader_id`, `underlying`, `trade_date`, `text`, `status`, `review_status`, `normalization`.

Preservation rule (frozen): any scoped edit must be merged into the complete loaded day document so every untouched ticker/trader group, leg, event, outcome, note, and note context survives byte-equivalently at the semantic document boundary. Acceptance receipts are the untouched stable-ID set, per-type counts, and semantic value equality; the full-day group-count delta must equal exactly the intended edit.
