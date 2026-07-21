# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan`
- Lifecycle status: `Proposed`
- Current phase: `none`
- Phase state: `none`
- Next gate: `activation-recording`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Current Proposed plan: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md` revision `v2-review-foldback-2026-07-21`; `review-002: approve/high`.
- Reviews: `review-001: revise/high` on v1 (append-only) → `review-002: approve/high` on exact v2.
- Next gate: explicit user instruction to move the approved Proposed plan to Active (`activation-recording`). No activation or implementation authority yet.
- V2 foldbacks locked: atomic registry + candidate SQLite projection for `vordin → vordinkkk`; pure cross-leg card time-range helper + Node cases; `marker_label` + tooltip `title` both display-name + BUY/SELL with four-action fail-closed map.
- Promoted OPT scope: session OPT-001 (cards points-only) + OPT-002 (BUY/SELL + `vordinkkk`); OPT-003…006 remain recorded-only.
- **Optimization record mode remains open** for non-promoted items under `docs/optimization/`.
- Session batch: `docs/optimization/2026-07-21-review-trade-and-kline-session/`; named promotion source: `.../2026-07-21-trade-points-and-kline-marker-labels/`.
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
