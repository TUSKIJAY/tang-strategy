from __future__ import annotations

import copy
import unittest

from app.services.trade_statistics import (
    TradeCalculationError,
    calculate_long_premium_outcome,
    outcome_conflict,
    summarize_trade_groups,
)


def calculation_group() -> dict:
    return {
        "legs": [
            {
                "instrument_type": "option",
                "position_side": "long",
                "contract_multiplier": 100,
                "events": [
                    {"sequence": 1, "action": "buy_open", "premium": 1.0, "quantity": 2, "fees": 0.0},
                    {"sequence": 2, "action": "buy_add", "premium": 2.0, "quantity": 1, "fees": 0.0},
                    {"sequence": 3, "action": "sell_partial", "premium": 3.0, "quantity": 1, "fees": 0.0},
                    {"sequence": 4, "action": "sell_close", "premium": 2.0, "quantity": 2, "fees": 0.0},
                ],
            }
        ]
    }


class TradeStatisticsTests(unittest.TestCase):
    def test_weighted_average_add_and_partial_close(self) -> None:
        outcome = calculate_long_premium_outcome(calculation_group())

        self.assertIsNotNone(outcome)
        self.assertAlmostEqual(outcome["average_entry_premium"], 4 / 3)
        self.assertAlmostEqual(outcome["average_exit_premium"], 7 / 3)
        self.assertAlmostEqual(outcome["gross_pnl"], 300.0)
        self.assertAlmostEqual(outcome["return_pct"], 75.0)
        self.assertAlmostEqual(outcome["net_pnl"], 300.0)

    def test_unknown_fee_preserves_gross_and_nulls_net(self) -> None:
        group = calculation_group()
        group["legs"][0]["events"][2]["fees"] = None
        outcome = calculate_long_premium_outcome(group)

        self.assertAlmostEqual(outcome["gross_pnl"], 300.0)
        self.assertIsNone(outcome["net_pnl"])

    def test_partial_open_and_missing_fill_are_not_calculated(self) -> None:
        partial = calculation_group()
        partial["legs"][0]["events"].pop()
        missing = calculation_group()
        missing["legs"][0]["events"][0]["quantity"] = None

        self.assertIsNone(calculate_long_premium_outcome(partial))
        self.assertIsNone(calculate_long_premium_outcome(missing))

    def test_oversell_and_wrong_final_action_fail_closed(self) -> None:
        oversell = calculation_group()
        oversell["legs"][0]["events"][-1]["quantity"] = 3
        with self.assertRaisesRegex(TradeCalculationError, "exceeds"):
            calculate_long_premium_outcome(oversell)

        wrong_final = calculation_group()
        wrong_final["legs"][0]["events"][-1]["action"] = "sell_partial"
        with self.assertRaisesRegex(TradeCalculationError, "final closing event"):
            calculate_long_premium_outcome(wrong_final)

    def test_reported_and_calculated_summaries_never_mix(self) -> None:
        groups = [
            {
                "reported_stats_eligible": True,
                "reported_outcome": {"return_pct": 40.0},
                "calculated_stats_eligible": False,
                "calculated_outcome": None,
                "result_conflict": False,
            },
            {
                "reported_stats_eligible": False,
                "reported_outcome": None,
                "calculated_stats_eligible": True,
                "calculated_outcome": {"return_pct": -10.0},
                "result_conflict": False,
            },
        ]
        summary = summarize_trade_groups(groups)

        self.assertEqual(summary["reported"]["eligible_count"], 1)
        self.assertEqual(summary["reported"]["average_return_pct"], 40.0)
        self.assertEqual(summary["calculated"]["eligible_count"], 1)
        self.assertEqual(summary["calculated"]["average_return_pct"], -10.0)

    def test_conflict_uses_two_decimal_display_rounding(self) -> None:
        self.assertFalse(outcome_conflict({"return_pct": 40.004}, {"return_pct": 40.003}))
        self.assertTrue(outcome_conflict({"return_pct": 40.01}, {"return_pct": 40.02}))


if __name__ == "__main__":
    unittest.main()
