# Phase 1 — Pure Workspace And Trader-Availability Contracts

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Closed at: `phase-1:complete`, 2026-07-19
- Scope: pure state contracts + frontend Node tests only. No DOM/API/DB/content/workflow change; no page rewiring (Phase 2/3).

## 1. Implemented surface

| Path | Change |
| --- | --- |
| `frontend/src/features/review/reviewWorkspace.js` | New pure workspace contract: `normalizeInteractiveDays`/`normalizeStaticDays`, `listTickers`/`preferredTicker`, `datesForTicker`/`groupDatesByMonth`, `findDay`/`findDayByKey`, `formatDaySlug`/`formatDayHash`/`parseDayHash`, `contextToken`, `resolveInitialWorkspace`, `switchTicker`, `selectWorkspaceDay`, `compareWorkspaceDays` |
| `frontend/src/features/review/tradeRecords.js` | Added plan-§3.3 contract: `displayableTradeGroups`, `deriveAvailableTraders`, `reconcileTraderSelection`, `mirrorWorkspaceContext`, `filtersMatchWorkspace` (appended; existing exports untouched) |
| `frontend/src/features/review/TraderFilters.jsx` | New `context` prop renders ticker/date as readonly mirrors (`trade-context-mirror`, `aria-readonly`); new `availableTraderIds` prop renders only displayable traders with one neutral `role="status"` empty state; Focus exposes `aria-pressed`. Legacy select branch retained until Review/Static/Admin rewiring in Phases 2-3, when it must be removed |
| `frontend/src/features/review/reviewWorkspace.test.js` | 10 fixture-driven tests over `reviewWorkspace.fixtures.js` |
| `frontend/src/features/review/tradeRecords.test.js` | +6 tests (availability, pending/empty day, reconciliation, mirror divergence, export reconciliation, TraderFilters source pins); existing 11 untouched and green |
| `frontend/package.json` | `test:trade-records` broadened to run both test files in deterministic order; carrier name unchanged (`.harness/config.json` and CI untouched) |

Behavior notes: default resolution is SPY-newest even though QQQ sorts first canonically; ticker switch keeps the same date only when owned (otherwise newest real date); invalid/missing hash or day falls back deterministically with a reported `resolution` and never fabricates a ticker/date; `contextToken` (`TICKER:DATE:SESSION`) is the dependent-state reset token with `contextChanged` on every transition.

## 2. Verification matrix (plan Phase 1)

| Required proof | Carrier |
| --- | --- |
| Asymmetric histories (46 SPY + 3 QQQ) | `reviewWorkspace.test.js`: asymmetric inventory, month grouping |
| SPY default | `reviewWorkspace.test.js`: default resolution, SPY-absent fallback |
| Missing target date | `reviewWorkspace.test.js`: explicit day selection missing-date; ticker switch `newest-date` |
| Invalid hash | `reviewWorkspace.test.js`: unknown-day/malformed/case-mismatch/empty hash cases |
| Pending-only / static behavior | `tradeRecords.test.js`: pending-only and empty days expose no visible trader |
| No-trader state | `tradeRecords.test.js`: SPY 2026-05-29 and static pending day availability `[]` |
| Intentional empty selection | `tradeRecords.test.js`: same-context empty selection stays empty |
| Context-change fallback | `tradeRecords.test.js`: empty intersection re-selects all available |
| Focused-trader clearing | `tradeRecords.test.js`: unavailable focus cleared, available focus kept |
| Export selection reconciliation | `tradeRecords.test.js`: reconciled filters drive markers/lists/exports from one resolved object |
| Readonly mirror + labels/states | `tradeRecords.test.js`: TraderFilters source pins (`context ? (`, mirror markup, `aria-readonly`, empty state, `aria-pressed`) + mirror divergence fixtures |
| No DOM/API side effects | both modules import nothing outside pure data fixtures; tests run under plain `node --test` |

## 3. Results

- `npm run test:trade-records`: 28/28 pass (11 pre-existing + 17 new).
- `npm run build`: pass; `VITE_STATIC_REVIEWS=true npm run build:static-reviews`: pass.
- `check-operating-modes.py`, governed + auto harness, startup budget: pass; `git diff --check`: pass.
- Backend untouched in this phase (76/76 baseline unchanged); tracked DB/content/workflow hashes unchanged.

## 4. Exit gate statement

`phase-1:complete`: the state contract has no DOM/API side effects (both modules are pure), every transition produces one internally consistent context/filter result (resolution + contextToken + reconciled selection), and current trade-record tests remain green. Known deferral inside the frozen manifest: the legacy editable ticker/date branch of `TraderFilters.jsx` is removed when Review/Static (Phase 2) and Admin (Phase 3) are rewired to the shared workspace; until then callers pass no `context` prop and keep current behavior.
