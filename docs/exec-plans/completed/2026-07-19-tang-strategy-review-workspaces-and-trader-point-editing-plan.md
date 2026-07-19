# Tang Strategy Review Workspaces And Trader Point Editing

- Lifecycle schema: `operating-modes-v1`
- Status: Completed
- Plan slug: `2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan`
- Revision: `v3-round-1-review-foldback-2026-07-19`
- Plan author ID: `codex-plan-author-2026-07-19-review-workspaces`
- Design reviews: ../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/review-001.md@revise@v2-review-loop-baseline-2026-07-19, ../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/review-002.md@revise@v2-review-loop-baseline-2026-07-19, ../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/review-003.md@approve@v3-round-1-review-foldback-2026-07-19, ../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/review-004.md@approve@v3-round-1-review-foldback-2026-07-19
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-19-dual-review-loop-through-active`
- Implementation start evidence: `user-instruction:2026-07-19-start-review-workspaces-implementation`
- Phase 0 evidence: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-0-baseline.md`, `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-0-contract-freeze.md`, `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-0-manifest.md`
- Phase 1 evidence: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-1-pure-contracts.md`
- Phase 2 evidence: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-2-engine-ownership-and-workspaces.md`
- Phase 3 evidence: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-3-trader-point-editing.md`
- Phase 4 evidence: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-4-static-parity.md`
- Phase 5 evidence: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-5-integrated-acceptance.md`
- Phase 6 review packet: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/implementation-review-packet-001.md`
- Review-ready implementation revision: `workspace-review-v1:3d24de3baf38cf6e13c8c7295528f22989cf67548d949e3cd98f0739d06717cd@d73502139e6d25d5e050c376e90289c70ef23ecc`
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: `../reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/implementation-review-001.md@accept`
- Implementation review session ID: `019f7bdd-3f80-7361-be62-f7be49f24147`
- Final disposition: Completed
- Verified implementation commit: `ab655568d50d20c2a97e970658ec9fa3b41719b7`
- Lifecycle reconciliation commit: `65fd15dd3a3b7030bc3d15fc0590ea26a048490c`
- Owner: Codex
- Created: 2026-07-19
- Source intake: [`docs/optimization/2026-07-19-review-ui-and-trader-editing.md`](../../optimization/2026-07-19-review-ui-and-trader-editing.md), OPT-001 through OPT-004
- Visual baseline: [`design/references/2026-07-19-review-ui-reference-v1.png`](../../../design/references/2026-07-19-review-ui-reference-v1.png), SHA-256 `57c34ea70bf7c6cab2c983b8feaedb6ad9be6f23fc02262ac7c97a48b156d3c5`
- Scope authority: lifecycle-only activation and Phases 0-6 are complete; `user-instruction:2026-07-19-start-review-workspaces-implementation`, `user-instruction:2026-07-20-kimi-limit-takeover`, the final Phase 6 closeout instruction, and `user-instruction:2026-07-20-commit-and-push` are fully consumed. External Grok Build accepted the exact review-ready revision above with high confidence and no findings. The plan-scoped commits and current `codex/project-harness` branch push completed without granting data writes, provider/broker access, PR, merge, Pages publication, hosted verification, or other remote changes
- Current request authority: consumed by the exact plan-scoped commit chain and current-branch push; any future source, data, Git, publication, provider/broker, PR, merge, or remote-setting action requires new authority

## 1. Context And Evidence

### 1.1 Current repository facts

The proposal was drafted from live repository evidence at `codex/project-harness@772b94595ccd15d41d06f966dd72e0bb7829c441`, with the optimization intake, its index/state routing, and the confirmed visual reference present as related uncommitted inputs. Unrelated `output/` artifacts were present and remain outside this plan and its proposal commit.

