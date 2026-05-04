# Daily Review

Daily Review is a local SPY intraday review tool for Tang Strategy. It helps load market data, visualize 1m / 5m candles, review strategy signals, and keep strategy versions as JSON files.

This project is designed for local use first: open the HTML file, load data, choose a strategy, and review the day.

## What It Does

- Shows 1m and 5m SPY candles with moving averages, VWAP, volume, and annotations.
- Supports Heikin-Ashi and regular OHLC views.
- Loads raw market JSON from `market-data/live/YYYY-MM-DD/`.
- Loads reviewed JSON with precomputed annotations from `reviewed/`.
- Loads strategy definitions from `strategies/json/tang_*.json`. v1 / v2 / v3 / **v4.4 Slope** / **v4.4 Activation** / **v4.4 Activation Wick** are inlined as preset options in the dropdown — no upload needed.
- Browser-side scanner runs strategy logic directly: v1~v3 use the legacy
  Reject/Support/SignalB detectors; **v4.4 (and any future declarative
  strategy) is driven by the `signals[].conditions` dict** — see
  [INTEGRATION.md](INTEGRATION.md) §13 for the routing rule.
- **Click any signal card to expand a full triggers checklist** with every
  condition the strategy declared, evaluated against the bar with concrete
  numbers — e.g. `✓ 1m MA10 向上 — 前根 713.22 → 当前 713.25` /
  `✓ 前根触碰均线 — HA[712.98, 713.65] 跨过 MA10=713.22`. The expanded panel
  also shows the invalidation rule (with the actual MA50 value at signal
  time) and the signal's MFE / MAE during its active window.
- Generates a self-contained "shareable" HTML snapshot via
  `app-data/scripts/build_reviewed_html.py` — embeds the day's data + strategy
  into a single file you can double-click anywhere.
- Provides Python scripts for signal scanning and options-style backtesting.

## What It Does NOT Do

This is a *review* tool, not a backtester or paper-trading system.

- **No take-profit logic.** Profit-taking depends on personality, sizing,
  intraday context — humans decide. Daily Review never claims to know "this
  was a winner." It traces each signal until the strategy's own
  invalidation rule fires (or EOD), then reports MFE / MAE / duration as
  data, not promises.
- **No win/loss / win-rate stats.** Win-rate would assume a fixed exit point
  the tool doesn't have. Stats use **MFE 中位 / 时长中位 / MAE 中位** instead.
- **No simulated trailing stops, time stops, or premium-percent stops.**
  Whatever the strategy JSON declares (`exit.L2_hard_stops.ma50_ha_close_break`
  for v4.4, `ma_stop_line` body-cross for v3) is the only invalidation logic.

## Tang v4.4 Activation

`Tang v4.4 Activation` is an additive derivative of `Tang v4.4 Slope`.
The original `strategies/json/tang_v4_4_slope.json` is the baseline and should not
be deleted, edited, or overwritten for this experiment.

Use Activation when reviewing whether a v4.4 setup was actually executable:

- `setup`: the original v4.4 match. It is shown as a blue candidate marker and
  is not counted as an official signal.
- `signal`: the activation bar. Within 8 x 1m bars after setup, regular close
  must break the running range from setup through the previous bar, while HA
  color and MA10 slope still align with the direction.
- `expired`: no activation within 8 x 1m bars. It is shown as a purple marker
  and is not counted in long/short signal stats.
- Position state and cooldown start only after activation. A setup does not
  lock position state and does not trigger cooldown.

`Tang v4.4 Activation Wick` is a second derivative for the “will strict close
confirmation miss a fast move?” scenario. It keeps the same setup window and
trend gates, but `entry_activation.confirm_price = "close_or_strong_wick"`:

- CALL can activate on either regular close breaking the running high, or wick
  piercing that line while the candle closes in the upper 40% of its range
  (`strong_wick.close_position_min = 0.6`).
- PUT can activate on either regular close breaking the running low, or wick
  piercing that line while the candle closes in the lower 40% of its range.
- HA color and MA10 slope still must align. This is looser than strict
  Activation, but still avoids pure upper/lower shadow traps.

CLI scan example:

```powershell
python "app-data/scripts/scan_signals.py" `
  --data "market-data/live/2026-04-24/SPY_2026-04-24.json" `
  --strategy "strategies/json/tang_v4_4_activation.json" `
  --out "reviewed/SPY_2026-04-24.tang_v4_4_activation.json"
