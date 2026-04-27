"""
Task 0: Polygon 历史 1min 数据拉取（D8=A+ 主路径）

参见 plan: ../../docs/planning/v0.6-data-foundation/data-foundation-plan.md#task-0
HANDOFF: ../state/HANDOFF.md

范围（2026-04-23 用户选窄）: 2025-10-01 ~ 2026-04-11

凭据规范（plan 0a）：
- 只读 os.environ["POLYGON_API_KEY"]，未设置 fail-fast
- 不打印 key；failure log / acceptance 不粘含 key 的 URL

本版本职责（Task 0 分两阶段；此处只做 Phase 1 = 纯 fetch）：
- per-day API 调用、per-day CSV 落到 state/task0_daily/
- 每日 flush state/task0_progress.json（单日级断点续跑，H3）
- 主路径重试 3 次（指数退避，H4）；仍失败登记到 failed
- 循环结束后 concat 所有 done 日 CSV → raw/bulk/SPY_1min_<start>_<end>.continuous.csv
- gap-fill 合成与 synthetic_fallback JSON 留给 Task 1（build_json.py --batch），避免在此重复 build_json 的 HA/MA/VWAP 逻辑

输出列对齐现有 bulk CSV（extended hours 全保留）:
timestamp,date,time,open,high,low,close,volume,vwap,trades
"""

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import requests


SYMBOL = "SPY"
API_BASE = "https://api.polygon.io/v2/aggs/ticker"
RATE_LIMIT_SLEEP = 13
MAX_RETRIES = 3
BACKOFF_BASE = 2

SCRIPT_DIR = Path(__file__).resolve().parent
V6_DIR = SCRIPT_DIR.parent
STATE_DIR = V6_DIR / "state"
DAILY_CSV_DIR = STATE_DIR / "task0_daily"
PROGRESS_FILE = STATE_DIR / "task0_progress.json"

DREAM_BIGGER_DIR = V6_DIR.parent.parent
RAW_BULK_DIR = DREAM_BIGGER_DIR / "data" / "raw" / "bulk"

CSV_COLS = ["timestamp", "date", "time", "open", "high", "low", "close", "volume", "vwap", "trades"]


def _require_api_key() -> str:
    key = os.environ.get("POLYGON_API_KEY")
    if not key:
        print("ERROR: POLYGON_API_KEY 环境变量未设置", file=sys.stderr)
        print("       export POLYGON_API_KEY='<your-key>'", file=sys.stderr)
        sys.exit(2)
    return key


def _load_state() -> dict:
    if not PROGRESS_FILE.exists():
        return {
            "done": [],
            "holidays": [],
            "failed": [],
            "gappy": [],
            "short": [],
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "last_update": None,
            "range": None,
        }
    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict) -> None:
    state["last_update"] = datetime.now().isoformat(timespec="seconds")
    tmp = PROGRESS_FILE.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    tmp.replace(PROGRESS_FILE)


def _weekdays_in_range(start: date, end: date):
    cur = start
    while cur <= end:
        if cur.weekday() < 5:
            yield cur
        cur += timedelta(days=1)


def _fetch_day(api_key: str, day: date) -> Optional[list]:
    """返回 Polygon results 列表；失败抛异常。空结果返回 []。"""
    d = day.isoformat()
    url = f"{API_BASE}/{SYMBOL}/range/1/minute/{d}/{d}"
    params = {"adjusted": "true", "sort": "asc", "limit": 50000, "apiKey": api_key}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    status = data.get("status")
    if status == "ERROR":
        msg = data.get("error") or data.get("message") or "unknown"
        raise RuntimeError(f"Polygon API ERROR: {msg}")
    return data.get("results") or []


def _results_to_df(results: list) -> pd.DataFrame:
    if not results:
        return pd.DataFrame(columns=CSV_COLS)
    df = pd.DataFrame(results)
    ts_utc = pd.to_datetime(df["t"], unit="ms", utc=True)
    ts_et = ts_utc.dt.tz_convert("America/New_York").dt.tz_localize(None)
    out = pd.DataFrame({
        "timestamp": ts_et.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "date": ts_et.dt.strftime("%Y-%m-%d"),
        "time": ts_et.dt.strftime("%H:%M"),
        "open": df["o"],
        "high": df["h"],
        "low": df["l"],
        "close": df["c"],
        "volume": df["v"],
        "vwap": df.get("vw"),
        "trades": df.get("n"),
    })
    return out.sort_values("timestamp").reset_index(drop=True)


def _rth_bar_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rth = df[(df["time"] >= "09:30") & (df["time"] <= "15:59")]
    return len(rth)


def _classify(rth_count: int) -> str:
    if rth_count == 0:
        return "holiday"
    if 380 <= rth_count <= 390:
        return "clean_or_gappy"
    if 200 <= rth_count < 380:
        return "short"
    return "invalid"


def _fetch_with_retry(api_key: str, day: date) -> list:
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return _fetch_day(api_key, day)
        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES:
                sleep_s = BACKOFF_BASE ** attempt
                print(f"  retry {attempt}/{MAX_RETRIES-1} after {sleep_s}s ({type(exc).__name__}: {exc})", flush=True)
                time.sleep(sleep_s)
    raise last_exc


