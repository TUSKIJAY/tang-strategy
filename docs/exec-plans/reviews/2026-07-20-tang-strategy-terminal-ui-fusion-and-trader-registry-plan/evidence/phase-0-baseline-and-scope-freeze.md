# Phase 0 Baseline And Scope Freeze

- Plan: `2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan`
- Revision: `v2-review-foldback-2026-07-20`
- Work unit: `phase-0`
- Baseline HEAD: `3f589a027d3c1351672660ab8f4e9157a792821e`
- Implementation start: `user-instruction:2026-07-20-execute-terminal-ui-registry-plan`
- Phase 0 checkpoint authority: `user-instruction:2026-07-20-commit-activation-with-next-phase`
- Browser capture root: `output/playwright/terminal-ui-registry-phase0-20260720/` at capture time; after visual inspection the generated set was moved outside the Git worktree to `C:\Users\LENOVO\.codex\visualizations\2026\07\20\019f7e98-6c47-76f1-829e-7c1764c47f9c\terminal-ui-registry-phase0-20260720\` so v2 unrelated-dirty postflight remains exact

## Entry And Dirty-Scope Result

The previously completed activation product was pre-dirty at session entry and therefore could not be retroactively represented as a v2 baseline-preflight checkpoint. It was verified under the still-v1 lifecycle contract and committed separately as scoped legacy-compatible activation commit `3f589a027d3c1351672660ab8f4e9157a792821e`. Phase 0 then opened from a clean index/worktree baseline. The Phase 0 durable-checkpoint baseline receipt has request identity `981a3393179c79e2ee5ecac50c7e67e66313c21a838db430a96afc885bcf7f03` and zero unrelated dirty paths.

Generated Playwright screenshots and Vite output are excluded from checkpoint staging. No pre-existing user path remains in the Phase 0 worktree baseline.

## Frozen Product Contract

The exact shared product-chrome tokens remain the approved values:

| Role | Token | Value |
| --- | --- | --- |
| App canvas | `--surface-app` | `#141413` |
| Panel | `--surface-panel` | `#1E1E1D` |
| Control | `--surface-control` | `#282827` |
| Raised/hover | `--surface-raised` | `#333331` |
| Decorative border | `--border-subtle` | `#3B3B38` |
| Control border | `--border-control` | `#74746E` |
| Primary text | `--text-primary` | `#E8E7E3` |
| Secondary text | `--text-secondary` | `#C9C8C2` |
| Muted text | `--text-muted` | `#A7A69F` |
| Product accent | `--accent` | `#8B9A6D` |
| Accent ink | `--accent-ink` | `#0F0F0E` |
| Success | `--status-success` | `#4CAF50` |
| Danger | `--status-danger` | `#E06B66` |
| Warning | `--status-warning` | `#C9A45C` |
| Brand-only warm mark | `--brand-warm` | `#A6532A` |

Frozen contrast pairs are primary/panel `13.48:1`, muted/panel `6.83:1`, accent-ink/accent `6.34:1`, accent/panel `5.51:1`, success/panel `6.00:1`, danger/panel `5.14:1`, warning/panel `7.11:1`, and white/brand-warm `5.40:1`. Browser phases must verify computed colors, focus visibility, and non-color cues.

Warm orange is allowed only on `.brand-mark`. Chart moving-average colors, signal colors, trader-owned colors, and CALL/PUT shapes remain domain-owned. Typography, K-line theme switching, route IDs, session behavior, business controls, and page layout are not theme-migration targets.

## Current Consumer Map

Baseline `frontend/src/styles.css` SHA-256 is `3530eeb4b5f9fce446abdb323389dbeb02f956d0e80ef68954976f9a6d13253f` (35,783 bytes).

- Paper root values are at `:root`, `body`, generic `select/input`, `.login-card`, `.metric/.panel`, `.table/.row`, `.engine-side button`, `.trade-leg`, `.tp-editor`, and `.tp-registry`.
- Review is rooted at `.dr-shell`; interactive/static use the same `.dr-app`, `.dr-sidebar`, `.dr-chart-area`, ticker/date/strategy controls, shared trade components, and K-line engine.
- The current dark patch family begins at `.dr-sidebar .trade-filter-panel` and separately overrides the shared filter/list components because their defaults are light.
- Data, Backtest, Teaching, Login, and Admin already expose semantic page/panel classes sufficient for a CSS-only chrome migration. They do not require page-component edits.
- Current shell uses upper `nav` items for Data/Review/Backtest/Teaching and a separate bottom `.secondary` button with `RefreshCcw` for trader records. The frozen target keeps the bottom placement but uses the same renderer/classes/state/accessibility contract and a `UsersRound` icon.

Legacy paper-chrome values currently present and required to disappear from product chrome are `--paper`, light `--panel`, `#F7F1E6`, `#FFFAF0`, `#FFFDF7`, `#FFF7DB`, `#EADCC6`, `#FFF7E8`, `#F8EAD1`, `#C8BDA8`, and `rgba(255, 250, 240, ...)`. Deliberate light chart mode inside the K-line engine is outside this chrome scan.

## Registry Boundary And Fixtures

The implementation remains frontend-only. Existing admin GET/PUT routes, full-document save, canonical repository validation, atomic replace, candidate projection, and rollback path are reused without backend changes.

Frozen create fixtures:

