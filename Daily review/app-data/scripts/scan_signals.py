#!/usr/bin/env python3
"""配置驱动的信号扫描器 — 读数据 JSON + 策略 JSON → 输出含 annotations 的 reviewed JSON。

用法:
    python scan_signals.py --data <processed.json> --strategy <strategy.json> [--out <output.json>]

数据 JSON 来自 build_json.py，每根 bar 已含 hO/hH/hL/hC、m10/m50/m200、vw。
策略 JSON 描述信号检测条件，不包含指标计算逻辑。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def find_project_root() -> Path:
    """Locate the Daily review project root regardless of script folder."""
    script_dir = Path(__file__).resolve().parent
    for candidate in (script_dir, *script_dir.parents):
        if (candidate / "daily-review.html").exists():
            return candidate
    return script_dir


PROJECT_ROOT = find_project_root()


# ---------------------------------------------------------------------------
# 1. 策略配置加载
# ---------------------------------------------------------------------------

def load_strategy(path: str) -> dict:
    """读取并校验策略配置 JSON。"""
    with open(path, encoding="utf-8") as f:
        strat = json.load(f)

    required = ["name", "version", "trend", "signals", "exit", "filter"]
    missing = [k for k in required if k not in strat]
    if missing:
        raise ValueError(f"策略配置缺少字段: {missing}")

    return strat


def load_data(path: str) -> dict:
    """读取 processed JSON。"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if "bars_1m" not in data:
        raise ValueError("数据 JSON 缺少 bars_1m")

    return data


# ---------------------------------------------------------------------------
# 2. 趋势检测
# ---------------------------------------------------------------------------

def detect_trends_relaxed(
    bars_5m: list[dict],
    fast_ma: str,
    slow_ma: str,
    slope_bars: int,
) -> list[str | None]:
    """Relaxed 趋势：fast_ma vs slow_ma 方向 + fast_ma 斜率。"""
    trends: list[str | None] = []
    for j, bar in enumerate(bars_5m):
        fast = bar.get(fast_ma)
        slow = bar.get(slow_ma)
        if fast is None or slow is None:
            trends.append(None)
            continue

        slope = 0.0
        if j >= slope_bars:
            prev_fast = bars_5m[j - slope_bars].get(fast_ma)
            if prev_fast is not None:
                slope = fast - prev_fast

        if fast > slow and slope > 0:
            trends.append("bullish")
        elif fast < slow and slope < 0:
            trends.append("bearish")
        else:
            trends.append(None)

    return trends


def detect_trends_strict(
    bars_5m: list[dict],
    lines: list[str],
) -> list[str | None]:
    """Strict 趋势：多条均线严格排列。

    bullish: lines[0] > lines[1] > ... > lines[-1]
    bearish: lines[0] < lines[1] < ... < lines[-1]
    只使用数据中实际存在的字段。
    """
    trends: list[str | None] = []
    for bar in bars_5m:
        vals = [bar.get(l) for l in lines]
        # 过滤掉数据中不存在的字段
        vals = [v for v in vals if v is not None]
        if len(vals) < 2:
            trends.append(None)
            continue

        if all(vals[i] > vals[i + 1] for i in range(len(vals) - 1)):
            trends.append("bullish")
        elif all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)):
            trends.append("bearish")
        else:
            trends.append(None)

    return trends


def detect_trends(bars_5m: list[dict], trend_cfg: dict) -> list[str | None]:
    """根据配置选择趋势检测方法。"""
    method = trend_cfg.get("method", "relaxed")
    if method == "strict":
        lines = trend_cfg.get("lines", ["m10", "m50", "m200"])
        return detect_trends_strict(bars_5m, lines)
    else:
        return detect_trends_relaxed(
            bars_5m,
            fast_ma=trend_cfg.get("fast_ma", "m10"),
            slow_ma=trend_cfg.get("slow_ma", "m50"),
            slope_bars=trend_cfg.get("slope_bars", 3),
        )


# ---------------------------------------------------------------------------
# 3. 1m → 5m 趋势映射
# ---------------------------------------------------------------------------

def map_1m_to_5m_trends(
    bars_1m: list[dict],
    bars_5m: list[dict],
    trends_5m: list[str | None],
) -> list[str | None]:
    """将 5m 趋势映射到每根 1m bar。

    每根 1m bar 继承当前或前一根 5m bar 的趋势。
    """
    if not bars_5m or not trends_5m:
        return [None] * len(bars_1m)

    # 构建 5m 时间索引
    ts_5m = [bar["t"] for bar in bars_5m]

    result: list[str | None] = []
    last_5m_idx = 0

    for bar_1m in bars_1m:
        t = bar_1m["t"]
        # 找到 <= 当前时间的最新 5m bar
        while last_5m_idx + 1 < len(ts_5m) and ts_5m[last_5m_idx + 1] <= t:
            last_5m_idx += 1
        result.append(trends_5m[last_5m_idx])

    return result


# ---------------------------------------------------------------------------
# 4. 通用条件匹配器
# ---------------------------------------------------------------------------

def _is_green(bar: dict) -> bool:
    return bar.get("hC", 0) >= bar.get("hO", 0)


def _is_red(bar: dict) -> bool:
    return bar.get("hC", 0) < bar.get("hO", 0)


def _resolve_value(bar: dict, ref: str) -> float | None:
    """解析字段引用：可以是 bar 的字段名或数字常量。"""
    if isinstance(ref, (int, float)):
        return float(ref)
    return bar.get(ref)


def _compare(left: float | None, operator: str, right: float | None) -> bool:
    """通用比较。"""
    if left is None or right is None:
        return False
    ops = {
        ">=": left >= right,
        "<=": left <= right,
        ">": left > right,
        "<": left < right,
        "==": left == right,
    }
    return ops.get(operator, False)