def _concat_and_write_bulk(start: date, end: date, state: dict) -> Optional[Path]:
    out_name = f"SPY_1min_{start.isoformat()}_{end.isoformat()}.continuous.csv"
    out_path = RAW_BULK_DIR / out_name
    done = state.get("done", [])
    if not done:
        print("没有 done 日期，跳过 concat")
        return None

    frames = []
    for d in sorted(done):
        p = DAILY_CSV_DIR / f"SPY_{d}.csv"
        if not p.exists():
            print(f"  [WARN] 日状态=done 但 CSV 缺失: {p.name}")
            continue
        frames.append(pd.read_csv(p, dtype={"date": str, "time": str}))
    if not frames:
        print("所有 done 日的 CSV 都缺失，未写 bulk")
        return None
    big = pd.concat(frames, ignore_index=True)
    big = big[CSV_COLS]
    RAW_BULK_DIR.mkdir(parents=True, exist_ok=True)
    big.to_csv(out_path, index=False)
    print(f"写入 bulk: {out_path.relative_to(DREAM_BIGGER_DIR)} ({len(big)} 行)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Task 0: Polygon per-day fetch")
    parser.add_argument("--start", default="2025-10-01")
    parser.add_argument("--end", default="2026-04-11")
    parser.add_argument("--force", action="store_true", help="重拉 done 日")
    parser.add_argument("--limit", type=int, default=None, help="仅处理前 N 个待办日（调试用）")
    parser.add_argument("--no-concat", action="store_true", help="循环结束后不 concat 到 bulk CSV")
    args = parser.parse_args()

    api_key = _require_api_key()
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    if end < start:
        print("ERROR: --end 早于 --start", file=sys.stderr)
        sys.exit(2)

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_CSV_DIR.mkdir(parents=True, exist_ok=True)

    state = _load_state()
    state["range"] = {"start": args.start, "end": args.end}
    if args.force:
        state["done"] = []
        state["holidays"] = []
        state["gappy"] = []
        state["short"] = []
        state["failed"] = []
    _save_state(state)

    done_set = set(state.get("done", []))
    holiday_set = set(state.get("holidays", []))
    failed_set = set(state.get("failed", []))

    todo = [d for d in _weekdays_in_range(start, end)
            if d.isoformat() not in done_set
            and d.isoformat() not in holiday_set]
    if args.limit:
        todo = todo[: args.limit]

    total_planned = sum(1 for _ in _weekdays_in_range(start, end))
    print(f"范围 {args.start} ~ {args.end}")
    print(f"工作日共 {total_planned} 天；已完成 {len(done_set)} clean+gappy+short，已知节假日 {len(holiday_set)}，失败 {len(failed_set)}")
    print(f"本轮计划拉取 {len(todo)} 天（rate limit: {RATE_LIMIT_SLEEP}s/call）")
    if not todo:
        print("无待办日期，直接进入 concat 阶段")

    t0 = time.time()
    for idx, day in enumerate(todo, 1):
        d_str = day.isoformat()
        print(f"[{idx}/{len(todo)}] {d_str} ...", end="", flush=True)

        try:
            results = _fetch_with_retry(api_key, day)
        except Exception as exc:
            msg = f"{type(exc).__name__}: {exc}"
            print(f" FAILED ({msg})", flush=True)
            if d_str not in failed_set:
                state.setdefault("failed", []).append(d_str)
                failed_set.add(d_str)
            _save_state(state)
            time.sleep(RATE_LIMIT_SLEEP)
            continue

        df = _results_to_df(results)
        rth_n = _rth_bar_count(df)
        cls = _classify(rth_n)

        if cls == "holiday":
            state.setdefault("holidays", []).append(d_str)
            holiday_set.add(d_str)
            print(f" holiday (0 bars)", flush=True)
        else:
            csv_path = DAILY_CSV_DIR / f"SPY_{d_str}.csv"
            df.to_csv(csv_path, index=False)
            state.setdefault("done", []).append(d_str)
            done_set.add(d_str)
            tag = cls
            if cls == "clean_or_gappy":
                tag = "full(≥380)"
            print(f" {tag} ({rth_n} RTH bars, total {len(df)})", flush=True)
            if cls == "short":
                state.setdefault("short", []).append(d_str)
            # clean vs gappy 的 gap 判定要看具体 RTH 连续性，
            # 这里先不在 Task 0 里严判，留给 Task 1 batch 输出 meta.gap_count

        _save_state(state)
        if idx < len(todo):
            time.sleep(RATE_LIMIT_SLEEP)

    elapsed = time.time() - t0
    print(f"\nFetch 结束。耗时 {elapsed:.1f}s；done={len(state.get('done',[]))} holidays={len(state.get('holidays',[]))} failed={len(state.get('failed',[]))} short={len(state.get('short',[]))}")

    if not args.no_concat:
        _concat_and_write_bulk(start, end, state)


if __name__ == "__main__":
    main()
