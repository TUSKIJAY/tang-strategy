# Tang Strategy Operating Modes

- Contract schema: `operating-modes-simple-v1`
- Status: Accepted
- Authority source: user instruction and the active repository request

This is the repository's single routing, lifecycle, and local-commit contract. `AGENTS.md` is the compact entry; `INSTRUCTIONS.md` owns stable project facts and commands.

## 1. Source Ownership

- A plan exists in exactly one of `docs/exec-plans/proposed/`, `active/`, or `completed/`.
- Reviews live under `docs/exec-plans/reviews/<plan-slug>/`.
- The lifecycle indexes, roadmap, `PROGRESS.md`, and `HANDOFF.md` must agree with the canonical plan and review files.
- `.harness/config.json` lists verification commands; it is not lifecycle state.
- Chat history and agent-private memory are not canonical repository state.

## 2. Authority And Task-Scoped Local Commit

A user instruction that authorizes repository file changes also authorizes one local commit containing the completed task result. This applies to every durable Coding Mode step, including:

- creating or updating an OPT record;
- generating or revising a proposed plan;
- writing a review;
- moving a plan to active;
- implementation and proportionate verification;
- writing an implementation review;
- moving a plan to completed and reconciling its direct lifecycle surfaces.

Do not create the local commit only when:

1. the user explicitly says not to commit;
2. the work remains a draft, failed, or incomplete;
3. task-owned files cannot be separated safely from unrelated dirty changes.

Stage only task-owned literal file paths. Never use `git add .`, `git add -A`, directory staging, globs, `git commit -a`, or implicit GUI staging. Inspect the staged path set and run `git diff --cached --check` before committing. Use a concise conventional commit message.

Local commit authority never includes push, PR, merge, Pages, publication, provider/broker access, hosted verification, branch administration, or any other remote action. Those require an explicit user request or the daily publish trigger contract.

Read-only tasks create no files and no commit. Data Update Mode follows §7; local data acceptance alone does not grant commit or publication authority.

## 3. Coding Mode

### Lane 1 — read-only inspection

Use for explanation, diagnosis, verification, ambiguous work, and anomaly investigation. Do not modify repository files.

### Lane 2 — bounded direct maintenance

Lane 2 needs no Exec Plan or independent review when all conditions hold:

- one requested outcome and a bounded file surface are known;
- the change is local, reversible, and proportionately verifiable;
- it does not change security, authorization, market-data, DB, publication, or cross-module contracts;
- unrelated user changes can be preserved.

Complete the task, verify it in proportion to risk, and apply the task-scoped local commit rule in §2.

### Lane 3 — governed Exec Plan

Use Lane 3 for DB or market-data safety, publication, security, cross-contract changes, broad/destructive work, or lifecycle governance. Lane 3 uses proposed review, explicit activation, implementation, implementation review, and closeout.

Do not expand a task because an adjacent issue was noticed. Record the adjacent issue and stop unless it blocks the requested outcome, crosses a hard safety boundary, or the user explicitly adds it to scope. Do not invent new plans, reviewers, state machines, or repeated remediation rounds as ceremony. Verification must be proportionate to actual risk.

## 4. Governed Lifecycle

1. A user-authorized OPT record is recorded and committed locally when complete.
2. A proposed plan is created only when the user asks for it; the proposal and its direct indexes are committed locally.
3. A governed plan review creates one review artifact, updates direct lifecycle links, and commits that review package locally.
4. A matching approval does not activate the plan. Activation requires an explicit user instruction, moves one plan to `active/`, reconciles direct surfaces, and creates a local commit.
5. Implementation requires an explicit start/execute instruction. Complete only the authorized scope, verify it, and commit the task-owned implementation result locally.
6. Implemented Lane 3 work receives an implementation review before completed disposition unless the user explicitly directs a simpler closeout for the current task.
7. Completed migration moves the plan to `completed/`, reconciles direct lifecycle surfaces, and creates a local commit.

Each user request should normally produce one commit. Split only when a real review target or rollback boundary requires it. A lifecycle verdict never grants remote authority.

## 5. Required Plan And Review Metadata

Every plan starts with these metadata bullets:

```text
- Lifecycle schema: `operating-modes-v1`
- Status: Proposed|Active|Completed
- Plan slug: `<filename without .md>`
- Revision: `<stable revision id>`
- Design reviews: none|<review references>
- Latest design verdict: none|approve|revise|reject
- Review independence: none|attested|legacy-unattested
- Activation evidence: none|user-instruction:<token>
- Current phase: none|phase-N
- Phase state: none|not-started|in-progress|blocked|complete
- Phase entry gate: none|<gate>
- Next gate: <gate>|closed
- Implementation review: none|<review path>@accept
- Final disposition: none|Completed|Rejected|Superseded|Terminated|Archived
- Verified implementation commit: none|<40-hex commit>
- Lifecycle reconciliation commit: none|<40-hex commit>
```

