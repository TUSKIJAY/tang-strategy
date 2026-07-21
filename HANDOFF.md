# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan`
- Lifecycle status: `Active`
- Current phase: `phase-0`
- Phase state: `not-started`
- Next gate: `phase-0-start`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Active plan: `docs/exec-plans/active/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md` revision `v2-review-foldback-2026-07-21`.
- Matching design approval: `review-002: approve/high`.
- Activation evidence: `user-instruction:2026-07-21-activate-sidebar-spacing-and-kline-selection-band-plan`.
- Parked at phase-0 not-started; next gate `phase-0-start`.
- Scope locks: Review+Static parity; ≈20px gaps + captions; Traders-row dedupe; Download removed (not relocated) on Review/Static; cancel blue group/event selection paint; keep fitRange; markers unchanged.
- Preserve untracked `output/` trees; do not stage.
- No push/PR/merge/Pages/provider/broker without explicit user request.

## Latest Completed Work

- Lifecycle activation of sidebar spacing + selection-band plan (docs only).
- Design review loop: `review-001 revise` → v2 foldback → `review-002 approve`.
- Trade Tools / Group Span / Viewport / Data Rail product commit: `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`.

## Verification Baseline

- Activation package: plan only under `active/`; operating-modes + harness green; no product code mutation.
- Prior product baseline (unchanged): `cd frontend && npm run test:trade-records`; builds; harness auto.

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Plan is **Active** but Phase 0 is **not started**. Starting Phase 0 / implementation requires a separate explicit user execute instruction.
4. No remote actions without explicit user request.
