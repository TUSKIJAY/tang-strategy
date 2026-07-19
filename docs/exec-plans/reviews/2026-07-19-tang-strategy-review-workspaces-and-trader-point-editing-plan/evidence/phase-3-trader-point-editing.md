# Phase 3 — Availability-Driven Filters And Trader Point Editing

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Status: complete; `phase-3-complete` exit gate met on 2026-07-20

## 1. Implemented surface (so far)

| Path | Change | Status |
| --- | --- | --- |
| `backend/app/services/trade_records.py` | `handle_trader_registry_admin_read` / `handle_trade_day_admin_read`: admin-only canonical reads returning write-valid documents; missing day raises `FileNotFoundError` (no fabricated default); no DB access | done |
| `backend/app/main.py` | `GET /api/admin/traders` + `GET /api/admin/trade-records` (404 missing day, 400 malformed, 403 readonly via `require_admin`); the existing two PUTs and the public GET unchanged | done |
| `backend/tests/test_trade_records.py` | route registration pinned as exact method+path pairs (GET+PUT on each admin path); new admin read shape/role tests; new public-projection-not-write-base round-trip tests | done (78/78) |
| `frontend/src/features/review/tradeCandidate.js` | pure candidate contract: `EDITOR_CONSTANTS`, `nextGroupId`, `buildNewGroup` (explicit normalization block per review-003 foldback), `buildNewEvent`, `mergeGroupIntoDay`, `preservationDiff` (fail-closed), `validateGroupForm` | done (35/35) |
| `frontend/src/api/client.js` | `Api.adminTraders`, `Api.adminTradeDay` | done |
| `frontend/src/components/Layout.jsx` + `styles.css` | `交易记录 / 点位管理` entry visible to every authenticated user with `admin 可编辑` / `只读` capability badge | done |
| `frontend/src/features/review/TraderPointEditor.jsx` | form/preview/save editor (implemented by the plan author after the delegated attempt produced no output in 45 min) | done (35/35) |
| `frontend/src/pages/AdminTradersPage.jsx` | capability-labeled rewrite; raw JSON textareas removed; workspace-context inspection; admin registry metadata form | done (35/35) |
| `frontend/src/main.jsx` | passes `marketDays` to the admin page | done |
| `frontend/src/styles.css` | `tp-*` editor/registry styles (light admin theme) | done |

Editor contract notes: the canonical write base is `Api.adminTradeDay` (public projection never seeds a write, pinned by source test); a 404 day requires the explicit `新建该日期文档` action; the form pins immutable IDs/trader/underlying/date context; every edit computes `validateGroupForm` + `preservationDiff` live and the save button is disabled unless both pass; save is `window.confirm`-gated, calls only the existing admin PUT of the complete merged day, retains unsaved state on failure with the server message surfaced, and never auto-retries; the preview is one reused `UnifiedKlineEngine` with candidate markers (no second chart implementation).

Availability-driven trader rendering and the neutral empty state were already delivered in Phase 2 and are exercised in this phase's browser matrix.

## 2. Verification receipts (so far)

- Backend: 78/78 tests (76 baseline + 2 new admin-read/projection suites), `compileall` pass.
- Route pin: `{(GET|PUT, /api/admin/traders)}` and `{(GET|PUT, /api/admin/trade-records)}` exact; no other verbs or twin routes.
- Live API smoke (temporary uvicorn, tracked DB untouched): admin registry GET `200`; readonly registry/day GET `403`; admin day GET returns `trades-day-v1` with 3 groups / 1 context / SPY+QQQ; missing date `404`; malformed date `400`.
- Frontend: 35/35 tests including candidate construction, full-day merge preservation (untouched IDs carried by reference), fail-closed diff (tamper/remove/context-change/two-add), and form-validation field paths.
- Fixture day `FIXTURE_MULTI_TICKER_DAY` previously proven write-valid against the real backend validator (Phase 0), round-trip stable.

## 3. Acceptance history

