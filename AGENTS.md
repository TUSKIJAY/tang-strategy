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

…they mean run the full daily publish flow defined in [`docs/daily-publish-runbook.md`](./docs/daily-publish-runbook.md). Execute the steps below without re-asking — the user has already given consent by using the trigger phrase. If they omit the date, default to the latest completed US trading day (yesterday if after 20:00 ET, else the prior weekday).

```bash
# 1. Fetch from IB Gateway (live, port 4002). Expect "960 1m bars, gaps=0".
cd backend && PYTHONPATH=. python scripts/fetch_ib_live_extended_day.py <YYYY-MM-DD>

# 2. Canonicalize the runtime DB.
PYTHONPATH=. python scripts/rebuild_live_extended_db.py

# 3. (Optional) Local export + static build as sanity check.
PYTHONPATH=. python scripts/export_static_reviews.py --output ../frontend/public/reviews --limit 250 --ticker SPY --strategy-families v3,v4,v5
cd ../frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews
rm -rf public/reviews dist && cd ..

# 4. Commit the DB (the only tracked artifact that carries new data) and push.
git add data/sqlite/tang_strategy_live_extended.db
git commit -m "feat: publish SPY <YYYY-MM-DD> review"
git push origin main

# 5. Watch the Pages workflow. URL: https://tuskijay.github.io/tang-strategy/#spy-<YYYY-MM-DD>-extended
gh run list --repo TUSKIJAY/tang-strategy --workflow "Publish static reviews" --branch main --limit 1
gh run watch <run-id> --repo TUSKIJAY/tang-strategy --exit-status
```

Pre-flight assumptions: IB Gateway is logged in to the live account on port 4002, and HMDS farm warm-up logged `Warning 2106 HMDS data farm connection is OK: ushmds` (not `2107 inactive`). If step 1 returns `0 bars` / `reqHistoricalData: Timeout`, restart IB Gateway and retry — see the troubleshooting table in the runbook. Do not skip step 2; the Pages workflow reads from the committed DB, not from the seed JSON (which is gitignored).
