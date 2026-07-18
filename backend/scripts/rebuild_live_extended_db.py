from __future__ import annotations

import argparse
import contextlib
import json
import math
import os
import re
import secrets
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from app.services.db_safety import (
    DatabaseToken,
    create_consistent_snapshot,
    db_write_lock,
    fsync_directory,
    fsync_file,
    promote_candidate,
    readonly_connect,
    validate_sqlite,
)


REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
DEFAULT_DB_PATH = REPO_DIR / "data" / "sqlite" / "tang_strategy_live_extended.db"
DEFAULT_LIVE_EXTENDED_DIR = REPO_DIR / "data" / "seed" / "market-data" / "live_extended"
DEFAULT_STRATEGIES_DIR = REPO_DIR / "strategies" / "json"
DEFAULT_CONTENT_DIR = REPO_DIR / "content"


@dataclass(frozen=True)
class MarketSeed:
    path: Path
    ticker: str
    trade_date: str
    session_mode: str
    bars_1m: int
    bars_5m: int

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.ticker, self.trade_date, self.session_mode)

    @property
    def label(self) -> str:
        return "|".join(self.key)


@dataclass(frozen=True)
class RuntimeKeys:
    market_days: frozenset[tuple[str, str, str]]
    strategies: frozenset[str]
    teaching_assets: frozenset[tuple[str, str, str]]


@dataclass(frozen=True)
class SeedManifest:
    market_seeds: tuple[MarketSeed, ...]
    strategy_slugs: frozenset[str]
    teaching_assets: frozenset[tuple[str, str, str]]

    @property
    def market_keys(self) -> frozenset[tuple[str, str, str]]:
        return frozenset(seed.key for seed in self.market_seeds)


def discover_seed_manifest(
    live_extended_dir: Path,
    strategies_dir: Path,
    content_dir: Path,
) -> SeedManifest:
    market_paths = sorted(
        path
        for path in live_extended_dir.expanduser().resolve().glob("**/*.json")
        if path.name.startswith("SPY_") or path.name.startswith("SPX_")
    )
    if not market_paths:
        raise RuntimeError(
            f"Refusing to rebuild: no SPY_/SPX_ market-day JSON files found under "
            f"{live_extended_dir.expanduser().resolve()}"
        )
    market_seeds = tuple(parse_market_seed(path) for path in market_paths)
    labels = [seed.label for seed in market_seeds]
    if len(labels) != len(set(labels)):
        duplicates = sorted(label for label in set(labels) if labels.count(label) > 1)
        raise RuntimeError(f"Refusing to rebuild: duplicate market-day logical keys: {duplicates}")

    strategy_slugs: set[str] = set()
    strategy_paths = sorted(strategies_dir.expanduser().resolve().glob("*.json"))
    for path in strategy_paths:
        if path.name.endswith("schema.json"):
            continue
        strategy = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(strategy, dict):
            raise RuntimeError(f"Strategy JSON must be an object: {path}")
        name = str(strategy.get("name") or path.stem)
        version = str(strategy.get("version") or "unknown")
        slug = slugify(f"{path.stem}-{version}")
        if slug in strategy_slugs:
            raise RuntimeError(f"Duplicate strategy slug from seed: {slug}")
        if not name:
            raise RuntimeError(f"Strategy name is empty: {path}")
        strategy_slugs.add(slug)

    teaching_assets: set[tuple[str, str, str]] = set()
    for path, asset_type, version, slug in teaching_sources(content_dir):
        if path.exists():
            json.loads(path.read_text(encoding="utf-8"))
            teaching_assets.add((asset_type, version, slug))

    if not strategy_slugs:
        raise RuntimeError(f"Refusing to rebuild: no strategy JSON found under {strategies_dir}")
    return SeedManifest(
        market_seeds=market_seeds,
        strategy_slugs=frozenset(strategy_slugs),
        teaching_assets=frozenset(teaching_assets),
    )


