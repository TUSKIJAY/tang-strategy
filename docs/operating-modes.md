# Tang Strategy Operating Modes

- Contract schema: `operating-modes-v1`
- Status: Accepted
- Authority source: `docs/decisions/2026-07-19-operating-modes-and-lifecycle-source.md`

This is the single normative repository contract for request routing, execution-plan lifecycle formats, reviewer evidence, authority boundaries, and routine market-data updates. `AGENTS.md` is the compact entry/router; `INSTRUCTIONS.md` owns stable project facts and commands. Neither file is a second copy of this contract.

## 1. Source Ownership

- One plan file in exactly one of `docs/exec-plans/proposed/`, `active/`, or `completed/` is the canonical lifecycle record.
- Review evidence belongs under `docs/exec-plans/reviews/<plan-slug>/`.
- The four lifecycle indexes, Exec Plan roadmap, `PROGRESS.md`, and `HANDOFF.md` are derived surfaces and must reconcile with canonical plan/review evidence.
- `.harness/config.json` configures verification only. It is never a lifecycle state store.
- Data Update states are an operational protocol evidenced by commands, data/provider metadata, DB checks, Git commits, workflow runs, and hosted checks. They are not a second committed database.
- Chat history and agent-private memory are not canonical repository state.

## 2. Peer Modes And Authority Dimensions

Coding Mode changes or inspects the system. Data Update Mode uses the existing system to update market data. They are peers; Data Update Mode is not a Coding Mode phase.

Evaluate every request independently across these dimensions:

- inspection/mutation: read-only, bounded local change, or planned system change;
- lifecycle: none, proposal, review, activation recording, or a named active phase;
- Git: no stage, stage, commit, push, PR, or merge;
- publication: none, local acceptance, or Pages publication;
- broker/provider: no connection, read/fetch prerequisite, or separately governed action;
- remote administration: none or an explicitly named setting change.

Ambiguity grants no additional authority. Local mutation or lifecycle authority never implies Git, publication, provider, broker, or remote-setting authority.

| Request intent | Route | Default authority |
| --- | --- | --- |
| Inspect, explain, diagnose, or verify | Coding Mode Lane 1 | read-only |
| Small change meeting every bounded criterion | Coding Mode Lane 2 | named local change only |
| Any hard proposal criterion is true or unresolved | Coding Mode Lane 3 | proposal/review only |
| Routine market-data fetch/rebuild/acceptance | Data Update Mode | Local Update Gate only |
| Existing daily trigger or equivalent explicit publish request | Data Update Mode | pending Publish Gate authority; local gates still mandatory |
| Data anomaly | Coding Mode Lane 1 first | diagnosis only, then evidence-based return or escalation |

## 3. Coding Mode

### Lane 1 — read-only inspection

Inspect repository, Git, docs, tests, logs, configuration, and data evidence. Diagnose and report without implementation. Ambiguous work and data anomalies begin here.

### Lane 2 — bounded direct maintenance

Lane 2 is legal only when every condition is true:

- one named outcome and bounded file surface are known before editing;
- no hard proposal criterion below applies;
- the change is locally reversible without migration or destructive cleanup;
- no security, authorization, market-data, DB, publication, or cross-module contract changes;
- proportionate local verification exists;
- the final handoff records why Lane 2 was appropriate.

Lane 2 needs no Exec Plan or independent review, but unrelated-change protection and separate Git/remote authority still apply.

### Lane 3 — proposed Exec Plan

Use Lane 3 when work affects any of these:

- DB schema/migration, rebuild/import semantics, promotion/rollback, or tracked-DB safety;
- market-data quality, session, source, provenance, or non-shrink contracts;
- Pages export/publish workflow or daily-publish authorization;
- authentication, secrets, security, authorization, or provider credentials;
- cross-backend/frontend/data contracts;
- multi-phase, destructive, broad, or difficult-to-rollback work;
- lifecycle checker, constrained formats, transitions, or governance policy.

