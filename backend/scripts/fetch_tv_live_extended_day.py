from __future__ import annotations

import argparse
import json
import math
import os
import time as time_module
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from app.services.importer import import_market_json
from app.settings import settings


ET = ZoneInfo("America/New_York")
SESSION_START = time(4, 0)
SESSION_END = time(20, 0)
TVDATAFEED_COMMIT = "e6f6aaa7de439ac6e454d9b26d2760ded8dc4923"


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def write_payload(payload: dict[str, Any], output_dir: Path) -> Path:
    meta = payload["meta"]
    path = output_dir / meta["date"] / f"{meta['ticker']}_{meta['date']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def market_session(trade_date: date, calendar_name: str = "NYSE") -> tuple[datetime, datetime]:
    try:
        import pandas_market_calendars as market_calendars
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pandas_market_calendars is required; install backend/requirements-tv.txt"
        ) from exc

    calendar = market_calendars.get_calendar(calendar_name)
    schedule = calendar.schedule(start_date=trade_date, end_date=trade_date)
    if schedule.empty:
        raise RuntimeError(f"{trade_date.isoformat()} is not a {calendar_name} trading day")

    row = schedule.iloc[0]
    market_open = row["market_open"].to_pydatetime().astimezone(ET)
    market_close = row["market_close"].to_pydatetime().astimezone(ET)
    if market_open.date() != trade_date or market_close.date() != trade_date:
        raise RuntimeError(
            f"Unexpected {calendar_name} session boundaries for {trade_date}: "
            f"{market_open.isoformat()} to {market_close.isoformat()}"
        )
    return market_open, market_close


def expected_bar_times(start: datetime, end: datetime, minutes: int) -> list[str]:
    cursor = start
    result: list[str] = []
    while cursor < end:
        result.append(cursor.strftime("%H:%M"))
        cursor += timedelta(minutes=minutes)
    return result


def _close_tv_socket(client: Any) -> None:
    socket = getattr(client, "ws", None)
    if socket is None:
        return
    try:
        socket.close()
    except Exception:
        pass
    finally:
        try:
            client.ws = None
        except Exception:
            pass


def fetch_tv_dataframe(
    symbol: str,
    exchange: str,
    bar_count: int,
    retry_attempts: int,
    retry_sleep: float,
) -> tuple[Any, bool]:
    try:
        from tvDatafeed import Interval, TvDatafeed
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "tvdatafeed is required; install backend/requirements-tv.txt"
        ) from exc

    username = os.getenv("TRADINGVIEW_USERNAME", "").strip()
    password = os.getenv("TRADINGVIEW_PASSWORD", "").strip()
    authenticated = bool(username and password)
    last_error: BaseException | None = None

    for attempt in range(1, max(1, retry_attempts) + 1):
        client = TvDatafeed(username, password) if authenticated else TvDatafeed()
        try:
            dataframe = client.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=Interval.in_1_minute,
                n_bars=bar_count,
                extended_session=True,
            )
            if dataframe is not None and not dataframe.empty:
                return dataframe, authenticated
            last_error = RuntimeError(f"TradingView returned no data for {exchange}:{symbol}")
        except Exception as exc:
            last_error = exc
        finally:
            _close_tv_socket(client)

        if attempt < max(1, retry_attempts):
            time_module.sleep(max(0.0, retry_sleep))

    raise RuntimeError(
        f"TradingView fetch failed for {exchange}:{symbol} after "
        f"{max(1, retry_attempts)} attempts: {last_error}"
    ) from last_error


def _timestamp_to_et(value: Any) -> datetime:
    if hasattr(value, "to_pydatetime"):
        value = value.to_pydatetime()
    if not isinstance(value, datetime):
        value = datetime.fromisoformat(str(value))
    if value.tzinfo is None:
        # tvDatafeed constructs naive timestamps in the host's local timezone.
        value = value.astimezone()
    return value.astimezone(ET)


