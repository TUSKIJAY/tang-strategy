from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any


BAR_MA_WINDOWS = (5, 10, 20, 30, 50, 60, 120, 200, 250)
BAR_WINDOW_COLUMNS = [f"m{window}" for window in BAR_MA_WINDOWS]


def pick_value(source: Any, *keys: str) -> Any:
    source_keys = None
    if not isinstance(source, dict):
        try:
            source_keys = set(source.keys())
        except AttributeError:
            source_keys = None

    for key in keys:
        if isinstance(source, dict) and key in source:
            return source[key]
        if source_keys is not None and key in source_keys:
            return source[key]
    return None


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _finite_values(values: list[float | None]) -> list[float]:
    return [value for value in values if value is not None]


def _typical_price(row: Any) -> float | None:
    high = _as_float(pick_value(row, "H", "high"))
    low = _as_float(pick_value(row, "L", "low"))
    close = _as_float(pick_value(row, "C", "close"))
    if high is None or low is None or close is None:
        return None
    return (high + low + close) / 3.0


def _source_vwap_price(row: Any) -> float | None:
    source_vwap = pick_value(row, "vw", "vwap")
    return _as_float(source_vwap) if source_vwap is not None else _typical_price(row)


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        normalized = str(value)
        if normalized.endswith("Z"):
            normalized = normalized[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _session_date(row: Any) -> date | None:
    dt = _parse_ts(pick_value(row, "ts"))
    return dt.date() if dt else None


def add_heikin_ashi_fields(bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    prev_ha_open: float | None = None
    prev_ha_close: float | None = None
    current_session_date: date | None = None

    for bar in bars:
        next_bar = dict(bar)
        bar_session_date = _session_date(next_bar)
        if bar_session_date != current_session_date:
            current_session_date = bar_session_date
            prev_ha_open = None
            prev_ha_close = None

        open_price = _as_float(pick_value(next_bar, "O", "open"))
        high_price = _as_float(pick_value(next_bar, "H", "high"))
        low_price = _as_float(pick_value(next_bar, "L", "low"))
        close_price = _as_float(pick_value(next_bar, "C", "close"))

        if open_price is None or high_price is None or low_price is None or close_price is None:
            next_bar["hO"] = None
            next_bar["hH"] = None
            next_bar["hL"] = None
            next_bar["hC"] = None
        else:
            ha_close = (open_price + high_price + low_price + close_price) / 4.0
            if prev_ha_open is None or prev_ha_close is None:
                ha_open = (open_price + close_price) / 2.0
            else:
                ha_open = (prev_ha_open + prev_ha_close) / 2.0
            ha_high = max(high_price, ha_open, ha_close)
            ha_low = min(low_price, ha_open, ha_close)
            next_bar["hO"] = ha_open
            next_bar["hH"] = ha_high
            next_bar["hL"] = ha_low
            next_bar["hC"] = ha_close
            prev_ha_open = ha_open
            prev_ha_close = ha_close

        normalized.append(next_bar)

    return normalized


def normalize_session_vwap(
    bars: list[dict[str, Any]],
    source_vwap_mode: str = "bar_price",
) -> list[dict[str, Any]]:
    if source_vwap_mode == "session_cumulative":
        return [dict(bar) for bar in bars]

    normalized: list[dict[str, Any]] = []
    current_session_date: date | None = None
    cumulative_vw_numerator = 0.0
    cumulative_vw_denominator = 0.0

    for bar in bars:
        next_bar = dict(bar)
        bar_session_date = _session_date(next_bar)
        if bar_session_date != current_session_date:
            current_session_date = bar_session_date
            cumulative_vw_numerator = 0.0
            cumulative_vw_denominator = 0.0

        price_value = _source_vwap_price(next_bar)
        volume_value = _as_float(pick_value(next_bar, "V", "volume"))
        if price_value is not None and volume_value is not None:
            cumulative_vw_numerator += price_value * volume_value
            cumulative_vw_denominator += volume_value

        vwap = (
            cumulative_vw_numerator / cumulative_vw_denominator
            if cumulative_vw_denominator > 0
            else None
        )
        next_bar["vw"] = vwap
        if "vwap" in next_bar:
            next_bar["vwap"] = vwap
        normalized.append(next_bar)

    return normalized


def bar_tuple_from_seed(bar_owner_id: int | str, idx: int, bar: dict[str, Any]) -> tuple[Any, ...]:
    return (
        bar_owner_id,
        idx,
        pick_value(bar, "ts"),
        pick_value(bar, "t", "time"),
        pick_value(bar, "O", "open"),
        pick_value(bar, "H", "high"),
        pick_value(bar, "L", "low"),
        pick_value(bar, "C", "close"),
        pick_value(bar, "V", "volume"),
        pick_value(bar, "vw", "vwap"),
        pick_value(bar, "hO", "ha_open"),
        pick_value(bar, "hH", "ha_high"),
        pick_value(bar, "hL", "ha_low"),
        pick_value(bar, "hC", "ha_close"),
        pick_value(bar, "m5"),
        pick_value(bar, "m10"),
        pick_value(bar, "m20"),
        pick_value(bar, "m30"),
        pick_value(bar, "m50"),
        pick_value(bar, "m60"),
        pick_value(bar, "m120"),
        pick_value(bar, "m200"),
        pick_value(bar, "m250"),
    )


def _time_from_ts(ts: str | None) -> str:
    return ts[11:16] if ts and len(ts) >= 16 else ""


def bar_row_to_payload(row: Any) -> dict[str, Any]:
    row_map = dict(row)
    ts = row_map.get("ts")
    return {
        "ts": ts,
        "t": row_map.get("time") if row_map.get("time") is not None else _time_from_ts(ts),
        "O": row_map.get("open"),
        "H": row_map.get("high"),
        "L": row_map.get("low"),
        "C": row_map.get("close"),
        "V": row_map.get("volume"),
        "vw": row_map.get("vwap"),
        "hO": row_map.get("ha_open"),
        "hH": row_map.get("ha_high"),
        "hL": row_map.get("ha_low"),
        "hC": row_map.get("ha_close"),
        "m5": row_map.get("m5"),
        "m10": row_map.get("m10"),
        "m20": row_map.get("m20"),
        "m30": row_map.get("m30"),
        "m50": row_map.get("m50"),
        "m60": row_map.get("m60"),
        "m120": row_map.get("m120"),
        "m200": row_map.get("m200"),
        "m250": row_map.get("m250"),
    }


def recalculate_ma_fields(
    bars: list[dict[str, Any]],
    warmup_closes: list[float | None] | None = None,
    preserve_warmup_values: bool = True,
) -> list[dict[str, Any]]:
    closes_for_ma: list[float | None] = list(warmup_closes or [])
    normalized: list[dict[str, Any]] = []

    for bar in bars:
        next_bar = dict(bar)
        close_price = _as_float(pick_value(next_bar, "C", "close"))
        closes_for_ma.append(close_price)

        for window, key in zip(BAR_MA_WINDOWS, BAR_WINDOW_COLUMNS):
            if len(closes_for_ma) >= window:
                window_values = closes_for_ma[-window:]
                next_bar[key] = sum(v for v in window_values if v is not None) / window if all(
                    v is not None for v in window_values
                ) else None
            elif not preserve_warmup_values:
                next_bar[key] = None

        normalized.append(next_bar)

    return normalized


def _bucket_start(ts: str) -> datetime:
    normalized = ts[:-1] + "+00:00" if ts.endswith("Z") else ts
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)


def build_5m_bars_from_1m(raw_rows: list[Any], source_vwap_mode: str = "bar_price") -> list[dict[str, Any]]:
    if not raw_rows:
        return []

    sorted_rows = sorted(raw_rows, key=lambda row: pick_value(row, "ts") or "")
    rows = [row for row in sorted_rows if pick_value(row, "ts")]
    if not rows:
        return []

    bars: list[dict[str, Any]] = []
    closes_for_ma: list[float | None] = []
    prev_ha_open: float | None = None
    prev_ha_close: float | None = None

    bucket_rows: list[dict[str, Any]] = []
    current_bucket = _bucket_start(pick_value(rows[0], "ts"))
    current_session_date = current_bucket.date()
    cumulative_vw_numerator = 0.0
    cumulative_vw_denominator = 0.0

    def _flush_bucket(bucket_dt: datetime, members: list[dict[str, Any]]) -> None:
        nonlocal prev_ha_open, prev_ha_close, closes_for_ma
        nonlocal current_session_date, cumulative_vw_numerator, cumulative_vw_denominator
        if not members:
            return
        if bucket_dt.date() != current_session_date:
            current_session_date = bucket_dt.date()
            prev_ha_open = None
            prev_ha_close = None
            cumulative_vw_numerator = 0.0
            cumulative_vw_denominator = 0.0

        open_price = _as_float(pick_value(members[0], "O", "open"))
        closes = [_as_float(pick_value(row, "C", "close")) for row in members]
        highs = [_as_float(pick_value(row, "H", "high")) for row in members]
        lows = [_as_float(pick_value(row, "L", "low")) for row in members]
        volumes = [_as_float(pick_value(row, "V", "volume")) for row in members]
        closes_without_none = _finite_values(closes)
        highs_without_none = _finite_values(highs)
        lows_without_none = _finite_values(lows)
        high_price = max(highs_without_none) if highs_without_none else None
        low_price = min(lows_without_none) if lows_without_none else None
        close_price = closes_without_none[-1] if closes_without_none else None

        volume_total = sum(v for v in volumes if v is not None)
        if source_vwap_mode == "session_cumulative":
            vwap = next(
                (value for value in (_source_vwap_price(row) for row in reversed(members)) if value is not None),
                None,
            )
        else:
            # Use 1m bar VWAP/IB average when present, otherwise typical price,
            # then keep a session-cumulative VWAP on the 5m series.
            bucket_vw_numerator = 0.0
            bucket_vw_denominator = 0.0
            for row, volume_value in zip(members, volumes):
                price_value = _source_vwap_price(row)
                if price_value is None or volume_value is None:
                    continue
                bucket_vw_numerator += price_value * volume_value
                bucket_vw_denominator += volume_value

            if bucket_vw_denominator > 0:
                cumulative_vw_numerator += bucket_vw_numerator
                cumulative_vw_denominator += bucket_vw_denominator
            vwap = cumulative_vw_numerator / cumulative_vw_denominator if cumulative_vw_denominator > 0 else None

        if open_price is None or high_price is None or low_price is None or close_price is None:
            ha_open = None
            ha_high = None
            ha_low = None
            ha_close = None
        else:
            ha_close = (open_price + high_price + low_price + close_price) / 4.0
            if prev_ha_open is None or prev_ha_close is None:
                ha_open = (open_price + close_price) / 2.0
            else:
                ha_open = (prev_ha_open + prev_ha_close) / 2.0
            ha_high = max(high_price, ha_open, ha_close)
            ha_low = min(low_price, ha_open, ha_close)
            prev_ha_open = ha_open
            prev_ha_close = ha_close

        closes_for_ma.append(close_price)

        ma_values: dict[str, float | None] = {}
        for window, key in zip(BAR_MA_WINDOWS, BAR_WINDOW_COLUMNS):
            if len(closes_for_ma) >= window:
                window_values = closes_for_ma[-window:]
                ma_values[key] = sum(v for v in window_values if v is not None) / window if all(
                    v is not None for v in window_values
                ) else None
            else:
                ma_values[key] = None

        bars.append({
            "ts": bucket_dt.isoformat(),
            "t": bucket_dt.strftime("%H:%M"),
            "O": open_price,
            "H": high_price,
            "L": low_price,
            "C": close_price,
            "V": volume_total,
            "vw": vwap,
            "hO": ha_open,
            "hH": ha_high,
            "hL": ha_low,
            "hC": ha_close,
            "m5": ma_values["m5"],
            "m10": ma_values["m10"],
            "m20": ma_values["m20"],
            "m30": ma_values["m30"],
            "m50": ma_values["m50"],
            "m60": ma_values["m60"],
            "m120": ma_values["m120"],
            "m200": ma_values["m200"],
            "m250": ma_values["m250"],
        })

    for row in rows:
        row_bucket = _bucket_start(pick_value(row, "ts"))
        if row_bucket != current_bucket:
            _flush_bucket(current_bucket, bucket_rows)
            bucket_rows = []
            current_bucket = row_bucket
        bucket_rows.append(row)

    _flush_bucket(current_bucket, bucket_rows)
    return bars