- slug accepts `ab` and a 64-character lowercase slug; rejects one character, 65 characters, uppercase, leading digit, and hyphen under exact `^[a-z][a-z0-9_]{1,63}$`;
- color accepts exact `^#[0-9A-Fa-f]{6}$`; missing `#`, short/long, and non-hex values reject without silent rewrite;
- display name trims surrounding whitespace and rejects blank;
- ID, color (case-insensitive canonical comparison), and non-negative integer sort order must be unique; negative/non-integer order rejects;
- sort order may default to the next free multiple of ten without renumbering existing rows; identity/color are never generated;
- unsaved rows may be removed, persisted IDs remain immutable, and append preserves every existing row/value;
- JSON FastAPI `detail`, raw-text paths, unknown index/field, root-level, invalid JSON, and no-path server errors are separately pinned;
- failed save retains the complete draft; success clears create state only after canonical reload;
- registry-only traders create no market day/group/leg/event/outcome/context and remain absent from availability-driven Review/Static controls.

## Exact Implementation Manifest

### Add

- `frontend/src/features/review/traderRegistry.js`
- `frontend/src/features/review/traderRegistry.test.js`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-0-baseline-and-scope-freeze.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-1-terminal-tokens-and-navigation.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-2-page-chrome-migration.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-3-review-panel-fusion.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-4-create-trader-flow.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-5-integrated-acceptance.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/implementation-review-packet-001.md`
- one independently authored `implementation-review-NNN.md` and any bounded remediation evidence required by its verdict

### Modify

- `frontend/src/components/Layout.jsx`
- `frontend/src/pages/AdminTradersPage.jsx`
- `frontend/src/features/review/tradeRecords.test.js`
- `frontend/src/features/review/reviewWorkspace.test.js`
- `frontend/src/styles.css`
- `frontend/package.json`
- `docs/architecture.md`
- the canonical plan plus `active/index.md`, `PROGRESS.md`, and `HANDOFF.md` at phase transitions
- `reviews/index.md`, `docs/exec-plans/roadmap.md`, the source optimization record/index, and completed index only when review/closeout changes their derived truth

### Remove Or Move

- no frontend, backend, schema, content, data, route, workflow, exporter, or screenshot source is removed;
- closeout moves exactly this canonical plan from `active/` to `completed/` after independent `accept`.

Explicitly excluded source paths include every backend file, content/schema/data file, page component other than `AdminTradersPage.jsx`, shared trade component, K-line engine, API client, `main.jsx`, daily runbook, publisher workflow, and static exporter. Requiring any excluded source change is a plan-revision stop.

## Protected Baseline

| Boundary | SHA-256 / count |
| --- | --- |
| tracked SQLite | `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` / 25,702,400 bytes / 49 market days |
| canonical registry | `9668400f2c3b9b514465e120e5e64e65350396ec5022f91de82f59b3a0553734` / 2 traders |
| 22 canonical day documents | manifest `3a09591cd5ff07317d49daf1f8c221d3634253b8b79429d1471fd3f1dcd1f525` / 87,403 bytes |
| backend routes | `27fb1fe71eb32828c8b0a14a5e9c01e24ff588c0d433aad9410781b1e33313b9` |
| trade service | `6fd508b7843761e60014a75b4ab57b0a0f3fe2d933080691cda7c8e547c4a4b4` |
| trader schema | `fcd9dcdf0e8396c9e0670aa95f252158e85a0c0895d1260a6b46c6710499f17b` |
| Pages publisher | `baaf5ad092bf35d29a6a33ba9083c82768bcb6c4c80169d83fdcf5c8370d5b37` |
| static exporter | `e3f66de6647de587ca34e5b145607dfa8b3f60a16af19f567f85bc8e003500cb` |
| daily runbook | `08f7bc1e2f58f8108ae9808174f78cbcc238f60af710cb2a63feb290be87f748` |
| SQLite integrity/FK | `ok` / `0` |

## Before-State Browser Evidence

Sixteen PNGs cover Login, Data, Review, Backtest, Teaching, Admin, interactive/static, desktop `1672x941`, narrow `820x1180`, and expanded/collapsed shell states. Their sorted filename/hash manifest SHA-256 is `a3156a6e564a40bfab7bb09f3233a6b57790cbb5cfd57ad549afe1651b5b6bb1` (5,284,817 bytes). Visual inspection confirms the three-family baseline: paper app chrome, a charcoal/olive Review island, and a warm-orange bottom trader CTA. Interactive console ended with zero errors; Static Review had only the existing missing `favicon.ico` 404.

## Baseline Verification

| Check | Result |
| --- | --- |
| frontend `test:trade-records` | pass, 38/38 |
| normal/static Vite builds | pass, 1,754 modules each |
| operating-mode fixtures | pass, 171/171 |
| governed/auto harness and direct operating checker | pass |
| startup budget | pass; `PROGRESS.md` remains archive-recommended but below hard limit |
| backend `test_trade_records.py` | 20/21 pass; one known Windows/Python 3.14 temporary SQLite teardown lock after its product assertions, reproduced before frontend source edits and classified as baseline environment failure |
| SQLite integrity / foreign keys | pass, `ok` / `0` |
| Playwright before matrix | pass; 16 screenshots, interactive console 0 product errors, static favicon-only 404 |
| `git diff --check` | pass |

Phase 0 exit is satisfied: the exact frontend/docs surface is frozen, no backend/route/schema/data/publisher change is required, every baseline check is truthfully classified, and generated/browser evidence is excluded from checkpoint staging.
