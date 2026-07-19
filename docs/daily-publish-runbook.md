# Daily Publish Runbook (SPY/QQQ Extended Pair)

This is the end-to-end daily contract for one completed NYSE session:

`canonical trade validation -> TradingView SPY/QQQ pair -> hard quality gates -> one candidate/promotion -> local acceptance -> separately authorized commit/push -> Pages -> hosted verification`

The published route remains `https://tuskijay.github.io/tang-strategy/#<ticker>-<date>-extended`. Grandfathered SPY-only dates remain legal. Newly accepted dates are pair-atomic: both SPY and QQQ advance from one provider or neither advances.

## 0. Authority And Pre-flight

- A daily trigger in `AGENTS.md`, or an equivalent explicit publish instruction, opens pending publication authority. It does not waive local gates.
- Resolve the date from the actual NYSE calendar and current ET. Include scheduled early closes; weekday-only logic is forbidden.
- Capture `git status --short --branch`, HEAD, and the tracked DB SHA-256 before the run.
- Preserve unrelated changes. Commit only the authorized DB and applicable canonical trader/day JSON.
- Install `backend/requirements-tv.txt` in the selected pinned Python environment.
- Do not check, open, or request IB Gateway before the TradingView pair attempt.
- Keep credentials and provider diagnostics outside tracked files.

## 1. Canonical Trader And Trade Content

Canonical source lives at:

```text
content/traders/index.json
content/trades/YYYY-MM-DD.json
```

One daily file may contain all configured traders and both underlyings. Missing facts remain null; do not fabricate fills, fees, outcomes, strikes, times, or a no-trade context. Raw screenshots, chats, attachments, and evidence blobs are forbidden.

Validate the whole repository before the pair run when content was supplied:

```bash
cd backend
PYTHONPATH=. python -c "
from pathlib import Path
from app.services.trade_records import load_trader_registry, validate_trade_repository
registry = load_trader_registry(Path('../content/traders/index.json'))
days = validate_trade_repository(Path('../content/trades').glob('*.json'), registry)
print({'trade_days': len(days), 'traders': len(registry['traders'])})
"
```

If an admin edits content after the pair run, use `PUT /api/admin/traders` or `PUT /api/admin/trade-records` through the admin UI/API. Those endpoints atomically replace canonical content and re-project the complete normalized repository through a drift-checked candidate DB; failure restores both boundaries.

## 2. TradingView Pair — Default

Run only the pair orchestrator:

```bash
cd backend
PYTHONPATH=. python scripts/update_spy_qqq_market_day.py <YYYY-MM-DD> --provider tradingview
```

The orchestrator:

1. snapshots Git and the tracked DB;
2. invokes the pinned one-symbol TV adapter with import disabled for `AMEX:SPY` and `NASDAQ:QQQ` into a unique temporary directory;
3. validates both payloads and the same date/session/provider contract;
4. copies the live DB to one candidate, imports both datasets, refreshes the canonical trade projection, and preserves grandfathered days;
5. requires integrity, zero FK failures, one active dataset per logical day, non-empty 1m/5m assemble paths, and no live-DB drift;
6. rollback-protects the accepted seed pair and atomically promotes the candidate;
7. returns a receipt with before/after DB hashes, per-ticker quality, candidate counts, preservation, trade projection, and cleanup warnings.

### Hard quality gates per ticker

| Gate | Full day | Scheduled early close |
| --- | ---: | ---: |
| RTH window | 09:30–15:59 ET | 09:30–12:59 ET |
| RTH 1m bars | 390 | 210 |
| RTH 5m bars | 78 | 42 |
| Missing/duplicate RTH minutes | 0 | 0 |

Also require:

- every `ts` belongs to the requested New York date, has the correct IANA offset, and agrees with display time `t`;
- strictly ordered unique timestamps;
- finite valid OHLC and non-negative finite volume;
- exact first/last RTH boundaries and complete derived 5m coverage;
- usable session VWAP and `synthetic_padding=false`;
- identical provider identity across SPY and QQQ;
- no change to non-target grandfathered day digests.

