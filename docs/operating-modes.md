# Tang Strategy Operating Modes

- Contract schema: `operating-modes-v2`
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

The TV and IB one-symbol adapters are provider primitives. The daily contract invokes them only through `update_spy_qqq_market_day.py`, which stages both tickers with import disabled and admits one same-provider candidate only after pair quality, preservation, integrity, and drift gates pass. A failed pair must leave the tracked DB and both accepted seeds on the prior coherent boundary.

### Local Update Gate

1. Resolve a completed NYSE session using the actual calendar and current ET, including holidays and early closes.
2. Capture Git scope and tracked-DB evidence before fetch.
3. Use the SPY/QQQ pair orchestrator with TradingView first without checking, starting, or requesting IB Gateway.
4. Apply the documented retries and hard quality gates independently to both tickers, then require same date/session/provider and no partial accepted-seed write.
5. Request IB fallback only after a named ticker's TV retry exhaustion or hard-gate failure; rerun the complete pair and never mix TV/IB providers.
6. For IB, require whole-day count, gap, and session evidence for both tickers before `quality_passed`.
7. Require the orchestrator's single candidate to preserve all grandfathered days and normalized trade projections, pass integrity/foreign keys/drift, and never use `--allow-date-loss` routinely.
8. Require both requested market days plus non-empty 1m and 5m assemble/API payloads and mandatory DB checks.
9. Validate user-supplied canonical trader/day JSON when applicable; admin writes must keep content and DB projection rollback-coherent.
10. Record optional static export/build/browser smoke as executed or not run; never turn not-run into pass.
11. Stop at `local_accepted` unless publish authority exists.

### Publish Gate

Only the daily trigger phrases in `AGENTS.md` or an equivalent explicit publish instruction create pending publish authority. Pending authority cannot skip local gates. Local acceptance, green checks, or a changed DB do not grant commit/push/publish. Commit scope remains the authorized tracked DB and applicable canonical trader/day JSON. Push, Pages workflow completion, and hosted URL verification are separate states.

### Escalation and return

Stop Data Update Mode for missing/unrecoverable history, integrity/foreign-key failure, unexplained DB drift, prior-row repair, schema/quality/source/tool/publisher changes, `--allow-date-loss`, gate weakening, code edits, or fabricated data. Diagnose in Coding Mode Lane 1. Return to the last safe data state only when evidence proves a transient environment/input issue; otherwise route the required system change through Lane 2 or Lane 3 without inheriting code authority from the data request.

## 7. Checker And Evidence Boundary

The focused checker is read-only and Python-stdlib-only; it may call installed `git` for dynamic truth. The governed harness composes it for an explicit `--root`; the minimal profile does not.

Machine fixtures cover plan discovery/uniqueness, duplicate constrained keys, metadata/state invariants, Proposed gate categories, exact index/roadmap/review-artifact sets, review target/type/revision matching, bounded current-state blocks, historical Git markers, required constrained paths/routing, executable verification carriers, read-only behavior, external-root composition, and governed/minimal profile separation. Constrained plan/review/template bullets and index tables are parsed only from operative Markdown outside HTML comments, fenced or indented code, multiline CommonMark code spans, and closed, nested, or unclosed raw HTML `code`/`pre` elements. Current-state and historical-evidence comment markers use their dedicated bounded parsers.

Required repository routes are canonical Markdown links resolving to this contract outside HTML comments, Markdown code carriers, and nested or unclosed raw HTML `code`/`pre` elements. Inline code inside a real link label remains legal. The project workflow has unique top-level mapping keys and contains a unique direct `on.pull_request.branches` trigger including `main`; duplicate event/field keys and nested lookalikes do not count. Plain, single-quoted, or double-quoted constrained mapping keys are equivalent, and `branches` accepts a direct block sequence or flow sequence with plain or quoted scalar items.

