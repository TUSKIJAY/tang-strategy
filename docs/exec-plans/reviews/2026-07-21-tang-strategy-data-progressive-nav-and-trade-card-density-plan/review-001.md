# Review 001 — Tang Strategy Data Progressive Navigation And Trade Card Density

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`
- Review target revision: `v1-proposal-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-data-nav-trade-density-r1`
- Plan author ID: `codex-plan-author-2026-07-21-data-nav-trade-density`
- Independence declaration: `attested`
- Evidence method: `Independent read-only inspection of the plan, startup and operating-mode contracts, linked optimization evidence and screenshots, frontend consumers, CSS cascade, contract tests, and governed harness output.`
- Verdict: revise
- Confidence: high

## Scope Checked

- Plan objective, source OPT boundaries, and non-goals
- Current `DashboardPage` / `ReviewContextPanel` progressive-navigation contract
- `TraderTradeList` consumers and shared CSS cascade
- Existing frontend source-contract tests and build commands
- Lifecycle gates, review requirements, indexes, state surfaces, and authority wording

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | §4 Phase 2, lines 218–227; §5 Commit boundaries | The closeout moves the plan from `proposed/` directly to `completed/` and does not require an independent implementation review. Once activated, the source state is `active/`; implementation completion cannot by itself authorize Completed migration. The single-commit wording also collapses implementation evidence, review, and lifecycle closeout. | Rewrite closeout as Active implementation verification → independent implementation review (`accept`) → separately authorized Completed migration. Keep commit/push authority separate. |
| P1 | §4 Phase 0 scope freeze and Phase 1 verification | The frozen two-file scope cannot preserve the current frontend contract suite. `reviewWorkspace.test.js` asserts that only Review opts into progressive navigation and pins `.dr-sidebar .trade-record-list` to `8px`; both assertions must change. `ReviewContextPanel.jsx` also contains a stale “Review only” comment after Data opts in. The plan does not run `npm run test:trade-records` or the static build. | Add `ReviewContextPanel.jsx` comment-only reconciliation and `reviewWorkspace.test.js` to the manifest. Require `npm run test:trade-records`, normal build, and `VITE_STATIC_REVIEWS=true npm run build:static-reviews`. |
| P2 | §4 WU-B CSS, lines 174–201 | Global `.trade-record-list`, `.trade-group-card`, `.trade-group-summary`, and child selectors also change `AdminTradersPage`, which renders the same `TraderTradeList` outside `.dr-sidebar`. The source OPT scopes the change to Review with Static parity, not Admin. | Prefix the density overrides with `.dr-sidebar`, or explicitly add Admin to scope and acceptance. Review and Static already share `.dr-sidebar`, so scoped selectors cover both intended surfaces. |
| P2 | §2.2 and line 204 | The final 11px/12px choice is deferred to subjective implementation-time judgment, so phase exit and independent review cannot reproduce the visual decision. No viewport, long-name, wrapping, expanded-state, or screenshot comparison matrix is pinned. | Freeze exact type/padding/gap values and a small desktop+narrow Review/Static screenshot matrix covering Tang, 沃德哥, long labels, selected state, and expanded legs/events. |
| P3 | Final contract link, line 257 | `../operating-modes.md` resolves to nonexistent `docs/exec-plans/operating-modes.md` from the proposed directory. | Change the link to `../../operating-modes.md`. |

## Verdict Rationale

The two user-facing objectives are narrow and appropriate for one small frontend plan, and the existing progressive DateRail can be reused without backend or data changes. Revision is still required because the current plan cannot preserve its own frontend contracts or complete the governed lifecycle as written, and the global CSS proposal expands beyond the recorded Review/Static scope. The review lifecycle package may be committed locally under standing review authority; this review does not activate, implement, push, or publish the plan.
