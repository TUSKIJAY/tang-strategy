# Phase 5 — Integrated Acceptance Evidence

- Plan revision: `v2-review-foldback-2026-07-20`
- Phase disposition: `complete`
- Entry gate: verified Phase 4 exit
- Canonical mutation authority: none

## Optimization Outcomes

| Optimization | Accepted resolution |
| --- | --- |
| OPT-001 | The trader workspace is a bottom-pinned peer inside the same primary nav renderer. It uses the same geometry, hover/active/current contract, collapsed icon behavior, and `UsersRound` semantics as Data/Review/Backtest/Teaching. The filled orange destination is gone; role capability remains visible and accessible. |
| OPT-002 | Admin exposes an explicit `新增交易者` inline create card with exact field validation, staged-unsaved/removal state, full-document save, reload confirmation, immutable persisted IDs, and failure retention. Readonly and Static expose no mutation path. |
| OPT-003 | Review ticker/date/strategy, Eligibility, trader/Focus, export, group cards, drilldown, empty state, and statuses share one continuous terminal surface. The light-component palette patch is removed; Review keeps density-only overrides. |
| OPT-004 | Login, shell, Data, Review, Backtest, Teaching, Admin, and Static Review use the same 15-token charcoal/olive product skin. Warm orange is computed only on `.brand-mark`; chart/signal/trader colors remain domain-owned. |

All six source optimization screenshots were compared with the fresh receipts. Their recorded paper/charcoal split, orange CTA bleed, light Eligibility select, edit-only registry, and collapsed-nav mismatch are absent in the accepted implementation.

## Visual And Accessibility Contract

Real-browser computed values returned the exact root contract: app `#141413`, panel `#1E1E1D`, control `#282827`, control border `#74746E`, primary text `#E8E7E3`, accent `#8B9A6D`, and brand warm `#A6532A`. The frozen contrast pairs remain primary/panel `13.48:1`, muted/panel `6.83:1`, accent-ink/accent `6.34:1`, accent/panel `5.51:1`, success/panel `6.00:1`, danger/panel `5.14:1`, warning/panel `7.11:1`, and white/brand-warm `5.40:1`.

Playwright verified:

- five named peer destinations retain `aria-current="page"`, stable title/accessibility names, keyboard reachability, and visible `2px` olive focus outlines in expanded and collapsed shells;
- admin and readonly capability copy remains textually distinct; collapsed mode retains the full accessible name;
- Login retains a labeled password field, rejected-password copy, keyboard focus, and a computed `rgb(139, 154, 109) solid 2px` outline;
- registry client/server errors use labels, inline alerts, focus management, and form-level announcements as appropriate;
- trader identity always includes text, CALL/PUT retains shape/text, and review/active states retain non-color wording;
- every captured desktop/narrow flow reported zero document horizontal overflow.

No legacy paper token/value remains in product chrome. The only literal/variable `#A6532A` consumer is `.brand-mark`.

## Integrated Behavior Matrix

| Surface | Browser result |
| --- | --- |
| Shell/Data | Admin and readonly, expanded/collapsed, desktop/narrow; 2 tickers, 49 market days, 11 strategies; active/current state and zero overflow pass. |
| Review | Data→Review, SPY→QQQ, context reconciliation, trader availability, Focus, group drilldown, and four-file JSON/CSV export pass. |
| Static Review | Legacy `#/qqq-2026-07-17-extended` normalizes to `#qqq-2026-07-17-extended`; QQQ/Vordin resolves, zero overflow, no registry/admin text, and the network log contains only static review/index/strategy assets with no `/api/admin`. |
| Backtest | Latest-ten-days run produces 10 rows and 44 signals, loads the unified K-line engine, and remains overflow-free at `820x1180`. |
| Teaching | QQQ replay advances from cutoff `#30` to `#31`, then Reveal moves to full-day cutoff `#914`; prompts and unified K-line engine remain present and overflow-free. |
| Admin | Terminal point editor and registry render together; `新增交易者` remains discoverable; the Phase 4 isolated create/error/reload matrix remains green. |
| Readonly | Inspect/export remains available; `.tp-editor`, `.tp-registry`, and create action are absent on desktop/narrow and expanded/collapsed shells. |
| Login | Invalid password remains rejected without auth behavior change; focus/error chrome uses the shared tokens. |

The browser console contained only the pre-existing missing `favicon.ico`, the intentionally rejected invalid-login request, and Phase 4's deliberately induced negative registry requests. There were no application exceptions.

## Repository Verification

