# Review 005 — Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md`
- Review target revision: `v4-round-2-review-foldback-2026-07-19`
- Review type: design
- Reviewer ID: `kimi-code-0.27.0-round-3`
- Plan author ID: `codex-plan-author-2026-07-19-multi-trader`
- Independence declaration: `attested`
- Evidence method: independent read-only re-inspection of frozen SHA-256 `122c3e673afc6f2cab3680d503b1d2816f31ddbfe150dc41729a3215e017467f`, startup/lifecycle docs, reviews 001-004, backend bar/digest/trade carriers, frontend marker/test surfaces, the 20-file legacy corpus, a read-only tracked-DB query, and the lifecycle/harness checkers
- Verdict: revise
- Confidence: high

## Scope Checked

- Every prior blocking finding and material foldback claim against v4 and live evidence
- Bar-identity/digest carrier surface and old/new-schema digest oracle
- Active-dataset resolution and Phase 5 internal/default boundary
- Legacy notes wording, live marker path, and the Phase-4-only frontend test gate
- Full-repository consumer sweep for trade payloads, legacy content, seed naming, and Tang marker documentation
- Lifecycle metadata, indexes, state blocks, and authority boundaries

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Blocking | Plan Section 5.2 versus `README.md:21`, `backend/README.md:18`, and `docs/kline-engine.md:23` | Three documentation carriers of contracts changed by this plan are absent from the exact Modify surface. The root README retains the same obsolete Tang-overlay content description that the listed `AGENTS.md` and `INSTRUCTIONS.md` copies must change; the backend README documents SPY/SPX-only accepted seed naming even though Phase 5 adds QQQ; and the K-line engine contract still describes Tang overlay consumers even though marker rendering becomes multi-trader. The plan's manifest-freeze rule would force either stale documentation or a mid-implementation plan revision. | Add `README.md`, `backend/README.md`, and `docs/kline-engine.md` to Section 5.2 and bind their reconciliation to the corresponding Phase 5/6 contract changes, or explicitly justify each exclusion; bump the revision and repeat the dual review round. |

## Verdict Rationale

All earlier blocking findings were independently verified closed. The recovery and operating-mode carriers remain covered; existing SPY-only history and prospective pair atomicity are coherent; the public payload switch remains atomic in Phase 6; legacy extraction reconciles 20 files, 27 trades, and the two day-level note entries; dataset/bar keys, active-dataset resolution, the old/new `BAR_COLUMNS` digest oracle, marker ownership, rebuild tests, and Phase-4 test timing are now defined and carried by the exact surface.

The remaining finding is narrow but blocking under the plan's own rule that any required path outside the frozen manifest triggers plan revision and renewed review. `README.md:21` becomes false when `content/trader-trades/` is replaced; `backend/README.md:18` becomes incomplete when QQQ seed discovery is enabled; and `docs/kline-engine.md:23` becomes stale when Tang-only marker semantics are generalized. This is the same exact-surface class as the earlier missing contract/code carriers.

No implementation, migration dry-run, provider/IB access, tracked-DB mutation, platform receipt, commit, push, publication, or sibling round-3 review was performed or claimed. This review does not activate or execute the plan.
