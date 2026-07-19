from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from app.services.trade_records import (
    DAY_FIELDS,
    PUBLIC_CONTEXT_FIELDS,
    PUBLIC_GROUP_FIELDS,
    PUBLIC_TRADER_FIELDS,
    TradeValidationError,
    TradeAuthorizationError,
    assert_no_raw_evidence_fields,
    build_trade_records_payload,
    handle_trade_day_admin_write,
    handle_trade_records_read,
    handle_trader_registry_admin_write,
    occurred_at_from_local_time,
    validate_trade_day,
    validate_trader_registry,
)
from app.services.trade_statistics import calculate_long_premium_outcome


def registry_fixture() -> dict:
    return {
        "schema_version": "traders-v1",
        "traders": [
            {
                "trader_id": "alice",
                "display_name": "Alice",
                "color": "#3366CC",
                "active": True,
                "sort_order": 10,
            },
            {
                "trader_id": "bob",
                "display_name": "Bob",
                "color": "#DC3912",
                "active": True,
                "sort_order": 20,
            },
        ],
    }


def group_fixture(
    trade_date: str = "2026-07-17",
    trader_id: str = "alice",
    ticker: str = "SPY",
    suffix: str = "001",
) -> dict:
    group_id = f"tg_{trade_date.replace('-', '')}_{trader_id}_{ticker.lower()}_{suffix}"
    leg_id = f"{group_id}_l1"
    return {
        "trade_group_id": group_id,
        "trader_id": trader_id,
        "underlying": ticker,
        "trade_date": trade_date,
        "direction": "CALL",
        "status": "active",
        "review_status": "verified",
        "display_eligible": True,
        "reported_stats_eligible": False,
        "calculated_stats_eligible": False,
        "supersedes_trade_group_id": None,
        "legs": [
            {
                "leg_id": leg_id,
                "instrument_type": "option",
                "position_side": "long",
                "option_type": "CALL",
                "strike": None,
                "expiry": trade_date,
                "expiry_provenance": "rule_default",
                "contract_multiplier": 100,
                "contract_multiplier_provenance": "rule_default",
                "events": [
                    {
                        "event_id": f"{leg_id}_e1",
                        "sequence": 1,
                        "action": "buy_open",
                        "occurred_at": occurred_at_from_local_time(trade_date, "11:27"),
                        "time_precision": "minute",
                        "time_incomplete": False,
                        "premium": None,
                        "quantity": None,
                        "fees": None,
                        "note": None,
                        "fact_provenance": {
                            "occurred_at": "user_provided",
                            "premium": "unknown",
                            "quantity": "unknown",
                            "fees": "unknown",
                        },
                    }
                ],
            }
        ],
        "reported_outcome": None,
        "calculated_outcome": None,
        "result_conflict": False,
        "notes": [{"text": "Normalized public note.", "provenance": "user_provided"}],
        "normalization": {
            "method": "manual_normalization",
            "source": "manual_note",
            "source_path": None,
            "source_index": None,
            "review_flags": [],
        },
    }


def day_fixture(groups: list[dict] | None = None, trade_date: str = "2026-07-17") -> dict:
    return {
        "schema_version": "trades-day-v1",
        "trade_date": trade_date,
        "timezone": "America/New_York",
        "trade_groups": groups if groups is not None else [group_fixture(trade_date=trade_date)],
        "note_contexts": [],
    }


