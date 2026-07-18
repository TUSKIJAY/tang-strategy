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

Every governed plan begins with one Markdown bullet per key using exact `- Key: value` syntax:

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

Additional human fields are allowed. Gate tokens must be non-empty and use only letters, digits, periods, underscores, colons, `@`, `/`, or hyphens.

State invariants:

- Proposed: `Status=Proposed`, no activation/current phase, and a review/revision/activation-recording next gate.
- Active: latest matching-revision design review is `approve`, independence is `attested`, activation is non-none, and phase/phase state/entry gate/next gate are non-none.
- Completed: final disposition is non-none; an implemented plan references an `accept` implementation review. Commit values may be `none` only when no commit was authorized.
- Historical bare review filenames are accepted only for explicitly migrated `operating-modes-legacy-v1` completed plans. New-schema plans use repository-relative review paths.

### Independent review metadata

A qualifying review must be authored from a context that did not draft the reviewed revision, independently inspect repository evidence, and contain:

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

The checker validates structure, target/revision, vocabulary, and unequal author/reviewer IDs. Human review validates identity, independence truth, evidence quality, user instructions, and publication authority.

### Fixed index rows

Each plan link appears exactly once in its state index. The reviews index contains one row per plan with review artifacts and uses the matching lifecycle state.

```text
proposed:  | [Title](./plan.md) | Proposed | [review-N](../reviews/.../review-N.md): verdict | <next-gate-token> |
active:    | [Title](./plan.md) | phase-N:<phase-state> | [evidence](...) | <next-gate-token> |
completed: | [Title](./plan.md) | <Final disposition> | [implementation review](...) | <40-hex-or-none> |
reviews:   | [Title](./review-dir/) | [review-N](...)[, ...] | <latest-verdict> | <Proposed|Active|Completed> |
```

Roadmap lifecycle sections contain only rows shaped as:

```text
- [Title](./<state>/<plan>.md) — <Proposed|Active|Completed>; canonical details: [<state> index](./<state>/index.md)
```

The checker compares exact plan-link/state sets, not prose summaries.

### Current-state blocks

`PROGRESS.md` and `HANDOFF.md` each contain exactly one matching block:

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

Machine fixtures cover plan discovery/uniqueness, metadata/state invariants, exact index/roadmap sets, review structure and revision matching, current-state blocks, historical Git markers, required paths/routing, read-only behavior, external-root composition, and governed/minimal profile separation. Contract inspection covers routing, Data Update ordering, unchanged daily trigger/runbook/publisher boundaries, and migration text. Existing backend tests remain the carrier for actual calendar, TV quality, rebuild, non-shrink, DB, and assemble behavior. Human evidence remains required for identity, authority, command order, optional checks, bounded-maintenance classification, and anomaly return decisions. Real commit/push/Pages/hosted proof is deferred to a separately authorized daily run.

No fixture or offline inspection may claim a real provider fetch, broker connection, tracked-DB update, push, Pages publication, or hosted verification passed.
