# Tang Strategy Terminal UI Fusion And Trader Registry

- Lifecycle schema: `operating-modes-v1`
- Status: Completed
- Plan slug: `2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan`
- Revision: `v2-review-foldback-2026-07-20`
- Plan author ID: `codex-plan-author-2026-07-20-terminal-ui-registry`
- Design reviews: docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/review-001.md@revise@v1-proposal-2026-07-20, docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/review-002.md@approve@v2-review-foldback-2026-07-20
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-20-activate-terminal-ui-trader-registry`
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: `../reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/implementation-review-002.md@accept`
- Final disposition: Completed
- Verified implementation commit: `43b96ab9c8ffffad2e76191b0d31d45e277afddc`
- Lifecycle reconciliation commit: `43b96ab9c8ffffad2e76191b0d31d45e277afddc`
- Owner: Codex
- Created: 2026-07-20
- Optimization source: `docs/optimization/2026-07-20-trader-workspace-nav-and-registry/2026-07-20-trader-workspace-nav-and-registry.md`
- Scope authority: `user-instruction:2026-07-20-execute-terminal-ui-registry-plan` authorized local Phase 0-6 implementation, verification, remediation, lifecycle closeout, and isolated temporary-copy acceptance; `user-instruction:2026-07-20-commit-activation-with-next-phase` authorized the consumed Phase 0 scoped commit; `user-instruction:2026-07-20-commit-and-push-terminal-ui-registry` is consumed by implementation/lifecycle commit `43b96ab9c8ffffad2e76191b0d31d45e277afddc`, this boundary-metadata commit, and the final push of `codex/project-harness`. Canonical data writes, further push, PR, merge, Pages publication, provider/broker access, hosted verification, and remote administration remain unauthorized

## 1. Context And Evidence

### 1.1 Proposal provenance

This plan converts the user-named optimization batch into one governed Lane 3 proposal. It was drafted from live repository evidence at `codex/project-harness@115d2cfee1d7e408b5ecd4465db73064c0d717b5`. The worktree already contained user-owned optimization reorganization and lifecycle-document edits; those unrelated or prior edits remain outside this plan's implementation authority and must be preserved.

The source batch contains six locally verified screenshots covering the expanded/collapsed shell, Review trade panel, app-wide color mismatch, and edit-only registry. Their recorded SHA-256 values match the files under the batch's `screenshots/` directory.

### 1.2 Current repository facts

- `frontend/src/styles.css` currently has three product-chrome families: warm paper root tokens (`--paper`, `--panel`, `--accent`), a warm-brown app sidebar, and a large charcoal/olive `.dr-*` Review island. Generic inputs still default to light backgrounds.
- `frontend/src/components/Layout.jsx` renders Data, Review, Backtest, and Teaching as one nav stack, but renders `交易记录 / 点位管理` separately as an orange `.secondary` button using a refresh icon. Its collapsed geometry and role badge are not peer-nav behavior.
- `TraderFilters`, `TradeExportControls`, and `TraderTradeList` are shared by interactive and static Review. Their light defaults are partially patched under `.dr-sidebar`, leaving the Eligibility select and adjacent controls visually inconsistent with the upper Review context controls.
- Data, Admin, Backtest, Teaching, and Login inherit the paper defaults. Interactive and static Review root at `.dr-shell` and use the existing terminal family.
- `AdminTradersPage.jsx` loads the canonical registry only for admins and can update metadata for existing rows, but it exposes no create-trader action or editable new `trader_id` field.
- The backend already supplies the required create boundary. `GET/PUT /api/admin/traders` are admin-only; `validate_trader_registry` requires a user-supplied stable lowercase slug matching exact regex `^[a-z][a-z0-9_]{1,63}$` (total length 2–64), a non-empty display name, a unique color matching exact regex `^#[0-9A-Fa-f]{6}$`, a boolean active flag, and a unique non-negative sort order. The PUT validates every canonical trade day before atomic replacement and then projects through the existing rollback-coherent path.
- Existing backend coverage already proves a third registry entry can be accepted, duplicate identity/color/order fails closed, readonly canonical reads are denied, and atomic content/projection failure does not leave a split boundary.
- Existing frontend source-contract tests explicitly pin light Admin button backgrounds and `.dr-sidebar` overrides. Those assertions must migrate with the visual contract instead of being weakened or deleted without replacement.
- Live protected baselines at proposal time are: tracked SQLite `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0`, canonical trader registry `9668400f2c3b9b514465e120e5e64e65350396ec5022f91de82f59b3a0553734`, Pages publisher `baaf5ad092bf35d29a6a33ba9083c82768bcb6c4c80169d83fdcf5c8370d5b37`, and static exporter `e3f66de6647de587ca34e5b145607dfa8b3f60a16af19f567f85bc8e003500cb`. Phase 0 must recapture rather than assume these values remain current.

### 1.3 Why one Lane 3 plan

OPT-004 owns the app-wide terminal-first palette. OPT-001 and OPT-003 are nested consumers of that same palette, while OPT-002 changes an admin workflow that persists the complete canonical trader registry. Separating the visual items would duplicate token migration and acceptance; implementing create-trader as an unplanned follow-up would under-specify the user-named batch. One plan therefore owns all four items, while separate phases and exit gates keep visual migration and registry mutation independently reviewable.

