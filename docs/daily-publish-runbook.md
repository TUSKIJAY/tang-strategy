# Daily Publish Runbook (SPY live extended)

SOP for the end-to-end daily flow: fetch SPY from TradingView first → validate the market day → use IB Gateway only when a hard quality gate fails → rebuild SQLite → record Tang SPY 0DTE trades → export static review payloads → push `main` → GitHub Pages.

The published target URL is `https://tuskijay.github.io/tang-strategy/#<ticker>-<date>-extended`.

## Source policy

The active operating model is **TV default, IB exception only**:

1. Run the tracked `fetch_tv_live_extended_day.py` adapter without checking or starting IB Gateway.
2. Validate the completed US market day before writing/importing the canonical seed.
3. If every hard gate passes, continue the publish flow with TradingView data. Do not ask the user to start Gateway.
4. If a hard gate fails after the documented retries, preserve the previous published page, report the exact failed gate, and ask the user to start IB Gateway.
5. After IB is ready, fetch the whole day from IB and restart validation. Never mix TV and IB bars inside one market day.

The adapter and its runtime are repository-owned:

- Entry point: `backend/scripts/fetch_tv_live_extended_day.py`.
- Reproducible dependencies: `backend/requirements-tv.txt`.
- Provider client: `tvDatafeed` pinned to commit `e6f6aaa7de439ac6e454d9b26d2760ded8dc4923`.
- Market calendar: `pandas_market_calendars==5.4.0` with `exchange_calendars==4.13.2`, using the NYSE schedule for holidays and scheduled early closes.
- Optional credentials: `TRADINGVIEW_USERNAME` and `TRADINGVIEW_PASSWORD`; anonymous access remains the default when both are absent.

Do not substitute an ad-hoc Downloads script or the separate local
`D:\Code\tradingview_fetch` checkout for the tracked adapter.

## 0. Pre-flight

- Resolve the requested date using the actual US equity trading calendar. Skip exchange holidays. Do not infer a valid session from weekday alone.
- Worktree is clean: `git status` shows no unrelated changes.
- Do not preflight, open, or restart IB Gateway before the TV attempt.
- Do not commit TradingView credentials. If authenticated access is later used, load it from local environment variables or GitHub Secrets.
- Keep raw/diagnostic TV output outside the tracked seed tree. Only a payload that passes every hard gate may replace `data/seed/market-data/live_extended/<date>/SPY_<date>.json`.

## 1. Fetch the day from TradingView (default path)

Install the TV runtime once per Python environment, then run the tracked adapter:

```bash
cd backend
python -m pip install -r requirements-tv.txt
PYTHONPATH=. python scripts/fetch_tv_live_extended_day.py <YYYY-MM-DD>
```

Expected behavior:

- Use the `tvDatafeed` commit pinned in `requirements-tv.txt`, not a mutable branch.
- Request `AMEX:SPY`, `1m`, `extended_session=True` with retries.
- Interpret/filter bars in `America/New_York` and retain only the requested market date.
- Resolve the real NYSE session from the exchange calendar; reject holidays and automatically use the scheduled early-close boundary.
- Build the same `live_extended` payload contract consumed by the importer, including derived 5m, MA, HA, session VWAP, provider metadata, and quality summary.
- Validate every hard gate before writing/importing. A hard-gate failure must not replace a previously valid seed or runtime DB.

### Hard TV quality gates

All must pass:

| Gate | Normal full day | Scheduled early close |
|---|---:|---:|
| Expected RTH window | 09:30–15:59 ET | 09:30–12:59 ET |
| RTH 1m bars | 390 | 210 |
| RTH 5m bars after derivation | 78 | 42 |
| Missing/duplicate RTH minutes | 0 | 0 |

Also require:

- Every timestamp belongs to the requested New York market date, is strictly ordered, and is unique.
- OHLC values are finite and positive; `high >= open/close/low` and `low <= open/close`; volume is finite and non-negative.
- The first and last RTH bars match the scheduled session boundaries.
- Derived RTH 5m bars cover the complete scheduled window without gaps.
- Session VWAP is available for usable positive-volume RTH bars.
- Rebuild/import succeeds, `/api/reviews/assemble` returns both 1m and 5m bars, and the static export/build completes.

### TV warnings that do not trigger IB by themselves

- Total extended-session bars are below 960 because TradingView may omit no-trade premarket/after-hours minutes.
- Premarket or after-hours minutes are sparse while the scheduled RTH window is complete.
- TradingView absolute volume is lower than IB's consolidated-looking volume.
- TV-derived VWAP differs from prior IB-derived VWAP, provided the payload and signal-impact checks complete and the difference is recorded.