```

Wick variant:

```powershell
python "app-data/scripts/scan_signals.py" `
  --data "market-data/live/2026-04-24/SPY_2026-04-24.json" `
  --strategy "strategies/json/tang_v4_4_activation_wick.json" `
  --out "reviewed/SPY_2026-04-24.tang_v4_4_activation_wick.json"
```

## 获取行情数据

> **2026-04-29 更新（Extended Hours 切换）**：`market-data/live/` 现在统一使用 **extended hours JSON**（meta.session_mode = `extended`，1m bars 04:00–19:59 ET）。`daily-review.html` 在 `loadData()` 入口对 extended JSON 自动切到 RTH (09:30–15:59) 显示，但每根 RTH bar 的 m10/m50/... 是用**含盘前/盘后的连续序列**算出来的，所以开盘均线不再像以前 RTH-only 数据那样偏离 moomoo 几个点。
>
> RTH-only 旧文件备份在 `market-data/live_rth_backup/`（同结构、144 个日期）。如果新数据出问题可以一键回退。

工具支持任意股票和 ETF，不限于 SPY。**数据源按优先级**：

| 优先级 | 数据源 | 用途 | 说明 |
|---|---|---|---|
| ⭐ 首选 | **IBKR Gateway**（Pro 账号）| 当日 + 历史 | SIP/NMS feed，与 moomoo 同源；MA 对齐到 0.001 点 |
| 备用 | **Polygon.io** | 历史回填 / IBKR 没装时 | 真实 SIP feed，free tier 24-72h 延迟 |
| 兜底 | yfinance | **不再推荐** | 盘前/盘后 vol=0，VWAP 不可信 |

> ⚠️ **不要再下 RTH-only CSV**：均线必须用连续 04:00–19:59 序列算才能对得上 moomoo。
> 旧 RTH 数据视为 legacy，用于历史对照，不要再喂入 Daily Review。

### IBKR Gateway（⭐ 首选）

前置：装 IB Gateway → Live 登录 → 配置→设置→API→设置：
- ✅ Enable ActiveX and Socket Clients
- ⬜ **不**勾 Read-Only API（否则 `Error 321`）
- Trusted IPs 加 `127.0.0.1`
- 端口 4001（Live）/ 4002（Paper）

```bash
python -m pip install ib_insync

# 单日（一日 ~5 秒）
python "../Dream bigger/scripts/v0.6/tasks/task0_fetch_ibkr.py" --start 2026-04-28 --end 2026-04-28

# 日期范围（11s/请求 pacing，10 天约 2 分钟）
python "../Dream bigger/scripts/v0.6/tasks/task0_fetch_ibkr.py" --start 2026-04-13 --end 2026-04-28
```

输出 → `Dream bigger/data/raw/daily_extended/SPY_1min_<date>.csv`，列对齐 Polygon bulk 标准。

### Polygon.io（备用）

```bash
# 单日 curl：
curl "https://api.polygon.io/v2/aggs/ticker/SPY/range/1/minute/2026-04-13/2026-04-13\
?apiKey=YOUR_KEY&adjusted=true&sort=asc&limit=50000"

# 批量带断点续跑：
POLYGON_API_KEY=... python "../Dream bigger/scripts/v0.6/tasks/task0_fetch.py" \
  --start 2025-10-01 --end 2026-04-11
```

> Free tier 对**最近 1-2 天**数据可能 403（`Your plan doesn't include this data timeframe`）—— 这种情况用 IBKR。

### yfinance（兜底，仅应急）

```python
import yfinance as yf
df = yf.Ticker("SPY").history(period="1d", interval="1m", prepost=True, auto_adjust=True)
# 警告：SPY 盘前/盘后 volume=0（quote 中点价格），VWAP 不可信
# 只在 IBKR + Polygon 都不可用时使用
```

### 下载后必须执行（数据 → JSON → live/）

完整流水线（IBKR 首选）：

```powershell
# 1. 拉 CSV（IBKR Gateway 必须开着）
python "..\Dream bigger\scripts\v0.6\tasks\task0_fetch_ibkr.py" --start 2026-04-28 --end 2026-04-28
# CSV 落 → Dream bigger\data\raw\daily_extended\SPY_1min_2026-04-28.csv

# 2. CSV → JSON（带跨日 warmup，session=extended）
cd "..\Dream bigger\data"
python build_json.py raw/daily_extended/SPY_1min_2026-04-28.csv --auto-warmup --session extended
# JSON 落 → processed_extended\SPY_2026-04-28.json

# 3. 复制到 live/（Daily Review 读这里）
mkdir "..\..\Daily review\market-data\live\2026-04-28" -Force
copy processed_extended\SPY_2026-04-28.json "..\..\Daily review\market-data\live\2026-04-28\SPY_2026-04-28.json"

# 4. （可选）跨日审计
python audit_sessions.py
# 报告 → reports\extended_backfill_<YYYYMMDD>.csv
```