If classification is uncertain, remain in Lane 1. No undocumented exception may bypass Lane 3.

## 4. Governed Lifecycle

The stages are proposal revision, independent design review, explicit user activation instruction, lifecycle activation recording, separate implementation start and phased work, independent implementation review, and closeout. Finishing one stage never grants the next.

- A proposed plan remains review-only even after `approve`.
- Activation recording moves exactly one plan to `active/`, records activation evidence, and sets `phase-0:not-started`; it performs no implementation.
- Implementation requires a separate explicit start/execute instruction and the phase entry gate.
- Implemented plans require an independent implementation review with `accept` before completed disposition.
- Transitions are manual lifecycle edits: verify authority, move one adjacent-state file, reconcile all four indexes/roadmap/two state blocks, and run the read-only checker. No transition helper is authorized by v1.

The current-state block tracks only the single plan presently in focus. Other proposed plans remain discoverable and validated through directories and indexes.

## 5. Constrained Format Package

The checker may interpret only the formats in this section. It must not infer lifecycle truth, authority, or Git state from unconstrained prose.

### Plan metadata

Every governed plan begins with one operative Markdown bullet per key using exact `- Key: value` syntax. Bullets inside HTML comments, fenced or indented code, multiline code spans, or raw HTML `code`/`pre` elements do not count:

```text
- Lifecycle schema: `operating-modes-v1`
- Status: Proposed|Active|Completed
- Plan slug: `<unique-slug>`
- Revision: `<stable-revision-id>`
- Plan author ID: `<non-empty-id>`
- Design reviews: none|`<review-path>@<approve|revise|reject>@<target-revision>`[, ...]
- Latest design verdict: none|approve|revise|reject
- Review independence: none|legacy-unattested|attested
- Activation evidence: none|`user-instruction:<durable-reference>`
- Current phase: none|phase-0|phase-1|phase-2|phase-3|phase-4|phase-5|phase-6
- Phase state: none|not-started|in-progress|blocked|complete
- Phase entry gate: none|`<gate-token>`
- Next gate: `<gate-token>`
- Implementation review: none|`<review-path>@accept`
- Final disposition: none|Completed|Terminated|Rejected|Superseded|Archived
- Verified implementation commit: none|`<40-hex-commit>`
- Lifecycle reconciliation commit: none|`<40-hex-commit>`
```

Additional human fields are allowed. Each constrained key appears exactly once; duplicates fail instead of using first- or last-write wins. Gate tokens must be non-empty and use only letters, digits, periods, underscores, colons, `@`, `/`, or hyphens.

State invariants:

- Proposed: `Status=Proposed`, no activation/current phase, and a next gate beginning with `design-review`, `review`, `revision`, `plan-revision`, or `activation-recording`.
- Active: latest matching-revision design review is `approve`, independence is `attested`, activation matches `user-instruction:<non-empty-token>`, and phase/phase state/entry gate/next gate are non-`none`.
- Completed: final disposition is non-none. `Final disposition=Completed` always classifies the plan as implemented and requires an `accept` implementation review even when commit values are `none`; any other disposition with implementation review or implementation commit evidence also requires that `accept`. Commit values may be `none` only when no commit was authorized.
- Review-field consistency: `Design reviews=none` requires both `Latest design verdict=none` and `Review independence=none`; a new-schema plan with design reviews requires `Review independence=attested`.
- Historical bare review filenames are accepted only for explicitly migrated `operating-modes-legacy-v1` completed plans. Every review declared by a new-schema plan requires the complete constrained metadata below, including reviews of prior revisions; metadata-only migration may add those fields without rewriting historical findings. New-schema plans use repository-relative review paths.

### Independent review metadata

A qualifying review must be authored from a context that did not draft the reviewed revision, independently inspect repository evidence, and contain the following operative Markdown bullets outside comments, Markdown code carriers, or raw HTML `code`/`pre` elements:

