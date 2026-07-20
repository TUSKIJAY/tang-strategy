# Repository Guidelines

## Agent Startup Contract

Before substantive work:

1. Confirm the repository root, current branch, and `git status --short --branch`.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and `HANDOFF.md` in that order.
3. Use `.harness/config.json` and `scripts/check-project-harness.py` for the current verification baseline.

`AGENTS.md` is the authoritative instruction entry. `CLAUDE.md` is a compatibility pointer and must not become a second policy copy. Keep stable project facts in `INSTRUCTIONS.md`, current lifecycle truth in `PROGRESS.md`, and only the latest resume point in `HANDOFF.md`. Update the two state files when the working state or next gate materially changes.

Preserve all unrelated user changes. Do not overwrite, revert, stage, or commit them as part of another task.

## Operating Modes Router

Use [`docs/operating-modes.md`](./docs/operating-modes.md) as the single normative routing and lifecycle contract. Coding Mode and Data Update Mode are peer modes. Read-only/ambiguous work starts in Coding Lane 1; bounded maintenance is legal only when every Lane 2 criterion passes; governance, DB, market-data, publication, security, cross-contract, broad, or difficult-to-rollback changes require a reviewed Lane 3 Exec Plan. Routine use of existing fetch/rebuild/acceptance tooling uses Data Update Mode. Local acceptance never grants commit, push, or publication authority; the daily triggers below are the only standing publish triggers.

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
- Data files: paired `SPY_YYYY-MM-DD.json` and `QQQ_YYYY-MM-DD.json` under `live_extended/<YYYY-MM-DD>/` for newly accepted dates.
- Keep naming lowercase with underscores for strategy/case/rule assets.

## Testing Guidelines

- For logic changes: validate SPY 2026-07-17 market day assembly with `tang-v4-4-slope-4-4`, normalized trade records, and a known strategy end-to-end through frontend.
- Backend validation: `/api/reviews/assemble` should return payload with 1m and 5m bars.
- Frontend validation: open Review and Backtest pages, run one-day regression manually.
- Harness validation: `python3 scripts/check-project-harness.py --root . --profile auto`.

## Commit & PR Guidelines

Use concise conventional commits (`feat:`, `fix:`, `docs:`, `chore:`). PRs should include:
- What changed and why.
- Data-impacted files or directories.
- How to verify (`rebuild`, day selection, screenshots or endpoint output).

Lifecycle-product local commits follow the durable checkpoint contract in [`docs/operating-modes.md`](./docs/operating-modes.md#9-durable-checkpoint-contract). The checker is read-only; only a separately authorized human or agent may stage literal manifest paths and create the scoped local commit. Checkpoint authority never grants push, PR, merge, Pages, or other remote authority.

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
- "发布 SPY/QQQ YYYY-MM-DD"

…they mean run the full daily publish flow defined in [`docs/daily-publish-runbook.md`](./docs/daily-publish-runbook.md). Execute the steps below without re-asking — the user has already given consent by using the trigger phrase. If they omit the date, resolve the latest completed session from the actual US equity trading calendar and current ET time; do not use weekday-only logic.

Market-source rule: the tracked SPY/QQQ pair orchestrator with TradingView is the default daily source.
Do not check, open, or require IB Gateway before the TV attempt. A closed Gateway
is normal and must not block publishing. Ask for IB Gateway only after the TV
retries or a hard TV quality gate fail, and report the exact failed gate first.

```bash
# 1. Validate any supplied normalized trader/day content before the pair run.
cd backend
PYTHONPATH=. python -c "from pathlib import Path; from app.services.trade_records import load_trader_registry, validate_trade_repository; r=load_trader_registry(Path('../content/traders/index.json')); print(len(validate_trade_repository(Path('../content/trades').glob('*.json'), r)))"

# 2. Fetch, validate, candidate-build, and atomically accept one same-provider pair.
PYTHONPATH=. python scripts/update_spy_qqq_market_day.py <YYYY-MM-DD> --provider tradingview

# 3. If normalized trader content is added after step 2, use the admin endpoint/UI;
# its atomic content replacement also candidate-projects and promotes the DB.

# 4. (Optional) Local export + static build as sanity check.
PYTHONPATH=. python scripts/export_static_reviews.py --output ../frontend/public/reviews --limit 250 --strategy-families v3,v4,v5
cd ../frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews
rm -rf public/reviews dist && cd ..

# 5. Commit the DB plus normalized trader/day JSON if created/changed, then push.
git add data/sqlite/tang_strategy_live_extended.db
git add content/traders/index.json content/trades/<YYYY-MM-DD>.json  # only if changed
git commit -m "feat: publish SPY/QQQ <YYYY-MM-DD> review"
git push origin main

# 6. Watch the Pages workflow. URL: https://tuskijay.github.io/tang-strategy/#spy-<YYYY-MM-DD>-extended
gh run list --repo TUSKIJAY/tang-strategy --workflow "Publish static reviews" --branch main --limit 1
gh run watch <run-id> --repo TUSKIJAY/tang-strategy --exit-status
```

Pre-flight assumptions: install the pinned TV runtime from `backend/requirements-tv.txt` when needed. The pair orchestrator uses the actual NYSE calendar, including scheduled early closes, and writes neither ticker unless both hard gates and the single candidate pass. If TV fails after retries or a hard quality gate fails, report the failed ticker/gate, ask the user to start IB Gateway on live port 4002, wait for HMDS `2106`, and rerun the complete pair with `--provider ibkr`. Do not bypass the pair step; Pages reads the committed DB, not gitignored seed JSON.
