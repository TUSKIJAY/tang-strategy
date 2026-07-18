# Repository Guidelines

## Agent Startup Contract

Before substantive work:

1. Confirm the repository root, current branch, and `git status --short --branch`.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and `HANDOFF.md` in that order.
3. Use `.harness/config.json` and `scripts/check-project-harness.py` for the current verification baseline.

`AGENTS.md` is the authoritative instruction entry. `CLAUDE.md` is a compatibility pointer and must not become a second policy copy. Keep stable project facts in `INSTRUCTIONS.md`, current lifecycle truth in `PROGRESS.md`, and only the latest resume point in `HANDOFF.md`. Update the two state files when the working state or next gate materially changes.

Preserve all unrelated user changes. Do not overwrite, revert, stage, or commit them as part of another task.

## Project Structure & Module Organization

This repo is a frontend/backend workspace for Tang Strategy.

- `backend/` exposes APIs, manages imports, and serves review payloads.
- `frontend/` renders Review, Backtest, and Teaching pages.
- `backend/app`, `frontend/src`, `strategies/`, `content/`, and `data/` are the active code/data boundaries.
- `data/seed/market-data/live_extended` is the only seed source format accepted by current pipeline.
- `docs/roadmap.md` owns product direction; governed lifecycle artifacts live under `docs/exec-plans`, `docs/decisions`, `docs/optimization`, and `docs/progress-archive`.
- Generated static review JSON belongs in `frontend/public/reviews`, Vite output belongs in `frontend/dist`, and publication output belongs on `gh-pages`; generated output must not be written back under `docs/`.

## Build, Test, and Development Commands

- `docker compose up --build` — run full stack.
- `cd backend && PYTHONPATH=. uvicorn app.main:app --reload` — run backend.
- `cd backend && PYTHONPATH=. python scripts/rebuild_live_extended_db.py` — build and validate a candidate DB, reject date/non-market shrink by default, then atomically promote.
- `cd frontend && npm run dev` — run frontend.
- `cd frontend && npm run build` — production build.

## Coding Style & Naming Conventions

- Python: 4-space indent, type hints on new/changed functions where practical.
- JS/JSX/CSS: 2-space indent.
- Data files: `SPY_YYYY-MM-DD.json` under `live_extended/<YYYY-MM-DD>/`.
- Keep naming lowercase with underscores for strategy/case/rule assets.

## Testing Guidelines

- For logic changes: validate SPY 2026-07-17 market day assembly with `tang-v4-4-slope-4-4` and a known strategy end-to-end through frontend.
- Backend validation: `/api/reviews/assemble` should return payload with 1m and 5m bars.
- Frontend validation: open Review and Backtest pages, run one-day regression manually.
- Harness validation: `python3 scripts/check-project-harness.py --root . --profile auto`.

## Commit & PR Guidelines

Use concise conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). PRs should include:
- What changed and why.
- Data-impacted files or directories.
- How to verify (`rebuild`, day selection, screenshots or endpoint output).

GitHub integration:

- Pull requests targeting `main` run `.github/workflows/project-harness.yml`: harness structure, backend tests/compile, and frontend build.
- Use `.github/pull_request_template.md`; keep `PROGRESS.md` and `HANDOFF.md` truthful when the next gate changes.
- A green GitHub check is verification evidence, not merge or publish authorization. Do not push, open/merge a PR, or change branch protection without an explicit user request.
- The existing `Publish static reviews` workflow remains the only Pages publisher and runs from `main` under the daily publish contract.

## Security & Config Notes

- Keep `.env` values private.
- Use admin token only for import endpoints.
- Do not commit provider credentials or generated historical artifacts.
- The tracked SQLite DB is the runtime and Pages input. Rebuild must remain candidate-first and fail closed; the daily/default path must never use `--allow-date-loss`.

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
