from __future__ import annotations

import contextlib
import io
import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.db import SCHEMA
from app.services.db_safety import (
    BAR_COLUMNS,
    bars_use_datasets,
    db_write_lock,
    file_sha256,
    validate_sqlite,
)
from scripts.update_spy_qqq_market_day import (
    BACKEND_DIR,
    PAIR,
    accept_staged_pair,
    fetch_one_symbol,
    main as pair_main,
    resolve_latest_completed_nyse_session,
    run_pair_update,
)


class SpyQqqPairUpdateTests(unittest.TestCase):
    trade_date = "2026-07-16"

    def test_completed_session_resolution_uses_nyse_calendar(self) -> None:
        self.assertEqual(
            resolve_latest_completed_nyse_session(
                datetime(2026, 7, 18, 12, 0, tzinfo=timezone.utc)
            ),
            "2026-07-17",
        )

    def test_provider_fetch_bootstraps_absolute_backend_pythonpath(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            staging = Path(raw_directory)

            def fake_run(command, **kwargs):
                symbol = command[command.index("--symbol") + 1]
                output = staging / self.trade_date / f"{symbol}_{self.trade_date}.json"
                self._write_payload(output, symbol)
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with patch(
                "scripts.update_spy_qqq_market_day.subprocess.run",
                side_effect=fake_run,
            ) as run:
                for symbol, exchange in (("SPY", "AMEX"), ("QQQ", "NASDAQ")):
                    with self.subTest(symbol=symbol):
                        output = fetch_one_symbol(
                            symbol,
                            self.trade_date,
                            staging,
                            "tradingview",
                        )
                        self.assertTrue(output.is_file())
                        command = run.call_args.args[0]
                        self.assertEqual(command[command.index("--exchange") + 1], exchange)
                        environment = run.call_args.kwargs["env"]
                        self.assertEqual(
                            Path(environment["PYTHONPATH"].split(os.pathsep)[0]),
                            BACKEND_DIR,
                        )

    def test_spy_pass_qqq_fetch_failure_writes_nothing(self) -> None:
        with self._workspace() as workspace:
            before = file_sha256(workspace["db"])
            with self.assertRaisesRegex(RuntimeError, "QQQ: forced fetch failure"):
                self._run(workspace, fail_symbols={"QQQ"})
            self.assertEqual(file_sha256(workspace["db"]), before)
            self.assertFalse((workspace["accepted"] / self.trade_date).exists())

    def test_qqq_pass_spy_fetch_failure_writes_nothing(self) -> None:
        with self._workspace() as workspace:
            before = file_sha256(workspace["db"])
            with self.assertRaisesRegex(RuntimeError, "SPY: forced fetch failure"):
                self._run(workspace, fail_symbols={"SPY"})
            self.assertEqual(file_sha256(workspace["db"]), before)
            self.assertFalse((workspace["accepted"] / self.trade_date).exists())

    def test_pair_date_session_and_provider_mismatch_are_rejected(self) -> None:
        cases = (
            ("QQQ", {"declared_date": "2026-07-17"}, "QQQ date gate failed"),
            ("SPY", {"session_mode": "rth"}, "SPY session gate failed"),
            ("QQQ", {"provider": "ibkr"}, "QQQ provider gate failed"),
        )
        for symbol, changes, message in cases:
            with self.subTest(message=message), self._workspace() as workspace:
                paths = self._staged_paths(workspace["staged"])
                self._write_payload(paths[symbol], symbol, **changes)
                before = file_sha256(workspace["db"])
                with self.assertRaisesRegex(RuntimeError, message):
                    accept_staged_pair(
                        paths,
                        self.trade_date,
                        "tradingview",
                        workspace["db"],
                        workspace["accepted"],
                        {"head": "test", "status": []},
                    )
                self.assertEqual(file_sha256(workspace["db"]), before)

    def test_non_nyse_pair_date_is_rejected_before_candidate_work(self) -> None:
        with self._workspace() as workspace:
            weekend = "2026-07-18"
            paths = {}
            for symbol in PAIR:
                path = workspace["staged"] / weekend / f"{symbol}_{weekend}.json"
                self._write_payload(path, symbol, declared_date=weekend)
                paths[symbol] = path
            before = file_sha256(workspace["db"])
            with self.assertRaisesRegex(RuntimeError, "not an NYSE trading session"):
                accept_staged_pair(
                    paths,
                    weekend,
                    "tradingview",
                    workspace["db"],
                    workspace["accepted"],
                    {"head": "test", "status": []},
                )
            self.assertEqual(file_sha256(workspace["db"]), before)

    def test_calendar_and_payload_quality_fail_closed(self) -> None:
        def wrong_claim(payload):
            payload["meta"]["quality"]["rth_1m_expected"] = 389

        def missing_receipt(payload):
            payload["meta"]["quality"]["rth_missing_minutes"] = ["10:00"]

        def duplicate_receipt(payload):
            payload["meta"]["quality"]["rth_duplicate_minutes"] = 1

        def synthetic_padding(payload):
            payload["meta"]["synthetic_padding"] = True

        def actual_bar_loss(payload):
            payload["bars_1m"].pop()
            payload["meta"].pop("counts")

        def wrong_timestamp_date(payload):
            payload["bars_1m"][0]["ts"] = "2026-07-15T09:30:00-04:00"

        def wrong_timestamp_offset(payload):
            payload["bars_1m"][0]["ts"] = "2026-07-16T09:30:00-05:00"

        def display_time_disagrees_with_timestamp(payload):
            payload["bars_1m"][0]["t"] = "09:31"

        cases = (
            ("calendar claim", wrong_claim),
            ("missing minute receipt", missing_receipt),
            ("duplicate minute receipt", duplicate_receipt),
            ("synthetic padding", synthetic_padding),
            ("actual bar loss", actual_bar_loss),
            ("timestamp date mismatch", wrong_timestamp_date),
            ("timestamp offset mismatch", wrong_timestamp_offset),
            ("display time mismatch", display_time_disagrees_with_timestamp),
        )
        for label, mutate in cases:
            with self.subTest(label=label), self._workspace() as workspace:
                paths = self._staged_paths(workspace["staged"])
                qqq = json.loads(paths["QQQ"].read_text(encoding="utf-8"))
                mutate(qqq)
                paths["QQQ"].write_text(json.dumps(qqq), encoding="utf-8")
                before = file_sha256(workspace["db"])
                with self.assertRaisesRegex(RuntimeError, "quality gate failed"):
                    accept_staged_pair(
                        paths,
                        self.trade_date,
                        "tradingview",
                        workspace["db"],
                        workspace["accepted"],
                        {"head": "test", "status": []},
                    )
                self.assertEqual(file_sha256(workspace["db"]), before)

    def test_concurrent_pair_run_is_serialized_before_any_write(self) -> None:
        with self._workspace(existing_pair=True) as workspace:
            paths = self._staged_paths(workspace["staged"])
            before_db = file_sha256(workspace["db"])
            before_seeds = self._accepted_bytes(workspace)
            lock_anchor = workspace["db"].with_name(f".{workspace['db'].stem}.spy-qqq-pair.db")
            with db_write_lock(lock_anchor):
                with self.assertRaisesRegex(TimeoutError, "Timed out waiting"):
                    accept_staged_pair(
                        paths,
                        self.trade_date,
                        "tradingview",
                        workspace["db"],
                        workspace["accepted"],
                        {"head": "test", "status": []},
                        pair_lock_timeout_seconds=0.01,
                    )
            self.assertEqual(file_sha256(workspace["db"]), before_db)
            self.assertEqual(self._accepted_bytes(workspace), before_seeds)

    def test_offline_staged_cli_refuses_tracked_targets(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            errors = io.StringIO()
            with redirect_stderr(errors):
                result = pair_main([
                    self.trade_date,
                    "--staged-payload-dir",
                    raw_directory,
                ])
            self.assertEqual(result, 1)
            self.assertIn("cannot target the tracked DB", errors.getvalue())

    def test_candidate_failure_preserves_db_and_accepted_pair(self) -> None:
        with self._workspace(existing_pair=True) as workspace:
            before_db = file_sha256(workspace["db"])
            before_seeds = self._accepted_bytes(workspace)

            def break_candidate(candidate: Path) -> None:
                with contextlib.closing(sqlite3.connect(candidate)) as connection, connection:
                    dataset = connection.execute(
                        "SELECT market_datasets.dataset_id FROM market_datasets "
                        "JOIN market_days ON market_days.id=market_datasets.market_day_id "
                        "WHERE market_days.ticker='QQQ' AND market_days.trade_date=? "
                        "AND market_datasets.state='active'",
                        (self.trade_date,),
                    ).fetchone()[0]
                    connection.execute("DELETE FROM bars_5m WHERE dataset_id=?", (dataset,))

            with self.assertRaisesRegex(RuntimeError, "QQQ candidate assemble gate failed"):
                self._run(workspace, candidate_hook=break_candidate)
            self.assertEqual(file_sha256(workspace["db"]), before_db)
            self.assertEqual(self._accepted_bytes(workspace), before_seeds)

    def test_tracked_db_drift_refuses_promotion_and_rolls_back_seeds(self) -> None:
        with self._workspace(existing_pair=True) as workspace:
            before_seeds = self._accepted_bytes(workspace)

            def concurrent_write(live: Path) -> None:
                with contextlib.closing(sqlite3.connect(live)) as connection, connection:
                    connection.execute(
                        "INSERT INTO teaching_assets(asset_type, version, slug, json_body) "
                        "VALUES ('test', 'default', 'concurrent-write', '{}')"
                    )

            with self.assertRaisesRegex(RuntimeError, "live DB drifted"):
                self._run(workspace, before_promote_hook=concurrent_write)
            self.assertEqual(self._accepted_bytes(workspace), before_seeds)
            with contextlib.closing(sqlite3.connect(workspace["db"])) as connection:
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM teaching_assets WHERE slug='concurrent-write'"
                    ).fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM market_days WHERE trade_date=?",
                        (self.trade_date,),
                    ).fetchone()[0],
                    0,
                )

        with self._workspace(existing_pair=True) as workspace:
            before_seeds = self._accepted_bytes(workspace)

            def fetch_then_drift(symbol: str, trade_date: str, staging: Path, provider: str) -> Path:
                path = staging / trade_date / f"{symbol}_{trade_date}.json"
                self._write_payload(path, symbol, provider=provider)
                if symbol == "SPY":
                    with contextlib.closing(sqlite3.connect(workspace["db"])) as connection, connection:
                        connection.execute(
                            "INSERT INTO teaching_assets(asset_type, version, slug, json_body) "
                            "VALUES ('test', 'default', 'during-staging', '{}')"
                        )
                return path

            with self.assertRaisesRegex(RuntimeError, "drifted during provider staging"):
                run_pair_update(
                    self.trade_date,
                    "tradingview",
                    db_path=workspace["db"],
                    accepted_seed_dir=workspace["accepted"],
                    git_baseline={"head": "test", "status": []},
                    fetch_one=fetch_then_drift,
                )
            self.assertEqual(self._accepted_bytes(workspace), before_seeds)
            with contextlib.closing(sqlite3.connect(workspace["db"])) as connection:
                self.assertEqual(
                    connection.execute(
                        "SELECT COUNT(*) FROM teaching_assets WHERE slug='during-staging'"
                    ).fetchone()[0],
                    1,
                )

    def test_second_seed_replace_failure_rolls_back_first_and_preserves_db(self) -> None:
        with self._workspace(existing_pair=True) as workspace:
            before_db = file_sha256(workspace["db"])
            before_seeds = self._accepted_bytes(workspace)
            replacements = 0

            def fail_second(source: Path, target: Path) -> None:
                nonlocal replacements
                replacements += 1
                if replacements == 2:
                    raise OSError("forced second seed replacement failure")
                os.replace(source, target)

            with self.assertRaisesRegex(OSError, "forced second seed replacement failure"):
                self._run(workspace, replace_file=fail_second)
            self.assertEqual(file_sha256(workspace["db"]), before_db)
            self.assertEqual(self._accepted_bytes(workspace), before_seeds)
            self.assertEqual(list(workspace["accepted"].rglob("*.candidate")), [])
            self.assertEqual(list(workspace["accepted"].rglob("*.backup")), [])

    def test_full_pair_success_promotes_one_candidate_and_both_seeds(self) -> None:
        with self._workspace(existing_pair=True) as workspace:
            before_db = file_sha256(workspace["db"])
            result = self._run(workspace)

            self.assertEqual(result["status"], "accepted")
            self.assertEqual(result["db"]["before_sha256"], before_db)
            self.assertNotEqual(result["db"]["after_sha256"], before_db)
            self.assertEqual(result["pair"]["tickers"], list(PAIR))
            self.assertEqual(result["candidate"]["pair_counts"]["SPY"]["bars_1m"], 390)
            self.assertEqual(result["candidate"]["pair_counts"]["QQQ"]["bars_5m"], 78)
            validate_sqlite(workspace["db"])
            with contextlib.closing(sqlite3.connect(workspace["db"])) as connection:
                self.assertTrue(bars_use_datasets(connection))
                rows = connection.execute(
                    "SELECT market_days.ticker, market_datasets.provider, "
                    "COUNT(DISTINCT market_datasets.dataset_id) "
                    "FROM market_days JOIN market_datasets "
                    "ON market_datasets.market_day_id=market_days.id "
                    "AND market_datasets.state='active' "
                    "WHERE market_days.trade_date=? GROUP BY market_days.ticker "
                    "ORDER BY market_days.ticker",
                    (self.trade_date,),
                ).fetchall()
            self.assertEqual(rows, [("QQQ", "tradingview", 1), ("SPY", "tradingview", 1)])
            for symbol in PAIR:
                accepted = workspace["accepted"] / self.trade_date / f"{symbol}_{self.trade_date}.json"
                self.assertEqual(
                    json.loads(accepted.read_text(encoding="utf-8"))["meta"]["ticker"],
                    symbol,
                )
                self.assertNotIn("old", accepted.read_text(encoding="utf-8"))

    @contextlib.contextmanager
    def _workspace(self, existing_pair: bool = False):
        with tempfile.TemporaryDirectory() as raw_directory:
            root = Path(raw_directory)
            staged = root / "staged"
            accepted = root / "accepted"
            staged.mkdir()
            accepted.mkdir()
            db_path = root / "live.db"
            self._create_live_db(db_path)
            if existing_pair:
                directory = accepted / self.trade_date
                directory.mkdir(parents=True)
                for symbol in PAIR:
                    (directory / f"{symbol}_{self.trade_date}.json").write_text(
                        json.dumps({"old": symbol}), encoding="utf-8"
                    )
            yield {"root": root, "staged": staged, "accepted": accepted, "db": db_path}

    def _run(self, workspace, fail_symbols=frozenset(), **kwargs):
        def fetch(symbol: str, trade_date: str, staging: Path, provider: str) -> Path:
            if symbol in fail_symbols:
                raise RuntimeError("forced fetch failure")
            path = staging / trade_date / f"{symbol}_{trade_date}.json"
            self._write_payload(path, symbol, provider=provider)
            return path

        return run_pair_update(
            self.trade_date,
            "tradingview",
            db_path=workspace["db"],
            accepted_seed_dir=workspace["accepted"],
            git_baseline={"head": "test", "status": []},
            fetch_one=fetch,
            **kwargs,
        )

    def _staged_paths(self, staged: Path) -> dict[str, Path]:
        paths = {}
        for symbol in PAIR:
            path = staged / self.trade_date / f"{symbol}_{self.trade_date}.json"
            self._write_payload(path, symbol)
            paths[symbol] = path
        return paths

    def _write_payload(
        self,
        path: Path,
        symbol: str,
        declared_date: str | None = None,
        session_mode: str = "extended",
        provider: str = "tradingview",
    ) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload_date = declared_date or self.trade_date
        start = datetime.fromisoformat(f"{payload_date}T09:30:00-04:00")

        def bar_at(offset: int) -> dict[str, object]:
            current = start + timedelta(minutes=offset)
            return {
                "ts": current.isoformat(),
                "t": current.strftime("%H:%M"),
                "O": 100.0,
                "H": 101.0,
                "L": 99.0,
                "C": 100.5,
                "V": 10.0,
                "vw": 100.0,
            }

        bars_1m = [bar_at(offset) for offset in range(390)]
        bars_5m = [bar_at(offset) for offset in range(0, 390, 5)]
        payload = {
            "meta": {
                "ticker": symbol,
                "date": payload_date,
                "session_mode": session_mode,
                "provider": provider,
                "source": f"{provider} fixture",
                "market_calendar": "NYSE",
                "synthetic_padding": False,
                "counts": {"bars_1m": 390, "bars_5m": 78},
                "quality": {
                    "rth_1m_bars": 390,
                    "rth_1m_expected": 390,
                    "rth_missing_minutes": [],
                    "rth_duplicate_minutes": 0,
                    "rth_5m_bars": 78,
                    "rth_5m_expected": 78,
                },
            },
            "bars_1m": bars_1m,
            "bars_5m": bars_5m,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def _create_live_db(self, path: Path) -> None:
        with contextlib.closing(sqlite3.connect(path)) as connection, connection:
            connection.executescript(SCHEMA)
            connection.execute(
                "INSERT INTO strategies(name, version, slug, description, json_body, active) "
                "VALUES ('Test', '1', 'test-1', '', '{}', 1)"
            )
            connection.execute(
                "INSERT INTO teaching_assets(asset_type, version, slug, json_body) "
                "VALUES ('rules', 'default', 'fixture', '{}')"
            )
            connection.execute("INSERT INTO tickers(symbol, name) VALUES ('SPY', 'SPY')")
            connection.execute(
                "INSERT INTO market_days(ticker, trade_date, session_mode, source, title, "
                "bar_count_1m, bar_count_5m, imported_at, meta_json) "
                "VALUES ('SPY', '2026-07-17', 'extended', 'fixture', 'SPY baseline', "
                "1, 1, '2026-07-18 00:00:00', '{}')"
            )
            day_id = connection.execute("SELECT id FROM market_days").fetchone()[0]
            values = self._bar_values("2026-07-17")
            placeholders = ", ".join("?" for _ in BAR_COLUMNS)
            for table in ("bars_1m", "bars_5m"):
                connection.execute(
                    f"INSERT INTO {table}(market_day_id, {', '.join(BAR_COLUMNS)}) "
                    f"VALUES (?, {placeholders})",
                    (day_id, *values),
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

    def _accepted_bytes(self, workspace) -> dict[str, bytes]:
        return {
            symbol: (
                workspace["accepted"] / self.trade_date / f"{symbol}_{self.trade_date}.json"
            ).read_bytes()
            for symbol in PAIR
        }


if __name__ == "__main__":
    unittest.main()
