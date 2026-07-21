# Review 002 — Tang Strategy Trade Points And K-line Marker Labels

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-points-kline-labels-r2`
- Plan author ID: `grok-plan-author-2026-07-21-trade-points-kline-labels`
- Independence declaration: `attested`
- Evidence method: `Independent read-only inspection of exact plan SHA-256 5bf605e26b90b62c07b902dbc844d58df6f0a5e6e146b4924303943c9d212c34 at HEAD bb8d204bf1d747938fdba2760e6c62e48015c829; v1 review-001 and v1-to-v2 diff; startup, operating-mode, and harness contracts; canonical registry and tracked SQLite state; admin registry write, atomic content rollback, candidate projection, compare-and-swap promotion, integrity/FK validation, K-line tooltip, action schema, frontend consumers, test carriers, source OPTs, and evidence hashes. No implementation, content/DB write, provider/broker, push, publication, or remote action was performed.`
- Verdict: approve
- Confidence: high

## Scope Checked

- Exact closure of all three `review-001` findings in the v2 plan body, manifest, success criteria, phases, and carrier matrix
- Canonical registry → candidate SQLite projection and failure-coherence contract
- Cross-leg card time-range semantics and executable Node proof
- Marker label, tooltip title, action mapping, grouping, display-name fallback, and fail-closed behavior
- Review/Static/Admin/editor surfaces, frozen OPT boundaries, lifecycle gates, and authority separation

## Findings

None.

## Review-001 Closure Verification

1. **Canonical registry and SQLite projection — closed.** V2 no longer permits a JSON-only rename. It adds both `content/traders/index.json` and `data/sqlite/tang_strategy_live_extended.db` to the exact manifest and freezes the existing `handle_trader_registry_admin_write(..., after_replace=_sync_trade_projection)` route. Current code validates the full registry/trade repository, rolls canonical content back when the follow-up fails, snapshots and candidate-projects the DB, validates integrity/FK, rejects live-DB drift before promotion, and restores the verified backup if post-promotion validation fails. V2 separately requires both JSON and SQLite/view proof for `vordin → vordinkkk`, unchanged day IDs, and preservation of non-target facts.
2. **Card time-range behavior — closed.** V2 freezes one pure helper over every complete `occurred_at`, chronological min/max independent of array order, and exact zero/one/two-or-more rendering. `N-Card-time-range` must cover multi-leg, deliberately out-of-order, and incomplete-time cases; `N-Card-source` is correctly limited to negative outcome/fees and helper-consumption assertions.
3. **All user-visible annotation text and action fallback — closed.** V2 governs both canvas `marker_label` and hover `title`, explicitly maps all four schema actions, omits missing/unknown actions, separates BUY/SELL at the same bar, preserves same-side `×N`, and requires display-name fallback plus absence of raw `vordin`/CALL/PUT from user-visible text. The Node carriers match the pure-function boundary, while V2 preserves direction-owned shape/color fields.

## Verified Strengths

- The v2 closure map is faithful to append-only `review-001`; the prior verdict is not reused as approval for the new revision.
- Current canonical JSON, SQLite `traders`, and `v_trade_group_performance` all still resolve `vordin` to `沃德哥`; SQLite integrity is `ok` with zero foreign-key failures. This is the correct untouched pre-implementation baseline.
- `_atomic_replace_text` restores the original canonical registry when the projection callback fails. `_sync_trade_projection` operates on a consistent snapshot/candidate and `promote_candidate` performs token/identity drift checks plus backup restoration on failed post-validation.
- Product scope remains limited to OPT-001/002. Eligibility removal, 5m viewport, group span/timeline, Data rail, day-file rewrites, provider/broker, Pages, and remote actions remain excluded.
- QQQ `2026-07-17`, the shared consumers, K-line tooltip `title` rendering, exact action enum, and all four evidence hashes remain valid.
- Baseline checks passed: direct operating-mode checker, 12/12 lifecycle fixtures, governed/auto harness, and `git diff --check`.

## Implementation Note

The existing projection route’s built-in post-validation checks SQLite integrity/FK, live-DB drift, and projected-table count agreement. It does not by itself prove arbitrary before/after logical equality for every non-target fact. Therefore the mandatory v2 `N-Registry-dual` receipt must independently compare the frozen pre/post non-target logical state and show that the only intended registry/database fact change is `vordin.display_name: 沃德哥 → vordinkkk`. This is already required by §§2.2, 2.4, 3.3, and Phase 1, so it is an implementation obligation rather than a plan-revision finding.

## Verdict Rationale

V2 closes the only data-coherence blocker and both executable-contract findings without expanding into adjacent OPT work. The objective, manifest, safety path, pure verification carriers, visual fixtures, lifecycle stages, and authority boundaries now form a coherent implementation contract. Approval applies only to exact revision `v2-review-foldback-2026-07-21`; it does not activate or implement the plan and grants no content/DB write, provider/broker, publication, push, or remote authority. The next gate is explicit lifecycle activation by the user.
