# Tang Strategy Default Full-Day K-Line Viewport

- Lifecycle schema: `operating-modes-v1`
- Status: Active
- Plan slug: `2026-07-30-tang-strategy-default-full-day-kline-viewport-plan`
- Revision: `v1-active-2026-07-30`
- Plan author ID: `codex-root`
- Design reviews: none
- Latest design verdict: none
- Review independence: none
- Activation evidence: `user-instruction:2026-07-30-direct-activate-default-full-day-kline-viewport-plan`
- Current phase: phase-0
- Phase state: not-started
- Phase entry gate: none
- Next gate: `phase-0-start`
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Owner: another agent after explicit execution authority
- Created: 2026-07-30
- Scope authority: lifecycle activation only; implementation has not started
- Local commit: task-scoped default; does not authorize implementation, push, or remote action

## 1. Context

Source OPT: [2026-07-30-01 Review Default Full-Day K-Line Viewport](../../optimization/2026-07-30-01-review-default-full-day-kline-viewport/2026-07-30-01-review-default-full-day-kline-viewport.md).

- [Figure 1](../../optimization/2026-07-30-01-review-default-full-day-kline-viewport/screenshots/current-default-partial-day-kline.png) shows the current partial-day tail window.
- [Figure 2](../../optimization/2026-07-30-01-review-default-full-day-kline-viewport/screenshots/target-default-full-day-kline.png) shows the requested full-day default.
- User runtime confirmation: clicking the current `Overview` button also returns to Figure 1.
- `frontend/src/kline/kline-engine.js:803-807` limits the default window to at most 96×1m or 72×5m bars.
- `overview()` at `frontend/src/kline/kline-engine.js:2666-2677` resets to that same tail window even though the button promises “Fit the full day”.

The user classified this as a simple bounded requirement and explicitly requested direct activation without a separate design-review round. This plan therefore records no design verdict and remains `phase-0:not-started`.

## 2. Required Outcome

### In scope

1. Review and Static Review open with every available bar from the displayed day/session visible.
2. `Overview` restores every available bar after the user zooms, drags, or focuses a smaller range.
3. The behavior works for both 1m and 5m.
4. Bar counts come from the payload. Normal RTH may be 390×1m / 78×5m; early closes or other valid session lengths use their actual counts.
5. Existing manual zoom, pan, Follow, playback, annotations, trade/signal `fitRange`, and price/volume scaling continue to work.
6. Teaching replay keeps its reveal-cutoff and follow behavior.

### Out of scope

- Backend, API, SQLite, market data, session filtering, strategies, trades, annotations, content, provider/broker, Pages, publication, or remote actions.
- Mobile redesign, marker-density work, new chart controls, or viewport persistence between browser sessions.

## 3. Implementation

Keep the change shared and small:

1. Add one engine-owned “fit all available bars” operation in `frontend/src/kline/kline-engine.js`.
2. Make `overview()` use that operation instead of `ViewportManager.reset()`.
3. Add an explicit Review/Static initial-viewport option in `frontend/src/features/review/engineOptions.js`; default behavior for other engine consumers stays unchanged.
4. On a Review/Static payload load, apply the same fit-all operation after the real bar lengths are known.
5. Do not implement the behavior with page-local repeated zoom clicks or hard-coded 390/78 values.
6. Change `frontend/src/kline/UnifiedKlineEngine.jsx` only if needed to carry the initial-viewport option cleanly; do not fork Review and Static page logic.

Expected product paths:

- `frontend/src/kline/kline-engine.js`
- `frontend/src/features/review/engineOptions.js`
- `frontend/src/kline/UnifiedKlineEngine.jsx` only if required
- one focused test or browser-acceptance script

Unrelated dirty path to preserve and never stage:

- `data/sqlite/tang_strategy_live_extended.db`

## 4. Acceptance

Use the existing `getViewportDebug()` seam in a real browser check.

| Check | Pass condition |
| --- | --- |
| Review 1m first paint | A normal 390-bar payload reports `start=0`, `end=389`, `count=390` without manual zoom. |
| Review 5m | A normal 78-bar payload reports `start=0`, `end=77`, `count=78`. |
| Overview | After a narrower zoom or `fitRange`, clicking `Overview` returns to `start=0`, `end=totalBars-1`, `count=totalBars`. |
| Static parity | Static Review passes the same first-paint and Overview assertions. |
| Variable length | A valid non-standard payload fits its actual first and final bar; the test derives totals from payload length. |
| Manual controls | Zoom/pan/focus can still produce a narrower viewport before Overview is clicked. |
| Teaching | Reveal cutoff still hides future bars and step/follow behavior remains bounded. |
| Data safety | Tracked SQLite hash is unchanged. |

Verification:

- focused browser acceptance for the table above;
- `npm run test:trade-records`;
- normal frontend build;
- static-reviews frontend build;
- `python scripts/check-project-harness.py --root . --profile auto`;
- `git diff --check`.

## 5. Phases

### Phase 0 — Baseline

- Entry gate: a later explicit execution/full-responsibility instruction opens `phase-0-start`.
- Record HEAD and tracked DB hash.
- Capture current failing first-paint and Overview viewport values.
- Confirm the chosen fixture contains paired 1m/5m bars.
- Exit gate: `phase-0-exit`.

### Phase 1 — Implement And Verify

- Entry gate: `phase-0-exit`.
- Implement §3.
- Run every acceptance check in §4.
- Confirm no backend/data/DB paths changed.
- Exit gate: `phase-1-exit`.

### Phase 2 — Closeout

- Entry gate: `phase-1-exit`.
- Record implementation commit and acceptance evidence.
- Complete the repository's required implementation review/closeout path unless the executing user instruction explicitly authorizes the simpler bounded-change closeout.
- Move the plan to `completed/` and mark source OPT-001 `completed` only after verified implementation.
- Exit gate: `closed`.

## 6. Current Gate And Handoff

- Current state: Active, `phase-0:not-started`.
- Next gate: `phase-0-start`.
- Design review: explicitly skipped by direct user instruction; no verdict is claimed.
- Implementation has not started.
- The executing agent must receive an explicit start/execute instruction before changing product files.
- No push, PR, merge, Pages, provider/broker, DB/content mutation, or remote authority exists.

Lifecycle paths owned by this activation:

- `docs/exec-plans/active/2026-07-30-tang-strategy-default-full-day-kline-viewport-plan.md`
- `docs/exec-plans/active/index.md`
- `docs/exec-plans/roadmap.md`
- `docs/exec-plans/reviews/index.md`
- `docs/exec-plans/reviews/2026-07-30-tang-strategy-default-full-day-kline-viewport-plan/.gitkeep`
- source OPT batch and `docs/optimization/index.md`
- `PROGRESS.md`
- `HANDOFF.md`

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for lifecycle transitions and scoped commits.