Do not pad missing TV minutes with synthetic prices merely to reach 960. Record extended-session coverage and source metadata in the payload/report.

### When to fall back to IB

Use the IB path only after one of these remains true after the configured TV retries:

- connection/authentication/rate-limit failure or no usable response;
- wrong market date/timezone/session boundaries;
- incomplete or duplicate RTH minutes;
- invalid OHLCV values;
- incomplete derived RTH 5m coverage;
- failed VWAP/payload/import/assemble/static-build validation attributable to TV data.

When fallback is required, stop before commit/push and tell the user exactly which gate failed. Ask them to start IB Gateway; do not attempt to publish a partial TV day.

## 2. Fetch the day from IB Gateway (fallback only)

Only enter this section after the tracked TV adapter exhausts its retries or a hard TV gate fails.

IB pre-flight:

- IB Gateway is logged in to the **live** account, with the API socket exposed.
- API socket port matches `IBKR_PORT` in `.env` / `backend/app/settings.py`. Default is **4002**.
- After restart, wait ~10 seconds and require HMDS `2106`, not `2107 inactive`:

  ```
  Warning 2104  Market data farm connection is OK: usfarm
  Warning 2106  HMDS data farm connection is OK: ushmds
  Warning 2158  Sec-def data farm connection is OK: secdefil
  ```

If `ushmds` remains `2107 inactive`, fully exit IB Gateway from the tray and log back in.

```bash
cd backend
PYTHONPATH=. python scripts/fetch_ib_live_extended_day.py <YYYY-MM-DD>
```

What it does:

- Connects to `IBKR_HOST:IBKR_PORT` (defaults to `127.0.0.1:4002`).
- Qualifies `Stock("SPY", "SMART", "USD", primaryExchange="ARCA")`.
- Requests `1 D / 1 min / TRADES / useRTH=False` ending at `20:00 ET` of the trade date (full extended session, 04:00–20:00 ET).
- Writes `data/seed/market-data/live_extended/<date>/SPY_<date>.json` and imports it into the runtime SQLite DB.

Expected output:

```
Wrote .../SPY_<date>.json with 960 1m bars, 192 5m bars, gaps=0, market_day_id=<n>
```

960 = 16h × 60m. Gaps > 0 means missing minutes — investigate before publishing.

Common failures:

| Symptom | Cause | Fix |
|---|---|---|
| `RuntimeError: There is no current event loop in thread 'MainThread'.` | Python 3.14 + `eventkit` import. | The script preinitializes the loop. If you see this on another script, copy the `asyncio.set_event_loop(asyncio.new_event_loop())` pattern at the top. |
| `reqHistoricalData: Timeout` + `0 bars` | HMDS farm inactive (see the IB pre-flight above) or pacing violation. | Restart IB Gateway; if pacing, wait 10 min and retry. |
| `IBKR could not qualify contract for SPY` | Wrong port (paper vs live) or no contract data subscription. | Confirm IB Gateway is on live, port matches, market-data subscriptions active. |

## 3. Rebuild the runtime DB

```bash
cd backend
PYTHONPATH=. python scripts/rebuild_live_extended_db.py
```

This is a fail-closed candidate rebuild. It never deletes the current DB before import:

1. Discover and validate every `SPY_*.json` / `SPX_*.json` under `live_extended/`.
2. Import market days, strategies, and teaching assets into a fresh adjacent candidate DB.
3. Require non-empty 1m/5m bars, seed/declared/actual count agreement, SQLite integrity and foreign keys, and no strategy/teaching key shrink.
4. By default, require the candidate market-day key set to be a superset of the current DB. If dates would be lost, the command exits nonzero and lists every missing date.
5. Re-check that the current DB did not drift while the candidate was built, then atomically promote the verified candidate.

On any empty seed, parse/import error, semantic mismatch, integrity failure, date loss, or concurrent drift, the current DB bytes remain unchanged. The explicit `--allow-date-loss` flag exists only for an intentional, supervised shrink. The daily publish flow and normal automation must never use it.

This step remains required because the published page reads from the committed DB, not the gitignored seed JSON.

Verify the new day landed:

```bash
PYTHONPATH=. python -c "
from app.db import connect
with connect() as c:
    print(c.execute('SELECT id, ticker, trade_date FROM market_days ORDER BY trade_date').fetchall())
    print('<date> 1m count:', c.execute(\"SELECT COUNT(*) FROM bars_1m b JOIN market_days m ON m.id=b.market_day_id WHERE m.trade_date='<date>'\").fetchone()[0])
"
```