def parse_market_seed(path: Path) -> MarketSeed:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"Market-day seed must be a JSON object: {path}")
    meta = data.get("meta") or {}
    if not isinstance(meta, dict):
        raise RuntimeError(f"Market-day meta must be an object: {path}")
    ticker = str(meta.get("ticker") or path.name.split("_")[0]).upper()
    trade_date = str(meta.get("date") or date_from_name(path.name))
    session_mode = str(meta.get("session_mode") or meta.get("session_type") or "rth")
    bars_1m = data.get("bars_1m")
    bars_5m = data.get("bars_5m")
    if not isinstance(bars_1m, list) or not isinstance(bars_5m, list):
        raise RuntimeError(f"Market-day bars_1m and bars_5m must both be lists: {path}")
    if not bars_1m or not bars_5m:
        raise RuntimeError(
            f"Refusing to rebuild from empty bars: {ticker}|{trade_date}|{session_mode} "
            f"bars_1m={len(bars_1m)} bars_5m={len(bars_5m)}"
        )
    validate_seed_bars(path, "bars_1m", bars_1m)
    validate_seed_bars(path, "bars_5m", bars_5m)
    counts = meta.get("counts") or {}
    if isinstance(counts, dict):
        for field, actual in (("bars_1m", len(bars_1m)), ("bars_5m", len(bars_5m))):
            if field in counts and int(counts[field]) != actual:
                raise RuntimeError(
                    f"Seed metadata count mismatch for {path}: "
                    f"{field} declared={counts[field]} actual={actual}"
                )
    return MarketSeed(path, ticker, trade_date, session_mode, len(bars_1m), len(bars_5m))


def validate_seed_bars(path: Path, timeframe: str, bars: list[Any]) -> None:
    timestamps: set[str] = set()
    for index, bar in enumerate(bars):
        if not isinstance(bar, dict):
            raise RuntimeError(f"{path} {timeframe}[{index}] must be an object")
        timestamp = str(pick_value(bar, "ts") or "")
        if not timestamp or timestamp in timestamps:
            raise RuntimeError(
                f"{path} {timeframe}[{index}] has missing/duplicate timestamp: {timestamp!r}"
            )
        timestamps.add(timestamp)
        open_price = finite_number(path, timeframe, index, bar, "O", "open")
        high_price = finite_number(path, timeframe, index, bar, "H", "high")
        low_price = finite_number(path, timeframe, index, bar, "L", "low")
        close_price = finite_number(path, timeframe, index, bar, "C", "close")
        volume = finite_number(path, timeframe, index, bar, "V", "volume")
        if min(open_price, high_price, low_price, close_price) <= 0:
            raise RuntimeError(f"{path} {timeframe}[{index}] has non-positive OHLC")
        if high_price < max(open_price, close_price, low_price):
            raise RuntimeError(f"{path} {timeframe}[{index}] has invalid high")
        if low_price > min(open_price, close_price, high_price):
            raise RuntimeError(f"{path} {timeframe}[{index}] has invalid low")
        if volume < 0:
            raise RuntimeError(f"{path} {timeframe}[{index}] has negative volume")
        vwap = pick_value(bar, "vw", "vwap")
        if vwap is not None and not math.isfinite(float(vwap)):
            raise RuntimeError(f"{path} {timeframe}[{index}] has non-finite VWAP")


def finite_number(
    path: Path,
    timeframe: str,
    index: int,
    bar: dict[str, Any],
    *keys: str,
) -> float:
    value = pick_value(bar, *keys)
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise RuntimeError(
            f"{path} {timeframe}[{index}] missing/non-numeric {'/'.join(keys)}: {value!r}"
        ) from exc
    if not math.isfinite(number):
        raise RuntimeError(f"{path} {timeframe}[{index}] has non-finite {'/'.join(keys)}")
    return number