The work is broad, multi-page, accessibility-sensitive, and touches a canonical-content write workflow even though no backend, schema, DB, market-data, or publication contract is intended to change. Coding Mode Lane 3 is required.

### 1.4 `review-001` foldback

Independent `review-001` returned `revise/high` against frozen revision `v1-proposal-2026-07-20` at SHA-256 `c2c209275e69a7643a1bcce9577651af8e207b34e3571ac22e8b7cdd153a923f`. Revision `v2-review-foldback-2026-07-20` folds every finding into the operative contract:

- replace the invented trader identity range with the live validator/schema regex `^[a-z][a-z0-9_]{1,63}$`, and pin its 2/64-character boundary cases in the pure helper fixtures;
- freeze color as exact `^#[0-9A-Fa-f]{6}$`, including the required leading `#`, while retaining server-authoritative validation;
- map server field errors only after inspecting the current API error body as FastAPI JSON `detail` or raw text for `registry.traders[<index>].<field>`; unrecognized bodies remain form-level alerts;
- keep the trader workspace bottom-pinned in its current left-rail location, but render it through the same peer-nav class/state/accessibility contract as the four upper destinations;
- keep the `test:trade-records` carrier name stable and expand only its `node --test` file list to include `traderRegistry.test.js`.

At the v2 foldback freeze, the plan remained Proposed and review-only. `review-001` targeted only v1 and did not qualify v2 for activation; the then-next gate was an independent design review of exact v2.

### 1.5 `review-002` approval

Independent `review-002` returned `approve/high` with no findings against exact revision `v2-review-foldback-2026-07-20` at reviewed SHA-256 `40afdcfd1eb98594a8f4816ad652411ca8957c371cfc8a315b975bcaf3dad12e`. It rechecked every `review-001` closure, the live slug/color validators and schema, JSON-`detail`/raw error carrier, bottom-pinned navigation structure, name-stable test carrier, protected hashes, token contrast, phase gates, and authority boundaries. No design-contract or revision change is required from `review-002`.

The plan remained Proposed and review-only after approval until the separate activation instruction recorded below. Design approval did not itself grant activation or implementation authority.

### 1.6 Activation recording

The user instruction `user-instruction:2026-07-20-activate-terminal-ui-trader-registry` authorizes exactly the adjacent lifecycle move from Proposed to Active for revision `v2-review-foldback-2026-07-20`. The plan is now recorded at `phase-0:not-started` with next gate `phase-0-start`.

This activation does not start Phase 0 or authorize implementation, Git stage/commit/push, canonical data writes, provider/broker access, Pages publication, hosted verification, or remote administration. A later explicit implementation-start instruction is still required.

### 1.7 Implementation start

The user instruction `user-instruction:2026-07-20-execute-terminal-ui-registry-plan` authorizes end-to-end local execution of this exact active revision through implementation, verification, remediation when required, independent implementation review, and lifecycle closeout. Phase 0 is now `in-progress` with next gate `phase-0-exit`.

The follow-up `user-instruction:2026-07-20-commit-activation-with-next-phase` authorizes one scoped Phase 0 local checkpoint after its exit gate. This authority includes isolated temporary-content/SQLite acceptance needed by the plan, but it does not authorize canonical content or tracked-DB writes, push, PR, merge, Pages publication, hosted verification, provider/broker access, or remote administration.

### 1.8 Phase 0 exit and schema compatibility decision

Phase 0 completed against clean baseline `3f589a027d3c1351672660ab8f4e9157a792821e`. The exact manifest, terminal token/contrast table, registry fixtures, protected hashes/counts, 16-image before-state browser matrix, and pass/fail classification are frozen in `evidence/phase-0-baseline-and-scope-freeze.md`. No backend, route, schema, data, publisher, exporter, API-client, K-line, or excluded page-component change is required.

The authorized Phase 0 commit `3d9a67cede36496d787bf4f2b34e16f69b3ca78d` passed its exact request postflight. A first-transition v2 migration was attempted in that commit, but the live repository audit then exposed a pre-existing checker incompatibility: `scripts/check-durable-checkpoint.py` applies v2 checkpoint ancestry to the append-only v1 design reviews and cannot resolve their accepted repository-relative paths. This contradicts `docs/operating-modes.md` §10's explicit v1-review compatibility rule.

The governance checker is outside this frontend plan's frozen scope. Rather than expand scope or rewrite historical reviews, the current plan remains `operating-modes-v1` for implementation and closeout. The scoped local Phase 0 commit remains real evidence; it is not represented as a currently claimed v2 checkpoint. Phase 1 is ready but not started.

### 1.9 Phase 1 start

Phase 1 started under the standing local implementation authority `user-instruction:2026-07-20-execute-terminal-ui-registry-plan` after the Phase 0 exit evidence and commit were verified. Its exact source scope is `frontend/src/styles.css`, `frontend/src/components/Layout.jsx`, and the existing source-contract test carriers; it may not enter Phase 2 page-specific or Phase 4 registry-create behavior.

### 1.10 Phases 1–3 visual exits

Phases 1–3 completed in order under the same local implementation authority. Phase 1 established the exact 15-token root contract and one five-destination peer navigation renderer with brand-warm restricted to `.brand-mark`. Phase 2 migrated Login, Data, Backtest, Teaching, and Admin chrome without changing their page components or behavior. Phase 3 removed the shared-light-plus-Review-patch palette duplication, leaving only Review density overrides while preserving interactive/static workspace, availability, export, hash, and mutation-free contracts.

