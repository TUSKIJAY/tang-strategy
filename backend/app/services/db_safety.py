from __future__ import annotations

import contextlib
import fcntl
import hashlib
import json
import math
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Iterator, Sequence


MARKET_DAY_COLUMNS = (
    "ticker",
    "trade_date",
    "session_mode",
    "source",
    "title",
    "bar_count_1m",
    "bar_count_5m",
    "imported_at",
    "meta_json",
)

BAR_COLUMNS = (
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
)

STRATEGY_COLUMNS = (
    "id",
    "name",
    "version",
    "slug",
    "description",
    "source_type",
    "json_body",
    "active",
    "created_at",
    "updated_at",
)

TEACHING_COLUMNS = (
    "id",
    "asset_type",
    "version",
    "slug",
    "json_body",
    "updated_at",
)


@dataclass(frozen=True)
class DatabaseToken:
    device: int
    inode: int
    size: int
    mtime_ns: int
    byte_sha256: str
    logical_sha256: str

    def as_dict(self) -> dict[str, int | str]:
        return asdict(self)


@contextlib.contextmanager
def db_write_lock(db_path: Path, timeout_seconds: float = 30.0) -> Iterator[Path]:
    """Serialize repository-managed writes and DB promotion for one DB path."""

    resolved = db_path.expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    lock_path = Path(f"{resolved}.write.lock")
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for DB write lock: {lock_path}")
                time.sleep(0.05)
        yield lock_path
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def readonly_connect(db_path: Path) -> sqlite3.Connection:
    resolved = db_path.expanduser().resolve()
    connection = sqlite3.connect(f"{resolved.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_consistent_snapshot(source_path: Path, snapshot_path: Path) -> DatabaseToken:
    """Create a SQLite-consistent snapshot and return the locked source token."""

    source = source_path.expanduser().resolve()
    snapshot = snapshot_path.expanduser().resolve()
    if snapshot.exists():
        raise FileExistsError(f"Snapshot path already exists: {snapshot}")
    if source.parent != snapshot.parent:
        raise ValueError("Snapshot must be adjacent to the source DB")

    with db_write_lock(source):
        _checkpoint_and_require_quiescent(source)
        with contextlib.closing(readonly_connect(source)) as source_connection:
            snapshot_connection = sqlite3.connect(snapshot)
            try:
                source_connection.backup(snapshot_connection)
                snapshot_connection.commit()
            finally:
                snapshot_connection.close()
        fsync_file(snapshot)
        validate_sqlite(snapshot)
        return capture_database_token(source)


def capture_database_token(db_path: Path) -> DatabaseToken:
    resolved = db_path.expanduser().resolve()
    require_no_sidecars(resolved)
    before = resolved.stat()
    byte_sha256 = file_sha256(resolved)
    logical_sha256 = logical_database_sha256(resolved)
    after = resolved.stat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity:
        raise RuntimeError(f"DB changed while capturing token: {resolved}")
    return DatabaseToken(
        device=after.st_dev,
        inode=after.st_ino,
        size=after.st_size,
        mtime_ns=after.st_mtime_ns,
        byte_sha256=byte_sha256,
        logical_sha256=logical_sha256,
    )


def promote_candidate(
    live_path: Path,
    candidate_path: Path,
    baseline_token: DatabaseToken,
    backup_path: Path,
    post_validate: Callable[[Path], None],
) -> None:
    """Compare-and-swap a verified candidate while preserving a verified backup."""

    live = live_path.expanduser().resolve()
    candidate = candidate_path.expanduser().resolve()
    backup = backup_path.expanduser().resolve()
    if live.parent != candidate.parent or live.parent != backup.parent:
        raise ValueError("Live DB, candidate, and backup must be on the same adjacent filesystem")
    if not candidate.is_file() or not backup.is_file():
        raise FileNotFoundError("Candidate and verified backup must both exist before promotion")

    validate_sqlite(candidate)
    validate_sqlite(backup)
    require_no_sidecars(candidate)
    require_no_sidecars(backup)
    fsync_file(candidate)
    fsync_file(backup)

    with db_write_lock(live):
        _checkpoint_and_require_quiescent(live)
        current_token = capture_database_token(live)
        if current_token != baseline_token:
            raise RuntimeError(
                "Refusing DB promotion: live DB drifted after the candidate snapshot "
                f"(baseline={baseline_token.as_dict()}, current={current_token.as_dict()})"
            )
        current_stat = live.stat()
        current_identity = (
            current_stat.st_dev,
            current_stat.st_ino,
            current_stat.st_size,
            current_stat.st_mtime_ns,
        )
        expected_identity = (
            baseline_token.device,
            baseline_token.inode,
            baseline_token.size,
            baseline_token.mtime_ns,
        )
        if current_identity != expected_identity:
            raise RuntimeError("Refusing DB promotion: live DB identity changed before os.replace")

        os.replace(candidate, live)
        fsync_directory(live.parent)
        try:
            post_validate(live)
        except Exception:
            os.replace(backup, live)
            fsync_directory(live.parent)
            raise


def validate_sqlite(db_path: Path) -> None:
    with contextlib.closing(readonly_connect(db_path)) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if [row[0] for row in integrity] != ["ok"]:
            raise RuntimeError(f"SQLite integrity_check failed for {db_path}: {integrity}")
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise RuntimeError(f"SQLite foreign_key_check failed for {db_path}: {foreign_keys}")


def day_sha256(
    connection: sqlite3.Connection,
    ticker: str,
    trade_date: str,
    session_mode: str,
) -> dict[str, str]:
    row = connection.execute(
        f"SELECT {', '.join(MARKET_DAY_COLUMNS)} FROM market_days "
        "WHERE ticker=? AND trade_date=? AND session_mode=?",
        (ticker, trade_date, session_mode),
    ).fetchone()
    if row is None:
        raise KeyError(f"Market day not found: {ticker} {trade_date} {session_mode}")
    market_day_id_row = connection.execute(
        "SELECT id FROM market_days WHERE ticker=? AND trade_date=? AND session_mode=?",
        (ticker, trade_date, session_mode),
    ).fetchone()
    market_day_id = int(market_day_id_row[0])
    return {
        "market_day": rows_sha256([row]),
        "bars_1m": _bars_sha256(connection, "bars_1m", market_day_id),
        "bars_5m": _bars_sha256(connection, "bars_5m", market_day_id),
    }


def logical_database_sha256(db_path: Path) -> str:
    digest = hashlib.sha256()
    with contextlib.closing(readonly_connect(db_path)) as connection:
        days = connection.execute(
            "SELECT id, ticker, trade_date, session_mode, "
            f"{', '.join(MARKET_DAY_COLUMNS[3:])} FROM market_days "
            "ORDER BY ticker, trade_date, session_mode"
        ).fetchall()
        _update_digest(digest, "market_days", ([row[column] for column in MARKET_DAY_COLUMNS] for row in days))
        for day in days:
            key = [day["ticker"], day["trade_date"], day["session_mode"]]
            _update_digest(digest, "day-key", [key])
            _update_digest(
                digest,
                "bars_1m",
                _bar_values(connection, "bars_1m", int(day["id"])),
            )
            _update_digest(
                digest,
                "bars_5m",
                _bar_values(connection, "bars_5m", int(day["id"])),
            )
        strategy_rows = connection.execute(
            f"SELECT {', '.join(STRATEGY_COLUMNS)} FROM strategies ORDER BY id"
        ).fetchall()
        _update_digest(
            digest,
            "strategies",
            ([row[column] for column in STRATEGY_COLUMNS] for row in strategy_rows),
        )
        teaching_rows = connection.execute(
            f"SELECT {', '.join(TEACHING_COLUMNS)} FROM teaching_assets ORDER BY id"
        ).fetchall()
        _update_digest(
            digest,
            "teaching_assets",
            ([row[column] for column in TEACHING_COLUMNS] for row in teaching_rows),
        )
    return digest.hexdigest()


def table_sha256(db_path: Path, table: str) -> str:
    if table not in {"strategies", "teaching_assets"}:
        raise ValueError(f"Unsupported normalized table: {table}")
    columns = STRATEGY_COLUMNS if table == "strategies" else TEACHING_COLUMNS
    with contextlib.closing(readonly_connect(db_path)) as connection:
        rows = connection.execute(
            f"SELECT {', '.join(columns)} FROM {table} ORDER BY id"
        ).fetchall()
        return rows_sha256([tuple(row[column] for column in columns) for row in rows])


def rows_sha256(rows: Iterable[Sequence[object]]) -> str:
    digest = hashlib.sha256()
    _update_digest(digest, "rows", rows)
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def require_no_sidecars(db_path: Path) -> None:
    found = [str(path) for path in sqlite_sidecars(db_path) if path.exists()]
    if found:
        raise RuntimeError(f"Unresolved SQLite sidecars for {db_path}: {found}")


def sqlite_sidecars(db_path: Path) -> tuple[Path, Path, Path]:
    resolved = db_path.expanduser().resolve()
    return (
        Path(f"{resolved}-journal"),
        Path(f"{resolved}-wal"),
        Path(f"{resolved}-shm"),
    )


def fsync_file(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _checkpoint_and_require_quiescent(db_path: Path) -> None:
    connection = sqlite3.connect(db_path)
    try:
        journal_mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0]).lower()
        if journal_mode == "wal":
            busy, log_frames, checkpointed = connection.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            if busy or log_frames != checkpointed:
                raise RuntimeError(
                    f"Unable to checkpoint WAL for {db_path}: "
                    f"busy={busy} log_frames={log_frames} checkpointed={checkpointed}"
                )
    finally:
        connection.close()
    require_no_sidecars(db_path)


def _bars_sha256(connection: sqlite3.Connection, table: str, market_day_id: int) -> str:
    return rows_sha256(_bar_values(connection, table, market_day_id))


def _bar_values(
    connection: sqlite3.Connection,
    table: str,
    market_day_id: int,
) -> Iterable[list[object]]:
    if table not in {"bars_1m", "bars_5m"}:
        raise ValueError(f"Unsupported bars table: {table}")
    rows = connection.execute(
        f"SELECT {', '.join(BAR_COLUMNS)} FROM {table} WHERE market_day_id=? ORDER BY idx",
        (market_day_id,),
    )
    for row in rows:
        yield [row[column] for column in BAR_COLUMNS]


def _update_digest(
    digest: "hashlib._Hash",
    label: str,
    rows: Iterable[Sequence[object]],
) -> None:
    digest.update(label.encode("utf-8"))
    digest.update(b"\n")
    for row in rows:
        values = [_canonical_value(value) for value in row]
        digest.update(
            json.dumps(
                values,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        digest.update(b"\n")


def _canonical_value(value: object) -> object:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"Non-finite SQLite REAL cannot be hashed canonically: {value}")
    return value
