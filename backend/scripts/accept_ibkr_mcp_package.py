"""Explicit operator package -> existing atomic pair acceptance. No broker login."""
from __future__ import annotations

import argparse
import contextlib
import json
import tempfile
from pathlib import Path

from app.services.db_safety import bar_market_day_join, capture_database_token, readonly_connect
from app.services.ibkr_mcp import build_payload, load_package
from scripts.update_spy_qqq_market_day import accept_staged_pair, capture_git_baseline


def warmup(db_path: Path, symbol: str, target: str) -> tuple[dict, list]:
    values, sources = {}, set()
    with contextlib.closing(readonly_connect(db_path)) as conn:
        for frame in ("1m", "5m"):
            table = f"bars_{frame}"
            join = bar_market_day_join(conn, table)
            rows = conn.execute(
                f"SELECT {table}.close, market_days.trade_date, market_days.meta_json {join} "
                "WHERE market_days.ticker=? AND market_days.trade_date<? "
                f"AND market_days.session_mode='extended' AND {table}.close IS NOT NULL "
                f"ORDER BY market_days.trade_date DESC, {table}.idx DESC LIMIT 249",
                (symbol, target),
            ).fetchall()
            values[frame] = [r["close"] for r in reversed(rows)]
            for row in rows:
                sources.add((row["trade_date"], json.loads(row["meta_json"] or "{}").get("provider", "unknown")))
    return values, [{"date": day, "provider": source} for day, source in sorted(sources)]


def accept_package(package_path: Path, package_sha: str, target: str, repo: Path, db_path: Path, seed_dir: Path) -> dict:
    baseline = capture_git_baseline(repo)
    token = capture_database_token(db_path)
    with contextlib.closing(readonly_connect(db_path)) as conn:
        existing = conn.execute("SELECT ticker FROM market_days WHERE trade_date=? AND session_mode='extended' AND ticker IN ('SPY','QQQ')", (target,)).fetchall()
        if existing:
            raise ValueError("MCP package entry point refuses to replace an existing market day")
    package = load_package(package_path, package_sha, target)
    with tempfile.TemporaryDirectory(prefix="tang-mcp-pair-") as temporary:
        paths = {}
        for symbol in ("SPY", "QQQ"):
            prior, sources = warmup(db_path, symbol, target)
            payload = build_payload(symbol, package, prior, sources)
            path = Path(temporary) / f"{symbol}_{target}.json"
            path.write_text(json.dumps(payload, ensure_ascii=False, allow_nan=False))
            paths[symbol] = path
        # Recheck the pinned input immediately before the drift-checked acceptance.
        load_package(package_path, package_sha, target)
        result = accept_staged_pair(paths, target, "ibkr_mcp", db_path, seed_dir, baseline, expected_db_token=token, content_dir=repo / "content")
    result["pair"]["manifest_sha256"] = package_sha
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date")
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--repo-dir", type=Path, required=True)
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--accepted-seed-dir", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if args.validate_only:
        package = load_package(args.package, args.manifest_sha256, args.date)
        result = {"trade_date": args.date, "provider": "ibkr_mcp", "tickers": ["SPY", "QQQ"], "manifest_sha256": args.manifest_sha256, "latest_1m": {symbol: package["quality"][symbol]["last"] for symbol in ("SPY", "QQQ")}}
    else:
        repo = args.repo_dir.resolve(strict=True)
        result = accept_package(args.package, args.manifest_sha256, args.date, repo, args.db_path or repo / "data/sqlite/tang_strategy_live_extended.db", args.accepted_seed_dir or repo / "data/seed/market-data/live_extended")
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
