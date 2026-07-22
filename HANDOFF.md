# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `none`
- Lifecycle status: `None`
- Current phase: `none`
- Phase state: `none`
- Next gate: `none`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-22
- Branch: `codex/project-harness`
- Latest OPT intake: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/` OPT-001…003 `recorded` (Scope Lock foldback 2026-07-22).
- Design mock: `docs/optimization/2026-07-22-review-date-rail-and-trade-quantity-session/mock.html` — shape/legend polish deferred to a separate agent; OPT Scope Lock is authoritative.
- Last completed plan: `docs/exec-plans/completed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md` revision `v2-review-foldback-2026-07-21` (product `5f36d29a`; `implementation-review-001: accept/high`; next gate `closed`).
- Preserve untracked `output/` trees; do not stage.
- No push/PR/merge/Pages/provider/broker without explicit user request.
- No proposed plan / activation / implementation for the 2026-07-22 OPT batch unless the user explicitly requests promotion.

## Latest Completed Work

- 2026-07-22: OPT session record foldback (Scope Lock + index + state) for date-rail order + trade quantity OPTs; mock legend polish left to separate agent.
- Sidebar Spacing + Selection Band product commit: `5f36d29a44fb12aee2319ae147303cc970d83193`.
- Trade Tools / Group Span / Viewport / Data Rail product commit: `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`.

## Verification Baseline

- `cd frontend && npm run test:trade-records` (64/64)
- `python scripts/check-operating-modes.py --root .`
- `python -m unittest scripts.tests.test_operating_modes`
- `python scripts/check-project-harness.py --root . --profile auto`

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. No active plan. New governed work requires its own OPT/plan lifecycle from the start.
4. For the 2026-07-22 quantity/date-rail OPTs: promote only on explicit user request; do not implement from the record alone.
5. No remote actions without explicit user request.
