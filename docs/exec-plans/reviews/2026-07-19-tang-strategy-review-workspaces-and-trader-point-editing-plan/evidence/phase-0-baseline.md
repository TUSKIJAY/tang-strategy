# Phase 0 — Baseline Evidence Capture

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Captured at: `phase-0:in-progress`, 2026-07-19
- Implementation start: `user-instruction:2026-07-19-start-review-workspaces-implementation` (goal-mode objective attaching the active plan) opened `phase-0-start`.

## 1. Startup contract and worktree

- Repository root: `/Users/neowang/Code/tang-strategy-github`; branch `codex/project-harness`, HEAD `d73502139e6d25d5e050c376e90289c70ef23ecc`, upstream `origin/codex/project-harness` (ahead 8 at capture).
- Startup chain read in order: `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, `HANDOFF.md`; routing per `docs/operating-modes.md`; verification baseline per `.harness/config.json`.
- Unrelated worktree paths preserved: untracked `output/` (pre-existing user artifacts, including `output/playwright/...`) is left untouched except the new `output/phase-0-baseline-20260719/` evidence subdirectory created by this phase.
- Phase 0 worktree changes at capture: lifecycle state edits (`HANDOFF.md`, `PROGRESS.md`, active plan, active index), new evidence directory, new `frontend/src/features/review/reviewWorkspace.fixtures.js` (frozen Add).

## 2. Tracked DB baseline (read-only checks)

- Path: `data/sqlite/tang_strategy_live_extended.db`; SHA-256 `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` (matches the plan's recorded baseline).
- `PRAGMA integrity_check` = `ok`; `PRAGMA foreign_key_check` = 0 rows; 16 tables.
- Counts: 49 logical `market_days` (46 SPY 2026-05-12…2026-07-17 + QQQ 2026-07-10/14/17, all `extended`); 52 `market_datasets`; 11 strategies (all active); trade projection 2 traders / 33 groups (27 SPY, 6 QQQ; 30 verified, 3 pending) / 33 legs / 46 events / 7 outcomes / 5 note contexts.

## 3. Boundary hashes (SHA-256)

| File | SHA-256 |
| --- | --- |
| `.github/workflows/publish-static-reviews.yml` | `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8` |
| `.github/workflows/project-harness.yml` | `31de168a898380ac5f44808475483f78e1040abed4ae1f0d0e4023d37e3d0dac` |
| `backend/scripts/export_static_reviews.py` | `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996` |
| `docs/daily-publish-runbook.md` | `2010e73b65483009a2273a380faa3ae081f0bb725089013effe7dd755d0f230f` |
| `AGENTS.md` | `53af582e499654ec589e1d9fecc75661e3fe900dca9991690a8b8e5324c79c53` |
| `frontend/src/pages/StaticReviewsApp.jsx` | `b0343385e69384d47ce0ae3da3b1827442afc595efa6da9f26d5a0db612c84f4` |
| `frontend/vite.config.js` | `4183874a1780da31e7bff5d420e6b1243e34e07853e6a75c4ab23b65eb7dfcc0` |
| `frontend/package.json` | `e44cfdead784a34a166cc380d1535c24e2ac280f19246f20d5600f63c41bb695` |

## 4. Existing static hash behavior (recorded)

- Day slugs are `<ticker>-<trade_date>-<session_mode>` lowercased with `_`→`-` (`export_static_reviews.py:18-21`), e.g. `spy-2026-07-17-extended`; each manifest `reviews[]` entry carries `slug`, `file`, `ticker`, `trade_date`, `session_mode`, `title`, `bars_1m`, `bars_5m` (`:183-201`).
- `StaticReviewsApp.jsx` treats the hash as an opaque slug: strip `^#\/?` (`:192`, `:236`), exact-match `manifest.reviews[].slug` (`:241`), fall back to the first manifest review, and write the fallback slug back to the hash (`:224-227`). Ticker/date/session are never parsed out of the hash today; they come from the matched manifest entry.
- Static export admits all DB market days but only `active` + `verified` trade records (`export_static_reviews.py:78-85`), so pending-only days (QQQ 2026-07-14) export the market day with zero trader groups.
- Publisher: `.github/workflows/publish-static-reviews.yml` runs on every `main` push + dispatch; export → `VITE_STATIC_REVIEWS=true npm run build:static-reviews` → force-push `gh-pages`. Static build differs from normal build only via `--base=./` and the entry swap in `frontend/src/main.jsx:63`; both emit to `frontend/dist`.
- Frontend helper `reviewHashRoute` (`tradeRecords.js:110-112`) already formats `#<ticker>-<date>-<session>` but is referenced only by tests at freeze time.

## 5. Source control-ownership inventory

Recorded in `phase-0-manifest.md` §5 (ownership table with `file:line` duplicate evidence) and §7 (baseline notes). Headline freeze-time facts: no selected-ticker state exists anywhere; every day list (Review footer select `ReviewPage.jsx:472-474`, Dashboard `:65`, Teaching `:87-89`, Static `:455-461`) is a flat mixed SPY/QQQ enumeration; chart-generic duplicates exist on Review (`:496-503`), Static (`:542-547`), Backtest (`:123-126`), and Teaching (`:90-93`) pages on top of the engine toolbar (`kline-engine.js:1020-1045`); no visible engine fit/overview control exists (`overview()` is wrapper-only, `UnifiedKlineEngine.jsx:95-103`); `Rescan` and `Backtest` currently call the same handler (`ReviewPage.jsx:362-366,501-502`); admin trader editing is raw-JSON textareas (`AdminTradersPage.jsx:67-76`) behind an admin-only icon nav entry (`Layout.jsx:45-50`).

