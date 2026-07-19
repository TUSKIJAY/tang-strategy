from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from app.db import build_target_candidate, project_trade_repository
from app.services.trade_records import load_trader_registry, validate_trade_day, validate_trade_repository
from scripts.migrate_trader_trades import (
    classify_legacy_corpus,
    classify_legacy_note,
    legacy_trade_to_group,
    render_canonical_documents,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LEGACY_DIR = REPOSITORY_ROOT / "content" / "trader-trades"
TANG_REGISTRY = {
    "schema_version": "traders-v1",
    "traders": [
        {
            "trader_id": "tang",
            "display_name": "Tang",
            "color": "#E45756",
            "active": True,
            "sort_order": 10,
        }
    ],
}


class LegacyMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = classify_legacy_corpus(LEGACY_DIR.glob("*.json"))

    def test_complete_corpus_is_20_files_27_trades_and_2_day_contexts(self) -> None:
        self.assertEqual(self.result["source_files"], 20)
        self.assertEqual(self.result["trade_rows"], 27)
        self.assertEqual(self.result["day_context_rows"], 2)
        self.assertEqual(len(self.result["rows"]), 29)
        self.assertEqual(len(self.result["source_targets"]), 20)

    def test_allowlist_extracts_four_returns_and_three_approximate_exit_times(self) -> None:
        trade_rows = [row for row in self.result["rows"] if row["kind"] == "trade"]
        extracted = [row for row in trade_rows if row["reported_return_pct"] is not None]
        exit_times = [row for row in extracted if row["exit_time"] is not None]

        self.assertEqual([row["reported_return_pct"] for row in extracted], [50.0, 40.0, 40.0, 30.0])
        self.assertEqual([row["exit_time"] for row in exit_times], ["11:41", "14:07", "14:31"])
        self.assertTrue(all(row["exit_time_precision"] == "approximate" for row in exit_times))
        self.assertTrue(
            all(row["matched_rule"] == "allow_explicit_signed_result_with_result_verb" for row in extracted)
        )

    def test_position_size_is_denied_and_ambiguous_end_is_flagged(self) -> None:
        position = classify_legacy_note("10:45 put；35% 仓位。")
        ambiguous = classify_legacy_note("09:36 call；40% 结束。")

        self.assertIsNone(position["reported_return_pct"])
        self.assertEqual(position["non_extraction_reason"], "deny_position_size_percentage")
        self.assertFalse(position["review_required"])
        self.assertIsNone(ambiguous["reported_return_pct"])
        self.assertEqual(
            ambiguous["non_extraction_reason"],
            "review_ambiguous_unsigned_percentage_with_end_word",
        )
        self.assertEqual(ambiguous["review_flags"], ["ambiguous_exit_percentage"])
        self.assertTrue(ambiguous["review_required"])

    def test_every_generated_day_passes_pure_validation_with_repository_unique_ids(self) -> None:
        repository_ids: set[str] = set()
        validated = [
            validate_trade_day(day, TANG_REGISTRY, repository_ids=repository_ids)
            for day in self.result["days"]
        ]

        self.assertEqual(len(validated), 20)
        self.assertEqual(sum(len(day["trade_groups"]) for day in validated), 27)
        self.assertEqual(sum(len(day["note_contexts"]) for day in validated), 2)
        self.assertEqual(len(repository_ids), 27 + 27 + 30 + 2)

    def test_source_notes_and_declared_fields_are_preserved_in_report_rows(self) -> None:
        trade_rows = [row for row in self.result["rows"] if row["kind"] == "trade"]
        source_items = []
        for path in sorted(LEGACY_DIR.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            for index, trade in enumerate(payload["trades"]):
                source_items.append((path.relative_to(REPOSITORY_ROOT).as_posix(), index, trade))

        self.assertEqual(len(source_items), len(trade_rows))
        for (path, index, trade), row in zip(source_items, trade_rows, strict=True):
            self.assertEqual(row["source_path"], path)
            self.assertEqual(row["source_index"], index)
            self.assertEqual(row["source_time"], trade["time"])
            self.assertEqual(row["source_side"], trade["side"])
            self.assertEqual(row["source_strike"], trade["strike"])
            self.assertEqual(row["source_expiry"], trade["expiry"])
            self.assertEqual(row["source_action"], trade["action"])
            self.assertEqual(row["source_reason_type"], trade["reason_type"])
            self.assertEqual(row["source_note"], trade["note"])

    def test_day_contexts_distinguish_notes_with_trades_and_trades_empty_date(self) -> None:
        contexts = [row for row in self.result["rows"] if row["kind"] == "day_context"]
        self.assertEqual(
            [row["source_path"] for row in contexts],
            [
                "content/trader-trades/2026-05-26.json",
                "content/trader-trades/2026-05-29.json",
            ],
        )
        days = {day["trade_date"]: day for day in self.result["days"]}
        self.assertEqual(len(days["2026-05-26"]["trade_groups"]), 2)
        self.assertEqual(len(days["2026-05-26"]["note_contexts"]), 1)
        self.assertEqual(len(days["2026-05-29"]["trade_groups"]), 0)
        self.assertEqual(len(days["2026-05-29"]["note_contexts"]), 1)

    def test_legacy_ids_do_not_depend_on_mutable_trade_facts(self) -> None:
        source_path = LEGACY_DIR / "2026-06-08.json"
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        original = payload["trades"][0]
        modified = copy.deepcopy(original)
        modified["time"] = "12:00"
        modified["strike"] = 999
        modified["note"] = "Changed descriptive note."

        first, _ = legacy_trade_to_group(source_path, "2026-06-08", "SPY", 0, original)
        second, _ = legacy_trade_to_group(source_path, "2026-06-08", "SPY", 0, modified)

        self.assertEqual(first["trade_group_id"], second["trade_group_id"])
        self.assertEqual(first["legs"][0]["leg_id"], second["legs"][0]["leg_id"])
        self.assertEqual(first["legs"][0]["events"][0]["event_id"], second["legs"][0]["events"][0]["event_id"])

    def test_classification_is_idempotent(self) -> None:
        second = classify_legacy_corpus(LEGACY_DIR.glob("*.json"))
        self.assertEqual(
            json.dumps(self.result, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            json.dumps(second, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        )

    def test_canonical_repository_exactly_matches_pure_render(self) -> None:
        registry = load_trader_registry(REPOSITORY_ROOT / "content" / "traders" / "index.json")
        days = validate_trade_repository(
            (REPOSITORY_ROOT / "content" / "trades").glob("*.json"),
            registry,
        )
        expected = render_canonical_documents(self.result)
        actual = {
            relative: (REPOSITORY_ROOT / "content" / relative).read_text(encoding="utf-8")
            for relative in expected
        }

        self.assertEqual(actual, expected)
        self.assertEqual(len(days), 20)
        self.assertEqual(sum(len(day["trade_groups"]) for day in days), 27)
        self.assertEqual(sum(len(day["note_contexts"]) for day in days), 2)
        self.assertEqual(
            hashlib.sha256("".join(actual[key] for key in sorted(actual)).encode()).hexdigest(),
            "f22c5866cea04f39ec772b7542f75f06b1537bcae860668773dd7dd2da589a7e",
        )

    def test_canonical_projection_is_candidate_only_and_duplicate_safe(self) -> None:
        registry = load_trader_registry(REPOSITORY_ROOT / "content" / "traders" / "index.json")
        days = validate_trade_repository(
            (REPOSITORY_ROOT / "content" / "trades").glob("*.json"),
            registry,
        )
        live = REPOSITORY_ROOT / "data" / "sqlite" / "tang_strategy_live_extended.db"
        with tempfile.TemporaryDirectory() as raw_directory:
            candidate = Path(raw_directory) / "candidate.db"
            build_target_candidate(live, candidate)
            counts = project_trade_repository(candidate, registry, days)
            self.assertEqual(
                counts,
                {
                    "traders": 1,
                    "trade_groups": 27,
                    "trade_legs": 27,
                    "trade_events": 30,
                    "trade_outcomes": 4,
                    "trade_note_contexts": 2,
                },
            )
            with self.assertRaisesRegex(Exception, "duplicate|UNIQUE"):
                project_trade_repository(candidate, registry, days)


if __name__ == "__main__":
    unittest.main()