def match_conditions(bar: dict, conditions: dict) -> bool:
    """通用条件匹配器 — 读配置的 field/operator/target 做比较。

    支持的条件类型:
    - candle_color: "green" / "red"
    - 带 field/operator/target 的比较条件
    - 带 fields (列表) 的多字段条件 — 所有字段都满足
    """
    for key, cond in conditions.items():
        if key == "candle_color":
            if cond == "green" and not _is_green(bar):
                return False
            if cond == "red" and not _is_red(bar):
                return False
            continue

        if isinstance(cond, dict):
            # 单字段比较
            if "field" in cond:
                left = _resolve_value(bar, cond["field"])
                right = _resolve_value(bar, cond["target"])
                if not _compare(left, cond["operator"], right):
                    return False
            # 多字段比较 — 所有字段都必须满足
            elif "fields" in cond:
                for f in cond["fields"]:
                    left = _resolve_value(bar, f)
                    right = _resolve_value(bar, cond["target"])
                    if not _compare(left, cond["operator"], right):
                        return False

    return True


def match_confirm(bar: dict | None, confirm: dict | None) -> bool:
    """确认条件：下一根 bar 的颜色。"""
    if confirm is None or bar is None:
        return confirm is None
    if "next_bar_color" in confirm:
        expected = confirm["next_bar_color"]
        if expected == "green":
            return _is_green(bar)
        if expected == "red":
            return _is_red(bar)
    return True


# ---------------------------------------------------------------------------
# 5. 评分系统
# ---------------------------------------------------------------------------

def compute_score(
    bar: dict,
    trend: str | None,
    direction: str,
    scoring_cfg: dict,
    filter_cfg: dict,
) -> float:
    """参数化评分 — 维度和阈值从配置读取。"""
    if not scoring_cfg.get("enabled", False):
        return 0.0

    s = 0.0
    dims = scoring_cfg.get("dimensions", {})

    # 1. trend_clarity
    if "trend_clarity" in dims:
        expected = "bearish" if direction == "bearish" else "bullish"
        s += dims["trend_clarity"]["max"] if trend == expected else 0

    # 2. entangle_distance
    if "entangle_distance" in dims:
        m10 = bar.get("m10")
        m50 = bar.get("m50")
        if m10 is not None and m50 is not None:
            dist = abs(m10 - m50)
            threshold = filter_cfg.get("entangle_threshold", 0.12)
            margin = dist - threshold
            if margin > 0.5:
                s += dims["entangle_distance"]["max"]
            elif margin > 0:
                s += 1

    # 3. vwap_alignment
    if "vwap_alignment" in dims:
        vw = bar.get("vw")
        price = bar.get("hC")
        if vw is not None and price is not None:
            if direction == "bearish" and price < vw:
                s += dims["vwap_alignment"]["max"]
            elif direction == "bullish" and price > vw:
                s += dims["vwap_alignment"]["max"]

    # 4. space_to_barrier
    if "space_to_barrier" in dims:
        space = _compute_space(bar, direction)
        threshold = filter_cfg.get("space_threshold", 0.30)
        if space > 2.0:
            s += dims["space_to_barrier"]["max"]
        elif space > threshold:
            s += 1

    # 5. kline_quality
    if "kline_quality" in dims:
        body = abs(bar.get("hC", 0) - bar.get("hO", 0))
        shadow = (bar.get("hH", 0) - bar.get("hL", 0)) - body
        total = body + shadow
        if total > 0:
            ratio = body / total
            if ratio > 0.7:
                s += dims["kline_quality"]["max"]
            elif ratio > 0.4:
                s += 1

    max_total = scoring_cfg.get("max_total", 10)
    return min(s, max_total)


def _compute_space(bar: dict, direction: str) -> float:
    """计算信号方向上到最近障碍的距离。"""
    price = bar.get("hC", 0)
    m50 = bar.get("m50")
    m200 = bar.get("m200")
    vw = bar.get("vw")

    barriers: list[float] = []
    for b in [m50, m200, vw]:
        if b is not None:
            barriers.append(b)

    if not barriers:
        return 999.0

    if direction == "bearish":
        below = [b for b in barriers if b < price]
        return min(price - b for b in below) if below else 999.0
    else:
        above = [b for b in barriers if b > price]
        return min(b - price for b in above) if above else 999.0


# ---------------------------------------------------------------------------
# 6. Hard block 检测
# ---------------------------------------------------------------------------

def check_hard_blocks(
    bar: dict,
    trend: str | None,
    direction: str,
    filter_cfg: dict,
    hard_blocks_cfg: dict,
) -> list[str]:
    """检查硬阻断条件。"""
    blocks: list[str] = []

    if hard_blocks_cfg.get("no_trend", False):
        expected = "bearish" if direction == "bearish" else "bullish"
        if not trend or trend != expected:
            blocks.append("no_trend")

    if hard_blocks_cfg.get("entangle", False):
        m10 = bar.get("m10")
        m50 = bar.get("m50")
        if m10 is not None and m50 is not None:
            dist = abs(m10 - m50)
            if dist < filter_cfg.get("entangle_threshold", 0.12):
                blocks.append("entangle")

    if hard_blocks_cfg.get("no_space", False):
        space = _compute_space(bar, direction)
        if space < filter_cfg.get("space_threshold", 0.30):
            blocks.append("no_space")

    return blocks


# ---------------------------------------------------------------------------
# 7. 主扫描逻辑
# ---------------------------------------------------------------------------

def _time_in_session(t: str, session: dict) -> bool:
    """
    检查时间是否在交易窗口内。

    `start` / `end` 为 `None` 时视为该侧无边界（兼容 tang_v4_4_slope.json：
    "V4.4 源码没有时间锁"，session.start / end 都是 null）。空 dict 时维持
    旧默认 10:00–15:45（用于早期策略 v1~v3）。
    """
    if not session:
        start, end = "10:00", "15:45"
    else:
        start = session.get("start", "10:00")
        end = session.get("end", "15:45")
    if start is not None and t < start:
        return False
    if end is not None and t > end:
        return False
    return True


