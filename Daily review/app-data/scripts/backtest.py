"""
Tang Strategy Backtest v0.3 — SPY Options Scalping
====================================================
v0.2 -> v0.3 changes:
  1. Three-layer exit system:
     L1: Technical exit (MA10 break — existing)
     L2: Hard stops (SPY price / premium % / max hold time)
     L3: Trailing stop (premium high-water mark pullback)
  2. Premium-based P&L tracking during position
  3. New CLI flags: --hard-sl, --prem-sl, --prem-tp, --max-hold, --trail

History:
  v0.1: basic backtest with positional args
  v0.2: argparse, scoring, adaptive exit, batch mode
  v0.3: three-layer exit system (hard stop + trailing stop)
"""

import argparse
import csv
import math
import os
from datetime import datetime, timedelta
from pathlib import Path

# ── Paths ──
def find_project_root() -> Path:
    """Locate the Daily review project root even if scripts are nested."""
    script_dir = Path(__file__).resolve().parent
    for candidate in (script_dir, *script_dir.parents):
        if (candidate / "daily-review.html").exists():
            return candidate
    return script_dir


PROJECT_ROOT = find_project_root()
# Set TANG_DATA_DIR env variable to point at a directory containing raw/bulk/ and raw/daily/.
# Default falls back to a local `data/` subfolder inside this project.
DATA_DIR = Path(os.environ.get("TANG_DATA_DIR", str(PROJECT_ROOT / "data")))
BULK_1MIN = DATA_DIR / "raw" / "bulk" / "SPY_1min_2025-10-01_2026-04-11.csv"
DAILY_DIR = DATA_DIR / "raw" / "daily"

# ── Constants ──
DEFAULT_IV = 0.22
RISK_FREE = 0.045
RTH_MINUTES = 390
TRADING_DAYS_YEAR = 252

PROFILES = {
    "strict":   {"k_quality": 0.50, "entangle": 0.30, "space": 0.50},
    "moderate": {"k_quality": 0.30, "entangle": 0.20, "space": 0.40},
    "loose":    {"k_quality": 0.15, "entangle": 0.12, "space": 0.30},
}

# ══════════════════════════════════════════════════════════════════════
# Black-Scholes (unchanged from v0.1)
# ══════════════════════════════════════════════════════════════════════

def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def bs_price(S, K, T, r, sigma, opt_type):
    if T <= 0:
        return max(S - K, 0) if opt_type == "call" else max(K - S, 0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if opt_type == "call":
        return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)

def bs_delta(S, K, T, r, sigma, opt_type):
    if T <= 0:
        return (1.0 if S > K else 0.0) if opt_type == "call" else (-1.0 if S < K else 0.0)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return norm_cdf(d1) if opt_type == "call" else norm_cdf(d1) - 1

def time_to_close(time_str):
    h, m = map(int, time_str.split(":"))
    return 16 * 60 - (h * 60 + m)

def minutes_to_T(mins_remaining, dte):
    return (mins_remaining + dte * RTH_MINUTES) / (RTH_MINUTES * TRADING_DAYS_YEAR)

def atm_strike(price):
    return round(price)

def estimate_option(spy_price, time_str, opt_type, dte, iv=DEFAULT_IV):
    K = atm_strike(spy_price)
    mins = time_to_close(time_str)
    T = minutes_to_T(mins, dte)
    return {
        "strike": K,
        "premium": bs_price(spy_price, K, T, RISK_FREE, iv, opt_type),
        "delta": bs_delta(spy_price, K, T, RISK_FREE, iv, opt_type),
        "T_min": mins, "iv": iv, "dte": dte,
    }


# ══════════════════════════════════════════════════════════════════════
# Data loading (unchanged from v0.1)
# ══════════════════════════════════════════════════════════════════════

def load_bulk_csv(path, start_date=None):
    rows = []
    with open(path, "r") as f:
        for r in csv.DictReader(f):
            if start_date and r["date"] < start_date:
                continue
            if r["time"] < "09:30" or r["time"] >= "16:00":
                continue
            rows.append({
                "datetime": datetime.strptime(r["timestamp"], "%Y-%m-%d %H:%M:%S"),
                "date": r["date"],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"]),
                "volume": int(float(r["volume"])),
            })
    return rows

def load_daily_csv(path):
    rows = []
    with open(path, "r") as f:
        for r in csv.DictReader(f):
            dt_clean = r["datetime"][:19]
            dt = datetime.strptime(dt_clean, "%Y-%m-%d %H:%M:%S")
            time_str = dt_clean[11:16]
            if time_str < "09:30" or time_str >= "16:00":
                continue
            rows.append({
                "datetime": dt, "date": dt_clean[:10],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"]),
                "volume": int(float(r["volume"])),
            })
    return rows

