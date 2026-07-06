# Daily Publish Runbook (SPY live extended)

SOP for the end-to-end daily flow: pull bars from IB Gateway → rebuild SQLite → export static review payloads → push `main` → GitHub Pages.

The published target URL is `https://tuskijay.github.io/tang-strategy/#<ticker>-<date>-extended`.

## 0. Pre-flight

- IB Gateway is logged in to the **live** account, with the API socket exposed.
- API socket port matches `IBKR_PORT` in `.env` / `backend/app/settings.py`. Default is **4002**.
- After any IB Gateway restart, wait ~10 seconds and check the farm warm-up log:

  ```
  Warning 2104  Market data farm connection is OK: usfarm
  Warning 2106  HMDS data farm connection is OK: ushmds        ← must be 2106, not 2107 inactive
  Warning 2158  Sec-def data farm connection is OK: secdefil
  ```

  If `ushmds` shows `2107 inactive`, fully exit IB Gateway (tray icon → Exit, not just the window) and log back in. Historical requests against an inactive HMDS farm silently time out.
- Working tree is clean: `git status` shows no uncommitted changes (the `publish_spy_review.ps1` helper enforces this).

## 1. Fetch the day from IB Gateway

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
| `reqHistoricalData: Timeout` + `0 bars` | HMDS farm inactive (see §0) or pacing violation. | Restart IB Gateway; if pacing, wait 10 min and retry. |
| `IBKR could not qualify contract for SPY` | Wrong port (paper vs live) or no contract data subscription. | Confirm IB Gateway is on live, port matches, market-data subscriptions active. |

## 2. Rebuild the runtime DB

```bash
cd backend
PYTHONPATH=. python scripts/rebuild_live_extended_db.py
```

This deletes and re-imports `data/sqlite/tang_strategy_live_extended.db` from every `SPY_*.json` / `SPX_*.json` under `live_extended/`. Idempotent — required because the published page reads from the committed DB.

Verify the new day landed:

```bash
PYTHONPATH=. python -c "
from app.db import connect
with connect() as c:
    print(c.execute('SELECT id, ticker, trade_date FROM market_days ORDER BY trade_date').fetchall())
    print('5/19 1m count:', c.execute(\"SELECT COUNT(*) FROM bars_1m b JOIN market_days m ON m.id=b.market_day_id WHERE m.trade_date='<date>'\").fetchone()[0])
"
```

## 3. Export static review payloads (local sanity build)

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

## 4. Commit and push

Only one tracked artifact carries new data into the workflow: the SQLite DB.

```bash
git add data/sqlite/tang_strategy_live_extended.db
git commit -m "feat: publish SPY <YYYY-MM-DD> review"
git push origin main
```

If you also changed source code (e.g. fetch script, settings), bundle them into the same commit and reword the message accordingly.

The fetched JSON under `data/seed/market-data/live_extended/<date>/` is gitignored by design — the DB is the source of truth that ships to Pages.

## 5. Wait for the Pages workflow

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

`scripts/publish_spy_review.ps1` chains steps 0–5 above. It is gitignored on purpose — keep it as personal scaffolding, not a shared tool. Defaults: `IbPort=4002`, `Symbol=SPY`, latest completed market date.

```powershell
pwsh scripts/publish_spy_review.ps1                 # latest market day
pwsh scripts/publish_spy_review.ps1 -Date 2026-05-19
pwsh scripts/publish_spy_review.ps1 -NoPush         # dry run, no git push
```
