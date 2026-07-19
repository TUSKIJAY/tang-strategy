from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from app.db import build_target_candidate
from app.services.trade_records import load_trader_registry, validate_trade_repository
from scripts.migrate_trader_trades import (
    classify_legacy_corpus,
    classify_legacy_note,
    legacy_trade_to_group,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CANONICAL_DIR = REPOSITORY_ROOT / "content" / "trades"
MIGRATION_EVIDENCE = (
    REPOSITORY_ROOT
    / "docs"
    / "exec-plans"
    / "reviews"
    / "2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan"
    / "evidence"
    / "legacy-migration-report.md"
)


class LegacyMigrationTests(unittest.TestCase):
    def test_cutover_canonical_repository_preserves_22_33_5_acceptance(self) -> None:
        registry = load_trader_registry(REPOSITORY_ROOT / "content" / "traders" / "index.json")
        days = validate_trade_repository(CANONICAL_DIR.glob("*.json"), registry)
        serialized = {
            path.relative_to(REPOSITORY_ROOT / "content").as_posix(): path.read_text(encoding="utf-8")
            for path in sorted(CANONICAL_DIR.glob("*.json"))
        }
        registry_path = REPOSITORY_ROOT / "content" / "traders" / "index.json"
        serialized["traders/index.json"] = registry_path.read_text(encoding="utf-8")

        self.assertEqual(len(days), 22)
        self.assertEqual(sum(len(day["trade_groups"]) for day in days), 33)
        self.assertEqual(sum(len(day["note_contexts"]) for day in days), 5)
        self.assertEqual(
            hashlib.sha256("".join(serialized[key] for key in sorted(serialized)).encode()).hexdigest(),
            "58783cfe888f6f922810eceb6a402ef0a002646d91830acb6476e3db371512ec",
        )
        evidence = MIGRATION_EVIDENCE.read_text(encoding="utf-8")
        self.assertIn("- Source files: `20`", evidence)
        self.assertIn("- Classified trade rows: `27`", evidence)
        self.assertIn("- Classified day-context rows: `2`", evidence)

    def test_allowlist_and_deny_rules_remain_pinned_after_source_removal(self) -> None:
        extracted = classify_legacy_note("11:41 附近反馈 +50% 止盈出场")
        position = classify_legacy_note("10:45 put；35% 仓位。")
        ambiguous = classify_legacy_note("09:36 call；40% 结束。")

        self.assertEqual(extracted["reported_return_pct"], 50.0)
        self.assertEqual(extracted["exit_time"], "11:41")
        self.assertEqual(extracted["exit_time_precision"], "approximate")
        self.assertIsNone(position["reported_return_pct"])
        self.assertEqual(position["non_extraction_reason"], "deny_position_size_percentage")
        self.assertIsNone(ambiguous["reported_return_pct"])
        self.assertEqual(ambiguous["review_flags"], ["ambiguous_exit_percentage"])

    def test_legacy_ids_do_not_depend_on_mutable_trade_facts(self) -> None:
        source_path = Path("content/trader-trades/2026-06-08.json")
        original = {
            "time": "09:36",
            "side": "CALL",
            "strike": 600,
            "expiry": "2026-06-08",
            "action": "buy_open",
            "source": "historical_record",
            "reason_type": "explicit_note",
            "note": "11:41 附近反馈 +50% 止盈出场",
        }
        modified = copy.deepcopy(original)
        modified.update({"time": "12:00", "strike": 999, "note": "Changed descriptive note."})

        first, _ = legacy_trade_to_group(source_path, "2026-06-08", "SPY", 0, original)
        second, _ = legacy_trade_to_group(source_path, "2026-06-08", "SPY", 0, modified)

        self.assertEqual(first["trade_group_id"], second["trade_group_id"])
        self.assertEqual(first["legs"][0]["leg_id"], second["legs"][0]["leg_id"])
        self.assertEqual(first["legs"][0]["events"][0]["event_id"], second["legs"][0]["events"][0]["event_id"])

    def test_inline_legacy_classification_is_idempotent_without_tracked_legacy_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            source = Path(raw_directory) / "2026-07-17.json"
            source.write_text(
                json.dumps({
                    "date": "2026-07-17",
                    "ticker": "SPY",
                    "trades": [{
                        "time": "09:36",
                        "side": "CALL",
                        "strike": None,
                        "expiry": "2026-07-17",
                        "action": "buy_open",
                        "source": "historical_record",
                        "reason_type": "unknown",
                        "note": "strategy aligned",
                    }],
                    "notes": [],
                }),
                encoding="utf-8",
            )
            first = classify_legacy_corpus([source])
            second = classify_legacy_corpus([source])
            self.assertEqual(first, second)
            self.assertEqual((first["source_files"], first["trade_rows"]), (1, 1))

    def test_canonical_projection_is_idempotent_on_old_or_target_live_db(self) -> None:
        registry = load_trader_registry(REPOSITORY_ROOT / "content" / "traders" / "index.json")
        days = validate_trade_repository(CANONICAL_DIR.glob("*.json"), registry)
        live = REPOSITORY_ROOT / "data" / "sqlite" / "tang_strategy_live_extended.db"
        with tempfile.TemporaryDirectory() as raw_directory:
            first = Path(raw_directory) / "first.db"
            second = Path(raw_directory) / "second.db"
            baseline, first_report = build_target_candidate(live, first, registry, days)
            second_baseline, second_report = build_target_candidate(first, second, registry, days)
            expected = {
                "traders": 2,
                "trade_groups": 33,
                "trade_legs": 33,
                "trade_events": 46,
                "trade_outcomes": 7,
                "trade_note_contexts": 5,
            }
            self.assertEqual(
                {key: first_report["counts"][key] for key in expected},
                expected,
            )
            self.assertEqual(
                {key: second_report["counts"][key] for key in expected},
                expected,
            )
            self.assertEqual(first_report["logical_market_sha256"], baseline.logical_sha256)
            self.assertEqual(second_report["logical_market_sha256"], second_baseline.logical_sha256)


if __name__ == "__main__":
    unittest.main()