The deterministic carriers, both Vite builds, computed browser styles, focus/current behavior, desktop/narrow overflow, SPY↔QQQ transitions, empty state, drilldown, and Static current/legacy hashes passed. Exact receipts are frozen in `evidence/phase-1-terminal-tokens-and-navigation.md`, `evidence/phase-2-page-chrome-migration.md`, and `evidence/phase-3-review-panel-fusion.md`.

### 1.11 Phase 4 create-trader exit

Phase 4 added the pure `traderRegistry.js` contract and admin-only inline create draft while reusing the existing complete-document registry PUT. The isolated browser matrix covered exact client boundaries, staged removal, real JSON-`detail` rejection, raw recognized rejection, unmapped form fallback, successful reload, immutable persisted IDs, readonly denial, and interactive/static no-group visibility. The isolated accepted copy contains `codex_demo` with zero groups/legs/events/outcomes; canonical tracked registry, content, and DB remain Phase 0 byte-exact. Evidence is `evidence/phase-4-create-trader-flow.md`.

### 1.12 Phase 5 integrated acceptance exit

Phase 5 resolved OPT-001 through OPT-004 against the six durable source screenshots and completed the fresh expanded/collapsed admin/readonly, desktop/narrow, Login/Data/Review/Static/Backtest/Teaching/Admin matrix. Review export produced the expected JSON plus three CSV files, Backtest returned 10 rows/44 signals, Teaching advanced and revealed the full day, Static normalized the legacy QQQ hash without any admin API, and every probed layout had zero horizontal overflow.

Frontend 46/46, lifecycle 171/171, governed/auto/direct harness checks, compileall, both 1,755-module builds, SQLite integrity/FK, protected hashes/counts, stale-paper scan, and `git diff --check` pass. The full backend suite remains 77/78 because the exact Phase 0 Windows SQLite temporary-file teardown lock occurs after product assertions; it reproduces under isolated Python 3.12 with the full pinned TV runtime and no backend source diff. This unchanged baseline environment failure is retained truthfully in `evidence/phase-5-integrated-acceptance.md` and does not expand the frozen frontend/docs scope.

### 1.13 Phase 6 start

Phase 6 started after the verified Phase 5 exit. `docs/architecture.md` now records the shared terminal/navigation and registry-create ownership contracts. The next gate is a frozen implementation/evidence packet followed by an independently authored implementation review of that exact target. No later phase commit, canonical data write, push, PR, Pages publication, provider/broker access, or remote action is authorized.

### 1.14 Implementation review 001 and remediation-1

Independent `implementation-review-001` returned `revise/high` against exact frozen target `terminal-ui-registry-v1:3c73a671ab10d315dac42c0d923192638b1c1bfffa25bd6ece2cb8313a282440@3d9a67cede36496d787bf4f2b34e16f69b3ca78d`. It found no implementation-source defect and independently matched all 19 manifest hashes, the aggregate, frontend 46/46, protected data/source boundaries, and authority claims. Closeout remained blocked by two lifecycle-receipt findings: active index Evidence linked Phase 5 rather than the latest direct review, and three HANDOFF surfaces still instructed a Phase 1/v2-schema resume.

Remediation-1 changed only lifecycle/evidence surfaces. The active index now resolves to `implementation-review-001`, the reviews index includes that artifact with `revise`, HANDOFF consistently names `phase-6:in-progress` under `operating-modes-v1`, and the Phase 5 evidence explicitly retracts checker claims invalidated by the later index mutation. Fresh direct operating, governed, auto, and diff checks pass. Exact receipts are in `evidence/remediation-1-lifecycle-reconciliation.md`; a new non-self-referential target must receive follow-up independent `accept` before closeout.

### 1.15 Implementation review 002 acceptance and closeout

Independent `implementation-review-002` returned `accept/high` with no findings against exact target `terminal-ui-registry-v1-remediation-1:606b9434b80e32da99e68cbf51cab5a9cd6b8bd208ee9feee98325dabe2a4ae8@3d9a67cede36496d787bf4f2b34e16f69b3ca78d`. It independently matched all 23 manifest hashes and the aggregate, confirmed the packet-001 frontend subset remained byte-identical, closed both prior findings, and reran direct/governed/auto plus 46/46 frontend checks. Protected data/source and the empty Git index also passed.

All Phase 0–6 exit gates are satisfied. This plan is Completed with next gate `closed`. The accepted implementation and lifecycle closeout are committed at `43b96ab9c8ffffad2e76191b0d31d45e277afddc`; the separately authorized current-branch push includes the immediate boundary-metadata commit containing this record. No further commit/push, PR, merge, Pages, canonical-data, provider/broker, hosted, or other remote authority remains.

## 2. Objective And Success Criteria

### 2.1 Objective

Create one terminal-first Tang Strategy product skin across shell and application pages, fuse the trader workspace and Review trade panel into that system, and give admins a discoverable, validated way to add a trader through the existing canonical registry boundary without fabricating trade data or expanding authority.

### 2.2 Success criteria