```text
- Review target: `<plan-path>`
- Review target revision: `<revision-id>`
- Review type: design|implementation|closeout
- Reviewer ID: `<non-empty-id>`
- Plan author ID: `<non-empty-id>`
- Independence declaration: `attested`
- Evidence method: `<non-empty-summary>`
- Verdict: approve|revise|reject|accept
- Confidence: low|medium|high
```

The checker validates unique keys, structure, target/revision, vocabulary, and unequal author/reviewer IDs. A review target is an exact repository-relative `docs/exec-plans/<proposed|active|completed>/<plan filename>` path, and the artifact is a direct Markdown file under `docs/exec-plans/reviews/<plan-slug>/`. A `Design reviews` entry requires `Review type: design`; `Implementation review` requires `Review type: implementation`. Human review validates identity, independence truth, evidence quality, user instructions, and publication authority.

### Fixed index rows

Each index contains exactly one operative canonical four-cell header followed immediately by exactly one `| --- | --- | --- | --- |` separator. Tables inside HTML comments, fenced or indented code, multiline code spans, or raw HTML `code`/`pre` elements do not count. The headers are `Plan | Status | Review | Next gate`, `Plan | Current phase | Evidence | Next gate`, `Plan | Disposition | Verification | Final commit`, and `Plan | Reviews | Latest verdict | Lifecycle state` for Proposed, Active, Completed, and Reviews respectively. Every header, separator, data row, and sentinel begins and ends with `|`; a missing terminal delimiter fails. Reserved words such as `Plan` or `Decision` cannot introduce another skipped row.

Each fixed data row has exactly four cells, and its Plan cell is exactly one canonical Markdown link with no appended text or second link. Each plan link appears exactly once in its state index. A Proposed plan with design reviews links the latest one and otherwise uses exact `none`; Active evidence always resolves to the latest review artifact; Completed verification resolves to the declared implementation review and otherwise uses exact `none`. Evidence-free rows reject links. The reviews index contains one row per plan, lists the exact direct Markdown artifact set once, derives its latest verdict from the final listed artifact, and uses the matching lifecycle state. When the artifact set is empty, the row links the canonical plan instead of a non-durable empty review directory and uses exact `none` for both Reviews and Latest verdict.

An empty state index requires exactly `| None | — | — | none |`; an empty reviews index requires exactly `| None | — | none | None |`. A None sentinel cannot coexist with a plan row. Other no-link data rows, extra cells (including a trailing empty cell), missing sentinels, and multiple sentinels fail.

```text
proposed:  | [Title](./plan.md) | Proposed | [review-N](../reviews/.../review-N.md): verdict | <next-gate-token> |
active:    | [Title](./plan.md) | phase-N:<phase-state> | [evidence](...) | <next-gate-token> |
completed: | [Title](./plan.md) | <Final disposition> | [implementation review](...) | <40-hex-or-none> |
reviews:   | [Title](./review-dir/) | [review-N](...)[, ...] | <latest-verdict> | <Proposed|Active|Completed> |
no review: | [Title](../<state>/<plan>.md) | none | none | <Proposed|Completed> |
```

Roadmap lifecycle sections contain only rows shaped as:

```text
- [Title](./<state>/<plan>.md) — <Proposed|Active|Completed>; canonical details: [<state> index](./<state>/index.md)
```

The checker compares exact plan-link/state sets, not prose summaries.

### Current-state blocks

`PROGRESS.md` and `HANDOFF.md` each contain exactly one matching block. The single start marker must precede the single end marker, and only the bounded interval is parsed; missing, reversed, nested, or unclosed forms fail:

```text
<!-- operating-modes-state:start -->
- Current plan: `<plan-slug-or-none>`
- Lifecycle status: `Proposed|Active|Completed|None`
- Current phase: `none|phase-N`
- Phase state: `none|not-started|in-progress|blocked|complete`
- Next gate: `<gate-token>`
<!-- operating-modes-state:end -->
```

