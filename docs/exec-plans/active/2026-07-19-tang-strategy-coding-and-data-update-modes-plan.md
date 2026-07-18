# Tang Strategy Coding And Data Update Modes

- Lifecycle schema: `operating-modes-v1`
- Status: Active
- Plan slug: `2026-07-19-tang-strategy-coding-and-data-update-modes-plan`
- Revision: `v2-review-foldback-2026-07-19`
- Plan author ID: `codex-plan-author-2026-07-19`
- Owner: Codex
- Created: 2026-07-19
- Design reviews: ../reviews/2026-07-19-tang-strategy-coding-and-data-update-modes-plan/review-001.md@revise@v1-initial, ../reviews/2026-07-19-tang-strategy-coding-and-data-update-modes-plan/review-002.md@revise@v1-initial, ../reviews/2026-07-19-tang-strategy-coding-and-data-update-modes-plan/review-003.md@approve@v2-review-foldback-2026-07-19
- Review status: v1 reviews revise; v2 matching-revision design review `review-003` returned approve; user activation instruction recorded
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-19-move-proposed-plan-to-active`
- Current phase: phase-6
- Phase state: in-progress
- Phase entry gate: `phase-5-complete@28629a59a2eb7d0fdce362e2754d8476b7f4aa8e`
- Next gate: phase-6-re-review-r12
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Implementation authority: Phases 0-5 and remediations r1-r11 are complete under `user-goal-execute-plan-2026-07-19`; Phase 6 now requires renewed independent implementation review and a qualifying `accept` before closeout
- Scope authority: re-review-r12 is read-only except for its review artifact; no further implementation mutation is authorized until a review finding requires bounded remediation, and runtime, data, provider, publisher, and remote surfaces remain frozen
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

The checker can verify field presence, target revision, accepted verdict vocabulary, and that reviewer/author IDs differ. It cannot prove that the identity or declaration is truthful, nor can it prove that a user actually issued an activation/publish instruction. A human reviewer must validate those attestations and evidence references. Existing `review-001`/`review-002` remain valid `revise` feedback; remediation-r5 migrated only their constrained metadata to the new schema while preserving their historical findings and verdicts. Neither can satisfy the matching-revision activation gate because both target `v1-initial`.

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
- Existing verdicts: `review-001: revise@v1-initial`, `review-002: revise@v1-initial` (metadata-only migrated to attested constrained records in remediation-r5); `review-003: approve@v2-review-foldback-2026-07-19` (attested under Section 3.5)
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

This plan is **Active** at `phase-6:in-progress`. Independent re-review `implementation-review-011` returned `revise` with `high` confidence against remediation-r10 commit `ff00efdeb1c1f17d5ed6dbd89c6acf491a320bca`; remediation-r11 has now closed the recorded raw YAML printable-source finding with 145 passing fixtures and the full bounded verification set. The only next gate is fresh independent implementation re-review-r12 against the stable remediation commit. Completed disposition still requires `accept`. No broker, provider, tracked-DB mutation, publication, remote, PR, merge, or push authority was created.

## 14. Phase Execution Record

### Phase 0 — complete

- Entry authority: `user-goal-execute-plan-2026-07-19` explicitly instructed Codex to execute this active plan.
- Startup baseline: repository root `/Users/neowang/Code/tang-strategy-github`, branch `codex/project-harness`, clean index/worktree, and HEAD `a4b4007a9e529d1748f7f3b9884768471751dc33` were observed before implementation. This is historical execution evidence, not a durable live-Git claim.
- Harness baseline: `python3 scripts/check-project-harness.py --root . --profile governed` returned `passed=true` and `errors=[]`; `python3 scripts/check-startup-doc-budget.py` returned no hard-limit or archive requirement.
- Manifest revalidation: all existing modification targets and read-only references in Section 2.2 were present; the four planned additions (`docs/operating-modes.md`, the operating-modes decision, focused checker, and fixture test module) were absent as expected. No extra implementation path was required.
- Checker baseline: `scripts/check-project-harness.py` was 277 lines and had no Git invocation, lifecycle discovery, plan-metadata parser, directory uniqueness check, or state-surface reconciliation.
- Runtime compatibility baseline: both tracked TV and IB fetch adapters expose `--skip-import` but import into the runtime DB by default; `rebuild_live_extended_db.py` owns candidate-first validation/promotion. The daily runbook remains TV-first and the Pages workflow remains the only `gh-pages` publisher.
- Frozen read-only hashes: `docs/daily-publish-runbook.md` = `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`; `.github/workflows/publish-static-reviews.yml` = `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`; tracked DB = `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`.
- Authority freeze: local plan-scoped implementation and verified phase-boundary commits are authorized; fetch, rebuild, DB mutation, broker/provider connection, push, PR, merge, Pages publish, remote administration, and scope expansion are not authorized.
- Exit result: no unresolved manifest/baseline mismatch; Phase 1 may start after the scoped Phase 0 lifecycle/evidence commit succeeds.

### Phase 1 — complete

- Entry evidence: Phase 0 exit commit `6b1707cd75a2396dc39b6611ff6028fdacf851d2` and clean scoped baseline.
- Contract: added `docs/operating-modes.md` as the single normative source for peer modes, authority dimensions, Coding lanes, lifecycle stages, `operating-modes-v1` formats, reviewer evidence, Data Update gates, escalation, and checker/human boundaries.
- Decision and routing: added the Accepted operating-modes/source decision and routed both contract and decision from the documentation authority map and decision index. Decision acceptance is explicitly non-executing.
- Constrained formats: plan and review templates now own every required field; four index tables and roadmap lifecycle rows use fixed link/state shapes; `PROGRESS.md` and `HANDOFF.md` contain one matching current-state block. Gate tokens use a minimal character constraint rather than a closed vocabulary.
- Migration treatment: existing completed-plan prose remains untouched until metadata-only migration in Phase 2; fixed current index rows already use the future deterministic shapes.
- Fixture-carrier attestation: every Section 9.1 and 9.2 row has an implementable carrier. Lifecycle/state/review/read-only/profile cases map to temporary-repository fixtures; routing and unchanged text map to contract inspection; actual calendar/TV/rebuild/DB/assemble behavior maps to named existing backend tests in Phase 3; identity/authority/order/optional checks map to human evidence; real publish proof remains a future authorized run.
- Exit result: no checker requirement depends on ambiguous prose, and no offline carrier claims a provider, broker, DB update, push, Pages run, or hosted verification passed. Phase 2 may start after the scoped Phase 1 commit succeeds.

### Phase 2 — complete

- Entry evidence: Phase 1 exit commit `e1b976820aeb93e6e8889eb2fb5d1c8b9a603a7b` and clean scoped baseline.
- Legacy migration: added only constrained lifecycle metadata to the 2026-07-18 completed plan, using `operating-modes-legacy-v1`, explicit design/implementation review paths, final disposition, implementation commit, and lifecycle reconciliation commit. Historical narrative and review bodies remain unchanged.
- Routing: `AGENTS.md` now links the single normative contract with a compact peer-mode/risk router while preserving every daily trigger; `INSTRUCTIONS.md` routes the same contract and lists focused verification commands.
- Checker: added dependency-free `scripts/check-operating-modes.py`. It discovers canonical plans, rejects duplicate slug/state mismatch, validates state invariants and reviewer evidence, compares state indexes/reviews index/roadmap, reconciles the two current-state blocks, rejects forbidden live-Git keys, reports dynamic Git status, validates required contract paths/routes/templates, emits JSON/errors, and performs no writes.
- Harness composition: governed `scripts/check-project-harness.py` invokes the focused checker with the caller's explicit `--root`; minimal profile does not invoke it.
- Coding/lifecycle fixtures: 26 temporary Git-repository tests passed, including valid active/proposed/completed states; duplicate/status/index/reviews/roadmap failures; missing approve/activation/phase/disposition/implementation review; current-block mismatch; historical versus forbidden Git claims; required-path/router/reviewer/revision checks; read-only byte/status preservation; governed external-root composition; and minimal-profile exclusion.
- Current repository: focused checker and composed governed checker pass with the migrated legacy plan and active v2 plan. No transition helper was added.
- Exit result: invalid lifecycle states fail specifically, valid migrated state passes, and Phase 3 may start after the scoped Phase 2 commit succeeds.

### Phase 3 — complete

- Entry evidence: Phase 2 exit commit `10e19e71012c2573334e743395507349125f34c2` and clean scoped baseline.
- Contract finalization: added an explicit 19-row Data Update carrier map to `docs/operating-modes.md`, covering calendar/source ordering, TV/IB quality, import-before-rebuild, candidate safety, local acceptance, optional checks, publication separation, anomaly routing, and future hosted evidence.
- Existing test mapping: calendar/RTH cases map to `test_fetch_tv_live_extended_day.py`; candidate/non-shrink/semantic/integrity/drift/rollback cases map to all 11 rebuild and 4 DB-safety tests. The current system-Python run executed 19 tests: 18 passed and only the calendar test errored because `pandas_market_calendars` is absent from both available local Python environments. Per repository contract this is an environment prerequisite failure, not a code pass or regression.
- Runtime-only evidence: a new requested day's real provider provenance, default-import before/after DB evidence, IB whole-day/gap/session proof, assemble 1m/5m receipt, optional page smoke status, user-supplied Tang JSON, command order, Git publication boundary, Pages run, and hosted URL remain future authorized-run or human evidence.
- Compatibility inspection: daily trigger phrases, TV-first runbook ordering, `--allow-date-loss` prohibition, default TV/IB `import_market_json` calls, tracked-DB publisher input, and the sole `gh-pages` workflow remain unchanged. Frozen hashes still match Phase 0.
- Exit result: local success cannot be interpreted as publish authority, no offline evidence claims a real publish, and no separately proposed runtime change is required for this plan. Phase 4 may start after the scoped Phase 3 commit succeeds.

### Phase 4 — complete

- Entry evidence: Phase 3 exit commit `549ec914d8fed9c47e96995e552c2d909a599f51` and clean scoped baseline.
- Config: `.harness/config.json` retains the canonical governed entry and adds `python3 -m unittest scripts.tests.test_operating_modes` immediately after it.
- CI: the existing `Harness structure` job runs the same canonical command then the fixture suite. Job display names remain exactly `Harness structure`, `Backend checks`, and `Frontend build`; backend/frontend jobs are otherwise unchanged.
- Enforcement: the focused checker now rejects missing/misordered canonical or fixture commands in config/workflow. Three new negative fixtures cover config omission, config ordering, and workflow omission; the suite now passes 29 tests.
- Compatibility: governed and minimal profile behavior, external fixture roots, state-block reconciliation, startup-document budget, Markdown links, workflow job names/order, and no Pages workflow diff all pass. `.github/workflows/publish-static-reviews.yml` retains its Phase 0 hash.
- Exit result: local and PR harness paths enforce the same operating-modes contract without network, provider, broker, tracked DB, or publication access. Phase 5 may start after the scoped Phase 4 commit succeeds.

### Phase 5 — complete

- Entry evidence: Phase 4 exit commit `f8e84d657a6de7bac5a825f620cd6641d4a67c92` and clean scoped baseline.
- Historical Phase 5 matrix: added active independence, migrated legacy completed-plan, daily-trigger, TV-first runbook, default fetch-import, and Pages publisher cases. The temporary-Git suite passed 35 tests, but the later independent review demonstrated that its constrained-lifecycle negative coverage was incomplete.
- Review-corrected evidence boundary: Phase 5 attempted to enforce runbook, adapter, rebuild, and publisher behavior through raw source/prose tokens. Independent review proved both comment-token false-pass and equivalent-refactor false-failure, so Phase 6 removes that semantic scanning; unchanged compatibility is supported by the already recorded baseline-to-HEAD exact diff/hashes, named behavior tests, and human inspection.
- Backend verification: an isolated `/tmp` venv installed the pinned `backend/requirements-tv.txt`; all 19 backend tests passed, including the calendar/holiday/early-close carrier that was unavailable in the pre-existing environments. Backend compileall passed. Third-party calendar libraries emitted only deprecation warnings. The temporary venv and generated caches were removed.
- Compatibility verification: frontend production build passed with 1746 transformed modules and generated `frontend/dist` was removed; tracked DB read-only `integrity_check=ok` and foreign-key output was empty; focused/composed checkers, startup budget, launcher syntax, Markdown links, job names, whitespace, intended paths, and read-only hashes passed.
- Deferred evidence: no real provider fetch, IB fallback, tracked-DB update, Tang trade input, local page smoke, data commit/push, Pages run, or hosted URL verification was authorized or executed. Those items are not called passes and remain future Data Update evidence.
- Exit result: Phase 5 reached independent implementation review at commit `28629a59a2eb7d0fdce362e2754d8476b7f4aa8e`; `implementation-review-001` returned `revise`, so its green checks are historical evidence rather than closeout acceptance.

### Phase 6 — in progress

- Entry evidence: Phase 5 exit commit `28629a59a2eb7d0fdce362e2754d8476b7f4aa8e` and independent implementation review `implementation-review-001.md`.
- Review boundary: reviewer `independent-implementation-reviewer-2026-07-19-r1` returned `revise` with `high` confidence after inspecting the baseline-to-Phase-5 diff, phase commits, checker/fixtures, lifecycle evidence, read-only DB state, frontend build, and frozen hashes.
- Required remediation: reject duplicate constrained keys; bind design and implementation review types to their use; constrain review targets/artifact paths; constrain Proposed next gates; reconcile review-index artifacts/latest verdict and lifecycle-index evidence; remove unconstrained source/prose semantic scanning from the focused lifecycle checker; correct the stale handoff wording.
- Closeout gate: record this review boundary separately, implement only the reviewed remediation scope, pass focused/composed/native verification, and obtain a fresh independent `accept` before completed disposition.
- Remediation result: the checker now rejects duplicate constrained keys across plans, reviews, templates, and current-state blocks; binds review type/target/path to its evidence role; limits Proposed gates; reconciles exact review artifact sets/latest verdicts plus state-index evidence; and treats non-constrained runbook/source/workflow content as external compatibility evidence rather than lifecycle semantics. The governed wrapper also fails closed when the focused checker exits nonzero without structured errors.
- Adversarial verification: 49 temporary-Git fixtures pass, including all implementation-review-001 reproductions plus duplicate state/template cases. Comment-only adapter tokens and behavior-equivalent multiline adapters both leave lifecycle validation unchanged, proving the false-pass/false-failure source scanner was removed.
- Native/read-only verification: focused and governed/auto composed checkers, startup budget, launcher syntax, whitespace, 19/19 pinned backend tests plus compileall, frontend production build (1746 modules to a temporary output), tracked DB integrity/foreign keys, runtime zero-diff from Phase 5, and frozen runbook/Pages/DB hashes all pass. Temporary environments/output and generated caches were removed.
- Review gate: commit the scoped remediation boundary, then request a fresh independent review against that stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review boundary: `implementation-review-002.md`, authored by `independent-implementation-reviewer-2026-07-19-r2`, returned `revise` with `high` confidence against stable commit `6c108feaa0870c3c363349088b6333a3c8f51f6f`. It confirmed every implementation-review-001 finding closed and found two local follow-ups: optional evidence must use truthful `none` sentinels for pre-review Proposed and non-implemented Completed states while rejecting bogus links, and `design-review` must allow the same delimiter/suffix grammar as the other Proposed gate categories.
- Remediation-r2 gate: record this review separately, add positive and adversarial fixtures for both optional-evidence lifecycle states plus all allowed gate prefixes, rerun the bounded verification set, and obtain a fresh independent `accept` before closeout.
- Remediation-r2 result: the reviews index now requires one row for every plan. Rows with no review artifacts link the canonical plan and use exact `none`/`none`, avoiding non-durable empty directories; Proposed and non-implemented Completed state rows likewise require an unlinked `none` sentinel and reject bogus links. Artifact-bearing rows retain exact review-directory/set/latest-verdict enforcement. `design-review` now supports the same delimited suffix grammar as the other four Proposed categories.
- Remediation-r2 verification: 55 temporary-Git fixtures pass, including truthful-pass and bogus-link-fail cases for pre-review Proposed and non-implemented Completed states, a missing reviews-index row failure, and suffixed positive cases for all five allowed Proposed gate prefixes. Focused/governed/auto checks, startup budget, launcher syntax, DB integrity/FK, runtime zero-diff, frozen hashes, and whitespace pass. The earlier pinned 19/19 backend/compileall and temporary frontend build evidence remains applicable because remediation-r2 changes only the contract, focused checker, and its fixtures.
- Re-review-r3 gate: commit this scoped remediation boundary, then request another fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r3 boundary: `implementation-review-003.md`, authored by `independent-implementation-reviewer-2026-07-19-r3`, returned `revise` with `high` confidence against stable commit `8a93fcd20ea32ed8d09049091b9f16bd8445dbd0`. It confirmed all prior findings and remediation-r2 target cases closed, then found three local false-passes: `Final disposition=Completed` must require implementation `accept` even without commit evidence; `Design reviews=none` must imply latest verdict and independence `none`; and every fixed index Plan cell must contain exactly one canonical link with no appended second link.
- Remediation-r3 gate: record this review separately, add the three constrained consistency checks and their adversarial fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r3 result: `Final disposition=Completed` now classifies the plan as implemented and always requires an implementation `accept`, independent of commit authority/evidence. New-schema plans with no design reviews require latest verdict and independence `none`; new-schema plans with design reviews require `attested`. Fixed index rows now contain exactly four cells, and every Plan cell must be exactly one standalone canonical link.
- Remediation-r3 verification: 62 temporary-Git fixtures pass, adding Completed-without-review, contradictory no-review verdict/attestation, reviewed-without-attestation, second Plan-link in state/reviews indexes, and extra-cell failures. Focused/governed/auto checks, startup budget, launcher syntax, DB integrity/FK, runtime zero-diff, frozen hashes, and whitespace pass. No runtime, provider, broker, tracked-DB mutation, publisher, or remote action occurred.
- Re-review-r4 gate: commit this scoped remediation boundary, then request another fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r4 boundary: `implementation-review-004.md`, authored by `independent-implementation-reviewer-2026-07-19-r4`, returned `revise` with `high` confidence against stable commit `b3625e907c4ce843f3b9dc52c7376a0bfebb5fca`. It confirmed all prior findings closed, then found that empty `user-instruction:` can activate a plan, Active `Next gate=none` can pass, and the table tokenizer can erase a trailing empty fifth cell or ignore arbitrary no-link data rows.
- Remediation-r4 gate: record this review separately, enforce non-empty Active activation/next-gate evidence and exact fixed-table row/sentinel tokenization, add adversarial fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r4 result: activation evidence now matches `user-instruction:<non-empty-token>`, Active `Next gate` must be non-`none`, and the table tokenizer removes at most one outer delimiter so trailing empty cells remain visible. Fixed indexes reject arbitrary no-link rows, duplicate/mixed sentinels, appended empty fifth cells, extra cells, and malformed Plan cells. The real Proposed index was migrated from prose to the canonical `none` sentinel.
- Remediation-r4 verification: 67 temporary-Git fixtures pass, adding empty activation, Active next-gate none, trailing empty fifth cells across all four indexes, arbitrary no-link rows, and mixed sentinel failures. Focused/governed/auto checks, startup budget, launcher syntax, DB integrity/FK, runtime zero-diff, frozen hashes, and whitespace pass. No runtime, provider, broker, tracked-DB mutation, publisher, or remote action occurred.
- Re-review-r5 gate: commit this scoped remediation boundary, then request another fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r5 boundary: `implementation-review-005.md`, authored by `independent-implementation-reviewer-2026-07-19-r5`, returned `revise` with `high` confidence against stable commit `68f117f84e6cc72fa27bbbe90f8a2f196d404088`. It confirmed all prior findings closed, then found four categories: comment-only workflow/router tokens can satisfy carriers; empty indexes can omit sentinels and reserved headers/missing delimiters bypass grammar; current-state markers can be reversed; and new-schema prior-revision reviews can incorrectly use legacy unstructured evidence.
- Remediation-r5 gate: record this review separately, enforce executable/non-comment carriers and exact constrained grammar, migrate any affected new-schema review metadata without rewriting review findings, add adversarial fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r5 result: contract routes now require non-comment, non-fenced canonical Markdown links. The project workflow accepts required commands only from actual inline/block `steps[].run` carriers in declared order and rejects comments or nested dead keys. All four indexes require their exact header, immediately adjacent separator, terminal delimiters, fixed rows, and exactly one sentinel when empty. Current-state blocks require start-before-end bounded markers. New-schema plans require full metadata on every declared review revision; `review-001` and `review-002` received metadata-only migration with their findings and verdicts unchanged.
- Remediation-r5 verification: 79 temporary-Git fixtures pass, including every implementation-review-005 repro plus block-run positive, nested-run negative, header adjacency, four delimiter forms, missing state/reviews sentinels, reserved-word rows, reversed markers, and new-schema prior-revision bare-review failure. Focused/governed/auto checks, startup budget, launcher/checker syntax, frontend production build (1746 modules to deleted temporary output), DB integrity/FK, runtime zero-diff, frozen hashes, and whitespace pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r6 gate: commit this scoped remediation boundary, then request another fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r6 boundary: `implementation-review-006.md`, authored by `independent-implementation-reviewer-2026-07-19-r6`, returned `revise` with `high` confidence against stable commit `cc00bc40075b560a091b5ce30f2c60ba426b3a7e`. It confirmed all implementation-review-005 findings and prior key regressions closed, then found three categories: commands in non-job, `if:false`, dead-shell, and heredoc contexts can satisfy workflow carriers; lifecycle tables and constrained metadata inside HTML comments/fenced code can pass; and router pseudo-links inside inline/indented code can pass.
- Remediation-r6 gate: record this review separately, constrain workflow carriers to direct runnable job steps, exclude non-operative Markdown contexts from lifecycle/router evidence, add the recorded negative fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r6 result: workflow enforcement is limited to direct, unconditional `jobs.<job>.steps[].run` values. Inline/quoted scalars must exactly equal the command; literal/folded blocks must normalize to exactly one non-comment command, so non-job steps, any job/step `if`, dead branches, heredocs, early exits, nested keys, and multi-line shell flow do not count. A shared Markdown preprocessor removes closed/unclosed HTML comments, fenced code, and indented code before constrained plan/review/template bullets and index tables are parsed. Router matching additionally rejects pseudo-links wholly contained in inline code while preserving real links with code-formatted labels.
- Remediation-r6 verification: 96 temporary-Git fixtures pass, including all implementation-review-006 reproductions, four comment-wrapped indexes, fenced/indented tables, commented plan/review/template metadata, unclosed comments, inline/indented router code, non-job and conditioned workflow carriers, dead-shell/heredoc/early-exit blocks, plus quoted-inline and single-command literal/folded positives. Focused/governed/auto checks, startup budget, launcher/checker syntax, frontend production build (1746 modules to deleted temporary output), DB integrity/FK, runtime zero-diff, frozen hashes, and whitespace pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r7 gate: commit this scoped remediation boundary, then request another fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r7 boundary: `implementation-review-007.md`, authored by `independent-implementation-reviewer-2026-07-19-r7`, returned `revise` with `high` confidence against stable commit `7c750c24d8b53b41260d926e7a57ae896707c322`. It confirmed every implementation-review-006 repro and prior key regression closed, then found three categories: valid quoted `if` keys and execution modifiers can make non-running required steps count; multiline CommonMark/raw HTML code contexts can hide lifecycle or route evidence; and folded block handling can both accept a shell-comment no-op and reject a valid scalar that normalizes to the exact command.
- Remediation-r7 gate: record this review separately, fail closed on execution modifiers and quoted conditions, implement actual constrained literal/folded normalization, mask multiline/raw-HTML code contexts, add all recorded positive/negative fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r7 result: required workflow evidence now requires an operative `pull_request` trigger for `main`, an `ubuntu-latest` job with only the declared direct job keys, and a required step with only optional `name` plus exactly one `run`. Bare or quoted conditions, execution modifiers, workflow/job defaults or environment, unsupported runners, duplicate keys, and other direct carrier modifiers fail closed. Literal/folded blocks preserve source comments and normalize by declared style before exact command comparison, including valid folded commands split across physical source lines. Operative Markdown parsing now excludes multiline CommonMark code spans and closed/unclosed raw HTML `code`/`pre` contexts while preserving real links with code-formatted labels.
- Remediation-r7 verification: 114 temporary-Git fixtures pass, including every implementation-review-007 reproduction and added pull-request-trigger, duplicate-key, runner/default/environment, quoted-condition, modifier, folded-comment, folded-split-command, multiline-code-span, and raw-HTML-code cases. Focused/governed/auto checks, startup budget, launcher/checker syntax, `git diff --check`, baseline runtime/data zero-diff, exact frozen hashes, read-only DB integrity/foreign keys/46-day count, and a Vite production build of 1746 modules to an external temporary directory all pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r8 gate: commit this scoped remediation boundary, then request a fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r8 boundary: `implementation-review-008.md`, authored by `independent-implementation-reviewer-2026-07-19-r8`, returned `revise` with `high` confidence against stable commit `9dad5a9396ecc0efd0e776707aa6f0a5a27dedaf`. It confirmed all implementation-review-007 reproductions and prior key regressions closed, then found two serious false-pass groups: duplicate/unrelated workflow mappings and cross-job flattening can claim a trigger or ordered commands that are not operative, while nested same-tag raw HTML can expose hidden routes or lifecycle metadata. It also found valid quoted/flow YAML spellings and an explicit block-indent form false-rejected outside a declared source restriction.
- Remediation-r8 gate: record this review separately, enforce unique direct YAML hierarchy and same-job command order, mask nested raw HTML code carriers, normalize or explicitly constrain supported equivalent YAML forms, add every recorded positive/negative fixture, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r8 result: workflow evidence now rejects duplicate top-level mappings, duplicate direct event/field keys, duplicate job IDs including inline shadow values, structurally nested trigger lookalikes, and commands split across concurrent jobs. `on.pull_request.branches` must be a unique direct hierarchy containing `main`, while plain/quoted constrained keys, plain/quoted block sequence items, flow branch sequences, quoted runners, and declared literal/folded block indicators normalize consistently. Both required commands must occur in order in one qualifying job. Operative Markdown uses a nested stack for raw HTML `code`/`pre`, masks matching outer carriers and unclosed carriers, and retains real links with code-formatted labels.
- Remediation-r8 verification: 133 temporary-Git fixtures pass, including all implementation-review-008 reproductions, duplicate top-level/event/field mappings, duplicate top-level `jobs`, block and inline duplicate job IDs, nested trigger, path-filter and second-document weakening, cross-job order, nested route/plan/review/table raw-code contexts, custom tag boundary, quoted keys, quoted/flow branch sequences, quoted `jobs`/job IDs, and explicit block indentation indicators. Focused/governed/auto checks, startup budget, launcher/checker syntax, `git diff --check`, baseline runtime/data zero-diff, exact frozen hashes, read-only DB integrity/foreign keys/46-day count, and a Vite production build of 1746 modules to an external temporary directory all pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r9 gate: commit this scoped remediation boundary, then request a fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r9 boundary: `implementation-review-009.md`, authored by `independent-implementation-reviewer-2026-07-19-r9`, returned `revise` with `high` confidence against stable commit `fbc3729c35e55f8f28e383c5ed7dc2b475f4f3ef`. It confirmed all implementation-review-008 reproductions and prior key regressions closed, then found two serious source-grammar false-passes: a branch flow sequence can contain empty or mapping members alongside `main`, and a qualifying job can silently skip a bare null step or treat comment-null `name` as non-empty.
- Remediation-r9 gate: record this review separately, fully consume and validate declared branch string scalars, reject empty/mapping/collection/anchor/alias/tag members, reject bare/null/scalar direct steps, interpret comment/null/whitespace names as absent, add all recorded negative and retained positive fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r9 result: branch flow sequences now use a quote-aware full-consumption tokenizer and every flow/block member must parse as a supported non-empty string scalar. Empty members, malformed quotes, mappings, nested collections, anchors, aliases, tags, source-comment values, YAML null/boolean/numeric coercions, and undeclared structures fail closed. A qualifying job enumerates every direct step item; bare/null/scalar items disqualify the job. Job and required-step names use the same non-coercing scalar subset and reject comment-null, null words, or quoted whitespace.
- Remediation-r9 verification: 139 temporary-Git fixtures pass, including both implementation-review-009 reproductions, syntactically invalid and valid non-scalar flow variants, anchor/alias/tag/malformed-quote variants, block mapping member, bare/null/scalar step items, comment/null/whitespace names, plus retained quoted and trailing-comma flow positives. Focused/governed/auto checks, startup budget, launcher/checker syntax, `git diff --check`, baseline runtime/data zero-diff, exact frozen hashes, read-only DB integrity/foreign keys/46-day count, and a Vite production build of 1746 modules to an external temporary directory all pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r10 gate: commit this scoped remediation boundary, then request a fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r10 boundary: `implementation-review-010.md`, authored by `independent-implementation-reviewer-2026-07-19-r10`, returned `revise` with `high` confidence against stable commit `b5f754b9feed272ea57dad58dfa56c5c553c613b`. It confirmed all implementation-review-009 reproductions and prior key regressions closed, then found binary and underscore-separated numeric YAML scalars can enter string-only branch/name carriers, an unquoted terminal colon can enter as a mapping-like branch member, and valid YAML `\xNN` double-quoted string escapes are rejected.
- Remediation-r10 gate: record this review separately, align the declared YAML string subset with those three bounded source forms, add exact negative and retained-positive fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r10 result: the shared constrained string parser now rejects YAML 1.1/1.2 binary, octal, hex, underscore-separated, decimal, exponent, float, and sexagesimal numeric spellings plus unquoted terminal-colon mapping indicators. A stdlib single-line YAML double-quoted decoder supports named and `\x`/`\u`/`\U` escapes while rejecting malformed escapes and invalid Unicode scalar values. Branch members and job/step names retain one non-coercing grammar; quoted terminal colons remain valid strings.
- Remediation-r10 verification: 143 temporary-Git fixtures pass, including flow/block binary and underscore numerics, numeric job/step names, flow/block terminal-colon negatives, quoted terminal-colon positives, YAML `\x6d` positive, and invalid escape negative. Focused/governed/auto checks, startup budget, launcher/checker syntax, `git diff --check`, baseline runtime/data zero-diff, exact frozen hashes, read-only DB integrity/foreign keys/46-day count, and a Vite production build of 1746 modules to a deleted external temporary directory all pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r11 gate: commit this scoped remediation boundary, then request a fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
- Re-review-r11 boundary: `implementation-review-011.md`, authored by `independent-implementation-reviewer-2026-07-19-r11`, returned `revise` with `high` confidence against stable commit `ff00efdeb1c1f17d5ed6dbd89c6acf491a320bca`. It confirmed all implementation-review-010 findings and prior key regressions closed, then found raw U+007F-U+0084 and U+0086-U+009F source characters can enter a double-quoted branch member even though YAML parsers reject that source.
- Remediation-r11 gate: record this review separately, enforce YAML's printable-source ranges for the declared single-line double-quoted scalar, distinguish raw forbidden characters from valid escaped values, add exact fixtures, rerun bounded verification, and obtain a fresh independent `accept` before closeout.
- Remediation-r11 result: the single-line YAML double-quoted decoder now permits only raw tab, U+0020-U+007E, U+00A0-U+D7FF, U+E000-U+FFFD, and valid supplementary scalar values. Raw C0/DEL/C1 controls, line breaks, surrogates, and noncharacters fail closed, while valid escapes can still decode to values such as U+007F without putting forbidden raw source into the workflow.
- Remediation-r11 verification: 145 temporary-Git fixtures pass, including raw U+007F, U+0080, U+0084, U+0085, U+0086, and U+009F negatives plus an escaped `\x7F` retained positive. Focused/governed/auto checks, startup budget, launcher/checker syntax, `git diff --check`, baseline runtime/data zero-diff, exact frozen hashes, read-only DB integrity/foreign keys/46-day count, and a Vite production build of 1746 modules to a deleted external temporary directory all pass. The earlier pinned 19/19 backend evidence remains applicable because no runtime file changed.
- Re-review-r12 gate: commit this scoped remediation boundary, then request a fresh independent review against the stable commit. `Implementation review` remains `none` until a qualifying `accept` artifact exists.
