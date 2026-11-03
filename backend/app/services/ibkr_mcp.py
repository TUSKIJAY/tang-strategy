"""Read an operator-supplied market-only MCP package. Never logs in or trades."""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from app.services.bar_utils import add_heikin_ashi_fields, normalize_session_vwap, recalculate_ma_fields

ET = ZoneInfo("America/New_York")
PROVIDER = "ibkr_mcp"
SYMBOLS = ("SPY", "QQQ")
STEPS = {"ONE_MIN": 60, "FIVE_MINS": 300}
TOLERANCE = 1e-8


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _json(data: bytes | str) -> Any:
    return json.loads(data, object_pairs_hook=_object, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON")))


def _safe_file(root: Path, name: str) -> bytes:
    if not isinstance(name, str) or Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("package path escape")
    path = root / name
    if path.is_symlink() or not path.is_file() or path.resolve().parent != root:
        raise ValueError("package file is not a regular local file")
    if path.stat().st_size > 10_000_000:
        raise ValueError("package file too large")
    return path.read_bytes()


def _market_only(value: Any) -> None:
    forbidden = {"token", "access_token", "accesstoken", "refresh_token", "refreshtoken", "password", "cookie", "authorization", "account", "account_id", "accountid", "positions", "orders", "api_key", "apikey", "secret", "client_secret", "credentials", "credential", "session_token", "bearer_token"}
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in forbidden:
                raise ValueError(f"non-market field forbidden: {key}")
            _market_only(child)
    elif isinstance(value, list):
        for child in value:
            _market_only(child)


def _response(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict) or raw.get("isError") is True:
        raise ValueError("MCP tool error")
    _market_only(raw)
    structured = raw.get("structuredContent")
    blocks = raw.get("content", [])
    text = [item["text"] for item in blocks if isinstance(item, dict) and item.get("type") == "text"]
    if len(text) > 1:
        raise ValueError("ambiguous text response")
    textual = _json(text[0]) if text else None
    if structured is not None and textual is not None and structured != textual:
        raise ValueError("text and structured response disagree")
    result = structured if structured is not None else textual
    if not isinstance(result, dict) or result.get("error"):
        raise ValueError("missing or failed price response")
    _market_only(result)
    return result


def _number(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _rows(data: dict[str, Any], seconds: int, target: str) -> tuple[list[dict], int]:
    arrays = [data.get(key) for key in ("time", "open", "high", "low", "close", "volume")]
    if any(not isinstance(a, list) for a in arrays) or not arrays[0] or len({len(a) for a in arrays}) != 1:
        raise ValueError("price arrays must be nonempty and equal length")
    if data.get("chart_step") != seconds or data.get("source") != "Last":
        raise ValueError("unexpected chart step or price source")
    result, previous, excluded = [], None, 0
    for ts, op, hi, lo, cl, volume in zip(*arrays):
        if not isinstance(ts, str):
            raise ValueError("invalid timestamp")
        instant = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if instant.tzinfo is None or instant.microsecond or instant.timestamp() % seconds:
            raise ValueError("unaligned or timezone-free timestamp")
        if previous is not None and instant <= previous:
            raise ValueError("duplicate or unordered timestamp")
        previous = instant
        if not all(_number(n) for n in (op, hi, lo, cl, volume)) or min(op, hi, lo, cl) <= 0 or volume < 0:
            raise ValueError("invalid OHLCV number")
        if hi < max(op, cl, lo) or lo > min(op, cl, hi):
            raise ValueError("invalid OHLC envelope")
        local = instant.astimezone(ET)
        if local.date().isoformat() != target:
            excluded += 1
            continue
        if not time(4) <= local.time().replace(tzinfo=None) < time(20):
            raise ValueError("target row outside requested extended window")
        result.append({"ts": local.isoformat(), "t": local.strftime("%H:%M"), "O": op, "H": hi, "L": lo, "C": cl, "V": volume})
    return result, excluded


def session_bounds(target: str) -> tuple[datetime, datetime]:
    import pandas_market_calendars as calendars
    schedule = calendars.get_calendar("NYSE").schedule(start_date=target, end_date=target)
    if schedule.empty:
        raise ValueError("not an NYSE session")
    row = schedule.iloc[0]
    return row.market_open.to_pydatetime().astimezone(ET), row.market_close.to_pydatetime().astimezone(ET)


def _rth(rows: list[dict], op: datetime, cl: datetime, seconds: int) -> int:
    expected, cursor = [], op
    while cursor < cl:
        expected.append(cursor.isoformat())
        cursor += timedelta(seconds=seconds)
    actual = [row["ts"] for row in rows if op <= datetime.fromisoformat(row["ts"]) < cl]
    if actual != expected:
        raise ValueError(f"RTH completeness failed: {len(actual)}/{len(expected)}")
    return len(expected)


def _aggregate(rows: list[dict]) -> dict:
    return {"O": rows[0]["O"], "H": max(r["H"] for r in rows), "L": min(r["L"] for r in rows), "C": rows[-1]["C"], "V": sum(r["V"] for r in rows)}


def _compare(minutes: list[dict], native: list[dict]) -> dict:
    buckets: dict[str, list] = {}
    for row in minutes:
        ts = datetime.fromisoformat(row["ts"])
        key = ts.replace(minute=ts.minute // 5 * 5).isoformat()
        buckets.setdefault(key, []).append(row)
    if set(buckets) != {r["ts"] for r in native}:
        raise ValueError("1m/5m bucket coverage mismatch")
    differences, all_zero = [], []
    for row in native:
        members = buckets[row["ts"]]
        positive = [r for r in members if r["V"] > 0]
        full = _aggregate(members)
        delta = [key for key in full if abs(full[key] - row[key]) > TOLERANCE]
        if positive:
            clean = _aggregate(positive)
            if any(abs(clean[key] - row[key]) > TOLERANCE for key in clean):
                raise ValueError(f"unexplained 1m/5m mismatch at {row['t']}")
        else:
            all_zero.append(row["t"])
            if delta:
                raise ValueError("inconsistent all-zero 5m bucket")
        if delta:
            # The diagnostic must not discard arbitrary zero-volume prices.
            for index, member in enumerate(minutes):
                if member in members and member["V"] == 0:
                    prior = minutes[index - 1]["C"] if index else None
                    if prior is None or any(member[key] != prior for key in ("O", "H", "L", "C")):
                        raise ValueError("5m difference not explained by zero-volume carry price")
            differences.append({"t": row["t"], "fields": delta})
    return {"all_minute_differences": differences, "positive_volume_comparison": "pass" if not all_zero else "warn", "all_zero_buckets": all_zero, "tolerance": TOLERANCE}


def load_package(root: Path, manifest_sha256: str, target: str, *, now: datetime | None = None) -> dict:
    if root.is_symlink():
        raise ValueError("package root is a symlink")
    root = root.resolve(strict=True)
    manifest_bytes = _safe_file(root, "manifest.json")
    if digest(manifest_bytes) != manifest_sha256:
        raise ValueError("manifest digest mismatch")
    manifest = _json(manifest_bytes)
    _market_only(manifest)
    if manifest.get("schema_version") != 1 or manifest.get("provider") != PROVIDER or manifest.get("trade_date") != target:
        raise ValueError("package identity mismatch")
    contracts = manifest.get("contracts", [])
    selected = {}
    for symbol in SYMBOLS:
        matches = [c for c in contracts if c.get("symbol") == symbol and c.get("country_code") == "US" and {"security_type": "STK"} in c.get("sections", [])]
        if len(matches) != 1 or type(matches[0].get("underlying_contract_id")) is not int:
            raise ValueError("missing exact US stock contract evidence")
        selected[symbol] = matches[0]
    op, cl = session_bounds(target)
    if (now or datetime.now(timezone.utc)).astimezone(timezone.utc) < cl.astimezone(timezone.utc):
        raise ValueError("NYSE session has not closed")
    entries = manifest.get("responses")
    if not isinstance(entries, list) or len(entries) != 4:
        raise ValueError("package requires four responses")
    normalized, seen, files, excluded = {}, set(), {"manifest.json": manifest_bytes}, {}
    for entry in entries:
        if entry.get("tool") != "interactive_brokers_ibkr_get_price_history":
            raise ValueError("unsupported market-data tool")
        symbol, request = entry.get("symbol"), entry.get("request", {})
        step = request.get("step")
        key = (symbol, step)
        if symbol not in SYMBOLS or step not in STEPS or key in seen:
            raise ValueError("duplicate or unsupported response identity")
        if request.get("contract_id") != selected[symbol]["underlying_contract_id"] or request.get("security_type") != "STK" or request.get("outside_rth") is not True:
            raise ValueError("request contract or session mismatch")
        if ("period" in request) == ("step_count" in request):
            raise ValueError("request must use period xor step_count")
        name = entry.get("file")
        if name in files:
            raise ValueError("duplicate package file")
        blob = _safe_file(root, name)
        if digest(blob) != entry.get("sha256"):
            raise ValueError("raw response digest mismatch")
        files[name] = blob
        data = _response(_json(blob))
        rows, removed = _rows(data, STEPS[step], target)
        normalized[key], excluded[f"{symbol}_{step}"] = rows, removed
        _rth(rows, op, cl, STEPS[step])
        seen.add(key)
    quality = {}
    for symbol in SYMBOLS:
        m, f = normalized[(symbol, "ONE_MIN")], normalized[(symbol, "FIVE_MINS")]
        quality[symbol] = {**_compare(m, f), "zero_volume_minutes": [r["t"] for r in m if r["V"] == 0], "first": m[0]["ts"], "last": m[-1]["ts"]}
    if _safe_file(root, "manifest.json") != manifest_bytes or any(_safe_file(root, name) != blob for name, blob in files.items()):
        raise ValueError("package changed during validation")
    return {"manifest_sha256": manifest_sha256, "trade_date": target, "rows": normalized, "quality": quality, "excluded": excluded, "files": files, "contracts": selected, "open": op, "close": cl}


def build_payload(symbol: str, package: dict, warmup: dict[str, list] | None = None, warmup_sources: list | None = None) -> dict:
    warmup = warmup or {}
    minutes = recalculate_ma_fields(add_heikin_ashi_fields(normalize_session_vwap(package["rows"][(symbol, "ONE_MIN")])), warmup.get("1m"), preserve_warmup_values=False)
    five = [dict(r) for r in package["rows"][(symbol, "FIVE_MINS")]]
    for bar in five:
        start = datetime.fromisoformat(bar["ts"])
        members = [r for r in minutes if start <= datetime.fromisoformat(r["ts"]) < start + timedelta(minutes=5)]
        bar["vw"] = members[-1]["vw"]
    five = recalculate_ma_fields(add_heikin_ashi_fields(five), warmup.get("5m"), preserve_warmup_values=False)
    op, cl = package["open"], package["close"]
    rth_minutes = [r for r in minutes if op <= datetime.fromisoformat(r["ts"]) < cl]
    if any(not _number(r["vw"]) for r in rth_minutes):
        raise ValueError("unusable RTH cumulative VWAP")
    count_m, count_f = _rth(minutes, op, cl, 60), _rth(five, op, cl, 300)
    actual = {r["t"] for r in minutes}
    cursor = datetime.combine(op.date(), time(4), tzinfo=ET)
    missing = []
    while cursor.time().replace(tzinfo=None) < time(20):
        if cursor.strftime("%H:%M") not in actual:
            missing.append(cursor.isoformat())
        cursor += timedelta(minutes=1)
    return {"meta": {"ticker": symbol, "date": package["trade_date"], "session_mode": "extended", "title": f"{symbol} {package['trade_date']} IBKR MCP", "source": "IBKR MCP · 典型价近似 VWAP", "provider": PROVIDER, "market_calendar": "NYSE", "synthetic_padding": False, "session_type": "extended_session_sparse_rth_complete", "session_window": "04:00-20:00 ET", "gap_count": len(missing), "missing_minutes": missing, "vwap_source": "typical_price_approximation (H+L+C)/3 weighted by source volume", "vwap_mode": "session_cumulative", "vwap_session_anchor": "04:00 ET", "counts": {"bars_1m": len(minutes), "bars_5m": len(five)}, "quality": {"rth_1m_bars": count_m, "rth_1m_expected": count_m, "rth_5m_bars": count_f, "rth_5m_expected": count_f, "rth_missing_minutes": [], "rth_duplicate_minutes": 0}, "ibkr_mcp": {"manifest_sha256": package["manifest_sha256"], "contract": package["contracts"][symbol], "volume_units": "not_declared", "market_completeness": "unproven", "diagnostics": package["quality"][symbol], "warmup_sources": warmup_sources or [], "warmup_may_use_other_providers": bool(warmup_sources)}}, "bars_1m": minutes, "bars_5m": five}