Live Git truth never appears in this block. These legacy structured keys are forbidden outside an explicit historical evidence block: `Branch/HEAD`, `Current HEAD`, `Git state`, `Current worktree`, and `Worktree status`.

```text
<!-- git-evidence:historical:start -->
- Verified at: `<timestamp-or-date>`
- Verified commit: `<40-hex>`
- Observation: `<historical statement>`
<!-- git-evidence:historical:end -->
```

## 6. Data Update Mode

The state sequence is:

`requested -> date_resolved -> fetched -> quality_passed -> candidate_verified -> local_accepted -> publish_authorized -> committed -> published -> hosted_verified`

The TV and IB adapters currently import/upsert into the tracked DB by default after producing a valid seed payload; `--skip-import` exists, but the daily contract does not use it. Candidate-first protection begins at `rebuild_live_extended_db.py`. Therefore a successful fetch may already be an unaccepted tracked-DB mutation. A later failure must report before/after evidence and must not claim unchanged DB bytes.

### Local Update Gate

1. Resolve a completed NYSE session using the actual calendar and current ET, including holidays and early closes.
2. Capture Git scope and tracked-DB evidence before fetch.
3. Use TradingView first without checking, starting, or requesting IB Gateway.
4. Apply the documented TV retries and hard quality gates.
5. Request IB fallback only after named TV retry exhaustion or hard-gate failure; never mix TV/IB bars within one market day.
6. For IB, require whole-day count, gap, and session evidence before `quality_passed`.
7. Run canonical candidate-first rebuild; reject semantic/integrity/foreign-key/drift/date/non-market shrink and never use `--allow-date-loss` routinely.
8. Require the requested day plus non-empty 1m and 5m assemble/API payloads and mandatory DB checks.
9. Validate user-supplied Tang SPY 0DTE trade/context JSON when applicable.
10. Record optional static export/build/browser smoke as executed or not run; never turn not-run into pass.
11. Stop at `local_accepted` unless publish authority exists.

### Publish Gate

Only the daily trigger phrases in `AGENTS.md` or an equivalent explicit publish instruction create pending publish authority. Pending authority cannot skip local gates. Local acceptance, green checks, or a changed DB do not grant commit/push/publish. Commit scope remains the authorized tracked DB and applicable Tang trade/context JSON. Push, Pages workflow completion, and hosted URL verification are separate states.

### Escalation and return

Stop Data Update Mode for missing/unrecoverable history, integrity/foreign-key failure, unexplained DB drift, prior-row repair, schema/quality/source/tool/publisher changes, `--allow-date-loss`, gate weakening, code edits, or fabricated data. Diagnose in Coding Mode Lane 1. Return to the last safe data state only when evidence proves a transient environment/input issue; otherwise route the required system change through Lane 2 or Lane 3 without inheriting code authority from the data request.

## 7. Checker And Evidence Boundary

The focused checker is read-only and Python-stdlib-only; it may call installed `git` for dynamic truth. The governed harness composes it for an explicit `--root`; the minimal profile does not.

Machine fixtures cover plan discovery/uniqueness, duplicate constrained keys, metadata/state invariants, Proposed gate categories, exact index/roadmap/review-artifact sets, review target/type/revision matching, bounded current-state blocks, historical Git markers, required constrained paths/routing, executable verification carriers, read-only behavior, external-root composition, and governed/minimal profile separation. Constrained plan/review/template bullets and index tables are parsed only from operative Markdown outside HTML comments, fenced or indented code, multiline CommonMark code spans, and closed, nested, or unclosed raw HTML `code`/`pre` elements. Current-state and historical-evidence comment markers use their dedicated bounded parsers.