## 4. Record Tang SPY 0DTE trades

Tang's real SPY option entries are stored separately from market data under:

```
content/trader-trades/<YYYY-MM-DD>.json
```

This file is optional for market data publishing, but required when Tang provided real SPY 0DTE execution points or a relevant SPY context note. Do **not** put trade notes into `data/seed/market-data/live_extended`; that tree is market bars only.

Use this shape when Tang traded SPY:

```json
{
  "date": "2026-05-26",
  "ticker": "SPY",
  "trades": [
    {
      "time": "09:42",
      "side": "CALL",
      "strike": 750,
      "expiry": "2026-05-26",
      "action": "buy_open",
      "source": "screenshot",
      "reason_type": "explicit_note",
      "note": "5min MA200 附近支撑，1min MA10 跌破后拉回，目标 5min MA50。"
    }
  ],
  "notes": []
}
```

Use this shape when Tang did **not** trade SPY, but SPY was still used as market context:

```json
{
  "date": "2026-05-29",
  "ticker": "SPY",
  "trades": [],
  "notes": [
    "SPY 仅作为大盘方向确认；当天 IV 偏高，Tang 未交易 SPY 0DTE。"
  ]
}
```

Rules:

- Only record actual **SPY 0DTE** entries in `trades`.
- If Tang traded another symbol (for example NVDA) while using SPY as market context, leave `trades` empty and put the SPY context in `notes`; do not create a fake SPY trade.
- `note` may be empty when the entry simply follows the existing strategy.
- `reason_type` should be one of `explicit_note`, `strategy_aligned`, `manual_discretion`, or `unknown`.
- Times are Eastern market time in `HH:MM`, matching the chart bars.

Quick validation:

```bash
cd backend
PYTHONPATH=. python -c "
from app.services.tang_trades import load_tang_trades
import json
print(json.dumps(load_tang_trades('SPY', '<YYYY-MM-DD>'), ensure_ascii=False, indent=2))
"
```

The Review page renders these as a separate `Tang Trades` layer. They should appear as Tang-specific gold/purple markers and must not be visually confused with strategy signals.

## 5. Export static review payloads (local sanity build)

```bash
cd backend
PYTHONPATH=. python scripts/export_static_reviews.py \
  --output ../frontend/public/reviews \
  --limit 250 \
  --ticker SPY \
  --strategy-families v3,v4,v5
```

```bash
cd frontend
VITE_STATIC_REVIEWS=true npm run build:static-reviews
```

This step is **optional but recommended** — it reproduces what the GitHub Action will do, so any export/build regression surfaces locally before pushing.

After build, clean the temp inputs (they are not committed):

```bash
rm -rf frontend/public/reviews frontend/dist
```

## 6. Commit and push

The SQLite DB carries the market bars into the workflow. Tang trade files carry the manual execution layer when present.

```bash
git add data/sqlite/tang_strategy_live_extended.db
git add content/trader-trades/<YYYY-MM-DD>.json  # only if created or changed
git commit -m "feat: publish SPY <YYYY-MM-DD> review"
git push origin main
```

If you also changed source code (e.g. fetch script, settings), bundle them into the same commit and reword the message accordingly.

The fetched JSON under `data/seed/market-data/live_extended/<date>/` is gitignored by design — the DB is the market-data source of truth that ships to Pages.

## 7. Wait for the Pages workflow

```bash
gh run list --repo TUSKIJAY/tang-strategy --workflow "Publish static reviews" --branch main --limit 1
gh run watch <run-id> --repo TUSKIJAY/tang-strategy --exit-status
```

The workflow exports payloads, builds the static site, and publishes to `gh-pages`. Typical run time is ~25 seconds. On success, open:

```
https://tuskijay.github.io/tang-strategy/#spy-<YYYY-MM-DD>-extended
```

CDN/cache typically refreshes in under a minute; hard-reload (`Ctrl+Shift+R`) if you see the previous day.

## One-command helper (local only)

`scripts/publish_spy_review.ps1` is an existing gitignored, IB-oriented personal helper. It is **not** the authoritative TV-first automation and must not be described as such until it is replaced by a tracked helper that applies the hard gates above. Tang trade JSON still needs to be reviewed/edited manually when Tang provides execution notes.

```powershell
pwsh scripts/publish_spy_review.ps1                 # latest market day
pwsh scripts/publish_spy_review.ps1 -Date 2026-05-19
pwsh scripts/publish_spy_review.ps1 -NoPush         # dry run, no git push
```