- The tracked SQLite database is SHA-256 `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` and currently exposes 49 logical market days: 46 SPY and 3 QQQ. It also contains 11 active strategies, 2 traders, and 33 trade groups.
- `frontend/src/main.jsx` stores a flat `marketDays` array plus `selectedDayId`, but has no explicit ticker-workspace state. `DashboardPage.jsx` renders the first 20 mixed market days, and `ReviewPage.jsx` renders every ticker/date in one `Market day` selector.
- `ReviewPage.jsx` renders Review-owned context/workflow controls together with page-level `1m`, `5m`, Back, Step, Play/Pause, and Overview buttons. `StaticReviewsApp.jsx` repeats the same generic chart controls. `BacktestPage.jsx` and `TeachingPage.jsx` also expose page-level replay controls already owned by the shared engine.
- `frontend/src/kline/kline-engine.js` already owns timeframe, replay navigation, playback speed, zoom, follow mode, indicator visibility, candle type/fill, and theme. `UnifiedKlineEngine.jsx` exposes the corresponding imperative API. The engine lacks a visible fit/overview action even though the wrapper implements `overview()`.
- `TraderFilters.jsx` renders every registry trader and initializes all active traders without first deriving which traders have displayable groups for the resolved ticker/date. Review payload changes reset the filter object, but there is no reusable stale-selection reconciliation contract.
- `Layout.jsx` exposes the trader workspace only to admins and collapses it to an icon. `AdminTradersPage.jsx` can inspect normalized groups, but mutation is driven by raw registry/day JSON textareas instead of a trader/day/group/event task flow.
- `GET /api/trade-records` is a readonly public projection, not a canonical write base: it is ticker-filtered, projects full `normalization` to `normalization_method`, and cannot represent every ticker/trader/context in a date-keyed canonical day file. The existing admin PUT routes already enforce schema validation, candidate projection, atomic canonical replacement, DB drift checks, and rollback coherence, but safe form editing additionally requires narrow admin-only canonical registry/day reads before using those unchanged PUT boundaries.
- `export_static_reviews.py` already includes ticker/date/session metadata in a flat manifest and preserves `#<ticker>-<date>-<session>` day slugs. Static parity can therefore be implemented by shared client-side workspace resolution without changing the export or Pages workflow.
- The confirmed visual reference fixes the preferred direction: compact dark trading-terminal layout, explicit SPY/QQQ tabs, ticker-scoped date rail, Review-owned business context in the left panel, one engine-owned generic toolbar, availability-driven trader controls, and a secondary but discoverable `编辑交易者点位` action.

### 1.2 Why Coding Mode Lane 3 is required

OPT-001 through OPT-004 form one cross-surface behavior contract spanning shared chart ownership, authenticated Data/Review state, admin-only mutation UX, static Review routing, responsive layout, and accessibility. The change is broader than bounded maintenance and difficult to verify safely as isolated page edits. It therefore requires a reviewed Lane 3 Exec Plan even though the intended implementation leaves the database, market-data, API, and publisher contracts unchanged.

### 1.3 Review-loop and activation instruction

The user's `user-instruction:2026-07-19-dual-review-loop-through-active` instruction requires Kimi and Grok to review each frozen revision independently. Both outputs for one revision must be captured before any finding is folded back. If either reviewer returns `revise` or `reject`, the plan author produces a new revision and both reviewers inspect that same new revision without sibling-review context. Lifecycle activation is allowed only after both reviewers return `approve` for the same revision. Activation stops at `phase-0:not-started`; it does not start Phase 0 or authorize source/runtime/data/publication work.

### 1.4 Round 1 review foldback

Kimi `review-001` and Grok `review-002` independently returned `revise/high` against frozen revision `v2-review-loop-baseline-2026-07-19` at SHA-256 `c90406702862991511c68fb10d33e94b9a20a8b5430399bcaddd9d77101acc17`. This revision folds every finding into the contract:

- the public projection is explicitly forbidden as an editor write base, and the candidate surface now includes admin-only canonical registry/day GET handlers that return write-valid documents without changing roles or PUT authority;
- every edit begins from the complete date document and preserves all untouched tickers, traders, groups, events, legs, outcomes, and note contexts; count/ID/diff receipts make silent group loss a hard failure;
- trader filter ticker/date inputs are removed as independent authorities and may only be readonly mirrors of the resolved workspace;
- Admin preview is frozen as one read-only `UnifiedKlineEngine` chart using the resolved market day plus the candidate's shared marker/list helpers; no second chart implementation or auto-save path is allowed;
- the existing `test:trade-records` carrier name remains stable and is broadened to include new review contract tests, so `.harness/config.json` and the CI workflow require no command rename;
- pure label/selected/disabled-state fixtures supplement, but do not replace, browser keyboard/focus/announcement acceptance.

## 2. Objective And Success Criteria

### 2.1 Objective

Create one coherent SPY/QQQ review workspace in which ticker/date is the authoritative parent context, chart-generic controls have exactly one engine owner, trader controls reflect only displayable records in that context, admins can edit trader points through a validated form-and-preview workflow, and interactive/static Review share the same selection rules without making Static Review a copy of the full authenticated application.

### 2.2 Success criteria

