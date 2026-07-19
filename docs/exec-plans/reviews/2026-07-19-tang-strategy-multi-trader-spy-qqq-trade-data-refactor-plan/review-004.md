# Review 004 — Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v3-round-1-review-foldback-2026-07-19`
- Review type: design
- Reviewer ID: `grok-build-0.2.103-round-2`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: independent read-only inspection of frozen plan SHA-256 `90cc4ee056f423b3678c6a1cad3361b6d2a52e02ca614521f01a876f217f1188`, startup/lifecycle docs, round-1 reviews, live SQLite/legacy corpus, backend bar/trade consumers, frontend marker path, workflows, and operating-modes checker
- Verdict: revise
- Confidence: high

## Scope Checked

- Plan objective, success criteria, non-goals, and round-1 foldback completeness
- Current SQLite/legacy/trade-overlay/market-data evidence
- Exact planned file surface versus bar/trade consumers
- Historical grandfathering and prospective pair behavior
- Dataset/bar ownership, active-dataset enforcement, and assemble/export resolution
- Legacy extraction, phase sequencing, Phase 6 cutover, verification, authority, and lifecycle

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Blocking | Plan Sections 3.4/5.2/Phase 2 versus `backend/app/services/bar_utils.py:160-162`, `backend/app/services/importer.py:215-219`, `backend/app/services/db_safety.py:28-50`, `backend/app/services/db_safety.py:374-387`, `backend/scripts/rebuild_live_extended_db.py:307-309`, and `backend/tests/test_db_safety.py` | v3 re-keys bars to `(dataset_id, idx)` and keeps ordered digests as the preservation oracle, but the exact Modify surface omits helpers that hardcode `market_day_id` for inserts, digests, candidate counts, and safety tests. Implementers would have to edit unlisted files or leave the oracle inconsistent. | Add `backend/app/services/bar_utils.py`, `backend/app/services/db_safety.py`, and `backend/tests/test_db_safety.py`; require Phase 2 to re-key insert/select/digest helpers and rebuild semantic counts through active datasets without weakening non-shrink/drift gates. |
| Non-blocking | Plan decision 18 versus Phase 5 | Decision 18 says import/rebuild switch together with public cutover, while Phase 5 adds QQQ discovery/orchestrator capability before Phase 6. The additive design is workable, but the wording invites dispute about default behavior. | Scope switch-together to the public trade payload and default daily contract; explicitly allow Phase 5 internal QQQ capability without changing the default SPY/Tang entry. |
| Non-blocking | Plan Section 4.1 versus legacy corpus | The plan says “both note-only contexts,” but one of the two top-level note entries coexists with two trades; only one date is trades-empty. | Say “both day-level note entries, including one notes-with-trades day and one trades-empty day.” |
| Non-blocking | Plan marker surface versus live imports | `DailyReviewChart.jsx` is listed, but current Review/Static pages use `UnifiedKlineEngine` and `kline-engine.js`; the file is not a live consumer. | Keep or remove it with explicit rationale and do not call it the live marker path. |

## Verdict Rationale

The verdict is `revise`. v3 is a substantial and mostly successful foldback: all round-1 findings around recovery, operating modes, historical asymmetry, public payload sequencing, extraction, markers, rebuild tests, dataset policy, response shape, and frontend test carriers were independently verified closed.

The remaining blocking issue is narrower: the new dataset policy is clear, but the frozen manifest omits the existing bar identity/digest carriers needed to implement and verify it. This is the same exact-surface class as the first-round recovery omission and must be folded before activation.

Live evidence independently confirmed 46 SPY / 0 QQQ days, 20 legacy files / 27 trades / 2 top-level note entries, current bar/trade consumers, adapter flags, SPY/SPX discovery, Pages SPY pin, hash-route shape, and reconciled lifecycle state. The operating-modes checker passed. No implementation, provider/IB access, DB mutation, publication, Windows/macOS receipt, or hosted check was performed. The sibling round-2 reviewer output was not read. This review does not activate or execute the plan.
