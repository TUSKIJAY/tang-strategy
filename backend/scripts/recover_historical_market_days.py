from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import secrets
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.services.db_safety import (
    BAR_COLUMNS,
    MARKET_DAY_COLUMNS,
    DatabaseToken,
    bar_owner,
    bars_use_datasets,
    create_consistent_snapshot,
    day_sha256,
    file_sha256,
    promote_candidate,
    readonly_connect,
    table_sha256,
    validate_sqlite,
)
from app.settings import settings


REPO_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_DIR / "backend"
SENSITIVE_KEY_PARTS = ("credential", "password", "secret", "token", "api_key", "apikey")
PROVENANCE_META_KEYS = (
    "ticker",
    "date",
    "provider",
    "source",
    "generated_at",
    "session_mode",
    "session_type",
    "session_window",
    "counts",
    "gap_count",
    "missing_minutes",
    "vwap_mode",
    "vwap_session_anchor",
    "vwap_source",
    "warmup_complete",
    "ib_contract",
    "ib_request",
    "quality",
)


@dataclass(frozen=True)
class SourceSpec:
    ticker: str
    trade_date: str
    session_mode: str
    db_path: Path

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.ticker, self.trade_date, self.session_mode)

    @property
    def label(self) -> str:
        return "|".join(self.key)


def parse_source(raw: str) -> SourceSpec:
    try:
        raw_key, raw_path = raw.split("=", 1)
        ticker, trade_date, session_mode = raw_key.split("|", 2)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "source must be TICKER|YYYY-MM-DD|SESSION=/absolute/source.db"
        ) from exc
    path = Path(raw_path).expanduser().resolve()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"historical DB not found: {path}")
    return SourceSpec(ticker.upper(), trade_date, session_mode, path)


def market_day_keys(db_path: Path) -> list[tuple[str, str, str]]:
    with contextlib.closing(readonly_connect(db_path)) as connection:
        return [
            (str(row[0]), str(row[1]), str(row[2]))
            for row in connection.execute(
                "SELECT ticker, trade_date, session_mode FROM market_days "
                "ORDER BY ticker, trade_date, session_mode"
            ).fetchall()
        ]


def all_day_hashes(db_path: Path) -> dict[str, dict[str, str]]:
    hashes: dict[str, dict[str, str]] = {}
    with contextlib.closing(readonly_connect(db_path)) as connection:
        for ticker, trade_date, session_mode in market_day_keys(db_path):
            label = f"{ticker}|{trade_date}|{session_mode}"
            hashes[label] = day_sha256(connection, ticker, trade_date, session_mode)
    return hashes


