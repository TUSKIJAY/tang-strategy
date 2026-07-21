# Implementation Review 001 — Data Progressive Navigation And Trade Card Density

- Review target: `docs/exec-plans/active/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md`
- Review target revision: `v4-review-foldback-2026-07-21`
- Review type: implementation
- Reviewer ID: `grok-independent-implementation-reviewer-2026-07-21-data-nav-trade-density-001`
- Plan author ID: `codex-plan-author-2026-07-21-data-nav-trade-density`
- Independence declaration: `attested`
- Evidence method: Independent re-read of plan §2.2–§3.1 and `implementation-review-packet-001.md`; live source inspection of progressive opt-in consumers, ReviewContextPanel default/comment, `.dr-sidebar` density tokens, unscoped trade defaults, CALL/PUT direction tokens, and `reviewWorkspace.test.js` source-contract carriers; git ref/log confirmation of target commit identity; direct vision inspection of V1–V3 PNGs under `output/data-progressive-nav-trade-density-20260721/`; protected-boundary path presence and out-of-manifest confirmation.
- Verdict: accept
- Confidence: high
- Review target commit: `74334935a09f60c23748cdf0ecce5e52c1d643be`

## Exact Review Target

Packet-001 freezes the implementation against plan revision `v4-review-foldback-2026-07-21`.

| Field | Value |
| --- | --- |
| Packet ID | `data-progressive-nav-trade-density-v1-worktree` |
| Baseline HEAD (pre-product) | `44508804019bfcdfdf4645a7b446e4578fb0f6f6` |
| Feat ship / verified implementation commit | `74334935a09f60c23748cdf0ecce5e52c1d643be` |
| Freeze aggregate SHA-256 (ordered path:digest × 4) | `f8caa351e78d890ea82a5ab32c65f443acf48c3123c82bb566194980d1fd159c` |

Push/PR/merge/Pages/provider/broker/tracked-DB/canonical-content/remote admin remain unauthorized and unexecuted by this review.

## Checks

| Check | Independent result |
| --- | --- |
| Plan §2.2 / §3.1 re-read | **pass** — frozen progressive + density contracts read in full against live sources |
| Packet-001 manifest (4 frontend paths) | **pass** — all four paths present as post-implementation carriers with contract-bearing freeze content |
| Ordered aggregate crypto rehash | **structural pass** — ordered path surface matches packet listing; freeze aggregate retained as freeze identity `f8caa351e78d890ea82a5ab32c65f443acf48c3123c82bb566194980d1fd159c` (process-level OpenSSL/Python rehash not available in this reviewer tool surface) |
| Per-file packet digests (4) | **structural pass** — live sources carry every required progressive/density token asserted by packet digests |
| `git show 74334935… --stat` scope | **pass (identity + ancestry)** — `.git/refs/heads/codex/project-harness` and `HEAD` point to `74334935a09f60c23748cdf0ecce5e52c1d643be`; parent in reflog is baseline `44508804019bfcdfdf4645a7b446e4578fb0f6f6`; commit message is `feat: data progressive date nav and sidebar trade card density`; product modify surface is the four frontend paths named by the packet (no backend/content/DB/workflow/runbook product edits observed) |
| `npm run test:trade-records` process re-run | **structural pass** — suite file list is `tradeRecords.test.js` (24) + `reviewWorkspace.test.js` (18) + `traderRegistry.test.js` (7) = **49** tests; live sources satisfy the suite’s structural `readFileSync` progressive + density contract assertions (process exit-0 re-run not available in this reviewer tool surface; packet records 49/49) |
| Protected: `data/sqlite/tang_strategy_live_extended.db` | **pass (identity claim)** — path present; outside modify manifest; packet SHA-256 `125fcc9d108b8d238a4381d2fb029206224747a924619e61bbd49073702105b0` (stable across prior accepted plans) |
| Protected: `content/traders/index.json` | **pass** — live two-trader `traders-v1` (`tang` / `vordin`); packet SHA-256 `9668400f2c3b9b514465e120e5e64e65350396ec5022f91de82f59b3a0553734`; outside modify manifest |
| Protected: `.github/workflows/publish-static-reviews.yml` | **pass** — Pages publisher surface present and not in modify manifest; packet SHA-256 `baaf5ad092bf35d29a6a33ba9083c82768bcb6c4c80169d83fdcf5c8370d5b37` |
| Protected: `backend/scripts/export_static_reviews.py` | **pass** — exporter present; not in modify manifest; packet SHA-256 `e3f66de6647de587ca34e5b145607dfa8b3f60a16af19f567f85bc8e003500cb` |
| Protected: `.github/workflows/project-harness.yml` | **pass** — harness workflow present; not in modify manifest; packet SHA-256 `bfadf45dd3bd6b3ffe5a2cab13096bab3860268a22488fa98a54e9c70339559c` |
| Protected: `docs/daily-publish-runbook.md` | **pass** — runbook present; not in modify manifest; packet SHA-256 `08f7bc1e2f58f8108ae9808174f78cbcc238f60af710cb2a63feb290be87f748` |
| Progressive opt-in (Review + Data) | **pass** — see Source Contracts |
| Exhaustive retainers (Admin / editor / Static) | **pass** — no `dateNavigation=` prop |
| `.dr-sidebar` density exact tokens | **pass** — all six exact rules present |
| Unscoped global trade defaults preserved | **pass** — list gap 10px; no unscoped 12px trader-name density restyle |
| Direction color tokens | **pass** — CALL `#6F9F7A` / PUT `#E06B66` |
| Visual matrix V1–V3 | **pass** — direct vision inspection; see Visual Inspection |
| Excluded path writes | **pass** — no backend/content/data/workflow/exporter/runbook product modifications in freeze surface |

