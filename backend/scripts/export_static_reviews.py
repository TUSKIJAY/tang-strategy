from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.db import connect, init_db
from app.services.bar_utils import BAR_MA_WINDOWS, bar_row_to_payload, build_5m_bars_from_1m, recalculate_ma_fields
from app.services.tang_trades import load_tang_trades
from app.settings import settings


BAR_SELECT = (
    "SELECT market_day_id, idx, ts, time, open, high, low, close, volume, vwap, "
    "ha_open, ha_high, ha_low, ha_close, m5, m10, m20, m30, m50, m60, m120, m200, m250 "
    "FROM {table} WHERE market_day_id=? ORDER BY idx"
)


def slugify_day(day: dict[str, Any]) -> str:
    ticker = str(day["ticker"]).lower()
    session = str(day["session_mode"] or "session").lower().replace("_", "-")
    return f"{ticker}-{day['trade_date']}-{session}"


def include_strategy(row: dict[str, Any], family_filter: set[str]) -> bool:
    if not family_filter:
        return True
    haystack = " ".join([
        str(row.get("slug") or ""),
        str(row.get("name") or ""),
        str(row.get("version") or ""),
    ]).lower()
    return any(f"v{family}" in haystack or haystack.startswith(family) for family in family_filter)


def select_strategies(conn, families: str) -> list[dict[str, Any]]:
    family_filter = {item.strip().lower().removeprefix("v") for item in families.split(",") if item.strip()}
    rows = [
        dict(row)
        for row in conn.execute(
            """
            SELECT * FROM strategies
            WHERE active=1
            ORDER BY name, version, slug
            """,
        ).fetchall()
    ]
    strategies = []
    for row in rows:
        if not include_strategy(row, family_filter):
            continue
        row["json"] = json.loads(row.pop("json_body"))
        strategies.append(row)
    if not strategies:
        raise RuntimeError(f"No active strategies matched families: {families}")
    return strategies


def latest_market_days(conn, limit: int, ticker: str | None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM market_days"
    params: list[Any] = []
    if ticker:
        sql += " WHERE ticker=?"
        params.append(ticker.upper())
    sql += " ORDER BY trade_date DESC, ticker ASC, session_mode ASC LIMIT ?"
    params.append(limit)
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def build_day_payload(conn, day: dict[str, Any]) -> dict[str, Any]:
    rows = conn.execute(BAR_SELECT.format(table="bars_1m"), (day["id"],)).fetchall()
    stored_5m_rows = conn.execute(BAR_SELECT.format(table="bars_5m"), (day["id"],)).fetchall()
    bars_5m_source = (
        [bar_row_to_payload(row) for row in stored_5m_rows]
        if stored_5m_rows
        else build_5m_bars_from_1m(rows, source_vwap_mode="session_cumulative")
    )
    bars_5m = recalculate_ma_fields(bars_5m_source, warmup_closes=fetch_prior_5m_closes(conn, day))
    tang_trades = load_tang_trades(day["ticker"], day["trade_date"])
    meta = json.loads(day["meta_json"] or "{}")
    meta.update({
        "ticker": day["ticker"],
        "date": day["trade_date"],
        "session_mode": day["session_mode"],
        "source": day["source"],
        "counts": {
            "bars_1m": len(rows),
            "bars_5m": len(bars_5m),
            "tang_trades": len(tang_trades["trades"]),
        },
    })
    return {
        "meta": meta,
        "market_day": {
            "id": day["id"],
            "ticker": day["ticker"],
            "trade_date": day["trade_date"],
            "session_mode": day["session_mode"],
            "title": day["title"],
        },
        "bars_1m": [bar_row_to_payload(row) for row in rows],
        "bars_5m": bars_5m,
        "annotations_1m": [],
        "annotations_5m": [],
        "tang_trades": tang_trades,
    }


def fetch_prior_5m_closes(conn, day: dict[str, Any]) -> list[float | None]:
    rows = conn.execute(
        """
        SELECT bars_5m.close
        FROM bars_5m
        JOIN market_days ON market_days.id = bars_5m.market_day_id
        WHERE market_days.ticker=?
          AND market_days.session_mode=?
          AND market_days.trade_date<?
          AND bars_5m.close IS NOT NULL
        ORDER BY market_days.trade_date DESC, bars_5m.idx DESC
        LIMIT ?
        """,
        (day["ticker"], day["session_mode"], day["trade_date"], max(BAR_MA_WINDOWS) - 1),
    ).fetchall()
    return [row["close"] for row in reversed(rows)]


def export_static_reviews(output_dir: Path, limit: int, ticker: str | None, strategy_families: str) -> dict[str, Any]:
    init_db()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    days_dir = output_dir / "days"
    strategies_dir = output_dir / "strategies"
    days_dir.mkdir(parents=True, exist_ok=True)
    strategies_dir.mkdir(parents=True, exist_ok=True)

    with connect() as conn:
        strategies = select_strategies(conn, strategy_families)
        days = latest_market_days(conn, limit, ticker)
        if not days:
            scope = f" for ticker {ticker.upper()}" if ticker else ""
            raise RuntimeError(f"No market days found{scope} in {settings.db_path}")

        strategy_items = []
        for strategy in strategies:
            filename = f"{strategy['slug']}.json"
            strategy_payload = {
                "id": strategy["id"],
                "name": strategy["name"],
                "version": strategy["version"],
                "slug": strategy["slug"],
                "description": strategy["description"],
                "json": strategy["json"],
            }
            (strategies_dir / filename).write_text(
                json.dumps(strategy_payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            strategy_items.append({
                "id": strategy["id"],
                "name": strategy["name"],
                "version": strategy["version"],
                "slug": strategy["slug"],
                "description": strategy["description"],
                "file": f"strategies/{filename}",
            })

        items = []
        for day in days:
            slug = slugify_day(day)
            filename = f"{slug}.json"
            payload = build_day_payload(conn, day)
            (days_dir / filename).write_text(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )
            items.append({
                "slug": slug,
                "file": f"days/{filename}",
                "ticker": day["ticker"],
                "trade_date": day["trade_date"],
                "session_mode": day["session_mode"],
                "title": day["title"] or f"{day['ticker']} {day['trade_date']}",
                "bars_1m": payload["meta"]["counts"]["bars_1m"],
                "bars_5m": payload["meta"]["counts"]["bars_5m"],
            })

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "limit": limit,
        "ticker": ticker,
        "strategy_families": strategy_families,
        "strategies": strategy_items,
        "reviews": items,
    }
    (output_dir / "index.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Export latest market-day reviews for static GitHub Pages hosting.")
    parser.add_argument("--output", type=Path, default=Path("../frontend/public/reviews"))
    parser.add_argument("--limit", type=int, default=int(os.environ.get("TANG_STATIC_REVIEW_LIMIT", "250")))
    parser.add_argument("--ticker", default=os.environ.get("TANG_STATIC_REVIEW_TICKER", "SPY"))
    parser.add_argument("--strategy-families", default=os.environ.get("TANG_STATIC_REVIEW_STRATEGY_FAMILIES", "v3,v4,v5"))
    args = parser.parse_args()

    manifest = export_static_reviews(
        output_dir=args.output,
        limit=args.limit,
        ticker=args.ticker or None,
        strategy_families=args.strategy_families,
    )
    print(
        f"Exported {len(manifest['reviews'])} static days and {len(manifest['strategies'])} strategies "
        f"to {args.output}"
    )


if __name__ == "__main__":
    main()