1. Shell, Data, Review, Backtest, Teaching, Admin, and Login use one recognizable charcoal/neutral/olive product palette. K-line remains the densest dark region of that palette, not a second page brand.
2. Shared product chrome uses the exact token contract in section 3.1. Legacy cream paper values are absent from default application chrome; any deliberate exception must be named in the Phase 0 manifest and independently reviewed.
3. Warm orange is limited to the brand mark or an explicitly documented semantic mark. It is not a destination-button skin, generic action color, page background, or competing accent family.
4. `交易记录 / 点位管理` remains bottom-pinned at the foot of the left rail but is a peer destination in the primary nav model, with the same renderer, geometry, hover/active treatment, collapsed alignment, and keyboard behavior as Data/Review/Backtest/Teaching. Its icon and accessible name communicate traders/records rather than refresh.
5. Admin/readonly capability remains visible without relying on orange fill or color alone. Every active destination exposes a programmatic current-page state; collapsed mode preserves an accessible name and contains no overflowing label/badge.
6. Interactive Review reads as one continuous left-column surface from ticker/date/strategy through Eligibility, trader selection/focus, export, group cards, and drilldown. No light paper select or bolted-on card skin remains.
7. Static Review inherits the same Review panel tokens and interaction states while remaining mutation-free and free of authenticated Admin/API entry points.
8. An admin can find `新增交易者`, enter an immutable stable lowercase `trader_id` matching `^[a-z][a-z0-9_]{1,63}$` plus display name, unique color matching `^#[0-9A-Fa-f]{6}$`, active flag, and unique sort order, add it to the full registry draft, and explicitly persist it through the existing save path.
9. `trader_id` is user-entered, never silently generated, and remains editable only while the new row is unsaved. Existing persisted IDs remain immutable. The UI may prefill the next free sort order, but it must not renumber existing traders.
10. Invalid slug, blank display name, malformed/duplicate color, duplicate ID, and duplicate/negative sort order produce field-level or clearly associated form errors. The pure helper pins the same exact slug/color regexes and their length/leading-`#` boundaries; client validation is advisory, the server remains authoritative, and server rejection retains the unsaved draft.
11. Successful create reloads the canonical registry and shows the new trader. It creates no market day, trade group, leg, event, outcome, note context, or synthetic availability. Review/Static trader controls continue to hide registry-only traders on ticker/dates with no displayable group.
12. Readonly users never load or render registry mutation controls. No delete-trader, rename-ID, bulk reorder, role change, raw JSON editor, auto-save, or retry-on-failure behavior is introduced.
13. Desktop `1672x941` and narrow `820x1180` acceptance covers expanded/collapsed shell, Data, Review, Backtest, Teaching, Admin, Login, and Static Review as applicable. Focus, labels, contrast, announcements, overflow, and keyboard order remain usable.
14. Existing workspace, availability, export, chart, strategy, auth, canonical-write, projection, rollback, static hash, and daily publication contracts remain unchanged.

### 2.3 Non-goals

- No backend route, role, schema, validator, database, market-data, provider, broker, exporter, workflow, or Pages change.
- No canonical trader or trade-day content change during implementation or acceptance; successful mutation tests use isolated copies and prove tracked bytes remain unchanged.
- No new trader deletion, persisted-ID rename, drag reorder, profile/avatar system, credentials, invitation, or per-trader authorization model.
- No typography, information-architecture, K-line engine behavior, signal palette, trader-owned marker color, strategy logic, or page-feature redesign beyond the named fusion work.
- No static Admin surface and no authenticated mutation entry in Static Review.
- No automatic lifecycle activation, implementation start, stage/commit/push, PR, merge, publication, hosted verification, or other remote action.

## 3. Target Contracts

### 3.1 Terminal-first token contract

The v1 implementation target is the following shared product-chrome table, derived from the accepted Review family. Phase 0 must freeze the CSS variable names and consumer map; changing these values or creating a second page-level theme after design approval requires a plan revision.

| Role | Token | Value | Intended use |
| --- | --- | --- | --- |
| App canvas | `--surface-app` | `#141413` | body, main canvas, Review/chart surround |
| Panel | `--surface-panel` | `#1E1E1D` | sidebar, cards, page panels |
| Control | `--surface-control` | `#282827` | inputs, buttons, tabs, compact controls |
| Raised/hover | `--surface-raised` | `#333331` | hover, selected-neutral, nested surfaces |
| Decorative border | `--border-subtle` | `#3B3B38` | non-essential separators |
| Control border | `--border-control` | `#74746E` | boundaries that must remain perceivable |
| Primary text | `--text-primary` | `#E8E7E3` | body and primary labels |
| Secondary text | `--text-secondary` | `#C9C8C2` | secondary labels and values |
| Muted text | `--text-muted` | `#A7A69F` | hints and metadata, not disabled-only meaning |
| Product accent | `--accent` | `#8B9A6D` | active/focus/primary product interaction |
| Accent ink | `--accent-ink` | `#0F0F0E` | text/icons on accent fill |
| Success | `--status-success` | `#4CAF50` | success state plus text/icon cue |
| Danger text | `--status-danger` | `#E06B66` | readable error text plus alert cue |
| Warning | `--status-warning` | `#C9A45C` | warning/pending plus text/icon cue |
| Brand-only warm mark | `--brand-warm` | `#A6532A` | `TS` brand mark only unless review approves one named exception |

Initial contrast calculations are at least `13.48:1` for primary text on panel, `6.83:1` for muted text on panel, `6.34:1` for accent ink on accent, `5.51:1` for accent on panel, `6.00:1` for success on panel, `5.14:1` for danger on panel, `7.11:1` for warning on panel, and `5.40:1` for white brand initials on the warm mark. Browser acceptance must verify computed colors, focus visibility, and non-color cues rather than treating this calculation as sufficient evidence.