def run_candidate_import(
    candidate_path: Path,
    live_extended_dir: Path,
    strategies_dir: Path,
    content_dir: Path,
) -> dict[str, Any]:
    environment = os.environ.copy()
    environment.update({
        "PYTHONPATH": ".",
        "TANG_DB_PATH": str(candidate_path),
        "TANG_LIVE_EXTENDED_DIR": str(live_extended_dir.expanduser().resolve()),
        "TANG_STRATEGIES_DIR": str(strategies_dir.expanduser().resolve()),
        "TANG_CONTENT_DIR": str(content_dir.expanduser().resolve()),
    })
    completed = subprocess.run(
        [sys.executable, "scripts/import_seed.py"],
        cwd=BACKEND_DIR,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Candidate seed import failed: "
            f"stdout={completed.stdout!r} stderr={completed.stderr!r}"
        )
    return {
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def runtime_keys(db_path: Path) -> RuntimeKeys:
    with contextlib.closing(readonly_connect(db_path)) as connection:
        market_days = frozenset(
            (str(row[0]), str(row[1]), str(row[2]))
            for row in connection.execute(
                "SELECT ticker, trade_date, session_mode FROM market_days"
            ).fetchall()
        )
        strategies = frozenset(
            str(row[0]) for row in connection.execute("SELECT slug FROM strategies").fetchall()
        )
        teaching_assets = frozenset(
            (str(row[0]), str(row[1]), str(row[2]))
            for row in connection.execute(
                "SELECT asset_type, version, slug FROM teaching_assets"
            ).fetchall()
        )
    return RuntimeKeys(market_days, strategies, teaching_assets)


def validate_candidate_semantics(
    candidate_path: Path,
    manifest: SeedManifest,
    current_keys: RuntimeKeys | None,
    allow_date_loss: bool,
) -> dict[str, Any]:
    validate_sqlite(candidate_path)
    candidate_keys = runtime_keys(candidate_path)
    if candidate_keys.market_days != manifest.market_keys:
        missing = sorted(manifest.market_keys - candidate_keys.market_days)
        extra = sorted(candidate_keys.market_days - manifest.market_keys)
        raise RuntimeError(
            "Candidate market-day keys do not match discovered seed keys: "
            f"missing={format_keys(missing)} extra={format_keys(extra)}"
        )
    if candidate_keys.strategies != manifest.strategy_slugs:
        raise RuntimeError(
            "Candidate strategy slugs do not match discovered strategy files: "
            f"missing={sorted(manifest.strategy_slugs - candidate_keys.strategies)} "
            f"extra={sorted(candidate_keys.strategies - manifest.strategy_slugs)}"
        )
    if candidate_keys.teaching_assets != manifest.teaching_assets:
        raise RuntimeError(
            "Candidate teaching keys do not match discovered teaching files: "
            f"missing={sorted(manifest.teaching_assets - candidate_keys.teaching_assets)} "
            f"extra={sorted(candidate_keys.teaching_assets - manifest.teaching_assets)}"
        )

    by_key = {seed.key: seed for seed in manifest.market_seeds}
    with contextlib.closing(readonly_connect(candidate_path)) as connection:
        active_strategies = int(connection.execute(
            "SELECT COUNT(*) FROM strategies WHERE active=1"
        ).fetchone()[0])
        if active_strategies <= 0:
            raise RuntimeError("Candidate has no active strategies")
        for key, seed in by_key.items():
            day = connection.execute(
                "SELECT id, bar_count_1m, bar_count_5m FROM market_days "
                "WHERE ticker=? AND trade_date=? AND session_mode=?",
                key,
            ).fetchone()
            if day is None:
                raise RuntimeError(f"Candidate is missing imported day: {'|'.join(key)}")
            for table, declared_column, expected in (
                ("bars_1m", "bar_count_1m", seed.bars_1m),
                ("bars_5m", "bar_count_5m", seed.bars_5m),
            ):
                actual, distinct_indexes = connection.execute(
                    f"SELECT COUNT(*), COUNT(DISTINCT idx) FROM {table} WHERE market_day_id=?",
                    (day["id"],),
                ).fetchone()
                declared = int(day[declared_column])
                if actual <= 0 or actual != distinct_indexes or actual != declared or actual != expected:
                    raise RuntimeError(
                        f"Candidate {seed.label} {table} semantic count mismatch: "
                        f"seed={expected} declared={declared} actual={actual} "
                        f"distinct_indexes={distinct_indexes}"
                    )

    if current_keys is not None:
        missing_days = current_keys.market_days - candidate_keys.market_days
        if missing_days and not allow_date_loss:
            raise RuntimeError(
                "Refusing DB replacement because candidate would lose market days:\n"
                + "\n".join(f"  - {'|'.join(key)}" for key in sorted(missing_days))
            )
        missing_strategies = current_keys.strategies - candidate_keys.strategies
        if missing_strategies:
            raise RuntimeError(
                "Refusing DB replacement because candidate would lose strategies: "
                f"{sorted(missing_strategies)}"
            )
        missing_teaching = current_keys.teaching_assets - candidate_keys.teaching_assets
        if missing_teaching:
            raise RuntimeError(
                "Refusing DB replacement because candidate would lose teaching assets: "
                f"{sorted(missing_teaching)}"
            )

    return {
        "market_days": len(candidate_keys.market_days),
        "strategies": len(candidate_keys.strategies),
        "teaching_assets": len(candidate_keys.teaching_assets),
        "allow_date_loss": allow_date_loss,
    }


def rebuild_db(
    db_path: Path,
    live_extended_dir: Path,
    strategies_dir: Path,
    content_dir: Path,
    allow_date_loss: bool = False,
    candidate_importer: Callable[[Path, Path, Path, Path], dict[str, Any]] = run_candidate_import,
) -> dict[str, Any]:
    target = db_path.expanduser().resolve()
    manifest = discover_seed_manifest(live_extended_dir, strategies_dir, content_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    nonce = secrets.token_hex(6)
    candidate = target.parent / f".{target.stem}.rebuild-{nonce}.candidate.db"
    backup = target.parent / f".{target.stem}.rebuild-{nonce}.backup.db"
    baseline_token: DatabaseToken | None = None
    current_keys: RuntimeKeys | None = None
    promoted = False
    try:
        if target.exists():
            baseline_token = create_consistent_snapshot(target, backup)
            current_keys = runtime_keys(backup)
        import_result = candidate_importer(
            candidate,
            live_extended_dir,
            strategies_dir,
            content_dir,
        )
        validation = validate_candidate_semantics(
            candidate,
            manifest,
            current_keys,
            allow_date_loss,
        )
        if baseline_token is not None:
            promote_candidate(
                target,
                candidate,
                baseline_token,
                backup,
                lambda path: validate_candidate_semantics(
                    path,
                    manifest,
                    current_keys,
                    allow_date_loss,
                ),
            )
        else:
            validate_sqlite(candidate)
            fsync_file(candidate)
            with db_write_lock(target):
                if target.exists():
                    raise RuntimeError("Refusing fresh DB promotion because target appeared concurrently")
                os.replace(candidate, target)
                fsync_directory(target.parent)
                validate_candidate_semantics(target, manifest, None, allow_date_loss)
        promoted = True
        return {
            "db_path": str(target),
            "candidate_import": import_result,
            "validation": validation,
            "promoted": True,
        }
    finally:
        if candidate.exists() and not promoted:
            candidate.unlink()
        if backup.exists():
            backup.unlink()
        for auxiliary in (
            Path(f"{candidate}.write.lock"),
            Path(f"{backup}.write.lock"),
        ):
            if auxiliary.exists():
                auxiliary.unlink()


def teaching_sources(content_dir: Path) -> tuple[tuple[Path, str, str, str], ...]:
    content = content_dir.expanduser().resolve()
    return (
        (content / "rules" / "compiled" / "index.json", "rules", "default", "compiled-index"),
        (content / "cases" / "index.json", "cases", "default", "index"),
        (content / "teaching" / "checkpoints.json", "training", "default", "checkpoints"),
    )


def pick_value(source: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in source:
            return source[key]
    return None


def date_from_name(name: str) -> str:
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", name)
    if not match:
        raise RuntimeError(f"Cannot infer trade date from {name}")
    return match.group(1)


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower().strip())
    return normalized.strip("-") or "item"


def format_keys(keys: list[tuple[str, str, str]]) -> list[str]:
    return ["|".join(key) for key in keys]


def path_from_cli(value: Path | None, environment_name: str, fallback: Path) -> Path:
    if value is not None:
        return value
    environment_value = os.environ.get(environment_name)
    return Path(environment_value) if environment_value else fallback


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild live_extended into a verified candidate and atomically promote it."
    )
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--live-extended-dir", type=Path)
    parser.add_argument("--strategies-dir", type=Path)
    parser.add_argument("--content-dir", type=Path)
    parser.add_argument(
        "--allow-date-loss",
        action="store_true",
        help="Explicitly allow intentional market-day shrink; semantic/non-market gates still apply.",
    )
    args = parser.parse_args(argv)
    try:
        result = rebuild_db(
            db_path=path_from_cli(args.db_path, "TANG_DB_PATH", DEFAULT_DB_PATH),
            live_extended_dir=path_from_cli(
                args.live_extended_dir,
                "TANG_LIVE_EXTENDED_DIR",
                DEFAULT_LIVE_EXTENDED_DIR,
            ),
            strategies_dir=path_from_cli(
                args.strategies_dir,
                "TANG_STRATEGIES_DIR",
                DEFAULT_STRATEGIES_DIR,
            ),
            content_dir=path_from_cli(args.content_dir, "TANG_CONTENT_DIR", DEFAULT_CONTENT_DIR),
            allow_date_loss=args.allow_date_loss,
        )
    except Exception as exc:
        print(f"Rebuild refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
