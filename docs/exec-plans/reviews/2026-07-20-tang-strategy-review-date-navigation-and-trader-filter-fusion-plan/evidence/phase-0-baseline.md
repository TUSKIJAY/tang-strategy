# Phase 0 Baseline — Review Date Navigation And Trader Filter Fusion

- Recorded: 2026-07-20T16:52:37Z
- Implementation start: `user-instruction:2026-07-21-execute-review-date-filter-fusion-plan` (goal OBJECTIVE: 全权执行active plan)
- Plan revision: `v2-review-foldback-2026-07-20`
- Branch: `codex/project-harness`
- HEAD: `3d0f59f090d0bf37b8ec3fc947e70d1536a076f9`
- Status:

```
## codex/project-harness...origin/codex/project-harness [ahead 6]
?? .playwright-cli/
?? output/mockups/
?? output/phase-3-acceptance-20260719/
?? output/playwright/multimodal-acceptance-20260719/
```

## Contract freeze

| Constant | Value |
| --- | --- |
| dateNavigation | `exhaustive` \| `progressive` (default exhaustive) |
| progressive opt-in | ReviewPage only |
| recent limit | `12` |
| chip inline / summary | `<=6` / `>=7` |
| CALL / PUT | `#6F9F7A` / `#E06B66` |
| utility label | `Review 工具` |
| UI font stack | Microsoft YaHei / 微软雅黑 / PingFang SC / Noto Sans SC / sans-serif |
| mono stack | ui-monospace / SFMono-Regular / Menlo / Consolas / monospace |
| shell badges | visible `可编辑`/`只读`; a11y full sentences |

## Exact Add/Modify/Delete manifest

### Modify
- `frontend/src/features/review/ReviewContextPanel.jsx`
- `frontend/src/features/review/reviewWorkspace.js`
- `frontend/src/features/review/reviewWorkspace.test.js`
- `frontend/src/features/review/TraderFilters.jsx`
- `frontend/src/features/review/tradeRecords.js`
- `frontend/src/features/review/tradeRecords.test.js`
- `frontend/src/features/review/TraderTradeList.jsx`
- `frontend/src/pages/ReviewPage.jsx`
- `frontend/src/pages/StaticReviewsApp.jsx`
- `frontend/src/pages/AdminTradersPage.jsx`
- `frontend/src/components/Layout.jsx`
- `frontend/src/styles.css`
- `docs/exec-plans/active/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md`
- `docs/exec-plans/active/index.md`
- `docs/exec-plans/completed/index.md`
- `docs/exec-plans/reviews/index.md`
- `docs/exec-plans/roadmap.md`
- `PROGRESS.md`
- `HANDOFF.md`

