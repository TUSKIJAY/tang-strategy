# Daily Review

Daily Review is a local SPY intraday review tool for Tang Strategy. It helps load market data, visualize 1m / 5m candles, review strategy signals, and keep strategy versions as JSON files.

This project is designed for local use first: open the HTML file, load data, choose a strategy, and review the day.

## What It Does

- Shows 1m and 5m SPY candles with moving averages, VWAP, volume, and annotations.
- Supports Heikin-Ashi and regular OHLC views.
- Loads raw market JSON from `market-data/live/YYYY-MM-DD/`.
- Loads reviewed JSON with precomputed annotations from `reviewed/`.
- Loads strategy definitions from `strategies/tang_*.json`. v1 / v2 / v3 / **v4.4 Slope** are inlined as preset options in the dropdown — no upload needed.
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

## 获取行情数据

工具支持任意股票和 ETF，不限于 SPY。根据所需历史深度选择数据源：

| 场景 | 数据源 | 说明 |
|------|--------|------|
| 近 **7 天内** | **yfinance**（免费） | 直接拉，无需 API Key |
| **7 天以上** 历史 | **Polygon.io** | 需 API Key（见 CLAUDE.md） |

### yfinance（≤ 7 天）

```python
import yfinance as yf

ticker = "SPY"          # 换成任意 ticker：NVDA、AAPL、QQQ …
df = yf.Ticker(ticker).history(period="1d", interval="1m")
df.to_csv(f"SPY_1min_2026-04-27.csv")
```

### Polygon.io（> 7 天）

```bash
curl "https://api.polygon.io/v2/aggs/ticker/SPY/range/1/minute/2026-04-01/2026-04-27\
?apiKey=YOUR_KEY&limit=50000&sort=asc"
# 把 URL 里的 SPY 换成目标 ticker 即可
```

### 下载后必须执行

拿到 CSV 后，用数据管道生成引擎可消费的 JSON，再放入 `market-data/live/YYYY-MM-DD/`：

```powershell
cd "..\Dream bigger\data"
python build_json.py raw/daily/SPY_1min_2026-04-27.csv --auto-warmup
# 输出: processed/SPY_2026-04-27.json → 复制到 Daily review/market-data/live/2026-04-27/
```

详细用法见 `Dream bigger/data/README.md`。

---

## Quick Start

Open the app directly:

```powershell
Start-Process ".\daily-review.html"
```

Then use the page controls to load:

- Market data: `market-data/live/YYYY-MM-DD/SPY_YYYY-MM-DD.json`
- Strategy JSON: `strategies/tang_v*.json`
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
    tang_*.pine                     # PineScript references
```

## Strategy JSON

All strategy versions should live in `strategies/` and follow `strategy.schema.json`.

Validate strategy files with:

```powershell
npx --yes ajv-cli@5 validate --spec=draft2020 `
  -s "strategies/strategy.schema.json" `
  -d "strategies/tang_v*.json"
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
  --strategy "strategies/tang_v3_5_1_full.json" `
  --out "reviewed/SPY_2026-04-22.tang_v3_5_1_full.json"
```

## Generate Shareable HTML Snapshot

For a single-file HTML you can open offline (double-click, no HTTP server),
inline the day's market JSON + strategy into `daily-review.html`:

```powershell
python "app-data/scripts/build_reviewed_html.py" `
  --date 2026-04-27 `
  --strategy "strategies/tang_v4_4_slope.json"
# → reviewed/SPY_2026-04-27_review.html
```

The script reads `daily-review.html`, injects
`window.__EMBEDDED_DATA__ / __EMBEDDED_STRATEGY__ / __EMBEDDED_DATE__`
and patches `init()` to consume them. Strategy is optional; if omitted, the
viewer falls back to its dropdown default (currently `tang_v3`).

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