1. Data, interactive Review, and Static Review make SPY or QQQ visible as the selected parent workspace before presenting dates; their default lists never interleave tickers.
2. An explicit existing day selection or static hash wins. Without one, SPY is selected when present; otherwise the first available ticker is chosen deterministically. No missing ticker/date is fabricated or silently substituted across workspaces.
3. Switching ticker retains the same date only when that ticker has it; otherwise it selects that ticker's newest real date. It refreshes chart, signals, statistics, trade groups, export metadata, error/loading state, and trader controls as one context transition.
4. Data-page day selection opens or reconciles Review to the same ticker/day. Strategy remains selected when valid; session-window and engine preferences follow their declared persistence rules rather than being reset accidentally.
5. Timeframe, replay Back/Step/Play/Pause, speed, zoom, follow/fit/overview, indicators, candle rendering, and theme appear only in the K-line engine toolbar. Review owns ticker/date, strategy, Ext K/RTH, traders, eligibility/focus, Backtest, Rescan, export, edit entry, and assembly status.
6. Review's `Rescan` recomputes the current resolved review. `Backtest` has a distinct business action and may navigate with the current strategy/ticker context; it must not remain a second label bound to the Rescan handler.
7. For a resolved ticker/date, only traders with at least one currently displayable group appear by name, checkbox, or Focus action. No matching groups produces a neutral empty state. Stale selected/focused traders cannot affect markers, statistics, lists, or exports after a context switch.
8. Every authenticated user can discover `交易记录 / 点位管理` in one navigation action and understand the readonly/admin capability difference. Static Review never exposes this authenticated editing entry.
9. An admin can load the write-valid canonical registry and complete multi-ticker day through admin-only reads, choose ticker/date/trader, inspect groups and events against one reused `UnifiedKlineEngine` preview, add or edit a point through labeled fields, preview the merged canonical candidate and marker/list effect, and explicitly save the complete day through the existing atomic admin PUT without editing raw JSON as the primary path.
10. Readonly users can inspect the public workspace without mutation controls. A successful save preserves every untouched group/context/ID from the complete day base; failed client/server validation focuses or identifies the responsible field when possible, never writes partial canonical content, and never leaves content and DB projection on different boundaries.
11. Existing static `#<ticker>-<date>-<session>` links still resolve. Static mode remains Review-only, verified-record-only, and mutation-free while using the same ticker/date/trader/control-ownership rules as interactive Review.
12. Interactive and static fixtures prove asymmetric SPY/QQQ history, pending/verified differences, available/unavailable traders, empty-trader dates, stale-selection reset, legacy hash resolution, and chart/signal/trade/export reconciliation.
13. The confirmed `1672 x 941` reference is the desktop fidelity baseline. Narrow/collapsed layouts preserve ownership, reading order, labels, keyboard reachability, and visible selected state without recreating a duplicate control bar.

### 2.3 Non-goals

- No SQLite schema/data migration, market-data fetch, seed change, historical backfill, SPY/QQQ pair-policy change, provider or broker access.
- No authentication/login redesign, role expansion, credentials UI, secret handling change, or readonly mutation capability.
- No database/schema/auth-role change or new write route. The only planned API additions are admin-only canonical GET handlers for the full trader registry and one complete date document; public `GET /api/trade-records` remains a lossy readonly projection, and the existing authoritative PUT paths remain the only mutation boundaries.
- No static Data, Backtest, Teaching, login, or Admin application. Static remains a standalone read-only Review surface.
- No Pages workflow, export-manifest schema, daily runbook, `gh-pages`, or hosted-site mutation. Local static build/browser acceptance is evidence only.
- No physical SPY/QQQ database separation, comparison mode, synthetic dates, or automatic cross-ticker fallback.
- No redesign of Backtest or Teaching business workflows beyond removing page-level duplicates of engine-generic controls and preserving their page-specific actions.
- No raw evidence, screenshot, chat transcript, option-bar history, or private field in canonical content or exports.
- No implementation, implementation commit, push, PR, merge, publication, or remote action under proposal/design-review authority.

## 3. Target Product And State Contracts

### 3.1 Shared ticker/date workspace contract

Add one pure workspace model consumed by Data, Review, Admin inspection/editing, and Static Review. The exact module/component manifest is frozen in Phase 0, but the contract must expose and test:

- available tickers derived only from real market days or static manifest entries;
- ordered dates grouped by selected ticker and month for the preferred tabs + date-rail presentation;
- deterministic initial selection from explicit interactive state or legacy static hash, then SPY if available, then the first available ticker/date;
- same-date preservation on ticker switch only when the target ticker owns that date, otherwise the newest real target date;
- an atomic transition result containing selected ticker, selected day ID/slug, and the dependent-state reset token;
- canonical static hash formatting/parsing compatible with `#spy-2026-07-17-extended` and `#qqq-2026-07-17-extended`;
- explicit invalid/missing-route behavior that selects a deterministic valid local item and reports the resolution without pretending the missing day exists.