def mapping_sha256(mapping: dict[str, Any]) -> str:
    payload = json.dumps(
        mapping,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def copy_market_day(candidate_path: Path, source: SourceSpec) -> dict[str, Any]:
    with contextlib.closing(readonly_connect(source.db_path)) as source_connection:
        source_day = source_connection.execute(
            "SELECT * FROM market_days WHERE ticker=? AND trade_date=? AND session_mode=?",
            source.key,
        ).fetchone()
        if source_day is None:
            raise RuntimeError(f"Historical source is missing {source.label}: {source.db_path}")
        source_id = int(source_day["id"])
        source_ticker = source_connection.execute(
            "SELECT id, symbol, name, asset_type, enabled FROM tickers WHERE symbol=?",
            (source.ticker,),
        ).fetchone()
        if source_ticker is None:
            raise RuntimeError(f"Historical source has no ticker row for {source.ticker}: {source.db_path}")
        bars: dict[str, list[sqlite3.Row]] = {}
        source_owner_column, source_owner_id = bar_owner(source_connection, source_id)
        source_dataset = None
        if source_owner_column == "dataset_id":
            dataset_row = source_connection.execute(
                "SELECT * FROM market_datasets WHERE dataset_id=?",
                (source_owner_id,),
            ).fetchone()
            source_dataset = dict(dataset_row) if dataset_row is not None else None
        for table, declared_column in (("bars_1m", "bar_count_1m"), ("bars_5m", "bar_count_5m")):
            rows = source_connection.execute(
                f"SELECT {', '.join(BAR_COLUMNS)} FROM {table} "
                f"WHERE {source_owner_column}=? ORDER BY idx",
                (source_owner_id,),
            ).fetchall()
            declared = int(source_day[declared_column])
            if not rows or len(rows) != declared:
                raise RuntimeError(
                    f"Historical {source.label} {table} count mismatch: "
                    f"declared={declared} actual={len(rows)}"
                )
            bars[table] = rows
        source_hash = day_sha256(source_connection, *source.key)

    candidate_connection = sqlite3.connect(candidate_path)
    candidate_connection.row_factory = sqlite3.Row
    candidate_connection.execute("PRAGMA foreign_keys = ON")
    try:
        with candidate_connection:
            duplicate = candidate_connection.execute(
                "SELECT id FROM market_days WHERE ticker=? AND trade_date=? AND session_mode=?",
                source.key,
            ).fetchone()
            if duplicate is not None:
                raise RuntimeError(f"Candidate already contains target day {source.label}")
            candidate_connection.execute(
                "INSERT OR IGNORE INTO tickers(symbol, name, asset_type, enabled) VALUES (?, ?, ?, ?)",
                (
                    source_ticker["symbol"],
                    source_ticker["name"],
                    source_ticker["asset_type"],
                    source_ticker["enabled"],
                ),
            )
            market_values = [source_day[column] for column in MARKET_DAY_COLUMNS]
            candidate_connection.execute(
                f"INSERT INTO market_days({', '.join(MARKET_DAY_COLUMNS)}) "
                f"VALUES ({', '.join('?' for _ in MARKET_DAY_COLUMNS)})",
                market_values,
            )
            candidate_id = int(candidate_connection.execute(
                "SELECT id FROM market_days WHERE ticker=? AND trade_date=? AND session_mode=?",
                source.key,
            ).fetchone()[0])
            candidate_owner_column, candidate_owner_id = _recovery_bar_owner(
                candidate_connection,
                candidate_id,
                source_day,
                source_hash,
                source_dataset,
            )
            placeholders = ", ".join("?" for _ in BAR_COLUMNS)
            for table in ("bars_1m", "bars_5m"):
                candidate_connection.executemany(
                    f"INSERT INTO {table}({candidate_owner_column}, {', '.join(BAR_COLUMNS)}) "
                    f"VALUES (?, {placeholders})",
                    [(candidate_owner_id, *(row[column] for column in BAR_COLUMNS)) for row in bars[table]],
                )
    finally:
        candidate_connection.close()

    with contextlib.closing(readonly_connect(candidate_path)) as candidate_ro:
        candidate_hash = day_sha256(candidate_ro, *source.key)
        candidate_ticker_id = int(candidate_ro.execute(
            "SELECT id FROM tickers WHERE symbol=?", (source.ticker,)
        ).fetchone()[0])
    if source_hash != candidate_hash:
        raise RuntimeError(
            f"Normalized hash mismatch after copying {source.label}: "
            f"source={source_hash} candidate={candidate_hash}"
        )
    return {
        "key": source.label,
        "source_db": str(source.db_path),
        "source_market_day_id": source_id,
        "candidate_market_day_id": candidate_id,
        "source_ticker_id": int(source_ticker["id"]),
        "candidate_ticker_id": candidate_ticker_id,
        "bars_1m": len(bars["bars_1m"]),
        "bars_5m": len(bars["bars_5m"]),
        "normalized_hashes": candidate_hash,
        "summary": summarize_day(source.db_path, source),
    }


def summarize_day(db_path: Path, source: SourceSpec) -> dict[str, Any]:
    with contextlib.closing(readonly_connect(db_path)) as connection:
        day = connection.execute(
            "SELECT * FROM market_days WHERE ticker=? AND trade_date=? AND session_mode=?",
            source.key,
        ).fetchone()
        if day is None:
            raise RuntimeError(f"Missing day while summarizing {source.label}")
        raw_metadata = json.loads(day["meta_json"] or "{}")
        safe_metadata = {
            key: redact_sensitive(raw_metadata[key])
            for key in PROVENANCE_META_KEYS
            if key in raw_metadata
        }
        result: dict[str, Any] = {
            "market_day_id": int(day["id"]),
            "source": day["source"],
            "title": day["title"],
            "declared_bars_1m": int(day["bar_count_1m"]),
            "declared_bars_5m": int(day["bar_count_5m"]),
            "imported_at": day["imported_at"],
            "metadata": safe_metadata,
        }
        for table in ("bars_1m", "bars_5m"):
            owner_column, owner_id = bar_owner(connection, int(day["id"]))
            first = connection.execute(
                f"SELECT idx, ts, time, open, vwap FROM {table} "
                f"WHERE {owner_column}=? ORDER BY idx LIMIT 1",
                (owner_id,),
            ).fetchone()
            last = connection.execute(
                f"SELECT idx, ts, time, close, vwap FROM {table} "
                f"WHERE {owner_column}=? ORDER BY idx DESC LIMIT 1",
                (owner_id,),
            ).fetchone()
            aggregate = connection.execute(
                f"SELECT COUNT(*), MIN(low), MAX(high), SUM(volume), MIN(vwap), MAX(vwap) "
                f"FROM {table} WHERE {owner_column}=?",
                (owner_id,),
            ).fetchone()
            result[table] = {
                "count": int(aggregate[0]),
                "first": dict(first) if first is not None else None,
                "last": dict(last) if last is not None else None,
                "low_min": aggregate[1],
                "high_max": aggregate[2],
                "volume_sum": aggregate[3],
                "vwap_min": aggregate[4],
                "vwap_max": aggregate[5],
            }
        return result


def _recovery_bar_owner(
    candidate_connection: sqlite3.Connection,
    candidate_market_day_id: int,
    source_day: sqlite3.Row,
    source_hash: dict[str, str],
    source_dataset: dict[str, Any] | None,
) -> tuple[str, int | str]:
    if not bars_use_datasets(candidate_connection):
        return "market_day_id", candidate_market_day_id
    checksum = hashlib.sha256(
        f"{source_hash['bars_1m']}\n{source_hash['bars_5m']}".encode("utf-8")
    ).hexdigest()
    safe_session = "".join(
        character if character.isalnum() else "_"
        for character in str(source_day["session_mode"]).lower()
    )
    dataset_id = (
        str(source_dataset["dataset_id"])
        if source_dataset is not None
        else f"mds_{str(source_day['ticker']).lower()}_"
        f"{str(source_day['trade_date']).replace('-', '')}_{safe_session}_recovery"
    )
    candidate_connection.execute(
        "INSERT INTO market_datasets(dataset_id, market_day_id, provider, venue, "
        "source_revision, fetcher_revision, imported_at, checksum, quality_json, state) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')",
        (
            dataset_id,
            candidate_market_day_id,
            source_dataset["provider"] if source_dataset is not None else str(source_day["source"] or "historical_recovery"),
            source_dataset["venue"] if source_dataset is not None else None,
            source_dataset["source_revision"] if source_dataset is not None else None,
            source_dataset["fetcher_revision"] if source_dataset is not None else None,
            source_dataset["imported_at"] if source_dataset is not None else source_day["imported_at"],
            source_dataset["checksum"] if source_dataset is not None else checksum,
            source_dataset["quality_json"] if source_dataset is not None else "{}",
        ),
    )
    return "dataset_id", dataset_id


def redact_sensitive(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower()
            redacted[str(key)] = (
                "[redacted]"
                if any(part in normalized for part in SENSITIVE_KEY_PARTS)
                else redact_sensitive(item)
            )
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value


def verify_candidate(
    candidate_path: Path,
    baseline_hashes: dict[str, dict[str, str]],
    sources: list[SourceSpec],
    expected_before: int,
    expected_after: int,
    baseline_strategy_hash: str,
    baseline_teaching_hash: str,
) -> dict[str, Any]:
    validate_sqlite(candidate_path)
    candidate_hashes = all_day_hashes(candidate_path)
    candidate_keys = market_day_keys(candidate_path)
    if len(baseline_hashes) != expected_before:
        raise RuntimeError(
            f"Baseline day count mismatch: expected={expected_before} actual={len(baseline_hashes)}"
        )
    if len(candidate_keys) != expected_after:
        raise RuntimeError(
            f"Candidate day count mismatch: expected={expected_after} actual={len(candidate_keys)}"
        )
    mismatches = {
        key: {"baseline": digest, "candidate": candidate_hashes.get(key)}
        for key, digest in baseline_hashes.items()
        if candidate_hashes.get(key) != digest
    }
    if mismatches:
        raise RuntimeError(f"Existing day hashes changed in candidate: {mismatches}")
    target_labels = {source.label for source in sources}
    added_labels = set(candidate_hashes) - set(baseline_hashes)
    if added_labels != target_labels:
        raise RuntimeError(
            f"Candidate added the wrong logical days: expected={sorted(target_labels)} "
            f"actual={sorted(added_labels)}"
        )
    candidate_strategy_hash = table_sha256(candidate_path, "strategies")
    candidate_teaching_hash = table_sha256(candidate_path, "teaching_assets")
    if candidate_strategy_hash != baseline_strategy_hash:
        raise RuntimeError("Candidate changed strategies while recovering market days")
    if candidate_teaching_hash != baseline_teaching_hash:
        raise RuntimeError("Candidate changed teaching assets while recovering market days")
    runtime = verify_runtime_paths(candidate_path, sources)
    return {
        "market_days_before": expected_before,
        "market_days_after": len(candidate_keys),
        "original_day_hash_map_sha256_before": mapping_sha256(baseline_hashes),
        "original_day_hash_map_sha256_candidate": mapping_sha256(
            {key: candidate_hashes[key] for key in sorted(baseline_hashes)}
        ),
        "original_day_hash_mismatches": mismatches,
        "added_days": sorted(added_labels),
        "strategies_sha256_before": baseline_strategy_hash,
        "strategies_sha256_candidate": candidate_strategy_hash,
        "teaching_sha256_before": baseline_teaching_hash,
        "teaching_sha256_candidate": candidate_teaching_hash,
        "integrity_check": "ok",
        "foreign_key_check_rows": 0,
        "runtime": runtime,
    }


def verify_runtime_paths(candidate_path: Path, sources: list[SourceSpec]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="tang-recovery-runtime-") as raw_directory:
        runtime_directory = Path(raw_directory)
        output_directory = runtime_directory / "reviews"
        environment = os.environ.copy()
        environment.update({
            "PYTHONPATH": ".",
            "TANG_DB_PATH": str(candidate_path),
        })
        regression_code = """
import json

from app.db import connect
from app.main import assemble_review

connection = connect()
try:
    day = connection.execute(
        "SELECT id FROM market_days "
        "WHERE ticker='SPY' AND trade_date='2026-07-17' AND session_mode='extended'"
    ).fetchone()
    strategy = connection.execute(
        "SELECT id, slug FROM strategies WHERE active=1 AND slug='tang-v4-4-slope-4-4'"
    ).fetchone()
finally:
    connection.close()

payload = assemble_review(int(day["id"]), int(strategy["id"]), "readonly")
print(json.dumps({
    "day_id": day["id"],
    "strategy_id": strategy["id"],
    "strategy_slug": strategy["slug"],
    "bars_1m": len(payload["bars_1m"]),
    "bars_5m": len(payload["bars_5m"]),
}, sort_keys=True))
"""
        regression = subprocess.run(
            [
                sys.executable,
                "-c",
                regression_code,
            ],
            cwd=BACKEND_DIR,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if regression.returncode != 0:
            raise RuntimeError(
                "Candidate 2026-07-17 assemble regression failed: "
                f"stdout={regression.stdout!r} stderr={regression.stderr!r}"
            )
        regression_summary = json.loads(regression.stdout.strip().splitlines()[-1])
        if regression_summary["bars_1m"] <= 0 or regression_summary["bars_5m"] <= 0:
            raise RuntimeError(f"2026-07-17 assemble returned empty bars: {regression_summary}")

        export = subprocess.run(
            [
                sys.executable,
                "scripts/export_static_reviews.py",
                "--output",
                str(output_directory),
                "--limit",
                "250",
                "--ticker",
                "SPY",
                "--strategy-families",
                "v3,v4,v5",
            ],
            cwd=BACKEND_DIR,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if export.returncode != 0:
            raise RuntimeError(
                "Candidate static export failed: "
                f"stdout={export.stdout!r} stderr={export.stderr!r}"
            )
        overlays: dict[str, Any] = {}
        for source in sources:
            if source.trade_date not in {"2026-06-30", "2026-07-01"}:
                continue
            payload_path = output_directory / "days" / f"spy-{source.trade_date}-{source.session_mode}.json"
            payload = json.loads(payload_path.read_text(encoding="utf-8"))
            tang_trades = payload.get("tang_trades") or {}
            if not tang_trades.get("trades") and not tang_trades.get("notes"):
                raise RuntimeError(f"Tang overlay is empty after export for {source.trade_date}")
            overlays[source.trade_date] = {
                "payload": str(payload_path.relative_to(output_directory)),
                "trades": len(tang_trades.get("trades") or []),
                "notes": len(tang_trades.get("notes") or []),
            }
        return {
            "assemble_2026-07-17": regression_summary,
            "export_stdout": export.stdout.strip(),
            "tang_overlays": overlays,
        }


def verify_promoted_db(
    live_path: Path,
    expected_after: int,
    target_labels: set[str],
    baseline_hashes: dict[str, dict[str, str]],
) -> None:
    validate_sqlite(live_path)
    hashes = all_day_hashes(live_path)
    if len(hashes) != expected_after:
        raise RuntimeError(f"Promoted DB day count mismatch: {len(hashes)}")
    if not target_labels.issubset(hashes):
        raise RuntimeError(f"Promoted DB is missing recovered days: {sorted(target_labels - set(hashes))}")
    for key, digest in baseline_hashes.items():
        if hashes.get(key) != digest:
            raise RuntimeError(f"Promoted DB changed original day: {key}")


def build_recovery(
    target_db: Path,
    sources: list[SourceSpec],
    expected_before: int,
    expected_after: int,
    promote: bool,
) -> dict[str, Any]:
    target = target_db.expanduser().resolve()
    nonce = secrets.token_hex(6)
    backup = target.parent / f".{target.stem}.recovery-{nonce}.backup.db"
    candidate = target.parent / f".{target.stem}.recovery-{nonce}.candidate.db"
    baseline_token: DatabaseToken | None = None
    promoted = False
    try:
        baseline_token = create_consistent_snapshot(target, backup)
        shutil.copy2(backup, candidate)
        baseline_hashes = all_day_hashes(backup)
        baseline_strategy_hash = table_sha256(backup, "strategies")
        baseline_teaching_hash = table_sha256(backup, "teaching_assets")
        recovered = [copy_market_day(candidate, source) for source in sources]
        validation = verify_candidate(
            candidate,
            baseline_hashes,
            sources,
            expected_before,
            expected_after,
            baseline_strategy_hash,
            baseline_teaching_hash,
        )
        candidate_sha256 = file_sha256(candidate)
        if promote:
            promote_candidate(
                target,
                candidate,
                baseline_token,
                backup,
                lambda path: verify_promoted_db(
                    path,
                    expected_after,
                    {source.label for source in sources},
                    baseline_hashes,
                ),
            )
            promoted = True
        result = {
            "schema_version": "tang-market-day-recovery-evidence-v1",
            "target_db": str(target),
            "promoted": promoted,
            "baseline_token": baseline_token.as_dict(),
            "baseline_backup_sha256": file_sha256(backup) if backup.exists() else None,
            "candidate_sha256_before_promotion": candidate_sha256,
            "recovered": recovered,
            "validation": validation,
            "post_promotion": (
                {
                    "db_sha256": file_sha256(target),
                    "market_days": len(market_day_keys(target)),
                    "integrity_check": "ok",
                    "foreign_key_check_rows": 0,
                }
                if promoted
                else None
            ),
            "pages_publish_occurred": False,
        }
        return result
    finally:
        if candidate.exists() and not promoted:
            candidate.unlink()
        if backup.exists():
            backup.unlink()
        candidate_lock = Path(f"{candidate}.write.lock")
        backup_lock = Path(f"{backup}.write.lock")
        if candidate_lock.exists():
            candidate_lock.unlink()
        if backup_lock.exists():
            backup_lock.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Recover selected logical market days from historical SQLite DBs via a verified candidate."
    )
    parser.add_argument("--target-db", type=Path, default=settings.db_path)
    parser.add_argument("--source", action="append", type=parse_source, required=True)
    parser.add_argument("--expected-before", type=int, required=True)
    parser.add_argument("--expected-after", type=int, required=True)
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--evidence-json", type=Path)
    args = parser.parse_args(argv)

    sources: list[SourceSpec] = args.source
    labels = [source.label for source in sources]
    if len(labels) != len(set(labels)):
        parser.error(f"duplicate recovery source logical key: {labels}")
    evidence = build_recovery(
        args.target_db,
        sources,
        args.expected_before,
        args.expected_after,
        args.promote,
    )
    output = json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True)
    if args.evidence_json:
        destination = args.evidence_json.expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