Legacy `--paper`, light `--panel`, `#f7f1e6`, `#fffaf0`, `#fffdf7`, and equivalent cream chrome must have zero unreviewed product-chrome consumers at the integrated exit gate. Chart/signal/trader colors remain domain-owned and are not mechanically remapped to the product accent.

### 3.2 Shell and navigation contract

- Keep the trader workspace bottom-pinned after the sidebar's flexible spacer, rather than inserting it into the upper Data→Teaching visual order, while promoting it into the primary nav model as the fifth peer destination. Use a trader/records icon such as `UsersRound`; do not retain `RefreshCcw` semantics.
- Reuse one nav-item rendering/state contract and the same item classes for all five destinations; bottom placement is the only intentional structural distinction. Preserve Logout as a separate muted utility action.
- Use `aria-current="page"` or an equivalent programmatic current-state carrier for the active destination. Title/accessible name must survive icon-only mode.
- Show admin/readonly capability as restrained metadata in expanded mode; hide or compact it in collapsed mode without losing the capability explanation from the accessible name.
- Preserve current route IDs, session/logout behavior, local collapsed preference, and readonly access to inspection.

### 3.3 Review trade-panel contract

- Keep `TraderFilters`, `TradeExportControls`, and `TraderTradeList` shared; do not fork business logic into a Review-only component family.
- Replace the light-default-plus-`.dr-sidebar` patch model with shared product tokens and an optional density/layout class only. Density may change spacing, not the brand palette or data behavior.
- Match ticker/date/strategy controls for surface, border, type scale, focus, and selected states. Native select/options must opt into the dark color scheme and cannot fall back to a white paper surface.
- Preserve availability-driven visibility, intentional empty selection, focused-trader reconciliation, export selection, group activation, drilldown, labels, and non-color direction/trader cues.
- Interactive and Static Review must resolve the same visible skin. Static remains read-only and retains existing hash behavior.

### 3.4 Create-trader contract

- Add one explicit `新增交易者` action inside the admin registry section. It reveals an inline create row/card; no modal library or new route is required.
- A new row begins as an unsaved draft. `trader_id` is user-entered, must match exact regex `^[a-z][a-z0-9_]{1,63}$` (2–64 total characters), and is editable until first successful persistence, then rendered readonly like every existing ID. `color` must match exact regex `^#[0-9A-Fa-f]{6}$`; the leading `#` is mandatory.
- The draft uses the backend's exact field vocabulary. `active` may default to true; sort order may prefill the next unused multiple of ten but remains editable; color and identity are never guessed from a display name.
- A pure frontend helper owns draft creation, normalization limited to trimming surrounding whitespace, exact slug/color regex checks, duplicate checks, field-error mapping, and append-to-full-registry behavior. It must not silently lowercase, rewrite, auto-prefix a color, or auto-deduplicate identity.
- `添加到草稿` appends only a valid new entry to the full registry draft and visibly marks it unsaved. `保存注册表` remains the one persistence action for the complete document. Unsaved new rows may be removed; persisted rows gain no delete action.
- Save uses the existing `onSaveRegistry`/`Api.saveTraders` PUT, then reloads `Api.adminTraders`. A failure retains all draft inputs and exposes `role="alert"`; success exposes `role="status"` and clears create state only after canonical reload.
- Server errors remain authoritative. The current API client exposes `response.text()` as `Error.message`; field association first attempts to parse that body as JSON and use a string FastAPI `detail`, otherwise searches the raw text. Only a recognized `registry.traders[<index>].<field>` path whose index maps to a rendered registry row and whose field maps to a real control is associated/focused. Invalid JSON, root-level paths, unknown indices/fields, or messages without a path render a form-level `role="alert"` without inventing success; this plan does not require a shared API-client or backend change.

### 3.5 Compatibility and protected boundaries

- No backend source change is planned. A need to change `backend/app/main.py`, `backend/app/services/trade_records.py`, schema files, DB projection, or auth semantics stops implementation for plan revision.
- All save-path browser tests use temporary copies of `content/` and the tracked SQLite DB with an isolated backend. They must verify the tracked DB, registry, trade-day tree, publisher, and exporter remain byte-exact.
- The current 22 canonical trade-day documents and every existing trader/group/context must remain unchanged by proposal work and by isolated acceptance.
- No generated screenshots or build output are written under `docs/`; temporary evidence belongs under `output/` and durable summaries under the plan review/evidence directory.

## 4. Planned File Surface

Phase 0 must freeze an exact Add/Modify/Remove manifest. If implementation needs a backend, content, schema, DB, workflow, runbook, exporter, K-line engine, or unlisted cross-contract change, stop for plan revision.

### 4.1 Candidate additions

- `frontend/src/features/review/traderRegistry.js` — pure new-trader draft, exact slug/color validation, duplicate, API-error-body association, and full-registry append helpers.
- `frontend/src/features/review/traderRegistry.test.js` — exact valid/invalid/duplicate/default/no-rewrite fixtures, slug 2/64-character boundaries, required color `#`, and JSON-`detail`/raw-text/fallback error carriers.

### 4.2 Candidate modifications

