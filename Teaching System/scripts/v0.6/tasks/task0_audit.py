"""
Task 0 数据审计脚本（独立可跑）

参见 plan: ../../docs/planning/v0.6-data-foundation/data-foundation-plan.md#0-数据底座现状
HANDOFF: ../state/HANDOFF.md

用途：
- 跑前：审计现有 bulk CSV 的连续性现状（重现 plan 第 0 节的 132/4/38/90 数据）
- 跑后：验证 Polygon 重拉后的 raw/bulk/*.continuous.csv 是否真的连续完整

分类口径（plan 0.2）：
- full_session_clean : 380 ≤ N ≤ 390 且 RTH 内连续无缺口
- full_session_gappy : 380 ≤ N ≤ 390 但有内部缺口
- short_session     : 200 ≤ N < 380
- invalid_session   : N < 200

输出：
- stdout: 分类统计表 + 少数样本
- 追加到 state/acceptance.md：完整审计报告（每日清单按分类列出）

CLI:
  python task0_audit.py                       # 自动探测：优先 continuous.csv，否则 state/task0_daily/
  python task0_audit.py --csv <path>          # 审计指定 CSV
  python task0_audit.py --daily-dir <path>    # 审计一个装 per-day CSV 的目录
  python task0_audit.py --compare-old         # 也跑一遍老 bulk，输出 diff
  python task0_audit.py --out <path>          # 追加报告到指定 .md（默认 state/acceptance.md）
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
V6_DIR = SCRIPT_DIR.parent
STATE_DIR = V6_DIR / "state"
DAILY_CSV_DIR = STATE_DIR / "task0_daily"
ACCEPTANCE_FILE = STATE_DIR / "acceptance.md"

DREAM_BIGGER_DIR = V6_DIR.parent.parent
RAW_BULK_DIR = DREAM_BIGGER_DIR / "data" / "raw" / "bulk"

# 让我们直接复用 build_json 的 load_csv
sys.path.insert(0, str(DREAM_BIGGER_DIR / "data"))
try:
    from build_json import load_csv  # type: ignore
except Exception as exc:
    print(f"ERROR: 无法 import build_json.load_csv: {exc}", file=sys.stderr)
    sys.exit(2)


def _classify_day(df_day: pd.DataFrame) -> tuple[str, int, int]:
    """
    返回 (session_type, bar_count, gap_count)
    gap_count = RTH 范围内 "相邻两根间隔 > 1min" 的次数
    """
    n = len(df_day)
    if n == 0:
        return ("invalid_session", 0, 0)

    ts = df_day["timestamp"].sort_values().reset_index(drop=True)
    diffs = ts.diff().dropna()
    gaps = int((diffs > pd.Timedelta(minutes=1)).sum())

    if n < 200:
        return ("invalid_session", n, gaps)
    if 200 <= n < 380:
        return ("short_session", n, gaps)
    # n in [380, 390+]
    if gaps == 0:
        return ("full_session_clean", n, 0)
    return ("full_session_gappy", n, gaps)


def _audit_dataframe(df: pd.DataFrame) -> dict:
    """按 date groupby 做每日分类统计。df 必须已经过 load_csv（RTH filter + tz）。"""
    buckets = {k: [] for k in
               ("full_session_clean", "full_session_gappy", "short_session", "invalid_session")}
    per_day_detail = []

    for d, grp in df.groupby("date", sort=True):
        cls, n, gaps = _classify_day(grp)
        ts_first = grp["timestamp"].min().strftime("%H:%M")
        ts_last = grp["timestamp"].max().strftime("%H:%M")
        buckets[cls].append(str(d))
        per_day_detail.append({
            "date": str(d),
            "session_type": cls,
            "bars": n,
            "gap_count": gaps,
            "first_bar": ts_first,
            "last_bar": ts_last,
        })

    return {
        "buckets": buckets,
        "per_day": per_day_detail,
        "total_days": len(per_day_detail),
        "total_bars": int(len(df)),
    }


def _format_summary(label: str, result: dict) -> str:
    b = result["buckets"]
    lines = [f"### {label}", ""]
    lines.append(f"总交易日：**{result['total_days']}** | 总 bar 数（RTH 过滤后）：**{result['total_bars']}**")
    lines.append("")
    lines.append("| 分类 | 天数 |")
    lines.append("|---|---|")
    for k in ("full_session_clean", "full_session_gappy", "short_session", "invalid_session"):
        lines.append(f"| `{k}` | {len(b[k])} |")
    lines.append("")
    return "\n".join(lines)


def _format_detail(result: dict) -> str:
    lines = ["<details><summary>逐日分类明细</summary>", "", "| 日期 | session | bars | gaps | first | last |", "|---|---|---|---|---|---|"]
    for d in result["per_day"]:
        lines.append(
            f"| {d['date']} | {d['session_type']} | {d['bars']} | {d['gap_count']} | {d['first_bar']} | {d['last_bar']} |"
        )
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def _load_combined_from_daily_dir(daily_dir: Path) -> pd.DataFrame:
    """把 state/task0_daily/ 里的 per-day CSV 合起来走 load_csv。"""
    csvs = sorted(daily_dir.glob("SPY_*.csv"))
    if not csvs:
        raise FileNotFoundError(f"{daily_dir} 下没有 SPY_*.csv")
    frames = [pd.read_csv(p) for p in csvs]
    combined = pd.concat(frames, ignore_index=True)
    # 写到临时路径让 load_csv 处理（避免重复实现 tz + RTH 过滤）
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tf:
        combined.to_csv(tf.name, index=False)
        tmp_path = tf.name
    try:
        return load_csv(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _pick_default_source() -> tuple[str, Path]:
    """优先级：continuous.csv → daily-dir → 老 bulk.csv"""
    cont = list(RAW_BULK_DIR.glob("SPY_1min_*.continuous.csv"))
    if cont:
        return ("continuous", cont[0])
    if DAILY_CSV_DIR.exists() and any(DAILY_CSV_DIR.glob("SPY_*.csv")):
        return ("daily-dir", DAILY_CSV_DIR)
    old = list(RAW_BULK_DIR.glob("SPY_1min_*.csv"))
    old = [p for p in old if ".continuous" not in p.name and "5min" not in p.name]
    if old:
        return ("old-bulk", old[0])
    raise FileNotFoundError("找不到可审计的数据源")


def _run_audit(source_kind: str, source_path: Path) -> tuple[str, dict]:
    label = f"{source_kind}: `{source_path.name}`"
    if source_kind == "daily-dir":
        df = _load_combined_from_daily_dir(source_path)
    else:
        df = load_csv(str(source_path))
    return label, _audit_dataframe(df)


def _check_seed_window(df: pd.DataFrame) -> str:
    """关键 sanity check：2026-01-07 11:05-12:11 应有 67 根 bar。"""
    target = pd.to_datetime("2026-01-07").date()
    day = df[df["date"] == target]
    if day.empty:
        return "2026-01-07 窗口检查：❌ 当日无数据"
    t = day["timestamp"].dt.strftime("%H:%M")
    window = day[(t >= "11:05") & (t <= "12:11")]
    n = len(window)
    status = "✅" if n == 67 else "❌"
    return f"2026-01-07 11:05-12:11 seed 窗口：**{n}** bars（期望 67）{status}"


def main():
    parser = argparse.ArgumentParser(description="Task 0 数据审计")
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--daily-dir", type=Path)
    parser.add_argument("--compare-old", action="store_true", help="同时审计老 bulk 对比")
    parser.add_argument("--out", type=Path, default=ACCEPTANCE_FILE)
    args = parser.parse_args()

    sources = []
    if args.csv:
        sources.append(("csv", args.csv))
    elif args.daily_dir:
        sources.append(("daily-dir", args.daily_dir))
    else:
        kind, path = _pick_default_source()
        sources.append((kind, path))

    if args.compare_old:
        old = [p for p in RAW_BULK_DIR.glob("SPY_1min_*.csv")
               if ".continuous" not in p.name and "5min" not in p.name]
        if old:
            sources.append(("old-bulk", old[0]))

    report_blocks = [f"## Task 0 Audit — {datetime.now().isoformat(timespec='seconds')}", ""]

    for kind, path in sources:
        print(f"\n=== 审计 {kind}: {path.name if path.is_file() else path} ===", flush=True)
        label, result = _run_audit(kind, path)

        summary = _format_summary(label, result)
        print(summary)

        # seed window check（只对联合数据源有意义，取 dataframe 再算一次）
        if kind == "daily-dir":
            df_all = _load_combined_from_daily_dir(path)
        else:
            df_all = load_csv(str(path))
        seed_msg = _check_seed_window(df_all)
        print(seed_msg, flush=True)

        report_blocks.append(summary)
        report_blocks.append(seed_msg + "\n")
        report_blocks.append(_format_detail(result))
        report_blocks.append("")

    # 追加到 acceptance.md
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("a", encoding="utf-8") as f:
        f.write("\n".join(report_blocks) + "\n\n---\n\n")
    print(f"\n报告追加到 {args.out}", flush=True)


if __name__ == "__main__":
    main()
