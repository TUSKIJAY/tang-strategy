# Phase 5 — Integrated UX, Accessibility, And Regression Acceptance

- Plan: `docs/exec-plans/active/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md` (`v3-round-1-review-foldback-2026-07-19`)
- Status: complete; `phase-5-complete` exit gate met on 2026-07-20
- Acceptance stack: fresh local copy at `/tmp/tang-phase5-integrated-i56dIM`, backend `8034`, interactive frontend `5196`, static server `5197`; no Kimi process reused or modified

## 1. Complete verification set

| Check | Result |
| --- | --- |
| backend | 78/78 pass in pinned `.venv`; `compileall` pass; existing FastAPI deprecation and two SQLite ResourceWarnings remain non-failing observations |
| frontend | 38/38 pass after the final accessibility assertions; normal and `VITE_STATIC_REVIEWS=true` builds pass, 1,754 modules each |
| lifecycle fixtures | 146/146 pass |
| harness/lifecycle | governed pass, auto pass, direct operating-modes pass, startup budget pass, launcher `bash -n` pass |
| SQLite | tracked and temporary copy both `integrity_check=ok`, foreign-key failures `0`, SHA-256 `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` |
| whitespace/scope | `git diff --check` pass; every source addition/modification is in the Phase 0 frozen manifest; no removal and no out-of-scope source path |
| static rebuild | fresh temporary 49-day / 9-strategy export and isolated static build pass |

## 2. Desktop integrated browser matrix (`1672 x 941`)

| Surface | Receipt |
| --- | --- |
| Data | 49 market days; deterministic SPY default; date rail contains SPY-only labels; QQQ/SPY tabs are programmatically selected |
| interactive Review | one engine, one engine Overview owner, no outer toolbar; SPY and QQQ reconcile date/chart/trader/export context; Ext K is a labeled switch and assembly status is a live status |
| Review keyboard/loading/error | Enter activates QQQ tab and QQQ 07-14 date; focus remains on the selected `aria-selected`/`aria-pressed` control; a delayed assemble request exposes `正在从 SQLite 组装复盘...` as `role=status aria-live=polite`; an injected 500 exposes `role=alert`, retains focus on QQQ 07-17, and recovers after the route is removed |
| Admin | capability label, form-driven editor, existing canonical save action, reused read-only chart, no primary raw JSON workflow; no save was performed in this phase |
| readonly | inspect/export and capability explanation visible; editor/save/registry mutation controls all absent |
| Backtest | `Run latest 10 days` executed successfully; 44 signals; one unified engine and one Overview owner |
| Teaching | rules/cases/training content loaded with one unified engine, one Overview owner, and the page-specific `Reveal full day`; no page-level Play/Pause duplicate |
| Static | shared ticker/date/trader contracts, no mutation/auth path, delayed manifest exposes a live loading status, injected day-payload 500 exposes `role=alert`, focus remains on the selected date, and recovery succeeds |

Positive fresh interactive and static sessions had no product error/warning; each recorded only the existing missing `favicon.ico` 404. Negative sessions additionally recorded the intentionally injected Review/static 500. These expected negative console entries are not relabeled as clean-console passes.

Several acceptance-script mistakes were kept separate from product truth: missing global `setTimeout`, a non-exact date locator that also matched trade cards, an incorrect Teaching heading string, and an incorrect readonly prose substring. Each was corrected and the affected case rerun to pass.

## 3. Narrow, focus, and programmatic-state acceptance (`820 x 1180`)

- Interactive Review computed one `820px` grid column with zero horizontal overflow; chart, ticker tabs, business context, availability filter, normalized groups, and signals remain reachable in reading order.
- Static Review computed one `820px` grid column with zero horizontal overflow; the QQQ rail contains exactly three QQQ dates, vordin is the only visible trader on 07-17, engine Overview count is 1, and mutation entry count is 0.
- Admin form has zero horizontal overflow. Entering `2026-07-17T09:42` keeps focus in the occurred-at field, renders `leg.events[0].occurred_at: ISO datetime with explicit offset required` in `role=alert`, and disables save. No temporary or canonical write occurred.
- Ticker identity is not color-only: ticker text, `role=tab`, `aria-selected`, and ticker-scoped date labels all carry the state. Dates use text plus `aria-pressed`; Ext K uses `role=switch` plus `aria-checked`; Focus uses `aria-pressed`.
- Review and Static async/error containers now explicitly use status/alert semantics; the editor canonical-read loading state is also a polite status.

