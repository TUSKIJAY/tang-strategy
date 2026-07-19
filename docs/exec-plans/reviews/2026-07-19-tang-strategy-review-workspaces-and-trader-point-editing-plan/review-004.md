# Review 004 — Tang Strategy Review Workspaces And Trader Point Editing

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md`
- Review target revision: `v3-round-1-review-foldback-2026-07-19`
- Review type: design
- Reviewer ID: `grok-build-0.2.103-round-2`
- Plan author ID: `codex-plan-author-2026-07-19-review-workspaces`
- Independence declaration: attested
- Evidence method: Frozen plan SHA-256 `10fa26a14c9f9b6c51546748e28295014239507e89355201c8763f35e7e7ae69` matched on the live worktree; independent re-read of prior same-plan `review-001.md` and `review-002.md` only; live read-only checks of backend trade-record projection/admin PUT/auth, multi-ticker canonical day `content/trades/2026-07-17.json`, frontend Review/Static/Data/Admin/Backtest/Teaching/engine/filters/layout/API client, harness/CI `test:trade-records` carriers, tracked DB hash/counts, visual-reference PNG hash/dims, optimization intake, and operating-modes lifecycle wording. No sibling current-round review output was inspected. No implementation, browser acceptance, hosted verification, DB write, provider/broker access, push, or publication was performed.
- Verdict: approve
- Confidence: high

## Scope Checked

- Frozen revision identity and SHA against the supplied freeze.
- Every round-1 finding from Kimi `review-001` and Grok `review-002` against v3 foldback text and live contracts.
- Admin-only canonical full registry/day reads; public projection forbidden as write base; complete multi-ticker day merge and untouched preservation receipts.
- Ticker/date workspace authority; stale trader reconciliation; engine ownership and admin `UnifiedKlineEngine` preview.
- Interactive/static parity; accessibility dual-gate; candidate file surface; rollback; phases; verification carriers; authority and activation boundaries.
- Current-evidence bullets in plan §1.1 against live repository state.

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | — | — |

## Verdict Rationale

The frozen SHA and revision match. v3 is a complete, implementable foldback of both round-1 `revise/high` reviews; no blocking contract gap remains.

**Prior finding closures (independently re-verified):**

1. **Public projection is not a write base (review-002 blocking).** Live `build_trade_records_payload` / `_public_group` reduce full `normalization` to `normalization_method`, are ticker-filtered, and return active/referenced traders only. Replaying SPY public groups as a day document fails validation (`missing fields: normalization`). Canonical `2026-07-17.json` holds 3 groups across SPY+QQQ; a SPY-only public seed would drop both QQQ groups and the QQQ note context while still allowing schema/projection coherence. v3 forbids public seeding, freezes admin-only `GET /api/admin/traders` and `GET /api/admin/trade-records?trade_date=…` as write-valid full documents, and keeps existing PUTs as the only mutation boundary. Live code currently has admin PUTs only and public GET fabrication of empty missing days — exactly the gap the new GETs close without inventing defaults.

2. **Complete multi-ticker merge + preservation receipts (review-001 blocking).** v3 §3.4, Phase 0/3, success criteria 9–10, and §6 require clone-of-complete-day merge, semantic untouched preservation, fail-closed preservation diffs, and day group-count delta equal only to the intended edit. That closes the silent same-day group-loss path that server schema/ID checks alone cannot detect.

3. **TraderFilters ticker/date authority (review-002 non-blocking).** Live `TraderFilters.jsx` still owns editable ticker/date selects. v3 §3.1 removes independent authority and pins readonly mirrors plus pure divergence fixtures.

4. **Admin preview boundary (review-002 non-blocking).** v3 freezes one read-only reused `UnifiedKlineEngine` with shared marker/list helpers; no second chart implementation and no auto-save on preview.

5. **Test carrier / harness-CI sync (review-001 non-blocking).** Live carriers are `frontend/package.json` `test:trade-records`, `.harness/config.json`, and `.github/workflows/project-harness.yml`. v3 keeps the script name stable, broadens its command body, and forbids silent harness/workflow renames without plan revision.

6. **Accessibility pure fixtures (review-002 non-blocking).** v3 requires pure/component label/selected/disabled fixtures that supplement, not replace, browser keyboard/focus/announcement acceptance.

**Current-contract coherence against live evidence:**

- §1.1 facts match: DB SHA `125fcc9d…`, 49 market days (46 SPY / 3 QQQ), 11 active strategies, 2 traders, 33 trade groups; visual reference SHA `57c34ea7…` at `1672 x 941`; flat `marketDays`/`selectedDayId`; mixed Data/Review/Static selectors; duplicated page-level 1m/5m/Back/Step/Play/Pause/Overview with Review Backtest/Rescan both bound to `runBacktest`; engine toolbar owns generic controls but lacks visible fit/overview while the wrapper implements `overview()`; admin-only collapsed Traders nav and raw JSON admin editors; static flat `#<ticker>-<date>-<session>` slugs.
- Control ownership, availability-driven traders, static client-side grouping without export/publisher change, rollback-as-source-revert, temp-copy acceptance, and dual matching-revision lifecycle-only activation are internally consistent with `docs/operating-modes.md` and the stated user instruction.
- Planned surface includes the backend files needed for the two admin GETs and does not claim DB, auth-role, write-route, publisher, or Pages changes.
- Residual implementation freezes (exact empty-day create path for market dates without trade files; whether registry metadata uses the separate registry PUT) belong inside Phase 0 contract freeze and do not reopen the write-base or multi-ticker preservation hazards.

**Unverified by design-review boundary:** implementation, browser/a11y execution, hosted Pages, provider/broker behavior, and sibling current-round output. This review does not activate or execute the plan.
