# Implementation Review 001 — Tang Strategy Review Sidebar Spacing And K-line Selection Band

- Review target: `docs/exec-plans/completed/2026-07-21-tang-strategy-review-sidebar-spacing-and-kline-selection-band-plan.md`
- Review target revision: `v2-review-foldback-2026-07-21`
- Review target commit: `5f36d29a44fb12aee2319ae147303cc970d83193`
- Review type: implementation
- Reviewer ID: `independent-impl-reviewer-2026-07-21-sidebar-spacing-selection-band-001`
- Plan author ID: `grok-plan-author-2026-07-21-sidebar-spacing-selection-band`
- Packet author ID: `kimi-executor-2026-07-21-sidebar-spacing-selection-band`
- Independence declaration: `attested` (reviewer did not author the plan design or the implementation; product tree re-inspected from frozen packet + live sources)
- Evidence method: full plan/packet/Phase-0-note read; `git show 5f36d29a --stat` + full source diff inspection; `npm run test:trade-records` re-run locally (64/64); receipts.json re-read; V1–V3 screenshots visually inspected; new Playwright runner read line-by-line; harness auto re-run; git boundary diffs checked.
- Verdict: accept
- Confidence: high

## Scope Checked

Plan revision `v2-review-foldback-2026-07-21` (read from `docs/exec-plans/active/`, identical content expected at the `completed/` migration target) against product implementation commit `5f36d29a44fb12aee2319ae147303cc970d83193`:

- §2.2 success criteria 1–10 (OPT-001 spacing/captions/title/Download; OPT-002 band cancel; locate retention; marker contract; surface parity; tests/builds/receipts).
- §2.4 carrier matrix: N-Sidebar-source, N-Highlight-source, N-Marker-regression, N-Export-pure, N-Span-oracle; B-Sidebar-layout, B-Group-band-cancel, B-Event-focus-cancel (Review + Static each); V1–V3; independent-oracle and empty-highlight rules; historical-runner exclusion.
- §3.1 frozen manifest: items 1–8 modified exactly; item 9 (AdminTradersPage) correctly not required; item 10 (historical runner) untouched; no backend/API/DB/seed/content/Pages/provider changes.

### What was independently verified

1. **Changed path set** — `git show 5f36d29a --stat` lists exactly 9 files, all frontend: the 8 manifest items (TraderFilters.jsx, ReviewPage.jsx, StaticReviewsApp.jsx, TraderTradeList.jsx, ReviewSignalList.jsx, styles.css, tradeRecords.js, tradeRecords.test.js) plus the new tracked runner `frontend/scripts/playwright/review-sidebar-spacing-and-selection-band-acceptance.mjs` (+444). `git diff 0462fb33..HEAD` confirms zero changes to `backend/`, `data/`, `content/`, `frontend/src/pages/AdminTradersPage.jsx`, and the historical `trade-tools-group-span-viewport-data-rail-acceptance.mjs`.
2. **OPT-002 band cancel** — `selectTradeGroup`/`focusTradeEvent` on both pages now call `setHighlightRanges(null)` (clear-stale), contain no painted range object and no `style: 'blue'`; fitRange retained with the frozen padding pairs (group `0.2/4`, event `0.35/8`); no post-fit `scrollTo` in either body (the `scrollTo` at ReviewPage.jsx:387 / StaticReviewsApp.jsx:442 belongs to the out-of-scope annotation-select path). `tradeRecords.js` change is a 3-line doc comment only; marker builders untouched.
3. **OPT-001 layout/Download** — Review/Static no longer import or pass `TradeExportControls`; Admin still imports and mounts it (AdminTradersPage.jsx:4,247, unmodified). `TraderFilters.jsx` has no `Trade tools` title; head row renders only when `exportControls` is provided; single `trade-filter-label` "Traders" row. Captions `交易者 · Trades` (TraderTradeList) and `策略讲解 · Signals` + `.dr-signal-stack` wrapper (ReviewSignalList) present; styles.css adds scoped `.dr-sidebar .dr-signal-list { gap: 20px }`, `.stack-caption` + `::after` hairline, removes `.trade-tools-title`; in-block density pins unchanged.
4. **N-carriers** — `npm run test:trade-records` re-run by this reviewer: **64/64 pass**. The three new tests (N-Sidebar-source, N-Highlight-source, N-Span-oracle) read the live sources and assert the actual contract (no TradeExportControls on Review/Static, Admin retains it, no title string, caption markers, 20px CSS rule; clear-or-skip highlight bodies with padding pairs; frozen fixture span `[12,31]` / event bar `20` cross-checked against runner constants). N-Marker-regression / N-Export-pure retained and green.
5. **B-carriers + V1–V3** — receipts at `output/playwright/review-sidebar-spacing-selection-band-20260721151606/receipts.json`: all 9 receipts PASS with sane numbers (gaps exactly 20/20 both surfaces; `toolsTitleCount=0`, `toolsHeadCount=0`, `downloadCount=0`, `tradersLabelCount=1`; group select highlights `0`, viewport `[8,35]` ⊇ `[12,31]`; event focus highlights `0`, bar `20` inside `[12,28]`, window `17 ≤ 120`). V1/V2/V3 screenshots visually inspected by this reviewer: captions + hairlines + gaps visible, no blue band after group select, BUY/SELL marker labels readable, Static parity confirmed.
6. **Runner oracle integrity** — the new runner hard-codes the Phase 0 frozen constants (`tg_20260717_vordin_qqq_002`, row 1, `[12,31]`, bar `20`, 390 RTH bars), asserts `getHighlightRanges()` length `0` after group select, after group settle, after event focus, and after event settle; checks viewport containment only against the independent constants; checks window stability across settle (no post-fit recenter); never reads highlight storage as an expectation; contains no blue-band assertions. Receipts fail-closed (throw → `failure.json`, exit 1).
7. **Working tree state** — `git status --short` shows no uncommitted product-code changes; only untracked `output/**` evidence and the review packet. Authority boundary held: product commit is frontend-only; no push/PR/remote artifacts observed.