The unique top-level `jobs` mapping uses unique direct job IDs. Required commands are accepted only from ordered steps in the same direct job on `ubuntu-latest` whose direct keys are exactly `name`, `runs-on`, and `steps`; workflow/job `env` or `defaults`, any job condition/extra key, duplicate key, shadow mapping, or unavailable runner disqualifies that carrier. Every direct item in that job's `steps` sequence is a non-null mapping. A required step contains only optional non-empty string `name` and exactly one `run`; source comments, YAML null words, numeric/boolean coercions, quoted whitespace, bare/null/scalar items, quoted/bare conditions, `shell`, `working-directory`, `continue-on-error`, `env`, duplicate keys, or any other direct modifier disqualify it. Commands in separate jobs do not prove order unless a future contract explicitly defines and checks a dependency relation.

An inline/quoted `run` scalar must equal the required command after removing only matching scalar quotes. Literal and folded block headers accept YAML's optional chomping and explicit indentation indicators; blocks are normalized according to their declared style, with source comments retained as shell text, and the resulting complete scalar must exactly equal the command. A folded command may span physical source lines when YAML folding produces the exact command. Branch block/flow sequences are fully consumed and every member is a supported non-empty plain, single-quoted, or single-line YAML double-quoted string scalar. Double-quoted source accepts raw tab plus YAML printable scalar ranges U+0020-U+007E, U+00A0-U+D7FF, U+E000-U+FFFD, and U+10000-U+10FFFF; other raw controls, line breaks, surrogates, and BMP U+FFFE/U+FFFF fail closed. The listed supplementary range is authoritative, including its YAML-accepted plane-end values. Named and `\x`/`\u`/`\U` escapes may represent their declared decoded values, including values that cannot appear raw. Empty members, mappings, nested collections, anchors, aliases, tags, YAML 1.1/1.2 numeric coercions, unquoted terminal-colon mapping indicators, and malformed quotes/escapes fail closed; quoted terminal colons remain strings. Anchors, aliases, merge keys, flow mappings other than the declared branch sequence, document separators, and other undeclared workflow source forms are outside this constrained grammar and fail closed. The direct `pull_request` mapping contains only `branches`, so path/type filters cannot silently weaken the carrier. Non-job `steps`, multi-line shell flow that does not normalize exactly, dead branches, heredoc bodies, early exits, comments/no-op programs, and nested keys do not count. The two required commands retain declared order in one qualifying job.

The focused checker does not infer business behavior from unconstrained AGENTS prose, runbook text, Python source, or unrelated workflow text. Unchanged daily trigger/runbook/adapter/rebuild/publisher compatibility for this implementation is carried by baseline-to-HEAD exact diff/hash evidence plus the named behavior tests and human inspection. Existing backend tests remain the carrier for actual calendar, TV quality, rebuild, non-shrink, DB, and assemble behavior. Human evidence remains required for identity, authority, command order beyond the constrained workflow carrier, optional checks, bounded-maintenance classification, and anomaly return decisions. Real commit/push/Pages/hosted proof is deferred to a separately authorized daily run.

No fixture or offline inspection may claim a real provider fetch, broker connection, tracked-DB update, push, Pages publication, or hosted verification passed.

For lifecycle subjects declaring `operating-modes-v2`, the same focused checker also enforces the strict-superset metadata, review-target commit, authority fields, and work-unit state machine in §10. V1 and legacy-v1 subjects retain their existing acceptance contract.

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
| Canonical trader/day content is supplied | Daily runbook Section 4, trade-record repository validator, atomic admin content/DB projection path, and future authorized run | Validate before an authorized commit; absence of supplied content creates no synthetic trade or context. |
| Anomaly proves no system defect | human diagnosis evidence | Return only to the last safe Data Update state for a bounded retry. |
| Anomaly requires a system change | Coding Mode hard-routing contract plus human diagnosis evidence | Stop Data Update Mode and route the change; the data request grants no code authority. |
| Routine update edits code, weakens a gate, uses date-loss override, or fabricates data | contract inspection plus human diff/command evidence | Stop; none is allowed as a completion shortcut. |
| Routine existing-system update has no Exec Plan | peer-mode/routing contract inspection | Allowed when all existing gates work and no system change is needed. |
| Daily triggers, runbook sequence, adapters/rebuild, and Pages publisher remain compatible | baseline-to-HEAD exact diff/hash inspection of `AGENTS.md`, `docs/daily-publish-runbook.md`, both fetch adapters, `rebuild_live_extended_db.py`, and `.github/workflows/publish-static-reviews.yml`; named behavior tests where available | Compatibility evidence only; the focused lifecycle checker does not parse these unconstrained sources and this is not a hosted publish test. |
| Commit/push/Pages/hosted sequence succeeds | future authorized run | No offline fixture, implementation phase, or green local check can satisfy this row. |

