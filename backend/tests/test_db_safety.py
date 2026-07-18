from __future__ import annotations

import contextlib
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.db import SCHEMA
from app.services.db_safety import (
    BAR_COLUMNS,
    capture_database_token,
    create_consistent_snapshot,
    day_sha256,
    promote_candidate,
    readonly_connect,
    validate_sqlite,
)


class DatabaseSafetyTests(unittest.TestCase):
    def test_consistent_snapshot_and_atomic_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            live = directory / "live.db"
            backup = directory / "backup.db"
            candidate = directory / "candidate.db"
            self._create_db(live, ["2026-07-17"])

            baseline = create_consistent_snapshot(live, backup)
            shutil.copy2(backup, candidate)
            self._insert_day(candidate, "2026-07-18")

            promote_candidate(
                live,
                candidate,
                baseline,
                backup,
                lambda path: self._assert_dates(path, ["2026-07-17", "2026-07-18"]),
            )

            self._assert_dates(live, ["2026-07-17", "2026-07-18"])
            self.assertFalse(candidate.exists())
            self.assertTrue(backup.exists())

    def test_promotion_rejects_source_drift_and_preserves_new_write(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            live = directory / "live.db"
            backup = directory / "backup.db"
            candidate = directory / "candidate.db"
            self._create_db(live, ["2026-07-17"])

            baseline = create_consistent_snapshot(live, backup)
            shutil.copy2(backup, candidate)
            self._insert_day(candidate, "2026-07-18")
            self._insert_day(live, "2026-07-19")

            with self.assertRaisesRegex(RuntimeError, "live DB drifted"):
                promote_candidate(live, candidate, baseline, backup, validate_sqlite)

            self._assert_dates(live, ["2026-07-17", "2026-07-19"])
            self.assertTrue(candidate.exists())
            self.assertTrue(backup.exists())

    def test_day_hash_excludes_database_local_ids(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            first = directory / "first.db"
            second = directory / "second.db"
            self._create_db(first, ["2026-07-17"])
            self._create_db(second, [])
            self._insert_day(second, "2026-07-16")
            with contextlib.closing(sqlite3.connect(second)) as connection, connection:
                day_id = connection.execute(
                    "SELECT id FROM market_days WHERE trade_date='2026-07-16'"
                ).fetchone()[0]
                connection.execute("DELETE FROM market_days WHERE id=?", (day_id,))
            self._insert_day(second, "2026-07-17")

            with contextlib.closing(readonly_connect(first)) as first_connection:
                first_digest = day_sha256(first_connection, "SPY", "2026-07-17", "extended")
            with contextlib.closing(readonly_connect(second)) as second_connection:
                second_digest = day_sha256(second_connection, "SPY", "2026-07-17", "extended")

            self.assertEqual(first_digest, second_digest)

    def test_post_validation_failure_restores_verified_backup(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            live = directory / "live.db"
            backup = directory / "backup.db"
            candidate = directory / "candidate.db"
            self._create_db(live, ["2026-07-17"])
            baseline = create_consistent_snapshot(live, backup)
            shutil.copy2(backup, candidate)
            self._insert_day(candidate, "2026-07-18")

            def fail_validation(_: Path) -> None:
                raise RuntimeError("forced post-validation failure")

            with self.assertRaisesRegex(RuntimeError, "forced post-validation failure"):
                promote_candidate(live, candidate, baseline, backup, fail_validation)

            self._assert_dates(live, ["2026-07-17"])
            self.assertFalse(backup.exists())

    def _create_db(self, path: Path, dates: list[str]) -> None:
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.executescript(SCHEMA)
            connection.execute(
                "INSERT INTO strategies(name, version, slug, description, json_body, active) "
                "VALUES ('Test', '1', 'test-1', '', '{}', 1)"
            )
            connection.execute(
                "INSERT INTO teaching_assets(asset_type, version, slug, json_body) "
                "VALUES ('rules', 'default', 'compiled-index', '{}')"
            )
        for trade_date in dates:
            self._insert_day(path, trade_date)

    def _insert_day(self, path: Path, trade_date: str) -> None:
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                "INSERT OR IGNORE INTO tickers(symbol, name) VALUES ('SPY', 'SPY')"
            )
            connection.execute(
                "INSERT INTO market_days("
                "ticker, trade_date, session_mode, source, title, "
                "bar_count_1m, bar_count_5m, imported_at, meta_json"
                ") VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?)",
                (
                    "SPY",
                    trade_date,
                    "extended",
                    "test-source",
                    f"SPY {trade_date}",
                    "2026-07-18 00:00:00",
                    "{}",
                ),
            )
            market_day_id = int(connection.execute(
                "SELECT id FROM market_days WHERE ticker='SPY' AND trade_date=? AND session_mode='extended'",
                (trade_date,),
            ).fetchone()[0])
            values = [0, f"{trade_date}T09:30:00-04:00", "09:30", 100.0, 101.0, 99.0, 100.5, 10.0]
            values.extend([100.0] * (len(BAR_COLUMNS) - len(values)))
            placeholders = ", ".join("?" for _ in BAR_COLUMNS)
            for table in ("bars_1m", "bars_5m"):
                connection.execute(
                    f"INSERT INTO {table}(market_day_id, {', '.join(BAR_COLUMNS)}) "
                    f"VALUES (?, {placeholders})",
                    (market_day_id, *values),
                )

    def _assert_dates(self, path: Path, expected: list[str]) -> None:
        validate_sqlite(path)
        self.assertEqual(capture_database_token(path).logical_sha256 != "", True)
        with contextlib.closing(readonly_connect(path)) as connection:
            dates = [
                row[0]
                for row in connection.execute(
                    "SELECT trade_date FROM market_days ORDER BY trade_date"
                ).fetchall()
            ]
        self.assertEqual(dates, expected)


if __name__ == "__main__":
    unittest.main()