class TradeRecordValidationTests(unittest.TestCase):
    def test_unregistered_read_handler_filters_dates_roles_and_eligibility(self) -> None:
        root = Path(__file__).resolve().parents[2]
        content = root / "content"
        reported = handle_trade_records_read(
            "readonly",
            content,
            "SPY",
            trade_date="2026-06-08",
            eligibility="reported",
        )
        no_trade = handle_trade_records_read(
            "admin",
            content,
            "SPY",
            trade_date="2026-05-29",
        )
        date_range = handle_trade_records_read(
            "readonly",
            content,
            "SPY",
            date_from="2026-06-29",
            date_to="2026-07-02",
            statuses=["active"],
            review_statuses=["verified"],
        )

        self.assertEqual(len(reported), 1)
        self.assertEqual(reported[0]["counts"]["trade_groups_total"], 3)
        self.assertEqual(
            [group["reported_outcome"]["return_pct"] for group in reported[0]["trade_groups"]],
            [50.0, 40.0, 40.0],
        )
        self.assertEqual(no_trade[0]["counts"]["trade_groups_total"], 0)
        self.assertEqual(no_trade[0]["counts"]["note_contexts_total"], 1)
        self.assertEqual(
            [payload["trade_date"] for payload in date_range],
            ["2026-06-29", "2026-06-30", "2026-07-01", "2026-07-02"],
        )
        with self.assertRaises(TradeAuthorizationError):
            handle_trade_records_read("anonymous", content, "SPY", trade_date="2026-07-17")

    def test_admin_handlers_validate_repository_and_replace_atomically(self) -> None:
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as raw_directory:
            content = Path(raw_directory) / "content"
            shutil.copytree(root / "content" / "traders", content / "traders")
            shutil.copytree(root / "content" / "trades", content / "trades")
            target = content / "trades" / "2026-07-17.json"
            original = target.read_bytes()
            day = json.loads(original)
            day["trade_groups"][0]["notes"].append(
                {"text": "Atomic admin fixture.", "provenance": "user_provided"}
            )

            with self.assertRaises(TradeAuthorizationError):
                handle_trade_day_admin_write("readonly", content, day)
            self.assertEqual(target.read_bytes(), original)

            def fail_replace(*_: object) -> None:
                raise OSError("forced replace failure")

            with self.assertRaisesRegex(OSError, "forced replace failure"):
                handle_trade_day_admin_write("admin", content, day, replace=fail_replace)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(target.parent.glob(".*.candidate")), [])

            def fail_projection() -> None:
                raise RuntimeError("forced projection failure")

            with self.assertRaisesRegex(RuntimeError, "forced projection failure"):
                handle_trade_day_admin_write(
                    "admin",
                    content,
                    day,
                    after_replace=fail_projection,
                )
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(target.parent.glob(".*.rollback")), [])

            report = handle_trade_day_admin_write("admin", content, day)
            self.assertEqual(report["trade_groups"], 1)
            self.assertIn("Atomic admin fixture.", target.read_text(encoding="utf-8"))

            registry = json.loads(
                (content / "traders" / "index.json").read_text(encoding="utf-8")
            )
            registry["traders"].append(
                {
                    "trader_id": "alice",
                    "display_name": "Alice",
                    "color": "#3366CC",
                    "active": True,
                    "sort_order": 20,
                }
            )
            registry_report = handle_trader_registry_admin_write("admin", content, registry)
            self.assertEqual(registry_report["traders"], 2)

    def test_phase_6_routes_are_registered_without_legacy_compatibility(self) -> None:
        from app.main import app

        paths = {route.path for route in app.routes}
        self.assertTrue({
            "/api/trade-records",
            "/api/admin/traders",
            "/api/admin/trade-records",
        }.issubset(paths))
        self.assertFalse(any("tang-trade" in path for path in paths))
        importer_source = (
            Path(__file__).resolve().parents[1] / "app" / "services" / "importer.py"
        ).read_text(encoding="utf-8")
        self.assertIn("replace_trade_repository(settings.db_path", importer_source)
        self.assertNotIn("project_trade_repository(settings.db_path", importer_source)

    def test_machine_readable_schemas_are_valid_json_and_freeze_top_level(self) -> None:
        root = Path(__file__).resolve().parents[2]
        traders = json.loads(
            (root / "content/schemas/traders.schema.json").read_text(encoding="utf-8")
        )
        day = json.loads(
            (root / "content/schemas/trades-day.schema.json").read_text(encoding="utf-8")
        )

        self.assertEqual(traders["properties"]["schema_version"]["const"], "traders-v1")
        self.assertEqual(set(day["required"]), DAY_FIELDS)
        self.assertFalse(day["additionalProperties"])

    def test_valid_spy_dst_and_qqq_standard_time_records(self) -> None:
        spy = validate_trade_day(day_fixture(), registry_fixture())
        qqq_group = group_fixture(
            trade_date="2026-01-15", trader_id="bob", ticker="QQQ", suffix="001"
        )
        qqq_group["legs"][0]["events"][0]["occurred_at"] = occurred_at_from_local_time(
            "2026-01-15", "10:05"
        )
        qqq = validate_trade_day(day_fixture([qqq_group], "2026-01-15"), registry_fixture())

        self.assertTrue(spy["trade_groups"][0]["legs"][0]["events"][0]["occurred_at"].endswith("-04:00"))
        self.assertTrue(qqq["trade_groups"][0]["legs"][0]["events"][0]["occurred_at"].endswith("-05:00"))

    def test_rule_defaults_expiry_and_multiplier_without_inference(self) -> None:
        day = day_fixture()
        leg = day["trade_groups"][0]["legs"][0]
        leg["expiry"] = None
        leg.pop("expiry_provenance")
        leg["contract_multiplier"] = None
        leg.pop("contract_multiplier_provenance")

        validated = validate_trade_day(day, registry_fixture())
        normalized_leg = validated["trade_groups"][0]["legs"][0]
        self.assertEqual(normalized_leg["expiry"], "2026-07-17")
        self.assertEqual(normalized_leg["expiry_provenance"], "rule_default")
        self.assertEqual(normalized_leg["contract_multiplier"], 100)
        self.assertEqual(normalized_leg["contract_multiplier_provenance"], "rule_default")
        self.assertIsNone(normalized_leg["events"][0]["premium"])
        self.assertIsNone(normalized_leg["events"][0]["fees"])

    def test_offset_mismatch_fails_closed(self) -> None:
        day = day_fixture()
        day["trade_groups"][0]["legs"][0]["events"][0]["occurred_at"] = (
            "2026-07-17T11:27:00-05:00"
        )
        with self.assertRaisesRegex(TradeValidationError, "offset does not match"):
            validate_trade_day(day, registry_fixture())

    def test_explicitly_incomplete_time_is_displayable_but_not_calculated(self) -> None:
        day = day_fixture()
        event = day["trade_groups"][0]["legs"][0]["events"][0]
        event["occurred_at"] = None
        event["time_precision"] = None
        event["time_incomplete"] = True

        validated = validate_trade_day(day, registry_fixture())
        group = validated["trade_groups"][0]
        self.assertTrue(group["display_eligible"])
        self.assertFalse(group["calculated_stats_eligible"])

    def test_duplicate_stable_id_rejected_across_days(self) -> None:
        seen: set[str] = set()
        validate_trade_day(day_fixture(), registry_fixture(), repository_ids=seen)
        with self.assertRaisesRegex(TradeValidationError, "duplicate stable ID"):
            validate_trade_day(day_fixture(), registry_fixture(), repository_ids=seen)

    def test_voided_or_superseded_record_cannot_remain_eligible(self) -> None:
        day = day_fixture()
        group = day["trade_groups"][0]
        group["status"] = "voided"
        with self.assertRaisesRegex(TradeValidationError, "cannot remain eligible"):
            validate_trade_day(day, registry_fixture())

    def test_reported_and_calculated_conflict_is_explicit(self) -> None:
        day = day_fixture()
        group = day["trade_groups"][0]
        leg = group["legs"][0]
        entry = leg["events"][0]
        entry["premium"] = 1.0
        entry["quantity"] = 1
        entry["fees"] = 0.0
        leg["events"].append(
            {
                "event_id": f"{leg['leg_id']}_e2",
                "sequence": 2,
                "action": "sell_close",
                "occurred_at": occurred_at_from_local_time("2026-07-17", "11:40"),
                "time_precision": "minute",
                "time_incomplete": False,
                "premium": 1.5,
                "quantity": 1,
                "fees": 0.0,
                "note": None,
                "fact_provenance": {"premium": "user_provided", "quantity": "user_provided"},
            }
        )
        group["calculated_outcome"] = calculate_long_premium_outcome(group)
        group["calculated_stats_eligible"] = True
        group["reported_outcome"] = {
            "return_pct": 40.0,
            "gross_pnl": None,
            "net_pnl": None,
            "provenance": "user_provided",
            "note": None,
        }
        group["reported_stats_eligible"] = True
        group["result_conflict"] = True

        validated = validate_trade_day(day, registry_fixture())
        self.assertEqual(validated["trade_groups"][0]["calculated_outcome"]["return_pct"], 50.0)
        self.assertTrue(validated["trade_groups"][0]["result_conflict"])

    def test_calculated_eligibility_rejects_incomplete_fills(self) -> None:
        day = day_fixture()
        group = day["trade_groups"][0]
        group["calculated_stats_eligible"] = True
        group["calculated_outcome"] = {
            "return_pct": 1.0,
            "gross_pnl": 1.0,
            "net_pnl": None,
            "closed_quantity": 1.0,
            "average_entry_premium": 1.0,
            "average_exit_premium": 1.01,
            "calculation_version": "long-premium-v1",
        }
        with self.assertRaisesRegex(TradeValidationError, "fully closed complete fills"):
            validate_trade_day(day, registry_fixture())

    def test_raw_evidence_fields_fail_closed_recursively(self) -> None:
        with self.assertRaisesRegex(TradeValidationError, "raw evidence fields are forbidden"):
            assert_no_raw_evidence_fields({"nested": {"screenshots": ["raw"]}})

    def test_trader_registry_rejects_duplicate_identity_color_and_order(self) -> None:
        registry = registry_fixture()
        registry["traders"][1]["trader_id"] = "alice"
        with self.assertRaisesRegex(TradeValidationError, "duplicate trader ID"):
            validate_trader_registry(registry)

    def test_public_payload_has_exact_allowlisted_shape_and_private_fields_absent(self) -> None:
        day = day_fixture()
        day["note_contexts"] = [
            {
                "context_id": "ctx_20260717_alice_spy_001",
                "trader_id": "alice",
                "underlying": "SPY",
                "trade_date": "2026-07-17",
                "text": "Public normalized context.",
                "status": "active",
                "review_status": "verified",
                "normalization": {
                    "method": "manual_normalization",
                    "source": "manual_note",
                    "source_path": "/private/source/path",
                    "source_index": 0,
                    "review_flags": [],
                },
            }
        ]
        payload = build_trade_records_payload(registry_fixture(), day, "spy")

        self.assertEqual(
            set(payload),
            {
                "schema_version",
                "ticker",
                "trade_date",
                "traders",
                "trade_groups",
                "note_contexts",
                "counts",
                "export_metadata",
            },
        )
        self.assertEqual(set(payload["traders"][0]), set(PUBLIC_TRADER_FIELDS))
        self.assertEqual(set(payload["trade_groups"][0]), set(PUBLIC_GROUP_FIELDS) | {"normalization_method"})
        self.assertEqual(set(payload["note_contexts"][0]), set(PUBLIC_CONTEXT_FIELDS) | {"normalization_method"})
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        self.assertNotIn("source_path", serialized)
        self.assertNotIn("source_index", serialized)
        self.assertEqual(payload["counts"]["trade_groups_total"], 1)
        self.assertFalse(payload["export_metadata"]["includes_bars"])

    def test_public_payload_rejects_unknown_trader_filter(self) -> None:
        with self.assertRaisesRegex(TradeValidationError, "unknown trader ID"):
            build_trade_records_payload(
                registry_fixture(), day_fixture(), "SPY", trader_ids=["missing"]
            )

    def test_round_trip_json_is_deterministic(self) -> None:
        validated = validate_trade_day(day_fixture(), registry_fixture())
        first = json.dumps(validated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        second = json.dumps(json.loads(first), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        self.assertEqual(first, second)

    def test_loader_rejects_invalid_top_level_json_shape(self) -> None:
        with tempfile.TemporaryDirectory() as raw_directory:
            path = Path(raw_directory) / "bad.json"
            path.write_text("[]", encoding="utf-8")
            from app.services.trade_records import load_trade_day

            with self.assertRaisesRegex(TradeValidationError, "top-level JSON value"):
                load_trade_day(path, registry_fixture())


if __name__ == "__main__":
    unittest.main()
