from __future__ import annotations

import contextlib
import json
import secrets
import shutil
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .auth import create_token, require_admin, require_readonly, role_from_password
from .db import connect, init_db, replace_trade_repository, rows_to_dicts
from .services.importer import import_default_seed, import_market_json, import_strategy_json
from .services.bar_utils import BAR_MA_WINDOWS, bar_row_to_payload, build_5m_bars_from_1m, recalculate_ma_fields
from .services.db_safety import (
    bar_market_day_join,
    bar_owner,
    create_consistent_snapshot,
    promote_candidate,
    validate_sqlite,
)
from .services.trade_records import (
    TradeAuthorizationError,
    TradeValidationError,
    handle_trade_day_admin_read,
    handle_trade_day_admin_write,
    handle_trade_records_read,
    handle_trader_registry_admin_read,
    handle_trader_registry_admin_write,
)
from .settings import settings

app = FastAPI(title="Tang Strategy API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BAR_SELECT_COLUMNS = (
    "idx, ts, time, open, high, low, close, volume, vwap, "
    "ha_open, ha_high, ha_low, ha_close, m5, m10, m20, m30, m50, m60, m120, m200, m250"
)


class LoginRequest(BaseModel):
    password: str


class ImportPathRequest(BaseModel):
    path: str


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "db": str(settings.db_path)}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict[str, str]:
    role = role_from_password(payload.password)
    if role is None:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"token": create_token(role), "role": role}


@app.get("/api/tickers")
def tickers(_: str = Depends(require_readonly)) -> list[dict]:
    with connect() as conn:
        return rows_to_dicts(conn.execute("SELECT symbol, name, asset_type, enabled FROM tickers WHERE enabled=1 ORDER BY symbol"))


@app.get("/api/market-days")
def market_days(ticker: str | None = None, date_from: str | None = None, date_to: str | None = None, _: str = Depends(require_readonly)) -> list[dict]:
    sql = "SELECT id, ticker, trade_date, session_mode, source, title, bar_count_1m, bar_count_5m, imported_at FROM market_days WHERE 1=1"
    params: list[Any] = []
    if ticker:
        sql += " AND ticker=?"
        params.append(ticker.upper())
    if date_from:
        sql += " AND trade_date>=?"
        params.append(date_from)
    if date_to:
        sql += " AND trade_date<=?"
        params.append(date_to)
    sql += " ORDER BY trade_date DESC, ticker"
    with connect() as conn:
        return rows_to_dicts(conn.execute(sql, params))


@app.get("/api/market-days/{market_day_id}")
def market_day(market_day_id: int, _: str = Depends(require_readonly)) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM market_days WHERE id=?", (market_day_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Market day not found")
        result = dict(row)
        result["meta"] = json.loads(result.pop("meta_json") or "{}")
        return result


@app.get("/api/market-days/{market_day_id}/bars")
def bars(market_day_id: int, timeframe: str = "1m", _: str = Depends(require_readonly)) -> dict[str, Any]:
    if timeframe not in {"1m", "5m"}:
        raise HTTPException(status_code=400, detail="timeframe must be 1m or 5m")
    with connect() as conn:
        day = conn.execute("SELECT * FROM market_days WHERE id=?", (market_day_id,)).fetchone()
        if not day:
            raise HTTPException(status_code=404, detail="Market day not found")
        bars_1m_rows = _fetch_bar_rows(conn, "bars_1m", market_day_id)
        if timeframe == "1m":
            bars_payload = [bar_row_to_payload(row) for row in bars_1m_rows]
        else:
            bars_payload = _build_5m_payload(conn, day, bars_1m_rows)
        return {
            "market_day": {
                "id": day["id"],
                "ticker": day["ticker"],
                "trade_date": day["trade_date"],
                "session_mode": day["session_mode"],
                "meta": json.loads(day["meta_json"] or "{}"),
            },
            "timeframe": timeframe,
            "bars": bars_payload,
        }


@app.get("/api/strategies")
def strategies(_: str = Depends(require_readonly)) -> list[dict]:
    with connect() as conn:
        return rows_to_dicts(conn.execute(
            "SELECT id, name, version, slug, description, source_type, active, updated_at FROM strategies WHERE active=1 ORDER BY name, version"
        ))


@app.get("/api/strategies/{strategy_id}")
def strategy(strategy_id: int, _: str = Depends(require_readonly)) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM strategies WHERE id=? AND active=1", (strategy_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Strategy not found")
        result = dict(row)
        result["json"] = json.loads(result.pop("json_body"))
        return result


