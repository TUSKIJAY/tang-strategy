from __future__ import annotations

import json
import re
from typing import Any

from ..settings import settings


def _slug_part(value: Any) -> str:
    text = str(value or "").strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _option_code(side: str) -> str:
    return "P" if side == "PUT" else "C"


def _normalize_trade(raw: dict[str, Any], index: int, ticker: str, trade_date: str) -> dict[str, Any]:
    side = str(raw.get("side") or raw.get("direction") or "").upper()
    side = "PUT" if side == "PUT" else "CALL"
    strike = raw.get("strike")
    time = str(raw.get("time") or "").strip()
    expiry = str(raw.get("expiry") or trade_date)
    trade_id = raw.get("id") or "-".join(
        filter(
            None,
            [
                "tang",
                ticker.lower(),
                _slug_part(trade_date),
                _slug_part(time),
                _slug_part(strike),
                _option_code(side).lower(),
                str(index + 1),
            ],
        )
    )

    return {
        "id": trade_id,
        "time": time,
        "symbol": str(raw.get("symbol") or ticker).upper(),
        "side": side,
        "strike": strike,
        "expiry": expiry,
        "action": raw.get("action") or "buy_open",
        "source": raw.get("source") or "manual",
        "reason_type": raw.get("reason_type") or "unknown",
        "note": raw.get("note") or "",
    }


def load_tang_trades(ticker: str, trade_date: str) -> dict[str, Any]:
    """Load optional Tang real-trade notes without coupling them to market seed data."""
    normalized_ticker = ticker.upper()
    path = settings.content_dir / "trader-trades" / f"{trade_date}.json"
    if not path.exists():
        return {
            "ticker": normalized_ticker,
            "date": trade_date,
            "trades": [],
            "notes": [],
        }

    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_trades = payload.get("trades") or []
    trades = [
        _normalize_trade(raw, index, normalized_ticker, trade_date)
        for index, raw in enumerate(raw_trades)
        if str(raw.get("symbol") or normalized_ticker).upper() == normalized_ticker
    ]
    return {
        "ticker": str(payload.get("ticker") or normalized_ticker).upper(),
        "date": str(payload.get("date") or trade_date),
        "trades": trades,
        "notes": payload.get("notes") or [],
    }
