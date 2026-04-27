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
    """检查时间是否在交易窗口内。"""
    start = session.get("start", "10:00")
    end = session.get("end", "15:45")
    return start <= t <= end


def scan_day(
    bars_1m: list[dict],
    bars_5m: list[dict],
    strategy: dict,
) -> list[dict]:
    """主循环：遍历 1m bar → 匹配信号 → 生成 annotations。"""
    # 检测 5m 趋势
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
    print(f"检测到 {len(annotations_1m)} 个 1m 信号")

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
            print(f"  [{t}] {a['title']} ({a['style']}) {a.get('score', '')}")


if __name__ == "__main__":
    main()
