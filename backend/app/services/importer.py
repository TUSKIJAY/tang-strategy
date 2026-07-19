from __future__ import annotations

import contextlib
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from ..db import connect, init_db, replace_trade_repository
from ..settings import settings
from .bar_utils import BAR_MA_WINDOWS, bar_tuple_from_seed, recalculate_ma_fields
from .db_safety import bar_market_day_join, bars_use_datasets, db_write_lock


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "item"


def import_market_json(path: Path) -> int:
    init_db()
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("meta") or {}
    ticker = str(meta.get("ticker") or path.name.split("_")[0]).upper()
    trade_date = str(meta.get("date") or _date_from_name(path.name))
    session_mode = str(meta.get("session_mode") or meta.get("session_type") or "rth")
    bars_1m = data.get("bars_1m") or []
    bars_5m = data.get("bars_5m") or []

    with db_write_lock(settings.db_path):
        with contextlib.closing(connect()) as conn, conn:
            return _import_market_data(conn, ticker, trade_date, session_mode, meta, bars_1m, bars_5m, path)


def _import_market_data(
    conn: sqlite3.Connection,
    ticker: str,
    trade_date: str,
    session_mode: str,
    meta: dict[str, Any],
    bars_1m: list[dict[str, Any]],
    bars_5m: list[dict[str, Any]],
    path: Path,
) -> int:
    conn.execute(
        "INSERT OR IGNORE INTO tickers(symbol, name) VALUES (?, ?)",
        (ticker, ticker),
    )
    conn.execute(
        """
        INSERT INTO market_days(
            ticker, trade_date, session_mode, source, title, bar_count_1m, bar_count_5m, meta_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticker, trade_date, session_mode) DO UPDATE SET
            source=excluded.source,
            title=excluded.title,
            bar_count_1m=excluded.bar_count_1m,
            bar_count_5m=excluded.bar_count_5m,
            imported_at=CURRENT_TIMESTAMP,
            meta_json=excluded.meta_json
        """,
        (
            ticker,
            trade_date,
            session_mode,
            str(meta.get("source") or path.name),
            str(meta.get("title") or f"{ticker} {trade_date}"),
            len(bars_1m),
            len(bars_5m),
            json.dumps(meta, ensure_ascii=False, separators=(",", ":")),
        ),
    )
    market_day_id = int(conn.execute(
        "SELECT id FROM market_days WHERE ticker=? AND trade_date=? AND session_mode=?",
        (ticker, trade_date, session_mode),
    ).fetchone()["id"])
    bars_5m = recalculate_ma_fields(
        bars_5m,
        warmup_closes=_fetch_prior_5m_closes(conn, ticker, trade_date, session_mode),
    )
    owner_column, owner_id = _prepare_bar_owner(
        conn,
        market_day_id,
        ticker,
        trade_date,
        session_mode,
        meta,
        bars_1m,
        bars_5m,
        path,
    )
    conn.execute(f"DELETE FROM bars_1m WHERE {owner_column}=?", (owner_id,))
    conn.execute(f"DELETE FROM bars_5m WHERE {owner_column}=?", (owner_id,))
    conn.executemany(
        BAR_INSERT_SQL.format(table="bars_1m", owner_column=owner_column),
        [bar_tuple_from_seed(owner_id, i, b) for i, b in enumerate(bars_1m)],
    )
    if bars_5m:
        conn.executemany(
            BAR_INSERT_SQL.format(table="bars_5m", owner_column=owner_column),
            [bar_tuple_from_seed(owner_id, i, b) for i, b in enumerate(bars_5m)],
        )
    return market_day_id


def import_strategy_json(path: Path) -> int:
    init_db()
    strategy = json.loads(path.read_text(encoding="utf-8"))
    name = str(strategy.get("name") or path.stem)
    version = str(strategy.get("version") or "unknown")
    slug = slugify(f"{path.stem}-{version}")
    body = json.dumps(strategy, ensure_ascii=False, separators=(",", ":"))
    with db_write_lock(settings.db_path):
        with contextlib.closing(connect()) as conn, conn:
            return _import_strategy_data(conn, strategy, name, version, slug, body)


def _import_strategy_data(
    conn: sqlite3.Connection,
    strategy: dict[str, Any],
    name: str,
    version: str,
    slug: str,
    body: str,
) -> int:
    conn.execute(
        """
        INSERT INTO strategies(name, version, slug, description, json_body)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            name=excluded.name,
            version=excluded.version,
            description=excluded.description,
            json_body=excluded.json_body,
            active=1,
            updated_at=CURRENT_TIMESTAMP
        """,
        (name, version, slug, strategy.get("description", ""), body),
    )
    return int(conn.execute("SELECT id FROM strategies WHERE slug=?", (slug,)).fetchone()["id"])


def import_teaching_asset(path: Path, asset_type: str, slug: str, version: str = "default") -> int:
    init_db()
    body = path.read_text(encoding="utf-8")
    with db_write_lock(settings.db_path):
        with contextlib.closing(connect()) as conn, conn:
            return _import_teaching_data(conn, body, asset_type, slug, version)


