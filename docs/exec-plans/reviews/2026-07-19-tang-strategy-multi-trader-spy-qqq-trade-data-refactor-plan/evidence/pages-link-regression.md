# Pages And Link Regression Evidence

## Phase 0 Current Contract Capture

- Captured: `2026-07-19T03:33:59.319530+00:00`
- Source DB: a temporary byte copy of the tracked DB
- Tracked DB before/after SHA-256: `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`
- Provider, IB, remote Git, Pages, and hosted actions: not run

### Interactive assemble baseline

| Field | Value |
| --- | --- |
| Endpoint contract | `/api/reviews/assemble` |
| `market_day_id` | `43` |
| Ticker/date/session | `SPY` / `2026-07-17` / `extended` |
| `strategy_id` / slug | `8` / `tang-v4-4-slope-4-4` |
| Top-level keys | `annotations_1m`, `annotations_5m`, `bars_1m`, `bars_5m`, `market_day`, `meta`, `strategy`, `tang_trades` |
| 1m / 5m counts | `868` / `192` |
| Tang trade count | `1` |
| `tang_trades` keys | `date`, `notes`, `ticker`, `trades` |
| Sorted compact JSON SHA-256 | `95132bc6bc3089c0f1e8dee1728e87c843a883b1b0c778c7f56b2fe7b3300387` |

The payload was assembled by the current endpoint function against the temporary DB copy; no HTTP server or tracked DB startup hook was used.

### Static manifest and day baseline

The current exporter ran into a temporary directory with `limit=1`, `ticker=SPY`, and strategy families `v3,v4,v5`.

| Field | Value |
| --- | --- |
| Manifest SHA-256 | `437d6b0d54d4721802ff546131a1cedac04c1e7e08b9eb137d41664d0f652b61` |
| Review slug | `spy-2026-07-17-extended` |
| Day file | `days/spy-2026-07-17-extended.json` |
| Day file SHA-256 | `b3d14fd01f5fb924321b685be511d619e02e3c03a3a9caba8df6c633eef4a44a` |
| Day top-level keys | `annotations_1m`, `annotations_5m`, `bars_1m`, `bars_5m`, `market_day`, `meta`, `tang_trades` |
| 1m / 5m / Tang counts | `868` / `192` / `1` |
| Existing hash route | `#spy-2026-07-17-extended` |
| Strategies in manifest | `9` |

The generated timestamp makes the complete manifest hash capture-specific. The stable compatibility carriers are the slug/hash route, day filename, payload shape, ticker/date/session, and bar counts.

### Boundary file hashes

| File | SHA-256 |
| --- | --- |
| `AGENTS.md` | `5161322145ab79015700979f9cc28e0e3bc479d3e1a42fa8e0d977180e576694` |
| `docs/daily-publish-runbook.md` | `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac` |
| `docs/operating-modes.md` | `e62f225f9df3594ac7e6fb5b7112986e087f4f1881ed1414dfd06a5d1b6687e6` |
| `.github/workflows/project-harness.yml` | `898acd92cdc78f9a00692ae6f75a160d58c417ab27920c10892adbe71251c6db` |
| `.github/workflows/publish-static-reviews.yml` | `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d` |
| `backend/scripts/fetch_tv_live_extended_day.py` | `b33430692a2d174d1918dcc83770a0433cc21141ab2f10029e1999e63d17bd1d` |
| `backend/scripts/fetch_ib_live_extended_day.py` | `9020311fea38c5a51147a8d74657032e44826ff86a04197b41151eba7b18be70` |
| `backend/scripts/rebuild_live_extended_db.py` | `8474d3fff529cb6e594b602dc10f3ce69b0d83b7cb38087b2e3dfe5489c27d96` |
| `backend/scripts/export_static_reviews.py` | `ca4674b212800add93137ad2575cc9749705ab0e59355653cf3e3b184d98721c` |

No Pages workflow was invoked and no hosted URL was checked. This artifact is a local compatibility baseline only.

## Phase 1 Compatibility Recheck

The Phase 0 capture was repeated against a new temporary DB copy after Phase 1 implementation:

- API sorted compact JSON SHA-256: `95132bc6bc3089c0f1e8dee1728e87c843a883b1b0c778c7f56b2fe7b3300387` — unchanged;
- static day SHA-256: `b3d14fd01f5fb924321b685be511d619e02e3c03a3a9caba8df6c633eef4a44a` — unchanged;
- counts: 868 1m, 192 5m, one Tang trade — unchanged;
- top-level public member: `tang_trades` only — unchanged;
- hash route: `#spy-2026-07-17-extended` — unchanged;
- tracked DB before/after SHA-256: `76a885c2...28f8` — unchanged.

`backend/app/main.py`, `backend/scripts/export_static_reviews.py`, `.github/workflows/publish-static-reviews.yml`, `docs/daily-publish-runbook.md`, `AGENTS.md`, and `docs/operating-modes.md` have zero Phase 1 diff. No static build, Pages workflow, or hosted verification was run in Phase 1.

