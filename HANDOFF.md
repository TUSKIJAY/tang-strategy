# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan`
- Lifecycle status: `Active`
- Current phase: `phase-0`
- Phase state: `not-started`
- Next gate: `phase-0-start`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Active plan: `docs/exec-plans/active/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md` revision `v3-review-foldback-2026-07-21`.
- Matching design approval: `review-003: approve/high`.
- Activation: `user-instruction:2026-07-21-activate-trade-tools-group-span-viewport-data-rail-plan`.
- State: `phase-0:not-started`; next gate `phase-0-start`.
- Scope: session OPT-003…006 (Eligibility removal, group span+timeline, 5m first-paint, Data rail density).
- **This activation does not start Phase 0** and does **not** authorize implementation, content/DB writes, push, PR, merge, Pages, provider/broker, or remote action.
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
3. Active plan is parked at `phase-0-start`; do not begin Phase 0 without a separate explicit implementation-start / full-execution instruction.
4. No remote actions without explicit user request.