def dataframe_to_rows(dataframe: Any, trade_date: date) -> list[dict[str, Any]]:
    frame = dataframe.reset_index()
    timestamp_column = "datetime" if "datetime" in frame.columns else frame.columns[0]
    rows: list[dict[str, Any]] = []

    for record in frame.to_dict(orient="records"):
        local = _timestamp_to_et(record[timestamp_column])
        if local.date() != trade_date or not (SESSION_START <= local.time() < SESSION_END):
            continue
        high = float(record["high"])
        low = float(record["low"])
        close = float(record["close"])
        rows.append(
            {
                "ts": local.isoformat(),
                "t": local.strftime("%H:%M"),
                "O": float(record["open"]),
                "H": high,
                "L": low,
                "C": close,
                "V": float(record.get("volume") or 0),
                "vw": (high + low + close) / 3.0,
            }
        )

    rows.sort(key=lambda item: item["ts"])
    return rows


def validate_source_rows(
    rows: list[dict[str, Any]],
    trade_date: date,
    market_open: datetime,
    market_close: datetime,
) -> list[dict[str, Any]]:
    if not rows:
        raise RuntimeError(f"TradingView returned no usable bars for {trade_date}")

    timestamps = [str(row["ts"]) for row in rows]
    if timestamps != sorted(timestamps) or len(timestamps) != len(set(timestamps)):
        raise RuntimeError("TV hard gate failed: timestamps are not strictly ordered and unique")

    for row in rows:
        local = datetime.fromisoformat(str(row["ts"])).astimezone(ET)
        if local.date() != trade_date:
            raise RuntimeError(f"TV hard gate failed: wrong market date at {row['ts']}")
        values = [float(row[key]) for key in ("O", "H", "L", "C", "V")]
        if not all(math.isfinite(value) for value in values):
            raise RuntimeError(f"TV hard gate failed: non-finite OHLCV at {row['t']}")
        if min(float(row[key]) for key in ("O", "H", "L", "C")) <= 0 or float(row["V"]) < 0:
            raise RuntimeError(f"TV hard gate failed: non-positive price or negative volume at {row['t']}")
        if float(row["H"]) < max(float(row[key]) for key in ("O", "C", "L")):
            raise RuntimeError(f"TV hard gate failed: invalid high at {row['t']}")
        if float(row["L"]) > min(float(row[key]) for key in ("O", "C", "H")):
            raise RuntimeError(f"TV hard gate failed: invalid low at {row['t']}")

    open_text = market_open.strftime("%H:%M")
    close_text = market_close.strftime("%H:%M")
    rth = [row for row in rows if open_text <= row["t"] < close_text]
    expected = expected_bar_times(market_open, market_close, 1)
    actual = [str(row["t"]) for row in rth]
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        duplicates = len(actual) - len(set(actual))
        raise RuntimeError(
            f"TV hard gate failed: RTH count={len(actual)}, expected={len(expected)}, "
            f"missing={missing}, duplicates={duplicates}"
        )
    return rth


