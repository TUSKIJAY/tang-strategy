# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan`
- Lifecycle status: `Proposed`
- Current phase: `none`
- Phase state: `none`
- Next gate: `design-review`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Current proposed plan: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md` revision `v1-proposal-2026-07-21`.
- Source OPT batch: `docs/optimization/2026-07-21-review-trade-and-kline-session/` **OPT-003…006** (`promoted`).
- OPT-001/002 remain completed under `docs/exec-plans/completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md` (`717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`).
- Scope summary: remove Eligibility tools chrome (hard-default display); fix 5m TF first-paint viewport; group select span-fit + timeline legs UI; Data Market days progressive rail density.
- Next gate: independent `design-review` of exact `v1-proposal-2026-07-21`.
- **Does not authorize** activation, implementation, push, PR, merge, Pages, provider/broker, or remote action.
- Preserve untracked `output/local-acceptance/` and `output/playwright/*` evidence trees; do not stage.
- Coding Mode repository mutations include one task-scoped local commit by default. Stage only task-owned literal paths. Never use repository-wide, directory, glob, `-A`, `commit -a`, or implicit staging.

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
3. Use the simple lifecycle checker only for plan ownership, metadata, links, review verdict, and current-state agreement.
4. Next durable step is independent design review of the proposed plan — not activation or implementation.
5. Do not push or perform another remote action without a new explicit user request.
