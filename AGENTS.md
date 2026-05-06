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