def build_tv_payload(
    symbol: str,
    exchange: str,
    trade_date: date,
    rows: list[dict[str, Any]],
    market_open: datetime,
    market_close: datetime,
    bar_count: int,
    retry_attempts: int,
    authenticated: bool,
) -> dict[str, Any]:
    # Reuse the established deterministic MA/HA/VWAP builder. Importing this
    # module does not connect to IB; only fetch_ib_1m_bars opens the Gateway.
    from scripts.fetch_ib_live_extended_day import build_payload

    rth = validate_source_rows(rows, trade_date, market_open, market_close)
    payload = build_payload(symbol, trade_date, rows, {}, {}, "TradingView", 443)
    open_text = market_open.strftime("%H:%M")
    close_text = market_close.strftime("%H:%M")
    rth_5m = [row for row in payload["bars_5m"] if open_text <= row["t"] < close_text]
    expected_5m = expected_bar_times(market_open, market_close, 5)
    if [str(row["t"]) for row in rth_5m] != expected_5m:
        raise RuntimeError(
            f"TV hard gate failed: derived RTH 5m count={len(rth_5m)}, "
            f"expected={len(expected_5m)}"
        )
    if any(
        row.get("vw") is None or not math.isfinite(float(row["vw"]))
        for row in rth
        if float(row["V"]) > 0
    ):
        raise RuntimeError("TV hard gate failed: unusable RTH VWAP")

    meta = payload["meta"]
    meta["source"] = f"TradingView {exchange}:{symbol} via tvdatafeed@{TVDATAFEED_COMMIT[:7]}"
    meta["provider"] = "tradingview"
    meta.pop("ib_contract", None)
    meta.pop("ib_request", None)
    meta["tradingview_request"] = {
        "symbol": symbol,
        "exchange": exchange,
        "timeframe": "1m",
        "bar_count": bar_count,
        "extended_session": True,
        "authenticated": authenticated,
        "retry_attempts": retry_attempts,
        "tvdatafeed_commit": TVDATAFEED_COMMIT,
    }
    meta["market_calendar"] = "NYSE"
    meta["rth_window"] = f"{open_text}-{close_text} ET"
    meta["session_type"] = "extended_session_sparse_rth_complete"
    meta["synthetic_padding"] = False
    meta["quality"] = {
        "rth_1m_bars": len(rth),
        "rth_1m_expected": len(expected_bar_times(market_open, market_close, 1)),
        "rth_missing_minutes": [],
        "rth_duplicate_minutes": 0,
        "rth_5m_bars": len(rth_5m),
        "rth_5m_expected": len(expected_5m),
        "extended_1m_bars": len(rows),
        "extended_missing_minutes": meta["missing_minutes"],
    }
    meta["vwap_source"] = (
        "TradingView OHLC typical price weighted by source volume; session cumulative"
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch one supported symbol extended-session day from TradingView and import it."
    )
    parser.add_argument("date", help="Trade date, YYYY-MM-DD.")
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--exchange", default="AMEX")
    parser.add_argument("--bar-count", type=int, default=3000)
    parser.add_argument("--retry-attempts", type=int, default=3)
    parser.add_argument("--retry-sleep", type=float, default=1.0)
    parser.add_argument("--output-dir", type=Path, default=settings.live_extended_dir)
    parser.add_argument("--skip-import", action="store_true")
    args = parser.parse_args()

    trade_date = parse_trade_date(args.date)
    symbol = args.symbol.upper()
    exchange = args.exchange.upper()
    market_open, market_close = market_session(trade_date)
    dataframe, authenticated = fetch_tv_dataframe(
        symbol=symbol,
        exchange=exchange,
        bar_count=max(1, args.bar_count),
        retry_attempts=max(1, args.retry_attempts),
        retry_sleep=max(0.0, args.retry_sleep),
    )
    rows = dataframe_to_rows(dataframe, trade_date)
    payload = build_tv_payload(
        symbol=symbol,
        exchange=exchange,
        trade_date=trade_date,
        rows=rows,
        market_open=market_open,
        market_close=market_close,
        bar_count=max(1, args.bar_count),
        retry_attempts=max(1, args.retry_attempts),
        authenticated=authenticated,
    )
    output_path = write_payload(payload, args.output_dir)
    market_day_id = None if args.skip_import else import_market_json(output_path)
    quality = payload["meta"]["quality"]
    print(
        f"Wrote {output_path} with {len(payload['bars_1m'])} 1m bars, "
        f"{len(payload['bars_5m'])} 5m bars, "
        f"RTH={quality['rth_1m_bars']}/{quality['rth_1m_expected']} 1m and "
        f"{quality['rth_5m_bars']}/{quality['rth_5m_expected']} 5m, "
        f"extended_gaps={payload['meta']['gap_count']}, market_day_id={market_day_id}"
    )


if __name__ == "__main__":
    main()
