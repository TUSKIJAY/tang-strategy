from __future__ import annotations

import copy
import contextlib
import hashlib
import json
import tempfile
import unittest
import sqlite3
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.services.ibkr_mcp import ET, build_payload, load_package


class McpPackageTests(unittest.TestCase):
    """Synthetic input exercises rejection; it is never published as market data."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.target = "2026-11-02"
        self.manifest = {"schema_version": 1, "trade_date": self.target, "provider": "ibkr_mcp", "contracts": [], "responses": []}
        self.data = {}
        for symbol, contract in (("SPY", 756733), ("QQQ", 320227571)):
            self.manifest["contracts"].append({"symbol": symbol, "country_code": "US", "underlying_contract_id": contract, "sections": [{"security_type": "STK"}]})
            start = datetime(2026, 11, 2, 4, tzinfo=ET)
            minute = [{"time": (start + timedelta(minutes=i)).astimezone(timezone.utc).isoformat(), "open": 100 + i / 100, "high": 100.1 + i / 100, "low": 99.9 + i / 100, "close": 100 + i / 100, "volume": 10} for i in range(960)]
            for step, seconds in (("ONE_MIN", 60), ("FIVE_MINS", 300)):
                rows = minute if seconds == 60 else [{"time": minute[i]["time"], "open": minute[i]["open"], "high": max(r["high"] for r in minute[i:i + 5]), "low": min(r["low"] for r in minute[i:i + 5]), "close": minute[i + 4]["close"], "volume": 50} for i in range(0, 960, 5)]
                data = {"chart_step": seconds, "source": "Last", **{key: [r[key] for r in rows] for key in ("time", "open", "high", "low", "close", "volume")}}
                name = f"{symbol}_{step}.json"
                self.data[name] = {"structuredContent": data, "content": [{"type": "text", "text": json.dumps(data)}], "isError": False}
                self.manifest["responses"].append({"symbol": symbol, "tool": "interactive_brokers_ibkr_get_price_history", "file": name, "request": {"contract_id": contract, "security_type": "STK", "outside_rth": True, "period": "TWO_DAYS", "step": step}})

    def save(self):
        for entry in self.manifest["responses"]:
            raw = self.data[entry["file"]]
            if raw.get("structuredContent") is not None:
                raw["content"][0]["text"] = json.dumps(raw["structuredContent"])
            blob = json.dumps(raw).encode()
            (self.root / entry["file"]).write_bytes(blob)
            entry["sha256"] = hashlib.sha256(blob).hexdigest()
        blob = json.dumps(self.manifest).encode()
        (self.root / "manifest.json").write_bytes(blob)
        return hashlib.sha256(blob).hexdigest()

    def load(self):
        return load_package(self.root, self.save(), self.target, now=datetime(2026, 11, 3, tzinfo=timezone.utc))

    def test_valid_native_bars_and_computed_fields(self):
        package = self.load()
        payload = build_payload("SPY", package, {"1m": [80] * 249, "5m": [80] * 249}, [{"provider": "tradingview", "date": "2026-10-30"}])
        self.assertEqual((len(payload["bars_1m"]), len(payload["bars_5m"])), (960, 192))
        self.assertTrue(payload["bars_1m"][0]["ts"].endswith("-05:00"))
        self.assertEqual(payload["bars_5m"][0]["vw"], payload["bars_1m"][4]["vw"])
        self.assertAlmostEqual(payload["bars_1m"][0]["m250"], (249 * 80 + 100) / 250)
        self.assertEqual(payload["meta"]["provider"], "ibkr_mcp")
        self.assertTrue(payload["meta"]["ibkr_mcp"]["warmup_may_use_other_providers"])

    def test_rejects_invalid_numbers_order_and_rth_gaps(self):
        original = copy.deepcopy(self.data)
        for kind in ("negative_volume", "bool", "nan", "envelope", "duplicate", "reverse", "missing", "wrong_step"):
            with self.subTest(kind=kind):
                self.data = copy.deepcopy(original)
                d = self.data["SPY_ONE_MIN.json"]["structuredContent"]
                if kind == "negative_volume": d["volume"][400] = -1
                if kind == "bool": d["open"][400] = True
                if kind == "nan": d["open"][400] = float("nan")
                if kind == "envelope": d["high"][400] = 1
                if kind == "duplicate": d["time"][400] = d["time"][399]
                if kind == "reverse": d["time"][400], d["time"][401] = d["time"][401], d["time"][400]
                if kind == "missing":
                    for key in ("time", "open", "high", "low", "close", "volume"): d[key].pop(400)
                if kind == "wrong_step": d["chart_step"] = 300
                with self.assertRaises(ValueError): self.load()

    def test_rejects_digest_and_dual_response_conflict(self):
        sha = self.save()
        raw = self.data["SPY_ONE_MIN.json"]
        raw["content"][0]["text"] = "{}"
        blob = json.dumps(raw).encode()
        path = self.root / "SPY_ONE_MIN.json"
        path.write_bytes(blob)
        with self.assertRaisesRegex(ValueError, "digest"): load_package(self.root, sha, self.target)
        self.manifest["responses"][0]["sha256"] = hashlib.sha256(blob).hexdigest()
        blob = json.dumps(self.manifest).encode()
        (self.root / "manifest.json").write_bytes(blob)
        with self.assertRaisesRegex(ValueError, "disagree"): load_package(self.root, hashlib.sha256(blob).hexdigest(), self.target)

    def test_missing_contract_response_date_or_future_session(self):
        baseline = copy.deepcopy(self.manifest)
        for kind in ("contract", "response", "date", "future"):
            with self.subTest(kind=kind):
                self.manifest = copy.deepcopy(baseline)
                if kind == "contract": self.manifest["contracts"][0]["country_code"] = "MX"
                if kind == "response": self.manifest["responses"].pop()
                if kind == "date": self.manifest["trade_date"] = "2026-10-30"
                sha = self.save()
                with self.assertRaises(ValueError):
                    load_package(self.root, sha, self.target, now=datetime(2026, 11, 2, 12, tzinfo=timezone.utc) if kind == "future" else None)

    def test_path_escape_symlink_and_sensitive_fields(self):
        sha = self.save()
        path = self.root / "SPY_ONE_MIN.json"
        path.rename(self.root / "original.json")
        path.symlink_to(self.root / "original.json")
        with self.assertRaisesRegex(ValueError, "regular"): load_package(self.root, sha, self.target)
        path.unlink()
        self.data["SPY_ONE_MIN.json"]["access_token"] = "synthetic-secret"
        with self.assertRaisesRegex(ValueError, "forbidden"): self.load()
        self.data["SPY_ONE_MIN.json"].pop("access_token")
        self.manifest["responses"][0]["file"] = "../escape.json"
        blob = json.dumps(self.manifest).encode(); (self.root / "manifest.json").write_bytes(blob)
        with self.assertRaisesRegex(ValueError, "escape"): load_package(self.root, hashlib.sha256(blob).hexdigest(), self.target)

    def test_zero_volume_carry_explains_native_difference(self):
        for symbol in ("SPY", "QQQ"):
            minute = self.data[f"{symbol}_ONE_MIN.json"]["structuredContent"]
            # Start of a bucket: native OHLC ignores the carried zero-volume price.
            i = 5
            for key in ("open", "high", "low", "close"): minute[key][i] = minute["close"][i - 1]
            minute["volume"][i] = 0
            five = self.data[f"{symbol}_FIVE_MINS.json"]["structuredContent"]
            five["open"][1] = minute["open"][6]
            five["low"][1] = min(minute["low"][6:10])
            five["volume"][1] = 40
        package = self.load()
        self.assertEqual(package["quality"]["SPY"]["zero_volume_minutes"], ["04:05"])
        self.assertEqual(package["quality"]["SPY"]["positive_volume_comparison"], "pass")

    def test_calendar_early_close_and_summer_offset(self):
        original = copy.deepcopy(self.data)
        for day, expected, offset in (("2026-11-27", 210, "-05:00"), ("2026-10-30", 390, "-04:00")):
            with self.subTest(day=day):
                self.data = copy.deepcopy(original)
                self.target = day
                self.manifest["trade_date"] = day
                for raw in self.data.values():
                    d = raw["structuredContent"]
                    d["time"] = [datetime.combine(datetime.fromisoformat(day).date(), datetime.fromisoformat(t).astimezone(ET).time().replace(tzinfo=None), tzinfo=ET).astimezone(timezone.utc).isoformat() for t in d["time"]]
                package = load_package(self.root, self.save(), day, now=datetime(2026, 11, 28, tzinfo=timezone.utc))
                payload = build_payload("SPY", package)
                self.assertEqual(payload["meta"]["quality"]["rth_1m_expected"], expected)
                self.assertEqual(payload["meta"]["quality"]["rth_5m_expected"], expected // 5)
                self.assertTrue(payload["bars_1m"][0]["ts"].endswith(offset))

    def test_unexplained_five_minute_difference_refused(self):
        self.data["SPY_FIVE_MINS.json"]["structuredContent"]["high"][80] += 1
        with self.assertRaisesRegex(ValueError, "unexplained"): self.load()

    def test_all_zero_bucket_is_reported_and_initial_vwap_is_null(self):
        for symbol in ("SPY", "QQQ"):
            m = self.data[f"{symbol}_ONE_MIN.json"]["structuredContent"]
            f = self.data[f"{symbol}_FIVE_MINS.json"]["structuredContent"]
            for i in range(5):
                for key in ("open", "high", "low", "close"): m[key][i] = 100
                m["volume"][i] = 0
            for key in ("open", "high", "low", "close"): f[key][0] = 100
            f["volume"][0] = 0
        package = self.load()
        self.assertEqual(package["quality"]["SPY"]["all_zero_buckets"], ["04:00"])
        payload = build_payload("SPY", package)
        self.assertIsNone(payload["bars_1m"][0]["vw"])
        self.assertIsNone(payload["bars_5m"][0]["vw"])
        self.assertIsNotNone(payload["bars_1m"][5]["vw"])

    def test_entry_point_refuses_existing_or_partial_day_before_import(self):
        from scripts.accept_ibkr_mcp_package import accept_package
        db = self.root / "existing.db"
        with contextlib.closing(sqlite3.connect(db)) as conn, conn:
            conn.execute("CREATE TABLE market_days(ticker TEXT, trade_date TEXT, session_mode TEXT)")
            conn.execute("INSERT INTO market_days VALUES('SPY', ?, 'extended')", (self.target,))
        with mock.patch("scripts.accept_ibkr_mcp_package.capture_git_baseline", return_value={}), mock.patch("scripts.accept_ibkr_mcp_package.capture_database_token"), mock.patch("scripts.accept_ibkr_mcp_package.load_package") as load:
            with self.assertRaisesRegex(ValueError, "replace"):
                accept_package(self.root, "a" * 64, self.target, self.root, db, self.root / "seeds")
            load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
