# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan`
- Lifecycle status: `Proposed`
- Current phase: `none`
- Phase state: `none`
- Next gate: `plan-revision`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Current proposed plan: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md` revision `v2-review-foldback-2026-07-21`.
- Latest design review: `review-002.md` — `revise/high` on exact v2; three findings. `review-001.md` remains append-only v1 evidence.
- Source OPT batch: `docs/optimization/2026-07-21-review-trade-and-kline-session/` **OPT-003…006** (`promoted`).
- Review-002 verified closures: display-only canonicalize and blue band + fitRange-only group select. Remaining foldback: deterministic TF first-frame oracle; mandatory browser event-row focus; one exact Data host plus month-bar computed-layout proof.
- Next gate: `plan-revision`; do not activate or implement v2.
- **Does not authorize** activation, implementation, push, PR, merge, Pages, provider/broker, or remote action.
- Preserve untracked `output/local-acceptance/` and `output/playwright/*` evidence trees; do not stage.
- Coding Mode repository mutations include one task-scoped local commit by default. Stage only task-owned literal paths.

## Latest Completed Work

- Trade Points And K-line Marker Labels product commit: `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`; `implementation-review-001: accept/high`.
- Trade Panel Visual Polish product commit: `35a007efbd9db2a99967fb007adff2415f243e0b`.

## Verification Baseline

- `python scripts/check-operating-modes.py --root .`
- `python -m unittest scripts.tests.test_operating_modes`
- `python scripts/check-project-harness.py --root . --profile auto`
- `git diff --check`

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` evidence trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Next durable step is plan revision folding `review-002` into a later exact revision — not activation or implementation.
4. Do not push or perform another remote action without a new explicit user request.