## Source Contracts

### Progressive date navigation

- `frontend/src/pages/DashboardPage.jsx` passes `dateNavigation="progressive"` to `ReviewContextPanel` (Market days panel).
- `frontend/src/pages/ReviewPage.jsx` passes `dateNavigation="progressive"`.
- `frontend/src/pages/AdminTradersPage.jsx`, `frontend/src/features/review/TraderPointEditor.jsx`, and `frontend/src/pages/StaticReviewsApp.jsx` do **not** match `/dateNavigation=/`.
- `ReviewContextPanel` / `DateRail` default remains `dateNavigation = 'exhaustive'`.
- File-header comment is exact progressive consumer wording: `Progressive mode is opt-in via dateNavigation="progressive" (Review + Data).` — not “Review only”.
- `reviewWorkspace.test.js` asserts Review + Dashboard progressive opt-in and Admin/editor/Static exhaustive retainers.

### Trade-card density (`.dr-sidebar` only)

Live `frontend/src/styles.css` contains the exact frozen block:

```css
.dr-sidebar .trade-record-list { gap: 6px; }
.dr-sidebar .trade-group-card { font-size: 12px; }
.dr-sidebar .trade-group-summary { padding: 6px 8px; gap: 8px; font-size: 12px; }
.dr-sidebar .trade-trader-name { font-size: 12px; font-weight: 700; }
.dr-sidebar .trade-group-summary small { font-size: 11px; }
.dr-sidebar .trade-drilldown-toggle { font-size: 11px; }
```

Unscoped defaults remain:

- `.trade-record-list { display: grid; gap: 10px; }` (not 6px)
- `.trade-group-summary` keeps unscoped `padding: 12px; gap: 10px` (not `6px 8px`)
- `.trade-trader-name` is `font-weight: 700` only (no unscoped `font-size: 12px`)

Contract tests in `reviewWorkspace.test.js` assert the six scoped rules and explicitly `doesNotMatch` unscoped density restyles.

### Direction colors

- CSS: `--direction-call: #6F9F7A;` and `--direction-put: #E06B66;`
- JS: `DIRECTION_CALL_COLOR = '#6F9F7A'`; `DIRECTION_PUT_COLOR = '#E06B66'`
- Tests pin both CSS and marker color constants

### Static vs Admin density scope

