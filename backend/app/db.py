from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path
from typing import Iterable

from .settings import settings
from .services.db_safety import db_write_lock


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
            conn.executescript(SCHEMA)
            _migrate_raw_json_columns(conn)


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
    create_sql = _bars_create_sql()
    selected_columns = _bar_insert_columns(table_name)
    select_sql = ", ".join(selected_columns)

    conn.execute(f"CREATE TABLE {tmp_table} ({create_sql})")
    conn.execute(
        f"INSERT INTO {tmp_table} ({select_sql}) SELECT {select_sql} FROM {table_name}",
    )
    conn.execute(f"DROP TABLE {table_name}")
    conn.execute(f"ALTER TABLE {tmp_table} RENAME TO {table_name}")


def _bars_create_sql() -> str:
    return (
        "market_day_id INTEGER NOT NULL,\n"
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
        "    PRIMARY KEY (market_day_id, idx),\n"
        "    FOREIGN KEY (market_day_id) REFERENCES market_days(id) ON DELETE CASCADE"
    )


def _bar_insert_columns(_: str) -> list[str]:
    return [
        "market_day_id",
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