Sparse extended-session minutes or totals below 960 do not fail by themselves when scheduled RTH is exact. Never pad missing minutes with synthetic prices.

## 3. IB Pair — Fallback Only

Enter this section only after the TV retries exhaust or a named hard gate fails. Report the exact ticker and gate first, then ask the user to start IB Gateway.

IB requirements:

- live account socket at `IBKR_HOST:IBKR_PORT` (default `127.0.0.1:4002`);
- market-data subscriptions for both SPY and QQQ;
- HMDS `2106` ready, not only `2107 inactive`.

Then rerun the complete pair:

```bash
cd backend
PYTHONPATH=. python scripts/update_spy_qqq_market_day.py <YYYY-MM-DD> --provider ibkr
```

Do not accept a mixed TV/IB pair and do not run one symbol directly as the daily completion path.

## 4. Local Acceptance

The successful pair receipt must show both tickers, one promoted candidate, integrity `ok`, zero foreign-key failures, and preserved grandfathered days. Then verify:

```bash
cd backend
PYTHONPATH=. python -c "
from app.db import connect
with connect() as c:
    print(c.execute(
        \"SELECT ticker, trade_date, bar_count_1m, bar_count_5m FROM market_days WHERE trade_date=? ORDER BY ticker\",
        ('<YYYY-MM-DD>',),
    ).fetchall())
    print(c.execute('PRAGMA integrity_check').fetchall())
    print(c.execute('PRAGMA foreign_key_check').fetchall())
"
```

For each ticker, require `/api/reviews/assemble` to return non-empty `bars_1m`, `bars_5m`, and only the `trade_records` public member. Verify SPY 2026-07-17 with `tang-v4-4-slope-4-4` as the standing regression.

Optional but recommended static acceptance:

```bash
cd backend
PYTHONPATH=. python scripts/export_static_reviews.py \
  --output ../frontend/public/reviews \
  --limit 250 \
  --strategy-families v3,v4,v5
cd ../frontend
VITE_STATIC_REVIEWS=true npm run build:static-reviews
```

The manifest must retain existing `#spy-<date>-extended` links and add `#qqq-<date>-extended` only where QQQ exists. Generated `frontend/public/reviews` and `frontend/dist` remain untracked and must be cleaned after local acceptance.

Stop at `local_accepted` if publication authority is absent or any mandatory check fails.

## 5. Authorized Commit And Push

Only after every local gate passes and publish authority exists:

```bash
git add data/sqlite/tang_strategy_live_extended.db
git add content/traders/index.json content/trades/<YYYY-MM-DD>.json  # only if changed
git commit -m "feat: publish SPY/QQQ <YYYY-MM-DD> review"
git push origin main
```

Accepted seed JSON is gitignored. The committed SQLite DB is the interactive and Pages runtime input. Code, workflow, plan, or unrelated files need their own explicit scope.

## 6. Pages And Hosted Verification

```bash
gh run list --repo TUSKIJAY/tang-strategy --workflow "Publish static reviews" --branch main --limit 1
gh run watch <run-id> --repo TUSKIJAY/tang-strategy --exit-status
```

Verify both URLs for the newly paired date:

```text
https://tuskijay.github.io/tang-strategy/#spy-<YYYY-MM-DD>-extended
https://tuskijay.github.io/tang-strategy/#qqq-<YYYY-MM-DD>-extended
```

Workflow green is not enough: confirm both hosted payloads render bars, normalized trader filters/markers, and the existing strategy review flow. Record push, workflow, and hosted states separately; never label a not-run state as pass.

## Failure Rule

Any provider, pair, candidate, integrity, FK, preservation, projection, assemble, static, push, workflow, or hosted failure stops advancement at the last proven state. Preserve the prior accepted pair and DB, report the named failed gate plus before/after evidence, and do not use `--allow-date-loss`, fabricate data, weaken validation, or publish a partial result.