Required repository routes are canonical Markdown links resolving to this contract outside HTML comments, Markdown code carriers, and nested or unclosed raw HTML `code`/`pre` elements. Inline code inside a real link label remains legal. The project workflow has unique top-level mapping keys and contains a unique direct `on.pull_request.branches` trigger including `main`; duplicate event/field keys and nested lookalikes do not count. Plain, single-quoted, or double-quoted constrained mapping keys are equivalent, and `branches` accepts a direct block sequence or flow sequence with plain or quoted scalar items.

The unique top-level `jobs` mapping uses unique direct job IDs. Required commands are accepted only from ordered steps in the same direct job on `ubuntu-latest` whose direct keys are exactly `name`, `runs-on`, and `steps`; workflow/job `env` or `defaults`, any job condition/extra key, duplicate key, shadow mapping, or unavailable runner disqualifies that carrier. Every direct item in that job's `steps` sequence is a non-null mapping. A required step contains only optional non-empty string `name` and exactly one `run`; source comments, YAML null words, numeric/boolean coercions, quoted whitespace, bare/null/scalar items, quoted/bare conditions, `shell`, `working-directory`, `continue-on-error`, `env`, duplicate keys, or any other direct modifier disqualify it. Commands in separate jobs do not prove order unless a future contract explicitly defines and checks a dependency relation.

An inline/quoted `run` scalar must equal the required command after removing only matching scalar quotes. Literal and folded block headers accept YAML's optional chomping and explicit indentation indicators; blocks are normalized according to their declared style, with source comments retained as shell text, and the resulting complete scalar must exactly equal the command. A folded command may span physical source lines when YAML folding produces the exact command. Branch block/flow sequences are fully consumed and every member is a supported non-empty plain or quoted string scalar; empty members, mappings, nested collections, anchors, aliases, tags, and malformed quotes fail closed. Anchors, aliases, merge keys, flow mappings other than the declared branch sequence, document separators, and other undeclared workflow source forms are outside this constrained grammar and fail closed. The direct `pull_request` mapping contains only `branches`, so path/type filters cannot silently weaken the carrier. Non-job `steps`, multi-line shell flow that does not normalize exactly, dead branches, heredoc bodies, early exits, comments/no-op programs, and nested keys do not count. The two required commands retain declared order in one qualifying job.

The focused checker does not infer business behavior from unconstrained AGENTS prose, runbook text, Python source, or unrelated workflow text. Unchanged daily trigger/runbook/adapter/rebuild/publisher compatibility for this implementation is carried by baseline-to-HEAD exact diff/hash evidence plus the named behavior tests and human inspection. Existing backend tests remain the carrier for actual calendar, TV quality, rebuild, non-shrink, DB, and assemble behavior. Human evidence remains required for identity, authority, command order beyond the constrained workflow carrier, optional checks, bounded-maintenance classification, and anomaly return decisions. Real commit/push/Pages/hosted proof is deferred to a separately authorized daily run.

No fixture or offline inspection may claim a real provider fetch, broker connection, tracked-DB update, push, Pages publication, or hosted verification passed.

## 8. Data Update Verification Carrier Map

This map binds the Data Update cases to current repository evidence without turning offline inspection into a real daily-run receipt.

