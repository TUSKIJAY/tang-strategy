from __future__ import annotations

import contextlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from app.db import SCHEMA
from app.services.db_safety import BAR_COLUMNS, file_sha256, validate_sqlite
from scripts.rebuild_live_extended_db import rebuild_db, run_candidate_import


class RebuildLiveExtendedDatabaseTests(unittest.TestCase):
    def test_no_seed_refuses_and_preserves_original_bytes(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            before = file_sha256(live)

            with self.assertRaisesRegex(RuntimeError, "no SPY_/SPX_"):
                self._rebuild(workspace)

            self.assertEqual(file_sha256(live), before)

    def test_subset_seed_reports_missing_date_and_preserves_original_bytes(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17", "2026-07-18"])
            self._write_seed(workspace, "2026-07-18")
            before = file_sha256(live)

            with self.assertRaisesRegex(
                RuntimeError,
                r"candidate would lose market days:[\s\S]*SPY\|2026-07-17\|extended",
            ):
                self._rebuild(workspace)

            self.assertEqual(file_sha256(live), before)
            self._assert_dates(live, ["2026-07-17", "2026-07-18"])

    def test_explicit_date_loss_override_allows_intentional_shrink(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17", "2026-07-18"])
            self._write_seed(workspace, "2026-07-18")

            result = self._rebuild(workspace, allow_date_loss=True)

            self.assertTrue(result["promoted"])
            self._assert_dates(live, ["2026-07-18"])

    def test_candidate_import_exception_preserves_original_bytes(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            self._write_seed(workspace, "2026-07-17")
            before = file_sha256(live)

            def fail_import(*_: object) -> dict[str, object]:
                raise RuntimeError("forced candidate import failure")

            with self.assertRaisesRegex(RuntimeError, "forced candidate import failure"):
                self._rebuild(workspace, candidate_importer=fail_import)

            self.assertEqual(file_sha256(live), before)

    def test_corrupt_candidate_integrity_failure_preserves_original_bytes(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            self._write_seed(workspace, "2026-07-17")
            before = file_sha256(live)

            def corrupt_candidate(candidate: Path, *_: object) -> dict[str, object]:
                candidate.write_bytes(b"not-a-sqlite-database")
                return {"corrupt": True}

            with self.assertRaises(sqlite3.DatabaseError):
                self._rebuild(workspace, candidate_importer=corrupt_candidate)

            self.assertEqual(file_sha256(live), before)

    def test_date_complete_candidate_with_empty_bars_is_rejected(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            self._write_seed(workspace, "2026-07-17")
            before = file_sha256(live)

            def empty_candidate_bars(
                candidate: Path,
                live_extended: Path,
                strategies: Path,
                content: Path,
            ) -> dict[str, object]:
                result = run_candidate_import(candidate, live_extended, strategies, content)
                with contextlib.closing(sqlite3.connect(candidate)) as connection, connection:
                    connection.execute("DELETE FROM bars_1m")
                return result

            with self.assertRaisesRegex(RuntimeError, "semantic count mismatch"):
                self._rebuild(workspace, candidate_importer=empty_candidate_bars)

            self.assertEqual(file_sha256(live), before)

    def test_seed_count_mismatch_is_rejected_before_candidate(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            self._write_seed(workspace, "2026-07-17", declared_1m=2)
            before = file_sha256(live)

            with self.assertRaisesRegex(RuntimeError, "metadata count mismatch"):
                self._rebuild(workspace)

            self.assertEqual(file_sha256(live), before)

    def test_strategy_shrink_is_rejected_even_with_date_loss_override(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(
                workspace,
                ["2026-07-17"],
                strategy_slugs=["tang-test-1", "legacy-1"],
            )
            self._write_seed(workspace, "2026-07-17")
            before = file_sha256(live)

            with self.assertRaisesRegex(RuntimeError, "would lose strategies"):
                self._rebuild(workspace, allow_date_loss=True)

            self.assertEqual(file_sha256(live), before)

    def test_teaching_shrink_is_rejected(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(
                workspace,
                ["2026-07-17"],
                teaching_keys=[("rules", "default", "compiled-index")],
            )
            self._write_seed(workspace, "2026-07-17")
            before = file_sha256(live)

            with self.assertRaisesRegex(RuntimeError, "would lose teaching assets"):
                self._rebuild(workspace)

            self.assertEqual(file_sha256(live), before)

    def test_superset_candidate_atomically_replaces_original(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            self._write_seed(workspace, "2026-07-17")
            self._write_seed(workspace, "2026-07-18")

            result = self._rebuild(workspace)

            self.assertTrue(result["promoted"])
            self.assertEqual(result["validation"]["market_days"], 2)
            validate_sqlite(live)
            self._assert_dates(live, ["2026-07-17", "2026-07-18"])

    def test_concurrent_source_drift_refuses_promotion_and_preserves_new_write(self) -> None:
        with self._workspace() as workspace:
            live = self._create_live_db(workspace, ["2026-07-17"])
            self._write_seed(workspace, "2026-07-17")
            self._write_seed(workspace, "2026-07-18")

            def import_then_drift(
                candidate: Path,
                live_extended: Path,
                strategies: Path,
                content: Path,
            ) -> dict[str, object]:
                result = run_candidate_import(candidate, live_extended, strategies, content)
                self._insert_day(live, "2026-07-19")
                return result

            with self.assertRaisesRegex(RuntimeError, "live DB drifted"):
                self._rebuild(workspace, candidate_importer=import_then_drift)

            self._assert_dates(live, ["2026-07-17", "2026-07-19"])

    @contextlib.contextmanager
    def _workspace(self):
        with tempfile.TemporaryDirectory() as raw_directory:
            root = Path(raw_directory)
            (root / "live_extended").mkdir()
            (root / "strategies").mkdir()
            (root / "content").mkdir()
            (root / "strategies" / "tang_test.json").write_text(
                json.dumps({"name": "Tang Test", "version": "1"}),
                encoding="utf-8",
            )
            yield root

    def _rebuild(
        self,
        workspace: Path,
        allow_date_loss: bool = False,
        candidate_importer=run_candidate_import,
    ):
        return rebuild_db(
            db_path=workspace / "live.db",
            live_extended_dir=workspace / "live_extended",
            strategies_dir=workspace / "strategies",
            content_dir=workspace / "content",
            allow_date_loss=allow_date_loss,
            candidate_importer=candidate_importer,
        )

    def _create_live_db(
        self,
        workspace: Path,
        dates: list[str],
        strategy_slugs: list[str] | None = None,
        teaching_keys: list[tuple[str, str, str]] | None = None,
    ) -> Path:
        path = workspace / "live.db"
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.executescript(SCHEMA)
            for slug in strategy_slugs or ["tang-test-1"]:
                connection.execute(
                    "INSERT INTO strategies(name, version, slug, description, json_body, active) "
                    "VALUES (?, '1', ?, '', '{}', 1)",
                    (slug, slug),
                )
            for asset_type, version, slug in teaching_keys or []:
                connection.execute(
                    "INSERT INTO teaching_assets(asset_type, version, slug, json_body) "
                    "VALUES (?, ?, ?, '{}')",
                    (asset_type, version, slug),
                )
        for trade_date in dates:
            self._insert_day(path, trade_date)
        return path

    def _insert_day(self, path: Path, trade_date: str) -> None:
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("INSERT OR IGNORE INTO tickers(symbol, name) VALUES ('SPY', 'SPY')")
            connection.execute(
                "INSERT INTO market_days("
                "ticker, trade_date, session_mode, source, title, "
                "bar_count_1m, bar_count_5m, imported_at, meta_json"
                ") VALUES ('SPY', ?, 'extended', 'test', ?, 1, 1, '2026-07-18 00:00:00', '{}')",
                (trade_date, f"SPY {trade_date}"),
            )
            day_id = int(connection.execute(
                "SELECT id FROM market_days WHERE trade_date=?", (trade_date,)
            ).fetchone()[0])
            values = self._bar_values(trade_date)
            placeholders = ", ".join("?" for _ in BAR_COLUMNS)
            for table in ("bars_1m", "bars_5m"):
                connection.execute(
                    f"INSERT INTO {table}(market_day_id, {', '.join(BAR_COLUMNS)}) "
                    f"VALUES (?, {placeholders})",
                    (day_id, *values),
                )

    def _write_seed(self, workspace: Path, trade_date: str, declared_1m: int = 1) -> None:
        directory = workspace / "live_extended" / trade_date
        directory.mkdir(parents=True, exist_ok=True)
        bar = {
            "ts": f"{trade_date}T09:30:00-04:00",
            "t": "09:30",
            "O": 100.0,
            "H": 101.0,
            "L": 99.0,
            "C": 100.5,
            "V": 10.0,
            "vw": 100.0,
        }
        payload = {
            "meta": {
                "ticker": "SPY",
                "date": trade_date,
                "session_mode": "extended",
                "counts": {"bars_1m": declared_1m, "bars_5m": 1},
            },
            "bars_1m": [bar],
            "bars_5m": [bar],
        }
        (directory / f"SPY_{trade_date}.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )

    def _bar_values(self, trade_date: str) -> list[object]:
        values: list[object] = [
            0,
            f"{trade_date}T09:30:00-04:00",
            "09:30",
            100.0,
            101.0,
            99.0,
            100.5,
            10.0,
        ]
        values.extend([100.0] * (len(BAR_COLUMNS) - len(values)))
        return values

    def _assert_dates(self, path: Path, expected: list[str]) -> None:
        with contextlib.closing(sqlite3.connect(path)) as connection:
            actual = [
                row[0]
                for row in connection.execute(
                    "SELECT trade_date FROM market_days ORDER BY trade_date"
                ).fetchall()
            ]
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
