from __future__ import annotations

import argparse
import asyncio
import json
import math
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

asyncio.set_event_loop(asyncio.new_event_loop())

from ib_insync import IB, Stock  # noqa: E402

from app.settings import REPO_DIR, settings


ET = ZoneInfo("America/New_York")
MA_WINDOWS = (5, 10, 20, 30, 50, 60, 120, 200, 250)


def finite(value: object) -> float | None:
    if isinstance(value, Decimal):
        value = float(value)
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def round_price(value: object) -> float | None:
    number = finite(value)
    return round(number, 4) if number is not None else None


def latest_completed_market_date(now: datetime | None = None) -> str:
    current = (now or datetime.now(ET)).astimezone(ET)
    candidate = current.date()
    if current.time() < datetime.combine(candidate, datetime.min.time(), ET).replace(hour=20).time():
        candidate -= timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate.isoformat()


def previous_market_date(trade_date: str) -> str:
    candidate = date.fromisoformat(trade_date) - timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate -= timedelta(days=1)
    return candidate.isoformat()


def load_warmup(path: Path, series_key: str) -> list[float | None]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [bar.get("C") for bar in data.get(series_key, [])][-249:]


def add_heikin_ashi(bars: list[dict]) -> None:
    prev_ha_open: float | None = None
    prev_ha_close: float | None = None
    for bar in bars:
        open_price, high_price, low_price, close_price = bar["O"], bar["H"], bar["L"], bar["C"]
        ha_close = (open_price + high_price + low_price + close_price) / 4
        ha_open = (
            (open_price + close_price) / 2
            if prev_ha_open is None or prev_ha_close is None
            else (prev_ha_open + prev_ha_close) / 2
        )
        bar["hO"] = round_price(ha_open)
        bar["hH"] = round_price(max(high_price, ha_open, ha_close))
        bar["hL"] = round_price(min(low_price, ha_open, ha_close))
        bar["hC"] = round_price(ha_close)
        prev_ha_open = ha_open
        prev_ha_close = ha_close


def add_mas(bars: list[dict], warmup_closes: list[float | None]) -> None:
    closes = [finite(value) for value in warmup_closes if finite(value) is not None]
    for bar in bars:
        closes.append(finite(bar.get("C")))
        for window in MA_WINDOWS:
            values = closes[-window:]
            bar[f"m{window}"] = (
                round_price(sum(values) / window)
                if len(values) >= window and all(value is not None for value in values)
                else None
            )


