# Tang Strategy

## Objective

Keep coding-agent work restartable, scope-bounded, and verifiable while preserving the DB-first review runtime, TradingView-first daily source contract, and fail-closed publication data path.

## Project Type

FastAPI backend and React/Vite frontend workspace with a tracked SQLite-backed market-review runtime and a static GitHub Pages export mode.

## Harness Profile

`governed`

The lifecycle is:

`optimization intake -> proposed plan -> independent review -> explicit activation -> active implementation/verification -> independent implementation review -> completed plan`

Optimization records, decisions, proposed plans, and reviews do not grant execution authority by themselves.
Each user-authorized mutating lifecycle step becomes durable in one task-scoped local commit by default. The user may opt out; push, PR, merge, Pages, provider/broker, and other remote actions always require separate authority.

## Authority And Directory Map

- `AGENTS.md` — single authoritative agent entry and hard operational rules.
- `INSTRUCTIONS.md` — stable project facts, boundaries, and verification contract.
- `PROGRESS.md` — current lifecycle truth.
- `HANDOFF.md` — latest resume point, evidence, blocker, and next gate.
- [`docs/operating-modes.md`](./docs/operating-modes.md) — normative peer-mode routing, lifecycle formats, reviewer evidence, and authority gates.
- `.harness/config.json` — machine-readable governed profile and verification/GitHub contract.
- `backend/app/` — FastAPI API, SQLite access, import, auth, and review payload assembly.
- `backend/scripts/`, `backend/tests/` — fetch/rebuild/recovery/export tooling and backend tests.
- `frontend/src/` — Data, Review, Backtest, and Teaching UI plus the shared chart/scanner runtime.
- `strategies/json/`, `strategies/STRATEGY.md` — strategy definitions and canonical signal-intent documentation.
- `content/` — teaching/rule/case assets plus canonical multi-trader SPY/QQQ records and schemas.
- `data/seed/market-data/live_extended/` — the only accepted market-day seed shape; daily files remain gitignored.
- `data/sqlite/tang_strategy_live_extended.db` — tracked interactive runtime and Pages export input.
- `docs/roadmap.md` — product/module roadmap.
- `docs/exec-plans/` — governed proposed/active/completed/review lifecycle and evidence.
- `docs/decisions/` — durable decisions; no automatic implementation authority.
- `docs/optimization/` — record-only follow-up intake.
- `docs/progress-archive/` — indexed historical lifecycle evidence.
- `docs/planning.md` — historical planning summary/compatibility pointer, not active authority.
- `docs/daily-publish-runbook.md` — TV-first fetch through DB rebuild/publish SOP.
- `.github/workflows/project-harness.yml` — PR/manual validation only.
- `.github/workflows/publish-static-reviews.yml` — the only Pages publisher; it runs from `main` under the daily publish contract.

Generated review JSON belongs in `frontend/public/reviews`, the Vite build belongs in `frontend/dist`, and publication output belongs on `gh-pages`. Generated output must not be stored under `docs/`.

## Stable Runtime Contracts

- Interactive mode authenticates through `POST /api/auth/login`, uses readonly/admin bearer roles, lists `/api/market-days` and `/api/strategies`, and assembles a review through `/api/reviews/assemble?market_day_id=<id>&strategy_id=<id>`.
- Pages mode runs `export_static_reviews.py`, writes temporary JSON under `frontend/public/reviews`, builds `StaticReviewsApp` into `frontend/dist`, and force-pushes the build to `gh-pages` only from the authorized publisher workflow.
- Tracked SQLite remains the runtime and Pages data source. This project is not migrating to LFS, release artifacts, or a fully tracked seed history in the current plan.
- Rebuild is candidate-first. Empty/invalid input, semantic mismatch, integrity failure, market-day shrink, strategy/teaching shrink, or live DB drift must reject promotion and leave the current DB unchanged.
- `--allow-date-loss` is a supervised manual override for intentional market-day shrink only. Daily publication and default automation must never use it.
- Daily data acquisition uses the atomic SPY/QQQ pair orchestrator with TradingView first. Do not preflight or request IB Gateway until TV retries are exhausted or a named hard gate fails. A newly accepted date never mixes providers or accepts only one ticker.

## Agent Behavior Rules

1. Read the startup chain, `docs/operating-modes.md`, and the current active plan before modifying files.
2. Use repository evidence; do not invent architecture, completion, decisions, test results, or authority.
3. Preserve unrelated user changes. Stage and commit only task-owned literal paths; do not reset, restore, stash, checkout, stage, commit, or push unrelated work.
4. Keep `PROGRESS.md` truthful when lifecycle state changes; keep `HANDOFF.md` limited to the latest resume point.
5. Keep detailed evidence behind governed indexes so startup documents remain bounded.
6. A green local/GitHub check is verification evidence, not merge or publication authority.
7. Do not fetch, publish, connect to a broker, push, open/merge a PR, or change remote settings without the exact authority required by `AGENTS.md` and the active request.
8. Keep small work small. Do not turn an adjacent observation into a new implementation, plan, reviewer, commit protocol, state machine, or remediation round unless the user asks or a hard safety boundary requires it.

## Verification Commands

### Local Page Acceptance

Run the canonical protected page-acceptance service from the repository root:

```bash
./scripts/start-local-acceptance.sh
```

The script resolves the repository root independently of the caller's current directory, creates a consistent SQLite backup under `/tmp`, and starts the backend with `PYTHONPATH=backend`, `TANG_DB_PATH=<temporary-db>`, and `backend/.venv/bin/uvicorn`. It starts the frontend through `npm --prefix frontend run dev -- --host 127.0.0.1`. Defaults are backend port `8000` and frontend port `5173`; set `TANG_ACCEPTANCE_BACKEND_PORT` and `TANG_ACCEPTANCE_FRONTEND_PORT` to use other free ports. Occupied ports cause a fail-closed exit and no existing process is stopped. Ctrl-C stops only the process groups created by the script, verifies the tracked DB hash, and removes the temporary directory.

### Repository Checks

The verification battery is defined once, in `.harness/config.json` (`verification_commands`); do not restate the command list here or in `HANDOFF.md`. Run it through the cross-platform entry point:

```bash
python3 scripts/verify.py                 # full battery
python3 scripts/verify.py --list          # show commands without running
python3 scripts/verify.py --only frontend # substring filter (repeatable)
```

The runner executes each command through bash (macOS/Linux native; Git Bash on Windows) and exits non-zero on any failure.

TradingView tests require the pinned dependencies in `backend/requirements-tv.txt`; an environment missing them is an environment prerequisite failure, not a code regression.

Logic/data-pipeline changes also require:

- SPY 2026-07-17 assemble with `tang-v4-4-slope-4-4`, with non-empty 1m and 5m bars;
- Review and Backtest one-day regression for 2026-07-17 when browser conditions are available;
- SQLite integrity/foreign-key checks and the plan-specific data-safety matrix;
- complete `docs/daily-publish-runbook.md` only when a daily publish is separately authorized.
