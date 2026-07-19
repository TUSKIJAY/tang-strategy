# Phase 0 — Exact File Manifest, Ownership Table, And Fixture Inventory

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Frozen at: `phase-0:in-progress`, 2026-07-19, `codex/project-harness@d73502139e6d25d5e050c376e90289c70ef23ecc`
- Revalidation rule: any required path outside this manifest, or any backend DB/content/workflow/runbook/cross-contract change beyond the two frozen admin GETs, stops implementation for plan revision and renewed design review (plan §4).

## 1. Evidence paths (frozen)

- Phase receipts: `docs/exec-plans/reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/`
- Generated artifacts (screenshots, static builds): `output/phase-0-baseline-20260719/` (untracked local output), referenced by SHA-256 from receipts; never written under `docs/`.

## 2. Add manifest (verified absent 2026-07-19)

| Path | Phase | Role |
| --- | --- | --- |
| `frontend/src/features/review/reviewWorkspace.js` | 1 | Pure ticker/date/hash/availability workspace transition contract |
| `frontend/src/features/review/reviewWorkspace.test.js` | 1 | Pure Node fixtures for asymmetric history, route, stale-state, parity |
| `frontend/src/features/review/reviewWorkspace.fixtures.js` | 0 | Shared fixture data (created in Phase 0 per plan §5 Phase 0) |
| `frontend/src/features/review/ReviewContextPanel.jsx` | 2 | Shared ticker tabs, date rail, business context, capability-aware actions |
| `frontend/src/features/review/TraderPointEditor.jsx` | 3 | Form/preview/validation/save UI for trader point editing |
| `frontend/src/features/review/tradeCandidate.js` | 3 | Pure candidate construction: new-group factory (all schema-required fields incl. `normalization`), full-day merge, preservation diff, form validation (same-boundary split recorded per plan §4.1) |

Phase 0 may split these into smaller same-boundary frontend modules only by amending this manifest with exact names before implementation. Phase 3 amendment: `tradeCandidate.js` added above (pure editor candidate logic so `node --test` can import it without JSX); `TraderPointEditor.jsx` keeps the rendering shell.

## 3. Modify manifest (verified present 2026-07-19)

| Path | Planned change |
| --- | --- |
| `backend/app/main.py` | Register the two frozen admin GET routes; nothing else |
| `backend/app/services/trade_records.py` | Admin canonical read handlers reusing existing load/validate; no PUT/public change |
| `backend/tests/test_trade_records.py` | Admin read shape/role tests, public-not-write-base round-trip tests, five-route registration pin |
| `frontend/src/main.jsx` | Explicit selected-ticker workspace state; admin payloads via admin canonical reads |
| `frontend/src/api/client.js` | Admin canonical read helpers |
| `frontend/src/components/Layout.jsx` | Discoverable trader workspace entry with readonly/admin capability label |
| `frontend/src/pages/DashboardPage.jsx` | Ticker tabs + ticker-scoped date rail; day selection opens Review context |
| `frontend/src/pages/ReviewPage.jsx` | Remove engine-generic duplicate controls; context panel; distinct Rescan/Backtest |
| `frontend/src/pages/StaticReviewsApp.jsx` | Shared workspace partition; remove duplicate footer controls; no mutation surface |
| `frontend/src/pages/AdminTradersPage.jsx` | Form-driven editor (`TraderPointEditor`) replacing primary raw JSON flow |
| `frontend/src/pages/BacktestPage.jsx` | Remove engine-generic duplicate buttons; keep page-specific actions |
| `frontend/src/pages/TeachingPage.jsx` | Remove engine-generic duplicate buttons; keep cutoff/reveal actions |
| `frontend/src/features/review/TraderFilters.jsx` | Ticker/date reduced to readonly workspace mirrors; availability-driven traders |
| `frontend/src/features/review/tradeRecords.js` | Availability derivation and stale-selection reconciliation helpers |
| `frontend/src/features/review/tradeRecords.test.js` | Extended coverage (carrier stays `test:trade-records`) |
| `frontend/src/kline/UnifiedKlineEngine.jsx` | Expose engine fit/overview wiring |
| `frontend/src/kline/kline-engine.js` | Engine-owned visible fit/overview toolbar action with accessible labeling |
| `frontend/src/styles.css` | Workspace tabs/date rail/context panel/editor styles |
| `frontend/package.json` | Broaden `test:trade-records` command to include review workspace tests; name unchanged |
| `docs/architecture.md` | Phase 6 truth update |
| `docs/kline-engine.md` | Phase 6 engine-ownership truth update |
| Lifecycle/state/evidence documents per `docs/operating-modes.md` | Plan metadata, four indexes, roadmap, `PROGRESS.md`, `HANDOFF.md`, phase receipts |

## 4. Remove manifest

No source or data file removal is planned. Removing obsolete JSX/CSS blocks inside modified files is allowed only after source and browser evidence prove no remaining consumer (plan §4.3). Known dead code `frontend/src/kline/DailyReviewChart.jsx` (defined but unimported at freeze time) is explicitly **out of scope** and stays untouched.

## 5. Component/state/control ownership table (frozen)

Current duplicate evidence uses `file:line` at freeze HEAD `d7350213`.

