from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Mapping
from zoneinfo import ZoneInfo

from app.db import connect, migrate_candidate_schema
from app.services.db_safety import (
    DatabaseToken,
    capture_database_token,
    create_consistent_snapshot,
    db_write_lock,
    day_sha256,
    file_sha256,
    fsync_directory,
    fsync_file,
    promote_candidate,
    readonly_connect,
    table_sha256,
    validate_exactly_one_active_dataset,
    validate_sqlite,
)
from app.services.importer import _import_market_data
from scripts.rebuild_live_extended_db import parse_market_seed, runtime_keys


REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
DEFAULT_DB_PATH = REPO_DIR / "data" / "sqlite" / "tang_strategy_live_extended.db"
DEFAULT_ACCEPTED_SEED_DIR = REPO_DIR / "data" / "seed" / "market-data" / "live_extended"
PAIR = ("SPY", "QQQ")
SESSION_MODE = "extended"
PROVIDERS = {"tradingview", "ibkr"}
TRADINGVIEW_EXCHANGES = {"SPY": "AMEX", "QQQ": "NASDAQ"}

FetchOne = Callable[[str, str, Path, str], Path]
ReplaceFile = Callable[[Path, Path], None]


def _backend_subprocess_environment() -> dict[str, str]:
    environment = os.environ.copy()
    inherited = environment.get("PYTHONPATH", "")
    entries = [str(BACKEND_DIR)]
    if inherited:
        entries.append(inherited)
    environment["PYTHONPATH"] = os.pathsep.join(entries)
    return environment


def resolve_latest_completed_nyse_session(now: datetime | None = None) -> str:
    try:
        import pandas_market_calendars as market_calendars
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pandas_market_calendars is required; install backend/requirements-tv.txt"
        ) from exc

    instant = now or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    calendar = market_calendars.get_calendar("NYSE")
    end = instant.date()
    start = end - timedelta(days=14)
    schedule = calendar.schedule(start_date=start, end_date=end)
    completed = [
        index.date().isoformat()
        for index, row in schedule.iterrows()
        if row["market_close"].to_pydatetime() <= instant.astimezone(timezone.utc)
    ]
    if not completed:
        raise RuntimeError(f"No completed NYSE session found from {start} through {end}")
    return completed[-1]


def capture_git_baseline(repo_dir: Path = REPO_DIR) -> dict[str, Any]:
    root = repo_dir.expanduser().resolve()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    return {"head": head, "status": status}


def fetch_one_symbol(symbol: str, trade_date: str, staging_dir: Path, provider: str) -> Path:
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported pair provider: {provider}")
    script = (
        "scripts/fetch_tv_live_extended_day.py"
        if provider == "tradingview"
        else "scripts/fetch_ib_live_extended_day.py"
    )
    command = [
        sys.executable,
        script,
        trade_date,
        "--symbol",
        symbol,
    ]
    if provider == "tradingview":
        try:
            exchange = TRADINGVIEW_EXCHANGES[symbol]
        except KeyError as exc:
            raise ValueError(f"No TradingView exchange configured for {symbol}") from exc
        command.extend(["--exchange", exchange])
    command.extend(["--output-dir", str(staging_dir), "--skip-import"])
    completed = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=_backend_subprocess_environment(),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"{provider} fetch failed: stdout={completed.stdout!r} stderr={completed.stderr!r}"
        )
    output = staging_dir / trade_date / f"{symbol}_{trade_date}.json"
    if not output.is_file():
        raise RuntimeError(f"{provider} fetch did not create expected payload: {output}")
    return output