# ---------------------------------------------------------------------------
# 7a. v4 declarative scanner（与 daily-review.html scanSignalsDeclarative 对齐）
#
# v4.x 策略（如 tang_v4_4_slope）的 signals[].conditions 用一组词汇描述：
#   trend_5m / ma10_slope / space_ok / not_tangled / previous_range_touch /
#   previous_close_filter / current_bar_color / previous_elite / can_trigger
# 这些都不是 v1~v3 的 candle_color / field+operator+target 体系，老的
# match_conditions() 看不懂会全静默跳过 → 每根 bar 都通过 → 信号过密。
#
# 这里端口 JS 端的实现（一一对应到 daily-review.html L4193 matchesConditions
# 与 L4245 scanSignalsDeclarative），并在 scan_day() 顶部做能力检测路由。
# ---------------------------------------------------------------------------

DECLARATIVE_CONDITION_KEYS = frozenset({
    "can_trigger", "trend_5m", "ma10_slope", "space_ok", "not_tangled",
    "previous_range_touch", "previous_close_filter",
    "current_bar_color", "previous_elite",
})


def is_strategy_declarative(strategy: dict) -> bool:
    """检测 signals[].conditions 是否使用 v4 declarative 词汇。"""
    sigs = strategy.get("signals") or []
    for s in sigs:
        c = (s or {}).get("conditions") or {}
        if any(k in DECLARATIVE_CONDITION_KEYS for k in c.keys()):
            return True
    return False


def detect_trends_stack(
    bars_5m: list[dict],
    lines: list[str] | None = None,
) -> list[str | None]:
    """
    `regular_close_5m_ma_stack` 趋势：m10 > m20 > m30 = bullish；m10 < m20 < m30 = bearish。
    任一线缺失返回 None。
    """
    ks = lines if (lines and len(lines) >= 2) else ["m10", "m20", "m30"]
    out: list[str | None] = []
    for bar in bars_5m:
        vals = [bar.get(k) for k in ks]
        if any(v is None for v in vals):
            out.append(None)
            continue
        asc = all(vals[i - 1] > vals[i] for i in range(1, len(vals)))
        desc = all(vals[i - 1] < vals[i] for i in range(1, len(vals)))
        if asc:
            out.append("bullish")
        elif desc:
            out.append("bearish")
        else:
            out.append(None)
    return out


def _detect_trends_routed(bars_5m: list[dict], strategy: dict) -> list[str | None]:
    trend_cfg = strategy.get("trend") or {}
    if trend_cfg.get("method") == "regular_close_5m_ma_stack":
        return detect_trends_stack(bars_5m, trend_cfg.get("lines"))
    return detect_trends(bars_5m, trend_cfg)


def compute_bar_features_v4(
    bar: dict,
    prev: dict,
    trend_1m: str | None,
    opts: dict,
) -> dict:
    """
    每根 bar 的特征包，喂给 matches_declarative_conditions()。
    严格对应 daily-review.html `computeBarFeatures()` (L3978)。
    """
    m10 = bar.get("m10")
    pHL, pHH, pHC = prev.get("hL"), prev.get("hH"), prev.get("hC")
    pM10 = prev.get("m10")
    close = bar.get("C")

    # touch detection（前根 HA 区间是否跨过任一触发线）
    touched_line = None
    for k in opts.get("touch_lines") or ["m10", "m20", "m30"]:
        line = prev.get(k)
        if line is not None and pHL is not None and pHH is not None and pHL <= line <= pHH:
            touched_line = k
            break
    touch_prev = touched_line is not None

    # space（最近上方/下方 barrier 距离）
    space_thresh = (close or 0) * opts["space_ratio"]
    barrier_keys = opts.get("space_barriers") or ["m50", "m200", "vw"]
    barriers = [(k, bar.get(k)) for k in barrier_keys if bar.get(k) is not None]
    above = sorted([b for b in barriers if close is not None and b[1] > close], key=lambda x: x[1])
    below = sorted([b for b in barriers if close is not None and b[1] < close], key=lambda x: -x[1])
    space_call_gap = (above[0][1] - close) if (above and close is not None) else float("inf")
    space_put_gap = (close - below[0][1]) if (below and close is not None) else float("inf")
    space_call = space_call_gap >= space_thresh
    space_put = space_put_gap >= space_thresh

    # entangle（按 close 比例算阈值）
    entangle_keys = opts.get("entangle_lines") or ["m10", "m20", "m30", "m50"]
    e_vals = [bar.get(k) for k in entangle_keys]
    e_vals = [v for v in e_vals if v is not None]
    spread = (max(e_vals) - min(e_vals)) if len(e_vals) >= 2 else 0
    not_tangled = spread >= (close or 0) * opts["entangle_ratio"]

    # elite (前根 HA 同时叠 MA10 + 任一 major barrier)
    base_t10 = (
        pM10 is not None and pHL is not None and pHH is not None and pHL <= pM10 <= pHH
    )
    elite_match = False
    for k in opts.get("elite_major_lines") or ["m50", "m200", "vw"]:
        v = prev.get(k)
        if v is not None and pHL is not None and pHH is not None and pHL <= v <= pHH:
            elite_match = True
            break
    previous_elite = base_t10 and elite_match

    return {
        "trend": trend_1m,
        "slope_up": pM10 is not None and m10 is not None and m10 > pM10,
        "slope_down": pM10 is not None and m10 is not None and m10 < pM10,
        "is_green": (bar.get("hC") or 0) > (bar.get("hO") or 0),
        "is_red": (bar.get("hC") or 0) < (bar.get("hO") or 0),
        "touch_prev": touch_prev,
        "close_filter_call": pM10 is not None and pHC is not None and pHC >= pM10,
        "close_filter_put": pM10 is not None and pHC is not None and pHC <= pM10,
        "space_call": space_call,
        "space_put": space_put,
        "not_tangled": not_tangled,
        "previous_elite": previous_elite,
    }


