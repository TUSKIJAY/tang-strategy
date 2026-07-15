# Repository Guidelines

## Project Structure & Module Organization

This repo is a frontend/backend workspace for Tang Strategy.

- `backend/` exposes APIs, manages imports, and serves review payloads.
- `frontend/` renders Review, Backtest, and Teaching pages.
- `backend/app`, `frontend/src`, `strategies/`, `content/`, and `data/` are the active code/data boundaries.
- `data/seed/market-data/live_extended` is the only seed source format accepted by current pipeline.
- `legacy/` is not part of active code paths.

## Build, Test, and Development Commands

- `docker compose up --build` — run full stack.
- `cd backend && PYTHONPATH=. uvicorn app.main:app --reload` — run backend.
- `cd backend && PYTHONPATH=. python scripts/rebuild_live_extended_db.py` — rebuild DB from live_extended seed.
- `cd frontend && npm run dev` — run frontend.
- `cd frontend && npm run build` — production build.

## Coding Style & Naming Conventions

- Python: 4-space indent, type hints on new/changed functions where practical.
- JS/JSX/CSS: 2-space indent.
- Data files: `SPY_YYYY-MM-DD.json` under `live_extended/<YYYY-MM-DD>/`.
- Keep naming lowercase with underscores for strategy/case/rule assets.

## Testing Guidelines

- For logic changes: validate SPY 2026-04-22 market day assembly and a known strategy end-to-end through frontend.
- Backend validation: `/api/reviews/assemble` should return payload with 1m and 5m bars.
- Frontend validation: open Review and Backtest pages, run one-day regression manually.

## Commit & PR Guidelines

Use concise conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). PRs should include:
- What changed and why.
- Data-impacted files or directories.
- How to verify (`rebuild`, day selection, screenshots or endpoint output).

## Security & Config Notes

- Keep `.env` values private.
- Use admin token only for import endpoints.
- Do not commit provider credentials or generated historical artifacts.

## Daily publish playbook (one-sentence trigger)

If the user says any of:

- "发布 SPY YYYY-MM-DD"
- "拉一下 YYYY-MM-DD 的 SPY 然后更新页面"
- "publish SPY review for YYYY-MM-DD"
- "push 5/20 SPY"

…they mean run the full daily publish flow defined in [`docs/daily-publish-runbook.md`](./docs/daily-publish-runbook.md). Execute the steps below without re-asking — the user has already given consent by using the trigger phrase. If they omit the date, resolve the latest completed session from the actual US equity trading calendar and current ET time; do not use weekday-only logic.

Market-source rule: the tracked TradingView adapter is the default daily source.
Do not check, open, or require IB Gateway before the TV attempt. A closed Gateway
is normal and must not block publishing. Ask for IB Gateway only after the TV
retries or a hard TV quality gate fail, and report the exact failed gate first.

```bash
# 1. Fetch and validate the day from TradingView.
cd backend
PYTHONPATH=. python scripts/fetch_tv_live_extended_day.py <YYYY-MM-DD>

# 2. Canonicalize the runtime DB.
PYTHONPATH=. python scripts/rebuild_live_extended_db.py

# 3. Record Tang SPY 0DTE trades/context when provided.
# Edit ../content/trader-trades/<YYYY-MM-DD>.json:
# - actual SPY 0DTE entries go in "trades"
# - no SPY trade / SPY context only goes in "notes" with "trades": []

# 4. (Optional) Local export + static build as sanity check.
PYTHONPATH=. python scripts/export_static_reviews.py --output ../frontend/public/reviews --limit 250 --ticker SPY --strategy-families v3,v4,v5
cd ../frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews
rm -rf public/reviews dist && cd ..

# 5. Commit the DB plus Tang trade JSON if created/changed, then push.
git add data/sqlite/tang_strategy_live_extended.db
git add content/trader-trades/<YYYY-MM-DD>.json  # only if created or changed
git commit -m "feat: publish SPY <YYYY-MM-DD> review"
git push origin main

# 6. Watch the Pages workflow. URL: https://tuskijay.github.io/tang-strategy/#spy-<YYYY-MM-DD>-extended
gh run list --repo TUSKIJAY/tang-strategy --workflow "Publish static reviews" --branch main --limit 1
gh run watch <run-id> --repo TUSKIJAY/tang-strategy --exit-status
```

Pre-flight assumptions: install the pinned TV runtime from `backend/requirements-tv.txt` when needed. The script uses the actual NYSE calendar, including scheduled early closes, and writes only after its hard gates pass. If TV fails after retries or a hard quality gate fails, report the failed gate, ask the user to start IB Gateway on live port 4002, wait for HMDS `2106`, and then use the documented IB fallback. Do not skip step 2; the Pages workflow reads from the committed DB, not from the seed JSON (which is gitignored).