Basic state rules:

- Proposed: `Status=Proposed`, no activation, and a non-`none` next gate.
- Active: `Status=Active`, non-`none` activation, current phase, phase state, and next gate.
- Completed: `Status=Completed`, `Current phase=none`, `Phase state=none`, `Next gate=closed`, and non-`none` final disposition.
- A completed implementation uses an accepted implementation review. Historical completed plans may retain their original extra metadata; new templates do not add extra schema layers.

Every review artifact starts with:

```text
- Review target: `<repository-relative plan path>`
- Review target revision: `<revision id>`
- Review type: design|implementation|closeout
- Reviewer ID: `<id>`
- Plan author ID: `<id>`
- Independence declaration: attested
- Evidence method: `<summary>`
- Verdict: approve|revise|reject|accept
- Confidence: low|medium|high
```

The review target filename and revision must match the reviewed plan. A review does not activate or execute a plan.

## 6. Indexes And Current State

The canonical state indexes are:

- `docs/exec-plans/proposed/index.md`
- `docs/exec-plans/active/index.md`
- `docs/exec-plans/completed/index.md`
- `docs/exec-plans/reviews/index.md`

Each plan must be linked exactly once from its matching state index and from the roadmap. Review files must be linked from the plan's reviews-index row, whose latest verdict and lifecycle state must match the linked evidence and plan location.

`PROGRESS.md` and `HANDOFF.md` contain one matching current-state block:

```text
<!-- operating-modes-state:start -->
- Current plan: `<plan-slug-or-none>`
- Lifecycle status: `Proposed|Active|Completed|None`
- Current phase: `none|phase-N`
- Phase state: `none|not-started|in-progress|blocked|complete`
- Next gate: `<gate>|none|closed`
<!-- operating-modes-state:end -->
```

When `Current plan=none`, the other values are `None`, `none`, `none`, and `none`. Otherwise the block must match the named plan's metadata.

## 7. Data Update Mode

Routine use of the existing fetch/rebuild/acceptance system does not require an Exec Plan. Resolve the requested session with the actual US equity calendar, fetch the SPY/QQQ pair from TradingView first, validate hard session/OHLCV gates, rebuild through a candidate DB, reject shrink/integrity/drift failures, and verify the requested day through the runtime.

Stop after local acceptance unless the user used a daily publish trigger or otherwise explicitly requested publication. The publish authority permits only the runbook's scoped data/content commit and push sequence after every local gate passes. It does not permit code changes, gate weakening, fabricated data, `--allow-date-loss`, PR, merge, or unrelated remote administration.

If existing tooling needs code or contract changes, stop Data Update Mode and route that change through Coding Mode.

## 8. Verification

Run verification in proportion to the change:

- lifecycle or documentation changes: `python scripts/check-operating-modes.py --root .`, `python -m unittest scripts.tests.test_operating_modes`, `python scripts/check-project-harness.py --root . --profile auto`, and `git diff --check`;
- product changes: focused tests plus the relevant build or browser acceptance;
- DB/data changes: the candidate, integrity, non-shrink, runtime, and runbook gates;
- remote actions: only after explicit authority and only with their real remote receipts.

Browser acceptance runs write to `output/playwright/<plan-slug>-<run-id>/`. Commit that run's `receipts.json` — the assertion values are the durable evidence and stay greppable and re-verifiable. Every path a receipt records that points inside the repository is repository-relative with forward slashes (`output/playwright/<run>/v2-foo.png`); an absolute machine path to a repository file is a defect, since it names one developer's disk and reads as broken on every other machine and OS. An artifact deliberately written outside the worktree is named by its real absolute path — that is a location, not a repository path. Screenshots and scratch databases from the run stay local and are gitignored; a screenshot only enters the repository when a plan deliberately pins its SHA-256, and then it belongs in that plan's `evidence/` folder, not in `output/`.

Local acceptance artifacts have a defined life, and clearing them needs no separate authorization:

- Scratch databases die with the run that created them. Delete them at the end of the run, not later.
- A superseded run — any earlier attempt at the same acceptance — is deleted as soon as the run that the review packet cites exists. Only the cited run survives.
- The cited run's screenshots are deleted once the plan reaches `Completed`. From then on the committed `receipts.json` and the implementation review carry the claim.
- Nothing under `output/` is a record, and no `output/` tree survives its plan. A resumed session preserves untracked `output/` trees only while their plan is still open.

Because runs do not outlive their plan, a closed plan's review packet naming its run directory is a historical reference, not a broken link. Leave those records as written; do not rewrite frozen governance text to chase a path that was always ephemeral.

The lifecycle checker is intentionally small. It verifies plan uniqueness, required metadata, state-index and roadmap links, review verdict linkage, and matching `PROGRESS.md` / `HANDOFF.md` state. It does not parse Git history, CI YAML semantics, arbitrary Markdown edge cases, or remote authority.