- `frontend/src/components/Layout.jsx`
- `frontend/src/pages/AdminTradersPage.jsx`
- `frontend/src/pages/DashboardPage.jsx` only if a semantic class is required by the shared theme
- `frontend/src/pages/ReviewPage.jsx` only if a density/theme wrapper must be simplified
- `frontend/src/pages/StaticReviewsApp.jsx` only if the same wrapper simplification is required
- `frontend/src/pages/BacktestPage.jsx` only if a semantic class is required by the shared theme
- `frontend/src/pages/TeachingPage.jsx` only if a semantic class is required by the shared theme
- `frontend/src/pages/LoginPage.jsx` only if a semantic class is required by the shared theme
- `frontend/src/features/review/TraderFilters.jsx`
- `frontend/src/features/review/TradeExportControls.jsx` only if a semantic label/class is required
- `frontend/src/features/review/TraderTradeList.jsx` only if a semantic label/class is required
- `frontend/src/features/review/tradeRecords.test.js`
- `frontend/src/features/review/reviewWorkspace.test.js`
- `frontend/src/styles.css`
- `frontend/package.json` — keep the `test:trade-records` script name stable and append `src/features/review/traderRegistry.test.js` to its existing `node --test` file list; add no new script or command name.
- `docs/architecture.md`
- lifecycle/state/evidence artifacts required by `docs/operating-modes.md`

### 4.3 Candidate removals

- No source, content, data, screenshot, or route removal is planned. Obsolete CSS declarations may be removed only after a consumer scan and browser proof show they are no longer required.

## 5. Phased Execution Plan

### Phase 0 — Baseline, Token Table, And Exact Scope Freeze

- Entry gate: matching-revision `review-002: approve/high` and activation evidence `user-instruction:2026-07-20-activate-terminal-ui-trader-registry` are satisfied; the plan is Active at `phase-0:not-started`. Phase 0 remains closed until a later explicit implementation-start instruction opens `phase-0-start`.
- Work:
  - rerun the startup contract and inventory every pre-existing dirty path;
  - capture current HEAD/status, exact Add/Modify/Remove manifest, CSS token/color consumer map, page/root classes, nav semantics, frontend test carriers, and registry create/write boundaries;
  - capture fresh before screenshots at `1672x941` and `820x1180` for expanded/collapsed shell, Data, Review, Backtest, Teaching, Admin, Login, and Static Review as applicable;
  - freeze the section 3.1 token table, allowed brand-warm use, legacy-paper stale scan, and exact computed-style/contrast acceptance pairs;
  - freeze create-trader fixtures for exact slug regex `^[a-z][a-z0-9_]{1,63}$` (`ab` and length 64 accepted; one character, length 65, uppercase, leading digit, and hyphen rejected), exact color regex `^#[0-9A-Fa-f]{6}$` (leading `#` required), blank name, duplicate ID/color/order, negative order, unsaved removal, JSON-`detail`/raw-text/unmapped server rejection, success/reload, and registry-only no-availability behavior;
  - capture hashes/counts for the tracked DB, registry, 22 trade-day documents, backend registry handlers/routes, schema, publisher, exporter, and daily runbook.
- Verification: governed/auto harness, direct operating-modes checker, lifecycle fixtures, startup budget, current frontend test/build commands, focused backend registry tests, read-only SQLite integrity/FK, link scan, and `git diff --check`.
- Exit gate: the exact frontend/docs surface is frozen; no backend/new-route/schema/data/publisher change is required; all baseline checks are classified as pass/fail/not-run; and unrelated paths are explicitly excluded.

### Phase 1 — Shared Terminal Tokens And Peer Navigation

- Entry gate: `phase-0:complete` with the exact manifest and token contract frozen.
- Work:
  - install the shared terminal-first variables at the application root and migrate generic body, panel, metric, table, form, feedback, Login, and shell chrome away from paper defaults;
  - keep chart/signal/trader colors domain-owned while mapping shared chrome to the new tokens;
  - keep the trader workspace bottom-pinned after the flexible sidebar spacer while converting it to the shared primary nav item renderer/classes, replace refresh semantics, add programmatic active state, and make capability labeling stable in expanded/collapsed modes;
  - remove the orange destination CTA and limit `--brand-warm` to the frozen allowed consumer set;
  - add/replace source-contract tests for exact tokens, allowed warm use, peer nav structure, active/accessibility state, and forbidden legacy paper chrome.
- Verification: frontend contract tests, normal/static builds, computed-style probes, keyboard nav, and fresh expanded/collapsed Data/Admin screenshots at both viewport sizes.
- Exit gate: all shell and generic page chrome uses one token family; the five destinations are peer controls; no collapsed overflow or inaccessible active/capability state remains; and existing routing/session behavior is unchanged.

### Phase 2 — Data, Backtest, Teaching, Admin, And Login Chrome Migration

- Entry gate: `phase-1:complete` with a stable shell and shared variables.
- Work:
  - migrate remaining page-level panels, metrics, rows, toolbars, forms, empty/error/success states, and responsive surfaces to the shared token contract;
  - preserve page layout, typography, business controls, chart engine ownership, and behavior while eliminating cream default chrome;
  - update Admin point-editor and registry controls so fields, group pickers, preview surround, save states, and validation surfaces remain legible in the terminal palette;
  - retain the chart well as a high-density dark region without introducing a second page theme.
- Verification: frontend tests/builds, page-by-page computed-style and contrast probes, real-browser Data/Backtest/Teaching/Admin/Login behavior smoke, narrow overflow scan, and stale paper-color consumer scan.
- Exit gate: every non-Review authenticated page and Login belongs to the same terminal family; no behavior regression or unreviewed light-paper chrome remains.

