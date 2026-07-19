# Phase 4 — Static Review Parity And Link Compatibility

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Status: complete; `phase-4-complete` exit gate met on 2026-07-20
- Delivery boundary: local temporary export/build/browser acceptance only; no publisher, Pages, remote, DB, or canonical-content mutation

## 1. Shared static contract

`StaticReviewsApp` now normalizes the existing flat manifest with `normalizeStaticDays`, resolves the initial/legacy/invalid hash through `resolveInitialWorkspace`, and uses the shared `ReviewContextPanel`, `switchTicker`, and `selectWorkspaceDay` paths. Ticker is the parent authority, the date rail contains only that ticker's real dates, a same-date switch is retained only when owned, and fallback canonicalizes the URL while announcing its reason rather than fabricating the requested day.

The static consumer also uses `deriveAvailableTraders` and `reconcileTraderSelection` before trader selection. Filters mirror the resolved ticker/date, verified/displayable availability controls visible trader names, and pending-only/no-trader days show one neutral status. Static Review contains no authenticated editor, admin route, or mutation action.

Chart-generic controls have one visible owner: the old static day list, page-level 1m/5m/Back/Step/Play/Overview footer, and second sidebar Overview action were removed. Strategy and Ext K remain Review-owned business context inside the shared context panel; the embedded engine alone renders timeframe/replay/fit/indicators/rendering/theme controls.

## 2. Pure tests and local build

- Frontend carrier: 37/37 pass, including manifest/interactive parity, legacy and invalid hash cases, ticker/date switching, stale trader reconciliation, unavailable-trader suppression, one-owner source pins, no static edit/auth path, and dark-sidebar contrast scoping.
- Normal Vite build: pass, 1,754 modules.
- Static Vite build: pass, 1,754 modules.
- Temporary export: tracked DB was copied byte-exact to `/tmp`; the exporter produced 49 review days (46 SPY + 3 QQQ) and 9 strategy documents. Manifest SHA-256 was `5c37b1d0b48a4efe3eb9c09df0cf6d1b8b4edc875e5cf33ac8e83b741ab15b3e`.
- The first isolated build command truthfully failed because Vite 8 does not accept CLI `--publicDir`; the Vite JS API was used instead. The first JS-API build omitted `VITE_STATIC_REVIEWS=true` and correctly opened the authenticated login app, so it was not accepted. The corrected isolated build set the static flag and served only the static app.
- `git diff --check`: pass. No generated file appeared under tracked `frontend/public` or `frontend/dist` status.

## 3. Fresh browser matrix

All final checks used Chromium at `1672 x 941` against an isolated local static server. Final console result: 0 errors and 0 warnings.

| Case | Result |
| --- | --- |
| empty hash/default | canonical `#spy-2026-07-17-extended`; SPY selected; all 46 rail labels SPY-only; Tang is the only available trader; one engine `data-action=overview`; zero outer footer and zero mutation/admin entry |
| SPY -> QQQ | canonical `#qqq-2026-07-17-extended`; same date retained; rail exactly QQQ 07-17/07-14/07-10; only 沃德哥 visible; chart and context both QQQ 07-17 |
| legacy deep link | `#/qqq-2026-07-14-extended` resolved and canonicalized to `#qqq-2026-07-14-extended` without substitution |
| verified-only/no-trader | QQQ 2026-07-14 rendered zero trader options and the neutral `当前 ticker/date 没有可显示的交易者点位。` status; no pending trader was exposed |
| invalid deep link | `#spy-1999-01-01-extended` deterministically fell back to SPY newest, canonicalized the hash, and announced `unknown-day` |
| authenticated boundary | no `编辑交易者点位`, Admin link, canonical read, save, or mutation path in static DOM/source |

The initial browser assertion used a case-sensitive accessible-name regex for `Overview`; the actual engine aria-label is `Fit chart to full day overview`, so that script reported a false negative while every captured value was correct. The stable `data-action=overview` assertion passed with count 1.

## 4. Multimodal receipts

Artifacts are under `output/playwright/review-workspaces-phase4-20260720/`:

| Artifact | SHA-256 | Receipt |
| --- | --- | --- |
| `01-static-spy-default.png` | `d7ec1ddb8afe30d638d9a696979c4fde9ed7ef6d399e018c3efcb7dcb2378148` | SPY default, ticker-scoped date rail, single-owner chart toolbar |
| `02-static-qqq-same-date.png` | `46027f001605b49cd27d0fa37951f1f0c38a21527e5d1f782a195d1a1a127f5a` | QQQ same-date switch, three QQQ dates, vordin-only records |
| `03-static-legacy-link-no-trader.png` | `aa963a7cf2d540861f6eaa2a50af46834a03e09f7111c5cda22665a8db29a11f` | legacy hash compatibility and honest no-trader state |
| `04-static-invalid-link-fallback.png` | `0b21b66ee5b32e9fff345cc042f86719c9f4b97f7f360c29dfe389b7fba3bc86` | deterministic invalid-route fallback and announcement |

Visual inspection found that shared trader cards inherited light Admin variables inside the dark Static sidebar. Dark styles are now scoped only under `.dr-sidebar`; computed mirror/trader text is `rgb(232, 231, 227)` on a dark trader background, while Admin retains its light defaults. The final QQQ screenshot was visually re-inspected after the fix.

## 5. Frozen boundaries and cleanup

- Tracked DB SHA-256: `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` before/after.
- Registry SHA-256: `cf6f3122c29e24e842e4ae29d04f772b7b07d1e8ad2fcc43820c7c41c0b2716c`.
- Canonical 2026-07-17 SHA-256: `0d292b4329d4966a429100fe89eac64a4e6fcd3924306c173461b396679488fc`.
- Pages workflow SHA-256: `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8`.
- Static exporter SHA-256: `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996`.
- Exact workflow/export/DB/content scope diff: empty.
- The local static server was stopped. Direct deletion of `/tmp/tang-phase4-static-tHbwnt` was rejected by the safety layer; the exact temporary root was moved recoverably to `/Users/neowang/.Trash/tang-phase4-static-tHbwnt-20260720-0244`. No repository-generated static output remains from this phase.

The exit gate is met: interactive/static share the pure workspace/trader/control contract, legacy hashes resolve, invalid hashes fail over explicitly, static exposes no mutation path, final browser/console/multimodal checks pass, and no remote/publication action occurred.