@app.get("/api/reviews/assemble")
def assemble_review(market_day_id: int, strategy_id: int, _: str = Depends(require_readonly)) -> dict[str, Any]:
    with connect() as conn:
        day = conn.execute("SELECT * FROM market_days WHERE id=?", (market_day_id,)).fetchone()
        if not day:
            raise HTTPException(status_code=404, detail="Market day not found")
        strategy_row = conn.execute("SELECT * FROM strategies WHERE id=? AND active=1", (strategy_id,)).fetchone()
        if not strategy_row:
            raise HTTPException(status_code=404, detail="Strategy not found")
        bars_1m_rows = _fetch_bar_rows(conn, "bars_1m", market_day_id)
        bars_5m = _build_5m_payload(conn, day, bars_1m_rows)
        strategy_json = json.loads(strategy_row["json_body"])
        trade_records = _trade_records_for_day(day["ticker"], day["trade_date"])
        meta = json.loads(day["meta_json"] or "{}")
        meta.update({
            "ticker": day["ticker"],
            "date": day["trade_date"],
            "session_mode": day["session_mode"],
            "source": day["source"],
            "counts": {
                "bars_1m": len(bars_1m_rows),
                "bars_5m": len(bars_5m),
                "trade_groups": trade_records["counts"]["trade_groups_total"],
            },
            "strategy": {
                "id": strategy_row["id"],
                "name": strategy_row["name"],
                "version": strategy_row["version"],
                "slug": strategy_row["slug"],
            },
        })
        return {
            "meta": meta,
            "market_day": {
                "id": day["id"],
                "ticker": day["ticker"],
                "trade_date": day["trade_date"],
                "session_mode": day["session_mode"],
                "title": day["title"],
            },
            "strategy": {
                "id": strategy_row["id"],
                "name": strategy_row["name"],
                "version": strategy_row["version"],
                "slug": strategy_row["slug"],
                "description": strategy_row["description"],
                "json": strategy_json,
            },
            "bars_1m": [bar_row_to_payload(row) for row in bars_1m_rows],
            "bars_5m": bars_5m,
            "annotations_1m": [],
            "annotations_5m": [],
            "trade_records": trade_records,
        }


