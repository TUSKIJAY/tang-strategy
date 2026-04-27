"""
slice_teaching_segment.py — 从 processed/SPY_YYYY-MM-DD.json 切教学窗口

参见 plan: docs/planning/v0.6-data-foundation/data-foundation-plan.md#task-2

CLI 示例：
  python slice_teaching_segment.py \
    --date 2026-01-07 \
    --start 11:35 --end 12:11 \
    --preheat 30 \
    --title "MA10 首次拒绝" \
    --out processed/teaching/seg_0107_reject.json

窗口语义（plan Task 2）：
- 1m 闭区间 `[start - preheat * 1min, end]`
- 5m 默认从当日 RTH 09:30 开始到包含 end 的 5m bucket 为止
- 跨日 preheat 从 processed/ 里前一交易日 JSON 尾部取（优先 gap_count==0）

错误处理：
- 缺当日 / 前日 JSON → 报错指引 build_json.py
- start 在缺口里 → 默认报错；--allow-gappy-slice 时 fallback 到晚于 start 的最近一根
- synthetic_fallback/ 下的源默认拒读；--allow-synthetic 显式开启
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = SCRIPT_DIR / "processed"
SYNTHETIC_DIR = PROCESSED_DIR / "synthetic_fallback"
DATE_JSON_RE = re.compile(r"^SPY_(\d{4}-\d{2}-\d{2})\.json$")


class SliceError(Exception):
    pass


def _minute_offset(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _parse_time_arg(s: str) -> str:
    if not re.match(r"^\d{1,2}:\d{2}$", s):
        raise argparse.ArgumentTypeError(f"期望 HH:MM 格式，收到 {s!r}")
    h, m = s.split(":")
    return f"{int(h):02d}:{int(m):02d}"


def _load_day_json(date: str, allow_synthetic: bool) -> tuple[dict, bool]:
    """优先读 processed/；落到 synthetic_fallback/ 需 --allow-synthetic。"""
    primary = PROCESSED_DIR / f"SPY_{date}.json"
    fallback = SYNTHETIC_DIR / f"SPY_{date}.json"
    if primary.exists():
        with primary.open("r", encoding="utf-8") as f:
            return json.load(f), False
    if fallback.exists():
        if not allow_synthetic:
            raise SliceError(
                f"source {date} only in processed/synthetic_fallback/ — pass --allow-synthetic to use"
            )
        with fallback.open("r", encoding="utf-8") as f:
            return json.load(f), True
    raise SliceError(
        f"processed/SPY_{date}.json not found — run build_json.py first"
    )


def _list_prev_candidates(target: str, allow_synthetic: bool) -> list[Path]:
    """所有 processed/（及可选 fallback）里早于 target 的 JSON，按日期降序。"""
    roots = [PROCESSED_DIR]
    if allow_synthetic:
        roots.append(SYNTHETIC_DIR)
    out = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.iterdir():
            m = DATE_JSON_RE.match(p.name)
            if not m:
                continue
            d = m.group(1)
            if d < target:
                out.append((d, p))
    out.sort(reverse=True)
    return [p for _, p in out]


def _find_prev_day_json(target: str, allow_synthetic: bool) -> dict | None:
    """优先选 gap_count == 0 的最近前日；否则 fallback 最近 + warning。"""
    candidates = _list_prev_candidates(target, allow_synthetic)
    for p in candidates:
        with p.open("r", encoding="utf-8") as f:
            j = json.load(f)
        if j["meta"].get("gap_count", 0) == 0:
            return j
    if candidates:
        with candidates[0].open("r", encoding="utf-8") as f:
            j = json.load(f)
        print(
            f"[WARN] 前日用的是 {j['meta']['date']}（gap_count={j['meta'].get('gap_count', '?')}）—"
            " 没有 gap_count==0 的候选",
            file=sys.stderr,
        )
        return j
    return None


def _find_start_idx(day_bars: list, start: str, allow_gappy: bool, date_str: str) -> int:
    """返回 day_bars 中 t == start 的下标；找不到且 allow_gappy=True 时退回到 t > start 最近一根。"""
    for i, b in enumerate(day_bars):
        if b["t"] == start:
            return i
    if not allow_gappy:
        raise SliceError(
            f"start time {start} is missing from source {date_str} (in gap). "
            f"Use --allow-gappy-slice to fall back to nearest later bar."
        )
    for i, b in enumerate(day_bars):
        if b["t"] >= start:
            print(
                f"[WARN] {date_str} start={start} 落在缺口中，fallback 到 {b['t']}",
                file=sys.stderr,
            )
            return i
    raise SliceError(f"no bar at or after {start} in {date_str}")


def _find_end_idx(day_bars: list, end: str, start_idx: int, date_str: str) -> int:
    for i in range(len(day_bars) - 1, -1, -1):
        if day_bars[i]["t"] <= end:
            if i >= start_idx:
                return i
            break
    raise SliceError(f"no bars in [{start_idx}, {end}] on {date_str}")


def _slice_5m(day_5m: list, start: str, end: str) -> tuple[list, int]:
    """返回 (bars_5m, initial_index_5m)。5m 首根从 RTH 09:30 开始，末根是包含 end 的 5m bucket。"""
    end_off = _minute_offset(end)
    end_bucket_off = (end_off // 5) * 5
    rth_open_off = _minute_offset("09:30")
    start_off = _minute_offset(start)

    out = []
    for b in day_5m:
        off = _minute_offset(b["t"])
        if rth_open_off <= off <= end_bucket_off:
            out.append(b)

    initial_index_5m = -1
    for i in range(len(out) - 1, -1, -1):
        if _minute_offset(out[i]["t"]) <= start_off:
            initial_index_5m = i
            break
    if initial_index_5m < 0 and out:
        initial_index_5m = 0  # start 早于 09:30 的边界兜底
    return out, initial_index_5m


def run_slice(args) -> dict:
    day_json, source_is_synthetic = _load_day_json(args.date, args.allow_synthetic)
    source_meta = day_json["meta"]
    source_gap_count = source_meta.get("gap_count", 0)

    day_bars_1m = day_json["bars_1m"]
    day_bars_5m = day_json["bars_5m"]

    if source_gap_count > 0:
        # 窗口内 gap 数要等切出来才能算；这里先打整日警告
        print(
            f"[WARN] source {args.date} has {source_gap_count} total gaps; 窗口内 gap 数待切片后计算",
            file=sys.stderr,
        )

    start_idx = _find_start_idx(day_bars_1m, args.start, args.allow_gappy_slice, args.date)
    end_idx = _find_end_idx(day_bars_1m, args.end, start_idx, args.date)

    # preheat
    need_from_day = min(args.preheat, start_idx)
    need_from_prev = args.preheat - need_from_day

    prev_json = None
    if need_from_prev > 0:
        prev_json = _find_prev_day_json(args.date, args.allow_synthetic)
        if prev_json is None:
            raise SliceError(
                f"prev day JSON not found for {args.date} "
                f"(need {need_from_prev} more bars). "
                f"Run: python build_json.py raw/bulk/...csv --batch"
            )
        prev_bars = prev_json["bars_1m"]
        if len(prev_bars) < need_from_prev:
            raise SliceError(
                f"prev day {prev_json['meta']['date']} only has {len(prev_bars)} bars, "
                f"need {need_from_prev}"
            )
        preheat_bars = prev_bars[-need_from_prev:] + day_bars_1m[:start_idx]
    else:
        preheat_bars = day_bars_1m[start_idx - args.preheat : start_idx]

    teach_bars = day_bars_1m[start_idx : end_idx + 1]
    bars_1m = preheat_bars + teach_bars
    initial_index_1m = len(preheat_bars)

    # 闭区间 minute count
    expected_bars_1m = args.preheat + (_minute_offset(args.end) - _minute_offset(args.start) + 1)
    actual_bars_1m = len(bars_1m)
    window_gap_count = expected_bars_1m - actual_bars_1m
    if window_gap_count > 0:
        print(
            f"[WARN] 窗口 [{args.start}, {args.end}] (preheat {args.preheat}): "
            f"expected {expected_bars_1m} actual {actual_bars_1m} window_gaps={window_gap_count}",
            file=sys.stderr,
        )

    bars_5m, initial_index_5m = _slice_5m(day_bars_5m, args.start, args.end)

    out = {
        "meta": {
            "title": args.title,
            "ticker": "SPY",
            "date": args.date,
            "source": "slice_teaching_segment.py",
            "initial_timeframe": "1m",
            "initial_index_1m": initial_index_1m,
            "initial_index_5m": initial_index_5m,
            "expected_bars_1m": expected_bars_1m,
            "actual_bars_1m": actual_bars_1m,
            "window_gap_count": window_gap_count,
            "source_gap_count": source_gap_count,
            "source_synthetic": source_is_synthetic,
            "window": {
                "start": args.start,
                "end": args.end,
                "preheat": args.preheat,
            },
            "generated_at": datetime.now().isoformat(timespec="seconds"),
        },
        "bars_1m": bars_1m,
        "bars_5m": bars_5m,
        "annotations_1m": [],
        "annotations_5m": [],
    }
    return out


def main():
    parser = argparse.ArgumentParser(
        description="从权威实盘 JSON 切出教学窗口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--start", required=True, type=_parse_time_arg, help="HH:MM 教学起点")
    parser.add_argument("--end", required=True, type=_parse_time_arg, help="HH:MM 教学终点")
    parser.add_argument("--preheat", type=int, default=30, help="1m 起点之前额外保留的 bar 数")
    parser.add_argument("--title", default="", help="meta.title")
    parser.add_argument("--out", type=Path, required=True, help="输出 JSON 路径")
    parser.add_argument(
        "--allow-gappy-slice", action="store_true",
        help="start 落缺口时 fallback 到最近后续 bar（默认报错）",
    )
    parser.add_argument(
        "--allow-synthetic", action="store_true",
        help="允许从 processed/synthetic_fallback/ 读源 JSON（默认拒读）",
    )
    args = parser.parse_args()

    if _minute_offset(args.start) > _minute_offset(args.end):
        print("ERROR: --start > --end", file=sys.stderr)
        sys.exit(2)
    if args.preheat < 0:
        print("ERROR: --preheat 必须 ≥ 0", file=sys.stderr)
        sys.exit(2)

    try:
        result = run_slice(args)
    except SliceError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    m = result["meta"]
    print(
        f"[OK] {args.date} {args.start}~{args.end} preheat={args.preheat} → {args.out}\n"
        f"     1m: {m['actual_bars_1m']}/{m['expected_bars_1m']} bars, "
        f"initial_index_1m={m['initial_index_1m']}\n"
        f"     5m: {len(result['bars_5m'])} bars, "
        f"initial_index_5m={m['initial_index_5m']}\n"
        f"     source_gap_count={m['source_gap_count']} "
        f"window_gap_count={m['window_gap_count']} "
        f"synthetic={m['source_synthetic']}"
    )


if __name__ == "__main__":
    main()
