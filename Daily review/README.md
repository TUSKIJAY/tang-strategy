# Daily Review

Daily Review is a local SPY intraday review tool for Tang Strategy. It helps load market data, visualize 1m / 5m candles, review strategy signals, and keep strategy versions as JSON files.

This project is designed for local use first: open the HTML file, load data, choose a strategy, and review the day.

## What It Does

- Shows 1m and 5m SPY candles with moving averages, VWAP, volume, and annotations.
- Supports Heikin-Ashi and regular OHLC views.
- Loads raw market JSON from `market-data/live/YYYY-MM-DD/`.
- Loads reviewed JSON with precomputed annotations from `reviewed/`.
- Loads strategy definitions from `strategies/tang_*.json`.
- Provides Python scripts for signal scanning and options-style backtesting.

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
  app-data/scripts/
    scan_signals.py                 # Market JSON + strategy JSON -> reviewed JSON
    backtest.py                     # SPY options scalping backtest
  market-data/live/YYYY-MM-DD/
    SPY_YYYY-MM-DD.json             # Market data
  reviewed/
    *.json                          # Reviewed data with annotations
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