> ⚠️ **`--session extended` 不能省略**！默认是 `rth`，会落到 `processed/`（旧 RTH-only 路径），Daily Review 虽然能读但**开盘均线会偏离 moomoo 几个点** —— 这就是这次迁移要修的问题。

详细用法见 `Dream bigger/data/README.md`。

---

## Quick Start

Open the app directly:

```powershell
Start-Process ".\daily-review.html"
```

Then use the page controls to load:

- Market data: `market-data/live/YYYY-MM-DD/SPY_YYYY-MM-DD.json`
- Strategy JSON: `strategies/json/tang_v*.json`
- Reviewed data: `reviewed/*.json`

No build step is required.

## Project Layout

```text
Daily review/
  daily-review.html                 # Main static app
  README.md                         # Project overview
  INTEGRATION.md                    # Developer / agent handoff notes
  HANDOFF_v4_4_scanner.md           # V4.4 scanner upgrade handoff (delivered)
  app-data/scripts/
    scan_signals.py                 # Market JSON + strategy JSON -> reviewed JSON
    backtest.py                     # SPY options scalping backtest
    build_reviewed_html.py          # Inline data + strategy into a self-contained HTML
  market-data/live/YYYY-MM-DD/
    SPY_YYYY-MM-DD.json             # Market data
  reviewed/
    *.json                          # Reviewed data with annotations
    SPY_YYYY-MM-DD_review.html      # Self-contained shareable snapshots
  strategies/
    STRATEGY.md                     # Human-readable Tang Strategy spec
    strategy.schema.json            # JSON Schema for strategy files
    tang_v*.json                    # Versioned strategy definitions
    tang_v4_4_activation.json       # v4.4 Slope derivative: setup -> activation confirmation
    tang_v4_4_activation_wick.json  # Activation variant: close breakout or strong wick confirmation
    tang_*.pine                     # PineScript references
```

## Strategy JSON

All strategy versions should live in `strategies/` and follow `strategy.schema.json`.

Validate strategy files with:

```powershell
npx --yes ajv-cli@5 validate --spec=draft2020 `
  -s "strategies/strategy.schema.json" `
  -d "strategies/json/tang_v*.json"
```

Recommended strategy file header:

```json
{
  "$schema": "./strategy.schema.json",
  "name": "Tang vX",
  "version": "X.Y",
  "description": "What changed in this version"
}
```

## Generate Reviewed Data

```powershell
python "app-data/scripts/scan_signals.py" `
  --data "market-data/live/2026-04-22/SPY_2026-04-22.json" `
  --strategy "strategies/json/tang_v3_5_1_full.json" `
  --out "reviewed/SPY_2026-04-22.tang_v3_5_1_full.json"
```

## Generate Shareable HTML Snapshot

For a single-file HTML you can open offline (double-click, no HTTP server),
inline the day's market JSON + strategy into `daily-review.html`:

```powershell
python "app-data/scripts/build_reviewed_html.py" `
  --date 2026-04-27 `
  --strategy "strategies/json/tang_v4_4_slope.json"
# → reviewed/SPY_2026-04-27_review.html
```

The script reads `daily-review.html`, injects
`window.__EMBEDDED_DATA__ / __EMBEDDED_STRATEGY__ / __EMBEDDED_DATE__`
and patches `init()` to consume them. Strategy is optional; if omitted, the
viewer falls back to its dropdown default (currently `tang_v3`).

To generate a shareable review with the activation-gated v4.4 derivative, pass
the derived strategy explicitly:

```powershell
python "app-data/scripts/build_reviewed_html.py" `
  --date 2026-04-24 `
  --strategy "strategies/json/tang_v4_4_activation.json"
```

Use the Wick variant explicitly when you want close breakout or strong-wick
activation:

```powershell
python "app-data/scripts/build_reviewed_html.py" `
  --date 2026-04-24 `
  --strategy "strategies/json/tang_v4_4_activation_wick.json"
```

## Backtest

```powershell
python "app-data/scripts/backtest.py" 2026-04-14 --profile loose
```

For external raw CSV data, set:

```powershell
$env:TANG_DATA_DIR = "path\to\data"
```

## Notes For Development

Read `INTEGRATION.md` before changing behavior. It documents the data contract, strategy boundaries, validation checklist, and the parts of `daily-review.html` that should not be broken when updating the chart engine.