def load_all_data():
    bulk = load_bulk_csv(BULK_1MIN, start_date="2026-04-07")
    daily = []
    if os.path.isdir(DAILY_DIR):
        for fname in sorted(os.listdir(DAILY_DIR)):
            if fname.startswith("SPY_1min_") and fname.endswith(".csv"):
                daily.extend(load_daily_csv(os.path.join(DAILY_DIR, fname)))
    return sorted(bulk + daily, key=lambda x: x["datetime"])


# ══════════════════════════════════════════════════════════════════════
# Technical indicators (unchanged from v0.1)
# ══════════════════════════════════════════════════════════════════════

def compute_ha(bars):
    ha = []
    prev_o = prev_c = None
    prev_date = None
    for b in bars:
        hc = (b["open"] + b["high"] + b["low"] + b["close"]) / 4
        if prev_date != b["date"] or prev_o is None:
            ho = (b["open"] + b["close"]) / 2
        else:
            ho = (prev_o + prev_c) / 2
        ha.append({**b,
            "ha_open": ho, "ha_close": hc,
            "ha_high": max(b["high"], ho, hc),
            "ha_low": min(b["low"], ho, hc),
            "is_green": hc >= ho, "is_red": hc < ho,
        })
        prev_o, prev_c, prev_date = ho, hc, b["date"]
    return ha

def sma(values, period):
    result = []
    for i in range(len(values)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(values[i - period + 1: i + 1]) / period)
    return result

def vwap_daily(bars):
    vwap = []
    cum_pv = cum_v = 0
    prev_date = None
    for b in bars:
        if b["date"] != prev_date:
            cum_pv = cum_v = 0
            prev_date = b["date"]
        tp = (b["high"] + b["low"] + b["close"]) / 3
        cum_pv += tp * b["volume"]
        cum_v += b["volume"]
        vwap.append(cum_pv / cum_v if cum_v > 0 else None)
    return vwap