## 6. Interactive/static baseline screenshots

Captured against a temporary DB copy of the tracked DB (hash-verified unchanged after capture) at viewport `1672 x 941` into `output/phase-0-baseline-20260719/` (untracked local output; `SHA256SUMS.txt` alongside the captures). Browser console logs for both capture runs recorded zero errors (`interactive/console-log.json`, `static/console-log.json`, both `[]`). Interactive captures were taken with an admin session on the alternate-port acceptance stack; static captures used a temporary export + `VITE_STATIC_REVIEWS=true` build served locally (no publish step).

| Capture | SHA-256 (first 16) | Baseline behavior shown |
| --- | --- | --- |
| `interactive/01-login.png` | `88f74a9b9aa1d2fe` | Login gate |
| `interactive/02-data.png` | `50a343c8079ad041` | Data page first-20 flat mixed SPY/QQQ day list |
| `interactive/03-review-default.png` | `f00f148ddb9f91ea` | Review default selection is QQQ 2026-07-17 (newest mixed day); duplicate bottom control bar; TraderFilters Ticker/Date selects |
| `interactive/04-review-qqq-2026-07-17.png` | `f00f148ddb9f91ea` | Byte-identical to `03` — proves the interactive default resolves to QQQ 2026-07-17 |
| `interactive/05-review-qqq-2026-07-14.png` | `e25f70611fbe074b` | QQQ 2026-07-14 (pending-record day) interactive view |
| `interactive/06-admin-traders.png` | `e354c5541c0f4443` | Admin trader workspace: raw registry/daily JSON textareas (OPT-002 baseline) |
| `interactive/07-backtest.png` | `c8e111063bc50cd1` | Backtest page with page-level replay duplicates |
| `interactive/08-teaching.png` | `01cd96a3a0b67af3` | Teaching page with mixed day select |
| `static/01-static-default.png` | `e169ecbb8bb282f5` | Static default = QQQ 2026-07-17; flat mixed sidebar; duplicate footer controls; Tang checkbox rendered on a QQQ-only day (no availability rule) |
| `static/02-static-spy-2026-07-17.png` | `78850e0c43785b52` | Legacy hash `#spy-2026-07-17-extended` resolves |
| `static/03-static-qqq-2026-07-17.png` | `d50550094725f21e` | Legacy hash `#qqq-2026-07-17-extended` resolves |
| `static/04-static-qqq-2026-07-14.png` | `9b79f419c3dbd56b` | Pending-record day: market day renders with zero verified trader groups |
| `static/05-static-invalid-hash.png` | `d50550094725f21e` | Byte-identical to `03` — invalid hash `#spy-1999-01-01-extended` falls back to the first manifest review (QQQ 2026-07-17) |

## 7. Baseline verification classification

| Check | Result |
| --- | --- |
| `check-project-harness.py --profile governed` | pass (errors `[]`) |
| `check-project-harness.py --profile auto` | pass (errors `[]`) |
| `check-operating-modes.py --root .` | pass |
| `python3 -m unittest scripts.tests.test_operating_modes` | pass (146/146) |
| `check-startup-doc-budget.py` | pass |
| Backend unittest discover, system `python3` | environment prerequisite failure: TV tests require `backend/requirements-tv.txt` (`pandas_market_calendars` missing); not a code regression per `INSTRUCTIONS.md` |
| Backend unittest discover, pinned `backend/.venv/bin/python` | pass (76/76) |
| Backend `compileall` (system + venv) | pass |
| `npm run test:trade-records` | pass (11/11) |
| Fixture canonical day validated against real backend validator | pass: `FIXTURE_MULTI_TICKER_DAY` passes `validate_trade_day` with the live registry (3 groups / 1 context) and is round-trip stable under re-validation |
| `npm run build` | pass (Vite, 335.10 kB JS entry) |
| `VITE_STATIC_REVIEWS=true npm run build:static-reviews` | pass (Vite `--base=./`, 317.02 kB JS entry); a second static build also succeeded inside the screenshot capture flow against a temporary export of 49 days / 9 strategies |
| `git diff --check` | pass |
| Admin role/read-shape tests | not-run: the two admin canonical read routes do not exist until Phase 3; their contracts are frozen in `phase-0-contract-freeze.md` |
| SQLite read-only checks (integrity/FK/hash) | pass (§2) |
| Workflow/export exact hashes | pass (§3) |
| Interactive/static baseline screenshots | pass (§6): 13 captures, zero console errors, tracked DB SHA-256 re-verified unchanged after capture (`125fcc9d...02105b0`), static pending-day capture shows the neutral `No normalized trades for this filter` state, `frontend/dist` restored and `frontend/public/reviews` removed after the temporary static flow |

All Phase 0 checks are classified. The exit gate is met: the exact scope/evidence manifest is durable (`phase-0-manifest.md`), and the two frozen canonical read routes are implementable from existing loaders/validators without a DB/auth-role/write-route/publisher change (`phase-0-contract-freeze.md`).
