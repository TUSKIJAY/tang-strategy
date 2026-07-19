from __future__ import annotations

import contextlib
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .settings import settings
from .services.db_safety import (
    BAR_COLUMNS,
    DatabaseToken,
    capture_database_token,
    create_consistent_snapshot,
    day_sha256,
    db_write_lock,
    table_sha256,
    validate_exactly_one_active_dataset,
    validate_sqlite,
)


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    target = (db_path or settings.db_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: Path | None = None) -> None:
    target = (db_path or settings.db_path).expanduser().resolve()
    with db_write_lock(target):
        with contextlib.closing(connect(target)) as conn, conn:
            _execute_schema(conn, TARGET_SCHEMA)
            _migrate_raw_json_columns(conn)
            validate_exactly_one_active_dataset(conn)


def init_target_db(db_path: Path) -> None:
    """Create the Phase 2 schema explicitly; never used by default startup before cutover."""

    target = db_path.expanduser().resolve()
    with db_write_lock(target):
        with contextlib.closing(connect(target)) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                _execute_schema(conn, TARGET_SCHEMA)
                validate_exactly_one_active_dataset(conn)
                conn.commit()
            except Exception:
                conn.rollback()
                raise


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]


def _migrate_raw_json_columns(conn: sqlite3.Connection) -> None:
    if _table_exists(conn, "bars_1m"):
        _rebuild_bars_table_without_raw_json(conn, "bars_1m")
    if _table_exists(conn, "bars_5m"):
        _rebuild_bars_table_without_raw_json(conn, "bars_5m")


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone() is not None


def _table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def _rebuild_bars_table_without_raw_json(conn: sqlite3.Connection, table_name: str) -> None:
    columns = _table_columns(conn, table_name)
    if "raw_json" not in columns:
        return

    tmp_table = f"{table_name}_migrated"
    owner_column = "dataset_id" if "dataset_id" in columns else "market_day_id"
    create_sql = _bars_create_sql(owner_column)
    selected_columns = _bar_insert_columns(owner_column)
    select_sql = ", ".join(selected_columns)

    conn.execute(f"CREATE TABLE {tmp_table} ({create_sql})")
    conn.execute(
        f"INSERT INTO {tmp_table} ({select_sql}) SELECT {select_sql} FROM {table_name}",
    )
    conn.execute(f"DROP TABLE {table_name}")
    conn.execute(f"ALTER TABLE {tmp_table} RENAME TO {table_name}")


def _bars_create_sql(owner_column: str = "market_day_id") -> str:
    if owner_column not in {"market_day_id", "dataset_id"}:
        raise ValueError(f"Unsupported bars owner column: {owner_column}")
    owner_type = "INTEGER" if owner_column == "market_day_id" else "TEXT"
    parent_table = "market_days" if owner_column == "market_day_id" else "market_datasets"
    parent_column = "id" if owner_column == "market_day_id" else "dataset_id"
    return (
        f"{owner_column} {owner_type} NOT NULL,\n"
        "    idx INTEGER NOT NULL,\n"
        "    ts TEXT,\n"
        "    time TEXT,\n"
        "    open REAL,\n"
        "    high REAL,\n"
        "    low REAL,\n"
        "    close REAL,\n"
        "    volume REAL,\n"
        "    vwap REAL,\n"
        "    ha_open REAL,\n"
        "    ha_high REAL,\n"
        "    ha_low REAL,\n"
        "    ha_close REAL,\n"
        "    m5 REAL,\n"
        "    m10 REAL,\n"
        "    m20 REAL,\n"
        "    m30 REAL,\n"
        "    m50 REAL,\n"
        "    m60 REAL,\n"
        "    m120 REAL,\n"
        "    m200 REAL,\n"
        "    m250 REAL,\n"
        f"    PRIMARY KEY ({owner_column}, idx),\n"
        f"    FOREIGN KEY ({owner_column}) REFERENCES {parent_table}({parent_column}) ON DELETE CASCADE"
    )