def aggregate_5min(bars_1min):
    result = []
    bucket = None
    for b in bars_1min:
        minute = b["datetime"].hour * 60 + b["datetime"].minute
        bm = (minute // 5) * 5
        key = (b["date"], bm)
        if bucket is None or (bucket["date"], bucket["bm"]) != key:
            if bucket:
                result.append(bucket)
            bucket = {
                "datetime": b["datetime"].replace(minute=bm % 60, hour=bm // 60, second=0),
                "date": b["date"], "bm": bm,
                "open": b["open"], "high": b["high"],
                "low": b["low"], "close": b["close"],
                "volume": b["volume"],
            }
        else:
            bucket["high"] = max(bucket["high"], b["high"])
            bucket["low"] = min(bucket["low"], b["low"])
            bucket["close"] = b["close"]
            bucket["volume"] += b["volume"]
    if bucket:
        result.append(bucket)
    return result


# ══════════════════════════════════════════════════════════════════════
# v0.2 NEW: Relaxed 5min trend
# ══════════════════════════════════════════════════════════════════════

def compute_5min_trends(h5, m10_5, m50_5):
    """Relaxed trend: MA10 vs MA50 direction + MA10 slope (3-bar lookback).

    Returns list parallel to h5: "bullish" / "bearish" / None
    """
    trends = []
    for j in range(len(h5)):
        if m10_5[j] is None or m50_5[j] is None:
            trends.append(None)
            continue

        # MA10 slope: rising or falling over last 3 bars
        slope_lb = 3
        if j >= slope_lb and m10_5[j - slope_lb] is not None:
            slope = m10_5[j] - m10_5[j - slope_lb]
        else:
            slope = 0

        if m10_5[j] > m50_5[j] and slope > 0:
            trends.append("bullish")
        elif m10_5[j] < m50_5[j] and slope < 0:
            trends.append("bearish")
        else:
            trends.append(None)

    return trends


# ══════════════════════════════════════════════════════════════════════
# v0.2 NEW: DTE auto-selection
# ══════════════════════════════════════════════════════════════════════

def select_dte(time_str, dte_mode):
    """0DTE morning, 1DTE afternoon. Override with '0' or '1'."""
    if dte_mode in ("0", "1"):
        return int(dte_mode)
    # auto: switch at 14:00
    return 1 if time_str >= "14:00" else 0


# ══════════════════════════════════════════════════════════════════════
# v0.2 NEW: Signal strength scoring
# ══════════════════════════════════════════════════════════════════════

def compute_score(trend, entangle_dist, vwap_ok, space_dist, k_body, k_shadow, params):
    """Score 0-10 from signal quality dimensions."""
    s = 0.0

    # Trend clarity (0-2): bullish/bearish = 1, could add strict 4-line = 2
    s += 2 if trend else 0

    # Entangle distance (0-2): how far from entangle threshold
    ent_margin = entangle_dist - params["entangle"]
    if ent_margin > 0.5:
        s += 2
    elif ent_margin > 0:
        s += 1

    # VWAP alignment (0-1)
    s += 1 if vwap_ok else 0

    # Space (0-2)
    if space_dist > 2.0:
        s += 2
    elif space_dist > params["space"]:
        s += 1

    # K-line quality (0-2)
    total = k_body + k_shadow
    if total > 0:
        ratio = k_body / total
        if ratio > 0.7:
            s += 2
        elif ratio > 0.4:
            s += 1

    # Freshness bonus: omitted for now (needs trend-start tracking)

    return min(s, 10)


def score_to_tp(score, base_tp):
    """Adjust TP bars based on signal score."""
    if base_tp == 0:
        return 0  # TP disabled
    if score >= 7:
        return base_tp + 2
    elif score >= 5:
        return base_tp
    else:
        return max(base_tp - 1, 1)


# ══════════════════════════════════════════════════════════════════════
# v0.2 NEW: Adaptive exit
# ══════════════════════════════════════════════════════════════════════

def evaluate_exit(bar, position, m10, bars_in_trade, favorable_bars,
                  best_spy, tp_target, time_stop_bars,
                  entry_price, entry_opt, exit_params):
    """Three-layer exit system. Returns (should_exit, reason).

    Layer 1 (Technical): TP bars → time-stop → MA10 break
    Layer 2 (Hard stop): SPY price limit, premium % limit, max hold time
    Layer 3 (Trailing):  Premium pullback from high-water mark

    Priority: L2 hard-stop > L3 trailing > L1 TP > L1 time-stop > L1 MA10-stop
    Hard stops fire first because they protect capital regardless of signals.
    """
    price = bar["ha_close"]
    time_str = bar["datetime"].strftime("%H:%M")

    # ── Compute current premium for L2/L3 ──
    opt_type = "put" if position == -1 else "call"
    current_prem = bs_price(
        price, entry_opt["strike"],
        minutes_to_T(time_to_close(time_str), entry_opt["dte"]),
        RISK_FREE, entry_opt["iv"], opt_type,
    )
    prem_ret = (current_prem - entry_opt["premium"]) / entry_opt["premium"] * 100 \
        if entry_opt["premium"] > 0 else 0

    # ── L2: Hard stops (highest priority — capital protection) ──

    # L2a: SPY price hard stop
    hard_sl = exit_params.get("hard_sl", 0)
    if hard_sl > 0:
        if position == -1:
            spy_adverse = price - entry_price
        else:
            spy_adverse = entry_price - price
        if spy_adverse >= hard_sl:
            return True, f"HardSL: SPY {spy_adverse:+.2f}"

    # L2b: Premium % stop-loss
    prem_sl = exit_params.get("prem_sl", 0)
    if prem_sl > 0 and prem_ret <= -prem_sl:
        return True, f"PremSL: {prem_ret:.0f}%"

    # L2c: Premium % take-profit
    prem_tp = exit_params.get("prem_tp", 0)
    if prem_tp > 0 and prem_ret >= prem_tp:
        return True, f"PremTP: +{prem_ret:.0f}%"

    # L2d: Max hold time (minutes = bars for 1min chart)
    max_hold = exit_params.get("max_hold", 0)
    if max_hold > 0 and bars_in_trade >= max_hold:
        return True, f"MaxHold: {bars_in_trade}min"

    # ── L3: Trailing stop (premium high-water mark) ──
    trail_pct = exit_params.get("trail", 0)
    peak_prem = exit_params.get("_peak_prem", entry_opt["premium"])
    if trail_pct > 0 and peak_prem > entry_opt["premium"]:
        # Trailing activates only when we've been in profit
        peak_ret = (peak_prem - entry_opt["premium"]) / entry_opt["premium"] * 100
        drawdown_from_peak = peak_ret - prem_ret
        if drawdown_from_peak >= trail_pct and peak_ret > 10:
            return True, f"Trail: peak+{peak_ret:.0f}% now+{prem_ret:.0f}%"

    # ── L1: Technical exits (signal-based) ──

    # L1a: Take profit — N consecutive favorable bars
    if tp_target > 0 and favorable_bars >= tp_target:
        return True, f"TP: {favorable_bars} bars"

    # L1b: Time stop — no progress after M bars
    if time_stop_bars > 0 and bars_in_trade >= time_stop_bars:
        if position == 1 and bar["ha_high"] <= best_spy:
            return True, f"TimeStop: {bars_in_trade}bars no new high"
        elif position == -1 and bar["ha_low"] >= best_spy:
            return True, f"TimeStop: {bars_in_trade}bars no new low"

    # L1c: MA10 stop (safety net)
    if position == -1:
        if bar["is_green"] and bar["ha_close"] > m10 and bar["ha_open"] > m10:
            return True, "Stop: green K > MA10"
    elif position == 1:
        if bar["is_red"] and bar["ha_close"] < m10 and bar["ha_open"] < m10:
            return True, "Stop: red K < MA10"

    return False, ""


def _classify_exit(reason):
    """Map exit reason string to short category for stats."""
    r = reason.split(":")[0]
    mapping = {
        "TP": "TP", "TimeStop": "TimeStop", "Stop": "MA10Stop",
        "HardSL": "HardSL", "PremSL": "PremSL", "PremTP": "PremTP",
        "MaxHold": "MaxHold", "Trail": "Trail", "EOD": "EOD",
    }
    return mapping.get(r, r)


# ══════════════════════════════════════════════════════════════════════
# Signal detection + trade simulation
# ══════════════════════════════════════════════════════════════════════

def run_day(ha_1min, ma10_1m, ma50_1m, ma200_1m, vwap_1m, trend_5m_at,
            target_date, params, base_tp, time_stop, dte_mode, exit_params):
    """Run backtest for a single date. Returns (events, trades)."""

    MIN_SCORE = 3  # minimum signal score to enter

    n = len(ha_1min)
    events = []
    trades = []
    position = 0
    entry_price = entry_time = entry_reason = entry_opt = None
    bars_in_trade = 0
    favorable_bars = 0
    best_price = 0
    tp_target = base_tp
    peak_prem = 0  # L3: premium high-water mark

    for i in range(1, n):
        bar = ha_1min[i]
        prev = ha_1min[i - 1]
        if bar["date"] != target_date:
            continue

        time_str = bar["datetime"].strftime("%H:%M")
        m10 = ma10_1m[i]
        m50 = ma50_1m[i]
        m200 = ma200_1m[i]
        vw = vwap_1m[i]
        prev_m10 = ma10_1m[i - 1]
        if not all([m10, m50, m200, vw, prev_m10]):
            continue

        price = bar["ha_close"]
        prev_trend = trend_5m_at.get(i - 1)

        # ── Reject / Support MA10 (unchanged) ──
        reject = (prev["is_green"] and prev["ha_high"] >= prev_m10
                  and prev["ha_close"] <= prev_m10 and prev["ha_open"] <= prev_m10)
        support = (prev["is_red"] and prev["ha_low"] <= prev_m10
                   and prev["ha_close"] >= prev_m10 and prev["ha_open"] >= prev_m10)

        signal_put = prev_trend == "bearish" and reject and bar["is_red"]
        signal_call = prev_trend == "bullish" and support and bar["is_green"]

        # ── Metrics for scoring ──
        entangle_dist = abs(m10 - m50)
        dist_ma50 = abs(price - m50)
        dist_ma200 = abs(price - m200)
        dist_vwap = abs(price - vw)
        vwap_ok = (price > vw) if prev_trend == "bullish" else (price < vw) if prev_trend == "bearish" else False

        body = abs(bar["ha_close"] - bar["ha_open"])
        shadow = bar["ha_high"] - bar["ha_low"] - body

        # Signal B
        signal_b = (signal_put and prev["ha_close"] <= m50 and prev["ha_open"] > m50
                    and dist_ma200 > 2.0 and dist_vwap > 1.0)

        # ── Log raw signals ──
        if reject:
            events.append({"time": time_str, "type": "Reject MA10", "price": price,
                           "ma10": prev_m10, "trend": prev_trend, "valid": signal_put, "signal_b": signal_b})
        if support:
            events.append({"time": time_str, "type": "Support MA10", "price": price,
                           "ma10": prev_m10, "trend": prev_trend, "valid": signal_call, "signal_b": False})

        # ── Entry ──
        if position == 0 and time_str >= "10:00" and time_str < "15:45":
            if signal_put or signal_call:
                direction = "bearish" if signal_put else "bullish"
                opt_type = "put" if signal_put else "call"

                # Compute space
                if direction == "bearish":
                    barriers = [d for d in [dist_ma50 if m50 < price else 999,
                                            dist_ma200 if m200 < price else 999,
                                            dist_vwap if vw < price else 999] if d < 999]
                else:
                    barriers = [d for d in [dist_ma50 if m50 > price else 999,
                                            dist_ma200 if m200 > price else 999,
                                            dist_vwap if vw > price else 999] if d < 999]
                space_dist = min(barriers) if barriers else 999

                # Score
                score = compute_score(prev_trend, entangle_dist, vwap_ok,
                                      space_dist, body, shadow, params)

                # Hard blocks (even score can't override)
                blocked = []
                if not prev_trend or prev_trend != direction:
                    blocked.append("no_trend")
                if entangle_dist < params["entangle"]:
                    blocked.append("entangle")
                if space_dist < params["space"]:
                    blocked.append("no_space")

                if blocked:
                    events.append({"time": time_str, "type": "BLOCKED", "direction": opt_type.upper(),
                                   "spy": price, "fail": blocked, "score": score})
                elif score < MIN_SCORE:
                    events.append({"time": time_str, "type": "BLOCKED", "direction": opt_type.upper(),
                                   "spy": price, "fail": [f"low_score({score:.0f})"], "score": score})
                else:
                    # ENTER
                    dte = select_dte(time_str, dte_mode)
                    tp_target = score_to_tp(score, base_tp)

                    position = -1 if signal_put else 1
                    entry_price = price
                    entry_time = time_str
                    entry_reason = "Signal B" if signal_b else "Signal A"
                    entry_opt = estimate_option(price, time_str, opt_type, dte)
                    bars_in_trade = 0
                    favorable_bars = 0
                    best_price = bar["ha_low"] if position == -1 else bar["ha_high"]
                    peak_prem = entry_opt["premium"]

                    events.append({"time": time_str, "type": "ENTRY",
                                   "direction": opt_type.upper(), "spy": price,
                                   "reason": entry_reason, "score": score,
                                   "dte": dte, "tp_target": tp_target,
                                   "opt": entry_opt})

        # ── Exit (three-layer system) ──
        if position != 0:
            bars_in_trade += 1

            # Track best SPY price
            if position == 1:
                best_price = max(best_price, bar["ha_high"])
                is_favorable = bar["is_green"]
            else:
                best_price = min(best_price, bar["ha_low"])
                is_favorable = bar["is_red"]

            if is_favorable:
                favorable_bars += 1
            else:
                favorable_bars = 0

            # Track premium high-water mark (L3)
            opt_type_cur = "put" if position == -1 else "call"
            cur_prem = bs_price(
                price, entry_opt["strike"],
                minutes_to_T(time_to_close(time_str), entry_opt["dte"]),
                RISK_FREE, entry_opt["iv"], opt_type_cur,
            )
            peak_prem = max(peak_prem, cur_prem)

            # Pass peak_prem into exit_params for L3
            ep = {**exit_params, "_peak_prem": peak_prem}

            should_exit, reason = evaluate_exit(
                bar, position, m10, bars_in_trade, favorable_bars,
                best_price, tp_target, time_stop,
                entry_price, entry_opt, ep)

            if should_exit:
                d = "PUT" if position == -1 else "CALL"
                opt_type = "put" if position == -1 else "call"
                exit_prem = bs_price(price, entry_opt["strike"],
                                     minutes_to_T(time_to_close(time_str), entry_opt["dte"]),
                                     RISK_FREE, entry_opt["iv"], opt_type)
                spy_move = (entry_price - price) if d == "PUT" else (price - entry_price)
                opt_pnl = exit_prem - entry_opt["premium"]
                opt_ret = opt_pnl / entry_opt["premium"] * 100 if entry_opt["premium"] > 0 else 0

                trades.append({
                    "entry_time": entry_time, "exit_time": time_str,
                    "direction": d, "entry_spy": entry_price, "exit_spy": price,
                    "spy_move": spy_move, "reason_in": entry_reason, "reason_out": reason,
                    "strike": entry_opt["strike"],
                    "entry_premium": entry_opt["premium"], "exit_premium": exit_prem,
                    "entry_delta": entry_opt["delta"],
                    "opt_pnl": opt_pnl, "opt_ret": opt_ret,
                    "bars_held": bars_in_trade, "dte": entry_opt["dte"],
                    "score": events[-1].get("score", 0) if events else 0,
                    "exit_type": _classify_exit(reason),
                    "peak_prem": peak_prem,
                })
                events.append({"time": time_str, "type": "EXIT", "direction": d,
                               "spy": price, "reason": reason, "opt_ret": opt_ret})
                position = 0

    # EOD close
    if position != 0:
        last_bars = [b for b in ha_1min if b["date"] == target_date]
        if last_bars:
            last = last_bars[-1]
            d = "PUT" if position == -1 else "CALL"
            opt_type = d.lower()
            t_str = last["datetime"].strftime("%H:%M")
            p = last["ha_close"]
            exit_prem = bs_price(p, entry_opt["strike"],
                                 minutes_to_T(time_to_close(t_str), entry_opt["dte"]),
                                 RISK_FREE, entry_opt["iv"], opt_type)
            spy_move = (entry_price - p) if d == "PUT" else (p - entry_price)
            opt_pnl = exit_prem - entry_opt["premium"]
            opt_ret = opt_pnl / entry_opt["premium"] * 100 if entry_opt["premium"] > 0 else 0
            trades.append({
                "entry_time": entry_time, "exit_time": t_str,
                "direction": d, "entry_spy": entry_price, "exit_spy": p,
                "spy_move": spy_move, "reason_in": entry_reason, "reason_out": "EOD",
                "strike": entry_opt["strike"],
                "entry_premium": entry_opt["premium"], "exit_premium": exit_prem,
                "entry_delta": entry_opt["delta"],
                "opt_pnl": opt_pnl, "opt_ret": opt_ret,
                "bars_held": bars_in_trade, "dte": entry_opt["dte"],
                "score": 0, "exit_type": "EOD", "peak_prem": peak_prem,
            })

    return events, trades


# ══════════════════════════════════════════════════════════════════════
# Reporting
# ══════════════════════════════════════════════════════════════════════

def print_day_report(target_date, ha, m10, m50, m200, vw, trend_map, events, trades, args):
    """Print single-day report (same structure as v0.1 + new fields)."""

    params = PROFILES[args.profile]
    print("=" * 76)
    print(f"  Tang v0.2 Backtest -- SPY {target_date}")
    print(f"  Profile: {args.profile}  TP={args.tp}  TimeStop={args.time_stop}  DTE={args.dte}")
    exit_parts = []
    if args.hard_sl > 0:
        exit_parts.append(f"HardSL={args.hard_sl}")
    if args.prem_sl > 0:
        exit_parts.append(f"PremSL=-{args.prem_sl}%")
    if args.prem_tp > 0:
        exit_parts.append(f"PremTP=+{args.prem_tp}%")
    if args.max_hold > 0:
        exit_parts.append(f"MaxHold={args.max_hold}min")
    if args.trail > 0:
        exit_parts.append(f"Trail={args.trail}%")
    exit_desc = "  ".join(exit_parts) if exit_parts else "none"
    print(f"  L2/L3 exits: {exit_desc}  |  IV: {DEFAULT_IV*100:.0f}%")
    print("=" * 76)

    # Market overview
    day = [b for b in ha if b["date"] == target_date]
    if day:
        o, c = day[0]["ha_open"], day[-1]["ha_close"]
        h_val = max(b["ha_high"] for b in day)
        l_val = min(b["ha_low"] for b in day)
        print(f"\n  Open: {o:.2f}  Close: {c:.2f}  High: {h_val:.2f}  Low: {l_val:.2f}")
        print(f"  Day move: {c - o:+.2f} ({(c-o)/o*100:+.2f}%)")

    # Key snapshots
    print(f"\n  {'Time':>5}  {'Price':>7}  {'MA10':>7}  {'MA50':>7}  {'MA200':>7}  {'VWAP':>7}  5min")
    for snap in ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"]:
        for i, b in enumerate(ha):
            if b["date"] == target_date and b["datetime"].strftime("%H:%M") == snap:
                if all([m10[i], m50[i], m200[i], vw[i]]):
                    tr = trend_map.get(i, "-")
                    print(f"  {snap:>5}  {b['ha_close']:>7.2f}  {m10[i]:>7.2f}  {m50[i]:>7.2f}  {m200[i]:>7.2f}  {vw[i]:>7.2f}  {tr}")
                break

    # Signals
    sigs = [e for e in events if e["type"] in ("Reject MA10", "Support MA10")]
    valid = [e for e in sigs if e["valid"]]
    print(f"\n  Signals: {len(sigs)} raw | {len(valid)} valid (trend aligned)")
    for e in sigs:
        mark = " >>>" if e["valid"] else "    "
        sb = " [B!]" if e.get("signal_b") else ""
        tr = e['trend'] or '-'
        print(f"  {mark} [{e['time']}] {e['type']:<15} SPY={e['price']:.2f}  MA10={e['ma10']:.2f}  5m={tr}{sb}")

    # Entry checks
    checks = [e for e in events if e["type"] in ("ENTRY", "BLOCKED")]
    if checks:
        print(f"\n  Entry decisions:")
        for e in checks:
            sc = e.get('score', '?')
            if e["type"] == "ENTRY":
                tp_t = e.get('tp_target', '?')
                dte_v = e.get('dte', '?')
                print(f"    [{e['time']}] {e['direction']} @ {e['spy']:.2f}  ENTERED  score={sc:.0f}  dte={dte_v}DTE  tp={tp_t}")
            else:
                print(f"    [{e['time']}] {e['direction']} @ {e['spy']:.2f}  BLOCKED: {', '.join(e['fail'])}  score={sc:.0f}")

    # Trades
    print(f"\n{'='*76}")
    print(f"  TRADES")
    print(f"{'='*76}")

    if not trades:
        print("\n  No trades taken.")
    else:
        for j, t in enumerate(trades):
            hold_min = t.get("bars_held", 0)
            print(f"""
  #{j+1}  {t['direction']}  {t['entry_time']}->{t['exit_time']} ({hold_min}bars)  {t.get('dte',0)}DTE
     SPY {t['entry_spy']:.2f} -> {t['exit_spy']:.2f} ({t['spy_move']:+.2f})
     K={t['strike']}  Prem ${t['entry_premium']:.2f} -> ${t['exit_premium']:.2f}  Delta={t['entry_delta']:.3f}
     Opt P&L: ${t['opt_pnl']:+.2f} ({t['opt_ret']:+.1f}%)
     In: {t['reason_in']}  Out: {t['reason_out']}""")

    # Summary
    return print_summary(trades)


EXIT_TYPES = ["TP", "TimeStop", "MA10Stop", "HardSL", "PremSL", "PremTP", "MaxHold", "Trail", "EOD"]


def _exit_counts(trades):
    """Count exits by type."""
    return {et: sum(1 for t in trades if t["exit_type"] == et) for et in EXIT_TYPES}


def print_summary(trades):
    """Print summary and return stats dict."""
    if not trades:
        print("\n  No trades.")
        return {"trades": 0, "wins": 0, "total_ret": 0, **{f"{et}_exits": 0 for et in EXIT_TYPES}}

    wins = [t for t in trades if t["opt_ret"] > 0]
    losses = [t for t in trades if t["opt_ret"] <= 0]
    total_ret = sum(t["opt_ret"] for t in trades)
    ec = _exit_counts(trades)

    print(f"\n{'-'*76}")
    print(f"  SUMMARY")
    print(f"{'-'*76}")
    print(f"  Trades: {len(trades)}  Win: {len(wins)}/{len(trades)} ({len(wins)/len(trades)*100:.0f}%)")
    if wins:
        print(f"  Avg win:  +{sum(t['opt_ret'] for t in wins)/len(wins):.1f}%")
    if losses:
        print(f"  Avg loss: {sum(t['opt_ret'] for t in losses)/len(losses):.1f}%")
    print(f"  Total return: {total_ret:+.1f}%")

    # Exit breakdown — only show types that fired
    active = {k: v for k, v in ec.items() if v > 0}
    parts = [f"{k}={v}" for k, v in active.items()]
    print(f"  Exits: {' '.join(parts)}")

    print(f"\n  $100/trade:")
    for j, t in enumerate(trades):
        print(f"    #{j+1}: ${100 * t['opt_ret']/100:+.2f}  [{t['exit_type']}]")
    net = sum(100 * t['opt_ret']/100 for t in trades)
    print(f"    Net: ${net:+.2f} on ${100 * len(trades)} deployed")

    return {"trades": len(trades), "wins": len(wins), "total_ret": total_ret,
            **{f"{et}_exits": ec[et] for et in EXIT_TYPES}}


def print_batch_summary(day_results):
    """Print batch summary table across multiple days."""
    # Find which exit types actually fired
    all_stats = [s for _, s in day_results]
    active_exits = [et for et in EXIT_TYPES
                    if any(s.get(f"{et}_exits", 0) > 0 for s in all_stats)]

    header_exits = " ".join(f"{et:>6}" for et in active_exits)
    print("\n" + "=" * 90)
    print("  BATCH SUMMARY")
    print("=" * 90)
    print(f"  {'Date':<12} {'Trades':>6} {'Win%':>6} {'Return':>8} {header_exits}")
    print(f"  {'-'*12} {'-'*6} {'-'*6} {'-'*8} {' '.join('-'*6 for _ in active_exits)}")

    total_trades = total_wins = 0
    total_ret = 0

    for date, stats in day_results:
        n = stats["trades"]
        w = stats["wins"]
        wr = f"{w/n*100:.0f}%" if n > 0 else "-"
        ret = stats["total_ret"]
        exit_cols = " ".join(f"{stats.get(f'{et}_exits', 0):>6}" for et in active_exits)
        print(f"  {date:<12} {n:>6} {wr:>6} {ret:>+7.1f}% {exit_cols}")
        total_trades += n
        total_wins += w
        total_ret += ret

    print(f"  {'-'*12} {'-'*6} {'-'*6} {'-'*8}")
    wr_total = f"{total_wins/total_trades*100:.0f}%" if total_trades > 0 else "-"
    print(f"  {'TOTAL':<12} {total_trades:>6} {wr_total:>6} {total_ret:>+7.1f}%")


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser(description="Tang Strategy v0.3 Backtest (Options Scalping)")
    p.add_argument("dates", nargs="*", default=["2026-04-14"],
                   help="Date(s) to backtest, e.g. 2026-04-13 2026-04-14")
    p.add_argument("--profile", default="loose", choices=["strict", "moderate", "loose"])
    p.add_argument("--dte", default="auto", help="0, 1, or auto (default)")
    p.add_argument("--tp", type=int, default=2, help="TP bars, 0=disabled (default: 2)")
    p.add_argument("--time-stop", type=int, default=5, help="Time stop bars, 0=disabled (default: 5)")
    p.add_argument("--batch", action="store_true", help="Show batch summary table")

    # v0.3: Layer 2 — hard stops
    g2 = p.add_argument_group("L2: Hard stops")
    g2.add_argument("--hard-sl", type=float, default=0,
                    help="SPY adverse move hard stop, e.g. 0.50 (default: 0=off)")
    g2.add_argument("--prem-sl", type=float, default=0,
                    help="Premium %% stop-loss, e.g. 50 = exit at -50%% (default: 0=off)")
    g2.add_argument("--prem-tp", type=float, default=0,
                    help="Premium %% take-profit, e.g. 80 = exit at +80%% (default: 0=off)")
    g2.add_argument("--max-hold", type=int, default=0,
                    help="Max hold time in minutes/bars (default: 0=off)")

    # v0.3: Layer 3 — trailing stop
    g3 = p.add_argument_group("L3: Trailing stop")
    g3.add_argument("--trail", type=float, default=0,
                    help="Trailing stop: exit when premium drops N%% from peak (default: 0=off)")
    return p.parse_args()


def main():
    args = parse_args()
    params = PROFILES[args.profile]

    # Load data once
    all_1m = load_all_data()

    # Compute indicators once
    ha = compute_ha(all_1m)
    hc = [b["ha_close"] for b in ha]
    m10 = sma(hc, 10)
    m50 = sma(hc, 50)
    m200 = sma(hc, 200)
    vw = vwap_daily(all_1m)

    b5 = aggregate_5min(all_1m)
    h5 = compute_ha(b5)
    hc5 = [b["ha_close"] for b in h5]
    m10_5 = sma(hc5, 10)
    m50_5 = sma(hc5, 50)

    # v0.2: relaxed 5min trend
    trends_5 = compute_5min_trends(h5, m10_5, m50_5)

    # Map 5min trend to 1min indices
    trend_map = {}
    for j, bar5 in enumerate(h5):
        t5s = bar5["datetime"]
        t5e = t5s + timedelta(minutes=5)
        for i, b1 in enumerate(ha):
            if b1["datetime"] >= t5s and b1["datetime"] < t5e:
                trend_map[i] = trends_5[j]

    # Available dates in data
    available = sorted(set(b["date"] for b in all_1m))

    # Resolve requested dates
    dates = [d for d in args.dates if d in available]
    if not dates:
        print(f"  No data for requested dates. Available: {', '.join(available[-10:])}")
        return

    # Build exit params dict for L2/L3
    exit_params = {
        "hard_sl": args.hard_sl,
        "prem_sl": args.prem_sl,
        "prem_tp": args.prem_tp,
        "max_hold": args.max_hold,
        "trail": args.trail,
    }

    # Run each date
    day_results = []
    for target_date in dates:
        events, trades = run_day(ha, m10, m50, m200, vw, trend_map,
                                 target_date, params, args.tp, args.time_stop,
                                 args.dte, exit_params)

        if not args.batch or len(dates) == 1:
            stats = print_day_report(target_date, ha, m10, m50, m200, vw,
                                     trend_map, events, trades, args)
        else:
            # Batch: just collect stats
            wins = [t for t in trades if t["opt_ret"] > 0]
            ec = _exit_counts(trades)
            stats = {"trades": len(trades), "wins": len(wins),
                     "total_ret": sum(t["opt_ret"] for t in trades),
                     **{f"{et}_exits": ec[et] for et in EXIT_TYPES}}

        day_results.append((target_date, stats))

    # Batch summary
    if args.batch and len(dates) > 1:
        print_batch_summary(day_results)


if __name__ == "__main__":
    main()
