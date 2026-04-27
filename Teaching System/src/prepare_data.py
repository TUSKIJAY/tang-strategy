#!/usr/bin/env python3
"""
prepare_data.py — Build teaching segments for the Tang strategy replay tool.

Usage:
    python prepare_data.py
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = DATA_DIR / "processed"

FILE_1M = DATA_DIR / "SPY_1min_2025-10-01_2026-04-11.json"
FILE_5M = DATA_DIR / "SPY_5min_2025-10-01_2026-04-11.json"
SEED_FILE = PROJECT_DIR.parent / "_archive" / "all_chart_data_enriched.json"

RTH_START = "09:30"
RTH_END = "16:00"
ET = ZoneInfo("America/New_York")
WARMUP_SKIP_DATES = {"2025-10-01", "2025-10-02", "2025-10-03"}
PREHEAT_BARS = 30

SEED_CATEGORIES = {
    "01": {"cat": "support_ma10", "chapter": "03", "scenario": "bullish"},
    "02": {"cat": "reject_ma10", "chapter": "03", "scenario": "bearish"},
    "03": {"cat": "reject_ma10", "chapter": "03", "scenario": "bearish"},
    "04": {"cat": "reject_ma10", "chapter": "03", "scenario": "bearish"},
    "05": {"cat": "kline_quality", "chapter": "06", "scenario": "bearish"},
    "06": {"cat": "signal_b", "chapter": "04", "scenario": "bearish"},
    "07": {"cat": "reject_ma10", "chapter": "03", "scenario": "bearish"},
    "08": {"cat": "signal_b", "chapter": "04", "scenario": "bearish"},
    "09": {"cat": "barrier_test", "chapter": "07", "scenario": "bearish"},
    "10": {"cat": "ma_tangle", "chapter": "05", "scenario": "bearish"},
    "11": {"cat": "opening_gap", "chapter": "13", "scenario": "bearish"},
    "14": {"cat": "kline_quality", "chapter": "06", "scenario": "bearish"},
    "15": {"cat": "violent_reversal", "chapter": "08", "scenario": "bullish"},
    "16": {"cat": "bear_attack", "chapter": "09", "scenario": "bearish"},
}

CATEGORY_DEFS = [
    {"id": "reject_ma10", "name": "Reject MA10", "desc": "价格反弹触及MA10后被压回"},
    {"id": "support_ma10", "name": "Support MA10", "desc": "价格回调触及MA10后反弹"},
    {"id": "signal_b", "name": "信号B", "desc": "价格同时跌破MA10和MA50"},
    {
        "id": "trend_accumulation",
        "name": "多空转换",
        "desc": "单边趋势里的首次反转通常不会一次成功，需要多次尝试累积力量",
    },
    {"id": "ma_tangle", "name": "均线缠绕", "desc": "均线密集交叉，最危险时刻"},
    {"id": "kline_quality", "name": "K线质量", "desc": "通过K线形态判断趋势强弱"},
    {"id": "barrier_test", "name": "关卡测试", "desc": "测试MA50/MA200/VWAP关卡"},
    {"id": "violent_reversal", "name": "暴力反转", "desc": "极端行情的深V反转"},
    {"id": "opening_gap", "name": "开盘跳空", "desc": "开盘跳空引发的暴跌"},
    {"id": "bear_attack", "name": "空头总攻", "desc": "均线扇形发散的黄金做空时刻"},
]

CATEGORY_DESC_MAP = {c["id"]: c["desc"] for c in CATEGORY_DEFS}

SEED_OVERRIDES = {
    "01": {
        "variant_label": "单边顺延型",
        "teaching_focus": "标准 Support MA10，重点看多头单边和确认K。",
    },
    "02": {
        "variant_label": "标准瀑布型",
        "teaching_focus": "标准空头顺延里的 Reject MA10。",
    },
    "03": {
        "date": "2026-03-09",
        "interval": "1m",
        "time_start": "11:10",
        "time_end": "11:44",
        "visible_candles": 35,
        "title": "标准空头反抽后 Reject MA10",
        "variant_label": "标准反抽型",
        "teaching_focus": "5m 空头发散排列下，绿色反抽触 MA10 后继续下压。",
    },
    "04": {
        "date": "2026-02-03",
        "interval": "1m",
        "time_start": "09:55",
        "time_end": "10:20",
        "visible_candles": 26,
        "title": "绿色反抽触线后再压回",
        "variant_label": "绿色反抽型",
        "teaching_focus": "信号K 必须先是绿色反抽，再被 MA10 压回。",
    },
    "06": {
        "variant_label": "直达 MA200 型",
        "teaching_focus": "跌破双线后直奔 MA200，重点看 5m 拐头确认。",
    },
    "07": {
        "variant_label": "顺延加速型",
        "teaching_focus": "信号出现后几乎没有多余震荡，属于顺延加速版本。",
    },
    "08": {
        "variant_label": "VWAP 拦截型",
        "teaching_focus": "双线跌破后，反抽到 VWAP 一带再次被压回。",
    },
}

CUSTOM_SEGMENTS = [
    {
        "id": "case_16_attempts_01",
        "title": "单边多头里的首次反转通常失败",
        "category": "trend_accumulation",
        "chapter": "16",
        "scenario": "bearish",
        "date": "2026-04-09",
        "interval": "1m",
        "time_start": "13:45",
        "time_end": "15:05",
        "visible_candles": 81,
        "is_seed": False,
        "variant_label": "多次尝试型",
        "teaching_focus": "15m 长期多头排列下，14:03、14:15、14:30 三次下压都没有走出顺畅反转。",
        "background_note": "当前处于 15m 级别长期多头排列中，首次跌破通常不顺。",
    }
]

CUSTOM_SIGNAL_TIMES = {
    "case_16_attempts_01": "14:03",
}

CUSTOM_ANNOTATIONS_1M = {
    "seed_08": [
        {
            "time": "10:39",
            "title": "VWAP 拦截！",
            "body": "价格回到 VWAP 一带后没有站稳，VWAP 重新变成继续下压的关卡。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "amber",
        }
    ],
    "case_16_attempts_01": [
        {
            "time": "13:52",
            "title": "单边多头背景",
            "body": "15m 仍是多头排列。这里先记住大背景，别把第一脚回落直接当成已经翻空。",
            "anchor_side": "bottom",
            "auto_pause": True,
            "style": "blue",
        },
        {
            "time": "14:03",
            "title": "第一次尝试",
            "body": "第一次快速跌破看起来很凶，但后续扩展并不顺，多头力量还没有真正退场。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "amber",
        },
        {
            "time": "14:15",
            "title": "第二次尝试",
            "body": "第二脚再压低，依旧只是磨蹭推进。空头在累积力量，但还没拿到顺畅趋势。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "amber",
        },
        {
            "time": "14:30",
            "title": "第三次尝试",
            "body": "第三次下压仍然没有一波流。Tang 的意思就是：第一次就进去了，也会跌得非常不顺。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "red",
        },
        {
            "time": "15:05",
            "title": "等待更高周期也转弱",
            "body": "真正能提高胜率的，是等更高时间框架也开始转弱，而不是抢第一次反转。",
            "anchor_side": "bottom",
            "auto_pause": False,
            "style": "blue",
        },
    ]
}

CUSTOM_ANNOTATIONS_5M = {
    "seed_06": [
        {
            "time": "11:10",
            "title": "5m 拐头确认",
            "body": "5m 收盘跌回 MA10 下方，MA10 开始下弯。这里要的不是完整空头排列，而是有效拐头。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "blue",
        }
    ],
    "seed_08": [
        {
            "time": "10:45",
            "title": "5m 跟随确认",
            "body": "5m 阴线收在 MA10 下方，1m 的双线跌破不是孤立动作，VWAP 也在上方形成压制。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "blue",
        }
    ],
    "case_16_attempts_01": [
        {
            "time": "15:05",
            "title": "5m 只能辅助",
            "body": "这个概念更依赖 15m / 日线级背景。当前 15m 仍是多头排列，所以 1m 的首次反转并不顺。",
            "anchor_side": "top",
            "auto_pause": True,
            "style": "blue",
        }
    ],
}

MULTI_ATTEMPT_TIMES = {
    "case_16_attempts_01": ["14:03", "14:15", "14:30"],
}


def load_and_filter(filepath: Path) -> pd.DataFrame:
    print(f"  Loading {filepath.name} ...")
    raw = json.loads(filepath.read_text(encoding="utf-8"))
    df = pd.DataFrame(raw)

    ts_et = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(ET)
    df["date"] = ts_et.dt.strftime("%Y-%m-%d")
    df["time"] = ts_et.dt.strftime("%H:%M")
    df["ts_et"] = ts_et.dt.strftime("%Y-%m-%d %H:%M:%S")

    df = df[(df["time"] >= RTH_START) & (df["time"] < RTH_END)].copy()
    df = df[~df["date"].isin(WARMUP_SKIP_DATES)].copy()
    df.sort_values(["date", "time"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def compute_intraday_vwap(df: pd.DataFrame) -> pd.DataFrame:
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    cumulative_pv = (typical_price * df["volume"]).groupby(df["date"]).cumsum()
    cumulative_v = df["volume"].groupby(df["date"]).cumsum()
    df["vwap"] = np.round(cumulative_pv / cumulative_v, 4)
    return df


def compute_ha(df: pd.DataFrame) -> pd.DataFrame:
    ha_o = np.empty(len(df))
    ha_c = np.empty(len(df))
    ha_h = np.empty(len(df))
    ha_l = np.empty(len(df))

    dates = df["date"].values
    opens = df["open"].values
    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values

    for i in range(len(df)):
        ha_c[i] = (opens[i] + highs[i] + lows[i] + closes[i]) / 4.0
        if i == 0 or dates[i] != dates[i - 1]:
            ha_o[i] = (opens[i] + closes[i]) / 2.0
        else:
            ha_o[i] = (ha_o[i - 1] + ha_c[i - 1]) / 2.0
        ha_h[i] = max(highs[i], ha_o[i], ha_c[i])
        ha_l[i] = min(lows[i], ha_o[i], ha_c[i])

    df["ha_o"] = np.round(ha_o, 4)
    df["ha_h"] = np.round(ha_h, 4)
    df["ha_l"] = np.round(ha_l, 4)
    df["ha_c"] = np.round(ha_c, 4)
    return df


def compute_sma(df: pd.DataFrame) -> pd.DataFrame:
    for window in (10, 50, 200):
        df[f"sma{window}"] = df["close"].rolling(window, min_periods=window).mean()
    return df


def aggregate_to_15m(df_1m: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for date, day_df in df_1m.groupby("date", sort=False):
        day = day_df.copy()
        day["bucket"] = (
            pd.to_datetime(day["time"], format="%H:%M")
            .dt.floor("15min")
            .dt.strftime("%H:%M")
        )
        grouped = day.groupby("bucket", sort=True)
        agg = pd.DataFrame(
            {
                "date": date,
                "time": grouped["time"].first(),
                "open": grouped["open"].first(),
                "high": grouped["high"].max(),
                "low": grouped["low"].min(),
                "close": grouped["close"].last(),
                "volume": grouped["volume"].sum(),
            }
        ).reset_index(drop=True)
        rows.append(agg)

    df_15m = pd.concat(rows, ignore_index=True)
    df_15m = compute_intraday_vwap(df_15m)
    df_15m = compute_ha(df_15m)
    df_15m = compute_sma(df_15m)
    return df_15m


def compute_viewport(bars_records: list[dict]) -> dict:
    if not bars_records:
        return {"price_min": 0, "price_max": 0, "volume_max": 0}

    price_min = float("inf")
    price_max = float("-inf")
    volume_max = 0

    for bar in bars_records:
        price_values = [bar["hH"], bar["hL"]]
        for key in ("m10", "m50", "m200"):
            if key in bar:
                price_values.append(bar[key])
        price_min = min(price_min, *price_values)
        price_max = max(price_max, *price_values)
        volume_max = max(volume_max, bar["V"])

    padding = (price_max - price_min) * 0.04 or 1
    return {
        "price_min": round(price_min - padding, 2),
        "price_max": round(price_max + padding, 2),
        "volume_max": volume_max,
    }


def to_builtin(value):
    if isinstance(value, dict):
        return {key: to_builtin(val) for key, val in value.items()}
    if isinstance(value, list):
        return [to_builtin(item) for item in value]
    if isinstance(value, tuple):
        return [to_builtin(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def slice_1m_segment(df_1m: pd.DataFrame, date: str, time_start: str, time_end: str) -> pd.DataFrame:
    day_df = df_1m[df_1m["date"] == date]
    if day_df.empty:
        return pd.DataFrame()

    core_mask = (day_df["time"] >= time_start) & (day_df["time"] <= time_end)
    core_df = day_df[core_mask]
    if core_df.empty:
        return pd.DataFrame()

    core_start_iloc = day_df.index.get_loc(core_df.index[0])
    preheat_start_iloc = max(0, core_start_iloc - PREHEAT_BARS)
    return day_df.iloc[preheat_start_iloc: core_start_iloc + len(core_df)].copy()


def slice_context_segment(
    df: pd.DataFrame,
    date: str,
    time_end: str,
    visible_candles: int | None = None,
    exact_window: bool = False,
) -> pd.DataFrame:
    day_df = df[df["date"] == date]
    if day_df.empty:
        return pd.DataFrame()

    end_bars = day_df[day_df["time"] <= time_end]
    if end_bars.empty:
        return pd.DataFrame()

    end_label = end_bars.index[-1]
    end_iloc = day_df.index.get_loc(end_label)

    if exact_window and visible_candles:
        start_iloc = max(0, end_iloc - visible_candles + 1)
        return day_df.iloc[start_iloc:end_iloc + 1].copy()

    return day_df.iloc[:end_iloc + 1].copy()


def compute_regime(df_seg: pd.DataFrame, time_end: str) -> dict:
    if df_seg.empty:
        return {
            "trend": "neutral",
            "ma_alignment": "tangled",
            "ma_spread": 0.0,
            "nearest_barrier": "N/A",
            "barrier_distance_pct": 0.0,
            "vwap_side": "above",
            "candle_quality": "mixed",
        }

    target_bars = df_seg[df_seg["time"] <= time_end]
    bar = target_bars.iloc[-1] if not target_bars.empty else df_seg.iloc[-1]

    close = bar["close"]
    sma10 = bar.get("sma10", np.nan)
    sma50 = bar.get("sma50", np.nan)
    sma200 = bar.get("sma200", np.nan)
    vwap = bar.get("vwap", np.nan)

    if pd.notna(sma10) and pd.notna(sma50):
        if close > sma10 > sma50:
            trend = "bullish"
        elif close < sma10 < sma50:
            trend = "bearish"
        else:
            trend = "neutral"
    else:
        trend = "neutral"

    if pd.notna(sma10) and pd.notna(sma50) and pd.notna(sma200):
        if sma10 > sma50 > sma200:
            ma_alignment = "bull_排列"
        elif sma10 < sma50 < sma200:
            ma_alignment = "bear_排列"
        else:
            ma_alignment = "tangled"
    else:
        ma_alignment = "tangled"

    if pd.notna(sma10) and pd.notna(sma50) and close != 0:
        ma_spread = round(abs(sma10 - sma50) / close * 100, 4)
    else:
        ma_spread = 0.0

    barriers = {}
    if pd.notna(sma50):
        barriers["MA50"] = sma50
    if pd.notna(sma200):
        barriers["MA200"] = sma200
    if pd.notna(vwap):
        barriers["VWAP"] = vwap

    nearest_barrier = "N/A"
    barrier_distance_pct = 0.0
    if barriers and close:
        if trend == "bearish":
            directional = {k: v for k, v in barriers.items() if v < close}
            pool = directional or barriers
            nearest_barrier = min(pool, key=lambda key: abs(close - pool[key]))
            barrier_distance_pct = round(abs(close - pool[nearest_barrier]) / close * 100, 2)
        else:
            directional = {k: v for k, v in barriers.items() if v > close}
            pool = directional or barriers
            nearest_barrier = min(pool, key=lambda key: abs(pool[key] - close))
            barrier_distance_pct = round(abs(pool[nearest_barrier] - close) / close * 100, 2)

    vwap_side = "above" if pd.notna(vwap) and close > vwap else "below"

    last5 = df_seg.tail(5)
    strong_count = 0
    weak_count = 0
    for _, row in last5.iterrows():
        candle_range = row["high"] - row["low"]
        body = abs(row["close"] - row["open"])
        if candle_range <= 0:
            continue
        if body > 0.5 * candle_range:
            strong_count += 1
        if body < 0.3 * candle_range:
            weak_count += 1

    if strong_count >= 4:
        candle_quality = "strong"
    elif weak_count >= 3:
        candle_quality = "weak"
    else:
        candle_quality = "mixed"

    return {
        "trend": trend,
        "ma_alignment": ma_alignment,
        "ma_spread": ma_spread,
        "nearest_barrier": nearest_barrier,
        "barrier_distance_pct": barrier_distance_pct,
        "vwap_side": vwap_side,
        "candle_quality": candle_quality,
    }


def get_bar_index_by_time(seg_df: pd.DataFrame, time_value: str) -> int | None:
    matches = seg_df.index[seg_df["time"] == time_value].tolist()
    return matches[0] if matches else None


def measure_followthrough(seg_df: pd.DataFrame, idx: int, bars_forward: int, scenario: str) -> dict:
    current = seg_df.iloc[idx]
    future = seg_df.iloc[idx + 1: idx + 1 + bars_forward]
    if future.empty:
        return {"bars": 0, "max_extension_pct": 0.0}

    entry = current["close"]
    if scenario == "bearish":
        best = future["low"].min()
        extension = max(0.0, (entry - best) / entry * 100)
    else:
        best = future["high"].max()
        extension = max(0.0, (best - entry) / entry * 100)

    return {"bars": len(future), "max_extension_pct": round(extension, 2)}


def compute_signal_b_confirmation(seg_df_5m: pd.DataFrame, time_end: str) -> dict:
    target_bars = seg_df_5m[seg_df_5m["time"] <= time_end]
    if target_bars.empty:
        return {"passed": False, "bar_index": None, "reason": "没有找到对应 5m bar"}

    bar_index = len(target_bars) - 1
    row = target_bars.iloc[-1]
    prev = target_bars.iloc[-2] if len(target_bars) >= 2 else None

    close_below_ma10 = pd.notna(row.get("sma10", np.nan)) and row["close"] < row["sma10"]
    bearish_body = row["close"] < row["open"]
    ma10_slope_down = bool(prev is not None and pd.notna(prev.get("sma10", np.nan)) and row["sma10"] <= prev["sma10"])
    close_below_prev_low = bool(prev is not None and row["close"] < prev["low"])
    close_below_vwap = pd.notna(row.get("vwap", np.nan)) and row["close"] < row["vwap"]

    passed = close_below_ma10 and bearish_body and (ma10_slope_down or close_below_prev_low or close_below_vwap)
    reason_parts = []
    if close_below_ma10:
        reason_parts.append("收盘已回到 5m MA10 下方")
    if bearish_body:
        reason_parts.append("5m 为确认阴线")
    if ma10_slope_down:
        reason_parts.append("MA10 开始下弯")
    if close_below_prev_low:
        reason_parts.append("收盘跌破前一根 5m 低点")
    if close_below_vwap:
        reason_parts.append("价格位于 5m VWAP 下方")
    if not reason_parts:
        reason_parts.append("5m 还没有给出足够的拐头确认")

    return {
        "passed": passed,
        "bar_index": bar_index,
        "reason": "，".join(reason_parts),
    }


def detect_reject_ma10(seg_df: pd.DataFrame, preheat: int) -> int | None:
    visible = seg_df.iloc[preheat:]
    if visible.empty:
        return None

    best_idx = None
    best_score = float("inf")
    for i in range(1, len(visible) - 1):
        row = visible.iloc[i]
        nxt = visible.iloc[i + 1]
        sma10 = row.get("sma10", np.nan)
        if pd.isna(sma10):
            continue
        if not (row["ha_c"] > row["ha_o"]):
            continue
        if not (row["close"] < sma10 and row["ha_h"] >= sma10):
            continue
        if max(row["ha_o"], row["ha_c"]) >= sma10:
            continue
        if nxt["close"] >= row["close"]:
            continue

        wick = row["ha_h"] - max(row["ha_o"], row["ha_c"])
        distance = abs(row["ha_h"] - sma10)
        score = distance - min(wick, 0.2) * 0.1
        if score < best_score:
            best_score = score
            best_idx = preheat + i
    return best_idx


def detect_support_ma10(seg_df: pd.DataFrame, preheat: int) -> int | None:
    visible = seg_df.iloc[preheat:]
    if visible.empty:
        return None

    best_idx = None
    best_score = float("inf")
    for i in range(1, len(visible) - 1):
        row = visible.iloc[i]
        nxt = visible.iloc[i + 1]
        sma10 = row.get("sma10", np.nan)
        if pd.isna(sma10):
            continue
        if not (row["close"] > sma10 and row["ha_l"] <= sma10):
            continue
        if min(row["ha_o"], row["ha_c"]) <= sma10:
            continue
        if nxt["close"] <= row["close"]:
            continue

        wick = min(row["ha_o"], row["ha_c"]) - row["ha_l"]
        distance = abs(row["ha_l"] - sma10)
        score = distance - min(wick, 0.2) * 0.1
        if score < best_score:
            best_score = score
            best_idx = preheat + i
    return best_idx


def detect_signal_b(seg_df: pd.DataFrame, preheat: int) -> int | None:
    visible = seg_df.iloc[preheat:]
    if visible.empty:
        return None

    for i in range(len(visible) - 1):
        row = visible.iloc[i]
        sma10 = row.get("sma10", np.nan)
        sma50 = row.get("sma50", np.nan)
        if pd.isna(sma10) or pd.isna(sma50):
            continue
        if row["open"] > sma50 and row["close"] < sma50 and row["close"] < sma10:
            return preheat + i
    return None


def detect_vwap_intercept(seg_df: pd.DataFrame, start_index: int | None, scenario: str) -> dict:
    if start_index is None:
        return {"passed": False, "bar_index": None, "reason": "没有信号 bar，无法评估 VWAP"}

    signal_row = seg_df.iloc[start_index]
    signal_vwap = signal_row.get("vwap", np.nan)
    if pd.isna(signal_vwap) or signal_row["close"] == 0:
        return {"passed": False, "bar_index": None, "reason": "VWAP 数据缺失"}
    signal_distance = abs(signal_row["close"] - signal_vwap) / signal_row["close"] * 100
    if signal_distance > 0.12:
        return {"passed": False, "bar_index": None, "reason": "本案的主关卡不在 VWAP 附近，重点不在 VWAP 拦截"}

    upper = min(len(seg_df), start_index + 13)
    fallback = None
    for idx in range(start_index, upper):
        row = seg_df.iloc[idx]
        vwap = row.get("vwap", np.nan)
        if pd.isna(vwap) or row["close"] == 0:
            continue
        in_zone = row["low"] <= vwap <= row["high"] or abs(row["close"] - vwap) / row["close"] * 100 <= 0.08
        if not in_zone:
            continue

        next_row = seg_df.iloc[idx + 1] if idx + 1 < len(seg_df) else None
        if scenario == "bearish":
            passed = bool(next_row is not None and next_row["close"] <= vwap)
            reason = "价格反抽到 VWAP 一带后再次失守，VWAP 继续充当压制"
        else:
            passed = bool(next_row is not None and next_row["close"] >= vwap)
            reason = "价格回踩到 VWAP 一带后重新站稳，VWAP 继续充当支撑"
        candidate = {"passed": passed, "bar_index": idx, "reason": reason}
        if passed:
            return candidate
        if fallback is None:
            fallback = candidate

    return fallback or {"passed": False, "bar_index": None, "reason": "信号后没有出现清晰的 VWAP 拦截动作"}


def _annotation_body(row: pd.Series, category: str, scenario: str) -> str:
    sma10 = row.get("sma10", np.nan)
    sma50 = row.get("sma50", np.nan)
    close = row["close"]

    if category in ("reject_ma10", "support_ma10"):
        if pd.isna(sma10) or not close:
            return ""
        if scenario == "bullish":
            distance_pct = round(abs(row["ha_l"] - sma10) / close * 100, 2)
            return f"HA 下影线触及 MA10（距离 {distance_pct}%），实体仍稳在 MA10 上方"
        distance_pct = round(abs(row["ha_h"] - sma10) / close * 100, 2)
        color_text = "绿色反抽" if row["ha_c"] > row["ha_o"] else "非绿色"
        return f"{color_text} HA 反抽触及 MA10（距离 {distance_pct}%），实体仍被压在 MA10 下方"

    if category == "signal_b":
        if pd.isna(sma10) or pd.isna(sma50) or not close:
            return ""
        diff10 = round((close - sma10) / close * 100, 2)
        diff50 = round((close - sma50) / close * 100, 2)
        return f"收盘同时位于 MA10({diff10}%) 和 MA50({diff50}%) 下方，双线跌破成立"

    if category == "trend_accumulation":
        return "长期单边趋势里的第一次反转通常不顺，要观察 2-3 次尝试来累积力量。"

    if category == "kline_quality":
        body = abs(close - row["open"])
        candle_range = row["high"] - row["low"]
        ratio = round(body / candle_range * 100, 1) if candle_range > 0 else 0
        return f"K线实体占比 {ratio}% ，{'趋势强劲' if ratio > 50 else '趋势开始拉扯'}"

    if category == "barrier_test":
        barriers = {}
        if pd.notna(sma50):
            barriers["MA50"] = sma50
        if pd.notna(row.get("sma200", np.nan)):
            barriers["MA200"] = row["sma200"]
        if pd.notna(row.get("vwap", np.nan)):
            barriers["VWAP"] = row["vwap"]
        if barriers and close:
            nearest = min(barriers, key=lambda key: abs(close - barriers[key]))
            distance_pct = round(abs(close - barriers[nearest]) / close * 100, 2)
            return f"价格测试 {nearest}（距离 {distance_pct}%）"
        return "价格测试关键关卡"

    if category == "ma_tangle":
        if pd.notna(sma10) and pd.notna(sma50) and close:
            spread = round(abs(sma10 - sma50) / close * 100, 2)
            return f"均线密集缠绕（MA10-MA50 价差 {spread}%），容易进入垃圾时间"
        return "均线密集缠绕，方向不明"

    if category == "violent_reversal":
        return "极端行情里的深 V 反转，重点是仓位和止损。"

    if category == "opening_gap":
        return "开盘跳空后的急跌，先看是否出现回补或确认。"

    if category == "bear_attack":
        if pd.notna(sma10) and pd.notna(sma50) and close:
            spread = round(abs(sma10 - sma50) / close * 100, 2)
            return f"均线扇形发散（价差 {spread}%），空头总攻形态"
        return "均线扇形发散，空头总攻形态"

    return ""


def build_manual_annotations(seg_id: str, seg_df: pd.DataFrame, timeframe: str) -> list[dict]:
    source_map = CUSTOM_ANNOTATIONS_1M if timeframe == "1m" else CUSTOM_ANNOTATIONS_5M
    specs = source_map.get(seg_id, [])
    annotations = []
    for spec in specs:
        idx = get_bar_index_by_time(seg_df, spec["time"])
        if idx is None:
            continue
        annotations.append(
            {
                "bar_index": idx,
                "type": "info",
                "title": spec["title"],
                "body": spec["body"],
                "anchor_side": spec.get("anchor_side", "top"),
                "auto_pause": spec.get("auto_pause", True),
                "style": spec.get("style", "blue"),
            }
        )
    return annotations


def generate_annotations_1m(
    seg_id: str,
    seg_df: pd.DataFrame,
    preheat: int,
    category: str,
    scenario: str,
    background_note: str = "",
) -> tuple[list[dict], int | None]:
    annotations = [
        {
            "bar_index": preheat,
            "type": "info",
            "title": "回放开始",
            "body": background_note or CATEGORY_DESC_MAP.get(category, ""),
            "anchor_side": "bottom",
            "auto_pause": True,
            "style": "blue",
        }
    ]

    signal_idx = None
    signal_title = "信号!"
    signal_style = "green" if scenario == "bullish" else "red"

    if seg_id in CUSTOM_SIGNAL_TIMES:
        signal_idx = get_bar_index_by_time(seg_df, CUSTOM_SIGNAL_TIMES[seg_id])
        signal_title = "第一次尝试"
    elif category == "reject_ma10":
        signal_idx = detect_reject_ma10(seg_df, preheat)
        signal_title = "Reject MA10!"
        signal_style = "red"
    elif category == "support_ma10":
        signal_idx = detect_support_ma10(seg_df, preheat)
        signal_title = "Support MA10!"
        signal_style = "green"
    elif category == "signal_b":
        signal_idx = detect_signal_b(seg_df, preheat)
        signal_title = "信号B!"
        signal_style = "red"
    elif category == "kline_quality":
        signal_idx = preheat + max(1, int((len(seg_df) - preheat) * 0.6))
        signal_title = "K线质量变化!"
    elif category == "ma_tangle":
        signal_idx = preheat + max(1, int((len(seg_df) - preheat) * 0.6))
        signal_title = "均线缠绕!"
    elif category == "barrier_test":
        signal_idx = preheat + max(1, int((len(seg_df) - preheat) * 0.6))
        signal_title = "关卡测试!"
    elif category == "violent_reversal":
        signal_idx = preheat + max(1, int((len(seg_df) - preheat) * 0.6))
        signal_title = "暴力反转!"
    elif category == "opening_gap":
        signal_idx = preheat + max(1, int((len(seg_df) - preheat) * 0.55))
        signal_title = "跳空暴跌!"
    elif category == "bear_attack":
        signal_idx = preheat + max(1, int((len(seg_df) - preheat) * 0.6))
        signal_title = "空头总攻!"

    if signal_idx is not None and signal_idx < len(seg_df):
        row = seg_df.iloc[signal_idx]
        annotations.append(
            {
                "bar_index": signal_idx,
                "type": "signal",
                "title": signal_title,
                "body": _annotation_body(row, category, scenario),
                "anchor_side": "top" if scenario == "bearish" else "bottom",
                "auto_pause": True,
                "style": signal_style,
            }
        )

    annotations.extend(build_manual_annotations(seg_id, seg_df, "1m"))
    annotations.append(
        {
            "bar_index": len(seg_df) - 1,
            "type": "info",
            "title": "回放结束",
            "body": "",
            "anchor_side": "bottom",
            "auto_pause": False,
            "style": "blue",
        }
    )
    annotations.sort(key=lambda item: item["bar_index"])
    return annotations, signal_idx


def generate_annotations_5m(
    seg_id: str,
    seg_df_5m: pd.DataFrame,
    time_end: str,
    category: str,
    regime_5m: dict,
    regime_15m: dict | None = None,
) -> list[dict]:
    if seg_df_5m.empty:
        return []

    target_bars = seg_df_5m[seg_df_5m["time"] <= time_end]
    bar_index = len(target_bars) - 1 if not target_bars.empty else len(seg_df_5m) - 1

    if category == "signal_b":
        base_body = "切回 1m 看双线跌破细节，同时确认 5m 已经开始拐头。"
    elif category == "trend_accumulation" and regime_15m:
        base_body = f"当前 15m 背景是 {regime_15m['ma_alignment']}，这个概念更依赖高时间框架。"
    else:
        base_body = "切回 1m 查看细节。"

    annotations = [
        {
            "bar_index": bar_index,
            "type": "info",
            "title": "对应 1m 信号时刻",
            "body": base_body,
            "anchor_side": "top",
            "auto_pause": True,
            "style": "blue",
        }
    ]
    annotations.extend(build_manual_annotations(seg_id, seg_df_5m, "5m"))
    annotations.sort(key=lambda item: item["bar_index"])
    return annotations


def evaluate_trend_accumulation_case(
    seg_id: str,
    seg_df_1m: pd.DataFrame,
    regime_15m: dict,
) -> dict:
    attempt_times = MULTI_ATTEMPT_TIMES.get(seg_id, [])
    attempt_indices = [idx for idx in (get_bar_index_by_time(seg_df_1m, t) for t in attempt_times) if idx is not None]
    rule_events = []
    checkpoints = []

    checkpoints.append(
        {
            "key": "background_15m",
            "label": "15m 长期多头背景",
            "passed": regime_15m.get("ma_alignment") == "bull_排列",
            "bar_index": 0,
            "reason": f"15m 均线背景: {regime_15m.get('ma_alignment', 'N/A')}",
        }
    )

    for order, idx in enumerate(attempt_indices, start=1):
        followthrough = measure_followthrough(seg_df_1m, idx, bars_forward=10, scenario="bearish")
        smooth_fail = followthrough["max_extension_pct"] < 0.25
        checkpoints.append(
            {
                "key": f"attempt_{order}",
                "label": f"第 {order} 次尝试依旧不顺",
                "passed": smooth_fail,
                "bar_index": idx,
                "reason": f"后续 {followthrough['bars']} 根内最多只扩展 {followthrough['max_extension_pct']}%，没有顺畅走成单边",
            }
        )
        rule_events.append(
            {
                "type": f"attempt_{order}",
                "timeframe": "1m",
                "bar_index": idx,
                "passed": smooth_fail,
                "reason": checkpoints[-1]["reason"],
            }
        )

    checkpoints.append(
        {
            "key": "wait_higher_tf",
            "label": "等待更高周期同步转弱",
            "passed": True,
            "bar_index": attempt_indices[-1] if attempt_indices else None,
            "reason": "Tang 的核心是：第一次就算能进，也会跌得非常不顺；要等更高时间框架也开始松动。",
        }
    )

    return {
        "rule_events": rule_events,
        "checkpoints": checkpoints,
        "signal_bar_index": attempt_indices[0] if attempt_indices else None,
        "stop_price": None,
    }


def evaluate_rules(
    seg_id: str,
    seg_df_1m: pd.DataFrame,
    seg_df_5m: pd.DataFrame,
    seg_df_15m: pd.DataFrame,
    category: str,
    scenario: str,
    regime_5m: dict,
    regime_15m: dict,
    signal_bar_index: int | None,
) -> dict:
    if category == "trend_accumulation":
        return evaluate_trend_accumulation_case(seg_id, seg_df_1m, regime_15m)

    checkpoints = []
    rule_events = []

    if category == "signal_b":
        signal_time = seg_df_1m.iloc[signal_bar_index]["time"] if signal_bar_index is not None else seg_df_1m.iloc[-1]["time"]
        signal_b_5m = compute_signal_b_confirmation(seg_df_5m, signal_time)
        checkpoints.append(
            {
                "key": "trend_ok",
                "label": "5min 拐头确认",
                "passed": signal_b_5m["passed"],
                "bar_index": signal_b_5m["bar_index"],
                "reason": signal_b_5m["reason"],
            }
        )
        structure_ok = regime_5m.get("ma_spread", 0) >= 0.05
        checkpoints.append(
            {
                "key": "ma_alignment_ok",
                "label": "5min 结构未缠死",
                "passed": structure_ok,
                "bar_index": 0,
                "reason": f"5m MA10-MA50 间距 {regime_5m.get('ma_spread', 0)}%",
            }
        )
    else:
        trend_passed = regime_5m.get("trend") in ("bullish", "bearish")
        trend_matches = (
            (scenario == "bullish" and regime_5m.get("trend") == "bullish")
            or (scenario == "bearish" and regime_5m.get("trend") == "bearish")
            or category in ("ma_tangle", "violent_reversal", "barrier_test")
        )
        checkpoints.append(
            {
                "key": "trend_ok",
                "label": "5min 趋势确认",
                "passed": bool(trend_passed and trend_matches),
                "bar_index": 0,
                "reason": f"5m 趋势: {regime_5m.get('trend', 'N/A')}",
            }
        )

        alignment = regime_5m.get("ma_alignment", "tangled")
        alignment_ok = (
            (scenario == "bullish" and alignment == "bull_排列")
            or (scenario == "bearish" and alignment == "bear_排列")
            or (category == "ma_tangle" and alignment == "tangled")
            or category in ("violent_reversal", "barrier_test")
        )
        checkpoints.append(
            {
                "key": "ma_alignment_ok",
                "label": "均线排列方向",
                "passed": bool(alignment_ok),
                "bar_index": 0,
                "reason": f"5m 均线排列: {alignment}",
            }
        )

    signal_row = None
    if signal_bar_index is not None and signal_bar_index < len(seg_df_1m):
        signal_row = seg_df_1m.iloc[signal_bar_index]

    if category == "signal_b":
        body_passed = False
        body_reason = "未检测到有效信号"
        if signal_row is not None:
            close = signal_row["close"]
            sma10 = signal_row.get("sma10", np.nan)
            sma50 = signal_row.get("sma50", np.nan)
            if pd.notna(sma10) and pd.notna(sma50) and close:
                body_passed = close < sma10 and close < sma50
                diff10 = round((close - sma10) / close * 100, 2)
                diff50 = round((close - sma50) / close * 100, 2)
                body_reason = f"收盘位于 MA10({diff10}%) 与 MA50({diff50}%) 下方"

        checkpoints.append(
            {
                "key": "touch_ma10",
                "label": "跌破 MA10 和 MA50",
                "passed": body_passed,
                "bar_index": signal_bar_index,
                "reason": body_reason,
            }
        )
        checkpoints.append(
            {
                "key": "body_not_cross",
                "label": "收盘未拉回 MA50 上方",
                "passed": bool(signal_row is not None and signal_row["close"] < signal_row.get("sma50", np.nan)),
                "bar_index": signal_bar_index,
                "reason": "收盘仍压在 MA50 下方" if signal_row is not None and signal_row["close"] < signal_row.get("sma50", np.nan) else "收盘重新回到 MA50 上方",
            }
        )
    else:
        touch_passed = signal_row is not None
        touch_reason = "未检测到触及 MA10"
        if signal_row is not None and signal_row["close"]:
            sma10 = signal_row.get("sma10", np.nan)
            if pd.notna(sma10):
                if scenario == "bullish":
                    distance = abs(signal_row["ha_l"] - sma10) / signal_row["close"] * 100
                    touch_reason = f"HA 下影线与 MA10 距离 {distance:.2f}%"
                else:
                    distance = abs(signal_row["ha_h"] - sma10) / signal_row["close"] * 100
                    touch_reason = f"HA 上影线与 MA10 距离 {distance:.2f}%"
        checkpoints.append(
            {
                "key": "touch_ma10",
                "label": "K线触及 MA10",
                "passed": touch_passed,
                "bar_index": signal_bar_index,
                "reason": touch_reason,
            }
        )

        body_passed = False
        body_reason = "未评估"
        if signal_row is not None:
            sma10 = signal_row.get("sma10", np.nan)
            if pd.notna(sma10):
                if scenario == "bullish":
                    body_passed = min(signal_row["ha_o"], signal_row["ha_c"]) > sma10
                    body_reason = "HA 实体保持在 MA10 上方" if body_passed else "HA 实体穿回 MA10"
                else:
                    body_passed = max(signal_row["ha_o"], signal_row["ha_c"]) < sma10
                    body_reason = "HA 实体仍压在 MA10 下方" if body_passed else "HA 实体穿回 MA10"

        checkpoints.append(
            {
                "key": "body_not_cross",
                "label": "实体未穿越",
                "passed": body_passed,
                "bar_index": signal_bar_index,
                "reason": body_reason,
            }
        )

    confirm_idx = signal_bar_index + 1 if signal_bar_index is not None else None
    confirm_passed = False
    confirm_reason = "未评估"
    if confirm_idx is not None and confirm_idx < len(seg_df_1m) and signal_row is not None:
        next_row = seg_df_1m.iloc[confirm_idx]
        if scenario == "bullish":
            confirm_passed = next_row["close"] > signal_row["close"]
            confirm_reason = "确认K 延续上涨" if confirm_passed else "确认K 没有延续上涨"
        else:
            confirm_passed = next_row["close"] < signal_row["close"]
            confirm_reason = "确认K 延续下跌" if confirm_passed else "确认K 没有延续下跌"
    checkpoints.append(
        {
            "key": "confirm_bar",
            "label": "确认K延续方向",
            "passed": confirm_passed,
            "bar_index": confirm_idx,
            "reason": confirm_reason,
        }
    )

    stop_price = None
    if signal_row is not None:
        if category == "signal_b":
            stop_price = round(max(signal_row["high"], signal_row.get("sma50", signal_row["high"])) + 0.05, 2)
            stop_reason = f"止损放在信号K高点 / MA50 上方: {stop_price}"
        elif scenario == "bullish":
            stop_price = round(signal_row["ha_l"] - 0.05, 2)
            stop_reason = f"止损设在信号K低点下方: {stop_price}"
        else:
            stop_price = round(signal_row["ha_h"] + 0.05, 2)
            stop_reason = f"止损设在信号K高点上方: {stop_price}"
        stop_passed = True
    else:
        stop_reason = "未定义"
        stop_passed = False

    checkpoints.append(
        {
            "key": "stop_defined",
            "label": "止损位明确",
            "passed": stop_passed,
            "bar_index": signal_bar_index,
            "reason": stop_reason,
            "metrics": {"stop_price": stop_price} if stop_price is not None else {},
        }
    )

    barrier_dist = regime_5m.get("barrier_distance_pct", 0)
    checkpoints.append(
        {
            "key": "reward_ok",
            "label": "目标空间足够",
            "passed": bool(barrier_dist >= 0.15),
            "bar_index": signal_bar_index,
            "reason": f"最近关卡({regime_5m.get('nearest_barrier', 'N/A')}) 距离 {barrier_dist}%",
            "metrics": {"barrier_distance_pct": barrier_dist},
        }
    )

    if category == "signal_b":
        vwap_intercept = detect_vwap_intercept(seg_df_1m, signal_bar_index, scenario)
        checkpoints.append(
            {
                "key": "vwap_intercept",
                "label": "VWAP 拦截确认",
                "passed": vwap_intercept["passed"],
                "bar_index": vwap_intercept["bar_index"],
                "reason": vwap_intercept["reason"],
            }
        )
        if vwap_intercept["bar_index"] is not None:
            rule_events.append(
                {
                    "type": "vwap_intercept",
                    "timeframe": "1m",
                    "bar_index": vwap_intercept["bar_index"],
                    "passed": vwap_intercept["passed"],
                    "reason": vwap_intercept["reason"],
                }
            )

    forbidden_flags = []
    if category not in ("signal_b", "ma_tangle") and regime_5m.get("ma_alignment") == "tangled":
        forbidden_flags.append("均线缠绕")
    if category not in ("signal_b", "ma_tangle") and regime_5m.get("ma_spread", 0) < 0.03:
        forbidden_flags.append("均线过密")
    if signal_row is not None and signal_row["time"] < "10:00" and category not in ("opening_gap",):
        forbidden_flags.append("开盘30分钟内")

    checkpoints.append(
        {
            "key": "forbidden_absent",
            "label": "不在禁止条件内",
            "passed": len(forbidden_flags) == 0,
            "bar_index": None,
            "reason": "无禁做条件" if not forbidden_flags else f"触发: {', '.join(forbidden_flags)}",
            "metrics": {"forbidden_flags": forbidden_flags},
        }
    )

    if signal_bar_index is not None:
        rule_events.append(
            {
                "type": category,
                "timeframe": "1m",
                "bar_index": signal_bar_index,
                "passed": True,
                "reason": checkpoints[2]["reason"] if len(checkpoints) > 2 else "信号触发",
            }
        )

    return {
        "rule_events": rule_events,
        "checkpoints": checkpoints,
        "signal_bar_index": signal_bar_index,
        "stop_price": stop_price,
    }


def bars_to_records(df: pd.DataFrame) -> list[dict]:
    records = []
    for _, row in df.iterrows():
        rec = {
            "t": row["time"],
            "O": round(row["open"], 2),
            "H": round(row["high"], 2),
            "L": round(row["low"], 2),
            "C": round(row["close"], 2),
            "V": int(row["volume"]) if pd.notna(row["volume"]) else 0,
            "vw": round(row["vwap"], 2) if pd.notna(row.get("vwap", np.nan)) else 0,
            "hO": round(row["ha_o"], 2),
            "hH": round(row["ha_h"], 2),
            "hL": round(row["ha_l"], 2),
            "hC": round(row["ha_c"], 2),
        }
        for col, key in (("sma10", "m10"), ("sma50", "m50"), ("sma200", "m200")):
            if pd.notna(row.get(col, np.nan)):
                rec[key] = round(row[col], 2)
        records.append(rec)
    return records


def merge_seed_config(seed_key: str, source_key: str, seed: dict) -> dict:
    base = {
        "id": f"seed_{seed_key}",
        "title": source_key[3:],
        "date": seed["date"],
        "interval": seed.get("interval", "1m"),
        "time_start": seed["time_start"],
        "time_end": seed["time_end"],
        "visible_candles": seed["visible_candles"],
        "is_seed": True,
        "category": SEED_CATEGORIES[seed_key]["cat"],
        "chapter": SEED_CATEGORIES[seed_key]["chapter"],
        "scenario": SEED_CATEGORIES[seed_key]["scenario"],
        "variant_label": "",
        "teaching_focus": "",
        "background_note": "",
    }
    base.update(SEED_OVERRIDES.get(seed_key, {}))
    return base


def build_segment(config: dict, df_1m: pd.DataFrame, df_5m: pd.DataFrame, df_15m: pd.DataFrame) -> dict | None:
    seg_1m = slice_1m_segment(df_1m, config["date"], config["time_start"], config["time_end"]).reset_index(drop=True)
    if seg_1m.empty:
        print(f"  WARNING: missing 1m data for {config['id']}")
        return None

    preheat = int((seg_1m["time"] < config["time_start"]).sum())
    seg_5m = slice_context_segment(
        df_5m,
        config["date"],
        config["time_end"],
        visible_candles=config.get("visible_candles"),
        exact_window=(config["interval"] == "5m"),
    ).reset_index(drop=True)
    seg_15m = slice_context_segment(df_15m, config["date"], config["time_end"]).reset_index(drop=True)

    regime_5m = compute_regime(seg_5m, config["time_end"])
    regime_15m = compute_regime(seg_15m, config["time_end"])

    annotations_1m, signal_bar_index = generate_annotations_1m(
        config["id"],
        seg_1m,
        preheat,
        config["category"],
        config["scenario"],
        background_note=config.get("background_note", ""),
    )
    annotations_5m = generate_annotations_5m(
        config["id"],
        seg_5m,
        config["time_end"],
        config["category"],
        regime_5m,
        regime_15m=regime_15m,
    )

    bars_1m_records = bars_to_records(seg_1m)
    bars_5m_records = bars_to_records(seg_5m) if not seg_5m.empty else []

    rules = evaluate_rules(
        config["id"],
        seg_1m,
        seg_5m,
        seg_15m,
        config["category"],
        config["scenario"],
        regime_5m,
        regime_15m,
        signal_bar_index,
    )

    return {
        "id": config["id"],
        "title": config["title"],
        "category": config["category"],
        "date": config["date"],
        "source_interval": config["interval"],
        "is_seed": config.get("is_seed", True),
        "chapter": config["chapter"],
        "scenario": config["scenario"],
        "variant_label": config.get("variant_label", ""),
        "teaching_focus": config.get("teaching_focus", ""),
        "background_note": config.get("background_note", ""),
        "regime_5m": regime_5m,
        "regime_15m": regime_15m,
        "preheat_count": preheat,
        "derived": {
            "viewport_1m": compute_viewport(bars_1m_records),
            "viewport_5m": compute_viewport(bars_5m_records),
            "rule_events": rules["rule_events"],
            "checkpoints": rules["checkpoints"],
            "signal_bar_index": rules["signal_bar_index"],
            "stop_price": rules["stop_price"],
        },
        "bars_1m": bars_1m_records,
        "bars_5m": bars_5m_records,
        "annotations_1m": annotations_1m,
        "annotations_5m": annotations_5m,
    }


def main() -> None:
    print("=" * 60)
    print("prepare_data.py — Teaching Segment Generator v0.4")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[1] Load market data")
    df_1m = load_and_filter(FILE_1M)
    df_5m = load_and_filter(FILE_5M)

    print("\n[2] Recompute intraday cumulative VWAP")
    df_1m = compute_intraday_vwap(df_1m)
    df_5m = compute_intraday_vwap(df_5m)

    print("\n[3] Compute HA / SMA / 15m aggregation")
    df_1m = compute_ha(df_1m)
    df_5m = compute_ha(df_5m)
    df_1m = compute_sma(df_1m)
    df_5m = compute_sma(df_5m)
    df_15m = aggregate_to_15m(df_1m)
    print(f"  1m bars:  {len(df_1m)}")
    print(f"  5m bars:  {len(df_5m)}")
    print(f"  15m bars: {len(df_15m)}")

    print("\n[4] Load seed cases")
    seeds = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    configs = []
    for key, seed in seeds.items():
        num = key[:2]
        if num in ("12", "13") or num not in SEED_CATEGORIES:
            continue
        configs.append(merge_seed_config(num, key, seed))
    configs.extend(CUSTOM_SEGMENTS)
    print(f"  Build configs: {len(configs)}")

    print("\n[5] Build teaching segments")
    segments = []
    for config in configs:
        print(
            f"  [{config['id']}] {config['date']} {config['time_start']}-{config['time_end']} "
            f"{config['category']} ({config['interval']})"
        )
        segment = build_segment(config, df_1m, df_5m, df_15m)
        if segment is None:
            continue
        segments.append(segment)

    output = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "version": "4.0",
            "total_segments": len(segments),
        },
        "categories": CATEGORY_DEFS,
        "segments": segments,
    }

    out_path = OUTPUT_DIR / "teaching_segments.json"
    out_path.write_text(json.dumps(to_builtin(output), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"\n[6] Wrote {out_path}")
    print(f"  File size: {out_path.stat().st_size / 1024:.1f} KB")
    print(f"  Segments: {len(segments)}")


if __name__ == "__main__":
    main()