Current evidence boundaries are explicit: IB readiness and quality still depend on runbook/human evidence, and each newly requested date needs its own real pair/provider, assemble, and local-acceptance receipt. Offline fixtures or prior platform receipts cannot satisfy that future Data Update run.

## 9. Durable Checkpoint Contract

A durable checkpoint is a manually executed, exact-path local Git commit for one completed lifecycle work product. The checker is read-only. It never stages, unstages, commits, amends, resets, stashes, switches branches, pushes, or modifies lifecycle files. Underlying work authority, lifecycle-transition authority, durable-checkpoint local Git authority, and remote/publication authority are independent; none implies another.

### Authority and actor

One authorized human or coding agent is the commit actor. A checkpoint permits one scoped `git add -- <literal files>` plus one normal `git commit` attempt after the work product is complete. It grants no lifecycle transition, push, PR, merge, Pages, provider/broker, hosted-verification, branch, or remote-settings authority. Design approval is not activation; activation is not implementation start; implementation-review `revise` is not remediation authority; `accept` is not Completed migration authority.

`Tang-Authority` has exactly this form:

```text
user-instruction:<token>
```

The token matches `^[a-z0-9][a-z0-9._/-]{0,127}$`. Standing authority is valid only when the user explicitly names the subject and allowed checkpoint kinds. One-shot authority is consumed by one successful matching checkpoint. Standing authority ends when revoked or when the subject reaches Completed, Archived, Rejected, Terminated, or Superseded. A failed commit may be retried only after a fresh full preflight while authority remains unconsumed.

### Checkpoint catalog and scope

Every changed member of the minimum reconciliation set is staged. Only explicitly enumerated files in the allowed optional set may be added. Directory tokens below are documentation shorthand; requests expand them to literal files and never pass a directory or glob to Git.

| Kind | Outcome | Trigger | Minimum reconciliation set | Allowed optional staged set |
| --- | --- | --- | --- | --- |
| `opt-record` | `complete` | Formal OPT record generated | OPT record and optimization index | Explicit sibling screenshots; state files when resume truth changes |
| `plan-proposal` | `complete` | A request/OPT becomes Proposed | Proposed plan, proposed/reviews indexes, roadmap, promoted OPT record/index | State files and explicit proposal evidence |
| `design-review` | `approve`, `revise`, or `reject` | Independent design review finalized | Review, plan metadata, proposed/reviews indexes | Roadmap/state files and explicit review evidence |
| `proposal-revision` | `complete` | Stable revision folds back review | Revised plan, proposed/reviews indexes, roadmap | Source OPT/state files and explicit revision evidence |
| `activation-recording` | `complete` | Explicit Proposed to Active transition | Plan delete/create pair, proposed/active/reviews indexes, roadmap, state files | Explicit activation evidence |
| `implementation-start` | `complete` | Separate start instruction recorded | Active plan/index, roadmap, state files, baseline evidence | Explicit Phase 0 fixtures/evidence |
| `phase-exit` | `complete` | One primary `phase-N` exit passes | Active plan/index, roadmap, state files, phase evidence and frozen deliverables | Phase-manifest fixtures/evidence |
| `phase-blocked` | `blocked` | Primary/remediation work is formally blocked | Active plan/index, state files, blocker/recovery evidence | Roadmap and explicit diagnostics |
| `implementation-review` | `accept`, `revise`, or `reject` | Independent implementation review finalized | Review, plan metadata, active/reviews indexes, state files | Review packet/evidence and roadmap |
| `remediation-complete` | `complete` | One `remediation-N` exit passes | Active plan/index, roadmap, state files, remediation evidence/deliverables | Remediation-manifest fixtures/evidence |
| `completed-migration` | `complete` | Accepted implementation moves Active to Completed | Plan delete/create pair, active/completed/reviews indexes, roadmap, state files | Final closeout evidence and accepted review packet |

