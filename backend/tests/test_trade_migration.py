from __future__ import annotations

import copy
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
# The exact trade dates accepted by the 2026-07-19 migration cutover. Canonical
# content grows past this set through daily publishes; it must never lose it.
CUTOVER_TRADE_DATES = frozenset({
    "2026-05-26", "2026-05-27", "2026-05-29", "2026-06-02", "2026-06-08",
    "2026-06-15", "2026-06-22", "2026-06-23", "2026-06-24", "2026-06-25",
    "2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02", "2026-07-07",
    "2026-07-08", "2026-07-09", "2026-07-10", "2026-07-14", "2026-07-15",
    "2026-07-16", "2026-07-17",
})
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
    def test_cutover_canonical_repository_preserves_migration_floor(self) -> None:
        registry = load_trader_registry(REPOSITORY_ROOT / "content" / "traders" / "index.json")
        days = validate_trade_repository(CANONICAL_DIR.glob("*.json"), registry)

        # The cutover accepted 22 days / 33 groups / 5 note contexts. Daily
        # publishes may only add on top; losing any cutover date or dropping
        # below the accepted totals means migration data was destroyed.
        self.assertLessEqual(CUTOVER_TRADE_DATES, {day["trade_date"] for day in days})
        self.assertGreaterEqual(len(days), len(CUTOVER_TRADE_DATES))
        self.assertGreaterEqual(sum(len(day["trade_groups"]) for day in days), 33)
        self.assertGreaterEqual(sum(len(day["note_contexts"]) for day in days), 5)
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
            # Projection counts must equal what canonical content actually
            # contains, both times, so growth never breaks this test while a
            # lossy or non-idempotent projection still does.
            derived = {
                "trade_groups": sum(len(day["trade_groups"]) for day in days),
                "trade_legs": sum(len(group["legs"]) for day in days for group in day["trade_groups"]),
                "trade_events": sum(
                    len(leg["events"])
                    for day in days
                    for group in day["trade_groups"]
                    for leg in group["legs"]
                ),
                "trade_note_contexts": sum(len(day["note_contexts"]) for day in days),
            }
            for report in (first_report, second_report):
                self.assertEqual({key: report["counts"][key] for key in derived}, derived)
            self.assertEqual(first_report["counts"], second_report["counts"])
            self.assertGreaterEqual(first_report["counts"]["trade_outcomes"], 7)
            self.assertEqual(first_report["logical_market_sha256"], baseline.logical_sha256)
            self.assertEqual(second_report["logical_market_sha256"], second_baseline.logical_sha256)


if __name__ == "__main__":
    unittest.main()
