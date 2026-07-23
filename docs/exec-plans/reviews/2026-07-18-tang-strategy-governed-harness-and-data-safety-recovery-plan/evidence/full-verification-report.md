# Full Verification Report

- Date: 2026-07-18
- Branch/HEAD: `codex/project-harness@8c6851d8f469e7a84471cd2900b00b3d9dcbdf07`
- Result: pass
- Scope: local repository and temporary runtimes only

## Repository And Governed Harness

| Check | Result |
| --- | --- |
| `python3 scripts/check-project-harness.py --root . --profile governed` | pass; 15 governed artifacts, config, workflow contract, and lifecycle links resolved |
| `validate_harness.py --target . --profile governed --min-score 90` | pass; `100/100`, 0 critical failures |
| `python3 scripts/check-startup-doc-budget.py` | pass; no archive or hard-limit trigger |
| `git diff --check` | pass |
| Active-doc stale wording and deleted-path consumer searches | pass; no active match |

The current shell does not provide `actionlint`. The dependency-free checker still parsed the configured workflow and verified the exact `Harness structure`, `Backend checks`, and `Frontend build` job display names and ordering. The Pages workflow was not changed or invoked.

## Backend And Data Safety

An isolated environment created from `backend/requirements-tv.txt` ran:

```bash
cd backend
PYTHONPATH=. /tmp/tang-validation-venv.91F98R/bin/python \
  -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=. /tmp/tang-validation-venv.91F98R/bin/python \
  -m compileall -q app scripts tests
```

Result: 19 tests passed in 8.123 seconds; compileall exited 0. The only emitted warnings were third-party calendar-library deprecations concerning generic NumPy timedelta behavior.

The 19 tests include 11 rebuild tests, 4 shared DB-safety tests, and the 4 pre-existing TradingView quality-gate tests. They cover empty/subset seed refusal, exact missing-key output, explicit intentional date loss, importer failure, corrupt candidate, empty/count-mismatched bars, strategy and teaching shrink, complete-superset promotion, source drift, consistent snapshot, ID-independent hashes, and post-validation rollback.

Post-implementation immutable database checks:

| Check | Result |
| --- | --- |
| DB SHA-256 | `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` |
| `PRAGMA integrity_check` | `ok` |
| `PRAGMA foreign_key_check` | 0 rows |
| Market days | 46 |
| 2026-05-15 | 960 1m / 192 5m |
| 2026-06-30 | 960 1m / 192 5m |
| 2026-07-01 | 960 1m / 192 5m |
| 2026-07-17 | 868 1m / 192 5m |

Recovery hashes, original 43-day preservation, overlay reachability, and the real six-day seed refusal against a temporary 46-day copy are recorded in the companion reports.

## Frontend And Real Browser Regression

```bash
cd frontend
npm run build
```

Result: pass; Vite transformed 1746 modules and produced the production bundle.

A real browser was driven against local FastAPI and Vite services. FastAPI used a SQLite backup at `/tmp/tang-browser-regression.fLlY4t/runtime.db`, not the tracked DB.

| Flow | Evidence | Result |
| --- | --- | --- |
| Login/dashboard | readonly login succeeded; dashboard showed 1 ticker, 46 market days, 11 strategies | pass |
| Review | selected SPY 2026-07-17; assembled status shown; 868 1m / 192 5m source; 4 entries; Tang trade overlay visible | pass |
| Review controls | switched K-line engine from 1m to 5m and used Step | pass |
| Backtest | ran latest 10 days; 43 total signals; SPY 2026-07-17 result had 4 signals and opened in the K-line engine | pass |
| Backtest controls | switched 1m to 5m and used Step | pass |

All exercised API requests returned HTTP 200. The only console error was a non-product `favicon.ico` 404.

## Documentation And Cleanup

- Startup chain now assigns stable facts to `INSTRUCTIONS.md`, lifecycle truth to `PROGRESS.md`, and only the latest resume gate to `HANDOFF.md`.
- Product roadmap and governed execution-plan roadmap are separate.
- Architecture and runbook describe the DB-first export and Vite SPA/static JSON path accurately.
- TV remains the default daily source; IB is fallback only after named TV failure gates.
- `docs/index.html`, `docs/assets/`, `docs/reviews/`, `docs/reference.html`, `docs/reviewed/`, and zero-byte `.codex` were deleted only after consumer and recovery proof. All remain recoverable from Git history.
- Provider stubs, frontend helpers/scanner/chart assets, browser tooling, tracked DB, seed model, and Pages publisher were retained.
- Excluded repository-audit findings are recorded in `docs/optimization/2026-07-18-01-repository-audit-followups/2026-07-18-01-repository-audit-followups.md` without execution authority.

## Cleanup And Authority Boundary

Generated `frontend/dist`, repository export output, browser CLI artifacts, and Python bytecode caches are removed before final status capture. The persistent adjacent DB lock file is intentionally retained and ignored because it is part of the shared-writer contract.

No fetch, broker connection, real rebuild, repository export, stage, commit, push, pull request, merge, Pages publish, branch protection, environment approval, or other remote mutation occurred.
