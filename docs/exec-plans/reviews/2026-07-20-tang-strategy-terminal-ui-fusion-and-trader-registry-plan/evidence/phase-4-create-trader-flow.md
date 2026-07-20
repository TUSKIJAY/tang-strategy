# Phase 4 — Create Trader Flow Evidence

- Plan revision: `v2-review-foldback-2026-07-20`
- Phase disposition: `complete`
- Entry gate: verified Phase 3 exit
- Acceptance environment: isolated copy at `C:\Users\LENOVO\AppData\Local\Temp\tang-phase4-isolated-20260720-0912`
- Canonical mutation authority: none

## Implemented Scope

- Added `traderRegistry.js` as the pure registry boundary for the exact slug/color/order contract, append-only creation, unsaved-row removal, and recognized server-error association.
- Added the explicit admin-only `新增交易者` action and complete draft fields for `trader_id`, display name, color, active, and sort order.
- Preserved every persisted `trader_id` as immutable while keeping a staged unsaved ID editable and removable before save.
- Continued to submit one complete registry document through the existing PUT. Create state clears only after a successful canonical reload.
- Changed no backend, route, schema, content, data, publisher, exporter, or API-client source.

## Deterministic Contracts

- `npm run test:trade-records`: `46/46` pass. The seven new registry tests pin exact 2/64-character slug boundaries, exact `#RRGGBB`, trim/blank handling, case-insensitive color uniqueness, non-negative unique integer orders, next-free-multiple-of-ten defaults without renumbering, append preservation, unsaved removal, and server-error mapping.
- Normal and Static Review Vite builds: pass, 1,755 modules each.
- `git diff --check`: pass.

## Real Browser Matrix

Playwright drove the isolated interactive stack and verified:

- invalid `A`, blank display, missing-`#` color, and duplicate order produce four inline alerts and focus the first invalid control without losing input;
- a valid `codex_demo` row can be staged, visibly marked `未保存`, removed without touching the two persisted rows, then staged again;
- a real FastAPI JSON `detail` rejection maps to `registry.traders[0].display_name`, retains the complete draft, and focuses the matching control;
- a mocked raw-text `registry.traders[0].color` rejection maps only to that control and retains the complete draft;
- an unmapped plain-text `503` remains form-level and does not mark an unrelated field invalid;
- real save returns `注册表已保存。`, reloads three canonical rows, renders `codex_demo` as an immutable persisted ID, disables save, and re-enables creation;
- readonly login exposes inspection/export only and renders neither trader registry nor point editor;
- the registry-only trader is absent from interactive and Static Review availability controls and adds no group.

The only browser console noise was the existing missing `favicon.ico` plus expected rejected-request entries deliberately induced by the negative-path matrix; there were no application exceptions.

## Isolation And Protected Baseline

The isolated accepted copy contains the original two rows byte-for-value plus `codex_demo / Codex Demo / #3366CC / active / 30`. Its SQLite integrity is `ok`, foreign-key check is empty, and `codex_demo` owns exactly one registry row with zero groups, legs, events, or outcomes. The isolated and canonical `content/trades/*.json` sets remain an exact 22-file match.

Canonical protected boundaries remain equal to the Phase 0 baseline:

| Boundary | Current evidence |
| --- | --- |
| tracked SQLite | `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` |
| canonical registry | `9668400f2c3b9b514465e120e5e64e65350396ec5022f91de82f59b3a0553734` |
| backend routes | `27fb1fe71eb32828c8b0a14a5e9c01e24ff588c0d433aad9410781b1e33313b9` |
| trade service | `6fd508b7843761e60014a75b4ab57b0a0f3fe2d933080691cda7c8e547c4a4b4` |
| trader schema | `fcd9dcdf0e8396c9e0670aa95f252158e85a0c0895d1260a6b46c6710499f17b` |
| Pages publisher | `baaf5ad092bf35d29a6a33ba9083c82768bcb6c4c80169d83fdcf5c8370d5b37` |
| static exporter | `e3f66de6647de587ca34e5b145607dfa8b3f60a16af19f567f85bc8e003500cb` |
| daily runbook | `08f7bc1e2f58f8108ae9808174f78cbcc238f60af710cb2a63feb290be87f748` |

## Visual Receipts

Accepted PNGs live outside the Git worktree under:

`C:\Users\LENOVO\.codex\visualizations\2026\07\20\019f7e98-6c47-76f1-829e-7c1764c47f9c\terminal-ui-registry-phase4-20260720`

| Receipt | SHA-256 |
| --- | --- |
| Invalid create fields | `23cc661ab515c9cab05217bf501f96c11878646ff6a9a30c7e09f489ce5ea066` |
| Staged unsaved row | `245f8eace8a2c4a8cbb0a587ced3970fcbb3bb92c5841515caee3fc28bca23a2` |
| JSON detail field rejection | `5fe354c8267d43cfadb51762de92668588e81b9804d9aed65cadcd01f8b1403d` |
| Raw-text field rejection | `3d37a6d070f1d8ca9e8cdce8e6fbba7d6938cadc6a14354abc196f875a51c855` |
| Unmapped form error | `9d0e44b2b37aca518e9ea7445d773d7dbf7523009b1b9aee814145fe998606a2` |
| Successful save plus reload | `2277de5184f123d9e0d01badaf4bb654b944ba0b84e3cb8e21c324631db8dcee` |
| Registry-only trader hidden in Review | `21405a672b37397d310ff7ec2a7f95fbab0095a2136fe48fba2224be76a2f900` |
| Registry-only trader hidden in Static Review | `f33f8a3a47fbf2e875e1ff0d276cdc1774518f1cd3dbb51aec9cd83c1d4a14bc` |
| Readonly user receives no editors | `b779aaba657d1b88bbc4d4a73e41908db915e97a3ed0bc0b2e927d611715627d` |

Phase 4 exits complete. Phase 5 may now run the full regression, integrated responsive/accessibility browser matrix, protected-boundary comparison, and architecture/state closeout preparation.