### Phase 3 — Review Trade-Panel Fusion And Static Parity

- Entry gate: `phase-2:complete` with shared chrome stable.
- Work:
  - rebase ticker/date/strategy, Eligibility, trader options/Focus, export, group cards, drilldown, empty state, and status copy on the shared tokens and one compact Review density;
  - remove obsolete `.dr-sidebar` light-component patch duplication only after shared components render correctly in interactive and static Review;
  - ensure selects/options, hover, active, focus, trader color bars, direction shapes, and review badges remain legible and non-color-dependent;
  - preserve all availability, reconciliation, export, group selection, static hash, and mutation-free contracts.
- Verification: existing workspace/trade-record tests plus updated style contracts, normal/static builds, repeated SPY↔QQQ and date changes, filter/focus/export/group drilldown behavior, static legacy/current hash routes, desktop/narrow screenshots, keyboard/focus checks, and console scan.
- Exit gate: the full Review left column reads as one continuous surface in interactive and static modes, no light select or second brand remains, and behavior/output are unchanged.

### Phase 4 — Discoverable Create-Trader Flow

- Entry gate: `phase-3:complete` with the final shared Admin skin available.
- Work:
  - implement and test the pure registry-draft helpers against the exact slug/color regex boundaries and both current server error-body carriers;
  - add the admin-only inline create row/card, explicit unsaved state, field errors, add-to-draft/removal behavior, and save/reload announcements;
  - keep existing IDs immutable and reuse the current complete-document PUT without adding a route, backend branch, raw JSON path, auto-save, or blind retry;
  - reconcile server field paths where possible while retaining a form-level fail-closed fallback;
  - prove a newly registered trader with no groups does not appear in Review/Static availability controls and does not fabricate any canonical trade content.
- Verification: the name-stable `npm run test:trade-records` carrier including pure exact-regex/error-body fixtures; current backend registry/atomic/projection tests; normal/static builds; isolated temporary-content/DB browser matrix for admin valid create, invalid/duplicate fields, JSON-`detail` and raw/unmapped server rejection, successful reload, existing-row preservation, readonly denial, and no-group visibility; tracked protected-hash comparison before/after.
- Exit gate: an admin can discover and safely persist one valid new trader through the existing boundary; all failure paths retain coherent unsaved state; readonly/static remain mutation-free; and canonical tracked files are byte-exact.

### Phase 5 — Integrated Visual, Accessibility, And Regression Acceptance

- Entry gate: `phase-4:complete` with all functional and isolated-write checks green.
- Work:
  - run the full desktop/narrow page matrix for expanded/collapsed admin and readonly shells, all application pages, interactive/static Review, and Login where session setup permits;
  - compare against the six optimization screenshots and record how each OPT-001 through OPT-004 is resolved;
  - verify computed colors, WCAG text/control/focus contrast, focus order/rings, active/current state, field labels/errors, live announcements, no color-only meaning, and zero horizontal overflow;
  - exercise representative Data→Review, SPY↔QQQ, Review filter/export/drilldown, Backtest, Teaching, Admin inspect/edit, registry create failure/success/reload, and Static Review flows;
  - run full backend/frontend/governance checks and protected-boundary hash/count comparisons.
- Verification: section 7 complete matrix with fresh screenshots/behavior receipts and truthful pass/fail/not-run classification.
- Exit gate: all four optimization outcomes have fresh visual and behavioral evidence; full checks are green; no protected boundary drift or unauthorized artifact remains; and implementation is ready to freeze for independent review.

### Phase 6 — Documentation, Independent Implementation Review, And Closeout

- Entry gate: `phase-5:complete` with an exact review-ready implementation/evidence manifest.
- Work:
  - update `docs/architecture.md`, plan evidence, `PROGRESS.md`, and `HANDOFF.md` to the verified implementation truth;
  - freeze exact implementation paths, patch/addition digests, accepted evidence set, protected hashes, and authority boundary;
  - obtain an independent implementation review of the exact frozen revision; remediate `revise` findings through a new frozen revision and re-review;
  - only after `accept`, reconcile plan/index/roadmap/state surfaces and move the plan to `completed/` with a truthful final disposition;
  - record commit values only if separately authorized commits actually exist.
- Verification: frozen digest recomputation, implementation review metadata/verdict, governed/auto/operating checks, lifecycle fixtures, startup budget, link/stale-state scan, `git diff --check`, and intended-scope inspection.
- Exit gate: independent `accept`, all lifecycle surfaces reconciled, no unresolved finding, no false Git/data/publication claim, and final handoff names the next real gate.

## 6. Safety, Compatibility, And Rollback Matrix

