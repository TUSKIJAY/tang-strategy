from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from ..db import connect, init_db
from ..settings import settings
from .bar_utils import bar_tuple_from_seed


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

    with connect() as conn:
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
        conn.execute("DELETE FROM bars_1m WHERE market_day_id=?", (market_day_id,))
        conn.executemany(
            BAR_INSERT_SQL.format(table="bars_1m"),
            [bar_tuple_from_seed(market_day_id, i, b) for i, b in enumerate(bars_1m)],
        )
        return market_day_id


def import_strategy_json(path: Path) -> int:
    init_db()
    strategy = json.loads(path.read_text(encoding="utf-8"))
    name = str(strategy.get("name") or path.stem)
    version = str(strategy.get("version") or "unknown")
    slug = slugify(f"{path.stem}-{version}")
    body = json.dumps(strategy, ensure_ascii=False, separators=(",", ":"))
    with connect() as conn:
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
    with connect() as conn:
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
    counts = {"market_days": 0, "strategies": 0, "teaching_assets": 0}
    for path in sorted(settings.live_extended_dir.glob("**/*.json")):
        if path.name.startswith("SPY_") or path.name.startswith("SPX_"):
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
    return counts


def _date_from_name(name: str) -> str:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", name)
    if not match:
        raise ValueError(f"Cannot infer trade date from {name}")
    return match.group(1)


BAR_INSERT_SQL = """
INSERT INTO {table}(
    market_day_id, idx, ts, time, open, high, low, close, volume, vwap,
    ha_open, ha_high, ha_low, ha_close, m5, m10, m20, m30, m50, m60, m120, m200, m250
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