def _bar_insert_columns(owner_column: str = "market_day_id") -> list[str]:
    if owner_column not in {"market_day_id", "dataset_id"}:
        raise ValueError(f"Unsupported bars owner column: {owner_column}")
    return [
        owner_column,
        "idx",
        "ts",
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "vwap",
        "ha_open",
        "ha_high",
        "ha_low",
        "ha_close",
        "m5",
        "m10",
        "m20",
        "m30",
        "m50",
        "m60",
        "m120",
        "m200",
        "m250",
    ]


SCHEMA = """
CREATE TABLE IF NOT EXISTS tickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT,
    asset_type TEXT NOT NULL DEFAULT 'equity',
    enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS market_days (
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

CREATE TABLE IF NOT EXISTS bars_1m (
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

CREATE TABLE IF NOT EXISTS bars_5m (
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

CREATE TABLE IF NOT EXISTS strategies (
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

CREATE TABLE IF NOT EXISTS teaching_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT 'default',
    slug TEXT NOT NULL,
    json_body TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_type, version, slug)
);

CREATE INDEX IF NOT EXISTS idx_market_days_ticker_date ON market_days(ticker, trade_date);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(active, name, version);
"""


TARGET_FOUNDATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS tickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT,
    asset_type TEXT NOT NULL DEFAULT 'equity',
    enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS market_days (
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

CREATE TABLE IF NOT EXISTS market_datasets (
    dataset_id TEXT PRIMARY KEY,
    market_day_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    venue TEXT,
    source_revision TEXT,
    fetcher_revision TEXT,
    imported_at TEXT NOT NULL,
    checksum TEXT NOT NULL,
    quality_json TEXT NOT NULL DEFAULT '{}',
    state TEXT NOT NULL CHECK(state IN ('active', 'superseded')),
    FOREIGN KEY (market_day_id) REFERENCES market_days(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bars_1m (
    dataset_id TEXT NOT NULL,
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
    PRIMARY KEY (dataset_id, idx),
    FOREIGN KEY (dataset_id) REFERENCES market_datasets(dataset_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bars_5m (
    dataset_id TEXT NOT NULL,
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
    PRIMARY KEY (dataset_id, idx),
    FOREIGN KEY (dataset_id) REFERENCES market_datasets(dataset_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS strategies (
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

CREATE TABLE IF NOT EXISTS teaching_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_type TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT 'default',
    slug TEXT NOT NULL,
    json_body TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(asset_type, version, slug)
);
"""


TARGET_EXTENSION_SCHEMA = """
CREATE TABLE IF NOT EXISTS traders (
    trader_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    color TEXT NOT NULL UNIQUE,
    active INTEGER NOT NULL CHECK(active IN (0, 1)),
    sort_order INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS trade_groups (
    trade_group_id TEXT PRIMARY KEY,
    trader_id TEXT NOT NULL,
    market_day_id INTEGER NOT NULL,
    underlying TEXT NOT NULL CHECK(underlying IN ('SPY', 'QQQ')),
    trade_date TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('CALL', 'PUT')),
    status TEXT NOT NULL CHECK(status IN ('active', 'voided', 'superseded')),
    review_status TEXT NOT NULL CHECK(review_status IN ('pending', 'verified')),
    display_eligible INTEGER NOT NULL CHECK(display_eligible IN (0, 1)),
    reported_stats_eligible INTEGER NOT NULL CHECK(reported_stats_eligible IN (0, 1)),
    calculated_stats_eligible INTEGER NOT NULL CHECK(calculated_stats_eligible IN (0, 1)),
    supersedes_trade_group_id TEXT,
    result_conflict INTEGER NOT NULL CHECK(result_conflict IN (0, 1)),
    notes_json TEXT NOT NULL DEFAULT '[]',
    normalization_method TEXT NOT NULL,
    normalization_source TEXT NOT NULL,
    normalization_source_path TEXT,
    normalization_source_index INTEGER,
    normalization_review_flags_json TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
    FOREIGN KEY (market_day_id) REFERENCES market_days(id),
    FOREIGN KEY (supersedes_trade_group_id) REFERENCES trade_groups(trade_group_id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS trade_legs (
    leg_id TEXT PRIMARY KEY,
    trade_group_id TEXT NOT NULL,
    instrument_type TEXT NOT NULL,
    position_side TEXT NOT NULL,
    option_type TEXT NOT NULL CHECK(option_type IN ('CALL', 'PUT')),
    strike REAL,
    expiry TEXT NOT NULL,
    expiry_provenance TEXT NOT NULL,
    contract_multiplier REAL NOT NULL,
    contract_multiplier_provenance TEXT NOT NULL,
    FOREIGN KEY (trade_group_id) REFERENCES trade_groups(trade_group_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_events (
    event_id TEXT PRIMARY KEY,
    leg_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    action TEXT NOT NULL,
    occurred_at TEXT,
    occurred_at_utc TEXT,
    time_precision TEXT,
    time_incomplete INTEGER NOT NULL CHECK(time_incomplete IN (0, 1)),
    premium REAL,
    quantity REAL,
    fees REAL,
    note TEXT,
    fact_provenance_json TEXT NOT NULL,
    UNIQUE(leg_id, sequence),
    FOREIGN KEY (leg_id) REFERENCES trade_legs(leg_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_outcomes (
    trade_group_id TEXT NOT NULL,
    outcome_kind TEXT NOT NULL CHECK(outcome_kind IN ('reported', 'calculated')),
    return_pct REAL,
    gross_pnl REAL,
    net_pnl REAL,
    provenance TEXT,
    note TEXT,
    closed_quantity REAL,
    average_entry_premium REAL,
    average_exit_premium REAL,
    calculation_version TEXT,
    PRIMARY KEY (trade_group_id, outcome_kind),
    FOREIGN KEY (trade_group_id) REFERENCES trade_groups(trade_group_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS trade_note_contexts (
    context_id TEXT PRIMARY KEY,
    trader_id TEXT NOT NULL,
    market_day_id INTEGER NOT NULL,
    underlying TEXT NOT NULL CHECK(underlying IN ('SPY', 'QQQ')),
    trade_date TEXT NOT NULL,
    text TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('active', 'voided', 'superseded')),
    review_status TEXT NOT NULL CHECK(review_status IN ('pending', 'verified')),
    normalization_method TEXT NOT NULL,
    normalization_source TEXT NOT NULL,
    normalization_source_path TEXT,
    normalization_source_index INTEGER,
    normalization_review_flags_json TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
    FOREIGN KEY (market_day_id) REFERENCES market_days(id)
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    analysis_run_id TEXT PRIMARY KEY,
    algorithm TEXT NOT NULL,
    algorithm_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('running', 'complete', 'failed')),
    parameters_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS trade_market_context (
    context_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_run_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    dataset_id TEXT NOT NULL,
    timeframe TEXT NOT NULL CHECK(timeframe IN ('1m', '5m')),
    bar_idx INTEGER,
    relation TEXT NOT NULL,
    context_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE(analysis_run_id, event_id, dataset_id, timeframe),
    FOREIGN KEY (analysis_run_id) REFERENCES analysis_runs(analysis_run_id) ON DELETE CASCADE,
    FOREIGN KEY (event_id) REFERENCES trade_events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES market_datasets(dataset_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_market_datasets_one_active
ON market_datasets(market_day_id) WHERE state='active';
CREATE INDEX IF NOT EXISTS idx_market_datasets_day_state
ON market_datasets(market_day_id, state, imported_at);
CREATE INDEX IF NOT EXISTS idx_market_days_ticker_date ON market_days(ticker, trade_date);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(active, name, version);
CREATE INDEX IF NOT EXISTS idx_trade_groups_trader_ticker_date
ON trade_groups(trader_id, underlying, trade_date);
CREATE INDEX IF NOT EXISTS idx_trade_groups_filters
ON trade_groups(status, review_status, display_eligible, reported_stats_eligible, calculated_stats_eligible);
CREATE INDEX IF NOT EXISTS idx_trade_groups_direction ON trade_groups(direction, trade_date);
CREATE INDEX IF NOT EXISTS idx_trade_legs_group ON trade_legs(trade_group_id, leg_id);
CREATE INDEX IF NOT EXISTS idx_trade_events_leg_sequence ON trade_events(leg_id, sequence);
CREATE INDEX IF NOT EXISTS idx_trade_events_utc ON trade_events(occurred_at_utc);
CREATE INDEX IF NOT EXISTS idx_trade_note_context_filters
ON trade_note_contexts(trader_id, underlying, trade_date, status, review_status);
CREATE INDEX IF NOT EXISTS idx_trade_market_context_lineage
ON trade_market_context(analysis_run_id, dataset_id, event_id);

CREATE VIEW IF NOT EXISTS v_active_market_datasets AS
SELECT market_days.id AS market_day_id, market_days.ticker, market_days.trade_date,
       market_days.session_mode, market_datasets.dataset_id, market_datasets.provider,
       market_datasets.venue, market_datasets.source_revision,
       market_datasets.fetcher_revision, market_datasets.imported_at,
       market_datasets.checksum, market_datasets.quality_json
FROM market_days JOIN market_datasets
  ON market_datasets.market_day_id=market_days.id AND market_datasets.state='active';

CREATE VIEW IF NOT EXISTS v_trade_group_performance AS
SELECT trade_groups.trade_group_id, trade_groups.trader_id, traders.display_name,
       trade_groups.market_day_id, trade_groups.underlying, trade_groups.trade_date,
       trade_groups.direction, trade_groups.status, trade_groups.review_status,
       trade_groups.display_eligible, trade_groups.reported_stats_eligible,
       trade_groups.calculated_stats_eligible, trade_groups.result_conflict,
       reported.return_pct AS reported_return_pct,
       reported.gross_pnl AS reported_gross_pnl, reported.net_pnl AS reported_net_pnl,
       calculated.return_pct AS calculated_return_pct,
       calculated.gross_pnl AS calculated_gross_pnl,
       calculated.net_pnl AS calculated_net_pnl
FROM trade_groups JOIN traders ON traders.trader_id=trade_groups.trader_id
LEFT JOIN trade_outcomes AS reported
  ON reported.trade_group_id=trade_groups.trade_group_id AND reported.outcome_kind='reported'
LEFT JOIN trade_outcomes AS calculated
  ON calculated.trade_group_id=trade_groups.trade_group_id AND calculated.outcome_kind='calculated';

CREATE VIEW IF NOT EXISTS v_trade_event_facts AS
SELECT trade_events.event_id, trade_events.leg_id, trade_legs.trade_group_id,
       trade_groups.trader_id, trade_groups.underlying, trade_groups.trade_date,
       trade_groups.direction, trade_groups.status, trade_groups.review_status,
       trade_events.sequence, trade_events.action, trade_events.occurred_at,
       trade_events.occurred_at_utc, trade_events.time_precision,
       trade_events.time_incomplete, trade_events.premium, trade_events.quantity,
       trade_events.fees, trade_legs.strike, trade_legs.expiry,
       trade_legs.contract_multiplier
FROM trade_events JOIN trade_legs ON trade_legs.leg_id=trade_events.leg_id
JOIN trade_groups ON trade_groups.trade_group_id=trade_legs.trade_group_id;

CREATE VIEW IF NOT EXISTS v_trade_market_context AS
SELECT trade_market_context.context_row_id, trade_market_context.analysis_run_id,
       analysis_runs.algorithm, analysis_runs.algorithm_version,
       trade_market_context.event_id, trade_legs.trade_group_id,
       trade_groups.trader_id, trade_groups.underlying, trade_groups.trade_date,
       trade_market_context.dataset_id, market_datasets.provider,
       trade_market_context.timeframe, trade_market_context.bar_idx,
       trade_market_context.relation, trade_market_context.context_json
FROM trade_market_context
JOIN analysis_runs ON analysis_runs.analysis_run_id=trade_market_context.analysis_run_id
JOIN trade_events ON trade_events.event_id=trade_market_context.event_id
JOIN trade_legs ON trade_legs.leg_id=trade_events.leg_id
JOIN trade_groups ON trade_groups.trade_group_id=trade_legs.trade_group_id
JOIN market_datasets ON market_datasets.dataset_id=trade_market_context.dataset_id;
"""


TARGET_SCHEMA = TARGET_FOUNDATION_SCHEMA + TARGET_EXTENSION_SCHEMA


def migrate_candidate_schema(
    candidate_path: Path,
    registry: Mapping[str, Any] | None = None,
    trade_days: Sequence[Mapping[str, Any]] = (),
    failure_hook: Callable[[sqlite3.Connection], None] | None = None,
) -> dict[str, Any]:
    """Migrate only an explicit candidate and prove old/new logical preservation."""

    candidate = candidate_path.expanduser().resolve()
    if not candidate.is_file():
        raise FileNotFoundError(f"Candidate DB does not exist: {candidate}")
    with contextlib.closing(connect(candidate)) as conn:
        before = _preservation_snapshot(conn)
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN IMMEDIATE")
        try:
            if "market_day_id" in _table_columns(conn, "bars_1m"):
                _migrate_bar_ownership(conn)
            _execute_schema(conn, TARGET_EXTENSION_SCHEMA)
            if registry is not None:
                _clear_trade_projection(conn)
                _project_trade_records(conn, registry, trade_days)
            validate_exactly_one_active_dataset(conn)
            if failure_hook is not None:
                failure_hook(conn)
            foreign_key_failures = conn.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_failures:
                raise RuntimeError(f"Candidate foreign-key validation failed: {foreign_key_failures}")
            after = _preservation_snapshot(conn)
            _assert_preserved(before, after)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.execute("PRAGMA foreign_keys = ON")

    validate_sqlite(candidate)
    with contextlib.closing(connect(candidate)) as conn:
        validate_exactly_one_active_dataset(conn)
        counts = {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in (
                "market_days",
                "market_datasets",
                "bars_1m",
                "bars_5m",
                "traders",
                "trade_groups",
                "trade_legs",
                "trade_events",
                "trade_outcomes",
                "trade_note_contexts",
            )
        }
    return {
        "candidate_path": str(candidate),
        "preservation": "passed",
        "logical_market_sha256": capture_database_token(candidate).logical_sha256,
        "strategies_sha256": table_sha256(candidate, "strategies"),
        "teaching_sha256": table_sha256(candidate, "teaching_assets"),
        "counts": counts,
    }


def build_target_candidate(
    live_path: Path,
    candidate_path: Path,
    registry: Mapping[str, Any] | None = None,
    trade_days: Sequence[Mapping[str, Any]] = (),
    failure_hook: Callable[[sqlite3.Connection], None] | None = None,
) -> tuple[DatabaseToken, dict[str, Any]]:
    """Snapshot, migrate, and drift-check without promoting the live database."""

    live = live_path.expanduser().resolve()
    candidate = candidate_path.expanduser().resolve()
    baseline = create_consistent_snapshot(live, candidate)
    report = migrate_candidate_schema(candidate, registry, trade_days, failure_hook)
    current = capture_database_token(live)
    if current != baseline:
        raise RuntimeError(
            "Refusing candidate acceptance: live DB drifted after the candidate snapshot "
            f"(baseline={baseline.as_dict()}, current={current.as_dict()})"
        )
    return baseline, report


def project_trade_repository(
    candidate_path: Path,
    registry: Mapping[str, Any],
    trade_days: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    """Project validated canonical content into an explicit target-schema candidate."""

    candidate = candidate_path.expanduser().resolve()
    with contextlib.closing(connect(candidate)) as conn:
        if "dataset_id" not in _table_columns(conn, "bars_1m"):
            raise RuntimeError("Trade projection requires an explicit target-schema candidate")
        conn.execute("BEGIN IMMEDIATE")
        try:
            _project_trade_records(conn, registry, trade_days)
            foreign_key_failures = conn.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_failures:
                raise RuntimeError(f"Trade projection foreign-key validation failed: {foreign_key_failures}")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in (
                "traders",
                "trade_groups",
                "trade_legs",
                "trade_events",
                "trade_outcomes",
                "trade_note_contexts",
            )
        }


def replace_trade_repository(
    candidate_path: Path,
    registry: Mapping[str, Any],
    trade_days: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    """Replace the normalized trade projection on an explicit target-schema candidate."""

    candidate = candidate_path.expanduser().resolve()
    with contextlib.closing(connect(candidate)) as conn:
        if "dataset_id" not in _table_columns(conn, "bars_1m"):
            raise RuntimeError("Trade replacement requires an explicit target-schema candidate")
        conn.execute("BEGIN IMMEDIATE")
        try:
            _clear_trade_projection(conn)
            _project_trade_records(conn, registry, trade_days)
            foreign_key_failures = conn.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_failures:
                raise RuntimeError(
                    f"Trade replacement foreign-key validation failed: {foreign_key_failures}"
                )
            validate_exactly_one_active_dataset(conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return {
            table: int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in (
                "traders",
                "trade_groups",
                "trade_legs",
                "trade_events",
                "trade_outcomes",
                "trade_note_contexts",
            )
        }


def _clear_trade_projection(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM trade_market_context")
    conn.execute("DELETE FROM analysis_runs")
    conn.execute("DELETE FROM trade_outcomes")
    conn.execute("DELETE FROM trade_events")
    conn.execute("DELETE FROM trade_legs")
    conn.execute("DELETE FROM trade_note_contexts")
    conn.execute("DELETE FROM trade_groups")
    conn.execute("DELETE FROM traders")


def _execute_schema(conn: sqlite3.Connection, schema: str) -> None:
    for statement in schema.split(";"):
        sql = statement.strip()
        if sql:
            conn.execute(sql)


def _migrate_bar_ownership(conn: sqlite3.Connection) -> None:
    _execute_schema(conn, TARGET_FOUNDATION_SCHEMA.split("CREATE TABLE IF NOT EXISTS bars_1m", 1)[0])
    days = conn.execute(
        "SELECT id, ticker, trade_date, session_mode, source, imported_at, meta_json "
        "FROM market_days ORDER BY ticker, trade_date, session_mode"
    ).fetchall()
    for day in days:
        hashes = day_sha256(
            conn,
            str(day["ticker"]),
            str(day["trade_date"]),
            str(day["session_mode"]),
        )
        metadata = json.loads(day["meta_json"] or "{}")
        provider = str(metadata.get("provider") or metadata.get("source") or day["source"] or "legacy_bootstrap")
        venue = metadata.get("venue")
        source_revision = metadata.get("source_revision") or metadata.get("generated_at")
        fetcher_revision = metadata.get("fetcher_revision") or metadata.get("fetch_revision")
        quality = metadata.get("quality") if isinstance(metadata.get("quality"), dict) else {}
        checksum = hashlib.sha256(
            f"{hashes['bars_1m']}\n{hashes['bars_5m']}".encode("utf-8")
        ).hexdigest()
        dataset_id = _bootstrap_dataset_id(day)
        conn.execute(
            "INSERT INTO market_datasets(dataset_id, market_day_id, provider, venue, "
            "source_revision, fetcher_revision, imported_at, checksum, quality_json, state) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')",
            (
                dataset_id,
                day["id"],
                provider,
                venue,
                source_revision,
                fetcher_revision,
                day["imported_at"],
                checksum,
                _canonical_json(quality),
            ),
        )

    for table in ("bars_1m", "bars_5m"):
        legacy = f"{table}_market_day_legacy"
        conn.execute(f"ALTER TABLE {table} RENAME TO {legacy}")
        conn.execute(f"CREATE TABLE {table} ({_bars_create_sql('dataset_id')})")
        conn.execute(
            f"INSERT INTO {table}(dataset_id, {', '.join(BAR_COLUMNS)}) "
            f"SELECT market_datasets.dataset_id, {', '.join(f'{legacy}.{column}' for column in BAR_COLUMNS)} "
            f"FROM {legacy} JOIN market_datasets "
            f"ON market_datasets.market_day_id={legacy}.market_day_id "
            "AND market_datasets.state='active'"
        )
        conn.execute(f"DROP TABLE {legacy}")


def _bootstrap_dataset_id(day: sqlite3.Row) -> str:
    parts = (
        str(day["ticker"]).lower(),
        str(day["trade_date"]).replace("-", ""),
        "".join(character if character.isalnum() else "_" for character in str(day["session_mode"]).lower()),
    )
    return f"mds_{parts[0]}_{parts[1]}_{parts[2]}_bootstrap"


def _project_trade_records(
    conn: sqlite3.Connection,
    registry: Mapping[str, Any],
    trade_days: Sequence[Mapping[str, Any]],
) -> None:
    from .services.trade_records import validate_trade_day, validate_trader_registry

    registry_data = validate_trader_registry(registry)
    repository_ids: set[str] = set()
    validated_days = [
        validate_trade_day(day, registry_data, repository_ids=repository_ids)
        for day in trade_days
    ]
    for trader in registry_data["traders"]:
        conn.execute(
            "INSERT INTO traders(trader_id, display_name, color, active, sort_order) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                trader["trader_id"],
                trader["display_name"],
                trader["color"],
                int(trader["active"]),
                trader["sort_order"],
            ),
        )
    for day in validated_days:
        for group in day["trade_groups"]:
            market_day_id = _resolve_trade_market_day(conn, group["underlying"], group["trade_date"])
            normalization = group["normalization"]
            conn.execute(
                "INSERT INTO trade_groups(trade_group_id, trader_id, market_day_id, underlying, "
                "trade_date, direction, status, review_status, display_eligible, "
                "reported_stats_eligible, calculated_stats_eligible, supersedes_trade_group_id, "
                "result_conflict, notes_json, normalization_method, normalization_source, "
                "normalization_source_path, normalization_source_index, "
                "normalization_review_flags_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    group["trade_group_id"], group["trader_id"], market_day_id,
                    group["underlying"], group["trade_date"], group["direction"],
                    group["status"], group["review_status"], int(group["display_eligible"]),
                    int(group["reported_stats_eligible"]), int(group["calculated_stats_eligible"]),
                    group["supersedes_trade_group_id"], int(group["result_conflict"]),
                    _canonical_json(group["notes"]), normalization["method"],
                    normalization["source"], normalization["source_path"],
                    normalization["source_index"], _canonical_json(normalization["review_flags"]),
                ),
            )
            for leg in group["legs"]:
                conn.execute(
                    "INSERT INTO trade_legs(leg_id, trade_group_id, instrument_type, position_side, "
                    "option_type, strike, expiry, expiry_provenance, contract_multiplier, "
                    "contract_multiplier_provenance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        leg["leg_id"], group["trade_group_id"], leg["instrument_type"],
                        leg["position_side"], leg["option_type"], leg["strike"], leg["expiry"],
                        leg["expiry_provenance"], leg["contract_multiplier"],
                        leg["contract_multiplier_provenance"],
                    ),
                )
                for event in leg["events"]:
                    conn.execute(
                        "INSERT INTO trade_events(event_id, leg_id, sequence, action, occurred_at, "
                        "occurred_at_utc, time_precision, time_incomplete, premium, quantity, fees, "
                        "note, fact_provenance_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            event["event_id"], leg["leg_id"], event["sequence"], event["action"],
                            event["occurred_at"], _utc_timestamp(event["occurred_at"]),
                            event["time_precision"], int(event["time_incomplete"]), event["premium"],
                            event["quantity"], event["fees"], event["note"],
                            _canonical_json(event["fact_provenance"]),
                        ),
                    )
            for outcome_kind, outcome in (
                ("reported", group["reported_outcome"]),
                ("calculated", group["calculated_outcome"]),
            ):
                if outcome_kind == "calculated" and not group["calculated_stats_eligible"]:
                    continue
                if outcome is not None:
                    conn.execute(
                        "INSERT INTO trade_outcomes(trade_group_id, outcome_kind, return_pct, "
                        "gross_pnl, net_pnl, provenance, note, closed_quantity, "
                        "average_entry_premium, average_exit_premium, calculation_version) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            group["trade_group_id"], outcome_kind, outcome.get("return_pct"),
                            outcome.get("gross_pnl"), outcome.get("net_pnl"), outcome.get("provenance"),
                            outcome.get("note"), outcome.get("closed_quantity"),
                            outcome.get("average_entry_premium"), outcome.get("average_exit_premium"),
                            outcome.get("calculation_version"),
                        ),
                    )
        for context in day["note_contexts"]:
            market_day_id = _resolve_trade_market_day(conn, context["underlying"], context["trade_date"])
            normalization = context["normalization"]
            conn.execute(
                "INSERT INTO trade_note_contexts(context_id, trader_id, market_day_id, underlying, "
                "trade_date, text, status, review_status, normalization_method, normalization_source, "
                "normalization_source_path, normalization_source_index, normalization_review_flags_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    context["context_id"], context["trader_id"], market_day_id,
                    context["underlying"], context["trade_date"], context["text"],
                    context["status"], context["review_status"], normalization["method"],
                    normalization["source"], normalization["source_path"],
                    normalization["source_index"], _canonical_json(normalization["review_flags"]),
                ),
            )


def _resolve_trade_market_day(conn: sqlite3.Connection, ticker: str, trade_date: str) -> int:
    rows = conn.execute(
        "SELECT id FROM market_days WHERE ticker=? AND trade_date=? ORDER BY session_mode",
        (ticker, trade_date),
    ).fetchall()
    if len(rows) != 1:
        raise RuntimeError(
            f"Expected exactly one logical market day for trade {ticker}|{trade_date}; found {len(rows)}"
        )
    return int(rows[0][0])


def _preservation_snapshot(conn: sqlite3.Connection) -> dict[str, Any]:
    days = conn.execute(
        "SELECT ticker, trade_date, session_mode FROM market_days "
        "ORDER BY ticker, trade_date, session_mode"
    ).fetchall()
    return {
        "market_days": [tuple(row) for row in days],
        "day_hashes": {
            "|".join(str(value) for value in row): day_sha256(conn, *row)
            for row in days
        },
        "tickers": [
            tuple(row)
            for row in conn.execute(
                "SELECT id, symbol, name, asset_type, enabled FROM tickers ORDER BY id"
            ).fetchall()
        ],
        "strategies": [
            tuple(row)
            for row in conn.execute("SELECT * FROM strategies ORDER BY id").fetchall()
        ],
        "teaching_assets": [
            tuple(row)
            for row in conn.execute("SELECT * FROM teaching_assets ORDER BY id").fetchall()
        ],
    }


def _assert_preserved(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    for key in ("market_days", "day_hashes", "tickers", "strategies", "teaching_assets"):
        if before[key] != after[key]:
            raise RuntimeError(f"Candidate migration changed preserved {key}")


def _utc_timestamp(value: str | None) -> str | None:
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