def bucket_start(dt: datetime) -> datetime:
    return dt.replace(minute=(dt.minute // 5) * 5, second=0, microsecond=0)


def build_5m_bars(bars_1m: list[dict]) -> list[dict]:
    bars_5m: list[dict] = []
    current_bucket: datetime | None = None
    members: list[dict] = []
    prev_ha_open: float | None = None
    prev_ha_close: float | None = None
    cumulative_vw_num = 0.0
    cumulative_vw_den = 0.0

    def flush(bucket: datetime, rows: list[dict]) -> None:
        nonlocal prev_ha_open, prev_ha_close, cumulative_vw_num, cumulative_vw_den
        if not rows:
            return
        open_price = rows[0]["O"]
        high_price = max(row["H"] for row in rows)
        low_price = min(row["L"] for row in rows)
        close_price = rows[-1]["C"]
        volume = sum(int(row.get("V") or 0) for row in rows)
        bucket_vw_num = 0.0
        bucket_vw_den = 0.0
        for row in rows:
            row_volume = int(row.get("V") or 0)
            if row_volume <= 0:
                continue
            price = row.get("vw") or (row["H"] + row["L"] + row["C"]) / 3
            bucket_vw_num += price * row_volume
            bucket_vw_den += row_volume
        if bucket_vw_den > 0:
            cumulative_vw_num += bucket_vw_num
            cumulative_vw_den += bucket_vw_den
        vwap = cumulative_vw_num / cumulative_vw_den if cumulative_vw_den > 0 else None
        ha_close = (open_price + high_price + low_price + close_price) / 4
        ha_open = (
            (open_price + close_price) / 2
            if prev_ha_open is None or prev_ha_close is None
            else (prev_ha_open + prev_ha_close) / 2
        )
        bars_5m.append({
            "ts": bucket.isoformat(),
            "t": bucket.strftime("%H:%M"),
            "O": round_price(open_price),
            "H": round_price(high_price),
            "L": round_price(low_price),
            "C": round_price(close_price),
            "V": volume,
            "vw": round_price(vwap),
            "hO": round_price(ha_open),
            "hH": round_price(max(high_price, ha_open, ha_close)),
            "hL": round_price(min(low_price, ha_open, ha_close)),
            "hC": round_price(ha_close),
        })
        prev_ha_open = ha_open
        prev_ha_close = ha_close

    for bar in bars_1m:
        bucket = bucket_start(bar["_dt"])
        if current_bucket is None:
            current_bucket = bucket
        if bucket != current_bucket:
            flush(current_bucket, members)
            members = []
            current_bucket = bucket
        members.append(bar)
    if current_bucket is not None:
        flush(current_bucket, members)
    return bars_5m


def missing_minutes(trade_date: str, bars: list[dict]) -> tuple[int, list[str]]:
    present = {bar["t"] for bar in bars}
    day = date.fromisoformat(trade_date)
    cursor = datetime(day.year, day.month, day.day, 4, 0, tzinfo=ET)
    end = datetime(day.year, day.month, day.day, 20, 0, tzinfo=ET)
    missing: list[str] = []
    groups = 0
    in_gap = False
    while cursor < end:
        time_label = cursor.strftime("%H:%M")
        if time_label not in present:
            missing.append(time_label)
            if not in_gap:
                groups += 1
                in_gap = True
        else:
            in_gap = False
        cursor += timedelta(minutes=1)
    return groups, missing


def fetch_ib_bars(symbol: str, trade_date: str, host: str, port: int, client_id: int) -> tuple[list[dict], Stock]:
    ib = IB()
    ib.connect(host, port, clientId=client_id, timeout=10, readonly=True)
    try:
        contract = Stock(symbol, "SMART", "USD", primaryExchange="ARCA")
        qualified = ib.qualifyContracts(contract)
        if not qualified:
            raise RuntimeError(f"IB could not qualify {symbol} contract")
        contract = qualified[0]
        day = date.fromisoformat(trade_date)
        raw_bars = ib.reqHistoricalData(
            contract,
            endDateTime=datetime(day.year, day.month, day.day, 20, 0, tzinfo=ET),
            durationStr="1 D",
            barSizeSetting="1 min",
            whatToShow="TRADES",
            useRTH=False,
            formatDate=2,
            keepUpToDate=False,
            timeout=60,
        )
    finally:
        ib.disconnect()

    bars: list[dict] = []
    seen_minutes: set[str] = set()
    start = datetime(day.year, day.month, day.day, 4, 0, tzinfo=ET)
    end = datetime(day.year, day.month, day.day, 20, 0, tzinfo=ET)
    for raw in raw_bars:
        dt = raw.date
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ET)
        dt_et = dt.astimezone(ET)
        if not start <= dt_et < end:
            continue
        minute_key = dt_et.strftime("%Y-%m-%dT%H:%M")
        if minute_key in seen_minutes:
            continue
        seen_minutes.add(minute_key)
        open_price, high_price, low_price, close_price = map(finite, [raw.open, raw.high, raw.low, raw.close])
        if open_price is None or high_price is None or low_price is None or close_price is None:
            continue
        volume = finite(getattr(raw, "volume", None)) or 0
        average = finite(getattr(raw, "average", None))
        bars.append({
            "_dt": dt_et,
            "ts": dt_et.isoformat(),
            "t": dt_et.strftime("%H:%M"),
            "O": round_price(open_price),
            "H": round_price(high_price),
            "L": round_price(low_price),
            "C": round_price(close_price),
            "V": int(volume),
            "vw": round_price(average) if average is not None and volume > 0 else None,
        })
    bars.sort(key=lambda bar: bar["ts"])
    return bars, contract


def strip_internal(bars: list[dict]) -> list[dict]:
    return [{key: value for key, value in bar.items() if not key.startswith("_")} for bar in bars]


def write_live_extended(symbol: str, trade_date: str, host: str, port: int, client_id: int) -> Path:
    bars_1m, contract = fetch_ib_bars(symbol, trade_date, host, port, client_id)
    if not bars_1m:
        raise RuntimeError(f"No IB bars returned for {symbol} {trade_date}")

    previous_path = settings.live_extended_dir / previous_market_date(trade_date) / f"{symbol}_{previous_market_date(trade_date)}.json"
    add_heikin_ashi(bars_1m)
    add_mas(bars_1m, load_warmup(previous_path, "bars_1m"))
    bars_5m = build_5m_bars(bars_1m)
    add_mas(bars_5m, load_warmup(previous_path, "bars_5m"))
    gap_count, missing = missing_minutes(trade_date, bars_1m)
    counts = {
        "bars_1m": len(bars_1m),
        "bars_5m": len(bars_5m),
        "premarket_1m": sum(1 for bar in bars_1m if bar["t"] < "09:30"),
        "rth_1m": sum(1 for bar in bars_1m if "09:30" <= bar["t"] < "16:00"),
        "afterhours_1m": sum(1 for bar in bars_1m if bar["t"] >= "16:00"),
    }

    output_dir = settings.live_extended_dir / trade_date
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{symbol}_{trade_date}.json"
    payload = {
        "meta": {
            "title": f"{symbol} {trade_date} Full Day",
            "ticker": symbol,
            "date": trade_date,
            "source": f"Interactive Brokers Gateway historicalData {host}:{port}",
            "provider": "ibkr",
            "ib_contract": {
                "conId": contract.conId,
                "symbol": contract.symbol,
                "secType": contract.secType,
                "exchange": contract.exchange,
                "primaryExchange": contract.primaryExchange,
                "currency": contract.currency,
            },
            "ib_request": {
                "endDateTime": datetime.fromisoformat(f"{trade_date}T20:00:00").replace(tzinfo=ET).isoformat(),
                "durationStr": "1 D",
                "barSizeSetting": "1 min",
                "whatToShow": "TRADES",
                "useRTH": False,
                "formatDate": 2,
            },
            "session_mode": "extended",
            "session_window": "04:00-20:00 ET",
            "session_type": "full_session_gappy" if gap_count else "full_session",
            "gap_count": gap_count,
            "missing_minutes": missing,
            "warmup_complete": {
                "1m": len(load_warmup(previous_path, "bars_1m")) >= 249,
                "5m": len(load_warmup(previous_path, "bars_5m")) >= 249,
            },
            "counts": counts,
            "generated_at": datetime.now().isoformat(),
        },
        "bars_1m": strip_internal(bars_1m),
        "bars_5m": strip_internal(bars_5m),
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "path": str(output_path.relative_to(REPO_DIR)),
        "provider": "ibkr",
        "ticker": symbol,
        "trade_date": trade_date,
        "counts": counts,
        "gap_count": gap_count,
        "missing_minutes": missing,
    }, ensure_ascii=False, indent=2))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch IB Gateway 1m extended-session bars into live_extended JSON.")
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--date", default="", help="Trade date YYYY-MM-DD. Defaults to the latest completed US market day.")
    parser.add_argument("--host", default=settings.ibkr_host)
    parser.add_argument("--port", type=int, default=settings.ibkr_port)
    parser.add_argument("--client-id", type=int, default=51402)
    args = parser.parse_args()

    trade_date = args.date or latest_completed_market_date()
    write_live_extended(args.symbol.upper(), trade_date, args.host, args.port, args.client_id)


if __name__ == "__main__":
    main()
