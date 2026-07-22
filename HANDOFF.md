# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan`
- Lifecycle status: `Active`
- Current phase: `phase-0`
- Phase state: `not-started`
- Next gate: `phase-0-start`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-22
- Branch: `codex/project-harness`
- Active plan: `docs/exec-plans/active/2026-07-22-tang-strategy-date-rail-ascending-and-trade-quantity-plan.md`
- Revision: `v2-review-foldback-2026-07-22`
- Design reviews: `review-001.md` → `revise/high` @ v1; `review-002.md` → `approve/high` @ v2
- Activation evidence: `user-instruction:2026-07-22-activate-date-rail-ascending-and-trade-quantity-plan`
- Phase: `phase-0` / `not-started`
- Next gate: `phase-0-start` — requires a **separate explicit implementation-start / execute instruction**
- Source OPT: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/` OPT-001…003 `promoted-to-proposed`
- Proposal baseline HEAD: `f40887100a7b4f832c59da32ac1607dc47b05854`
- Design mock: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/mock.html`
- Activation does **not** start Phase 0 or authorize product implementation, content/DB, push, PR, merge, Pages, provider/broker
- Preserve untracked `output/` trees; do not stage

## Latest Completed Work

- 2026-07-22: Lifecycle activation `proposed/` → `active/` at `phase-0:not-started` after matching design approve.
- 2026-07-22: Independent design `review-002: approve/high` on exact `v2-review-foldback-2026-07-22`.
- 2026-07-22: Folded review-001 P1 into `v2-review-foldback-2026-07-22` (qty completeness + same-bar marker rules).
- 2026-07-22: Independent design `review-001: revise/high` on v1 (qty completeness oracle + same-bar wording P1).
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
3. Current plan is **Active** at revision `v2-review-foldback-2026-07-22`, parked at `phase-0:not-started`. Next gate is `phase-0-start` — not product implementation yet.
4. Phase 0 / implementation requires a **separate explicit start/execute instruction** after this activation.
5. No remote actions without explicit user request.