Interactive state gains an explicit selected-ticker context rather than inferring independent ticker values in Review and trader filters. The selected market day remains the assembled review identity; any child ticker/date fields derive from it and cannot disagree. `TraderFilters` no longer owns editable ticker/date selectors: those controls are removed or rendered only as readonly mirrors derived from the workspace, and pure fixtures reject any child-filter attempt to diverge from the resolved market day.

### 3.2 Control ownership contract

| Control family | Owner | Page behavior |
| --- | --- | --- |
| Timeframe, replay, speed, zoom, follow, fit/overview, MA/VWAP, candles, theme | K-line engine | Render once inside the engine; pages may invoke methods programmatically for context/list navigation but do not duplicate visible buttons |
| Ticker/date, strategy, Ext K/RTH, trader/eligibility/focus, exports, edit entry, assembly/error state | Review workspace | Render in the Review context panel and drive one resolved payload |
| Rescan | Interactive Review | Recompute the current resolved day/strategy without changing ticker/date |
| Backtest | Interactive Review/Backtest workflow | Distinct navigation/action preserving applicable context; never alias Rescan |
| Run-backtest/result selection | Backtest | Page-specific and retained |
| Training cutoff/reveal/prompt selection | Teaching | Page-specific and retained; generic replay buttons come from the engine |
| Admin candidate edit/preview/save | Authenticated trader workspace | Readonly inspection for readonly roles; mutation and save only for admin |

The engine receives a visible fit/overview action with keyboard-accessible labeling and state behavior. Existing imperative methods remain available for signal/trade-list navigation, but visible generic duplicates are removed from Review, Static, Backtest, and Teaching.

### 3.3 Availability-driven trader contract

Trader availability is computed from the resolved payload before applying trader selection:

1. Match the resolved ticker/date.
2. Keep groups allowed by the current record status, review-status, and display-eligibility contract. Static continues to receive verified active records only.
3. Derive the ordered available trader IDs from those groups and the registry order.
4. Render only those traders. A global registry entry without a matching displayable group is not a visible option.
5. On initial load or context change, intersect the previous multi-selection with available IDs. If the intersection is empty after a real context change, select all available traders; an unavailable focused trader is always cleared.
6. Within the same context, an intentional empty selection remains empty until the user changes it or changes context.
7. Build markers, lists, statistics, note contexts, and downloads only after reconciliation, using the same resolved filter object.

An empty available set hides names, checkboxes, and Focus actions and renders one neutral message. It must not render the global registry as a misleading empty trader list.

### 3.4 Trader point editor contract

The primary editor is form-driven and preserves the existing canonical hierarchy and backend authority:

- context selection: ticker, date, trader;
- canonical load base: an admin-only full registry read plus an admin-only date-keyed trade-day read returning the write-valid canonical document, including full `normalization`, all underlyings, all traders, all trade groups, and all note contexts; public `GET /api/trade-records` is inspection-only and must never seed a write;
- record selection: existing trade group or explicit new group;
- group fields: immutable resolved trade date, underlying, trader, stable ID rules, direction, status, review status, three eligibility flags, outcomes, and notes/provenance where the schema permits;
- leg fields: instrument/side/type, expiry, strike, contract multiplier, and their provenance;
- event fields: action, sequence, occurred-at/New York offset, time precision/incomplete flag, premium, quantity, fees, note, and fact provenance;
- registry metadata: display name, color, active state, and sort order, while `trader_id` remains immutable once referenced;
- full-day merge: clone the complete loaded day, apply only the scoped form edit, and carry every untouched ticker/trader group, leg, event, outcome, and note context byte-equivalently at the semantic document boundary; never construct a PUT payload from a ticker/trader-filtered projection;
- candidate preview: canonical structured summary plus the same list/marker rendering helpers used by Review, rendered against one read-only `UnifiedKlineEngine` chart for the resolved market day; no second chart implementation and no save occurs during preview;
- explicit save: one existing admin PUT call containing the complete merged date document after client-required/format checks, preservation-diff checks, and user confirmation; the server remains authoritative for schema, repository-wide IDs, timezone, candidate projection, drift, and rollback;
- error handling: retain unsaved form state, surface a general server message and field association when safely derivable, and never retry or partially write automatically;
- readonly behavior: inspection/export remains available, while add/edit/save controls and mutable fields are absent or disabled with a clear role explanation.

Raw JSON textareas are not the primary workflow. Retaining an advanced raw view is optional only if design review accepts it, it is clearly secondary/admin-only, and it uses the same preview/save gate without creating a bypass.