- Pure candidate/merge/diff: done (§2). Editor browser flows (readonly vs admin), mixed SPY/QQQ temp-copy save with untouched-ID receipts, injected validation failure, injected projection/cleanup failure, before/after canonical + temp DB coherence: pending.
- Round-1 browser FAIL and fix: the first acceptance run failed the edit-note step — `preservationDiff` was called with `targetGroupId: candidate.trade_group_id` (undefined; the candidate is the day document, not a group), so the badge falsely reported `untouched group changed` for the edited group itself. Fixed to `stripMeta(form).trade_group_id` in both the diff memo and the `save()` confirm summary; 35/35 tests and both builds re-verified. This is exactly the fail-closed behavior the preservation contract was designed to surface — the guard rejected a mismatched target rather than passing silently.
- Round-2 browser results (11/19 PASS with 2 implementation defects, both fixed and re-verified): (A) the Direction select did not sync `legs[0].option_type`, so the client validator correctly failed closed (`option type must match direction`) and blocked a non-CALL new point — fixed by syncing both fields in the Direction `onChange`; (B) the editor detected the missing-day 404 via a message regex while `client.js` threw only the response body — fixed by attaching `error.status` in `client.js` and mapping `err.status === 404` to the explicit missing-day branch. Round-2 receipts that PASSED: readonly capability surface (badge, explanation, zero mutation controls, zero textareas), admin editor visible, edit-note save on `tg_20260717_vordin_qqq_001` with byte-equivalence of the other two groups vs `git show HEAD` (both stringify orders), registry metadata save (vordin sort_order 25 via API), validation gate on missing offset, and boundary hashes (all 22 `content/trades/*.json`, `content/traders/index.json`, tracked DB `125fcc9d...`) byte-identical with mutations landing only in the temp copies. The full matrix is re-running against the fixed tree for the final receipt.
- Tracked DB and canonical repository remain unchanged during acceptance (receipts recorded here when complete).

## 4. Round-1 browser finding and fix

The first acceptance pass (10 steps planned, stopped at step 3) found a real UI wiring bug: `TraderPointEditor` computed the preservation diff with `targetGroupId: candidate.trade_group_id`, but `mergeGroupIntoDay` returns the whole day document, so the id was `undefined` and the diff reported the edited target group itself as `untouched group changed`. Pure tests passed the correct id explicitly and missed the wiring. Fix: pass `targetGroupId: stripMeta(form).trade_group_id`; the source pin now asserts the exact wiring. 35/35 frontend tests and build re-verified. Readonly capability steps 1-2 and the preview rendering passed in that pass; the full matrix re-run against the fixed tree follows.

## 5. 2026-07-20 takeover and final acceptance

The prior Kimi run stopped on a provider usage-limit error before a complete acceptance result. Its processes and `output/phase-3-acceptance-20260719/` artifacts were treated as diagnostic history only. The final run used an independently owned stack at frontend `5194`, backend `8033`, temporary content `/tmp/tang-codex-phase3-20260720/content`, and temporary database `/tmp/tang-codex-phase3-20260720/acceptance.db`; the earlier stack was neither killed nor overwritten.

### 5.1 Event-time defect, reproduction, and fix

- Fresh reproduction: after a user supplied `occurred_at`, the browser candidate still held `time_precision: null` and `time_incomplete: true`; authoritative validation rejected it with `time_incomplete: must be false when occurred_at is present`.
- Fix: `applyOccurredAt` now treats a non-empty timestamp as known time (`time_precision: minute` when no explicit precision exists, `time_incomplete: false`, provenance `user_provided`) and clearing it restores the unknown-time tuple. The form validator mirrors the paired backend rules instead of permitting an internally contradictory candidate.
- Regression: frontend carrier increased to 36/36 and pins both known/cleared transitions plus the editor wiring. Normal and static Vite builds and `git diff --check` passed.

### 5.2 Successful temp-copy mutation and preservation receipt

