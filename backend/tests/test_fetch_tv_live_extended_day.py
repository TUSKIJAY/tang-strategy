from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from scripts.fetch_tv_live_extended_day import (
    expected_bar_times,
    market_session,
    validate_source_rows,
)


ET = ZoneInfo("America/New_York")


def make_rows(trade_date: date) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    cursor = datetime.combine(trade_date, datetime.min.time(), tzinfo=ET).replace(hour=4)
    while cursor < datetime.combine(trade_date, datetime.min.time(), tzinfo=ET).replace(hour=20):
        rows.append(
            {
                "ts": cursor.isoformat(),
                "t": cursor.strftime("%H:%M"),
                "O": 100.0,
                "H": 101.0,
                "L": 99.0,
                "C": 100.5,
                "V": 10.0,
                "vw": 100.0,
            }
        )
        cursor += timedelta(minutes=1)
    return rows


class TradingViewQualityGateTests(unittest.TestCase):
    def test_market_calendar_resolves_normal_early_close_and_holiday(self) -> None:
        normal_open, normal_close = market_session(date(2026, 7, 14))
        early_open, early_close = market_session(date(2026, 11, 27))

        self.assertEqual(
            (normal_open.strftime("%H:%M"), normal_close.strftime("%H:%M")),
            ("09:30", "16:00"),
        )
        self.assertEqual(
            (early_open.strftime("%H:%M"), early_close.strftime("%H:%M")),
            ("09:30", "13:00"),
        )
        with self.assertRaisesRegex(RuntimeError, "not a NYSE trading day"):
            market_session(date(2026, 7, 3))

    def test_expected_times_support_normal_and_early_close_sessions(self) -> None:
        trade_date = date(2026, 7, 14)
        normal_open = datetime(2026, 7, 14, 9, 30, tzinfo=ET)
        normal_close = datetime(2026, 7, 14, 16, 0, tzinfo=ET)
        early_close = datetime(2026, 7, 14, 13, 0, tzinfo=ET)

        self.assertEqual(len(expected_bar_times(normal_open, normal_close, 1)), 390)
        self.assertEqual(len(expected_bar_times(normal_open, normal_close, 5)), 78)
        self.assertEqual(len(expected_bar_times(normal_open, early_close, 1)), 210)
        self.assertEqual(len(expected_bar_times(normal_open, early_close, 5)), 42)

    def test_sparse_extended_session_passes_when_rth_is_complete(self) -> None:
        trade_date = date(2026, 7, 14)
        market_open = datetime(2026, 7, 14, 9, 30, tzinfo=ET)
        market_close = datetime(2026, 7, 14, 16, 0, tzinfo=ET)
        rows = make_rows(trade_date)
        rows = [
            row
            for row in rows
            if market_open.strftime("%H:%M") <= str(row["t"]) < market_close.strftime("%H:%M")
            or str(row["t"]) in {"04:00", "08:00", "16:00", "19:59"}
        ]

        rth = validate_source_rows(rows, trade_date, market_open, market_close)

        self.assertEqual(len(rth), 390)
        self.assertEqual(len(rows), 394)

    def test_missing_rth_minute_fails_hard_gate(self) -> None:
        trade_date = date(2026, 7, 14)
        market_open = datetime(2026, 7, 14, 9, 30, tzinfo=ET)
        market_close = datetime(2026, 7, 14, 16, 0, tzinfo=ET)
        rows = make_rows(trade_date)
        rows = [row for row in rows if row["t"] != "10:00"]

        with self.assertRaisesRegex(RuntimeError, "RTH count=389"):
            validate_source_rows(rows, trade_date, market_open, market_close)


if __name__ == "__main__":
    unittest.main()
