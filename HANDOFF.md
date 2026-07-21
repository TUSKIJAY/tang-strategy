# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan`
- Lifecycle status: `Proposed`
- Current phase: `none`
- Phase state: `none`
- Next gate: `plan-revision`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Current proposed plan: `docs/exec-plans/proposed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md` revision `v1-proposal-2026-07-21`.
- Latest design review: `docs/exec-plans/reviews/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan/review-001.md` — `revise/high`, one P1 finding.
- Mock locks frozen in plan: ≈20px gaps + captions; Traders-row dedupe; Download **removed** (not relocated) on Review/Static; blue band cancel (group + event paint); keep fitRange; markers unchanged; Review+Static parity.
- Required foldback: freeze the exact tracked browser runner path or replacement; remove its stale blue-highlight expectations; add independent group/event fit oracles and measured Review/Static layout assertions.
- Next gate: plan-author foldback to a new stable revision, then independent design review of that exact revision.
- Preserve untracked `output/` trees; do not stage.
- No push/PR/merge/Pages/provider/broker without explicit user request.

## Latest Completed Work

- OPT record closeout: sidebar spacing + K-line selection band (record-only + mock).
- Trade Tools / Group Span / Viewport / Data Rail product commit: `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`.
- Trade Points And K-line Marker Labels product commit: `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`.
- Trade Panel Visual Polish product commit: `35a007efbd9db2a99967fb007adff2415f243e0b`.

## Verification Baseline

- Proposal package: plan metadata, proposed/reviews indexes, roadmap, OPT back-links, matching state blocks; `python scripts/check-operating-modes.py --root .`.
- Prior product baseline (unchanged): `cd frontend && npm run test:trade-records`; builds; harness auto.

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Current plan is **Proposed** only. `review-001` requires plan revision before another independent design review.
4. This review does not authorize activation or Phase 0 implementation.
5. No remote actions without explicit user request.