Renames list delete and create paths separately. Byte-identical reconciled files are recorded as inspected and are not forced into the commit. A changed required surface omitted from staging or any staged path outside the required/allowed scope fails closed.

The following never qualify: mid-phase work; transient test failure; active retry/diagnostic state; draft OPT/plan/review; a state-file-only edit without a completed product; generated/runtime/cache output; and unclear or piggybacked scope ownership.

### Request, baseline, and exact staging

`checkpoint-request-v1` is a JSON object with exactly `schema_version`, `kind`, `subject`, `revision`, `work_unit`, `outcome`, `authority`, `expected_branch`, `baseline_head`, and `paths`. `paths` is lexically sorted and duplicate-free; each object has exactly `path`, `operation`, `baseline_blob`, and `post_sha256`. Operations are `create`, `modify`, or `delete`; creates use `baseline_blob: null`, deletes use `post_sha256: null`, other Git blobs are lowercase 40-hex and SHA-256 values lowercase 64-hex. Paths use repository-relative `/` separators and may not be absolute, contain `..`, name `.git`, use pathspec magic/globs, or name a directory.

The actor follows one procedure:

1. With an empty index, run baseline preflight before work. Every modify/delete path is clean and every create path absent. `post_sha256` is initially null. The JSON receipt is kept outside the repository.
2. Complete separately authorized work, preserving immutable request metadata/baseline fields, and fill complete post-image hashes.
3. Stage every request path literally with `git add -- <file>...`; never use `.`, `-A`, `--all`, a directory, glob, `-p`, hunk splitting, `commit -a`, or GUI implicit staging.
4. Run staged preflight, then one normal commit with hooks enabled and all required trailers.
5. Run postflight against the new commit. Failure stops lifecycle progression and never triggers automatic amend/reset/retry.

At entry, a requested existing path must be clean in index and worktree and a create path absent. `baseline_blob` must equal `git rev-parse <baseline_head>:<path>`. Staged operation and full post-image must match the request. There is no pre-dirty override or partial-file adoption. Unrelated dirty paths may remain only when their status and content/absence tuples are unchanged from baseline through postflight.

Baseline/staged/postflight abort on a non-empty pre-checkpoint index, detached HEAD, merge, rebase, cherry-pick, branch mismatch, or HEAD drift. `git commit --amend`, reset, stash, checkout/switch, rebase, merge, cherry-pick, push, and `--no-verify` are prohibited. If commit fails, the actor reports it, unstages only literal checkpoint paths with `git restore --staged -- <files>`, verifies an empty index, records no formed checkpoint, and stops.

### Staged safety gates

`git diff --cached --check` must pass. The staged path set must exactly equal the request. Generated paths `frontend/dist/`, `frontend/public/reviews/`, `node_modules/`, `__pycache__/`, and `*.pyc` are denied.

UTF-8 governance text/source is limited to 1,048,576 bytes per file. For `opt-record` and `plan-proposal` only, PNG/JPG/JPEG/WebP files under the subject OPT's `screenshots/` are limited to 5,242,880 bytes each. Other binary files are denied. The total request is limited to 26,214,400 bytes. The repository fixture at `docs/optimization/2026-07-19-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png` is an allowed 1,688,940-byte OPT screenshot with SHA-256 `57c34ea70bf7c6cab2c983b8feaedb6ad9be6f23fc02262ac7c97a48b156d3c5`.

