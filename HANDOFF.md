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
- Current proposed plan: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md` revision `v3-review-foldback-2026-07-21`.
- Prior design reviews: `review-001` revise@v1; `review-002` revise@v2 (append-only; cannot approve v3).
- V3 freezes: deterministic TF first-paint oracle + getViewportDebug; mandatory event-row steps in B-Group-span; exact host `data-market-days-rail` including month bar ≤420px; tracked Playwright runner path.
- Next gate: independent `design-review` of exact `v3-review-foldback-2026-07-21`.
- **Does not authorize** activation, implementation, push, PR, merge, Pages, provider/broker, or remote action.
- Preserve untracked `output/` evidence trees; do not stage.
- Stage only task-owned literal paths for lifecycle commits.

## Latest Completed Work

- Trade Points And K-line Marker Labels product commit: `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`.
- Trade Panel Visual Polish product commit: `35a007efbd9db2a99967fb007adff2415f243e0b`.

## Verification Baseline

- `python scripts/check-operating-modes.py --root .`
- `python -m unittest scripts.tests.test_operating_modes`
- `python scripts/check-project-harness.py --root . --profile auto`
- `git diff --check`

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Next durable step is independent design review of exact v3.
4. No remote actions without explicit user request.