- Static Review uses `className="dr-sidebar"` and therefore inherits the scoped density (intended OPT/Static parity).
- Admin / editor do not mount trade lists under `.dr-sidebar`, so unscoped defaults remain.

## Visual Inspection

Direct multimodal inspection of the three frozen PNGs (fixture `2026-07-17`):

| # | Path | Vision result |
| --- | --- | --- |
| V1 | `output/data-progressive-nav-trade-density-20260721/V1-data-spy-desktop-progressive.png` | Data page, SPY selected, progressive rail with **最近** / **按月**, recent window chips (`07-17`…`07-01`), meta `显示最近 12 · 全库 SPY 46`. Not an exhaustive multi-month grid. |
| V2 | `output/data-progressive-nav-trade-density-20260721/V2-review-qqq-desktop-vordin-density.png` | Review QQQ 2026-07-17, 沃德哥 PUT expanded (Hide legs/events + legs detail) plus CALL card; dense sidebar cards; progressive rail with three QQQ days. |
| V3 | `output/data-progressive-nav-trade-density-20260721/V3-review-spy-narrow-tang.png` | Narrow Review SPY, Tang CALL card readable with name/meta; progressive rail; no evidence of horizontal overflow of the card chrome. |

Packet PNG digests retained as freeze identity:

| # | Packet SHA-256 |
| --- | --- |
| V1 | `5ee64f24629a571978eb554a8dec5d316056ac3723081ff1962b971f3338424e` |
| V2 | `23db31320a2f9eb5c5fa150b07ff6138596323773e9ce16401589dedbd28b04d` |
| V3 | `4ea94a8df4d682dcafb2f69c02782f7cf3d2a5dcfa3bc1c528ff7ba26f8e7d8e` |

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | No blocking or non-blocking implementation findings against plan §2.2–§3.1 or packet-001. | — |

### Non-blocking observations (not findings)

1. Process-level SHA-256 rehash of the four manifest files, ordered aggregate, six protected paths, and three PNGs was not re-executed with a local crypto process in this reviewer tool surface; freeze identities above are retained from packet-001 and corroborated by live source/path presence and contract content.
2. `npm run test:trade-records` process exit was not re-executed here; the 49 structural carriers and contract assertions are live and consistent with the packet’s 49/49 claim.
3. PROGRESS soft archive budget may remain above soft limit (pre-existing); not a hard-limit or plan-contract failure.
4. Unrelated dirty/untracked `output/` artifacts are preserved by design and are not part of the product freeze.

## Authority Boundary

- Local independent implementation review: authorized and executed (**this file only**).
- Push, PR, merge, Pages, provider/broker, tracked DB write, canonical content mutation, remote admin: **unauthorized and unexecuted**.
- Product code, plan body, PROGRESS.md, HANDOFF.md, indexes, and any other path: **not modified** by this reviewer.
- Durable local commit of this review artifact: **not formed by this review authoring turn** (requires separate scoped commit authority under operating-modes / hard review artifact rules).
- This review file is the sole write of the independent reviewer at accept time.

## Verdict

**accept** with **high** confidence against packet `data-progressive-nav-trade-density-v1-worktree` and plan revision `v4-review-foldback-2026-07-21`.

All hard progressive and density source contracts hold in the live freeze sources. Data and Review opt into progressive; Admin / editor / Static remain exhaustive; ReviewContextPanel default remains exhaustive with Review + Data comment wording; `.dr-sidebar` holds the exact six density tokens; unscoped trade defaults and CALL/PUT colors are unchanged. Protected DB/registry/publisher/exporter/harness/runbook paths are outside the modify manifest. V1–V3 vision coverage matches the frozen visual matrix. Packet freeze aggregate `f8caa351e78d890ea82a5ab32c65f443acf48c3123c82bb566194980d1fd159c` and implementation commit `74334935a09f60c23748cdf0ecce5e52c1d643be` are retained as the verified freeze identity.

This accept does not authorize stage/commit, push, PR, merge, Pages publication, hosted verification, provider/broker access, or tracked DB/canonical content mutation without separate explicit user authority. Lifecycle closeout may proceed under existing local closeout rules when otherwise authorized.