def stage_provider_pair(
    trade_date: str,
    staging_dir: Path,
    provider: str,
    fetch_one: FetchOne = fetch_one_symbol,
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    errors: list[str] = []
    for symbol in PAIR:
        try:
            paths[symbol] = fetch_one(symbol, trade_date, staging_dir, provider)
        except Exception as exc:
            errors.append(f"{symbol}: {exc}")
    if errors:
        raise RuntimeError("Pair fetch refused; " + "; ".join(errors))
    return paths


def validate_staged_pair(
    payload_paths: Mapping[str, Path],
    trade_date: str,
    provider: str,
) -> dict[str, Any]:
    if provider not in PROVIDERS:
        raise ValueError(f"Unsupported pair provider: {provider}")
    _require_nyse_session(trade_date)
    if set(payload_paths) != set(PAIR):
        raise RuntimeError(
            f"Pair requires exactly {list(PAIR)} payloads; found {sorted(payload_paths)}"
        )

    payloads: dict[str, dict[str, Any]] = {}
    seeds = {}
    for symbol in PAIR:
        path = payload_paths[symbol].expanduser().resolve()
        seed = parse_market_seed(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        meta = payload.get("meta") or {}
        if seed.ticker != symbol:
            raise RuntimeError(f"{symbol} ticker gate failed: payload declares {seed.ticker}")
        if seed.trade_date != trade_date:
            raise RuntimeError(
                f"{symbol} date gate failed: expected {trade_date}, found {seed.trade_date}"
            )
        if seed.session_mode != SESSION_MODE:
            raise RuntimeError(
                f"{symbol} session gate failed: expected {SESSION_MODE}, found {seed.session_mode}"
            )
        payload_provider = str(meta.get("provider") or "").lower()
        if payload_provider != provider:
            raise RuntimeError(
                f"{symbol} provider gate failed: expected {provider}, found {payload_provider or 'missing'}"
            )
        _validate_payload_quality(symbol, payload, provider, trade_date)
        payloads[symbol] = payload
        seeds[symbol] = seed

    identities = {
        (seeds[symbol].trade_date, seeds[symbol].session_mode, str(payloads[symbol]["meta"]["provider"]).lower())
        for symbol in PAIR
    }
    if identities != {(trade_date, SESSION_MODE, provider)}:
        raise RuntimeError(f"Pair identity gate failed: {sorted(identities)}")
    return {
        "trade_date": trade_date,
        "session_mode": SESSION_MODE,
        "provider": provider,
        "tickers": list(PAIR),
        "counts": {
            symbol: {"bars_1m": seeds[symbol].bars_1m, "bars_5m": seeds[symbol].bars_5m}
            for symbol in PAIR
        },
        "payloads": payloads,
    }


@lru_cache(maxsize=64)
def _require_nyse_session(trade_date: str) -> None:
    try:
        import pandas_market_calendars as market_calendars
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pandas_market_calendars is required; install backend/requirements-tv.txt"
        ) from exc
    schedule = market_calendars.get_calendar("NYSE").schedule(
        start_date=trade_date,
        end_date=trade_date,
    )
    if schedule.empty:
        raise RuntimeError(f"Pair date gate failed: {trade_date} is not an NYSE trading session")


def _validate_payload_quality(
    symbol: str,
    payload: Mapping[str, Any],
    provider: str,
    trade_date: str,
) -> None:
    meta = payload.get("meta") or {}
    if meta.get("synthetic_padding") is True:
        raise RuntimeError(f"{symbol} quality gate failed: synthetic padding is forbidden")
    expected_1m_instants = _expected_nyse_bar_instants(trade_date, 1)
    expected_5m_instants = _expected_nyse_bar_instants(trade_date, 5)
    expected_1m = [instant.strftime("%H:%M") for instant in expected_1m_instants]
    expected_5m = [instant.strftime("%H:%M") for instant in expected_5m_instants]
    actual_1m = _rth_bar_instants(
        symbol,
        "1m",
        payload.get("bars_1m"),
        trade_date,
        expected_1m_instants,
    )
    actual_5m = _rth_bar_instants(
        symbol,
        "5m",
        payload.get("bars_5m"),
        trade_date,
        expected_5m_instants,
    )
    expected_1m_utc = [instant.astimezone(timezone.utc) for instant in expected_1m_instants]
    expected_5m_utc = [instant.astimezone(timezone.utc) for instant in expected_5m_instants]
    if actual_1m != expected_1m_utc:
        raise RuntimeError(
            f"{symbol} quality gate failed: RTH 1m bars={len(actual_1m)}, expected={len(expected_1m)}"
        )
    if actual_5m != expected_5m_utc:
        raise RuntimeError(
            f"{symbol} quality gate failed: RTH 5m bars={len(actual_5m)}, expected={len(expected_5m)}"
        )
    if provider == "tradingview":
        if str(meta.get("market_calendar") or "").upper() != "NYSE":
            raise RuntimeError(f"{symbol} quality gate failed: market_calendar must be NYSE")
        quality = meta.get("quality")
        if not isinstance(quality, dict):
            raise RuntimeError(f"{symbol} quality gate failed: quality receipt is missing")
        pairs = (
            ("rth_1m_bars", "rth_1m_expected", len(expected_1m)),
            ("rth_5m_bars", "rth_5m_expected", len(expected_5m)),
        )
        for actual_key, expected_key, calendar_expected in pairs:
            actual = int(quality.get(actual_key, -1))
            expected = int(quality.get(expected_key, -1))
            if actual != calendar_expected or expected != calendar_expected:
                raise RuntimeError(
                    f"{symbol} quality gate failed: {actual_key}={actual}, "
                    f"{expected_key}={expected}, calendar_expected={calendar_expected}"
                )
        if quality.get("rth_missing_minutes") != []:
            raise RuntimeError(f"{symbol} quality gate failed: missing RTH minutes")
        if "rth_duplicate_minutes" not in quality or int(quality["rth_duplicate_minutes"]) != 0:
            raise RuntimeError(f"{symbol} quality gate failed: duplicate RTH minutes")
    elif int(meta.get("gap_count", 0)) < 0:
        raise RuntimeError(f"{symbol} quality gate failed: invalid IB gap count")


@lru_cache(maxsize=128)
def _expected_nyse_bar_instants(trade_date: str, minutes: int) -> tuple[datetime, ...]:
    import pandas_market_calendars as market_calendars

    schedule = market_calendars.get_calendar("NYSE").schedule(
        start_date=trade_date,
        end_date=trade_date,
    )
    if schedule.empty:
        raise RuntimeError(f"Pair date gate failed: {trade_date} is not an NYSE trading session")
    row = schedule.iloc[0]
    eastern = ZoneInfo("America/New_York")
    cursor = row["market_open"].to_pydatetime().astimezone(eastern)
    close = row["market_close"].to_pydatetime().astimezone(eastern)
    result: list[datetime] = []
    while cursor < close:
        result.append(cursor)
        cursor += timedelta(minutes=minutes)
    return tuple(result)


def _rth_bar_instants(
    symbol: str,
    timeframe: str,
    raw_bars: Any,
    trade_date: str,
    expected: tuple[datetime, ...],
) -> list[datetime]:
    bars = raw_bars if isinstance(raw_bars, list) else []
    if not expected:
        return []
    eastern = ZoneInfo("America/New_York")
    expected_date = datetime.strptime(trade_date, "%Y-%m-%d").date()
    step = 5 if timeframe == "5m" else 1
    open_utc = expected[0].astimezone(timezone.utc)
    close_utc = (expected[-1] + timedelta(minutes=step)).astimezone(timezone.utc)
    actual: list[datetime] = []
    for index, bar in enumerate(bars):
        if not isinstance(bar, Mapping):
            raise RuntimeError(
                f"{symbol} quality gate failed: {timeframe}[{index}] must be an object"
            )
        timestamp_text = str(bar.get("ts") or "")
        try:
            parsed = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise RuntimeError(
                f"{symbol} quality gate failed: {timeframe}[{index}] has invalid ts={timestamp_text!r}"
            ) from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise RuntimeError(
                f"{symbol} quality gate failed: {timeframe}[{index}] ts must include an offset"
            )
        local = parsed.astimezone(eastern)
        if local.date() != expected_date:
            raise RuntimeError(
                f"{symbol} quality gate failed: {timeframe}[{index}] ts resolves to "
                f"{local.date().isoformat()}, expected {trade_date}"
            )
        displayed_time = str(bar.get("t") or bar.get("time") or "")
        if displayed_time != local.strftime("%H:%M"):
            raise RuntimeError(
                f"{symbol} quality gate failed: {timeframe}[{index}] t={displayed_time!r} "
                f"does not match ts={timestamp_text!r}"
            )
        instant_utc = parsed.astimezone(timezone.utc)
        if open_utc <= instant_utc < close_utc:
            actual.append(instant_utc)
    return actual


def _pair_lock_anchor(live: Path) -> Path:
    return live.with_name(f".{live.stem}.spy-qqq-pair.db")


def accept_staged_pair(
    payload_paths: Mapping[str, Path],
    trade_date: str,
    provider: str,
    db_path: Path,
    accepted_seed_dir: Path,
    git_baseline: Mapping[str, Any],
    expected_db_token: DatabaseToken | None = None,
    candidate_hook: Callable[[Path], None] | None = None,
    before_promote_hook: Callable[[Path], None] | None = None,
    replace_file: ReplaceFile = os.replace,
    pair_lock_timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    live = db_path.expanduser().resolve()
    with db_write_lock(
        _pair_lock_anchor(live),
        timeout_seconds=pair_lock_timeout_seconds,
    ):
        return _accept_staged_pair_locked(
            payload_paths,
            trade_date,
            provider,
            db_path,
            accepted_seed_dir,
            git_baseline,
            expected_db_token=expected_db_token,
            candidate_hook=candidate_hook,
            before_promote_hook=before_promote_hook,
            replace_file=replace_file,
        )


def _accept_staged_pair_locked(
    payload_paths: Mapping[str, Path],
    trade_date: str,
    provider: str,
    db_path: Path,
    accepted_seed_dir: Path,
    git_baseline: Mapping[str, Any],
    expected_db_token: DatabaseToken | None = None,
    candidate_hook: Callable[[Path], None] | None = None,
    before_promote_hook: Callable[[Path], None] | None = None,
    replace_file: ReplaceFile = os.replace,
) -> dict[str, Any]:
    validation = validate_staged_pair(payload_paths, trade_date, provider)
    live = db_path.expanduser().resolve()
    accepted_root = accepted_seed_dir.expanduser().resolve()
    if not live.is_file():
        raise FileNotFoundError(f"Tracked/runtime DB does not exist: {live}")

    nonce = uuid.uuid4().hex[:12]
    candidate = live.parent / f".{live.stem}.pair-{nonce}.candidate.db"
    backup = live.parent / f".{live.stem}.pair-{nonce}.backup.db"
    seed_records: list[dict[str, Any]] = []
    seed_committed = False
    promoted = False
    baseline_token: DatabaseToken | None = None
    try:
        baseline_token = create_consistent_snapshot(live, backup)
        if expected_db_token is not None and baseline_token != expected_db_token:
            raise RuntimeError(
                "Refusing pair update: live DB drifted during provider staging "
                f"(baseline={expected_db_token.as_dict()}, current={baseline_token.as_dict()})"
            )
        before_hash = baseline_token.byte_sha256
        shutil.copy2(backup, candidate)
        fsync_file(candidate)
        migrate_candidate_schema(candidate)
        baseline_keys = runtime_keys(backup)
        expected_pair = {(symbol, trade_date, SESSION_MODE) for symbol in PAIR}
        with contextlib.closing(readonly_connect(backup)) as baseline_connection:
            preserved_day_hashes = {
                key: day_sha256(baseline_connection, *key)
                for key in sorted(baseline_keys.market_days)
                if key not in expected_pair
            }

        with contextlib.closing(connect(candidate)) as connection, connection:
            for symbol in PAIR:
                payload = validation["payloads"][symbol]
                meta = payload["meta"]
                _import_market_data(
                    connection,
                    symbol,
                    trade_date,
                    SESSION_MODE,
                    meta,
                    payload["bars_1m"],
                    payload["bars_5m"],
                    payload_paths[symbol].expanduser().resolve(),
                )
        if candidate_hook is not None:
            candidate_hook(candidate)
        candidate_receipt = _validate_pair_candidate(
            candidate,
            backup,
            trade_date,
            provider,
            preserved_day_hashes,
        )

        seed_records = _prepare_seed_pair(payload_paths, accepted_root, trade_date, nonce)
        _commit_seed_pair(seed_records, replace_file)
        seed_committed = True
        if before_promote_hook is not None:
            before_promote_hook(live)
        promote_candidate(
            live,
            candidate,
            baseline_token,
            backup,
            lambda path: _validate_promoted_pair(path, baseline_keys.market_days, trade_date, provider),
        )
        promoted = True
        seed_committed = False
        cleanup_warnings: list[str] = []
        try:
            after_hash = file_sha256(live)
        except Exception as exc:
            after_hash = "unavailable"
            cleanup_warnings.append(f"post-accept DB hash capture failed: {exc}")
        try:
            _finalize_seed_pair(seed_records)
        except Exception as exc:
            cleanup_warnings.append(f"accepted-seed artifact cleanup failed: {exc}")
        seed_records = []
        if backup.exists():
            try:
                backup.unlink()
            except Exception as exc:
                cleanup_warnings.append(f"verified DB backup cleanup failed: {exc}")
        return {
            "status": "accepted",
            "git_baseline": dict(git_baseline),
            "db": {
                "path": str(live),
                "before_sha256": before_hash,
                "after_sha256": after_hash,
                "baseline_token": baseline_token.as_dict(),
            },
            "pair": {key: value for key, value in validation.items() if key != "payloads"},
            "candidate": candidate_receipt,
            "accepted_seeds": [
                str(accepted_root / trade_date / f"{symbol}_{trade_date}.json") for symbol in PAIR
            ],
            "cleanup_warnings": cleanup_warnings,
        }
    except Exception as exc:
        if seed_committed:
            try:
                _rollback_seed_pair(seed_records)
                seed_records = []
            except Exception as rollback_exc:
                raise RuntimeError(
                    f"Pair update failed and seed rollback also failed: {rollback_exc}"
                ) from exc
        raise
    finally:
        if seed_records:
            _cleanup_seed_artifacts(seed_records)
        if candidate.exists() and not promoted:
            candidate.unlink()
        if backup.exists() and not promoted:
            backup.unlink()
        for path in (Path(f"{candidate}.write.lock"), Path(f"{backup}.write.lock")):
            if path.exists():
                path.unlink()


def _validate_pair_candidate(
    candidate: Path,
    baseline: Path,
    trade_date: str,
    provider: str,
    preserved_day_hashes: Mapping[tuple[str, str, str], Mapping[str, str]],
) -> dict[str, Any]:
    validate_sqlite(candidate)
    baseline_keys = runtime_keys(baseline)
    candidate_keys = runtime_keys(candidate)
    expected_pair = {(symbol, trade_date, SESSION_MODE) for symbol in PAIR}
    expected_keys = baseline_keys.market_days | expected_pair
    if candidate_keys.market_days != expected_keys:
        raise RuntimeError(
            "Pair candidate market keys mismatch: "
            f"missing={sorted(expected_keys - candidate_keys.market_days)} "
            f"extra={sorted(candidate_keys.market_days - expected_keys)}"
        )
    if candidate_keys.strategies != baseline_keys.strategies:
        raise RuntimeError("Pair candidate changed strategy keys")
    if candidate_keys.teaching_assets != baseline_keys.teaching_assets:
        raise RuntimeError("Pair candidate changed teaching keys")
    for table in ("strategies", "teaching_assets"):
        if table_sha256(candidate, table) != table_sha256(baseline, table):
            raise RuntimeError(f"Pair candidate changed {table} values")

    pair_counts: dict[str, dict[str, int]] = {}
    with contextlib.closing(readonly_connect(candidate)) as connection:
        validate_exactly_one_active_dataset(connection)
        for key, expected_hashes in preserved_day_hashes.items():
            if day_sha256(connection, *key) != expected_hashes:
                raise RuntimeError(f"Pair candidate changed grandfathered day: {'|'.join(key)}")
        for symbol in PAIR:
            row = connection.execute(
                "SELECT market_days.id, market_datasets.provider FROM market_days "
                "JOIN market_datasets ON market_datasets.market_day_id=market_days.id "
                "AND market_datasets.state='active' "
                "WHERE market_days.ticker=? AND market_days.trade_date=? "
                "AND market_days.session_mode=?",
                (symbol, trade_date, SESSION_MODE),
            ).fetchone()
            if row is None or str(row["provider"]).lower() != provider:
                raise RuntimeError(f"{symbol} candidate provider/active-dataset gate failed")
            dataset = connection.execute(
                "SELECT dataset_id FROM market_datasets WHERE market_day_id=? AND state='active'",
                (int(row["id"]),),
            ).fetchone()[0]
            counts = {
                table: int(connection.execute(
                    f"SELECT COUNT(*) FROM {table} WHERE dataset_id=?", (dataset,)
                ).fetchone()[0])
                for table in ("bars_1m", "bars_5m")
            }
            if min(counts.values()) <= 0:
                raise RuntimeError(f"{symbol} candidate assemble gate failed: {counts}")
            pair_counts[symbol] = counts
    return {
        "market_days": len(candidate_keys.market_days),
        "pair_counts": pair_counts,
        "integrity": "ok",
        "foreign_key_failures": 0,
        "grandfathered_days_preserved": len(preserved_day_hashes),
    }


def _validate_promoted_pair(
    live: Path,
    baseline_market_keys: frozenset[tuple[str, str, str]],
    trade_date: str,
    provider: str,
) -> None:
    validate_sqlite(live)
    expected = baseline_market_keys | {(symbol, trade_date, SESSION_MODE) for symbol in PAIR}
    if runtime_keys(live).market_days != expected:
        raise RuntimeError("Promoted pair market-day key set changed after candidate validation")
    with contextlib.closing(readonly_connect(live)) as connection:
        validate_exactly_one_active_dataset(connection)
        providers = connection.execute(
            "SELECT market_days.ticker, market_datasets.provider FROM market_days "
            "JOIN market_datasets ON market_datasets.market_day_id=market_days.id "
            "AND market_datasets.state='active' "
            "WHERE market_days.trade_date=? AND market_days.session_mode=? "
            "AND market_days.ticker IN ('SPY', 'QQQ') ORDER BY market_days.ticker",
            (trade_date, SESSION_MODE),
        ).fetchall()
    if [(row[0], str(row[1]).lower()) for row in providers] != [
        ("QQQ", provider),
        ("SPY", provider),
    ]:
        raise RuntimeError(f"Promoted pair provider gate failed: {providers}")


def _prepare_seed_pair(
    payload_paths: Mapping[str, Path],
    accepted_root: Path,
    trade_date: str,
    nonce: str,
) -> list[dict[str, Any]]:
    directory = accepted_root / trade_date
    directory.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for symbol in PAIR:
        target = directory / f"{symbol}_{trade_date}.json"
        candidate = directory / f".{target.name}.pair-{nonce}.candidate"
        backup = directory / f".{target.name}.pair-{nonce}.backup"
        candidate.write_bytes(payload_paths[symbol].expanduser().resolve().read_bytes())
        fsync_file(candidate)
        existed = target.exists()
        if existed:
            shutil.copy2(target, backup)
            fsync_file(backup)
        records.append(
            {"symbol": symbol, "target": target, "candidate": candidate, "backup": backup, "existed": existed}
        )
    fsync_directory(directory)
    return records


def _commit_seed_pair(records: list[dict[str, Any]], replace_file: ReplaceFile) -> None:
    try:
        for record in records:
            replace_file(record["candidate"], record["target"])
            fsync_directory(record["target"].parent)
    except Exception:
        _rollback_seed_pair(records)
        raise


def _rollback_seed_pair(records: list[dict[str, Any]]) -> None:
    for record in reversed(records):
        target = record["target"]
        backup = record["backup"]
        if record["existed"]:
            if backup.exists():
                os.replace(backup, target)
        elif target.exists():
            target.unlink()
        if record["candidate"].exists():
            record["candidate"].unlink()
        fsync_directory(target.parent)


def _finalize_seed_pair(records: list[dict[str, Any]]) -> None:
    _cleanup_seed_artifacts(records)
    for parent in {record["target"].parent for record in records}:
        fsync_directory(parent)


def _cleanup_seed_artifacts(records: list[dict[str, Any]]) -> None:
    for record in records:
        for key in ("candidate", "backup"):
            path = record[key]
            if path.exists():
                path.unlink()


def run_pair_update(
    trade_date: str,
    provider: str,
    db_path: Path = DEFAULT_DB_PATH,
    accepted_seed_dir: Path = DEFAULT_ACCEPTED_SEED_DIR,
    repo_dir: Path = REPO_DIR,
    fetch_one: FetchOne = fetch_one_symbol,
    git_baseline: Mapping[str, Any] | None = None,
    **accept_kwargs: Any,
) -> dict[str, Any]:
    datetime.strptime(trade_date, "%Y-%m-%d")
    baseline = dict(git_baseline) if git_baseline is not None else capture_git_baseline(repo_dir)
    pre_fetch_db_token = capture_database_token(db_path)
    with tempfile.TemporaryDirectory(prefix="tang-spy-qqq-pair-") as raw_staging:
        staging = Path(raw_staging)
        payload_paths = stage_provider_pair(trade_date, staging, provider, fetch_one)
        return accept_staged_pair(
            payload_paths,
            trade_date,
            provider,
            db_path,
            accepted_seed_dir,
            baseline,
            expected_db_token=pre_fetch_db_token,
            **accept_kwargs,
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stage and atomically accept one same-provider SPY/QQQ market-day pair."
    )
    parser.add_argument("date", nargs="?", help="Completed NYSE trade date, YYYY-MM-DD.")
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default="tradingview")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--accepted-seed-dir", type=Path, default=DEFAULT_ACCEPTED_SEED_DIR)
    parser.add_argument("--repo-dir", type=Path, default=REPO_DIR)
    parser.add_argument(
        "--staged-payload-dir",
        type=Path,
        help="Offline/test-only directory containing <date>/SPY_<date>.json and QQQ_<date>.json.",
    )
    args = parser.parse_args(argv)
    trade_date = args.date or resolve_latest_completed_nyse_session()
    try:
        baseline = capture_git_baseline(args.repo_dir)
        if args.staged_payload_dir is None:
            result = run_pair_update(
                trade_date,
                args.provider,
                db_path=args.db_path,
                accepted_seed_dir=args.accepted_seed_dir,
                repo_dir=args.repo_dir,
                git_baseline=baseline,
            )
        else:
            if args.db_path.expanduser().resolve() == DEFAULT_DB_PATH.resolve():
                raise RuntimeError(
                    "--staged-payload-dir is offline/test-only and cannot target the tracked DB; "
                    "pass an explicit temporary --db-path"
                )
            if args.accepted_seed_dir.expanduser().resolve() == DEFAULT_ACCEPTED_SEED_DIR.resolve():
                raise RuntimeError(
                    "--staged-payload-dir is offline/test-only and cannot target accepted seeds; "
                    "pass an explicit temporary --accepted-seed-dir"
                )
            root = args.staged_payload_dir.expanduser().resolve()
            paths = {symbol: root / trade_date / f"{symbol}_{trade_date}.json" for symbol in PAIR}
            result = accept_staged_pair(
                paths,
                trade_date,
                args.provider,
                args.db_path,
                args.accepted_seed_dir,
                baseline,
            )
    except Exception as exc:
        print(f"SPY/QQQ pair update refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
