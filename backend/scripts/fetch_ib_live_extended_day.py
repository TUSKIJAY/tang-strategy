from __future__ import annotations

import argparse
import asyncio
import json
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

# Python 3.14+ no longer auto-creates an event loop on import; eventkit (pulled in
# by ib_insync) requires one to exist before its module-level initialisation.
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

from app.db import connect, init_db
from app.services.bar_utils import (
    BAR_MA_WINDOWS,
    add_heikin_ashi_fields,
    build_5m_bars_from_1m,
    normalize_session_vwap,
    recalculate_ma_fields,
)
from app.services.importer import import_market_json
from app.settings import settings


ET = ZoneInfo("America/New_York")
SESSION_START = time(4, 0)
RTH_START = time(9, 30)
RTH_END = time(16, 0)
SESSION_END = time(20, 0)


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def to_et(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ET)
    return dt.astimezone(ET)


def in_extended_session(dt: datetime, trade_date: date) -> bool:
    local = dt.astimezone(ET)
    return local.date() == trade_date and SESSION_START <= local.time() < SESSION_END


def bar_source_vwap(bar: Any) -> float | None:
    average = float(getattr(bar, "average", 0) or 0)
    if average > 0:
        return average
    high = getattr(bar, "high", None)
    low = getattr(bar, "low", None)
    close = getattr(bar, "close", None)
    if high is None or low is None or close is None:
        return None
    return (float(high) + float(low) + float(close)) / 3.0


