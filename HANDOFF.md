# Handoff

## Current Snapshot

<!-- operating-modes-state:start -->
- Current plan: `2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan`
- Lifecycle status: `Proposed`
- Current phase: `none`
- Phase state: `none`
- Next gate: `design-review`
<!-- operating-modes-state:end -->

- Last updated: 2026-07-21
- Branch: `codex/project-harness`
- Current proposed plan: `docs/exec-plans/proposed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md` revision `v2-review-foldback-2026-07-21`.
- Latest design review: `review-001` — `revise/high` on v1 (folded into v2).
- V2 freezes replacement tracked Playwright runner + independent span/event oracles + empty-highlight asserts.
- Next gate: independent codex `design-review` of exact v2.
- Preserve untracked `output/` trees; do not stage.
- No push/PR/merge/Pages/provider/broker without explicit user request.

## Latest Completed Work

- OPT record closeout: sidebar spacing + K-line selection band (record-only + mock).
- Trade Tools / Group Span / Viewport / Data Rail product commit: `a76b83680e80ab8bf7a857fa776146a2aa4f24aa`.
- Trade Points And K-line Marker Labels product commit: `717ac8ae9bf5faf00ec6dff3b81d04c51c86b145`.
- Trade Panel Visual Polish product commit: `35a007efbd9db2a99967fb007adff2415f243e0b`.

## Verification Baseline

- Proposal/review package: operating-modes + harness on lifecycle docs.
- Prior product baseline (unchanged): `cd frontend && npm run test:trade-records`; builds; harness auto.

## Resume Rules

1. Re-run startup Git status and preserve untracked `output/` trees.
2. Read `AGENTS.md`, `INSTRUCTIONS.md`, `PROGRESS.md`, and this file.
3. Current plan is **Proposed** at revision `v2-review-foldback-2026-07-21`. Independent design review of **exact v2** required; prior `review-001` cannot approve v2.
4. This session’s user instruction authorizes post-approve activation; it does not start Phase 0 implementation.
5. No remote actions without explicit user request.
