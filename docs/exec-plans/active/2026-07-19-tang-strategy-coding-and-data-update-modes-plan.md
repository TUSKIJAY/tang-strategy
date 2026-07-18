# Tang Strategy Coding And Data Update Modes

- Lifecycle schema: `operating-modes-v1`
- Status: Active
- Plan slug: `2026-07-19-tang-strategy-coding-and-data-update-modes-plan`
- Revision: `v2-review-foldback-2026-07-19`
- Plan author ID: `codex-plan-author-2026-07-19`
- Owner: Codex
- Created: 2026-07-19
- Design reviews: `review-001.md@revise@v1-initial`, `review-002.md@revise@v1-initial`, `review-003.md@approve@v2-review-foldback-2026-07-19`
- Review status: v1 reviews revise; v2 matching-revision design review `review-003` returned approve; user activation instruction recorded
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-19-move-proposed-plan-to-active`
- Current phase: phase-0
- Phase state: not-started
- Phase entry gate: `explicit-start-or-execute-instruction`
- Next gate: phase-0-start
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Implementation authority: not started; a separate explicit start/execute instruction is required before Phase 0 work
- Scope authority: active lifecycle only; work remains limited to the recorded phase and its unopened entry gate
- Standing local commit authority: `user-instruction:2026-07-19-commit-at-lifecycle-or-phase-boundary`
- Local Git boundary: after a lifecycle transition or Phase exit passes its required verification and state/handoff reconciliation, stage only that boundary's plan-scoped files and create exactly one local conventional commit
- Remote boundary: no push, pull request, merge, Pages publish, branch-protection change, environment approval, or other remote mutation

## 1. Context, Review Foldback, And Reproducible Evidence

Tang Strategy has a complete governed harness surface, a TV-first daily-publish contract, candidate-first rebuild safety, and explicit proposed/review/active/completed directories. It still lacks a repository-owned execution layer that routes requests into two peer operating modes and checks lifecycle truth deterministically.

The original proposal's architectural backbone remains valid after `review-001` and `review-002`: peer modes, one authoritative contract with short routers, no second state store, dynamic Git truth separated from durable evidence, and local-update authority separated from publication authority.

This revision folds back both `revise` verdicts. In particular it now:

- defines the constrained format package that the future checker may parse;
- removes the transition helper from this implementation scope instead of designing a tool that necessarily leaves status surfaces inconsistent;
- defines a minimal reviewer-independence contract and its machine/human verification boundary;
- assigns a verification carrier to every required test case;
- expands the exact file manifest, including the authority map, all four indexes, one new decision, and legacy completed-plan metadata reconciliation;
- separates Coding Mode routing lanes from proposal-lane lifecycle stages;
- makes proposed-plan routing a hard rule for named risks instead of an undefined preference/exception;
- separates user activation instruction, lifecycle activation recording, and implementation start;
- acknowledges that the current TV/IB fetch scripts import into the tracked runtime DB before the canonical rebuild;
- distinguishes mandatory local DB/API acceptance from the runbook's optional static export/build;
- changes the next gate to renewed review of revision `v2-review-foldback-2026-07-19`.

The baseline drift evidence is anchored to committed content, not the already-reconciled working-tree copies:

- `git show 2454ccb7fc1c927f2a52a3bd2db7debe41998594:PROGRESS.md` shows the already committed acceptance work described as unstaged/uncommitted;
- `git show 2454ccb7fc1c927f2a52a3bd2db7debe41998594:HANDOFF.md` shows `a70be643...` as Branch/HEAD plus the stale unstaged/uncommitted claim;
- `git show 2454ccb7fc1c927f2a52a3bd2db7debe41998594:docs/exec-plans/roadmap.md` summarizes the completed recovery plan as having no commit;
- `git show --stat a70be643a968cc24215fe508e69b3e0496d3c34a` and `git show --stat 2454ccb7fc1c927f2a52a3bd2db7debe41998594` identify the implementation and acceptance/lifecycle-reconciliation commits;
- `python3 scripts/check-project-harness.py --root . --profile governed` passed with `errors=[]` while those committed lifecycle claims were stale;
- the current 277-line checker has no Git invocation, lifecycle discovery, metadata parser, directory uniqueness check, or state-surface reconciliation;
- the governed read-only audit found all 21 expected artifacts present, and the startup-document budget passed.

Structural PASS therefore proves the harness surface exists; it does not prove that lifecycle state or authority is truthful.

## 2. Objective, Scope, And Exact Future File Manifest

### 2.1 Objective

Establish two peer top-level repository operating modes:

1. **Coding Mode** changes the system under risk-based lanes and governed lifecycle gates.
2. **Data Update Mode** uses the existing system to update market data under a Local Update Gate and a separate Publish Gate.

The contract must be restartable and inspectable from repository evidence without depending on Codex-private state or remembered chat history.

### 2.2 Future implementation file manifest

Phase 0 must revalidate this manifest. Implementation outside it requires a plan revision and renewed design review.

Add:

- `docs/operating-modes.md` — single normative mode, lifecycle-format, reviewer, and authority contract;
- `docs/decisions/2026-07-19-operating-modes-and-lifecycle-source.md` — durable decision for the new authority layer; its status must reflect the explicit user decision and does not itself authorize implementation;
- `scripts/check-operating-modes.py` — focused, read-only, dependency-free-Python checker;
- `scripts/tests/test_operating_modes.py` — stdlib fixture-repository tests constructed under temporary directories.

Modify:

- `AGENTS.md` — compact router/link only; retain existing daily-publish triggers and hard rules;
- `INSTRUCTIONS.md` — stable mode/source/verification facts only;
- `docs/README.md` — route `docs/operating-modes.md` and the new decision from the authority map;
- `docs/decisions/index.md` — index the new decision;
- `docs/exec-plans/plan-template.md` — own all plan metadata fields defined in Phase 1;
- `docs/exec-plans/reviews/review-template.md` — own reviewer identity, target revision, independence declaration, evidence method, and verdict fields;
- `docs/exec-plans/proposed/index.md`;
- `docs/exec-plans/active/index.md`;
- `docs/exec-plans/completed/index.md`;
- `docs/exec-plans/reviews/index.md`;
- `docs/exec-plans/roadmap.md` — use constrained plan-list rows rather than free-form lifecycle facts;
- `docs/exec-plans/completed/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md` — metadata-only reconciliation for slug, final disposition, durable commits, and an unambiguous implementation-review path; historical narrative remains unchanged;
- this plan when its lifecycle state/phase/reviews change;
- `PROGRESS.md` and `HANDOFF.md` — add/update only the constrained current-state blocks and bounded human context;
- `scripts/check-project-harness.py` — compose the focused checker only under the governed profile;
- `.harness/config.json` — add the stdlib fixture-test command while retaining the canonical harness entry;
- `.github/workflows/project-harness.yml` — run the canonical checker and fixture tests without changing existing job display names.

Read-only compatibility references, not implementation targets:

- `docs/daily-publish-runbook.md`;
- `.github/workflows/publish-static-reviews.yml`;
- TV/IB fetch, rebuild, import, DB, backend, frontend, strategy, content, and data paths.

This plan does not edit the daily runbook. If implementation discovers a mismatch that requires changing the runbook, runtime, DB, provider, or Pages publisher, stop and revise the plan before touching it.

### 2.3 Non-goals for this proposal revision

- no Coding Mode or Data Update Mode implementation;
- no checker, tests, decision, template, helper, workflow, runtime, fetch, rebuild, DB, provider, or publisher change;
- no new review artifact in this revision turn;
- no activation or move to `active/`;
- no stage, commit, push, PR, merge, Pages publish, broker connection, or remote setting;
- no requirement that routine daily data updates create an Exec Plan;
- no generic workflow engine or second lifecycle state store;
- no rewrite of historical plan/review narrative.

## 3. Canonical Sources And Constrained Format Package

Phase 1 must deliver this named **Constrained Format Package** before checker implementation. The checker may parse only the formats below; it must not infer lifecycle truth from unconstrained prose.

### 3.1 Documentation ownership

- `docs/operating-modes.md`: single normative contract for routing, authority dimensions, lifecycle transitions, reviewer independence, Data Update states, and escalation.
- `AGENTS.md`: short entry/router and existing hard operational triggers/rules.
- `INSTRUCTIONS.md`: stable project facts and verification commands.
- one plan file in exactly one of `proposed/`, `active/`, or `completed/`: canonical lifecycle state.
- review artifacts under `reviews/<plan-slug>/`: review evidence.
- four indexes, Exec Plan roadmap, `PROGRESS.md`, and `HANDOFF.md`: derived surfaces validated against canonical plan/review evidence.
- `.harness/config.json`: verification configuration only, never lifecycle state.

### 3.2 Plan metadata schema

Every governed plan must start with one Markdown bullet per key using exact `- Key: value` syntax. `operating-modes-v1` defines these keys:

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

Additional human-readable fields such as owner, dates, scope, and remote boundary are allowed but do not replace the constrained keys.

Directory rules:

- Proposed: `Status=Proposed`; no activation; no current phase; next gate is revision/review/activation recording as applicable.
- Active: `Status=Active`; latest matching-revision design review is `approve`; independence is attested; activation evidence is non-none; current phase, phase state, entry gate, and next gate are non-none.
- Completed: `Status=Completed`; final disposition is non-none; implemented plans require `Implementation review@accept`; durable commit values may be `none` when no commit was authorized, but the field must exist.

The checker accepts historical bare review filenames only for explicitly migrated `operating-modes-legacy-v1` completed plans and resolves them under `reviews/<plan-slug>/`. The preferred migration for the existing completed plan is to add an unambiguous relative path in its metadata without changing historical prose.

### 3.3 Index and roadmap row templates

The four indexes retain their purpose-specific columns, but rows must use fixed lifecycle values and parseable Markdown links:

```text
proposed: | [Title](./plan.md) | Proposed | [review-N](../reviews/.../review-N.md): verdict | <next-gate-token> |
active:   | [Title](./plan.md) | phase-N:<phase-state> | [evidence](...) | <next-gate-token> |
completed:| [Title](./plan.md) | <Final disposition> | [implementation review](...) | <40-hex-or-none> |
reviews:  | [Title](./review-dir/) | [review-N](...)[, ...] | <latest-verdict> | <Proposed|Active|Completed> |
```

Each plan file must appear exactly once in its state index. The reviews index contains one row per plan that has review artifacts and its lifecycle state must match the plan directory.

The roadmap must stop duplicating free-form review, gate, and commit facts. Each lifecycle section uses only:

```text
- [Title](./<state>/<plan>.md) — <Proposed|Active|Completed>; canonical details: [<state> index](./<state>/index.md)
```

The checker compares plan-link sets and state tokens between directories, indexes, reviews index, and roadmap; it does not compare prose summaries.

### 3.4 PROGRESS/HANDOFF current-state blocks and Git evidence

Both `PROGRESS.md` and `HANDOFF.md` contain exactly one machine-readable block:

```text
<!-- operating-modes-state:start -->
- Current plan: `<plan-slug-or-none>`
- Lifecycle status: `Proposed|Active|Completed|None`
- Current phase: `none|phase-N`
- Phase state: `none|not-started|in-progress|blocked|complete`
- Next gate: `<gate-token>`
<!-- operating-modes-state:end -->
```

The two blocks must match canonical plan metadata. Human prose outside the block is not interpreted as lifecycle state.

Live Git truth must never be placed in the constrained state block. In `PROGRESS.md` and `HANDOFF.md`, these legacy structured keys are forbidden outside a historical-evidence block: `Branch/HEAD`, `Current HEAD`, `Git state`, `Current worktree`, and `Worktree status`.

Historical Git evidence uses explicit markers:

```text
<!-- git-evidence:historical:start -->
- Verified at: `<timestamp-or-date>`
- Verified commit: `<40-hex>`
- Observation: `<historical statement>`
<!-- git-evidence:historical:end -->
```

The checker ignores free prose and historical plan bodies; it only parses plan metadata, constrained state blocks, fixed index/roadmap rows, and the named legacy structured keys in `PROGRESS.md`/`HANDOFF.md`. A clean-worktree fixture containing `- Git state: unstaged/uncommitted diff` outside the historical block must fail. Ambiguous prose remains a human-review responsibility; the checker must not use keyword sentiment to guess whether prose is current or historical.

### 3.5 Minimal reviewer-independence contract

This contract applies immediately to the renewed review of revision `v2-review-foldback-2026-07-19` and will later live in `docs/operating-modes.md` plus `review-template.md`.

A qualifying independent review must:

- be authored by a reviewer ID different from the plan author ID and from an execution context that did not draft the reviewed revision;
- identify the exact plan path and exact `Revision` value;
- independently inspect repository evidence rather than only summarize the plan;
- record findings, verdict, confidence, and unverified items;
- include these constrained fields:

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

The checker can verify field presence, target revision, accepted verdict vocabulary, and that reviewer/author IDs differ. It cannot prove that the identity or declaration is truthful, nor can it prove that a user actually issued an activation/publish instruction. A human reviewer must validate those attestations and evidence references. Existing `review-001`/`review-002` remain valid `revise` feedback but are `legacy-unattested` and cannot satisfy the future activation gate.

## 4. Top-Level Routing And Least-Authority Rules

The modes are peers. Data Update Mode is not a Coding Mode phase.

Every request is evaluated independently across authority dimensions:

- inspection/mutation: read-only, bounded local change, or planned system change;
- lifecycle: none, proposal, review, activation recording, or named active phase;
- Git: no stage, stage, commit, push, PR, or merge;
- publication: none, local acceptance, or Pages publication;
- broker/provider: no connection, read/fetch prerequisite, or separately governed action;
- remote administration: none or an explicitly named setting change.

Ambiguity grants no additional authority in any dimension. Git, publication, broker, and remote-setting authority never follow merely from local mutation or lifecycle authority.

| Request intent | Route | Default authority |
| --- | --- | --- |
| Inspect, explain, diagnose, or verify | Coding Mode read-only lane | read-only only |
| Small change that meets every bounded-maintenance criterion in Section 5.1 | Coding Mode bounded-maintenance lane | named local change only |
| Any hard proposal criterion in Section 5.3 is true or cannot yet be ruled out | Coding Mode proposal lane | proposal/review only |
| Use existing fetch/rebuild/acceptance tooling for routine market data | Data Update Mode | Local Update Gate only |
| Existing daily-publish trigger or equivalent explicit publish instruction | Data Update Mode | pending Publish Gate authority; local gates still run first |
| Any data anomaly | Coding Mode read-only diagnosis first | diagnose only; then return to Data Update or route to Coding change lane from evidence |

## 5. Coding Mode

### 5.1 Routing lanes

**Lane 1 — Read-only inspection**

- inspect code, Git, docs, tests, logs, configuration, and data evidence;
- diagnose and report; do not implement without separate change authority;
- all ambiguous work and all data anomalies start here.

**Lane 2 — Bounded direct maintenance**

Lane 2 is allowed only when all of these are true:

- one clearly named outcome and a bounded file surface are known before editing;
- no criterion in Section 5.3 applies;
- the change is locally reversible without data migration or destructive cleanup;
- no security, authorization, market-data, DB, publication, or cross-module contract changes;
- proportionate local verification exists;
- the routing reason is reported in the final handoff, but no Exec Plan artifact is required.

Lane 2 does not require independent design or implementation review. It still requires unrelated-change protection and separate Git/remote authority.

**Lane 3 — Proposed Exec Plan**

- create/update a plan only in `proposed/`;
- synchronize the proposed, reviews, roadmap, `PROGRESS.md`, and `HANDOFF.md` surfaces as applicable;
- grant design-review authority only;
- do not implement until a matching-revision approve review, user activation instruction, lifecycle activation recording, and separate implementation-start gate all exist.

### 5.2 Proposal-lane lifecycle stages

1. **Proposal drafting/revision** — author the exact revision and constrained metadata.
2. **Independent design review** — review the exact revision under Section 3.5; `approve` is not activation.
3. **User activation instruction** — explicit instruction for the exact approved revision; this is external authority evidence, not the file move itself.
4. **Activation lifecycle recording** — a lifecycle-only change moves the plan to `active/`, records the user reference, sets `Current phase=phase-0`, `Phase state=not-started`, and `Next gate=phase-0-start`; it performs no implementation.
5. **Implementation start and phased work** — require a separate explicit start/execute instruction plus the active phase entry gate; work remains bounded by the phase.
6. **Independent implementation review** — checks implemented diff, evidence, scope, and residual risks.
7. **Closeout/completed** — records final disposition and reconciles all derived surfaces after required review/verification.

Completing a stage does not grant the next one. Bounded maintenance in Lane 2 does not inherit proposal-lane review/closeout requirements.

### 5.3 Hard proposal-routing criteria

If any item is true, the work must use Lane 3; there is no undocumented “equally strict” exception:

- database schema/migration, rebuild/import semantics, promotion/rollback, or tracked-DB safety;
- market-data quality/session/source/provenance/non-shrink contracts;
- Pages export/publish workflow or daily-publish authorization behavior;
- authentication, secrets, authorization, security, or provider credentials;
- cross-backend/frontend/data contract changes;
- multi-phase, destructive, difficult-to-rollback, or broadly scoped changes;
- lifecycle checker, constrained formats, transitions, or governance-policy changes.

If classification is uncertain, remain in Lane 1 until evidence resolves it. A future exception must itself be a separately accepted decision record referenced by the plan/checker; this plan creates no such exception.

## 6. Data Update Mode

### 6.1 State sequence and current runtime fact

`requested -> date_resolved -> fetched -> quality_passed -> candidate_verified -> local_accepted -> publish_authorized -> committed -> published -> hosted_verified`

These states are an operational protocol, not a second committed state database. Evidence comes from command output, payload/provider metadata, DB checks, Git commits, workflow runs, and hosted verification. A spanning-session handoff records the last verified state in human evidence; it does not become canonical machine state.

The current adapters have an important intermediate mutation: TV and IB fetch scripts import/upsert into the tracked runtime DB by default before the separate canonical rebuild. Candidate-first protection belongs to `rebuild_live_extended_db.py`, not to the default fetch import. This plan does not change that runtime behavior.

State meanings:

- `requested`: ticker/date/scope and pending publish authority are captured;
- `date_resolved`: actual NYSE calendar and current ET establish a completed valid session;
- `fetched`: the selected adapter produced the day payload and, on the current default path, may already have imported it into the tracked DB; this is not yet local acceptance;
- `quality_passed`: TV path passed adapter hard gates; IB fallback passed the runbook's whole-day count/gap/session checks plus downstream validation, because the IB script itself does not enforce TV-equivalent gates;
- `candidate_verified`: canonical candidate-first rebuild, non-shrink, semantic, integrity, foreign-key, drift, and promotion checks pass;
- `local_accepted`: mandatory DB and assemble/API checks pass; optional Tang trade/context data supplied by the user is recorded/validated; optional static export/build/page smoke is run when practical and otherwise recorded as not run without pretending it passed;
- `publish_authorized`: an existing daily trigger or equivalent explicit instruction is recorded and every mandatory local gate has passed;
- `committed`: only explicitly authorized data/trade files are committed;
- `published`: authorized push and Pages workflow complete;
- `hosted_verified`: the expected hosted URL is verified.

If fetch/import succeeds but rebuild or later validation fails, the tracked DB may already contain an unaccepted upsert. Stop, report the exact state and before/after evidence, do not claim the DB is unchanged, and route the anomaly through Coding Mode read-only diagnosis.

### 6.2 Local Update Gate

The Local Update Gate covers `requested` through `local_accepted`:

1. resolve the actual completed NYSE session, including holidays and early closes;
2. verify Git/worktree scope and capture relevant tracked-DB evidence before fetch;
3. use TradingView first without checking/starting/requesting IB Gateway;
4. apply documented TV retries and hard gates;
5. only after exhausted TV retries or a named hard-gate failure, report that gate and request the IB fallback prerequisite;
6. fetch the whole day from one source and never combine TV/IB bars within a market day;
7. for IB, apply the runbook's whole-day/gap/session checks before claiming `quality_passed`;
8. run canonical candidate-first rebuild and reject date/non-market shrink, semantic mismatch, integrity failure, or drift; never use `--allow-date-loss` in routine flow;
9. prove the tracked DB was not reduced because local gitignored seed history is incomplete;
10. require the requested day plus non-empty 1m/5m `/api/reviews/assemble` payload and mandatory DB checks;
11. when Tang supplied SPY 0DTE trades/context, record and validate the existing `content/trader-trades/<date>.json` step before publication;
12. treat local static export/build and browser page smoke as optional-but-recommended compatibility checks, recording executed/not-executed truthfully;
13. stop at `local_accepted` without stage/commit/push/publish unless publish authority exists.

### 6.3 Publish Gate

- only the current AGENTS one-sentence trigger or equivalent explicit publish instruction grants pending publish authority;
- pending authority cannot skip Local Update Gate states;
- local acceptance, a green check, or a changed DB alone never grants publication;
- commit scope remains the tracked DB plus an applicable Tang trade/context JSON and separately authorized files;
- authorized push, Pages workflow observation, and hosted URL verification remain distinct required states;
- failures preserve the last successful state and report the next safe action.

Routine local or published data updates do not require an Exec Plan when the existing system and gates work. This plan preserves current trigger wording and publisher behavior.

### 6.4 Escalation and return loop

Observable escalation conditions include:

- a missing historical day not recoverable through the routine path;
- failed integrity/foreign keys, unexplained before/after DB drift, or rebuild refusal that cannot be explained by known inputs;
- any attempted data repair of prior canonical rows;
- a required schema, quality-contract, source, rebuild, fetch, import, export, or publisher change;
- an attempted use of `--allow-date-loss`, code edit, gate weakening, or fabricated/padded data to complete the run.

Stop Data Update Mode and enter Coding Mode Lane 1. If read-only diagnosis proves the existing system is sound and identifies a transient/environment/input issue, record that evidence and return to the last safe Data Update state for a bounded retry. If a system change is required, route by Sections 5.1/5.3; the original data request grants no code-change authority.

## 7. Lifecycle Execution Layer

### 7.1 Focused checker

Implement `scripts/check-operating-modes.py` with Python stdlib only. Dynamic Git checks may call the installed `git` binary; “dependency-free” means no third-party Python package. `scripts/check-project-harness.py` composes it only for the governed profile and passes the explicit `--root`, including external temporary fixture roots.

The checker must only interpret the Constrained Format Package. It must:

- discover plan files in proposed/active/completed and reject duplicate slug/path or status-directory mismatch;
- compare exact plan-link sets across directories, all four indexes, and roadmap state sections;
- validate required plan metadata and state-specific invariants;
- validate review artifact existence, exact target revision, verdict vocabulary, and reviewer/author ID inequality for new-schema reviews;
- reject Active without matching-revision `approve`, independence attestation, activation evidence, phase, phase state, entry gate, and next gate;
- accept a Proposed plan with matching `approve` but no activation evidence as a legal pre-activation state;
- require implemented Completed plans to reference `accept` implementation review and final disposition;
- compare the exact constrained current-state blocks in `PROGRESS.md`/`HANDOFF.md` with canonical metadata;
- reject named legacy live-Git keys outside historical markers and compare structured fixture claims with dynamic Git status where applicable;
- validate required contract/router/template/config/workflow paths and link routing;
- remain read-only, emit specific JSON/errors, and return nonzero on invalid fixtures.

It cannot prove reviewer identity, independence truth, user speech, operational command order, or publish authorization. Those remain explicit human/evidence checks in Section 9.

### 7.2 Transition-helper decision

No transition helper is included in this plan.

Current lifecycle indexes have different schemas, roadmap entries are free-form, and `PROGRESS.md`/`HANDOFF.md` require human context. A helper that moves a plan before human reconciliation would intentionally create an invalid intermediate state; a helper that rewrites every surface would exceed the user-authorized “file move and consistency check” boundary and approach a workflow engine.

Transitions therefore remain explicit manual lifecycle edits:

1. verify review/activation/final-disposition authority;
2. move exactly one plan between adjacent state directories;
3. update all four indexes, roadmap, and both constrained current-state blocks;
4. run the read-only checker;
5. stop on any error.

A future helper may be proposed only after the v1 formats have stable operational evidence. It requires a separate plan/review and may only move files plus run consistency checks; it may not invent authority or rewrite human status prose.

### 7.3 Harness and CI

- retain `python3 scripts/check-project-harness.py --root . --profile governed` as canonical entry;
- add `python3 -m unittest scripts.tests.test_operating_modes` to `.harness/config.json` and the existing `Harness structure` job;
- configure fixture Git repositories with local `user.name`/`user.email` before fixture commits so CI does not depend on runner identity;
- use temporary fixture repositories only; no network, broker, provider, real tracked DB, or real publication;
- preserve existing GitHub job display names and the Pages publisher workflow;
- treat green checks as evidence, never activation/merge/publication authority.

## 8. Future Implementation Phases

This plan is Active after the matching-revision `approve` and the explicit 2026-07-19 user activation instruction. The lifecycle activation recording is complete. A separate explicit start/execute instruction is still required before Phase 0 implementation.

### Activation lifecycle recording — completed; not an implementation phase

- Entry gate: met by `review-003: approve` for revision v2 and the explicit 2026-07-19 user activation instruction.
- Work: completed; plan moved to `active/`, activation evidence recorded, and `phase-0:not-started` / `next gate=phase-0-start` set.
- Verification: run lifecycle/harness checks after all derived surfaces are reconciled.
- Exit gate: Active plan is valid; no implementation has started.
- State/handoff: activation-only result recorded; wait for implementation-start authority.
- Commit boundary: standing local commit authority applies; after verification and reconciliation, create one scoped local conventional commit for this lifecycle-only batch; do not push.

### Phase 0 — Baseline, manifest, and authority freeze

- Entry gate: valid Active state plus explicit start/execute instruction for this plan; startup scope rechecked.
- Scoped work: capture current lifecycle/data/publish/checker behavior; revalidate the exact manifest and read-only references; freeze authority dimensions.
- Verification: governed checker, startup budget, diff/status, and proof of no runtime/data/provider/publisher mutation.
- Exit gate: manifest and baseline evidence have no unresolved mismatch.
- State/handoff: `phase-0:complete`, next gate `phase-1-start`.
- Commit boundary: after the Phase 0 exit gate passes, create one scoped local conventional commit containing only baseline/lifecycle evidence; do not push.

### Phase 1 — Authority contract, decision, and Constrained Format Package

- Entry gate: Phase 0 complete and Phase 1 entry recorded.
- Scoped work: add `docs/operating-modes.md`; add/index the decision; update `docs/README.md`; freeze Sections 3.2–3.5 formats; update plan/review templates; standardize four indexes/roadmap rows; add constrained blocks to `PROGRESS.md`/`HANDOFF.md`; prepare the Section 9 fixture manifest.
- Verification: format examples parse deterministically; current and historical samples have explicit migration treatment; reviewer contract and authority dimensions are cross-checked; Section 9 has one carrier per row.
- Exit gate: no checker requirement depends on ambiguous prose; fixture expectations are the design-reviewed Section 9 matrix and the executor records a self-attestation that every row has an implementable carrier.
- State/handoff: record format version, migration decisions, fixture-carrier attestation, and next gate.
- Commit boundary: after the Phase 1 exit gate passes, create one scoped local conventional commit containing only the authority/format/template/index contract slice; do not push.

### Phase 2 — Legacy metadata migration, Coding router, and checker

- Entry gate: Phase 1 format package and carrier attestation complete.
- Scoped work: reconcile the existing completed plan metadata only; migrate this plan/current surfaces; add compact AGENTS/INSTRUCTIONS routing; implement focused checker and Coding lifecycle fixtures; do not add a transition helper.
- Verification: all lifecycle/Coding rows in Section 9; valid existing completed plan and current plan fixtures pass; checker is read-only and governed-only composition works for external `--root` fixtures.
- Exit gate: invalid lifecycle states fail specifically and valid migrated repository state passes.
- State/handoff: record migration evidence and exact negative cases.
- Commit boundary: after the Phase 2 exit gate passes, create one scoped local conventional commit containing only legacy metadata/router/checker/Coding fixtures; do not push.

### Phase 3 — Data Update contract and evidence mapping

- Entry gate: Coding lifecycle checker passes current repository and fixtures.
- Scoped work: finalize Data Update states/gates/escalation in `docs/operating-modes.md`; add only contract/fixture evidence that does not pretend to execute provider/DB/publish behavior; leave the runbook/runtime read-only.
- Verification: every Data Update row in Section 9 uses its declared carrier; compare current trigger/runbook/publisher text and existing backend test evidence; record runtime-only items as deferred real-run evidence.
- Exit gate: local success cannot be interpreted as publish authority, runtime gaps are explicit, and no offline fixture claims a real publish pass.
- State/handoff: record compatibility result and any separately proposed runtime gaps.
- Commit boundary: after the Phase 3 exit gate passes, create one scoped local conventional commit containing only the Data Update contract/evidence tests; do not push.

### Phase 4 — Harness and CI integration

- Entry gate: checker and fixture suite pass locally.
- Scoped work: compose governed checker, update config/workflow commands, keep job names, and finalize state-block reconciliation. Templates are not edited in this phase.
- Verification: configured commands/order, governed/minimal profiles, external fixture roots, startup budget, Markdown links, no Pages workflow diff.
- Exit gate: local and PR harness paths enforce the same contract without network/broker/real DB.
- State/handoff: record integration evidence and next gate.
- Commit boundary: after the Phase 4 exit gate passes, create one scoped local conventional commit containing only harness/config/CI integration; do not push.

### Phase 5 — Full negative matrix and compatibility closeout

- Entry gate: integrated positive fixture and current repository pass.
- Scoped work: complete Section 9 negative tests, error specificity, migration compatibility, and contract-text comparisons; collect but do not fabricate deferred real-run evidence.
- Verification: every machine/contract/human row is either passed by its carrier or explicitly deferred with its required future authority; no “not run” item is called a pass.
- Exit gate: all implementation-scope automated/inspection cases pass; deferred real publish evidence is non-blocking only because runtime behavior was not changed and current contract text remains compatible.
- State/handoff: save bounded verification evidence and unexecuted items.
- Commit boundary: after the Phase 5 exit gate passes, create one scoped local conventional commit containing only test/compatibility hardening; do not push.

### Phase 6 — Independent implementation review and closeout

- Entry gate: authorized implementation complete; final diff/evidence stable.
- Scoped work: qualifying independent implementation review; remediate; record disposition; move to completed and reconcile all derived surfaces.
- Verification: `accept`, Section 9 implementation-scope matrix, governed harness, budget, links, `git diff --check`, path/generated-artifact audit, and dynamic Git evidence.
- Exit gate: completed metadata, implementation review, disposition, evidence, and any durable commits are recorded truthfully.
- State/handoff: completed state and true next gate; no live Git claim stored as durable truth.
- Commit boundary: keep review remediation and lifecycle closeout separately reviewable; after each verified boundary, create its one scoped local conventional commit under the standing authority; no remote authority is implied.

## 9. Verification Matrix With Carriers

Carrier vocabulary:

- **new fixture**: stdlib temporary-repository test for the future checker;
- **existing backend test**: existing isolated TV/rebuild/data tests, with exact test mapping recorded in Phase 3;
- **contract inspection**: deterministic comparison of tracked contract text/links/file diffs;
- **human evidence**: review of identity/authority/command log/status that software cannot prove;
- **future authorized run**: evidence collected only during a separately authorized real daily update/publish.

### 9.1 Lifecycle and Coding Mode

| Case | Expected result | Verification carrier |
| --- | --- | --- |
| Same slug/path exists in two state directories | fail and identify both paths | new fixture |
| Plan `Status` disagrees with directory | fail | new fixture |
| State index has missing, duplicate, or ghost plan row | fail | new fixture |
| Reviews index lifecycle state disagrees with plan directory | fail | new fixture |
| Roadmap plan-link/state set differs from directories/indexes | fail | new fixture |
| Active lacks matching-revision approve review artifact | fail | new fixture |
| Active cites approve but lacks activation evidence or independence attestation | fail | new fixture |
| Proposed has matching approve but no activation evidence | pass as legal pre-activation state | new fixture |
| Active lacks phase, phase state, entry gate, or next gate | fail | new fixture |
| Completed implemented plan lacks `accept` implementation review or disposition | fail | new fixture |
| Existing completed legacy plan is migrated metadata-only | pass; historical prose unchanged | new fixture + contract inspection |
| PROGRESS/HANDOFF constrained blocks disagree with canonical plan | fail | new fixture |
| Clean fixture has forbidden `- Git state: unstaged/uncommitted diff` outside historical block | fail | new fixture |
| Historical Git evidence uses the explicit historical markers | pass and do not interpret observation prose | new fixture |
| Contract/router/templates/config/workflow path missing | fail specifically | new fixture |
| Checker run changes fixture bytes or Git status | fail test; checker must be read-only | new fixture |
| Governed profile composes focused checker with external `--root`; minimal does not | pass | new fixture |
| New-schema review lacks reviewer fields or uses same author/reviewer ID | fail structurally | new fixture |
| Reviewer identity/independence declaration is truthful | must be manually accepted | human evidence |
| Bounded maintenance meets every Lane 2 criterion and has no Exec Plan | allowed with routing reason and proportionate verification | contract inspection + human evidence |
| Any Section 5.3 criterion is true but work bypasses Lane 3 | stop; no implementation authority | contract inspection + human evidence |

### 9.2 Data Update Mode

| Case | Expected result | Verification carrier |
| --- | --- | --- |
| Date resolution handles holiday/early close and rejects incomplete session | pass/fail per calendar | existing backend test + future authorized run |
| IB is checked/requested before TV retries/hard-gate failure | prohibited by contract; stop if observed | contract inspection + human evidence |
| TV RTH/session/OHLCV/derived-5m hard gate fails | fail without claiming publish success | existing backend test |
| IB fallback lacks runbook whole-day/gap/session evidence | cannot reach `quality_passed` | contract inspection + future authorized run |
| TV and IB bars are mixed in one market day | prohibited; real provenance must show one source | contract inspection + future authorized run |
| Fetch imports tracked DB before rebuild | state recorded as unaccepted intermediate mutation | contract inspection + future authorized run |
| Candidate rebuild would lose market days or non-market rows | fail and preserve rebuild promotion safety | existing backend test |
| Local seed is incomplete relative to tracked DB | routine rebuild refuses shrink; no override | existing backend test |
| Mandatory DB/requested-day/assemble 1m+5m checks fail | cannot reach `local_accepted` | existing backend test + future authorized run |
| Optional static export/build/page smoke is not run | record `not run`; do not call it pass; existing publish contract remains usable | contract inspection + human evidence |
| Local acceptance passes without publish authorization | stop before stage/commit/push/publish | human evidence + Git status |
| Publish trigger exists but a local gate fails | pending authority cannot skip the failure | contract inspection + human evidence |
| Tang trade/context is supplied | validate existing JSON step before authorized commit | contract inspection + future authorized run |
| Data anomaly proves no system defect | return to last safe Data Update state for bounded retry | human evidence |
| Data anomaly requires code/schema/quality/tool change | stop and route Coding Mode; no silent repair | contract inspection + human evidence |
| Routine update edits code, weakens a gate, uses date-loss override, or fabricates data | fail/stop | contract inspection + human evidence |
| Routine daily update uses existing system without Exec Plan | allowed | contract inspection |
| Existing trigger phrases, runbook sequence, and Pages workflow remain unchanged | pass compatibility check; not a real publish test | contract inspection |
| Full commit/push/Pages/hosted sequence succeeds | collect later; not exercised by offline fixtures or this plan | future authorized run |

### 9.3 Repository verification

- `python3 scripts/check-project-harness.py --root . --profile governed`;
- `python3 scripts/check-operating-modes.py --root .` after implementation;
- `python3 -m unittest scripts.tests.test_operating_modes`;
- `python3 scripts/check-startup-doc-budget.py`;
- governed Markdown relative-link checks;
- `.harness/config.json`/workflow exact commands and unchanged job display names;
- no diff in `.github/workflows/publish-static-reviews.yml` or `docs/daily-publish-runbook.md`;
- `git diff --check` plus separate whitespace validation for untracked files;
- intended-path audit with no newly generated reviews export, `dist`, temporary DB, PID, log, or cache;
- backend/frontend native checks only if touched implementation paths or evidence mapping justify them; unavailable prerequisites are reported, never converted into a pass.

## 10. Migration And Compatibility

- First freeze formats, then migrate legacy metadata, then enable strict checking; never enable a checker that knowingly leaves the current completed plan red.
- Add only metadata to the existing completed plan; clearly labeled historical prose is outside checker scope and remains unchanged.
- Resolve its historical bare implementation-review filename to an explicit relative path during metadata reconciliation.
- Standardize all four index rows and roadmap link/state rows before relying on deterministic comparisons.
- Preserve current daily-publish triggers, runbook, runtime DB behavior, and Pages workflow. The direct-import-before-rebuild gap is documented, not silently fixed.
- Any runtime improvement for `--skip-import`, candidate-first fetch, stronger IB hard gates, or publish receipts is a separate Coding Mode proposal.
- `CLAUDE.md` remains a compatibility pointer.
- The new decision records authority ownership, not execution permission; decisions and reviews remain non-authorizing.

## 11. Stop, Rollback, And Scope-Change Conditions

Stop and return to proposal/review when:

- constrained formats cannot be parsed without semantic interpretation of prose;
- the implementation would require a second lifecycle state registry;
- a transition helper or generic workflow engine becomes necessary;
- current daily-publish behavior cannot remain compatible without runtime/runbook/publisher change;
- migration would rewrite historical evidence or break plan/review links;
- a target outside Section 2.2 needs modification;
- unrelated dirty changes overlap a target and cannot be preserved;
- a phase needs unavailable Git, remote, publish, broker, secret, or settings authority;
- independent review returns `revise` or `reject`.

Before commit, rollback is removal/revision of the scoped uncommitted implementation diff. No implementation step may use reset/restore/stash/checkout on unrelated user work.

## 12. Evidence, Review, And Commit Boundaries

- Review directory: `docs/exec-plans/reviews/2026-07-19-tang-strategy-coding-and-data-update-modes-plan/`
- Existing verdicts: `review-001: revise@v1-initial`, `review-002: revise@v1-initial` (legacy-unattested); `review-003: approve@v2-review-foldback-2026-07-19` (attested under Section 3.5)
- Design review gate for v2: closed by `review-003`
- Activation: recorded from explicit user instruction `user-instruction:2026-07-19-move-proposed-plan-to-active`
- Required implementation start: separate explicit start/execute instruction after activation recording
- Required implementation verdict: qualifying `accept` before completed disposition for implemented work
- Expected future commit boundaries: activation recording; authority/format package; legacy migration/router/checker; Data Update contract/evidence; harness/CI; verification hardening; closeout
- Standing local commit authority is granted by `user-instruction:2026-07-19-commit-at-lifecycle-or-phase-boundary` and takes effect for the current activation closeout and all later lifecycle/Phase boundaries in this plan.
- This is boundary authority, not per-edit authority: work may remain uncommitted within a phase, and a commit is created only after the applicable exit verification plus `PROGRESS.md`/`HANDOFF.md` reconciliation pass.
- Before committing, inspect dynamic Git status/diff, preserve unrelated user work, stage only the exact plan-scoped paths for that boundary, and use one concise conventional commit. Disjoint unrelated changes remain unstaged; overlapping or ambiguous unrelated changes stop the commit and require user direction.
- A failed validation or failed commit must be reported at the current gate and does not grant amend, rebase, reset, restore, stash, or broader cleanup authority.
- Push, PR, merge, Pages publish, branch protection, environment approval, and every other remote mutation remain separately authorized actions.

## 13. Current Gate

This plan is **Active** at `phase-0:not-started`. Revision `v2-review-foldback-2026-07-19` has a qualifying matching-revision design review (`review-003: approve`) and explicit user activation evidence. Activation recording is complete, but implementation has not started. The only next gate is `phase-0-start`, which requires a separate explicit start/execute instruction. Activation alone creates no implementation, publication, broker, or remote authority; local commits are authorized only by the separate standing boundary authority recorded in Section 12.