| Control family | Current visible duplicates | Target single owner | Page behavior |
| --- | --- | --- | --- |
| Timeframe `1m`/`5m` | engine `kline-engine.js:1028-1029`; `ReviewPage.jsx:496-497`; `StaticReviewsApp.jsx:542-543` | K-line engine toolbar | Pages invoke `setTimeframe` programmatically only |
| Replay Back/Step/Play/Pause | engine `:1030-1032`; `ReviewPage.jsx:498-500`; `StaticReviewsApp.jsx:544-546`; `BacktestPage.jsx:123-125`; `TeachingPage.jsx:90-91,93` | K-line engine toolbar | Pages drive replay only through the engine API |
| Speed/zoom/follow | engine only `:1033-1039` | K-line engine toolbar | unchanged |
| Fit/overview | **no visible engine control today** (imperative `fitRange` `kline-engine.js:2624`, wrapper `overview()` `UnifiedKlineEngine.jsx:95-103`); page buttons `ReviewPage.jsx:412,503`; `StaticReviewsApp.jsx:472,547`; `BacktestPage.jsx:126`; `TeachingPage.jsx:92` | K-line engine toolbar (new engine-owned fit/overview action with accessible label/state) | Pages may call `overview()`/`fitRange` for list navigation; no visible page duplicates |
| Indicators MA/VWAP, candle type/fill, theme | engine only `:1015-1019,1040-1043` | K-line engine toolbar | unchanged |
| Ticker/date | `ReviewPage.jsx:472-474` (flat mixed select); `TraderFilters.jsx:23-39` (shadow ticker/date authority); `DashboardPage.jsx:65` (first-20 mixed); `TeachingPage.jsx:87-89` (mixed); `StaticReviewsApp.jsx:455-461` (mixed) | Review workspace (ticker tabs + ticker-scoped date rail); `TraderFilters` ticker/date become readonly mirrors or are removed | One resolved market-day identity per context; Teaching keeps its page-specific day select scoped by the shared workspace model |
| Strategy | `ReviewPage.jsx:479-481`; `StaticReviewsApp.jsx:462-469` | Review workspace context panel | persists across ticker/date transitions when valid |
| Ext K/RTH window | `ReviewPage.jsx:485-495`; `StaticReviewsApp.jsx:531-541` | Review workspace context panel | declared localStorage persistence unchanged |
| Trader/eligibility/focus | `TraderFilters.jsx:41-70` embedded in Review/Static/Admin | Review workspace, availability-driven (§3.3 of plan) | unavailable traders never render; stale selection reconciled per context token |
| Rescan vs Backtest | both call the same `runBacktest()` (`ReviewPage.jsx:501-502` → `:362-366`) | Interactive Review, two distinct actions | Rescan recomputes the resolved day/strategy in place; Backtest navigates with current strategy/ticker context |
| Trade export/selection, assembly status | `ReviewPage.jsx:415-424,505` | Review workspace context panel | unchanged ownership |
| Edit entry (`交易记录 / 点位管理`) | admin-only icon in `Layout.jsx:45-50`; raw JSON textareas `AdminTradersPage.jsx:67-76` | Authenticated trader workspace; one-navigation-action discoverable with readonly/admin capability label | readonly inspects; admin edits via form + preview + existing PUT |
| Backtest run/result selection | `BacktestPage.jsx:92-95,122,132-137` | Backtest page | retained, page-specific |
| Teaching cutoff/reveal/prompt | `TeachingPage.jsx:87-94` | Teaching page | retained, page-specific; generic replay from engine |

## 6. Fixture inventory (`reviewWorkspace.fixtures.js`, created in Phase 0)

Pure data only; no DOM, API, SQLite, or repo-file reads. Covers:

1. **Asymmetric market-day history**: the real 49-day inventory (46 SPY dates 2026-05-12…2026-07-17 + QQQ 2026-07-10/14/17, all `extended` session) in interactive (`/api/market-days` item shape) and static (manifest `reviews[]` entry shape with `#<ticker>-<date>-extended` slugs) forms.
2. **Two traders**: `tang` (sort_order 10) and `vordin` (sort_order 20), registry order.
3. **Verified/pending records**: QQQ 2026-07-17 two verified vordin groups; QQQ 2026-07-14 two pending vordin groups (invisible to static export and to default display eligibility); SPY 2026-07-17 one verified tang group.
4. **Date with no visible trader**: SPY 2026-05-29 (zero trade groups; one tang note context) plus the static view of QQQ 2026-07-14 (pending-only → empty).
5. **Multi-ticker day preservation case**: a compact schema-faithful `trades-day-v1` document for 2026-07-17 mirroring the real three-group/two-ticker/two-trader shape plus one QQQ note context, with the expected untouched-ID set and per-type counts for preservation-diff assertions.
6. **Hash cases**: canonical `#spy-2026-07-17-extended` / `#qqq-2026-07-17-extended`; invalid `#spy-1999-01-01-extended` (unknown day), malformed `#qqq-2026-07-11`, wrong-case `#SPY-2026-07-17-EXTENDED`, and empty hash.
7. **Layout fixtures**: reference desktop `1672x941`, a representative narrow viewport, and collapsed-sidebar state for ownership/reading-order assertions.

## 7. Baseline control inventory notes (freeze-time facts)

- Shared app state (`frontend/src/main.jsx:17`) is `{tickers, marketDays, strategies, selectedDayId, selectedStrategyId}`; there is no selected-ticker state anywhere.
- `reviewHashRoute` (`tradeRecords.js:110-112`) already formats `#<ticker>-<date>-<session>` but is referenced only by tests; static hash resolution today is opaque slug equality against the manifest (`StaticReviewsApp.jsx:192,236,241`), with fallback to the first manifest review and hash write-back (`:224-227`).
- Static manifest entries already carry `slug`, `ticker`, `trade_date`, `session_mode` (`backend/scripts/export_static_reviews.py:183-201`), so client-side ticker partitioning needs no export change.
- Static export admits only `active` + `verified` trade records (`export_static_reviews.py:78-85`), so pending-only days (QQQ 2026-07-14) export the market day with zero trader groups.
- `test:trade-records` is the stable harness/CI carrier (`frontend/package.json:10`, `.harness/config.json`, `.github/workflows/project-harness.yml`); only its command line broadens.