The admin canonical reads do not widen inspection or mutation authority: readonly users continue to inspect the existing public projection, admin authentication is required for full canonical reads and every PUT, and no secret/private evidence field is added to public or static payloads.

### 3.5 Interactive/static parity contract

Interactive and static Review should share pure workspace selection, date grouping, trader availability/reconciliation, and presentational context components where capability differences allow. Static-specific boundaries remain explicit:

- consume the existing flat manifest and group it client-side; do not change export schema for UI convenience;
- use the legacy day slug as the canonical hash and derive ticker/date from the selected manifest item;
- never render login, admin editing, import, Backtest, Teaching, or authenticated-only actions;
- show that trade records are verified-only when the selected day has none because canonical records are pending;
- use identical engine ownership and remove the duplicate static footer controls;
- preserve local build output boundaries under temporary/generated directories and never treat build success as publish authority.

## 4. Planned File Surface

Phase 0 must compare this candidate surface to the live tree, freeze an exact Add/Modify/Remove manifest, and stop for plan revision if implementation requires a backend, DB, content, workflow, runbook, or unlisted cross-contract change.

### 4.1 Candidate additions

- `frontend/src/features/review/reviewWorkspace.js` — pure ticker/date/hash/availability transition contract.
- `frontend/src/features/review/reviewWorkspace.test.js` — asymmetric-history, route, stale-state, and parity fixtures.
- `frontend/src/features/review/ReviewContextPanel.jsx` — shared ticker tabs, date rail, business context, and capability-aware actions.
- `frontend/src/features/review/TraderPointEditor.jsx` — form, preview, validation presentation, and explicit save UI.

Phase 0 may split these into smaller same-boundary frontend modules, but must record the exact names before implementation.

### 4.2 Candidate modifications

- `backend/app/main.py`
- `backend/app/services/trade_records.py`
- `backend/tests/test_trade_records.py`
- `frontend/src/main.jsx`
- `frontend/src/api/client.js`
- `frontend/src/components/Layout.jsx`
- `frontend/src/pages/DashboardPage.jsx`
- `frontend/src/pages/ReviewPage.jsx`
- `frontend/src/pages/StaticReviewsApp.jsx`
- `frontend/src/pages/AdminTradersPage.jsx`
- `frontend/src/pages/BacktestPage.jsx`
- `frontend/src/pages/TeachingPage.jsx`
- `frontend/src/features/review/TraderFilters.jsx`
- `frontend/src/features/review/tradeRecords.js`
- `frontend/src/features/review/tradeRecords.test.js`
- `frontend/src/kline/UnifiedKlineEngine.jsx`
- `frontend/src/kline/kline-engine.js`
- `frontend/src/styles.css`
- `frontend/package.json`
- `docs/architecture.md`
- `docs/kline-engine.md`
- lifecycle/state/evidence documents required by `docs/operating-modes.md`

### 4.3 Candidate removals

- No source or data file removal is planned. Removing obsolete JSX/CSS blocks inside modified files is allowed only after source and browser evidence prove no remaining consumer.

## 5. Phased Execution Plan

### Phase 0 — Baseline, Exact Manifest, And Contract Freeze

- Entry gate: the plan has a qualifying independent design review with `approve`, the user has separately instructed activation, activation is recorded at `phase-0:not-started`, and a later explicit implementation-start instruction opens `phase-0-start`.
- Work:
  - rerun the startup contract and preserve unrelated worktree paths;
  - capture HEAD/upstream/status, tracked DB hash/integrity/FK/counts, Pages workflow/export hashes, existing static hash behavior, source control inventory, and current interactive/static screenshots;
  - freeze the exact contracts for `GET /api/admin/traders` and `GET /api/admin/trade-records?trade_date=<YYYY-MM-DD>`: admin-only, canonical/write-valid, no default fabricated day, no public/static exposure, and no change to the existing PUT handlers;
  - prove the public projection is not write-valid and record the current multi-ticker full-day shape that the editor must preserve;
  - freeze exact Add/Modify/Remove paths and a component/state/control ownership table;
  - create fixtures covering 46 SPY + 3 QQQ asymmetry, verified/pending records, two traders, a date with no visible trader, a multi-ticker day preservation case, invalid hash, and narrow/collapsed layout.
- Verification: governed/auto harness, operating-mode checks/tests, startup budget, current frontend tests/builds, backend trade-record tests, admin role/read-shape tests, SQLite read-only checks, workflow/export exact hashes, and `git diff --check`.
- Exit gate: exact scope/evidence manifest is durable, the two reviewed canonical read routes are sufficient without a DB/auth-role/write-route/publisher change, and all baseline checks are truthfully classified as pass/fail/not-run.

