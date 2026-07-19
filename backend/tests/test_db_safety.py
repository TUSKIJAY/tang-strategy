from __future__ import annotations

import contextlib
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.services import db_safety
from app.db import SCHEMA, build_target_candidate, connect, init_target_db, migrate_candidate_schema
from app.services.trade_records import load_trader_registry, validate_trade_repository
from app.services.importer import _import_market_data
from app.services.db_safety import (
    BAR_COLUMNS,
    bar_owner,
    capture_database_token,
    create_consistent_snapshot,
    day_sha256,
    file_sha256,
    promote_candidate,
    readonly_connect,
    validate_exactly_one_active_dataset,
    validate_sqlite,
)
from scripts.recover_historical_market_days import SourceSpec, copy_market_day


class DatabaseSafetyTests(unittest.TestCase):
    def test_windows_lock_backend_uses_one_byte_nonblocking_region(self) -> None:
        class FakeMsvcrt:
            LK_NBLCK = 1
            LK_UNLCK = 2

            def __init__(self) -> None:
                self.calls: list[tuple[int, int]] = []

            def locking(self, descriptor: int, mode: int, length: int) -> None:
                self.calls.append((mode, length))

        fake = FakeMsvcrt()
        original_fcntl = db_safety._fcntl
        original_msvcrt = db_safety._msvcrt
        try:
            db_safety._fcntl = None
            db_safety._msvcrt = fake
            with tempfile.TemporaryDirectory() as raw_directory:
                target = Path(raw_directory) / "target.db"
                with db_safety.db_write_lock(target):
                    self.assertEqual(Path(f"{target}.write.lock").read_bytes(), b"\0")
        finally:
            db_safety._fcntl = original_fcntl
            db_safety._msvcrt = original_msvcrt
        self.assertEqual(fake.calls, [(fake.LK_NBLCK, 1), (fake.LK_UNLCK, 1)])

    def test_fresh_target_schema_has_dataset_ownership_and_agent_views(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            target = Path(raw_directory) / "target.db"
            init_target_db(target)
            with contextlib.closing(readonly_connect(target)) as connection:
                self.assertEqual(
                    {row[1] for row in connection.execute("PRAGMA table_info(bars_1m)")},
                    {"dataset_id", *BAR_COLUMNS},
                )
                views = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='view'"
                    ).fetchall()
                }
                self.assertEqual(
                    views,
                    {
                        "v_active_market_datasets",
                        "v_trade_group_performance",
                        "v_trade_event_facts",
                        "v_trade_market_context",
                    },
                )

    def test_old_schema_candidate_rekeys_bars_without_logical_change(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            candidate = Path(raw_directory) / "candidate.db"
            self._create_db(candidate, ["2026-07-17"])
            with contextlib.closing(readonly_connect(candidate)) as connection:
                before = day_sha256(connection, "SPY", "2026-07-17", "extended")

            report = migrate_candidate_schema(candidate)

            with contextlib.closing(readonly_connect(candidate)) as connection:
                after = day_sha256(connection, "SPY", "2026-07-17", "extended")
                validate_exactly_one_active_dataset(connection)
                dataset = connection.execute(
                    "SELECT dataset_id, provider, state FROM market_datasets"
                ).fetchone()
                self.assertEqual(dataset[2], "active")
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM bars_1m WHERE dataset_id=?", (dataset[0],)).fetchone()[0],
                    1,
                )
            with contextlib.closing(sqlite3.connect(candidate)) as connection:
                with self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(
                        "INSERT INTO market_datasets(dataset_id, market_day_id, provider, imported_at, "
                        "checksum, state) VALUES ('duplicate-active', 1, 'test', 'now', 'x', 'active')"
                    )
                connection.execute("UPDATE market_datasets SET state='superseded'")
                connection.commit()
            with contextlib.closing(readonly_connect(candidate)) as connection:
                with self.assertRaisesRegex(RuntimeError, "exactly one active dataset"):
                    validate_exactly_one_active_dataset(connection)
            self.assertEqual(before, after)
            self.assertEqual(report["preservation"], "passed")

    def test_target_import_supersedes_dataset_as_one_atomic_owner(self) -> None:
        bar = {
            "ts": "2026-07-17T09:30:00-04:00",
            "t": "09:30",
            "O": 100.0,
            "H": 101.0,
            "L": 99.0,
            "C": 100.5,
            "V": 10.0,
            "vw": 100.0,
        }
        with tempfile.TemporaryDirectory() as raw_directory:
            target = Path(raw_directory) / "target.db"
            init_target_db(target)
            with contextlib.closing(connect(target)) as connection, connection:
                market_day_id = _import_market_data(
                    connection,
                    "SPY",
                    "2026-07-17",
                    "extended",
                    {"provider": "fixture"},
                    [bar],
                    [bar],
                    Path("SPY_2026-07-17.json"),
                )
                first_owner = bar_owner(connection, market_day_id)[1]
                changed = {**bar, "C": 100.75}
                _import_market_data(
                    connection,
                    "SPY",
                    "2026-07-17",
                    "extended",
                    {"provider": "fixture"},
                    [changed],
                    [changed],
                    Path("SPY_2026-07-17.json"),
                )
                second_owner = bar_owner(connection, market_day_id)[1]
                states = dict(
                    connection.execute(
                        "SELECT state, COUNT(*) FROM market_datasets GROUP BY state"
                    ).fetchall()
                )
                self.assertNotEqual(first_owner, second_owner)
                self.assertEqual(states, {"active": 1, "superseded": 1})
                self.assertEqual(
                    connection.execute(
                        "SELECT close FROM bars_1m WHERE dataset_id=?", (second_owner,)
                    ).fetchone()[0],
                    100.75,
                )

    def test_recovery_copies_old_owner_bars_into_target_dataset(self) -> None:
        root = Path(__file__).resolve().parents[2]
        live = root / "data" / "sqlite" / "tang_strategy_live_extended.db"
        source = SourceSpec("SPY", "2026-07-17", "extended", live)
        with tempfile.TemporaryDirectory() as raw_directory:
            candidate = Path(raw_directory) / "target.db"
            init_target_db(candidate)
            report = copy_market_day(candidate, source)
            self.assertEqual((report["bars_1m"], report["bars_5m"]), (868, 192))
            with contextlib.closing(readonly_connect(live)) as source_connection:
                expected = day_sha256(source_connection, *source.key)
            with contextlib.closing(readonly_connect(candidate)) as candidate_connection:
                actual = day_sha256(candidate_connection, *source.key)
                validate_exactly_one_active_dataset(candidate_connection)
            self.assertEqual(actual, expected)

    def test_candidate_failure_and_drift_never_change_live_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            directory = Path(raw_directory)
            live = directory / "live.db"
            candidate = directory / "candidate.db"
            self._create_db(live, ["2026-07-17"])
            original = file_sha256(live)

            def invalid_foreign_key(connection: sqlite3.Connection) -> None:
                connection.execute(
                    "INSERT INTO market_datasets(dataset_id, market_day_id, provider, imported_at, "
                    "checksum, state) VALUES ('invalid-fk', 999, 'test', 'now', 'x', 'superseded')"
                )

            with self.assertRaisesRegex(RuntimeError, "foreign-key validation failed"):
                build_target_candidate(live, candidate, failure_hook=invalid_foreign_key)
            self.assertEqual(file_sha256(live), original)

            candidate.unlink()

            def drift_live(_: sqlite3.Connection) -> None:
                self._insert_day(live, "2026-07-18")

            with self.assertRaisesRegex(RuntimeError, "live DB drifted"):
                build_target_candidate(live, candidate, failure_hook=drift_live)
            self._assert_dates(live, ["2026-07-17", "2026-07-18"])

    def test_repository_candidate_projects_49_days_and_agent_filters(self) -> None:
        root = Path(__file__).resolve().parents[2]
        live = root / "data" / "sqlite" / "tang_strategy_live_extended.db"
        registry = load_trader_registry(root / "content" / "traders" / "index.json")
        days = validate_trade_repository((root / "content" / "trades").glob("*.json"), registry)
        with tempfile.TemporaryDirectory() as raw_directory:
            candidate = Path(raw_directory) / "candidate.db"
            baseline, report = build_target_candidate(
                live,
                candidate,
                registry,
                days,
            )
            self.assertEqual(report["counts"]["market_days"], 49)
            self.assertEqual(report["counts"]["market_datasets"], 52)
            self.assertEqual(report["counts"]["trade_groups"], 33)
            self.assertEqual(report["counts"]["trade_outcomes"], 7)
            self.assertEqual(report["logical_market_sha256"], baseline.logical_sha256)
            with contextlib.closing(sqlite3.connect(candidate)) as connection:
                connection.row_factory = sqlite3.Row
                reported = connection.execute(
                    "SELECT trade_group_id, direction, reported_return_pct "
                    "FROM v_trade_group_performance "
                    "WHERE trader_id='tang' AND underlying='SPY' "
                    "AND reported_return_pct IS NOT NULL ORDER BY trade_date, trade_group_id"
                ).fetchall()
                self.assertEqual([row["reported_return_pct"] for row in reported], [50.0, 40.0, 40.0, 30.0])
                winning_reported = connection.execute(
                    "SELECT COUNT(*) FROM v_trade_group_performance "
                    "WHERE trader_id='tang' AND underlying='SPY' "
                    "AND reported_stats_eligible=1 AND reported_return_pct>0"
                ).fetchone()[0]
                incomplete_calculated = connection.execute(
                    "SELECT COUNT(*) FROM v_trade_group_performance "
                    "WHERE trader_id='tang' AND underlying='SPY' "
                    "AND calculated_stats_eligible=0"
                ).fetchone()[0]
                self.assertEqual((winning_reported, incomplete_calculated), (4, 27))
                event = connection.execute(
                    "SELECT event_id, trade_group_id, trade_date FROM v_trade_event_facts "
                    "WHERE direction='CALL' ORDER BY trade_date, event_id LIMIT 1"
                ).fetchone()
                dataset = connection.execute(
                    "SELECT dataset_id FROM v_active_market_datasets WHERE ticker='SPY' AND trade_date=?",
                    (event["trade_date"],),
                ).fetchone()[0]
                connection.execute(
                    "INSERT INTO analysis_runs VALUES ('run-test', 'context', '1', '2026-07-19T00:00:00Z', 'complete', '{}')"
                )
                connection.execute(
                    "INSERT INTO trade_market_context(analysis_run_id, event_id, dataset_id, timeframe, "
                    "bar_idx, relation, context_json) VALUES ('run-test', ?, ?, '1m', 0, 'at_or_before', '{}')",
                    (event["event_id"], dataset),
                )
                connection.commit()
                context_row = connection.execute(
                    "SELECT trader_id, underlying, trade_group_id, algorithm_version "
                    "FROM v_trade_market_context WHERE analysis_run_id='run-test'"
                ).fetchone()
                self.assertEqual(tuple(context_row), ("tang", "SPY", event["trade_group_id"], "1"))
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
