# Review 002 — Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v2-dual-review-loop-2026-07-19`
- Review type: design
- Reviewer ID: `grok-build-0.2.103-round-1`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: independent read-only inspection of plan SHA-256 `2c9dcab8b7e578ba74e512357af17121e0f3b3673597a8046cd1bcf8a010cd39`, startup docs, operating-modes contract, SQLite schema/counts, legacy trade JSON corpus, backend/frontend trade overlay paths, fetch/rebuild/export/Pages surfaces, and lifecycle indexes
- Verdict: revise
- Confidence: high

## Scope Checked

- Plan objective, success criteria, and non-goals
- Current repository evidence for Tang/SPY overlay, SQLite tables, market-day inventory, seed discovery, Pages ticker pin, and hash-route shape
- Architecture and data model: traders/trade hierarchy, eligibility/outcomes, market datasets, and Agent views
- Exact planned add/modify/remove file surface versus live consumers
- Migration, candidate DB promotion, data-safety matrix, and rollback coherence
- SPY/QQQ atomic update contract versus current Data Update Mode and adapter behavior
- API/UI/Pages cutover sequencing and historical link stability
- Phase 0-6 entry/exit gates and verification feasibility
- Authority, lifecycle metadata, dual-review loop, and activation/implementation separation
- Unrelated-change protection and proposal-only scope wording

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Blocking | Plan Sections 3.5-3.6 and 2.2; evidence `backend/app/db.py:136-148`, live DB 46 SPY / 0 QQQ | Atomic pair and export-both-tickers behavior are defined for new pair days, but the plan never defines post-cutover behavior for historical SPY-only days, first-time QQQ introduction, a mixed-history Pages manifest, or UI switching when one underlying is absent for a date. | State that pair atomicity applies to newly accepted same-date SPY+QQQ updates; pre-existing SPY-only days remain legal/exportable; UI offers only available underlyings per date; the manifest may contain unpaired historical days; and the first QQQ day does not rewrite or suppress historical SPY links. |
| Blocking | Plan Section 5.2 versus `docs/operating-modes.md:193-215` and `docs/operating-modes.md:247-255` | The plan changes the daily path to staged pair fetch, candidate pair promotion, canonical `content/trades`, and new triggers. `docs/operating-modes.md` is the normative Data Update contract but is absent from the Modify surface, guaranteeing contract drift. | Add `docs/operating-modes.md` and require Phase 5/6 reconciliation of the Local Update Gate, Publish Gate commit scope, verification carriers, pair staging, no-partial-pair behavior, and trade-path cutover. |
| Blocking | Plan decision 18, Section 3.5, Phase 3, and Phase 4; live consumers `backend/app/main.py:151-191`, `frontend/src/pages/ReviewPage.jsx:263-389`, `frontend/src/pages/StaticReviewsApp.jsx:298-447` | The plan forbids dual-write/compatibility, yet Phase 3 switches backend/static assembly to `trade_records` while Phase 4 replaces frontend consumers later. That intermediate branch state is end-to-end broken and contradicts switch-together. | Make the payload rename one atomic implementation boundary: switch backend, static export, and interactive/static frontend together, or keep the old member until final cutover. Explicitly keep intermediate broken states unauthorized for `main`. |
| Blocking | Plan decision 17 and Section 4.1; live legacy notes across `content/trader-trades/` | Actual notes contain return-like percentages, position-size percentages, and ambiguous phrases. A naive percentage extractor can invent returns and wrongly set `reported_stats_eligible`; mandatory negative fixtures are not sufficiently explicit. | Lock an allowlist of exact return patterns plus denylist/review cases: reject bare `N%` position-size phrases, leave ambiguous exit percentages unparsed unless a tested rule proves otherwise, and require the migration report to enumerate all extracted/unparsed notes across 27 trades and 20 files. |
| Blocking | Plan decision 15 and Section 5; `frontend/src/kline/kline-engine.js:2169-2170`, `frontend/src/features/review/TangTradeList.jsx:102-117`, `frontend/src/kline/DailyReviewChart.jsx:44-54` | Stable trader colors and CALL/PUT shapes are required, but chart styling is currently Tang/direction-hardcoded and the real marker files are absent from the Modify surface. | Add `frontend/src/kline/kline-engine.js` and, if still used, `frontend/src/kline/DailyReviewChart.jsx`, or prove markers are rendered solely through the new components. Update Phase 4 verification. |
| Blocking | Plan Section 5.2 versus `backend/tests/test_rebuild_live_extended_db.py:21` | Generalizing seed discovery beyond SPY/SPX changes refusal text and fixtures, but the existing rebuild suite is absent from the Modify surface. | Add `backend/tests/test_rebuild_live_extended_db.py` and any other seed-discovery assertion tests; require updated refusal/superset behavior for QQQ without weakening non-shrink gates. |
| Non-blocking | Plan Section 3.4; `backend/app/db.py:150-204` | Bars currently key by market day. The proposed dataset re-key does not state whether `dataset_id` becomes the bar FK, how exactly one active dataset is enforced, or how assemble/export remain market-day addressed. | Define bar ownership, the unique active-dataset constraint, and the assemble/export dataset-resolution rule; keep ordered bar digests as the preservation oracle. |
| Non-blocking | Plan Section 3.5; `backend/app/main.py:170-191` | The replacement member is named, but the minimum reviewable API/static JSON field structure is deferred. | Add a short response field table or make Phase 1 exit explicitly gate all payload work on the published trade-data contract. |
| Non-blocking | Plan Section 5.3; `backend/scripts/recover_historical_market_days.py:429-435` | Recovery tooling still inspects historical `tang_trades` keys, so a cutover diff claiming no consumers remain would be false. | Preserve a bounded historical-read exception or add the script to the cutover surface. |
| Non-blocking | Plan Phase 4; `frontend/package.json` | Frontend has build/dev scripts but no unit-test runner, so the proposed unit coverage is not currently runnable. | Add a runnable pure-JS test entry or state that acceptance is browser plus backend statistics tests and do not claim frontend unit coverage. |

## Verdict Rationale

The verdict is `revise`. The plan is a serious Lane 3 design: objective/non-goals are coherent, authority language correctly withholds implementation/provider/DB/Git/Pages power, candidate-only DB migration and the safety matrix match existing promotion semantics, and the same-revision Kimi/Grok loop is clear. Constrained Proposed metadata and lifecycle indexes/state blocks are consistent; the operating-modes checker passed on the proposal worktree.

Independently verified: the frozen SHA matches; the live DB has only the existing market-review tables with 46 SPY and 0 QQQ days; exactly 20 legacy files contain 27 trades plus note-only contexts; adapters accept `--symbol`/`--skip-import` but default-import one symbol; importer/rebuild discovery is SPY/SPX-only; the Pages workflow pins SPY; and static slugs preserve ticker/date/session.

Unverified: no implementation, migration dry-run, provider fetch, IB access, tracked-DB mutation, Pages publish, or hosted check was performed. Windows pair receipts remain unproven. The sibling Kimi review was not read or used.

The blocking findings require policy and file-surface decisions that implementers must not invent under an exact manifest freeze. Fold them into a new revision and repeat the same-revision dual design review. This review does not activate or execute the plan.
