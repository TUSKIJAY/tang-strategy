# Review 001 — Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v2-dual-review-loop-2026-07-19`
- Review type: design
- Reviewer ID: `kimi-code-0.27.0-round-1`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: Independent read-only inspection of the frozen plan (SHA-256 `2c9dcab8b7e578ba74e512357af17121e0f3b3673597a8046cd1bcf8a010cd39` re-computed via `shasum -a 256`, matches), startup/lifecycle docs, backend/frontend sources, workflows, the 20 legacy trade JSONs, a read-only `/tmp` copy of the tracked DB, and the repository's own read-only checker (`scripts/check-operating-modes.py --root .` returned `errors=[]`, `passed=true`).
- Verdict: revise
- Confidence: high

## Scope Checked

- Plan objective, success criteria, and non-goals against Lane 3 hard criteria in `docs/operating-modes.md`
- Current-state evidence in plan Section 1.1 against live repository files and tracked DB content
- Architecture and data model: canonical JSON, SQLite projection, outcome/eligibility, and timezone contract
- Exact planned file surface: add/modify/remove existence and completeness of consumer inventory
- Migration, data-safety, rollback matrix, and candidate-only DB contract
- SPY/QQQ atomic pair update contract against existing adapters/importer/rebuild behavior
- API/UI/Pages cutover and `#<ticker>-<date>-extended` link stability
- Phase gates, verification feasibility, authority/lifecycle wording, and the same-revision dual-review loop design
- Unrelated-change protection and lifecycle reconciliation state in the uncommitted worktree

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Blocking | Plan Section 5.2/4.3 versus `backend/scripts/recover_historical_market_days.py:427-435` | The recovery script is a live consumer of the old contract: it reads `payload.get("tang_trades")` from exported static payloads and hardcodes the `spy-...` payload filename, yet it appears in none of the plan's Add/Modify/Remove surfaces. Post-cutover this tool's overlay check would fail against `trade_records`, contradicting the plan's every-consumer and no-hidden-compatibility requirements. | Add `backend/scripts/recover_historical_market_days.py` to the Modify surface, or explicitly retire/scope it out with rationale; correct the current consumer inventory and add matching phase work and verification. |
| Blocking | Plan Section 5.2 versus `docs/operating-modes.md:209` and `docs/operating-modes.md:255` | The normative Local Update Gate and carrier-map row cite the Tang-specific trade step and existing `load_tang_trades` validation command. The plan removes that loader and replaces `content/trader-trades/` but does not list `docs/operating-modes.md`, so the normative contract would go stale at cutover. | List `docs/operating-modes.md` in Section 5.2 and include contract-text reconciliation for gate step 9 and the carrier-map row, or explicitly justify why the text remains unchanged. |
| Non-blocking | Plan Sections 3.5, 3.6, and 7 | Ticker-history asymmetry is under-specified: the DB holds 46 SPY days and zero QQQ days, but the plan does not state whether QQQ starts at the first pair run without backfill, how static export/manifest handles pre-onboarding SPY-only dates, or the steady state if Phase 5 closes on a truthful platform blocker while the runbook remains SPY-only. | State the QQQ onboarding/backfill policy, export/manifest behavior for dates with no accepted pair, and the blocked-platform end state. |
| Non-blocking | Plan Phase 0 exit gate | The phrase "committed as evidence" is ambiguous against the explicit no-commit authority boundary. | Reword it to "recorded/captured as evidence" or tie it explicitly to separately granted commit authority. |

## Verdict Rationale

Independently verified: the frozen SHA matches the file exactly; every Section 1.1 current-state claim checks out against live evidence; the tracked DB copy contains 46 SPY extended days and no QQQ; exactly 20 legacy JSONs match the Section 5.1 target dates one-for-one; both adapters expose `--symbol` and `--skip-import`; importer/rebuild discovery remains SPY/SPX-only; the Pages workflow pins SPY; and the current hash slug includes ticker/date/session. All listed Modify/Remove paths exist, listed Add paths are absent, and the read-only operating-modes checker passes.

Unverified boundaries: future phase feasibility, Windows/macOS receipts, real provider/IB behavior, and runtime execution were not run under the read-only design-review boundary.

The verdict is `revise`, not `reject`: the design is fundamentally sound, but the exact file surface omits one code consumer of `tang_trades` and one normative governance document that references the removed loader. Both omissions violate the plan's own completeness criteria and would otherwise trigger a mid-implementation plan revision. This review does not activate or execute the plan.
