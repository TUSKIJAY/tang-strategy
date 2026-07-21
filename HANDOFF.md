# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `none`
- Lifecycle status: `None`
- Current phase: `none`
- Phase state: `none`
- Next gate: `none`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- No active or proposed plan.
- **Optimization record mode is open** (user enabled). Record-only under `docs/optimization/`.
- Latest recorded batches (no implementation authority):
  - `docs/optimization/2026-07-21-trade-card-simplify-points-only/` — cards: drop $ / %; keep time + price points.
  - `docs/optimization/2026-07-21-kline-marker-action-and-trader-nickname/` — markers: BUY/SELL text; UI nickname `vordinkkk` → `trader_id: vordin`.
- Coding Mode repository mutations now include one task-scoped local commit by default. The only no-commit cases are an explicit user opt-out, draft/failed/incomplete work, or inability to separate task paths safely from unrelated dirty changes.
- Stage only task-owned literal paths. Never use repository-wide, directory, glob, `-A`, `commit -a`, or implicit staging.
- A local commit never grants push, PR, merge, Pages, publication, provider/broker, hosted verification, or another remote action.
- Keep small work small: adjacent issues are recorded, not automatically expanded into new plans, reviewers, commit protocols, state machines, or remediation loops.

## Latest Completed Work

- Trade Panel Visual Polish product commit: `35a007efbd9db2a99967fb007adff2415f243e0b`.
- Deterministic browser acceptance script: `680981f`.
- Lifecycle closeout: `77f4011`; implementation review `accept/high`; next gate closed.
- Evidence remains untracked under `output/playwright/trade-panel-polish-20260721/`; local acceptance DB output also remains untracked and must not be swept into another commit.

## Verification Baseline

- `python scripts/check-operating-modes.py --root .`
- `python -m unittest scripts.tests.test_operating_modes`
- `python scripts/check-project-harness.py --root . --profile auto`
- `git diff --check`

## Resume Rules

1. Re-run startup Git status and preserve the untracked `output/` evidence.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Use the simple lifecycle checker only for plan ownership, metadata, links, review verdict, and current-state agreement.
4. Do not push or perform another remote action without a new explicit user request.
