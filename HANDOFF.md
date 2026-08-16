# Handoff

This file is the latest resume point only. History belongs in `PROGRESS.md`, and older history in `docs/progress-archive/`. Do not add dated log entries here — `scripts/check-operating-modes.py` rejects them.

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan`
- Lifecycle status: `Active`
- Current phase: `phase-0`
- Phase state: `in-progress`
- Next gate: `phase-0-exit`
<!-- operating-modes-state:end -->

- Last updated: 2026-08-16
- Branch: `main` at `6f9a87c`, aligned with `origin/main`; unrelated untracked `output/` evidence is preserved.
- Active plan: [`2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan`](./docs/exec-plans/active/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan.md), revision `v3-active-amendment-2026-08-16`. Independent `review-003` approved the runtime-binding amendment. Local scanner/renderer-gate code is green; baseline evidence is frozen and the next gate is `phase-0-exit`.

## Open Threads

- Mobile Review/Static OPT batch `docs/optimization/2026-07-22-02-review-mobile-chart-canvas-and-floating-filter-dock/`: OPT-001…003 `recorded`, self-contained `mock.html` passed coarse-pointer Playwright acceptance, and a read-only Touch-contract Gap Evidence subsection records that the touch contract has no existing implementation to extend. No proposed plan, no implementation authority. Next gate: none unless the user explicitly requests promotion.
- Blocked on the user: two mock design decisions gate any engine scoping — whether to remove the header/dock ticker+date duplication (needs two Scope Lock rows amended), and whether trade markers leave the candle up/down palette (`direction-owned color` is a hard lock).
- Recorded, not fixed: eight `with connect()` API handlers in `backend/app/main.py` still rely on GC to close the SQLite handle.
- Recorded, not fixed: the `HANDOFF.md` dated-entry check is a shape heuristic; undated history prose still passes it.
- Recorded, not fixed: `frontend/src/kline/UnifiedKlineEngine.jsx`'s `annotations1m`/`annotations5m` default parameters (`= []`) get a new array identity every render on any page that omits those props (e.g. `TeachingPage.jsx`), re-triggering `loadData()` on unrelated re-renders. Pre-existing; does not affect Review/Static, which pass stable `useMemo`-derived annotation props. Diagnosed during the full-day viewport plan's acceptance work.
- Recorded, not fixed: several `output/playwright/*` run directories from already-`Completed` plans (`date-rail-qty-20260722023705`, `review-workspaces-phase3/4/5-20260720`, `trade-panel-polish-20260721`, `trade-points-marker-labels-20260721`) were left on disk past their plan's closure, though `docs/operating-modes.md` §8 says a closed plan's cited-run screenshots should be deleted at `Completed`. Untracked/gitignored, no repository-state risk; left alone this session to avoid touching other plans' artifacts.

## Verification Baseline

- `python scripts/verify.py` — runs the full battery from `.harness/config.json` (`verification_commands` is the only command list).
- Last full battery: 11/11 on 2026-07-23, including backend 78/78 and frontend `test:trade-records` 69/69. Frontend `test:trade-records` re-confirmed 69/69 on 2026-07-30 as part of the full-day viewport plan closeout.

## Resume Rules

1. Re-run startup Git status. Untracked `output/` trees are preserved only while their plan is open; closed plans' runs are deleted per `docs/operating-modes.md` §8.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Review exact revision `v2-proposed-2026-08-16`; after a matching `approve`, the current user instruction authorizes activation and execution without another confirmation.
4. Push/Pages/existing-transaction recovery are explicitly authorized for this hotfix; duplicate Discord delivery, cron changes, data reruns, and gate weakening are not.
