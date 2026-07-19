from __future__ import annotations

import csv
import io
import json
import unittest

from app.services.trade_exports import TradeExportError, render_trade_exports
from app.services.trade_records import build_trade_records_payload
from test_trade_records import day_fixture, registry_fixture


class TradeExportTests(unittest.TestCase):
    def _payload(self) -> dict:
        return build_trade_records_payload(registry_fixture(), day_fixture(), "SPY")

    def test_deterministic_json_and_three_csv_shapes(self) -> None:
        first = render_trade_exports(self._payload())
        second = render_trade_exports(self._payload())

        self.assertEqual(first, second)
        self.assertEqual(
            set(first),
            {
                "trade_records_spy_2026-07-17.json",
                "trade_groups.csv",
                "trade_legs.csv",
                "trade_events.csv",
            },
        )
        self.assertEqual(json.loads(first["trade_records_spy_2026-07-17.json"])["ticker"], "SPY")

    def test_csv_rows_and_foreign_keys_reconcile(self) -> None:
        bundle = render_trade_exports(self._payload())
        groups = list(csv.DictReader(io.StringIO(bundle["trade_groups.csv"])))
        legs = list(csv.DictReader(io.StringIO(bundle["trade_legs.csv"])))
        events = list(csv.DictReader(io.StringIO(bundle["trade_events.csv"])))

        self.assertEqual((len(groups), len(legs), len(events)), (1, 1, 1))
        self.assertEqual(legs[0]["trade_group_id"], groups[0]["trade_group_id"])
        self.assertEqual(events[0]["trade_group_id"], groups[0]["trade_group_id"])
        self.assertEqual(events[0]["leg_id"], legs[0]["leg_id"])
        self.assertEqual(groups[0]["display_eligible"], "true")
        self.assertEqual(events[0]["fees"], "")

    def test_private_and_raw_evidence_fields_are_absent(self) -> None:
        bundle = render_trade_exports(self._payload())
        combined = "\n".join(bundle.values())

        self.assertNotIn("source_path", combined)
        self.assertNotIn("source_index", combined)
        self.assertNotIn("screenshots", combined)
        self.assertNotIn("raw_chat", combined)

    def test_export_rejects_bars_or_raw_evidence_claim(self) -> None:
        payload = self._payload()
        payload["export_metadata"]["includes_bars"] = True
        with self.assertRaisesRegex(TradeExportError, "exclude bars"):
            render_trade_exports(payload)

    def test_export_rejects_duplicate_nested_ids(self) -> None:
        payload = self._payload()
        payload["trade_groups"].append(payload["trade_groups"][0])
        with self.assertRaisesRegex(TradeExportError, "duplicate leg ID"):
            render_trade_exports(payload)


if __name__ == "__main__":
    unittest.main()