### Phase 1 — Pure Workspace And Trader-Availability Contracts

- Entry gate: `phase-0:complete` with the frozen frontend-only manifest.
- Work:
  - implement pure ticker/date grouping, deterministic default, same-date fallback, interactive ID/static slug resolution, and legacy hash parsing/formatting;
  - implement context-transition and stale trader-selection reconciliation rules;
  - separate trader availability from selected-trader filtering so unavailable names cannot enter controls or output;
  - remove independent ticker/date authority from `TraderFilters` and pin readonly mirror behavior plus accessible labels/selected/disabled states;
  - extend the frontend test command to run all review contract tests deterministically.
- Verification: pure Node fixtures for asymmetric histories, SPY default, missing target date, invalid hash, pending-only/static behavior, no-trader state, intentional empty selection, context-change fallback, focused-trader clearing, and export selection reconciliation.
- Exit gate: the state contract has no DOM/API side effects, every transition produces one internally consistent context/filter result, and current trade-record tests remain green.

### Phase 2 — Engine Ownership And Interactive Data/Review Workspaces

- Entry gate: `phase-1:complete` with passing pure contracts.
- Work:
  - add engine-owned fit/overview behavior and accessible toolbar labeling/state;
  - remove visible page duplicates of engine-generic controls from Review, Backtest, and Teaching while retaining page-specific business actions;
  - add the shared ticker tabs + ticker-scoped date rail to Data and Review;
  - make Data day selection open/reconcile Review to the same ticker/day;
  - move Review-owned context/actions into the context panel, remove the duplicate bottom control bar, and give Rescan and Backtest distinct behavior;
  - preserve engine preferences across business-context changes while clearing context-bound signal/trade selection and loading/error state.
- Verification: pure transition tests, normal Vite build, source-level single-owner assertion, real-browser SPY/QQQ Data→Review navigation, Review context switching, strategy/session behavior, Backtest/Rescan distinction, and Backtest/Teaching engine regression.
- Exit gate: each visible control has one owner and one rendering location, no interactive list interleaves tickers, and chart/signals/trades/exports reconcile after repeated SPY↔QQQ switching.

### Phase 3 — Availability-Driven Filters And Trader Point Editing

- Entry gate: `phase-2:complete` with stable interactive workspace state.
- Work:
  - render only displayable traders and add the neutral no-points state;
  - make the authenticated trader workspace visible and capability-labeled for readonly/admin roles;
  - implement admin-only full canonical registry/day reads while preserving public projection and existing PUT/auth boundaries;
  - replace the primary raw JSON mutation flow with ticker/date/trader/group/leg/event forms;
  - load the complete date document, merge the scoped edit while retaining every untouched ticker/trader/group/context, and fail closed if the preservation diff exceeds the intended edit;
  - validate required/format fields, preview canonical/list/marker effects against one reused read-only `UnifiedKlineEngine`, and save the complete merged day only after an explicit action through the existing PUT endpoints;
  - keep server validation authoritative and preserve unsaved state/error focus on failure;
  - retain immutable IDs, fact provenance, eligibility, pending/verified, unknown/null, and private/export boundaries.
- Verification: pure candidate construction/merge/diff tests; full admin-read shape and public-projection non-write-base tests; role/capability tests; existing 76+ backend trade-record/full-suite baseline or the then-current full count; compileall; readonly/admin browser flows; successful temp-copy save on a mixed SPY/QQQ date; injected validation failure; injected projection/cleanup failure; and before/after canonical + temporary DB coherence checks. The tracked DB and canonical repository remain unchanged during acceptance.
- Exit gate: an admin completes a point edit without raw JSON, the reused chart shows the candidate marker/list effect, readonly cannot access canonical reads or mutate, unavailable traders never render, untouched group/leg/event/outcome/context IDs and semantic values survive exactly, the full-day group-count delta equals only the intended edit, and every failure replay proves content/DB coherence.

### Phase 4 — Static Review Parity And Link Compatibility

- Entry gate: `phase-3:complete` with accepted interactive contracts.
- Work:
  - consume the existing flat static manifest through the shared workspace model and context components;
  - partition SPY/QQQ dates, preserve legacy day hashes, and make invalid-route resolution deterministic;
  - reuse availability reconciliation and single-owner engine controls;
  - represent verified-only/no-trader days honestly and keep all edit/authenticated actions absent;
  - add interactive/static fixture parity assertions without changing the export manifest or publisher workflow.