## 4. Visual comparison

The canonical reference `docs/optimization/2026-07-19-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png` (relocated from `design/references/`) remains SHA-256 `57c34ea70bf7c6cab2c983b8feaedb6ad9be6f23fc02262ac7c97a48b156d3c5`. It was compared independently from behavior/accessibility acceptance.

The final 1672x941 Review preserves the reference direction: compact dark terminal, explicit QQQ/SPY parent tabs, ticker-scoped date rail, strategy/session/business actions in the left context, availability-driven trader/group stack, and one large engine-owned chart/toolbar. The authenticated shell navigation occupies additional left width, but does not reintroduce mixed dates or duplicate chart controls. The narrow composition intentionally reorders chart before the long sidebar stream and remains readable without horizontal overflow.

Visual inspection in Phases 3-5 found and fixed three issues that source tests alone missed: global engine CSS leaking into Admin, white-on-white Admin group buttons, and light trader cards/labels embedded in the dark Review/Static sidebar. The final desktop, narrow Review, QQQ Static, and narrow Admin validation images were all re-inspected after their respective fixes.

## 5. Multimodal evidence

Artifacts are under `output/playwright/review-workspaces-phase5-20260720/`:

| Artifact | SHA-256 |
| --- | --- |
| `01-data-desktop.png` | `12615b93c0be3971ecce70dbad4bdea4eb02632c642137fbe5fbd95f7e6cd487` |
| `02-review-spy-desktop.png` | `45dddfbbe0b52e52dd0930be3e278a5cdc70e8c2d52adea4c97c3de7cc588708` |
| `03-review-qqq-keyboard-recovered.png` | `5e20b5f835a39d17c3c8f06964035927bdde31a6d746319c9a2719eaf06e2d41` |
| `04-admin-desktop.png` | `a8217b286a1fee8c354ca1eb0aa2502690a3cd8039670e1028d3877684707d7f` |
| `05-backtest-desktop.png` | `e6ba65931df6f8933b09d66f10c2687b734bba703cf56f719f46f011fe8b7cd2` |
| `06-teaching-desktop.png` | `99b839adaa24517f4ade6b5350ed991c60253e9a6d5313457131a340be16a47a` |
| `07-review-narrow.png` | `4caef67c27b7d0e76172cfeceb75d68ef8329da40a1b33db1c29bc77b6462fd4` |
| `08-admin-narrow-validation.png` | `86dd2d12e0b02af5c86ec5a20fc06d9c32a8319ef23b6bfe5b92aadff8b1932d` |
| `09-readonly-desktop.png` | `c501433dcbf10821b591697332e64ff596d854a8351d757367fdef0d7a377e66` |
| `10-static-narrow.png` | `589004b05e98087115257746cf1bb4dcc40ee3dbd0495df10623621965b6754f` |

Phase 3 and Phase 4 screenshot sets remain complementary evidence for successful/failing editor writes and Static hash/no-trader behavior.

## 6. Protected boundaries and exit gate

The entire temporary content tree is recursively identical to `content/` after browser acceptance. Canonical and temporary registry hashes are both `cf6f3122c29e24e842e4ae29d04f772b7b07d1e8ad2fcc43820c7c41c0b2716c`; canonical and temporary 2026-07-17 hashes are both `0d292b4329d4966a429100fe89eac64a4e6fcd3924306c173461b396679488fc`. Pages workflow remains `7fe8c2e9bf54f4d33b556ba75250fdaa192bb6771661e461e44b562423c50dc8`; exporter remains `601548fae38a3206d7cdd382ed51ca1947791e8755ad580dcb095a2426c47996`; their scope diff is empty.

Every Phase 5 success criterion now has a named receipt. Failures and unavailable checks are classified explicitly. Tracked DB, canonical content, provider/broker, publisher/workflow, secrets, Git stage/commit, and remote boundaries are unchanged. The `phase-5-complete` exit gate is met.