def matches_declarative_conditions(features: dict, conds: dict) -> bool:
    """对应 daily-review.html `matchesConditions()` (L4193)。未知 key 静默通过。"""
    for key, want in conds.items():
        if key == "can_trigger":
            continue  # 由 cooldown / position 状态门控
        if key == "trend_5m":
            if features["trend"] != want:
                return False
        elif key == "ma10_slope":
            if want == "up" and not features["slope_up"]:
                return False
            if want == "down" and not features["slope_down"]:
                return False
        elif key == "space_ok":
            if want == "call" and not features["space_call"]:
                return False
            if want == "put" and not features["space_put"]:
                return False
        elif key == "not_tangled":
            if want is True and not features["not_tangled"]:
                return False
            if want is False and features["not_tangled"]:
                return False
        elif key == "previous_range_touch":
            if want and not features["touch_prev"]:
                return False
        elif key == "previous_close_filter":
            s = str(want)
            if ">=" in s and not features["close_filter_call"]:
                return False
            if "<=" in s and not features["close_filter_put"]:
                return False
        elif key == "current_bar_color":
            if want == "green" and not features["is_green"]:
                return False
            if want == "red" and not features["is_red"]:
                return False
        elif key == "previous_elite":
            if want is True and not features["previous_elite"]:
                return False
            if want is False and features["previous_elite"]:
                return False
        # else: unknown key, pass-through
    return True


def _v4_signal_body(sig_def: dict, features: dict) -> str:
    direction = "5m 多头" if sig_def.get("direction") == "bullish" else "5m 空头"
    if features["slope_up"]:
        slope = "MA10↑"
    elif features["slope_down"]:
        slope = "MA10↓"
    else:
        slope = "MA10–"
    is_strong = (sig_def.get("conditions") or {}).get("previous_elite") is True
    tag = "Elite 触碰" if is_strong else "触碰 MA10/20/30"
    return f"{direction} · {slope} · {tag}"


def _v4_signal_style(sig_def: dict, is_call: bool, is_strong: bool) -> str:
    return sig_def.get("style") or (
        ("teal" if is_strong else "green") if is_call else ("orange" if is_strong else "red")
    )


def _v4_signal_anchor(sig_def: dict, is_call: bool) -> str:
    return sig_def.get("anchor_side") or ("bottom" if is_call else "top")


def _activation_probe(
    pending: dict,
    bars_1m: list[dict],
    i: int,
    features: dict,
    activation_cfg: dict,
) -> dict | None:
    if i <= pending["index"]:
        return None
    bar = bars_1m[i]
    close = bar.get("C")
    if close is None:
        return None

    confirm_price = activation_cfg.get("confirm_price") or "close"
    allow_strong_wick = confirm_price in {"close_or_strong_wick", "strong_wick_or_close"}
    strong_wick_cfg = activation_cfg.get("strong_wick") or {}
    close_position_min = strong_wick_cfg.get("close_position_min", 0.6)
    require_same_direction = activation_cfg.get("require_same_direction_bar") is not False
    require_slope = activation_cfg.get("require_ma10_slope_still_aligned") is not False
    color_ok = features["is_green"] if pending["is_call"] else features["is_red"]
    slope_ok = features["slope_up"] if pending["is_call"] else features["slope_down"]

    window = bars_1m[pending["index"]:i]
    high = bar.get("H")
    low = bar.get("L")
    close_confirmed = False
    wick_confirmed = False
    close_position = None
    strong_wick_confirmed = False
    if pending["is_call"]:
        highs = [b.get("H") for b in window if b.get("H") is not None]
        if not highs:
            return None
        level = max(highs)
        close_confirmed = close > level
        wick_confirmed = high is not None and high > level
        miss_by = level - close
    else:
        lows = [b.get("L") for b in window if b.get("L") is not None]
        if not lows:
            return None
        level = min(lows)
        close_confirmed = close < level
        wick_confirmed = low is not None and low < level
        miss_by = close - level

    if high is not None and low is not None and high > low:
        close_position = (close - low) / (high - low)
        strong_wick_confirmed = (
            close_position >= close_position_min
            if pending["is_call"]
            else close_position <= (1 - close_position_min)
        )
    price_confirmed = close_confirmed or (
        allow_strong_wick and wick_confirmed and strong_wick_confirmed
    )
    confirm_method = (
        "close"
        if close_confirmed
        else ("strong_wick" if allow_strong_wick and wick_confirmed and strong_wick_confirmed else None)
    )
    is_activation = (
        price_confirmed
        and (not require_same_direction or color_ok)
        and (not require_slope or slope_ok)
    )
    return {
        "breakout_level": level,
        "close": close,
        "high": high,
        "low": low,
        "price_confirmed": price_confirmed,
        "close_confirmed": close_confirmed,
        "wick_confirmed": wick_confirmed,
        "close_position": close_position,
        "strong_wick_confirmed": strong_wick_confirmed,
        "allow_strong_wick": allow_strong_wick,
        "confirm_method": confirm_method,
        "color_ok": color_ok,
        "slope_ok": slope_ok,
        "require_same_direction": require_same_direction,
        "require_slope": require_slope,
        "miss_by": miss_by,
        "is_activation": is_activation,
    }