## Findings

| # | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| 1 | note | `python3 scripts/check-project-harness.py --root . --profile auto` currently reports one operating-modes error: `reviews index artifact links mismatch: 2026-07-21-...-plan`. Cause: the untracked `implementation-review-packet-001.md` (and now this `implementation-review-001.md`) exist in the reviews directory while `docs/exec-plans/reviews/index.md` line 7 links only `review-001`/`review-002`. Not caused by the product commit (which touches no lifecycle path); the executor's green-harness claim predates the packet landing in the directory. Plan §4 Phase 2 already owns this: the closeout commit must reconcile the reviews index (link packet + this review) and migrate the plan to `completed/`. This review file itself will keep the harness red until that reconciliation lands. | Reconcile in closeout commit; does not block accept of the product implementation. |

No P1/P2 findings. Every §2.2 criterion and every §2.4 mandatory carrier was re-verified from live sources, not from packet claims.

## Verdict Rationale

- All ten §2.2 success criteria check out from independent inspection: measured 20px gaps on both surfaces (B-receipts + V1/V3), captions/hairlines present, `Trade tools` title gone, single Traders row, Download removed from Review/Static and retained on Admin, group/event highlight paint cancelled with `setHighlightRanges(null)`, fitRange locate retained with frozen padding pairs, no post-fit recenter (runner window-stability check), marker label contract untouched, Review/Static parity confirmed in sources, tests, receipts, and screenshots.
- All §2.4 mandatory carriers green and structurally sound: N-* suite re-run 64/64 by this reviewer; B-* receipts present for Review **and** Static with independent-oracle and empty-highlight rules honored; the historical group-span runner is unmodified and correctly excluded; V1–V3 visually confirm the receipts.
- §3.1 manifest respected exactly (items 1–8; item 9 legitimately unused under the frozen default approach; item 10 untouched); no backend/API/DB/content/Pages/provider paths changed; authority boundary (local commits only, no remote action) held.
- The single open item (finding 1) is lifecycle bookkeeping already assigned to Phase 2 closeout, not an implementation defect.

**Verdict: accept** (confidence high).

Note: this accept verdict covers only the product implementation against plan revision `v2-review-foldback-2026-07-21`. It does **not** authorize push, PR, merge, Pages publication, provider/broker actions, tracked DB/content mutation beyond the closeout lifecycle paths, or any other remote action. Closeout (plan migration to `completed/`, OPT status updates, reviews/roadmap index reconciliation, state-file updates) proceeds under its own task-scoped local-commit authority only.