- At `1672 x 941`, an admin created `tg_20260717_vordin_qqq_003` for QQQ/2026-07-17/vordin with event time `2026-07-17T09:42-04:00`. Before save the UI showed `time_precision=minute`, unchecked `time_incomplete`, `user_provided` provenance, enabled save, and the candidate marker in the reused chart. The confirm summary reported one added group while preserving three existing groups and one context.
- After the existing complete-day PUT, the temporary day changed from 3 to 4 groups. `tg_20260717_tang_spy_001`, `tg_20260717_vordin_qqq_001`, `tg_20260717_vordin_qqq_002`, and `note_contexts` remained value-exact. All 22 temporary canonical days validated; the temporary DB projected the new group; SQLite integrity was `ok` and foreign-key failures were `0`.
- The admin and readonly capability/API matrix passed: admin canonical registry/day reads `200`; readonly canonical reads `403`; missing day `404`; malformed date `400`; readonly public projection `200` and remained `trade-records-v1`. The readonly browser exposed inspect/export only, with no editor, save, or registry mutation controls.

### 5.3 Failure-coherence receipts

- Server-authoritative replay: the saved timestamp was changed in unsaved state to the invalid New York offset `2026-07-17T09:42-05:00`. The PUT returned `400`, the exact field error was surfaced, unsaved input remained visible, and the temporary content and DB hashes stayed byte-identical across the failed request. The DB retained the valid `-04:00` value with integrity `ok` / FK `0`.
- Client replay: `2026-07-17T09:42` (missing offset) produced the field path `leg.events[0].occurred_at`, retained focus/input, and disabled save before any request.
- Projection/cleanup fault coverage: the two focused atomic/coherence tests passed, including post-promotion backup-cleanup failure preserving coherent content/DB state. The first command used a non-package test module path and collected two import errors; the corrected command passed 2/2. The complete backend suite then passed 78/78, with `compileall` passing.

### 5.4 Visual and console receipt

Fresh artifacts are under `output/playwright/review-workspaces-phase3-20260720/`:

| Artifact | SHA-256 | Receipt |
| --- | --- | --- |
| `01-time-contract-before-save.png` | `da11db511b25727439e6bc779f83e1e659232ccece9cb89746c1af7147b09a4e` | complete known-time tuple and candidate preview before save |
| `02-time-contract-after-save.png` | `7cf1c2334e9c2e8d6ba46ec91cec5669ddc18f466130558ea303c22869d02413` | successful save on the temporary copies |
| `03-server-validation-failure.png` | `e5666de70ff94bac1855ffeaac057f87618f7b14835528399cd94bcbffdba099` | server-authoritative invalid-offset failure |
| `04-client-validation-gate.png` | `36f2e325a961ae355866e14dbde1b792b10fdb486b622e01273d1cd5cea09df1` | client field gate and retained input |
| `05-readonly-capability.png` | `72ffa6c52837cd3860e4950b516be6e2105cd6f540fd7071dab533a78ea225e6` | readonly capability surface and absent mutation controls |
| `06-admin-contrast-fixed.png` | `6b8727e5a930cee9a648b6ab1cf3b1b294055c8fa1e4f49a07391f37c7efe4d2` | corrected light-theme text contrast after scoping engine CSS |

Visual inspection found the engine's dynamic `:root` and `html, body` CSS leaking into the host Admin page and a white-on-white group-picker label. The variables are now scoped to `.kline-engine`, standalone demo styling to `#demo-page`, and host buttons explicitly use `var(--ink)`. Computed text became `rgb(24, 23, 19)` on white; source tests pin the isolation and contrast rules. Fresh positive admin/readonly sessions contained only the existing favicon `404`; the negative server replay additionally contained the expected `400` request and no app exception, warning, or `500`.

### 5.5 Protected boundaries and exit gate

Canonical SHA-256 values after acceptance: tracked DB `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0`; registry `cf6f3122c29e24e842e4ae29d04f772b7b07d1e8ad2fcc43820c7c41c0b2716c`; canonical 2026-07-17 day `0d292b4329d4966a429100fe89eac64a4e6fcd3924306c173461b396679488fc`; Pages workflow `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8`; static exporter `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996`.

All Phase 3 exit conditions are met: form-only admin edit, reused candidate chart/list effect, readonly denial, availability suppression, exact untouched preservation and intended `+1` group delta, plus client/server/projection-cleanup coherence replays. No tracked DB, canonical content, auth/write boundary, provider, publisher, Git stage/commit, or remote action occurred.