def _update_pending_activation_stats(pending: dict, probe: dict, bar: dict, index: int) -> None:
    pending["last_checked_index"] = index
    pending["last_checked_time"] = bar.get("t", "")
    pending["last_breakout_level"] = probe.get("breakout_level")
    close = probe.get("close")
    if close is not None:
        best = pending.get("best_close")
        if best is None:
            pending["best_close"] = close
        elif pending["is_call"]:
            pending["best_close"] = max(best, close)
        else:
            pending["best_close"] = min(best, close)

    best = pending.get("best_close")
    level = probe.get("breakout_level")
    if best is not None and level is not None:
        pending["miss_by"] = level - best if pending["is_call"] else best - level

    wick = probe.get("high") if pending["is_call"] else probe.get("low")
    if wick is not None:
        best_wick = pending.get("best_wick")
        if best_wick is None:
            pending["best_wick"] = wick
        elif pending["is_call"]:
            pending["best_wick"] = max(best_wick, wick)
        else:
            pending["best_wick"] = min(best_wick, wick)

    if probe.get("allow_strong_wick") and probe.get("wick_confirmed"):
        pending["wick_confirmed_count"] = pending.get("wick_confirmed_count", 0) + 1
        pending["last_wick_confirmed_probe"] = probe

    if probe.get("price_confirmed"):
        pending["price_confirmed_count"] = pending.get("price_confirmed_count", 0) + 1
        pending["last_price_confirmed_probe"] = probe

    failed_gates: list[str] = []
    gate_probe = pending.get("last_price_confirmed_probe") or pending.get("last_wick_confirmed_probe") or probe
    if gate_probe.get("price_confirmed"):
        if gate_probe.get("require_same_direction") and not gate_probe.get("color_ok"):
            failed_gates.append("HA 颜色未顺向")
        if gate_probe.get("require_slope") and not gate_probe.get("slope_ok"):
            failed_gates.append("MA10 斜率未顺向")

    if pending.get("price_confirmed_count", 0) > 0 and failed_gates:
        pending["expiry_gate_reason"] = f"曾触价但{'、'.join(failed_gates)}"
    elif pending.get("price_confirmed_count", 0) > 0:
        pending["expiry_gate_reason"] = "曾触价但未形成完整确认"
    elif pending.get("wick_confirmed_count", 0) > 0 and gate_probe.get("close_position") is not None:
        pos_text = f"{round(gate_probe['close_position'] * 100)}%"
        pending["expiry_gate_reason"] = (
            f"曾刺破确认线，但收盘位置不够强（{pos_text}）"
            if pending["is_call"]
            else f"曾刺破确认线，但收盘位置不够弱（{pos_text}）"
        )
    else:
        pending["expiry_gate_reason"] = (
            f"窗口内没有{_activation_requirement_text(pending.get('activation_confirm_price'), pending['is_call'])}"
        )


def _activation_method_text(method: str | None, is_call: bool) -> str:
    if method == "strong_wick":
        return "强势刺破" if is_call else "强势下破"
    return "收盘突破" if is_call else "收盘跌破"


def _activation_requirement_text(confirm_price: str | None, is_call: bool) -> str:
    if confirm_price in {"close_or_strong_wick", "strong_wick_or_close"}:
        return "收盘突破或强势刺破" if is_call else "收盘跌破或强势下破"
    return "收盘突破" if is_call else "收盘跌破"


def _activation_body(
    pending: dict,
    activation_bar: dict,
    breakout_level: float,
    delay_bars: int,
    confirm_method: str | None = None,
) -> str:
    setup_time = pending["setup_bar"].get("t", f"#{pending['index']}")
    activation_time = activation_bar.get("t", "")
    direction = "CALL" if pending["is_call"] else "PUT"
    method_text = _activation_method_text(confirm_method, pending["is_call"])
    return (
        f"#{pending['setup_id']} Setup {setup_time} -> Activation {activation_time} · "
        f"启动延迟 {delay_bars}min · {direction} {method_text} {breakout_level:.2f} · "
        f"原始 {pending['sig_id']}"
    )


def _setup_body(sig_def: dict, features: dict, max_wait_bars: int, setup_id: int) -> str:
    return f"#{setup_id} {_v4_signal_body(sig_def, features)} · 候选 setup，等待 {max_wait_bars} 根内启动确认"


def _expired_body(pending: dict, expire_bar: dict, max_wait_bars: int) -> str:
    setup_time = pending["setup_bar"].get("t", f"#{pending['index']}")
    expire_time = expire_bar.get("t", "")
    direction = "CALL" if pending["is_call"] else "PUT"
    requirement_text = _activation_requirement_text(pending.get("activation_confirm_price"), pending["is_call"])
    level = pending.get("last_breakout_level")
    best_close = pending.get("best_close")
    miss_by = pending.get("miss_by")
    level_text = f"{level:.2f}" if level is not None else "--"
    best_text = f"{best_close:.2f}" if best_close is not None else "--"
    miss_text = f"，差 {max(0, miss_by):.2f}" if miss_by is not None else ""
    gate_text = f" · {pending.get('expiry_gate_reason')}" if pending.get("expiry_gate_reason") else ""
    return (
        f"#{pending['setup_id']} Setup {setup_time} -> Expired {expire_time} · "
        f"等待 {max_wait_bars} 根未启动 · {direction} 未形成启动确认：{requirement_text} {level_text}，"
        f"窗口最佳收盘 {best_text}{miss_text}{gate_text} · 原始 {pending['sig_id']}"
    )