### Add
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/evidence/phase-0-baseline.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/evidence/phase-1-date-navigation.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/evidence/phase-2-bchip-focus-removal.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/evidence/phase-3-chrome-direction-shell.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/evidence/phase-4-integrated-acceptance.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/evidence/phase-5-closeout.md`
- `docs/exec-plans/reviews/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan/implementation-review-packet-001.md`

### Delete
(none)

### Optional modify if needed
- `frontend/src/features/review/TradeExportControls.jsx`
- `docs/architecture.md`
- `docs/kline-engine.md`

### Explicitly excluded
- `backend/**`
- `content/**`
- `data/**`
- `strategies/**`
- `frontend/src/api/**`
- `frontend/src/kline/**`
- `backend/scripts/export_static_reviews.py`
- `.github/workflows/**`
- `docs/daily-publish-runbook.md`
- `frontend/public/reviews/**`
- `frontend/dist/**`
- `.playwright-cli/**`
- `output/**`

No production-source additions or removals. Pure progressive helpers land inside existing `reviewWorkspace.js`.

## Baseline hashes and protected counts

| Path | SHA-256 | Bytes | Kind |
| --- | --- | --- | --- |
| `frontend/src/features/review/ReviewContextPanel.jsx` | `f4a2a9d542e04e373b4dcfeab3f89d34e54fb505786067b0bcca5bce29761cc7` | 2239 | candidate |
| `frontend/src/features/review/reviewWorkspace.js` | `29010eae47746e156b21a27151280fcef4807e90166914c2b76f131505b31c4c` | 8690 | candidate |
| `frontend/src/features/review/reviewWorkspace.test.js` | `19ad1fa7045b28a1158de4992309886a9709855cdc27244280bf00ba777900e7` | 19028 | candidate |
| `frontend/src/features/review/TraderFilters.jsx` | `f10600f62a347de4a264954eaaa450dfed208e1b743c9bf6c283b77f981a0a93` | 4347 | candidate |
| `frontend/src/features/review/tradeRecords.js` | `34a4cda0bbdf43bf2e9963d2e9a809be5c8ae69f8135c3dee5b00c1ca7d8adbc` | 17542 | candidate |
| `frontend/src/features/review/tradeRecords.test.js` | `e1401fb4dd14ddd205681d56fad5dafa46455f619b32b65dc000673155ff35c8` | 28886 | candidate |
| `frontend/src/features/review/TraderTradeList.jsx` | `bcea09e4748510fecbcc07d8b5ea3bba2eeae6bdf3d74e441bc3156e670b7a44` | 3020 | candidate |
| `frontend/src/features/review/TradeExportControls.jsx` | `ab85dd011fb2e29246eb18f0e4a513381d7d65699ffbb1f1747798b3671d5439` | 945 | candidate |
| `frontend/src/pages/ReviewPage.jsx` | `56e46d6d5fe8f3fc6a5d3e461957a31bf87483506c972b7c03d51d028aa5a23f` | 24728 | candidate |
| `frontend/src/pages/StaticReviewsApp.jsx` | `335485c2073221371f4b1e129882984302f8ad7b084537d93c8394e90d92e9e1` | 26055 | candidate |
| `frontend/src/pages/AdminTradersPage.jsx` | `06c68be37969cea2800d8c5f1c2ac2d4652e509467cf2a6c5b597ef64483c52a` | 20371 | candidate |
| `frontend/src/pages/DashboardPage.jsx` | `da087155d846d44f7516026cfd98300baac86a73d833d1929ec351f0f9a7a210` | 3875 | candidate |
| `frontend/src/components/Layout.jsx` | `0760136dba5d7130d2efb7338dce74eb75ef9eaba28759673358d2799eace291` | 3114 | candidate |
| `frontend/src/styles.css` | `faebf6d00b3ea04da533e51b65e5175817f42b1a461c11ce53b9b959d86670c2` | 38571 | candidate |
| `data/sqlite/tang_strategy_live_extended.db` | `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` | 25702400 | protected |
| `content/traders/index.json` | `cf6f3122c29e24e842e4ae29d04f772b7b07d1e8ad2fcc43820c7c41c0b2716c` | 345 | protected |
| `.github/workflows/publish-static-reviews.yml` | `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8` | 2014 | protected |
| `backend/scripts/export_static_reviews.py` | `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996` | 8753 | protected |
| `.github/workflows/project-harness.yml` | `321abad63dfc0c2437b107314bf1422c32012ee79fbdca1c9b8ed377c6f80add` | 2634 | protected |
| `docs/daily-publish-runbook.md` | `2010e73b65483009a2273a380faa3ae081f0bb725089013effe7dd755d0f230f` | 7834 | protected |

### DB counts
```json
{
  "market_days": 49,
  "datasets": "err:no such table: datasets",
  "traders": 2,
  "trade_groups": 33,
  "trade_legs": 33,
  "trade_events": 46,
  "market_days_by_ticker": {
    "QQQ": 3,
    "SPY": 46
  },
  "integrity_check": "ok",
  "foreign_key_check_rows": 0
}
```

## Caller inventories (before)

### DateRail / ReviewContextPanel
- ReviewPage — will opt in progressive
- DashboardPage, AdminTradersPage, TraderPointEditor, StaticReviewsApp — exhaustive default

### focusedTraderId carriers
- tradeRecords.js, TraderFilters.jsx, ReviewPage, StaticReviewsApp, AdminTradersPage, tradeRecords.test.js

### Registry hue on shared trade surfaces
- TraderFilters / TraderTradeList inline `--trader-color`; CSS direction/card borders

### Left-column tools
- Review: Ext K + Rescan + Backtest
- Static: Ext K

## Browser before-state

Browser screenshots deferred to Phase 4 integrated matrix when local acceptance launcher is available; structural before-state is frozen via source inventories and protected hashes above. Unit suite and builds are recaptured during Phase 0 verification receipts under implementer scratch `phase-0/`.

## Authority

- Implementation/start/closeout: authorized by goal OBJECTIVE 全权执行active plan against Active plan revision v2.
- Push/PR/merge/Pages/provider/broker/tracked-DB/canonical-content/remote: **unauthorized**.
- Standing checkpoint kinds on plan still list design-review/proposal-revision/activation-recording only; durable local commits deferred unless a later exact-manifest authority is granted. Work proceeds as local uncommitted implementation.