| Case | Current carrier | Evidence boundary |
| --- | --- | --- |
| Calendar resolves normal, early-close, and holiday sessions | `backend/tests/test_fetch_tv_live_extended_day.py::test_market_calendar_resolves_normal_early_close_and_holiday`; `test_expected_times_support_normal_and_early_close_sessions`; future authorized run | The deterministic expected-time test passes without provider access. The calendar test requires the pinned `requirements-tv.txt` environment; a missing dependency is a prerequisite failure, not a pass. |
| IB is checked before a TV failure | `AGENTS.md` daily trigger contract plus `docs/daily-publish-runbook.md` Source policy/Pre-flight; human command evidence | Contract prohibits it; only a real command log can prove order. |
| TV RTH/session/OHLCV/derived-5m gate fails | `test_sparse_extended_session_passes_when_rth_is_complete`, `test_missing_rth_minute_fails_hard_gate`, expected-times test, and source inspection of `validate_source_rows`/payload derivation | Existing tests exercise RTH coverage and early-close counts. A future run supplies provider payload evidence. |
| IB fallback lacks whole-day/gap/session proof | Daily runbook Section 2 plus future authorized run | The IB adapter reports counts/gaps but the runbook/human gate owns acceptance; no offline fixture claims it passed. |
| TV and IB are mixed within one day | Runbook Source policy and this contract; future provenance evidence | Prohibited by contract; real payload metadata proves the selected source. |
| Fetch imports before rebuild | `backend/scripts/fetch_tv_live_extended_day.py` and `fetch_ib_live_extended_day.py` default branches calling `import_market_json`; future before/after evidence | `--skip-import` exists, but the tracked default path imports. Inspection proves code shape, not a real DB mutation. |
| Candidate loses market/non-market rows or fails integrity/drift | all 11 tests in `backend/tests/test_rebuild_live_extended_db.py` plus all 4 in `backend/tests/test_db_safety.py` | Temporary SQLite fixtures cover empty/subset/corrupt/semantic/non-market/drift/rollback and successful promotion without touching the tracked DB. |
| Local seed is incomplete relative to tracked DB | `test_subset_seed_reports_missing_date_and_preserves_original_bytes`; `test_no_seed_refuses_and_preserves_original_bytes` | Default rebuild refuses shrink. The override test proves the override exists but does not authorize its routine use. |
| Requested day, DB checks, or non-empty assemble payload fails | rebuild/DB safety tests; completed recovery-plan acceptance evidence; future authorized run | No dedicated current unit test proves a newly requested real day through `/api/reviews/assemble`; that receipt remains mandatory and deferred to the real update. |
| Optional static export/build/page smoke is not run | Daily runbook Section 5 and human handoff evidence | Record `not run`; do not call it pass. |
| Local acceptance has no publish authority | Git status plus human authority evidence | Stop before stage/commit/push/publish unless the Publish Gate is separately open. |
| Publish trigger exists but a local gate fails | `AGENTS.md` triggers, Local Update Gate ordering, and human command evidence | Pending publication authority cannot skip or relabel a failed local gate. |
| Tang trade/context is supplied | Daily runbook Section 4, existing `load_tang_trades` validation command, and future authorized run | Validate the user-supplied JSON before an authorized commit; absence of supplied context creates no synthetic trade. |
| Anomaly proves no system defect | human diagnosis evidence | Return only to the last safe Data Update state for a bounded retry. |
| Anomaly requires a system change | Coding Mode hard-routing contract plus human diagnosis evidence | Stop Data Update Mode and route the change; the data request grants no code authority. |
| Routine update edits code, weakens a gate, uses date-loss override, or fabricates data | contract inspection plus human diff/command evidence | Stop; none is allowed as a completion shortcut. |
| Routine existing-system update has no Exec Plan | peer-mode/routing contract inspection | Allowed when all existing gates work and no system change is needed. |
| Daily triggers, runbook sequence, adapters/rebuild, and Pages publisher remain compatible | baseline-to-HEAD exact diff/hash inspection of `AGENTS.md`, `docs/daily-publish-runbook.md`, both fetch adapters, `rebuild_live_extended_db.py`, and `.github/workflows/publish-static-reviews.yml`; named behavior tests where available | Compatibility evidence only; the focused lifecycle checker does not parse these unconstrained sources and this is not a hosted publish test. |
| Commit/push/Pages/hosted sequence succeeds | future authorized run | No offline fixture, implementation phase, or green local check can satisfy this row. |

Current runtime gaps are explicit: the default adapters can mutate the tracked DB before rebuild acceptance; IB quality acceptance depends on runbook/human evidence; and a newly requested day's assemble receipt is collected during the real update rather than by this contract-only implementation. Any proposal to change those facts is separate Coding Mode work.