def scan_day_declarative(
    bars_1m: list[dict],
    bars_5m: list[dict],
    strategy: dict,
) -> list[dict]:
    """
    v4 declarative 扫描：含 5m 趋势栈检测 + 持仓状态机 + cooldown +
    虚拟 MA50 出场。逻辑与 daily-review.html scanSignalsDeclarative()
    严格 1:1 对齐，确保前后端在同一份策略 JSON 上信号集合一致。
    """
    trends_5m = _detect_trends_routed(bars_5m, strategy)
    trends_1m = map_1m_to_5m_trends(bars_1m, bars_5m, trends_5m)

    sig_defs = strategy.get("signals") or []
    filter_cfg = strategy.get("filter") or {}
    cooldown_cfg = strategy.get("cooldown") or {}
    position_cfg = strategy.get("position_state") or {}
    exit_cfg = strategy.get("exit") or {}
    touch_cfg = strategy.get("touch_logic") or {}
    elite_cfg = strategy.get("elite_strong") or {}
    space_cfg = strategy.get("space_check") or {}
    activation_cfg = strategy.get("entry_activation") or {}

    entangle_lines = filter_cfg.get("entangle_lines") or ["m10", "m20", "m30", "m50"]

    feature_opts = {
        "entangle_ratio": filter_cfg.get("entangle_threshold_ratio", 0.0003) or 0.0003,
        "space_ratio": (
            (space_cfg.get("min_distance_pct_of_price") / 100)
            if space_cfg.get("min_distance_pct_of_price") is not None
            else (filter_cfg.get("space_threshold_ratio") or 0.0015)
        ),
        "touch_lines": touch_cfg.get("trend_touch_levels"),
        "entangle_lines": entangle_lines,
        "space_barriers": space_cfg.get("call_barriers_above") or space_cfg.get("put_barriers_below"),
        "elite_major_lines": elite_cfg.get("major_barriers") or ["m50", "m200", "vw"],
    }

    use_position = position_cfg.get("enabled") is True
    use_cooldown = cooldown_cfg.get("enabled") is True
    cooldown_bars = cooldown_cfg.get("bars", 0) or 0
    use_ma50_exit = bool((exit_cfg.get("L2_hard_stops") or {}).get("ma50_ha_close_break"))
    use_activation = activation_cfg.get("enabled") is True
    activation_max_wait = activation_cfg.get("max_wait_bars", 8) or 8

    annotations: list[dict] = []
    active_pos = 0
    last_signal_bar: int | None = None  # None 等价于 JS 的 -Infinity
    pending_setup: dict | None = None
    setup_seq = 0

    for i in range(1, len(bars_1m)):
        bar = bars_1m[i]
        prev = bars_1m[i - 1]
        if bar.get("m10") is None or prev.get("m10") is None:
            continue

        # 虚拟 MA50 出场（重置 cooldown 允许同 bar 反向）
        if use_ma50_exit and bar.get("m50") is not None:
            hc = bar.get("hC")
            if active_pos == 1 and hc is not None and hc < bar["m50"]:
                active_pos = 0
                last_signal_bar = None
            elif active_pos == -1 and hc is not None and hc > bar["m50"]:
                active_pos = 0
                last_signal_bar = None

        features = compute_bar_features_v4(bar, prev, trends_1m[i], feature_opts)

        if use_activation and pending_setup is not None:
            if (i - pending_setup["index"]) > activation_max_wait:
                annotations.append({
                    "bar_index": i,
                    "type": "expired",
                    "title": f"#{pending_setup['setup_id']} {'CALL' if pending_setup['is_call'] else 'PUT'} setup 过期",
                    "direction": "CALL" if pending_setup["is_call"] else "PUT",
                    "body": _expired_body(pending_setup, bar, activation_max_wait),
                    "style": "purple",
                    "anchor_side": pending_setup["anchor_side"],
                    "_signal_id": pending_setup["sig_id"],
                    "_setup_id": pending_setup["setup_id"],
                    "_setup_time": pending_setup["setup_bar"].get("t", ""),
                    "_setup_title": pending_setup["title"],
                    "_setup_bar_index": pending_setup["index"],
                    "_expire_bar_index": i,
                    "_expire_time": bar.get("t", ""),
                    "_activation_delay_bars": i - pending_setup["index"],
                    "_activation_window_bars": activation_max_wait,
                    "_activation_level": pending_setup.get("last_breakout_level"),
                    "_best_close_in_window": pending_setup.get("best_close"),
                    "_best_wick_in_window": pending_setup.get("best_wick"),
                    "_wick_confirmed_count": pending_setup.get("wick_confirmed_count", 0),
                    "_miss_by": pending_setup.get("miss_by"),
                    "_last_checked_bar_index": pending_setup.get("last_checked_index"),
                    "_last_checked_time": pending_setup.get("last_checked_time"),
                    "_expiry_gate_reason": pending_setup.get("expiry_gate_reason"),
                    "_activation_confirm_price": pending_setup.get("activation_confirm_price"),
                    "_raw_signal_id": pending_setup["sig_id"],
                })
                pending_setup = None
            else:
                probe = _activation_probe(
                    pending_setup, bars_1m, i, features, activation_cfg
                )
                if probe is not None:
                    _update_pending_activation_stats(pending_setup, probe, bar, i)
                if probe is not None and probe["is_activation"]:
                    delay_bars = i - pending_setup["index"]
                    annotations.append({
                        "bar_index": i,
                        "type": "signal",
                        "title": f"#{pending_setup['setup_id']} {pending_setup['title']}",
                        "direction": "CALL" if pending_setup["is_call"] else "PUT",
                        "body": _activation_body(
                            pending_setup, bar, probe["breakout_level"], delay_bars, probe.get("confirm_method")
                        ),
                        "style": pending_setup["style"],
                        "anchor_side": pending_setup["anchor_side"],
                        "score": pending_setup["score"],
                        "_signal_id": pending_setup["sig_id"],
                        "_setup_id": pending_setup["setup_id"],
                        "_setup_time": pending_setup["setup_bar"].get("t", ""),
                        "_setup_title": pending_setup["title"],
                        "_setup_bar_index": pending_setup["index"],
                        "_activation_bar_index": i,
                        "_activation_time": bar.get("t", ""),
                        "_activation_delay_bars": delay_bars,
                        "_activation_breakout_price": probe["breakout_level"],
                        "_activation_confirm_method": probe.get("confirm_method"),
                        "_activation_close_position": probe.get("close_position"),
                        "_activation_window_bars": activation_max_wait,
                        "_activation_confirm_price": pending_setup.get("activation_confirm_price"),
                        "_raw_signal_id": pending_setup["sig_id"],
                    })
                    if use_position:
                        active_pos = 1 if pending_setup["is_call"] else -1
                    last_signal_bar = i
                    pending_setup = None
                    continue
                continue

        if use_position and active_pos != 0:
            continue
        if use_cooldown and last_signal_bar is not None and (i - last_signal_bar) <= cooldown_bars:
            continue

        for sig_def in sig_defs:
            conds = sig_def.get("conditions")
            if not conds:
                continue
            if not matches_declarative_conditions(features, conds):
                continue

            is_call = sig_def.get("direction") == "bullish"
            is_strong = conds.get("previous_elite") is True
            label_el = sig_def.get("label") or {}
            style = _v4_signal_style(sig_def, is_call, is_strong)
            anchor_side = _v4_signal_anchor(sig_def, is_call)
            sig_id = sig_def.get("id")
            title = sig_def.get("name") or label_el.get("text") or sig_id
            score = "10/10" if is_strong else "7/10"

            if use_activation:
                setup_seq += 1
                pending_setup = {
                    "index": i,
                    "setup_bar": bar,
                    "sig_def": sig_def,
                    "is_call": is_call,
                    "sig_id": sig_id,
                    "setup_id": setup_seq,
                    "title": title,
                    "style": style,
                    "anchor_side": anchor_side,
                    "score": score,
                    "activation_confirm_price": activation_cfg.get("confirm_price") or "close",
                }
                annotations.append({
                    "bar_index": i,
                    "type": "setup",
                    "title": f"#{setup_seq} {title} setup",
                    "direction": "CALL" if is_call else "PUT",
                    "body": _setup_body(sig_def, features, activation_max_wait, setup_seq),
                    "style": "blue",
                    "anchor_side": anchor_side,
                    "_signal_id": sig_id,
                    "_setup_id": setup_seq,
                    "_setup_time": bar.get("t", ""),
                    "_setup_title": title,
                    "_setup_bar_index": i,
                    "_activation_window_bars": activation_max_wait,
                    "_activation_window_start_bar_index": i + 1,
                    "_activation_window_end_bar_index": i + activation_max_wait,
                    "_activation_confirm_price": activation_cfg.get("confirm_price") or "close",
                    "_raw_signal_id": sig_id,
                })
                break

            annotations.append({
                "bar_index": i,
                "type": "signal",
                "title": title,
                "direction": "CALL" if is_call else "PUT",
                "body": _v4_signal_body(sig_def, features),
                "style": style,
                "anchor_side": anchor_side,
                "score": score,
                "_signal_id": sig_id,
            })

            if use_position:
                active_pos = 1 if is_call else -1
            last_signal_bar = i
            break  # 单 bar 只匹配第一个信号

    return annotations