Denied credential paths are basename `.env`; basename beginning `.env.` except `.env.example`; extensions `.key`, `.pem`, `.p12`, `.pfx`; any path under `.ssh/`; and basenames `credentials.json`, `secrets.json`, or `secrets.yaml`. Added text lines reject PEM private-key headers and non-placeholder assignments to case-insensitive `api_key`, `access_token`, `client_secret`, `password`, or `private_key`. Exact values consisting only of `${...}`, `<...>`, `example`, `placeholder`, or `redacted` are placeholders. A harmless filename containing `token` and governance prose such as `gate-token` are not secrets.

### Commit evidence and self-reference

Every v2 durable checkpoint commit contains exactly one of each trailer:

```text
Tang-Checkpoint: <checkpoint-kind>
Tang-Subject: <plan-or-opt-slug>
Tang-Revision: <revision-or-none>
Tang-Work-Unit: <phase-N|remediation-N|none>
Tang-Outcome: <complete|blocked|approve|revise|accept|reject>
Tang-Authority: <user-instruction:token>
Tang-Remote-Authority: none
```

The commit object and trailers are the current checkpoint evidence. A later review names its prior checkpoint SHA in `Review target commit`. Completed migration is found by its trailer, so no file embeds the SHA of the commit containing that file. V1 plans remain frozen and may retain their historical reconciliation-SHA pattern.

Staged preflight and postflight are hard gates. Repository audit with `--legacy-tolerated` warns and exits zero for trailer-less history before a subject opts into v2, but fails for any partial, malformed, or duplicate `Tang-*` set; invalid one-shot/standing authority use; or a missing/mismatched latest checkpoint claimed by a v2 subject's `Expected checkpoint kind`. Historical completeness is not inferred from arbitrary commits.

The read-only carriers are:

```text
python3 scripts/check-durable-checkpoint.py --root . --mode preflight --step baseline --request <request.json>
python3 scripts/check-durable-checkpoint.py --root . --mode preflight --step staged --request <request.json> --baseline-receipt <receipt.json>
python3 scripts/check-durable-checkpoint.py --root . --mode postflight --request <request.json> --baseline-receipt <receipt.json> --commit HEAD
python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated
```

## 10. operating-modes-v2 Schema And Work-Unit State Machine

V2 is a literal strict key superset of the live v1 plan format. Schema selection is exact from `Lifecycle schema`; no key alias or hyphenated replacement is accepted. Every v2 plan uses these constrained keys in this order:

```text
- Lifecycle schema: `operating-modes-v2`
- Status: Proposed|Active|Completed
- Plan slug: `<unique-slug>`
- Revision: `<stable-revision-id>`
- Plan author ID: `<non-empty-id>`
- Design reviews: none|`<review-path>@<approve|revise|reject>@<target-revision>`[, ...]
- Latest design verdict: none|approve|revise|reject
- Review independence: none|legacy-unattested|attested
- Activation evidence: none|`user-instruction:<token>`
- Current phase: none|phase-0|phase-1|phase-2|phase-3|phase-4|phase-5|phase-6
- Phase state: none|not-started|in-progress|blocked|complete
- Phase entry gate: none|`<gate-token>`
- Next gate: `<gate-token>`
- Implementation review: none|`<accepted-review-path>@accept`
- Final disposition: none|Completed|Terminated|Rejected|Superseded|Archived
- Verified implementation commit: none|`<40-hex-commit>`
- Lifecycle reconciliation commit: none
- Implementation start evidence: none|`user-instruction:<token>`
- Current work unit: none|phase-0|phase-1|phase-2|phase-3|phase-4|phase-5|phase-6|remediation-1|remediation-2|...
- Work state: none|not-started|in-progress|blocked|complete
- Blocker evidence: none|`<repository-relative-evidence-path>`
- Implementation reviews: none|`<review-path>@<accept|revise|reject>@<40-hex-target-commit>`[, ...]
- Latest implementation verdict: none|accept|revise|reject
- Checkpoint authority: none|`user-instruction:<token>`
- Checkpoint authority mode: none|one-shot|standing
- Checkpoint authority kinds: none|`<ordered-kind-list>`
- Expected checkpoint kind: none|opt-record|plan-proposal|design-review|proposal-revision|activation-recording|implementation-start|phase-exit|phase-blocked|implementation-review|remediation-complete|completed-migration
```

