"""
build_json.py — 统一数据管道

功能:
  build    从 1min CSV 生成 processed/SPY_YYYY-MM-DD.json
  fix-ts   给现有 teaching_segments.json 补回 ts 字段

用法:
  python build_json.py raw/daily/SPY_1min_2026-04-13.csv
  python build_json.py raw/daily/SPY_1min_2026-04-14.csv
  python build_json.py raw/bulk/SPY_1min_2025-10-01_2026-04-11.csv --date 2026-01-07
  python build_json.py --fix-ts

输出格式:
  符合 JSON_SCHEMA.md v1.1
"""

import sys
import os
import json
import argparse
from datetime import datetime

import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════
#                              参数解析
# ═══════════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(
        description="CSV → JSON 数据管道 & teaching_segments ts 补丁",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例:
  python build_json.py raw/daily/SPY_1min_2026-04-14.csv --auto-warmup
  python build_json.py raw/daily/SPY_1min_2026-04-14.csv --warmup raw/bulk/SPY_1min_2025-10-01_2026-04-11.csv
  python build_json.py raw/bulk/SPY_1min_2025-10-01_2026-04-11.csv --date 2026-01-07
  python build_json.py --fix-ts""",
    )
    p.add_argument("csv_path", nargs="?", help="1min CSV 文件路径")
    p.add_argument("--date", help="从 bulk CSV 中提取指定日期 (YYYY-MM-DD)")
    p.add_argument(
        "--warmup", help="指定 warmup CSV（用于 SMA 热启动）",
    )
    p.add_argument(
        "--auto-warmup", action="store_true",
        help="自动从 raw/bulk/ 和 raw/daily/ 搜索历史数据做 warmup（推荐）",
    )
    p.add_argument(
        "--batch", action="store_true",
        help="批量模式：向量化处理 bulk CSV 中所有日期（v0.6）",
    )
    p.add_argument(
        "--force", action="store_true",
        help="批量模式下强制覆盖已存在的 JSON（默认跳过）",
    )
    p.add_argument(
        "--synthetic-list",
        help="批量模式下：列出需要落 processed/synthetic_fallback/ 的日期（每行一个 YYYY-MM-DD 或 JSON 数组）",
    )
    p.add_argument(
        "--fix-ts", action="store_true",
        help="给 teaching_segments.json 中的 bar 补回 ts 字段",
    )
    return p.parse_args()


# ═══════════════════════════════════════════════════════════════════════════
#                            指标计算函数
# ═══════════════════════════════════════════════════════════════════════════

def compute_ha(o, h, l, c, dates=None):
    """
    计算 Heikin-Ashi OHLC。每个交易日重置起点。

    首根 Bar（或新日期的第一根）:
      hO = (O + C) / 2
      hC = (O + H + L + C) / 4
    后续 Bar:
      hO = (prev_hO + prev_hC) / 2
      hC = (O + H + L + C) / 4
    hH = max(H, hO, hC)
    hL = min(L, hO, hC)
    """
    n = len(o)
    ha_c = (o + h + l + c) / 4

    ha_o = np.empty(n)
    ha_o[0] = (o[0] + c[0]) / 2
    for i in range(1, n):
        # 新交易日 → 重置 HA 起点
        if dates is not None and dates[i] != dates[i - 1]:
            ha_o[i] = (o[i] + c[i]) / 2
        else:
            ha_o[i] = (ha_o[i - 1] + ha_c[i - 1]) / 2

    ha_h = np.maximum(h, np.maximum(ha_o, ha_c))
    ha_l = np.minimum(l, np.minimum(ha_o, ha_c))

    return ha_o, ha_h, ha_l, ha_c


def compute_cumulative_vwap(df):
    """
    计算累积 VWAP（每个交易日从开盘重新累积）。

    若源数据有 per-bar vwap 列，使用 sum(vwap_i × vol_i) / sum(vol_i)。
    否则用 typical_price = (H + L + C) / 3 作为代理。
    """
    if "date" in df.columns:
        dates = df["date"].values
    else:
        dates = df["timestamp"].dt.date.values if "timestamp" in df.columns else np.zeros(len(df))
    vol = df["volume"].values

    typical = (df["high"].values + df["low"].values + df["close"].values) / 3
    if "vwap" in df.columns:
        # 使用 per-bar vwap（有值时），缺失时回退到 typical price
        bar_vwap = df["vwap"].values.copy()
        mask = pd.isna(bar_vwap)
        bar_vwap[mask] = typical[mask]
        pv_raw = bar_vwap * vol
    else:
        pv_raw = typical * vol

    # 按日期分组累积
    cum_pv = np.empty(len(df))
    cum_vol = np.empty(len(df))
    cum_pv[0] = pv_raw[0]
    cum_vol[0] = vol[0]
    for i in range(1, len(df)):
        if dates[i] != dates[i - 1]:
            cum_pv[i] = pv_raw[i]
            cum_vol[i] = vol[i]
        else:
            cum_pv[i] = cum_pv[i - 1] + pv_raw[i]
            cum_vol[i] = cum_vol[i - 1] + vol[i]

    return cum_pv / cum_vol


def compute_sma(values, window):
    """简单移动平均，前 window-1 个返回 NaN。"""
    return pd.Series(values).rolling(window=window, min_periods=window).mean().values


# ═══════════════════════════════════════════════════════════════════════════
#                              Bar 构建
# ═══════════════════════════════════════════════════════════════════════════

def _r4(x):
    """安全四舍五入到 4 位小数，NaN → None。"""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), 4)


def build_bars(df):
    """
    从 DataFrame 构建符合 JSON_SCHEMA.md 的 Bar 字典列表。

    要求 df 至少包含: timestamp, open, high, low, close, volume
    可选包含: vwap（若有则用于 VWAP 计算，否则用 typical price 代理）
    """
    o = df["open"].values.astype(float)
    h = df["high"].values.astype(float)
    l = df["low"].values.astype(float)
    c = df["close"].values.astype(float)

    dates = df["date"].values if "date" in df.columns else None
    ha_o, ha_h, ha_l, ha_c = compute_ha(o, h, l, c, dates)
    cum_vw = compute_cumulative_vwap(df)
    ma5   = compute_sma(c, 5)
    ma10  = compute_sma(c, 10)
    ma20  = compute_sma(c, 20)
    ma30  = compute_sma(c, 30)
    ma50  = compute_sma(c, 50)
    ma60  = compute_sma(c, 60)
    ma120 = compute_sma(c, 120)
    ma200 = compute_sma(c, 200)
    ma250 = compute_sma(c, 250)

    bars = []
    for i in range(len(df)):
        row = df.iloc[i]
        bars.append({
            "ts":   row["timestamp"].isoformat(),
            "t":    row["timestamp"].strftime("%H:%M"),
            "O":    _r4(o[i]),
            "H":    _r4(h[i]),
            "L":    _r4(l[i]),
            "C":    _r4(c[i]),
            "V":    int(row["volume"]),
            "vw":   _r4(cum_vw[i]),
            "hO":   _r4(ha_o[i]),
            "hH":   _r4(ha_h[i]),
            "hL":   _r4(ha_l[i]),
            "hC":   _r4(ha_c[i]),
            "m5":   _r4(ma5[i]),
            "m10":  _r4(ma10[i]),
            "m20":  _r4(ma20[i]),
            "m30":  _r4(ma30[i]),
            "m50":  _r4(ma50[i]),
            "m60":  _r4(ma60[i]),
            "m120": _r4(ma120[i]),
            "m200": _r4(ma200[i]),
            "m250": _r4(ma250[i]),
        })
    return bars


# ═══════════════════════════════════════════════════════════════════════════
#                          CSV 加载 & 5min 聚合
# ═══════════════════════════════════════════════════════════════════════════

def load_csv(path):
    """
    读取 1min CSV，兼容 daily（6 列）和 bulk（10 列）两种格式。
    返回含 timestamp, open, high, low, close, volume[, vwap] 列的 DataFrame。
    """
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]  # 兼容 yfinance 大写列名

    # 统一时间列，确保 tz-aware (ET)
    from zoneinfo import ZoneInfo
    et = ZoneInfo("America/New_York")

    if "datetime" in df.columns:
        ts = pd.to_datetime(df["datetime"])
    elif "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"])
    else:
        raise ValueError("CSV 缺少 datetime 或 timestamp 列")

    # 统一为 ET 时区：tz-aware 直接转换，tz-naive 当作 ET 本地时间
    if ts.dt.tz is None:
        df["timestamp"] = ts.dt.tz_localize(et)
    else:
        df["timestamp"] = ts.dt.tz_convert(et)

    # 统一列名（不区分大小写）
    rename = {}
    for c in df.columns:
        cl = c.strip().lower()
        if cl == "open":    rename[c] = "open"
        elif cl == "high":  rename[c] = "high"
        elif cl == "low":   rename[c] = "low"
        elif cl == "close": rename[c] = "close"
        elif cl == "volume": rename[c] = "volume"
        elif cl == "vwap":  rename[c] = "vwap"
    df = df.rename(columns=rename)

    df["date"] = df["timestamp"].dt.date

    # 过滤 RTH（09:30 ~ 16:00 ET）
    time_str = df["timestamp"].dt.strftime("%H:%M")
    df = df[(time_str >= "09:30") & (time_str < "16:00")].copy()
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def aggregate_to_5min(df_1m):
    """
    1min → 5min OHLCV 聚合。

    聚合规则:
      open   = 第 1 根 1min 的 open
      high   = 5 根 1min 的 max(high)
      low    = 5 根 1min 的 min(low)
      close  = 最后 1 根 1min 的 close
      volume = 5 根 1min 的 sum(volume)
      vwap   = 5 根 1min 的 成交量加权均价
    """
    df = df_1m.set_index("timestamp")

    ohlcv = df[["open", "high", "low", "close", "volume"]].resample("5min").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    ).dropna()

    # 计算每根 5min bar 的加权均价（供后续累积 VWAP 使用）
    if "vwap" in df.columns:
        pv = (df["vwap"] * df["volume"]).resample("5min").sum()
    else:
        typical = (df["high"] + df["low"] + df["close"]) / 3
        pv = (typical * df["volume"]).resample("5min").sum()
    vol = df["volume"].resample("5min").sum()
    ohlcv["vwap"] = (pv / vol).reindex(ohlcv.index)

    result = ohlcv.reset_index()
    result["date"] = result["timestamp"].dt.date
    return result


# ═══════════════════════════════════════════════════════════════════════════
#                         Auto-warmup 发现
# ═══════════════════════════════════════════════════════════════════════════

def discover_warmup_sources(data_dir, target_dates):
    """
    自动从 raw/bulk/ 和 raw/daily/ 搜索可用的 warmup CSV。

    策略：
    1. 优先加载 bulk CSV（覆盖范围最大）
    2. 补充 daily CSV 中早于目标日期的文件
    3. 返回合并后的 DataFrame
    """
    import glob
    import re

    earliest_target = min(target_dates)
    raw_dir = os.path.join(data_dir, "raw")
    frames = []

    # 1. 搜索 bulk CSV
    bulk_dir = os.path.join(raw_dir, "bulk")
    if os.path.isdir(bulk_dir):
        for f in sorted(glob.glob(os.path.join(bulk_dir, "SPY_1min_*.csv"))):
            print(f"  [auto-warmup] 加载 bulk: {os.path.basename(f)}")
            frames.append(load_csv(f))

    # 2. 搜索 daily CSV（只加载早于最早目标日期的）
    daily_dir = os.path.join(raw_dir, "daily")
    if os.path.isdir(daily_dir):
        date_pattern = re.compile(r"SPY_1min_(\d{4}-\d{2}-\d{2})\.csv")
        for f in sorted(glob.glob(os.path.join(daily_dir, "SPY_1min_*.csv"))):
            m = date_pattern.search(os.path.basename(f))
            if m:
                file_date = pd.Timestamp(m.group(1)).date()
                if file_date < earliest_target:
                    print(f"  [auto-warmup] 加载 daily: {os.path.basename(f)}")
                    frames.append(load_csv(f))

    if not frames:
        return None

    combined = pd.concat(frames, ignore_index=True)
    # 去重（bulk 和 daily 可能有重叠日期）
    combined = combined.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    n_days = combined["date"].nunique()
    print(f"  [auto-warmup] 合计: {len(combined)} bars, {n_days} 个交易日")
    return combined


# ═══════════════════════════════════════════════════════════════════════════
#                     v0.6 新增：分类 / warmup_complete / 向量化辅助
# ═══════════════════════════════════════════════════════════════════════════

def classify_session(bars_1m):
    """
    按 plan 0.2 口径分类单日 session。
    返回 (session_type, gap_count)。

    gap_count = 相邻两根 1m bar 间隔 > 1 分钟的次数（RTH 内部缺口）。
    """
    n = len(bars_1m)
    if n == 0:
        return "invalid_session", 0

    gap_count = 0
    prev = pd.Timestamp(bars_1m[0]["ts"])
    for b in bars_1m[1:]:
        cur = pd.Timestamp(b["ts"])
        if (cur - prev) > pd.Timedelta(minutes=1):
            gap_count += 1
        prev = cur

    if n < 200:
        return "invalid_session", gap_count
    if n < 380:
        return "short_session", gap_count
    if gap_count == 0:
        return "full_session_clean", 0
    return "full_session_gappy", gap_count


def compute_warmup_complete(bars_1m, bars_5m):
    """
    warmup_complete.{1m,5m} 判定：该 timeframe 的全部 bar 的 m250 均非 null。
    """
    def _all_m250(bars):
        return bool(bars) and all(b.get("m250") is not None for b in bars)
    return {"1m": _all_m250(bars_1m), "5m": _all_m250(bars_5m)}


def build_all_day_bars(df_all):
    """
    向量化路径：对全量 df 调 build_bars 一次，再按日期分桶。
    O(N) 替代 cmd_build 老逻辑的 O(N²) per-day 重建。

    返回 (bars_1m_by_date, bars_5m_by_date) — dict: {"YYYY-MM-DD": [bars...]}
    """
    from collections import defaultdict

    df_all = df_all.sort_values("timestamp").reset_index(drop=True)
    all_bars_1m = build_bars(df_all)

    df_5m = aggregate_to_5min(df_all)
    all_bars_5m = build_bars(df_5m)

    bars_1m_by_date = defaultdict(list)
    for b in all_bars_1m:
        bars_1m_by_date[b["ts"][:10]].append(b)
    bars_5m_by_date = defaultdict(list)
    for b in all_bars_5m:
        bars_5m_by_date[b["ts"][:10]].append(b)

    return bars_1m_by_date, bars_5m_by_date


def _load_synthetic_list(path):
    """解析 --synthetic-list：支持每行一个日期 或 JSON 数组。"""
    if not path or not os.path.exists(path):
        return set()
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()
    if not raw:
        return set()
    if raw.startswith("["):
        try:
            return set(json.loads(raw))
        except json.JSONDecodeError:
            pass
    return {line.strip() for line in raw.splitlines() if line.strip() and not line.startswith("#")}


def _build_meta(date_str, bars_1m, bars_5m, source, title=None):
    """统一 meta 构造（v0.6 新增 session_type / gap_count / warmup_complete）。"""
    session_type, gap_count = classify_session(bars_1m)
    return {
        "title": title or f"SPY {date_str} Full Day",
        "ticker": "SPY",
        "date": date_str,
        "source": source,
        "session_type": session_type,
        "gap_count": gap_count,
        "warmup_complete": compute_warmup_complete(bars_1m, bars_5m),
        "counts": {
            "bars_1m": len(bars_1m),
            "bars_5m": len(bars_5m),
        },
        "generated_at": datetime.now().isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════
#                           命令: build
# ═══════════════════════════════════════════════════════════════════════════

def cmd_build(csv_path, target_date=None, warmup_csv=None, auto_warmup=False):
    """从 1min CSV 构建 full-day JSON 文件。"""
    if not os.path.exists(csv_path):
        print(f"错误: 文件不存在 → {csv_path}")
        sys.exit(1)

    df = load_csv(csv_path)

    # 加载 warmup 数据（用于 SMA 热启动）
    df_warmup = None
    if auto_warmup:
        # 确定目标日期列表，用于发现 warmup 源
        if target_date:
            search_dates = {pd.Timestamp(target_date).date()}
        else:
            search_dates = set(df["date"].unique())
        data_dir = os.path.dirname(os.path.abspath(csv_path))
        # data_dir 可能是 raw/daily/ 或 raw/bulk/，需要回到 data/ 根目录
        # 通过查找 raw/ 子目录来定位
        candidate = data_dir
        for _ in range(3):
            if os.path.isdir(os.path.join(candidate, "raw")):
                break
            candidate = os.path.dirname(candidate)
        else:
            candidate = os.path.dirname(os.path.abspath(__file__))
        df_warmup = discover_warmup_sources(candidate, search_dates)
    elif warmup_csv:
        if not os.path.exists(warmup_csv):
            print(f"  警告: warmup 文件不存在 → {warmup_csv}，将跳过 warmup")
        else:
            df_warmup = load_csv(warmup_csv)
            print(f"  Warmup 数据: {warmup_csv} ({len(df_warmup)} bars)")

    # 合并 warmup + 主数据（用于跨日 SMA 计算）
    if df_warmup is not None:
        df_all = pd.concat([df_warmup, df], ignore_index=True)
    else:
        df_all = df

    # 确定要处理的日期（只处理主 CSV 中的日期）
    if target_date:
        td = pd.Timestamp(target_date).date()
        target_dates_set = {td}
        if df[df["date"] == td].empty:
            print(f"错误: CSV 中无 {target_date} 的数据")
            sys.exit(1)
        dates = [td]
    else:
        dates = sorted(df["date"].unique())

    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "processed")
    os.makedirs(out_dir, exist_ok=True)

    # 全部日期（含 warmup），用于查找前一交易日
    all_dates = sorted(df_all["date"].unique())

    total = 0
    for date in dates:
        date_str = str(date)
        day = df_all[df_all["date"] == date].sort_values("timestamp").reset_index(drop=True)

        if len(day) < 10:
            print(f"[SKIP] {date_str}: 仅 {len(day)} 根 1m，数据不足")
            continue

        # ── Warmup: 拼接目标日期之前的全部历史，让 SMA 充分热启动 ──
        # 取所有早于 target date 的 bar（HA/VWAP 按日重置，SMA 跨日滚动）
        history = df_all[df_all["date"] < date].sort_values("timestamp").reset_index(drop=True)
        if len(history) > 0:
            warmup_1m = pd.concat([history, day], ignore_index=True)
            warmup_offset_1m = len(history)
            n_days = history["date"].nunique()
            print(f"  [{date_str}] Warmup: {len(history)} bars from {n_days} trading days")
        else:
            warmup_1m = day
            warmup_offset_1m = 0
            print(f"  [{date_str}] No warmup data (first date in dataset)")

        # 构建 1m bars（含 warmup），然后裁掉 warmup 部分
        all_bars_1m = build_bars(warmup_1m)
        bars_1m = all_bars_1m[warmup_offset_1m:]

        # 聚合 5m 并构建 bars（同样带 warmup）
        df_5m = aggregate_to_5min(warmup_1m)
        all_bars_5m = build_bars(df_5m)
        # 裁掉 warmup 部分：只保留当天时间戳的 5m bar
        bars_5m = [b for b in all_bars_5m if b["ts"].startswith(date_str)]

        result = {
            "meta": _build_meta(date_str, bars_1m, bars_5m, os.path.basename(csv_path)),
            "bars_1m": bars_1m,
            "bars_5m": bars_5m,
        }

        out_path = os.path.join(out_dir, f"SPY_{date_str}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"[OK] {date_str}: 1m={len(bars_1m)} | 5m={len(bars_5m)} → {out_path}")
        total += 1

    print(f"\n完成: 共生成 {total} 个 JSON 文件")


# ═══════════════════════════════════════════════════════════════════════════
#                           命令: batch (v0.6 新增)
# ═══════════════════════════════════════════════════════════════════════════

def cmd_batch(csv_path, force=False, synthetic_list=None):
    """
    批量路径：向量化处理 bulk CSV，每日输出一个 JSON。
    - 默认已存在 JSON 的日期跳过（除非 --force）
    - meta 加 session_type / gap_count / warmup_complete.{1m,5m}
    - synthetic 日期（由 --synthetic-list 指定）路由到 processed/synthetic_fallback/
    - 进度行：[idx/total] date → session | gap | warmup(1m,5m) | bars
    """
    import time
    t0 = time.time()

    if not os.path.exists(csv_path):
        print(f"错误: 文件不存在 → {csv_path}")
        sys.exit(1)

    synthetic_set = _load_synthetic_list(synthetic_list)
    if synthetic_list:
        print(f"  [synthetic-list] 读入 {len(synthetic_set)} 个日期 → processed/synthetic_fallback/")

    print(f"Loading {csv_path} ...")
    df = load_csv(csv_path)
    n_bars = len(df)
    n_days = df["date"].nunique()
    print(f"  Loaded {n_bars} bars across {n_days} 交易日，开始向量化...")

    bars_1m_by_date, bars_5m_by_date = build_all_day_bars(df)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "processed")
    fallback_dir = os.path.join(out_dir, "synthetic_fallback")
    os.makedirs(out_dir, exist_ok=True)
    if synthetic_set:
        os.makedirs(fallback_dir, exist_ok=True)

    all_dates = sorted(bars_1m_by_date.keys())
    total = len(all_dates)
    written = skipped = invalid = 0
    per_day_status = []  # [(date, session_type, gap, ...), ...]

    for i, date_str in enumerate(all_dates, 1):
        bars_1m = bars_1m_by_date[date_str]
        bars_5m = bars_5m_by_date.get(date_str, [])

        is_synthetic = date_str in synthetic_set
        target_dir = fallback_dir if is_synthetic else out_dir
        out_path = os.path.join(target_dir, f"SPY_{date_str}.json")

        # 先分类（即便要跳过也登记 session_type）
        session_type, gap_count = classify_session(bars_1m)
        warmup = compute_warmup_complete(bars_1m, bars_5m)
        per_day_status.append({
            "date": date_str,
            "session_type": session_type,
            "gap_count": gap_count,
            "bars_1m": len(bars_1m),
            "bars_5m": len(bars_5m),
            "warmup_1m": warmup["1m"],
            "warmup_5m": warmup["5m"],
            "synthetic": is_synthetic,
        })

        if session_type == "invalid_session":
            print(f"[SKIP] {date_str}: invalid_session ({len(bars_1m)} bars)")
            invalid += 1
            continue

        if os.path.exists(out_path) and not force:
            print(f"[SKIP existing] [{i}/{total}] {date_str}")
            skipped += 1
            continue

        source_label = os.path.basename(csv_path)
        if is_synthetic:
            source_label = f"{source_label} (gap-filled synthetic)"
        result = {
            "meta": _build_meta(date_str, bars_1m, bars_5m, source_label),
            "bars_1m": bars_1m,
            "bars_5m": bars_5m,
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        tag = "⚠" if session_type == "short_session" else (
            "◈" if is_synthetic else "✓"
        )
        print(
            f"[{i}/{total}] {date_str} {tag} {session_type} gap={gap_count} "
            f"warmup(1m={'T' if warmup['1m'] else 'F'},5m={'T' if warmup['5m'] else 'F'}) "
            f"| 1m={len(bars_1m)} 5m={len(bars_5m)} → {os.path.basename(out_path)}"
        )
        written += 1

    elapsed = time.time() - t0
    print(f"\n批量完成：written={written} skipped={skipped} invalid={invalid} 总耗时 {elapsed:.1f}s")

    # 分类汇总
    buckets = {k: [] for k in
               ("full_session_clean", "full_session_gappy", "short_session", "invalid_session")}
    for d in per_day_status:
        buckets[d["session_type"]].append(d["date"])
    print("\n分类汇总：")
    for k, v in buckets.items():
        print(f"  {k}: {len(v)}")

    # 简单返回（便于被其它脚本调用时拿结果）
    return {
        "written": written,
        "skipped_existing": skipped,
        "invalid": invalid,
        "total_dates": total,
        "elapsed_sec": elapsed,
        "per_day": per_day_status,
        "buckets": buckets,
    }


# ═══════════════════════════════════════════════════════════════════════════
#                           命令: fix-ts
# ═══════════════════════════════════════════════════════════════════════════

def cmd_fix_ts():
    """给 teaching_segments.json 中所有 bar 补回 ts 字段。"""
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        from backports.zoneinfo import ZoneInfo  # Python < 3.9

    tz = ZoneInfo("America/New_York")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "processed", "teaching_segments.json")

    if not os.path.exists(json_path):
        print(f"错误: 找不到 → {json_path}")
        sys.exit(1)

    print(f"正在读取 {json_path} ...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    added = 0
    segments = data.get("segments", [])
    for seg in segments:
        date_str = seg.get("date")
        if not date_str:
            continue

        for key in ("bars_1m", "bars_5m"):
            for bar in seg.get(key, []):
                if "ts" not in bar:
                    # 根据日期自动判断 EST/EDT 时区偏移
                    dt = datetime.strptime(f"{date_str} {bar['t']}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=tz)
                    bar["ts"] = dt.isoformat()
                    added += 1

    # 写回（保持紧凑单行格式，与原文件一致）
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    print(f"[OK] 已为 {added} 个 bar 补回 ts 字段")
    print(f"     涉及 {len(segments)} 个 segment → {json_path}")


# ═══════════════════════════════════════════════════════════════════════════
#                               入口
# ═══════════════════════════════════════════════════════════════════════════

def main():
    args = parse_args()

    if args.fix_ts:
        cmd_fix_ts()
        return

    if not args.csv_path:
        print("错误: 请指定 CSV 路径或使用 --fix-ts")
        print()
        print("用法:")
        print("  python build_json.py <csv> --auto-warmup            # daily CSV：自动拼接历史 warmup")
        print("  python build_json.py <csv> --warmup <csv>           # daily CSV：指定 warmup CSV")
        print("  python build_json.py <csv> --date DATE              # bulk CSV：提取指定日期")
        print("  python build_json.py <csv> --batch [--force]        # bulk CSV：批量生成所有日期 (v0.6)")
        print("  python build_json.py <csv> --batch --synthetic-list PATH  # 路由 synthetic 日到 fallback/")
        print("  python build_json.py --fix-ts                       # 补回 teaching_segments 的 ts")
        sys.exit(1)

    if args.batch and args.date:
        print("错误: --batch 与 --date 互斥")
        sys.exit(2)

    if args.batch:
        cmd_batch(args.csv_path, force=args.force, synthetic_list=args.synthetic_list)
        return

    # 未指定 --batch / --date：不能对含多日期的 CSV 静默全量
    if args.date is None:
        df_peek = load_csv(args.csv_path)
        n_dates = df_peek["date"].nunique()
        if n_dates > 1:
            print(f"错误: CSV 含 {n_dates} 个交易日 — Bulk CSV requires --batch or --date")
            print("       --batch 批量生成所有日期 (v0.6)")
            print("       --date YYYY-MM-DD 提取指定日期")
            sys.exit(2)

    cmd_build(args.csv_path, args.date, args.warmup, args.auto_warmup)


if __name__ == "__main__":
    main()