- Verification: temporary static export from a consistent DB copy, manifest/hash fixtures, static build, local static-browser SPY/QQQ/deep-link/no-trader checks, exact workflow/export source hashes, and generated-output cleanup.
- Exit gate: interactive and static pass the same workspace/trader/control tests, old hashes resolve, static exposes no mutation path, and no remote/publication action occurred.

### Phase 5 — Integrated UX, Accessibility, And Regression Acceptance

- Entry gate: `phase-4:complete` with both delivery modes locally green.
- Work:
  - run the complete repository verification set;
  - execute interactive and static browser matrices at the `1672 x 941` reference size plus representative narrow/collapsed layouts;
  - verify keyboard order/actions, visible/programmatic labels, selected ticker state, focus after context change/validation error, loading/error announcements, and non-color-only ticker identity;
  - compare the implemented desktop layout to the canonical visual reference while treating behavior and accessibility evidence separately from screenshot fidelity;
  - verify no runtime data, canonical content, workflows, generated tracked output, or secrets changed.
- Verification: full backend tests/compileall, all frontend Node tests, normal/static Vite builds, governed/auto/focused operating-mode checks, startup budget, SQLite integrity/FK/hash, real-browser Review/Data/Admin/Backtest/Teaching/static matrices, `git diff --check`, and exact scope scan.
- Exit gate: every success criterion has a named receipt; failures and unavailable checks are not relabeled; tracked DB/content/provider/publisher boundaries are unchanged.

### Phase 6 — Documentation, Independent Implementation Review, And Closeout

- Entry gate: `phase-5:complete` with stable implementation revision and complete evidence.
- Work:
  - update `docs/architecture.md`, `docs/kline-engine.md`, lifecycle indexes, `PROGRESS.md`, and `HANDOFF.md` to the implemented truth;
  - prepare a bounded implementation review packet containing exact diff, frozen manifest, visual/behavior/accessibility receipts, DB/content/workflow hashes, tests, and authority boundaries;
  - obtain an independent implementation review against the stable revision;
  - remediate through a new stable revision and re-review if verdict is not `accept`;
  - move to completed only after qualifying `accept` and reconcile every lifecycle route.
- Verification: qualifying implementation-review metadata/evidence, all Phase 5 checks on the accepted revision, lifecycle checker, link resolution, startup budget, exact state-block reconciliation, and `git diff --check`.
- Exit gate: `implementation-review: accept`, completed disposition is truthful, and commit/remote/publication fields reflect only separately authorized actions actually executed.

## 6. Safety, Compatibility, And Rollback Matrix

| Risk | Fail-closed behavior | Required evidence |
| --- | --- | --- |
| Ticker switch leaves prior-day payload or filters | Commit one resolved context transition before rendering; clear context-bound state and reconcile traders | Repeated asymmetric SPY↔QQQ fixture/browser loop |
| Unavailable trader remains selected/focused | Intersect against displayable IDs; clear focus; select all available only on a real context transition with empty intersection | Pure filters plus marker/stat/export equality |
| No trader points are present | Hide trader options and show neutral empty state; do not infer registry availability | Interactive/static empty-day fixture |
| Page and engine both expose a generic control | Treat source/DOM duplicate as failure; page may call engine only programmatically | Source assertion and browser control inventory |
| Admin form produces invalid canonical data | Block client save for known field errors; server PUT remains authoritative and atomic | Validation failures with unchanged content/temp DB |
| Public/ticker-filtered projection is used as a write base | Public payload is never accepted by candidate construction; admin editor must load the write-valid full registry/day documents | Shape/round-trip tests proving public payload fails canonical validation and admin payload passes |
| Scoped edit drops untouched same-day tickers, traders, groups, or contexts | Merge into the complete date document and fail closed when the semantic diff exceeds the intended edit | Mixed SPY/QQQ temp-copy save with exact untouched ID/count/value receipts |
| Projection fails after content replacement | Existing rollback restores canonical content and DB coherence; no UI success state | Injected projection/cleanup tests and hashes |
| Readonly or static gains mutation capability | No save handler/control for readonly/static; server admin dependency remains unchanged | Role/source/browser/API authorization checks |
| Static route breaks old links | Preserve exact day slug parser/formatter; invalid route resolves explicitly | Legacy SPY/QQQ hash fixtures and browser loads |
| UI work changes DB/data/provider/publisher | Stop and revise plan; do not absorb it as incidental implementation | Before/after hashes and exact diff scope |
| Local static acceptance is mistaken for publication | Record build/browser as local only; no push/workflow/hosted claim | Git/remote status and handoff boundary |
| Visual fidelity hides keyboard/responsive defects | Treat screenshot, keyboard, accessibility, and responsive receipts as separate gates | Reference-size plus narrow/collapsed matrix |