`Implementation review` remains the v1 compatibility pointer. It is `none` through revise/reject rounds and becomes the final accepted review path plus `@accept` only when the latest verdict is `accept`. `Implementation reviews` records every round and target commit. `Verified implementation commit` equals the accepted review target. `Lifecycle reconciliation commit` is always `none`; the completed-migration trailer is non-circular evidence.

A v2 review retains the nine v1 review keys in their exact order and appends exactly one final constrained key:

```text
- Review target commit: `<40-hex-commit>`
```

Design reviews target the preceding `plan-proposal` or `proposal-revision` checkpoint. Implementation reviews target the preceding `phase-exit` or `remediation-complete` checkpoint. The target is an ancestor of the review checkpoint and must carry matching subject, revision, and kind trailers.

### Primary and remediation state

`Current phase` and `Phase state` remain authoritative for active-index and state-block derivation. `Current work unit` and `Work state` describe the executable unit; remediation may run while primary phase remains `phase-6`.

| Lifecycle point | Current phase / Phase state | Current work unit / Work state | Evidence and next gate |
| --- | --- | --- | --- |
| Proposed | `none / none` | `none / none` | implementation-start, blocker, and implementation-review fields are `none`; Proposed gate prefixes remain unchanged |
| Activated, not started | `phase-0 / not-started` | `none / none` | implementation start `none`; `phase-0-start` |
| Primary phase ready | `phase-N / not-started` | `none / none` | implementation start present; `phase-N-start` |
| Primary phase running | `phase-N / in-progress` | `phase-N / in-progress` | blocker `none`; `phase-N-exit` |
| Primary phase blocked | `phase-N / blocked` | `phase-N / blocked` | blocker present; `phase-N-recovery` |
| Prior exit recorded, next phase ready | `phase-(N+1) / not-started` | `none / none` | expected checkpoint `phase-exit`; `phase-(N+1)-start` |
| Awaiting implementation review | `phase-6 / complete` | `none / none` | blocker `none`; `implementation-review` |
| Review revise, remediation ready | `phase-6 / in-progress` | `remediation-N / not-started` | latest verdict `revise`; `remediation-N-start` |
| Remediation running or blocked | `phase-6 / in-progress|blocked` | `remediation-N / in-progress|blocked` | blocked requires evidence; `remediation-N-exit|remediation-N-recovery` |
| Remediation complete, awaiting review | `phase-6 / in-progress` | `remediation-N / complete` | expected checkpoint `remediation-complete`; `implementation-review` |
| Accepted, awaiting closeout | `phase-6 / complete` | `none / none` | latest verdict `accept`; `completed-migration` |

`phase-exit` applies only to a primary `phase-N`; `remediation-complete` only to a `remediation-N`. Remediation numbers begin at 1 and increment without gaps after each structured `revise`. `Blocker evidence` is non-`none` if and only if either authoritative state is blocked. State blocks and fixed active-index rows remain v1-shaped and derive only from primary phase fields.

`Phase entry gate` stays fixed for its admitted unit: activation uses `activation:user-instruction:<token>`; Phase 0 start uses the implementation-start reference; later primary phases use `phase-(N-1)-exit`; remediation uses `remediation-N:user-instruction:<token>` after the immediately preceding structured `revise`. A verdict alone never creates remediation authority.

### Compatibility and migration

- V1 and legacy-v1 subjects remain valid under their existing exact formats.
- V1 Completed plans are frozen; no review metadata or checkpoint history is backfilled.
- A Proposed v1 plan may migrate at its next revision or activation. An Active v1 plan may migrate at its next phase transition.
- Migration retains every v1 key, adds every v2 key, derives state from the table above, and defaults authority fields to `none` unless a matching explicit user instruction exists.
- The Durable Checkpoint governance plan that introduces this contract remains v1 for its entire proposal, review, activation, phase, implementation-review, and closeout lifecycle. The new rules are not applied retroactively to bootstrap themselves.