| Risk or contract | Required prevention/evidence | Rollback boundary |
| --- | --- | --- |
| Theme migration creates a fourth skin | Exact token/consumer table; stale legacy-paper and hard-coded chrome scan | Revert only planned frontend theme paths to the last phase receipt |
| Chart/signal/trader semantics are recolored | Domain-color allowlist and before/after chart marker comparison | Restore chart-owned declarations without reverting shared chrome |
| Trader nav loses readonly/admin meaning | Accessible name, visible expanded metadata, `aria-current`, collapsed keyboard test | Restore peer item rendering while retaining old route/session contract |
| Review business behavior changes during restyle | Existing workspace/trade/export fixtures plus repeated browser transitions | Revert density/style changes; no data rollback is needed |
| Static gains authenticated mutation | Source assertion, API/network inspection, browser route scan | Revert Static wrapper/component changes immediately |
| Duplicate/invalid trader reaches server | Pure client validation plus authoritative server validation and error retention | Keep draft unsaved; no canonical replacement occurs |
| Full registry save drops or rewrites existing entries | ID/value/count diff against canonical base before PUT and after reload | Server atomic rollback; restore temporary acceptance copy only |
| Registry save fabricates points/days | Before/after group/context/day counts and availability fixture | Reject candidate; no tracked content is touched |
| Content and DB projection diverge | Existing rollback-coherent PUT plus isolated projection-failure test | Existing service rollback; stop rather than retry blindly |
| User worktree changes are swept into scope | Phase 0 dirty-path inventory and intended-path diff/staging inspection | Do not reset/stash/restore unrelated paths |
| Local acceptance mutates tracked data | Temporary content + SQLite copy and exact tracked hashes | Destroy only the verified temporary root after evidence capture |
| Green checks are mistaken for remote authority | Explicit authority ledger in plan/evidence/handoff | Stop before stage/commit/push/PR/Pages/remote action |

## 7. Verification And Evidence Plan

### 7.1 Recurring repository checks

```bash
python3 scripts/check-project-harness.py --root . --profile governed
python3 scripts/check-project-harness.py --root . --profile auto
python3 scripts/check-operating-modes.py --root .
python3 -m unittest scripts.tests.test_operating_modes
python3 scripts/check-startup-doc-budget.py
cd backend && PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'
cd backend && PYTHONPATH=. python3 -m compileall -q app scripts tests
cd frontend && npm run test:trade-records
cd frontend && npm run build
cd frontend && VITE_STATIC_REVIEWS=true npm run build:static-reviews
git diff --check
```

Use the repository's pinned backend environment when the default interpreter lacks dependencies. Do not relabel a prerequisite failure or not-run browser check as pass.

### 7.2 Plan-specific acceptance matrix

| Surface | Required cases |
| --- | --- |
| Token contract | Exact variables/values; allowed warm consumer; no unreviewed paper chrome; computed contrast/focus pairs |
| Shell/nav | Five peer destinations; active/current state; admin/readonly copy; expanded/collapsed; keyboard; no overflow |
| Data | Terminal panels/metrics/rows; ticker/date navigation to Review unchanged |
| Review | Context controls through trade cards; Eligibility dark control; trader Focus/export/drilldown; SPY/QQQ/date changes |
| Static Review | Current + legacy hash; same fused panel; no admin/API/mutation entry |
| Backtest | Existing one-day/ten-day action and K-line result behavior unchanged under new chrome |
| Teaching | Existing reveal/step behavior and K-line embedding unchanged under new chrome |
| Admin | Terminal point editor/registry; create invalid/duplicate/success/reload; existing values preserved |
| Readonly | Inspect/export available; registry GET/write/create controls absent/denied |
| Login | Shared terminal brand; labeled/error/focus states; no auth behavior change |
| Protected state | DB/content/schema/backend/publisher/exporter/runbook hashes and counts unchanged |

### 7.3 Evidence locations

- Design reviews: `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/review-NNN.md`
- Phase evidence and final review packet: the same review directory under `evidence/`
- Temporary screenshots/behavior receipts: `output/playwright/terminal-ui-registry-<phase>-<timestamp>/`
- Durable visual source: `docs/optimization/2026-07-20-trader-workspace-nav-and-registry/screenshots/`

## 8. Commit, Remote, Data, And Publication Boundaries

- Activation and implementation authorities are consumed; the accepted implementation and lifecycle closeout are complete.
- `user-instruction:2026-07-20-commit-and-push-terminal-ui-registry` is consumed by exact-path implementation/lifecycle commit `43b96ab9c8ffffad2e76191b0d31d45e277afddc`, the immediate boundary-metadata commit, and their final `codex/project-harness` push. Unrelated worktree paths remain excluded.
- This Git authority does not authorize amend/reset/stash, PR, merge, Pages publication, hosted verification, provider/broker access, or remote administration.
- Registry-create acceptance must use isolated temporary content/DB copies. It does not authorize a new canonical trader in the tracked repository.
- Provider/broker access, market-data fetch, tracked DB/content writes, daily publication, PR, merge, Pages, hosted verification, branch protection, environments, and remote administration remain separately unauthorized.

## 9. Design Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/`
- Current review target revision: `v2-review-foldback-2026-07-20`; `review-001: revise/high` is retained as append-only v1 evidence, and `review-002: approve/high` qualifies exact v2 with no findings.
- Required design verdict: satisfied by qualifying independent `review-002` for exact v2 after checking the token/accessibility contract, single-plan bundling, no-backend boundary, create-trader draft/save semantics, isolated data acceptance, and phase exit gates.
- Any future design-contract change requires a new stable revision and matching-revision review; approval of an older revision never qualifies a changed contract.
- Activation is satisfied by `user-instruction:2026-07-20-activate-terminal-ui-trader-registry`; exactly this plan has moved to `active/` and stopped at `phase-0:not-started`.
- Implementation start requires a later explicit start/execute instruction. Review, activation, and implementation authority do not grant Git, data, provider/broker, publication, or remote authority.