| Check | Result |
| --- | --- |
| governed harness | the pre-index-update run passed; this claim was invalidated when the later Phase 6 packet update changed the active-index Evidence cell to Phase 5 evidence, and is superseded by remediation-1 evidence |
| auto entrypoint | the pre-index-update run passed and routed to governed; current lifecycle status is superseded by remediation-1 evidence |
| direct operating checker | the pre-index-update run passed; the exact packet-001 target failed on the active-index latest-evidence mismatch and is superseded by remediation-1 evidence |
| lifecycle fixtures | pass, 171/171 in 171.369s |
| startup budget | pass hard limit; `PROGRESS.md` remains archive-recommended only |
| frontend carrier | pass, 46/46 |
| normal Vite build | pass, 1,755 modules |
| Static Review Vite build | pass, 1,755 modules |
| backend compileall | pass |
| full backend suite | 77/78 product tests pass; the sole result is the exact Phase 0 baseline Windows SQLite `TemporaryDirectory` teardown lock after product assertions in `test_post_promotion_backup_cleanup_failure_keeps_content_and_db_coherent` |
| alternate pinned Python 3.12 + full TV dependencies | reproduces the same single Windows teardown lock, proving it is not Python 3.14-specific or introduced by this frontend-only patch |
| `git diff --check` | pass |

Implementation review 001 independently exposed the post-receipt index mutation above. This evidence preserves that chronology instead of continuing to claim the rejected packet target was green. The backend source is protected and unchanged, so the known baseline environment error is classified truthfully rather than relabeled or remediated outside the frozen frontend/docs manifest.

## Protected State

Canonical state remains Phase 0 exact: SQLite SHA-256 `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0`, 25,702,400 bytes, 49 market days, integrity `ok`, and zero foreign-key findings; registry SHA-256 `9668400f2c3b9b514465e120e5e64e65350396ec5022f91de82f59b3a0553734` with two traders; 22 trade documents totaling 87,403 bytes and the frozen manifest `3a09591cd5ff07317d49daf1f8c221d3634253b8b79429d1471fd3f1dcd1f525`.

Backend routes, trade service, trader schema, Pages publisher, static exporter, and daily runbook retain the exact Phase 0 hashes recorded in `phase-4-create-trader-flow.md`. No tracked content, DB, provider, broker, publication, or remote action occurred.

## Visual Receipts

Accepted PNGs live outside the Git worktree under:

`C:\Users\LENOVO\.codex\visualizations\2026\07\20\019f7e98-6c47-76f1-829e-7c1764c47f9c\terminal-ui-registry-phase5-20260720`

| Receipt | SHA-256 |
| --- | --- |
| Data admin expanded desktop | `92120065bf4b605cfce0a0a5f1282f4247b9bc02e5601bec23a6d61257a37d01` |
| Data admin collapsed desktop | `2703b0af202e87bc7bba572dc4f9d8cddd79a9be1bdadfc2881309771ac64f0f` |
| Data readonly expanded desktop | `2f62d3186f88f3c32dbee3ed8f6d5ae5ebf4a73f3964842245949a93bb6657f8` |
| Data readonly collapsed desktop | `02398bf813f89079b23242d2cc1f594931860b8e4cf4d4944a4b1205e55a8c38` |
| Review collapsed, Focus + drilldown | `f5bd1297cbc5a91f7495c0ae838bc97118558f4553355f3c60688eac58bf6b1e` |
| Review QQQ context | `8756105e39b3462082f1a36028af6643ccdf90f05ddfbd5ac1b6b31bee2dde08` |
| Backtest narrow, 44 signals | `1ffda2e8738d8c47ee44e3dc46f00dbce8c3ecc2b16e14c71043371f085e8676` |
| Teaching narrow, full reveal | `ef9708523cf864fc6e8aa4f3daf0befcf1bc1b210d5902a55d5e60306c8e061d` |
| Admin narrow expanded | `1e69d9238a84f1d4f47fae53e1d0dd125c42a55936713365881b913dcaf2625f` |
| Readonly inspect narrow collapsed | `8d8afcbc21dc617949f73e4971b1444e58a02ebc808fd3017cc76be6ec9f9b79` |
| Login narrow error focus | `b057a3a819ea2b07ea16b1fdd3fad08fb9268b072bd068f47285333e82c7b045` |
| Static legacy QQQ narrow | `0f9515a098cc94159dd99aac52dcef69d547ff357e53ee3a4c0ae5a99af6c494` |

Phase 5 exits complete with the unchanged baseline environment failure explicitly carried. The implementation is ready to freeze for independent review.