def _import_teaching_data(
    conn: sqlite3.Connection,
    body: str,
    asset_type: str,
    slug: str,
    version: str,
) -> int:
    conn.execute(
        """
        INSERT INTO teaching_assets(asset_type, version, slug, json_body)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(asset_type, version, slug) DO UPDATE SET
            json_body=excluded.json_body,
            updated_at=CURRENT_TIMESTAMP
        """,
        (asset_type, version, slug, body),
    )
    return int(conn.execute(
        "SELECT id FROM teaching_assets WHERE asset_type=? AND version=? AND slug=?",
        (asset_type, version, slug),
    ).fetchone()["id"])


def import_default_seed() -> dict[str, int]:
    counts = {
        "market_days": 0,
        "strategies": 0,
        "teaching_assets": 0,
        "traders": 0,
        "trade_groups": 0,
        "trade_events": 0,
        "trade_note_contexts": 0,
    }
    for path in sorted(settings.live_extended_dir.glob("**/*.json")):
        if path.name.startswith(("SPY_", "QQQ_", "SPX_")):
            import_market_json(path)
            counts["market_days"] += 1
    for path in sorted(settings.strategies_dir.glob("*.json")):
        if path.name.endswith("schema.json"):
            continue
        import_strategy_json(path)
        counts["strategies"] += 1
    content = settings.content_dir
    candidates = [
        (content / "rules" / "compiled" / "index.json", "rules", "compiled-index"),
        (content / "cases" / "index.json", "cases", "index"),
        (content / "teaching" / "checkpoints.json", "training", "checkpoints"),
    ]
    for path, asset_type, slug in candidates:
        if path.exists():
            import_teaching_asset(path, asset_type, slug)
            counts["teaching_assets"] += 1
    registry_path = content / "traders" / "index.json"
    if registry_path.exists():
        from .trade_records import load_trader_registry, validate_trade_repository

        registry = load_trader_registry(registry_path)
        trade_days = validate_trade_repository((content / "trades").glob("*.json"), registry)
        projected = replace_trade_repository(settings.db_path, registry, trade_days)
        counts["traders"] = projected["traders"]
        counts["trade_groups"] = projected["trade_groups"]
        counts["trade_events"] = projected["trade_events"]
        counts["trade_note_contexts"] = projected["trade_note_contexts"]
    return counts


def _date_from_name(name: str) -> str:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", name)
    if not match:
        raise ValueError(f"Cannot infer trade date from {name}")
    return match.group(1)


def _fetch_prior_5m_closes(conn, ticker: str, trade_date: str, session_mode: str) -> list[float | None]:
    join = bar_market_day_join(conn, "bars_5m")
    rows = conn.execute(
        f"""
        SELECT bars_5m.close
        {join}
        WHERE market_days.ticker=?
          AND market_days.session_mode=?
          AND market_days.trade_date<?
          AND bars_5m.close IS NOT NULL
        ORDER BY market_days.trade_date DESC, bars_5m.idx DESC
        LIMIT ?
        """,
        (ticker, session_mode, trade_date, max(BAR_MA_WINDOWS) - 1),
    ).fetchall()
    return [row["close"] for row in reversed(rows)]


def _prepare_bar_owner(
    conn: sqlite3.Connection,
    market_day_id: int,
    ticker: str,
    trade_date: str,
    session_mode: str,
    meta: dict[str, Any],
    bars_1m: list[dict[str, Any]],
    bars_5m: list[dict[str, Any]],
    path: Path,
) -> tuple[str, int | str]:
    if not bars_use_datasets(conn):
        return "market_day_id", market_day_id
    checksum = hashlib.sha256(
        json.dumps(
            {"bars_1m": bars_1m, "bars_5m": bars_5m},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    safe_session = re.sub(r"[^a-z0-9]+", "_", session_mode.lower()).strip("_")
    dataset_id = f"mds_{ticker.lower()}_{trade_date.replace('-', '')}_{safe_session}_{checksum[:16]}"
    conn.execute(
        "UPDATE market_datasets SET state='superseded' "
        "WHERE market_day_id=? AND state='active' AND dataset_id<>?",
        (market_day_id, dataset_id),
    )
    conn.execute(
        """
        INSERT INTO market_datasets(
            dataset_id, market_day_id, provider, venue, source_revision, fetcher_revision,
            imported_at, checksum, quality_json, state
        ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, 'active')
        ON CONFLICT(dataset_id) DO UPDATE SET
            provider=excluded.provider,
            venue=excluded.venue,
            source_revision=excluded.source_revision,
            fetcher_revision=excluded.fetcher_revision,
            imported_at=CURRENT_TIMESTAMP,
            checksum=excluded.checksum,
            quality_json=excluded.quality_json,
            state='active'
        """,
        (
            dataset_id,
            market_day_id,
            str(meta.get("provider") or meta.get("source") or path.name),
            meta.get("venue"),
            meta.get("source_revision") or meta.get("generated_at"),
            meta.get("fetcher_revision") or meta.get("fetch_revision"),
            checksum,
            json.dumps(meta.get("quality") or {}, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        ),
    )
    return "dataset_id", dataset_id


BAR_INSERT_SQL = """
INSERT INTO {table}(
    {owner_column}, idx, ts, time, open, high, low, close, volume, vwap,
    ha_open, ha_high, ha_low, ha_close, m5, m10, m20, m30, m50, m60, m120, m200, m250
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
