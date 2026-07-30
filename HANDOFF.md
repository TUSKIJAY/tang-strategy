# Handoff

This file is the latest resume point only. History belongs in `PROGRESS.md`, and older history in `docs/progress-archive/`. Do not add dated log entries here — `scripts/check-operating-modes.py` rejects them.

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-30-tang-strategy-default-full-day-kline-viewport-plan`
- Lifecycle status: `Active`
- Current phase: `phase-0`
- Phase state: `not-started`
- Next gate: `phase-0-start`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-30
- Branch: `main`
- Active plan: `docs/exec-plans/active/2026-07-30-tang-strategy-default-full-day-kline-viewport-plan.md`, revision `v1-active-2026-07-30`, direct user activation for a bounded simple change, `phase-0:not-started`, next gate `phase-0-start`
- Source OPT: `docs/optimization/2026-07-30-01-review-default-full-day-kline-viewport/` OPT-001 `active-plan`
- The user explicitly skipped a separate design-review round and intends another agent to execute. This activation did not start Phase 0.

## Open Threads

- Review/Static full-day viewport plan is Active at exact revision `v1-active-2026-07-30`, `phase-0:not-started`. Scope is limited to truthful full-day first paint and Overview for 1m/5m, with manual controls and Teaching replay preserved. Next gate: a later explicit execution instruction opens `phase-0-start`.
- Mobile Review/Static OPT batch `docs/optimization/2026-07-22-02-review-mobile-chart-canvas-and-floating-filter-dock/`: OPT-001…003 `recorded`, self-contained `mock.html` passed coarse-pointer Playwright acceptance, and a read-only Touch-contract Gap Evidence subsection records that the touch contract has no existing implementation to extend. No proposed plan, no implementation authority. Next gate: none unless the user explicitly requests promotion.
- Blocked on the user: two mock design decisions gate any engine scoping — whether to remove the header/dock ticker+date duplication (needs two Scope Lock rows amended), and whether trade markers leave the candle up/down palette (`direction-owned color` is a hard lock).
- Recorded, not fixed: eight `with connect()` API handlers in `backend/app/main.py` still rely on GC to close the SQLite handle.
- Recorded, not fixed: the `HANDOFF.md` dated-entry check is a shape heuristic; undated history prose still passes it.

## Verification Baseline

- `python scripts/verify.py` — runs the full battery from `.harness/config.json` (`verification_commands` is the only command list).
- Last full battery: 11/11 on 2026-07-23, including backend 78/78 and frontend `test:trade-records` 69/69.

## Resume Rules

1. Re-run startup Git status. Untracked `output/` trees are preserved only while their plan is open; closed plans' runs are deleted per `docs/operating-modes.md` §8.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Current plan is **Active** at `phase-0:not-started`; next gate `phase-0-start`. Do not infer implementation start from activation alone.
4. No remote actions without explicit user request.