## Phase 2 Candidate Compatibility Recheck

The Phase 0 compatibility capture was repeated against the actual 46-day target-schema candidate after bars were re-keyed from `market_day_id` to the one active `dataset_id`:

- API sorted compact JSON SHA-256: `95132bc6bc3089c0f1e8dee1728e87c843a883b1b0c778c7f56b2fe7b3300387` — unchanged;
- static day SHA-256: `b3d14fd01f5fb924321b685be511d619e02e3c03a3a9caba8df6c633eef4a44a` — unchanged;
- counts: 868 1m, 192 5m, one Tang trade — unchanged;
- public trade member: `tang_trades` only — unchanged;
- day file and route: `days/spy-2026-07-17-extended.json` and `#spy-2026-07-17-extended` — unchanged;
- tracked DB SHA-256 before/after: `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8` — unchanged.

This is local candidate evidence only. No Pages workflow, hosted URL, provider, IB, or remote Git action was run.

## Phase 3 Canonical And Handler Compatibility Recheck

After adding the registry, 20 canonical daily files, and unregistered service/admin handlers, the existing runtime was rechecked against a fresh consistent temporary snapshot:

- API sorted compact JSON SHA-256: `95132bc6bc3089c0f1e8dee1728e87c843a883b1b0c778c7f56b2fe7b3300387` — unchanged;
- static day SHA-256: `b3d14fd01f5fb924321b685be511d619e02e3c03a3a9caba8df6c633eef4a44a` — unchanged;
- API top-level keys still end in the existing `tang_trades` member and do not include `trade_records`;
- counts remain 868 1m, 192 5m, and one Tang trade;
- no trade-record or trader route is registered in the FastAPI application;
- tracked DB SHA-256 remains `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`.

The new canonical directory is exercised only through focused handler/projection tests. No existing Review/Static consumer, Pages workflow, hash route, or hosted artifact switched in Phase 3.

## Phase 4 Frontend Compatibility Recheck

- both normal and `VITE_STATIC_REVIEWS=true` static Vite builds passed;
- a real Chromium session against `scripts/start-local-acceptance.sh` and a temporary 46-day DB snapshot loaded SPY 2026-07-17 Review, exercised 1m/5m/Step, produced 43 signals from the latest-10-day Backtest with Step/5m, and exercised Teaching advance/5m/full-day reveal; the only console error was the existing `favicon.ico` 404;
- the existing hash-route helper remains `#spy-2026-07-17-extended` under the asymmetric SPY/QQQ fixture;
- `ReviewPage.jsx` and `StaticReviewsApp.jsx` do not import `AdminTradersPage`, `TraderFilters`, `TraderTradeList`, or the new `trade_records` member;
- the new admin preview has no route and is not rendered by the current app;
- the K-line engine retains its existing `tang_trade` branch while the additive `trade_record` branch accepts explicit trader colors and independent triangle direction;
- the Pages workflow, runbook, AGENTS, operating modes, public API/static member, and tracked DB remain unchanged.

No Pages workflow, hosted URL, provider, IB, or remote Git action was run. Phase 4 is local fixture/build evidence only.

## Phase 5 Offline Pair And Static Recheck

The current-code temporary 48-day candidate at `/tmp/tang-phase5-current.N9HN1F/live.db` was exported into separate generated directories with the unchanged static exporter:

| Export | Result |
| --- | --- |
| Grandfathered SPY latest review | `spy-2026-07-17-extended`, 868/192, 9 strategies |
| SPY day SHA-256 | `b3d14fd01f5fb924321b685be511d619e02e3c03a3a9caba8df6c633eef4a44a` — exact Phase 0 baseline |
| Offline fixture QQQ review | `qqq-2026-05-11-extended`, 390/78, 9 strategies |
| QQQ day SHA-256 | `8e70e08d0e43f2fb73e18d1882c1dd1441c71391d7b4c1907fb0e168a3ca30b6` |
| Public payload boundary | both still expose only current `tang_trades`; neither exposes `trade_records` |
| Workflow syntax | local YAML parse passed: harness jobs `backend/frontend/harness`, Pages job `publish` |
| Frontend | normal/static builds passed; generated `dist` moved to `/tmp/tang-phase5-actual.AUEQpv/frontend-dist` |

The current candidate byte SHA-256 is `1503359defd0b276f9ee8806e934c70ce6e2317cc9f7c10d62e96121f9ea3d05`; all 46 grandfathered logical-day hashes remained unchanged. The prior generated build carrier remains outside the repository, and the completion-audit build was moved to `/tmp/tang-completion-audit.u8pZJK/frontend-dist`.

Pages workflow SHA-256 remains `75245998...694`; project-harness workflow remains `898acd92...d96`; the runbook, AGENTS, operating modes, Review/Static consumers, hash-route contract, and tracked DB have no Phase 5 cutover diff. No workflow was invoked and no hosted claim is made.
