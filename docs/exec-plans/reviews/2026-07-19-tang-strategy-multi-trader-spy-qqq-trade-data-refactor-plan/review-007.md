# Review 007 — Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v5-round-3-review-foldback-2026-07-19`
- Review type: design
- Reviewer ID: `kimi-code-0.27.0-round-4`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: independent read-only re-inspection of frozen SHA-256 `bef679910ee98d20b57053e7ce1b2b1c4c85eeb8d7ddf9e2012c64caaecf00c7`, startup/lifecycle docs, reviews 001-006, live documentation/code carriers, full-repository trade/bar/SPY consumer sweeps, legacy-corpus recount, a read-only tracked-DB copy, and the operating-modes checker
- Verdict: approve
- Confidence: high

## Scope Checked

- Round-3 foldback for `README.md`, `backend/README.md`, and `docs/kline-engine.md`
- Every earlier blocking finding and material clarification against v5 and live evidence
- Full-repository code, data, workflow, lifecycle, documentation, bar-SQL, and hash-route carrier sweeps
- Old/new bar digest oracle, active-dataset resolution, Phase 5 internal/default boundary, and Phase 6 atomic public cutover
- Legacy 20-file/27-trade/2-note corpus rules, marker path, tests, authority, and lifecycle coherence

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Non-blocking | Plan Sections 3.2 and 8.2 versus `backend/scripts/fetch_tv_live_extended_day.py:11` and `backend/scripts/fetch_ib_live_extended_day.py:9` | The new parser validates offsets against installed IANA timezone rules and the Windows receipt includes timezone tests, but Windows `zoneinfo` may need the `tzdata` package and requirements files are outside the exact surface. This dependency characteristic already exists in both adapters, Phase 5 fails closed on a missing receipt, and Phase 0 stops on an unlisted required path, so it cannot produce a false pass. | Record IANA tzdata as a cross-platform environment prerequisite, or revise the manifest before implementation if a repository-level pin is required. No design re-review is required now. |

## Verdict Rationale

Round-3 foldback is closed: all three documentation carriers are in Section 5.2; backend seed wording is bound to Phase 5 internal QQQ enablement with the default path unchanged; and root content-layout plus K-line overlay wording are bound to Phase 6. Their live stale text was independently reproduced.

All earlier blocking findings remain closed. Every live `tang_trades`/legacy-content consumer is in Modify or Remove, every SQL consumer of the bar tables is in Modify, and remaining SPY mentions outside the surface are unchanged regression/teaching facts or preserved historical records. The logical-day bar digest remains valid because `BAR_COLUMNS` excludes the ownership key; active-dataset resolution and the Phase 5/6 boundary fail closed; the corpus is exactly 20 files, 27 trades, and two correctly named day-note records; the live marker path and orphan exclusion are accurate; and lifecycle metadata/indexes/state blocks pass the checker.

Unverified by design-review boundary: implementation, provider/IB behavior, platform receipts, candidate migration, tracked-DB promotion, publication, and hosted behavior. The sole finding is non-blocking. This review does not activate or execute the plan.