Rollback before publication is a scoped source revert to the last accepted implementation commit while preserving canonical content and tracked DB bytes. This plan contains no migration or cleanup requiring data rollback. Any later publication requires its own authorized workflow and must not use local acceptance as a substitute.

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

Keep the `test:trade-records` script name as the stable `.harness/config.json` and `.github/workflows/project-harness.yml` carrier; broaden its underlying command to include the review workspace tests. Any later carrier rename or configuration/workflow modification is outside this frozen surface and requires plan revision and independent re-review.

### 7.2 Plan-specific acceptance matrix

- Data: selected ticker is visible; only its actual dates render; selecting a day opens the matching Review context.
- Review: SPY 2026-07-17 and QQQ 2026-07-17 assemble non-empty 1m/5m bars with the known strategy and reconcile chart/signals/traders/exports.
- Asymmetry: QQQ 2026-07-10/14/17 and 46-day SPY history never interleave in the default date rail; a missing same-date fallback is deterministic.
- Trader visibility: verified groups render only their actual traders; QQQ 2026-07-14's pending record does not create a static trader option; an empty set has no name/checkbox/Focus remnants.
- Admin: readonly public inspection; admin-only canonical full-registry/full-day reads; public-payload write rejection; mixed-ticker full-day preservation; reused-engine candidate chart/list/marker preview; admin add/edit/save; invalid field; duplicate ID; timezone/offset error; and projection failure are exercised against temporary canonical/DB copies.
- Engine: Review, Static, Backtest, and Teaching expose one generic toolbar; page-specific actions remain functional.
- Static: both ticker hashes and at least one legacy hash open directly; static has no admin/mutation path and no mixed-symbol date list.
- Accessibility: pure/component fixtures pin tabs/date rail/form/overview accessible names plus selected/disabled state; browser evidence separately proves keyboard operation, predictable focus, announcements, and non-color-only identity.
- Fidelity: reference-size screenshot is compared with the confirmed layout direction; narrow/collapsed evidence proves the same ownership model.
- Protection: tracked DB SHA/integrity/FK, canonical content hashes, Pages workflow/export hashes, and remote state are unchanged unless a later separately reviewed and authorized scope says otherwise.

### 7.3 Evidence locations

Detailed phase receipts belong under `docs/exec-plans/reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/` or another Phase 0 frozen evidence path linked from the plan. Generated screenshots/builds remain under ignored/local output locations and are referenced by hash/path; they are not written under `docs/` as generated publication output.

## 8. Commit, Remote, And Publication Boundaries

- The current user instruction authorizes independent same-revision Kimi/Grok design reviews, append-only review artifacts, bounded foldback, lifecycle-only activation after matching-revision dual approval, and one final local commit containing the review/plan/lifecycle batch. It does not authorize implementation or future implementation commits.
- Each review round freezes one revision. Both outputs are captured before foldback, and neither reviewer receives the sibling output. An individual `approve` verdict does not activate the plan.
- Activation, implementation start, implementation commits, push, PR, merge, Pages publication, hosted verification, branch settings, provider access, and broker access remain separate gates.
- No plan phase may stage or commit unrelated `output/` artifacts or other user changes.
- Static export/build/browser acceptance must use temporary or generated paths and clean up only artifacts created by that acceptance run.
- A green check, screenshot, local DB copy, or independent review never grants remote or publication authority.

## 9. Design Review And Activation Gate

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md`
- Review target revision: `v3-round-1-review-foldback-2026-07-19`
- Review location: `docs/exec-plans/reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/`
- Required review method: an independent reviewer who did not draft this revision must inspect the live frontend/backend contracts, optimization intake, visual reference identity, exact planned surface, phase gates, testability, stale-state behavior, admin atomicity, static hash compatibility, accessibility, and authority boundaries.
- Required verdict before activation: satisfied by Kimi `review-003: approve/high` and Grok `review-004: approve/high`, both targeting frozen `v3-round-1-review-foldback-2026-07-19` with attested independence.
- Required user approval: satisfied and recorded as `user-instruction:2026-07-19-dual-review-loop-through-active`.
- Activation completed as lifecycle-only: the plan moved from `proposed/` to `active/`, indexes/roadmap/state blocks were reconciled, and state is `phase-0:not-started`. No source implementation was performed.
- Implementation requires another explicit start/execute instruction after activation recording and the Phase 0 entry gate.
- Any material revision after review invalidates matching-revision approval until the revised plan is independently reviewed.
