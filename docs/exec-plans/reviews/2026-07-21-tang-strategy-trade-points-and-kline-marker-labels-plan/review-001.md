# Review 001 — Tang Strategy Trade Points And K-line Marker Labels

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md`
- Review target revision: `v1-proposal-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-points-kline-labels-r1`
- Plan author ID: `grok-plan-author-2026-07-21-trade-points-kline-labels`
- Independence declaration: `attested`
- Evidence method: `Independent read-only inspection of exact plan SHA-256 0a30427c5222b38033f16f7cec9d00b23388b009a00cac56811453ac204f4659 at HEAD 2a5a9c788095040e7f3383544e5f20bae6a939f3; startup and operating-mode contracts; named and session OPT records; both live screenshots and locked mock hashes; current Review, Static, Admin, annotation-builder, K-line tooltip, registry, canonical-content, SQLite-projection, admin-write, static-export, schema, test, and harness carriers. No implementation, content/DB write, provider/broker, push, publication, or remote action was performed.`
- Verdict: revise
- Confidence: high

## Scope Checked

- User-promoted OPT-001/002 product decisions and exclusion of session OPT-003…006
- Shared `TraderTradeList` and `buildTradeRecordAnnotations` behavior across Review, Static, Admin, and editor preview
- Canonical registry, tracked SQLite trade projection, admin atomic-write path, and publication/runtime boundaries
- Card time-span and marker action/name semantics, including K-line hover text
- Frozen manifest, tests, visual receipts, lifecycle gates, and authority separation

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | Scope-authority bullet; §1.4 Nickname; §1.5; §3.1 item 5 and “Out of manifest”; §3.3; §4 Phase 1; §5 checks | The plan treats `content/traders/index.json` as an isolated presentation string and explicitly forbids a tracked-SQLite update. That bypasses the repository’s canonical registry write contract. `PUT /api/admin/traders` calls `handle_trader_registry_admin_write(..., after_replace=_sync_trade_projection)`, and `_sync_trade_projection` candidate-projects the complete normalized repository before atomic DB promotion. The tracked DB currently stores the same display name in `traders`, and `v_trade_group_performance` exposes it. Editing only JSON would leave canonical content at `vordinkkk` while the tracked DB remains `沃德哥`, contradicting the DB-first/projection consistency boundary and the daily runbook’s required atomic content replacement. | Revise the plan around one existing atomic registry-write/projection route, not a direct JSON-only edit. Add `data/sqlite/tang_strategy_live_extended.db` to the exact implementation manifest and freeze candidate-first acceptance: validate the full registry/trade repository; preserve market-day, strategy, teaching, bar, dataset, and non-target trade facts; pass integrity and foreign-key checks; prove both canonical JSON and SQLite `traders`/view resolve `vordin → vordinkkk`; and retain rollback/unchanged-current-DB behavior on failure. This is a local governed data mutation only and grants no provider, publication, or remote authority. |
| P2 | §1.4 Card meta; §2.2 criteria 1 and 3; §2.4 `N-Card-source`; §3.1 items 2–4 | The required first→last card meta is not executable as frozen. `N-Card-source` only scans JSX text, so it can pass while the implementation chooses array order, ignores a second leg, mishandles incomplete timestamps, or renders an undefined one-event state. The backend guarantees chronological known times within each leg, not a cross-leg group order. The locked mock covers only multi-event examples. | Freeze a pure group-time helper and Node assertions. Define the range as the chronological min/max of all complete `occurred_at` values across every leg, then specify exact rendering for zero, one, and two-or-more known times. Test multi-leg and deliberately out-of-order fixture arrays plus incomplete times. Keep source assertions only for the negative outcome/fees checks; use the pure helper for the time-range behavior. |
| P2 | §1.4 Marker text/BUY-SELL derivation; §2.2 criteria 4–8; §2.4 `N-Marker-label`/`N-Action-map`; §3.1 item 1 | The marker contract changes only `marker_label`, but `buildTradeRecordAnnotations` also emits a user-visible `title`; `kline-engine.js` renders that title in the annotation tooltip. The plan can therefore pass all current criteria while the chart label says `vordinkkk BUY` and hover still says raw `vordin CALL buy_open`. The action fallback is also fixture-dependent (`?` only if an unknown happens to appear), even though criteria 4–5 require BUY/SELL-only labels and canonical schema accepts exactly `buy_open`, `buy_add`, `sell_partial`, and `sell_close`. | Freeze all user-visible annotation text, including tooltip `title`, to the display-name + action-side vocabulary while leaving shape/color direction-owned. Map all four schema actions explicitly; fail closed by omitting any unrecognized action rather than emitting `?`. Add Node cases for all four actions, missing/unknown actions, BUY/SELL same-bar separation, same-side `×N`, display-name fallback, and absence of raw `vordin`/CALL/PUT from both `marker_label` and `title`. |

## Verified Strengths

- The plan is the only Proposed plan and is the latest lifecycle focus; its revision, author, indexes, roadmap, `PROGRESS.md`, and `HANDOFF.md` agreed before review.
- All four declared evidence SHA-256 values match the repository artifacts. Visual inspection confirms the card/result noise and raw `vordin CALL/PUT` marker problem; the locked mock clearly expresses points-only cards and `vordinkkk BUY/SELL` labels.
- The named batch is a truthful pointer to session OPT-001/002, and OPT-003…006 remain excluded.
- Current source confirms shared Review/Static/Admin card consumers, Review/Static/editor annotation-builder consumers, direction-owned marker shapes/colors, and preserved download/filter contracts.
- The QQQ `2026-07-17` fixture contains current `buy_open`, `sell_partial`, and `sell_close` events and is suitable for the intended visual receipts.
- Baseline checks passed before review: direct operating-mode checker, 12/12 lifecycle fixtures, governed/auto harness, and `git diff --check`.
- Activation, implementation, provider/broker, publication, push, and other remote authority remain correctly separated.

## Verdict Rationale

The subtraction direction, BUY/SELL vocabulary, stable `trader_id`, shared-component scope, and exclusion of adjacent OPT items are sound. This exact revision cannot be approved because its registry-only manifest would deliberately create canonical-content/SQLite projection drift. The time-range and user-visible marker-text carriers also permit implementations that pass the named checks without satisfying the interaction shown to the user. These are bounded plan corrections: fold them into a new stable revision and re-review that exact revision. This review does not activate or implement the plan and grants no data write, provider/broker, publication, push, or remote authority.