def fetch_ib_1m_bars(
    symbol: str,
    trade_date: date,
    host: str,
    port: int,
    client_id: int,
    timeout: float,
    primary_exchange: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    try:
        from ib_insync import IB, Stock
    except ModuleNotFoundError as exc:
        raise RuntimeError("ib_insync is required. Install backend requirements or use the existing TWS venv.") from exc

    ib = IB()
    ib.connect(host, port, clientId=client_id, timeout=timeout)
    try:
        contract = Stock(symbol, "SMART", "USD", primaryExchange=primary_exchange)
        qualified = ib.qualifyContracts(contract)
        if not qualified:
            raise RuntimeError(f"IBKR could not qualify contract for {symbol}")
        contract = qualified[0]

        end_dt = datetime.combine(trade_date, SESSION_END, tzinfo=ET)
        request = {
            "endDateTime": end_dt.isoformat(),
            "durationStr": "1 D",
            "barSizeSetting": "1 min",
            "whatToShow": "TRADES",
            "useRTH": False,
            "formatDate": 2,
        }
        ib_end = datetime.combine(trade_date, SESSION_END, tzinfo=ET)
        bars = ib.reqHistoricalData(
            contract,
            endDateTime=ib_end,
            durationStr=request["durationStr"],
            barSizeSetting=request["barSizeSetting"],
            whatToShow=request["whatToShow"],
            useRTH=request["useRTH"],
            formatDate=request["formatDate"],
            keepUpToDate=False,
            timeout=60,
        )
    finally:
        ib.disconnect()

    rows: list[dict[str, Any]] = []
    for bar in bars:
        dt = to_et(getattr(bar, "date"))
        if not in_extended_session(dt, trade_date):
            continue
        rows.append({
            "ts": dt.isoformat(),
            "t": dt.strftime("%H:%M"),
            "O": float(bar.open),
            "H": float(bar.high),
            "L": float(bar.low),
            "C": float(bar.close),
            "V": float(bar.volume or 0),
            "vw": bar_source_vwap(bar),
        })

    rows.sort(key=lambda row: row["ts"])
    contract_meta = {
        "conId": getattr(contract, "conId", None),
        "symbol": getattr(contract, "symbol", symbol),
        "secType": getattr(contract, "secType", "STK"),
        "exchange": getattr(contract, "exchange", "SMART"),
        "primaryExchange": getattr(contract, "primaryExchange", primary_exchange),
        "currency": getattr(contract, "currency", "USD"),
    }
    return rows, contract_meta, request


def fetch_prior_closes(table: str, ticker: str, trade_date: date, session_mode: str) -> list[float | None]:
    if table not in {"bars_1m", "bars_5m"}:
        raise ValueError(f"Unsupported bars table: {table}")
    init_db()
    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT {table}.close
            FROM {table}
            JOIN market_days ON market_days.id = {table}.market_day_id
            WHERE market_days.ticker=?
              AND market_days.session_mode=?
              AND market_days.trade_date<?
              AND {table}.close IS NOT NULL
            ORDER BY market_days.trade_date DESC, {table}.idx DESC
            LIMIT ?
            """,
            (ticker, session_mode, trade_date.isoformat(), max(BAR_MA_WINDOWS) - 1),
        ).fetchall()
    return [row["close"] for row in reversed(rows)]


def expected_minutes(trade_date: date) -> list[datetime]:
    cursor = datetime.combine(trade_date, SESSION_START, tzinfo=ET)
    end = datetime.combine(trade_date, SESSION_END, tzinfo=ET)
    minutes = []
    while cursor < end:
        minutes.append(cursor)
        cursor += timedelta(minutes=1)
    return minutes


def missing_minutes(bars: list[dict[str, Any]], trade_date: date) -> list[str]:
    actual = {bar["ts"][:16] for bar in bars}
    return [
        minute.strftime("%Y-%m-%dT%H:%M")
        for minute in expected_minutes(trade_date)
        if minute.isoformat()[:16] not in actual
    ]


def session_counts(bars_1m: list[dict[str, Any]], bars_5m: list[dict[str, Any]]) -> dict[str, int]:
    rth_start = RTH_START.strftime("%H:%M")
    rth_end = RTH_END.strftime("%H:%M")
    premarket_1m = sum(1 for bar in bars_1m if bar["t"] < rth_start)
    rth_1m = sum(1 for bar in bars_1m if rth_start <= bar["t"] < rth_end)
    afterhours_1m = sum(1 for bar in bars_1m if bar["t"] >= rth_end)
    premarket_5m = sum(1 for bar in bars_5m if bar["t"] < rth_start)
    return {
        "bars_1m": len(bars_1m),
        "bars_5m": len(bars_5m),
        "premarket_1m": premarket_1m,
        "rth_1m": rth_1m,
        "afterhours_1m": afterhours_1m,
        "premarket_5m": premarket_5m,
    }


def build_payload(
    symbol: str,
    trade_date: date,
    source_bars_1m: list[dict[str, Any]],
    contract_meta: dict[str, Any],
    ib_request: dict[str, Any],
    host: str,
    port: int,
) -> dict[str, Any]:
    if not source_bars_1m:
        raise RuntimeError(f"No {symbol} 1m bars returned for {trade_date}")

    session_mode = "extended"
    prior_1m_closes = fetch_prior_closes("bars_1m", symbol, trade_date, session_mode)
    prior_5m_closes = fetch_prior_closes("bars_5m", symbol, trade_date, session_mode)

    bars_5m = build_5m_bars_from_1m(source_bars_1m, source_vwap_mode="bar_price")
    bars_5m = recalculate_ma_fields(bars_5m, warmup_closes=prior_5m_closes, preserve_warmup_values=False)

    bars_1m = normalize_session_vwap(source_bars_1m, source_vwap_mode="bar_price")
    bars_1m = add_heikin_ashi_fields(bars_1m)
    bars_1m = recalculate_ma_fields(bars_1m, warmup_closes=prior_1m_closes, preserve_warmup_values=False)

    gaps = missing_minutes(bars_1m, trade_date)
    counts = session_counts(bars_1m, bars_5m)
    counts_without_5m_premarket = {key: value for key, value in counts.items() if key != "premarket_5m"}
    return {
        "meta": {
            "title": f"{symbol} {trade_date.isoformat()} Full Day",
            "ticker": symbol,
            "date": trade_date.isoformat(),
            "source": f"Interactive Brokers Gateway historicalData {host}:{port}",
            "provider": "ibkr",
            "ib_contract": contract_meta,
            "ib_request": ib_request,
            "session_mode": session_mode,
            "session_window": "04:00-20:00 ET",
            "session_type": "full_session" if not gaps else "full_session_gappy",
            "gap_count": len(gaps),
            "missing_minutes": gaps,
            "warmup_complete": {
                "1m": counts["premarket_1m"] >= max(BAR_MA_WINDOWS),
                "5m": counts["premarket_5m"] >= max(BAR_MA_WINDOWS),
            },
            "counts": counts_without_5m_premarket,
            "generated_at": datetime.now().isoformat(),
            "vwap_mode": "session_cumulative",
            "vwap_session_anchor": "04:00 ET extended session",
            "vwap_source": "IB historicalData average weighted by volume; typical price fallback",
        },
        "bars_1m": bars_1m,
        "bars_5m": bars_5m,
    }


def write_payload(payload: dict[str, Any], output_dir: Path) -> Path:
    meta = payload["meta"]
    path = output_dir / meta["date"] / f"{meta['ticker']}_{meta['date']}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch one supported symbol extended-session day from IBKR and import it."
    )
    parser.add_argument("date", help="Trade date, YYYY-MM-DD.")
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--host", default=settings.ibkr_host)
    parser.add_argument("--port", type=int, default=settings.ibkr_port)
    parser.add_argument("--client-id", type=int, default=42)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--primary-exchange", default="ARCA")
    parser.add_argument("--output-dir", type=Path, default=settings.live_extended_dir)
    parser.add_argument("--skip-import", action="store_true")
    args = parser.parse_args()

    trade_date = parse_trade_date(args.date)
    symbol = args.symbol.upper()
    rows, contract_meta, ib_request = fetch_ib_1m_bars(
        symbol=symbol,
        trade_date=trade_date,
        host=args.host,
        port=args.port,
        client_id=args.client_id,
        timeout=args.timeout,
        primary_exchange=args.primary_exchange,
    )
    payload = build_payload(
        symbol=symbol,
        trade_date=trade_date,
        source_bars_1m=rows,
        contract_meta=contract_meta,
        ib_request=ib_request,
        host=args.host,
        port=args.port,
    )
    output_path = write_payload(payload, args.output_dir)
    market_day_id = None if args.skip_import else import_market_json(output_path)
    counts = payload["meta"]["counts"]
    print(
        f"Wrote {output_path} with {counts['bars_1m']} 1m bars, {counts['bars_5m']} 5m bars, "
        f"gaps={payload['meta']['gap_count']}, market_day_id={market_day_id}"
    )


if __name__ == "__main__":
    main()