def scan_day(
    bars_1m: list[dict],
    bars_5m: list[dict],
    strategy: dict,
) -> list[dict]:
    """
    主循环：遍历 1m bar → 匹配信号 → 生成 annotations。

    路由：v4 declarative 策略走 scan_day_declarative；v1~v3 走老 path。
    """
    if is_strategy_declarative(strategy):
        return scan_day_declarative(bars_1m, bars_5m, strategy)

    # ── v1~v3 path ──
    trends_5m = detect_trends(bars_5m, strategy["trend"])
    trends_1m = map_1m_to_5m_trends(bars_1m, bars_5m, trends_5m)

    filter_cfg = strategy.get("filter", {})
    session = filter_cfg.get("session", {"start": "10:00", "end": "15:45"})
    scoring_cfg = strategy.get("scoring", {"enabled": False})
    hard_blocks_cfg = strategy.get("hard_blocks", {})
    min_score = filter_cfg.get("min_score")

    # 预构建信号定义列表（处理 extends）
    signal_defs = _resolve_extends(strategy["signals"])

    annotations: list[dict] = []

    for i in range(1, len(bars_1m)):
        prev = bars_1m[i - 1]
        curr = bars_1m[i]
        trend = trends_1m[i - 1] if i - 1 < len(trends_1m) else None

        # 时间窗口过滤（用 prev 的时间，因为信号 bar 是 prev）
        if not _time_in_session(prev["t"], session):
            continue

        for sig_def in signal_defs:
            direction = sig_def["direction"]

            # 条件匹配（在 prev bar 上检测形态）
            if not match_conditions(prev, sig_def["conditions"]):
                continue

            # 额外条件 (signal_b 等)
            extra = sig_def.get("extra_conditions")
            if extra and not _match_extra(prev, extra):
                continue

            # 确认条件（curr bar）
            if not match_confirm(curr, sig_def.get("confirm")):
                continue

            # 趋势要求
            trend_req = sig_def.get("trend_required")
            if trend_req and trend != trend_req:
                continue

            # Hard blocks
            blocks = check_hard_blocks(
                prev, trend, direction, filter_cfg, hard_blocks_cfg,
            )
            if blocks:
                continue

            # 评分
            score = compute_score(
                prev, trend, direction, scoring_cfg, filter_cfg,
            )

            # 最低分过滤
            if min_score is not None and scoring_cfg.get("enabled") and score < min_score:
                continue

            # 生成 annotation
            anno = to_annotation(
                bar_index=i,  # 确认 bar（entry bar）的索引
                signal_bar=prev,
                confirm_bar=curr,
                sig_def=sig_def,
                trend=trend,
                score=score if scoring_cfg.get("enabled") else None,
            )
            annotations.append(anno)

    return annotations