@app.get("/api/trade-records")
def trade_records(
    ticker: str,
    trade_date: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    trader_id: list[str] | None = Query(default=None),
    status: list[str] | None = Query(default=None),
    review_status: list[str] | None = Query(default=None),
    eligibility: str | None = None,
    role: str = Depends(require_readonly),
) -> list[dict[str, Any]]:
    try:
        return handle_trade_records_read(
            role,
            settings.content_dir,
            ticker,
            trade_date=trade_date,
            date_from=date_from,
            date_to=date_to,
            trader_ids=trader_id,
            statuses=status,
            review_statuses=review_status,
            eligibility=eligibility,
        )
    except (TradeValidationError, TradeAuthorizationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/admin/traders")
def read_traders(role: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return handle_trader_registry_admin_read(role, settings.content_dir)
    except (TradeValidationError, TradeAuthorizationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/admin/trade-records")
def read_trade_records(trade_date: str, role: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return handle_trade_day_admin_read(role, settings.content_dir, trade_date)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (TradeValidationError, TradeAuthorizationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/api/admin/traders")
def update_traders(payload: dict[str, Any], role: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return handle_trader_registry_admin_write(
            role,
            settings.content_dir,
            payload,
            after_replace=_sync_trade_projection,
        )
    except (TradeValidationError, TradeAuthorizationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.put("/api/admin/trade-records")
def update_trade_records(payload: dict[str, Any], role: str = Depends(require_admin)) -> dict[str, Any]:
    try:
        return handle_trade_day_admin_write(
            role,
            settings.content_dir,
            payload,
            after_replace=_sync_trade_projection,
        )
    except (TradeValidationError, TradeAuthorizationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/teaching/{asset_type}")
def teaching_asset(asset_type: str, _: str = Depends(require_readonly)) -> dict:
    with connect() as conn:
        row = conn.execute(
            "SELECT json_body FROM teaching_assets WHERE asset_type=? ORDER BY updated_at DESC LIMIT 1",
            (asset_type,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Teaching asset not found")
        return json.loads(row["json_body"])


@app.post("/api/admin/import/seed")
def admin_import_seed(_: str = Depends(require_admin)) -> dict[str, int]:
    return import_default_seed()


@app.post("/api/admin/import/market-json")
def admin_import_market(payload: ImportPathRequest, _: str = Depends(require_admin)) -> dict[str, int]:
    path = _safe_repo_path(payload.path, settings.seed_dir)
    return {"market_day_id": import_market_json(path)}


@app.post("/api/admin/import/strategy-json")
def admin_import_strategy(payload: ImportPathRequest, _: str = Depends(require_admin)) -> dict[str, int]:
    path = _safe_repo_path(payload.path, settings.strategies_dir)
    return {"strategy_id": import_strategy_json(path)}


def _safe_repo_path(raw_path: str, allowed_root: Path) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    resolved = path.resolve()
    allowed = allowed_root.resolve()
    if allowed not in resolved.parents and resolved != allowed:
        raise HTTPException(status_code=400, detail="Path is outside allowed import root")
    if not resolved.exists() or resolved.suffix != ".json":
        raise HTTPException(status_code=400, detail="JSON file not found")
    return resolved


def _trade_records_for_day(ticker: str, trade_date: str) -> dict[str, Any]:
    payloads = handle_trade_records_read(
        "readonly",
        settings.content_dir,
        ticker,
        trade_date=trade_date,
    )
    if len(payloads) != 1:
        raise RuntimeError(
            f"Expected one trade-record payload for {ticker}|{trade_date}; found {len(payloads)}"
        )
    return payloads[0]


def _sync_trade_projection() -> dict[str, Any]:
    from .services.trade_records import load_trader_registry, validate_trade_repository

    live = settings.db_path.expanduser().resolve()
    nonce = secrets.token_hex(6)
    candidate = live.parent / f".{live.stem}.trade-sync-{nonce}.candidate.db"
    backup = live.parent / f".{live.stem}.trade-sync-{nonce}.backup.db"
    promoted = False
    cleanup_warnings: list[str] = []
    try:
        baseline = create_consistent_snapshot(live, backup)
        shutil.copy2(backup, candidate)
        registry = load_trader_registry(settings.content_dir / "traders" / "index.json")
        days = validate_trade_repository(
            (settings.content_dir / "trades").glob("*.json"),
            registry,
        )
        counts = replace_trade_repository(candidate, registry, days)

        def validate_projection(path: Path) -> None:
            validate_sqlite(path)
            # contextlib.closing is required: sqlite3's context manager only
            # scopes the transaction, and an unclosed handle on the promoted
            # live DB blocks later file operations on Windows.
            with contextlib.closing(connect(path)) as connection:
                actual = {
                    table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                    for table in counts
                }
            if actual != counts:
                raise RuntimeError(
                    f"Promoted trade projection count mismatch: expected={counts} actual={actual}"
                )

        promote_candidate(live, candidate, baseline, backup, validate_projection)
        promoted = True
        if backup.exists():
            try:
                backup.unlink()
            except Exception as exc:
                cleanup_warnings.append(f"verified DB backup cleanup failed: {exc}")
        return {
            "promoted": True,
            "trade_days": len(days),
            "counts": counts,
            "cleanup_warnings": cleanup_warnings,
        }
    finally:
        if candidate.exists() and not promoted:
            candidate.unlink()
        if backup.exists() and not promoted:
            backup.unlink()


def _fetch_bar_rows(conn, table: str, market_day_id: int) -> list[Any]:
    owner_column, owner_id = bar_owner(conn, market_day_id)
    return conn.execute(
        f"SELECT {owner_column} AS market_day_id, {BAR_SELECT_COLUMNS} "
        f"FROM {table} WHERE {owner_column}=? ORDER BY idx",
        (owner_id,),
    ).fetchall()


def _fetch_stored_bar_payload(conn, table: str, market_day_id: int) -> list[dict[str, Any]]:
    rows = _fetch_bar_rows(conn, table, market_day_id)
    return [bar_row_to_payload(row) for row in rows]


def _build_5m_payload(conn, day: Any, bars_1m_rows: list[Any]) -> list[dict[str, Any]]:
    stored_bars = _fetch_stored_bar_payload(conn, "bars_5m", day["id"])
    bars = (
        stored_bars
        if stored_bars
        else build_5m_bars_from_1m(bars_1m_rows, source_vwap_mode="session_cumulative")
    )
    return recalculate_ma_fields(bars, warmup_closes=_fetch_prior_5m_closes(conn, day))


def _fetch_prior_5m_closes(conn, day: Any) -> list[float | None]:
    join = bar_market_day_join(conn, "bars_5m")
    rows = conn.execute(
        f"""
        SELECT bars_5m.close
        {join}
        WHERE market_days.ticker=?
          AND market_days.session_mode=?
          AND market_days.trade_date<?
          AND bars_5m.close IS NOT NULL
        ORDER BY market_days.trade_date DESC, bars_5m.idx DESC
        LIMIT ?
        """,
        (day["ticker"], day["session_mode"], day["trade_date"], max(BAR_MA_WINDOWS) - 1),
    ).fetchall()
    return [row["close"] for row in reversed(rows)]
