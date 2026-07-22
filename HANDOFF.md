# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan`
- Lifecycle status: `Proposed`
- Current phase: `none`
- Phase state: `none`
- Next gate: `design-review`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-22
- Branch: `codex/project-harness`
- Proposed plan: `docs/exec-plans/proposed/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md`
- Revision: `v1-proposal-2026-07-22`
- Source OPT: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/` OPT-001…003 `promoted-to-proposed`
- Proposal baseline HEAD: `f40887100a7b4f832c59da32ac1607dc47b05854`
- Design mock: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/mock.html`
- Next gate: independent `design-review` of exact revision `v1-proposal-2026-07-22`
- No activation, implementation, content/DB mutation, push, PR, merge, Pages, provider/broker without explicit user request
- Preserve untracked `output/` trees; do not stage

## Latest Completed Work

- 2026-07-22: Proposed plan for DateRail ascending + marker `*QTY` + close-qty derivation (OPT-001…003).
- 2026-07-22: OPT Scope Lock foldback + mock direction-legend fix `f408871`.
- Sidebar Spacing + Selection Band product commit: `5f36d29a44fb12aee2319ae147303cc970d83193`.

## Verification Baseline

- `cd frontend && npm run test:trade-records` (64/64 at last product closeout)
- `python scripts/check-operating-modes.py --root .`
- `python -m unittest scripts.tests.test_operating_modes`
- `python scripts/check-project-harness.py --root . --profile auto`

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Current plan is **Proposed** only. Next gate is independent design review — not activation, not implementation.
4. Activation requires matching design `approve` **and** a separate explicit user activation instruction.
5. No remote actions without explicit user request.