def _resolve_extends(signal_defs: list[dict]) -> list[dict]:
    """处理 extends 继承：子信号继承父信号的 conditions。"""
    by_id = {s["id"]: s for s in signal_defs}
    resolved: list[dict] = []

    for s in signal_defs:
        if "extends" in s:
            parent = by_id.get(s["extends"])
            if parent:
                merged = dict(s)
                # 继承父信号的 conditions
                merged["conditions"] = dict(parent.get("conditions", {}))
                # 继承父信号的 confirm
                if "confirm" not in merged and "confirm" in parent:
                    merged["confirm"] = parent["confirm"]
                # 继承 trend_required
                if "trend_required" not in merged and "trend_required" in parent:
                    merged["trend_required"] = parent["trend_required"]
                resolved.append(merged)
            else:
                resolved.append(s)
        else:
            resolved.append(s)

    return resolved


def _match_extra(bar: dict, extra: dict) -> bool:
    """匹配额外条件（signal_b 的 space 等）。"""
    for key, cond in extra.items():
        if isinstance(cond, dict):
            if "field" in cond:
                left = _resolve_value(bar, cond["field"])
                right = _resolve_value(bar, cond["target"])
                if not _compare(left, cond["operator"], right):
                    return False
            elif "fields" in cond:
                for f in cond["fields"]:
                    left = _resolve_value(bar, f)
                    right = _resolve_value(bar, cond["target"])
                    if not _compare(left, cond["operator"], right):
                        return False
            elif "min_distance" in cond:
                # space 检查
                if key == "space_m200":
                    ref = bar.get("m200")
                    price = bar.get("hC", 0)
                    if ref is not None and abs(price - ref) < cond["min_distance"]:
                        return False
                elif key == "space_vw":
                    ref = bar.get("vw")
                    price = bar.get("hC", 0)
                    if ref is not None and abs(price - ref) < cond["min_distance"]:
                        return False
    return True


# ---------------------------------------------------------------------------
# 8. Annotation 格式化
# ---------------------------------------------------------------------------

def to_annotation(
    bar_index: int,
    signal_bar: dict,
    confirm_bar: dict,
    sig_def: dict,
    trend: str | None,
    score: float | None,
) -> dict:
    """信号 → 引擎 annotation 格式。"""
    parts = [sig_def["name"]]
    if trend:
        parts.append(f"5min: {trend}")
    if score is not None:
        parts.append(f"评分: {score:.0f}/10")

    body = " | ".join(parts)

    anno: dict[str, Any] = {
        "bar_index": bar_index,
        "type": "signal",
        "title": sig_def["name"],
        "body": body,
        "style": sig_def.get("style", "red"),
        "anchor_side": sig_def.get("anchor_side", "top"),
    }
    if score is not None:
        anno["score"] = f"{score:.0f}/10"

    return anno


# ---------------------------------------------------------------------------
# 9. 5m 趋势 annotations
# ---------------------------------------------------------------------------

def generate_5m_trend_annotations(
    bars_5m: list[dict],
    trends_5m: list[str | None],
) -> list[dict]:
    """在 5m 趋势切换点生成 annotation。"""
    annos: list[dict] = []
    prev_trend = None
    for j, trend in enumerate(trends_5m):
        if trend != prev_trend and prev_trend is not None and trend is not None:
            annos.append({
                "bar_index": j,
                "type": "signal",
                "title": f"5m: {prev_trend}→{trend}",
                "body": f"5min 趋势转换: {prev_trend} → {trend}",
                "style": "blue",
                "anchor_side": "top",
            })
        prev_trend = trend
    return annos


# ---------------------------------------------------------------------------
# 10. CLI 入口
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="配置驱动的信号扫描器")
    parser.add_argument("--data", required=True, help="processed JSON 路径")
    parser.add_argument("--strategy", required=True, help="策略配置 JSON 路径")
    parser.add_argument("--out", help="输出路径（默认 reviewed/<原文件名>.json）")
    args = parser.parse_args()

    # 加载
    strategy = load_strategy(args.strategy)
    data = load_data(args.data)

    bars_1m = data["bars_1m"]
    bars_5m = data.get("bars_5m", [])

    print(f"策略: {strategy['name']} v{strategy['version']}")
    print(f"数据: {len(bars_1m)} bars (1m), {len(bars_5m)} bars (5m)")

    # 扫描
    annotations_1m = scan_day(bars_1m, bars_5m, strategy)
    official_signals = [a for a in annotations_1m if a.get("type") == "signal"]
    setups = [a for a in annotations_1m if a.get("type") == "setup"]
    expired = [a for a in annotations_1m if a.get("type") == "expired"]
    print(
        f"检测到 {len(official_signals)} 个 1m 正式信号"
        f"（setup {len(setups)}，expired {len(expired)}）"
    )

    # 5m 趋势标注
    trends_5m = detect_trends(bars_5m, strategy["trend"])
    annotations_5m = generate_5m_trend_annotations(bars_5m, trends_5m)
    print(f"检测到 {len(annotations_5m)} 个 5m 趋势转换")

    # 写入
    data["annotations_1m"] = annotations_1m
    data["annotations_5m"] = annotations_5m
    data["meta"]["strategy"] = {
        "name": strategy["name"],
        "version": strategy["version"],
        "description": strategy.get("description", ""),
    }

    if args.out:
        out_path = Path(args.out)
    else:
        src_name = Path(args.data).stem
        out_path = PROJECT_ROOT / "reviewed" / f"{src_name}.json"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"输出: {out_path}")

    # 打印信号摘要
    if annotations_1m:
        print("\n--- 信号摘要 ---")
        for a in annotations_1m:
            t = bars_1m[a["bar_index"]]["t"] if a["bar_index"] < len(bars_1m) else "?"
            kind = a.get("type", "info")
            print(f"  [{t}] {kind}: {a['title']} ({a['style']}) {a.get('score', '')}")


if __name__ == "__main__":
    main()
