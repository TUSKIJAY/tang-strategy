# Tang Strategy Durable Checkpoint And Scoped Local Commit Governance

- Lifecycle schema: `operating-modes-v1`
- Status: Completed
- Plan slug: `2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan`
- Revision: `v2-review-foldback-2026-07-20`
- Plan author ID: `codex-plan-author-2026-07-20-durable-checkpoint`
- Design reviews: docs/exec-plans/reviews/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan/review-001.md@revise@v1-proposal-2026-07-20, docs/exec-plans/reviews/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan/review-002.md@approve@v2-review-foldback-2026-07-20
- Latest design verdict: approve
- Review independence: attested
- Activation evidence: `user-instruction:2026-07-20-activate-durable-checkpoint-governance`
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: `closed`
- Implementation review: ../reviews/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan/implementation-review-001.md@accept
- Final disposition: Completed
- Verified implementation commit: 61ea580f0b284d835c79cd47130104b90a04d2f2
- Lifecycle reconciliation commit: none
- Owner: Codex
- Created: 2026-07-20
- Activated: 2026-07-20
- Scope authority: implementation and accepted lifecycle closeout completed under the named instructions; standing plan-scoped local commit authority remains valid only for the final v1 reconciliation-boundary recording, with no push, PR, merge, Pages publication, provider/broker access, tracked data write, hosted verification, or remote administration authority

## 1. Context And Evidence

### 1.1 Proposal provenance

This plan addresses a structural gap in the current `operating-modes-v1` governance: the lack of a normative durable checkpoint contract. Today, lifecycle transitions and completed work products have no standardized mechanism for scoped local Git commits. The result is that multiple unrelated lifecycle products accumulate in the worktree, creating interleaved dirty state that cannot be cleanly separated for review, audit, or rollback.

Revision `v2-review-foldback-2026-07-20` incorporates every finding in `review-001`. The historical filename and plan slug retain `auto-commit` only to preserve stable links. Operative contract text retires that term: this plan authorizes no unattended Git mutation and defines only a human- or agent-executed **scoped local commit procedure** guarded by a read-only checker.

The plan was drafted from live repository evidence at branch `codex/project-harness`. The worktree contains substantial uncommitted user-owned changes covering the Terminal UI/Trader Registry proposal, its reviews, optimization directory restructuring, and state updates. Those changes are outside this plan's scope and must not be touched.

### 1.2 Current repository facts

- `operating-modes-v1` defines lifecycle stages (Proposed → Active → Completed) with manual transitions and a read-only checker, but provides no normative contract for when or how a local Git commit should be formed after completing a lifecycle product.
- The existing `Lifecycle reconciliation commit` field attempts to record a commit SHA after plan completion, but this creates a self-reference problem: the commit cannot contain its own SHA in its content.
- Current v1 plan metadata has `Current phase` supporting only `phase-0` through `phase-6`, with no structured representation for remediation cycles.
- There is no structured separation between activation recording and implementation start; both are evidenced by free prose.
- The `check-operating-modes.py` checker validates lifecycle field consistency but does not verify that durable checkpoints were actually formed, that staged changes are scoped, or that unrelated dirty files were preserved.
- The Terminal UI/Trader Registry plan (`v2-review-foldback-2026-07-20`) is currently Proposed with `approve/high` from `review-002` and next gate `activation-recording`. Multiple lifecycle products (OPT restructuring, reviews, proposals, state updates) coexist uncommitted in the same worktree.
- Four completed plans demonstrate the v1 lifecycle end-to-end but each required ad-hoc workaround for commit scoping, resulting in multi-step commit chains with metadata-only follow-up commits to record reconciliation SHAs.

### 1.3 Why Lane 3

This plan changes lifecycle governance policy, constrained format schemas, checker logic, CI workflow integration, and the normative contract in `docs/operating-modes.md`. Each of these is an explicit Lane 3 trigger per §3 of the operating-modes contract: lifecycle checker, constrained formats, transitions, governance policy.

### 1.4 Relationship to Terminal UI/Trader Registry plan

This governance plan is fully independent. It must not be folded into the Terminal UI plan because:

- It changes the rules under which all plans operate, not a specific product feature.
- The Terminal UI plan is already approved and awaiting activation under v1 rules.
- Mixing governance and product scope would make the Terminal UI plan's v2 approval invalid.
- Each plan requires its own independent design review, activation, implementation, implementation review, and closeout cycle.

### 1.5 `review-001` foldback closure map

| Review finding | V2 closure |
| --- | --- |
| Commit actor/authority/read-only contradiction | §§3.2–3.3 and §5.1 freeze one manual actor procedure, exact request inputs, exact authority grammar, and checker-only read behavior |
| 1 MB gate rejects live OPT evidence | §5.6 uses per-file classes plus aggregate cap and pins the actual 1,688,940-byte reference PNG as a positive fixture |
| Legacy trailer-less CI semantics | §6.4 and Phases 3–4 freeze exact `--legacy-tolerated` command and warn/fail exit policy |
| Live §8 numbering collision | §8.2 and Phases 1–2 preserve §§1–8 and append only new §§9–10 |
| V2 key mismatch/plan review-target leakage | §§7.2–7.3 retain every exact v1 key, use space-separated additions, keep `Review target commit` review-only, and retain `Implementation review` |
| Lifecycle checkpoint scopes too narrow | §4.1 defines minimum reconciliation and allowed optional sets for all eleven kinds using real plan/index/roadmap/state products |
| Phase/remediation ambiguity | §7.4 defines legal state combinations, entry/next gates, checkpoint kinds, blocker invariant, and index authority |
| Same-file ambiguity | §5.4 requires clean/absent paths at work-unit entry, exact blobs/full post-images, and forbids partial staging |
| Missing-checkpoint enforcement gap | §6.4 separates hard staged/postflight/v2-claim failures from advisory pre-v2 history |
| Over-broad `*token*` secret path | §5.6 replaces it with exact deny paths, added-line heuristics, placeholders, and false-positive fixtures |
| Bootstrap race and concurrent dirty surfaces | §§3.3, 5.4, Phase 0, and Phase 5 keep this full lifecycle on v1 and block until shared dirty manifest paths are separately resolved |

## 2. Objective And Success Criteria

### 2.1 Objective

Design and implement a repository-level durable checkpoint mechanism for manually executed, scoped local commits at well-defined lifecycle milestones, while maintaining strict separation of underlying work authority, lifecycle transition authority, durable checkpoint Git authority, and push/PR/merge/Pages/remote authority.

### 2.2 Success criteria

1. Exactly eleven checkpoint kinds are normatively defined, each with an explicit trigger condition, minimum reconciliation set, allowed optional path set, Git trailer contract, and post-commit invariants.
2. Exactly seven exclusion categories are normatively defined, with clear rationale for why each does not qualify for a durable checkpoint.
3. The four authority dimensions (underlying work, lifecycle transition, durable checkpoint Git, remote/publication) are formally separated with no implicit escalation path between them.
4. A new `operating-modes-v2` lifecycle schema is a literal strict superset of the live space-separated v1 keys and adds structured fields for implementation start evidence, current work unit, blocker evidence, multiple implementation reviews, checkpoint authority, expected checkpoint kind, and review target commits.
5. The self-reference problem is resolved: Git commit/trailers serve as current checkpoint evidence; reviews target prior checkpoint commits; completed lifecycle commits are identified by trailer, not by embedding their own SHA in their content.
6. A new read-only `check-durable-checkpoint.py` checker provides baseline/staged preflight, HEAD postflight, and repository audit modes; a human or coding agent remains the only commit actor.
7. The checker integrates into `.harness/config.json` and `.github/workflows/project-harness.yml` with the exact `--mode audit --legacy-tolerated` CI policy and without breaking existing CI jobs.
8. v1 completed plans remain frozen with no historical rewrite.
9. Plans that are Proposed or Active when this governance takes effect can migrate via a documented policy.
10. The governance plan itself operates under v1 rules throughout its own lifecycle, with plan-scoped standing local commit authority granted separately by the user.

### 2.3 Non-goals

- This plan does not implement an automated commit workflow engine, daemon, hook, background actor, or CI writer. The checkpoint checker is read-only.
- The term `auto-commit` in the historical filename/slug grants no authority and is not an operative synonym for unattended Git mutation.
- This plan does not retroactively rewrite v1 completed plans or fabricate historical checkpoints.
- This plan does not grant push, PR, merge, Pages, or remote authority.
- This plan does not modify the Data Update Mode publish gate or daily publish contract.
- This plan does not change runtime code, DB schema, market data, or frontend behavior.
- This plan does not implement, activate, or modify the Terminal UI/Trader Registry plan.

## 3. Authority Model

### 3.1 Four authority dimensions

| Dimension | What it authorizes | What it does NOT authorize |
| --- | --- | --- |
| **Underlying work authority** | Creating the deliverable (writing an OPT, drafting a plan, writing code, running a review) | Lifecycle state change, Git operations, remote operations |
| **Lifecycle transition authority** | Moving a plan between Proposed/Active/Completed, recording activation, starting implementation | Git operations, remote operations, creating deliverables |
| **Durable checkpoint local Git authority** | One scoped `git add` + `git commit` for exactly the files produced by the completed work unit | Lifecycle state change, push, PR, merge, Pages, branch operations, remote settings |
| **Remote/publication authority** | Push, PR, merge, Pages publish, branch protection, provider/broker, hosted verification | Creating deliverables, lifecycle state changes, local Git beyond the push scope |

### 3.2 Checkpoint authority rules

1. Durable checkpoint commit authority is a post-completion packaging right, not the authority source for producing the deliverable.
2. Each checkpoint permits one human or coding agent (the **commit actor**) to attempt exactly one scoped local `git add` + `git commit` procedure for the completed work unit. The actor may be different from the deliverable author or independent reviewer, but must not change their authorship or independence evidence.
3. The read-only checker never stages, unstages, commits, amends, resets, stashes, switches branches, or pushes. The actor supplies the checkpoint kind, subject, revision, work unit, outcome, authority reference, expected branch, baseline receipt, and explicit path manifest through `checkpoint-request-v1`.
4. A checkpoint commit does not authorize the next lifecycle action.
5. Design review `approve` ≠ activation.
6. Design review `revise` does not authorize a proposal revision by itself.
7. Activation ≠ implementation-start.
8. Implementation review `revise` does not authorize remediation by itself.
9. Implementation review `accept` does not authorize Completed migration by itself.
10. No checkpoint may push, create/merge a PR, publish to Pages, switch branches, access providers/brokers, or modify remote settings.
11. Data Update Mode continues to use its existing Publish Gate. Local acceptance does not grant commit authority.

### 3.3 Durable authority grammar and recording

`Tang-Authority` has exactly one accepted value form:

```text
user-instruction:<token>
```

`<token>` must match `^[a-z0-9][a-z0-9._/-]{0,127}$`. A chat paraphrase, plan approval, implementation instruction, passing check, or lifecycle verdict is not a durable checkpoint authority unless the user instruction explicitly grants local commit authority and the actor records its exact durable reference.

For `operating-modes-v2` plans, standing authority is recorded in the plan's constrained `Checkpoint authority`, `Checkpoint authority mode`, and `Checkpoint authority kinds` fields. The subject is the exact `Plan slug`. For OPT records, the same three keys are added to the OPT constrained header and the subject is the exact OPT slug. Rules:

- `Checkpoint authority: none` requires both companion fields to be `none`.
- `Checkpoint authority mode: one-shot` permits one successful checkpoint commit for that authority reference, subject, and one listed kind; a failed Git attempt may be retried only after a fresh full preflight while the authority remains unconsumed.
- `Checkpoint authority mode: standing` is valid only when the user instruction explicitly says it is standing, names the plan/OPT subject, and names the allowed kinds. It may be reused only for that subject and those kinds until revoked or the subject reaches Completed/Archived/Rejected/Terminated/Superseded.
- `Checkpoint authority kinds` is `none` or an ascending, comma-separated, duplicate-free list drawn from the eleven exact kinds, with no spaces.
- The baseline and staged preflights require the request authority to equal the constrained subject field. Postflight requires the commit trailer to equal the request. Audit fails on reuse of a one-shot reference or use outside the standing subject/kind set.

The current governance plan remains `operating-modes-v1`; any standing local commit authority for its own lifecycle must be separately and explicitly granted and recorded in v1 phase evidence. This proposal revision grants none.

## 4. Checkpoint Catalog

### 4.1 Qualifying checkpoints and real lifecycle scopes

The **minimum reconciliation set** must be inspected on every checkpoint of that kind and every changed member must be staged. The **allowed optional set** is the only additional path surface that may be staged when changed by the same work product. Unchanged reconciled files are evidenced but are not staged. Directory tokens below mean explicit file paths expanded in the request; Git directory arguments and globs remain forbidden.

| # | Kind / allowed outcome | Trigger | Minimum reconciliation set | Allowed optional staged set |
| --- | --- | --- | --- | --- |
| 1 | `opt-record` / `complete` | Formal OPT record generated | `docs/optimization/<opt>/<opt>.md`; `docs/optimization/index.md` | Explicit images under `docs/optimization/<opt>/screenshots/`; `PROGRESS.md` and `HANDOFF.md` only when the current resume point changes |
| 2 | `plan-proposal` / `complete` | OPT or explicit request becomes a Proposed plan | Proposed plan; proposed index; reviews index; roadmap; source OPT record/index when promoted | `PROGRESS.md`; `HANDOFF.md`; explicit proposal evidence files |
| 3 | `design-review` / `approve|revise|reject` | Independent design review finalized | Review artifact; plan metadata; proposed index; reviews index | Roadmap and state files when focus/next gate changes; review evidence files |
| 4 | `proposal-revision` / `complete` | New stable plan revision folds back review | Revised plan; proposed index; reviews index; roadmap | Source OPT record/index when scope changes; `PROGRESS.md`; `HANDOFF.md`; revision evidence |
| 5 | `activation-recording` / `complete` | Explicit activation; one plan moves Proposed → Active | Plan delete/create pair; proposed, active, and reviews indexes; roadmap; `PROGRESS.md`; `HANDOFF.md` | Activation evidence under the plan review directory |
| 6 | `implementation-start` / `complete` | Separate implementation-start instruction recorded | Active plan; active index; roadmap; `PROGRESS.md`; `HANDOFF.md`; work-unit baseline evidence | Explicit Phase 0 fixture/evidence files created by the start product |
| 7 | `phase-exit` / `complete` | One primary `phase-N` exit gate passes | Active plan; active index; roadmap; `PROGRESS.md`; `HANDOFF.md`; phase evidence; frozen phase deliverables | Plan-scoped test fixtures and generated evidence explicitly listed by the active phase manifest |
| 8 | `phase-blocked` / `blocked` | Primary phase or remediation is formally blocked | Active plan; active index; `PROGRESS.md`; `HANDOFF.md`; blocker evidence with residual state/recovery | Roadmap when lifecycle prose changes; diagnostic evidence explicitly listed by the work-unit manifest |
| 9 | `implementation-review` / `accept|revise|reject` | Independent implementation review finalized | Review artifact; plan metadata; active index; reviews index; `PROGRESS.md`; `HANDOFF.md` | Review packet/evidence; roadmap when next gate text changes |
| 10 | `remediation-complete` / `complete` | One `remediation-N` exit gate passes | Active plan; active index; roadmap; `PROGRESS.md`; `HANDOFF.md`; remediation evidence; frozen remediation deliverables | Plan-scoped regression fixtures/evidence explicitly listed by the remediation manifest |
| 11 | `completed-migration` / `complete` | Accepted implementation moves Active → Completed | Plan delete/create pair; active, completed, and reviews indexes; roadmap; `PROGRESS.md`; `HANDOFF.md` | Final closeout evidence and accepted implementation review packet |

For renamed/moved plans, the request lists the deleted and created file paths separately. A required derived surface that is byte-identical is recorded as inspected, not forced into the commit. Any changed required surface omitted from staging, or any staged path outside the required/allowed sets, fails closed.

### 4.2 Explicit exclusions

| # | Exclusion | Rationale |
| --- | --- | --- |
| 1 | Mid-phase work | Incomplete deliverable; checkpoint would freeze partial state |
| 2 | Transient test failure | Noise; the failure is not a formal lifecycle product |
| 3 | Active retry or diagnostic session | Ephemeral state that may be superseded |
| 4 | Draft review/plan/OPT | Not formally generated; content may change before formal generation |
| 5 | Single-line PROGRESS/HANDOFF edit | Derived surface edit without underlying lifecycle product |
| 6 | Lifecycle/index/state not yet synchronized | Inconsistent state would be committed |
| 7 | Unclear scope ownership or piggyback state | Cannot form a clean scoped commit without touching unrelated changes |

## 5. Scope And Fail-Closed Design

### 5.1 Single execution procedure and inputs

There is one execution model: an authorized human or coding agent performs the Git mutation; the checker is read-only. The actor must follow this exact order:

1. At work-unit entry, prepare explicit repository-relative paths and run baseline preflight while the index is empty and every manifest path is clean or absent-as-declared. At this step only, `post_sha256` is `null` for every entry. Capture the checker's JSON stdout in an OS temporary file outside the repository.
2. Complete the separately authorized work. Prepare the staged `checkpoint-request-v1` with the same immutable metadata/path/operation/baseline fields and fill expected post-image hashes (`null` remains only for deletes). The staged preflight rejects any other change from the baseline request recorded in the receipt.
3. Run `git add -- <path-1> ... <path-N>` with every path enumerated literally. Run staged preflight against the baseline receipt and request.
4. If staged preflight passes, run one normal `git commit` with the required trailers. Hooks remain enabled.
5. Run postflight against the new `HEAD`, baseline receipt, and request. A failure stops the lifecycle; it never triggers amend/reset/retry automatically.

`checkpoint-request-v1` is a JSON object supplied through `--request <path>` with exactly these keys: `schema_version`, `kind`, `subject`, `revision`, `work_unit`, `outcome`, `authority`, `expected_branch`, `baseline_head`, and `paths`. `schema_version` is exact `checkpoint-request-v1`. `paths` is a lexically sorted, duplicate-free array of objects with exact keys `path`, `operation`, `baseline_blob`, and `post_sha256`; operations are `create|modify|delete`, deletes use `post_sha256: null`, creates use `baseline_blob: null`, and all other populated hashes are lowercase 40-hex Git blob IDs or 64-hex SHA-256 values as applicable. Paths must be repository-relative files with `/` separators and may not be absolute, contain `..`, name `.git`, use a glob, or name a directory. Rename is represented by one delete plus one create. The temporary request/receipt files are never placed under the repository and are never part of the staged manifest.

Exact checker carriers are:

```text
python3 scripts/check-durable-checkpoint.py --root . --mode preflight --step baseline --request <request.json>
python3 scripts/check-durable-checkpoint.py --root . --mode preflight --step staged --request <request.json> --baseline-receipt <receipt.json>
python3 scripts/check-durable-checkpoint.py --root . --mode postflight --request <request.json> --baseline-receipt <receipt.json> --commit HEAD
python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated
```

Before the actor stages anything, baseline preflight captures and verifies:

- Current branch name (must match the expected working branch)
- HEAD commit SHA
- Index state (`git diff --cached` must be empty unless the checkpoint itself staged files)
- Dirty baseline (`git status --porcelain`) snapshot for post-commit comparison

### 5.2 Pre-existing staged changes

If `git diff --cached` is non-empty before the checkpoint stages its files, the checkpoint MUST abort. Pre-existing staged changes indicate another operation is in progress. No silent `git reset` or `git stash` is permitted.

### 5.3 Unrelated dirty files

Unrelated dirty files outside the request may remain in the worktree. The actor and checker MUST NOT stage, modify, revert, stash, or otherwise touch them. The baseline receipt records status code plus SHA-256/content absence for each unrelated path; postflight requires the same path/status/content tuple. A changed unrelated path is a hard failure even when `git status` still shows the same two-letter code.

### 5.4 Same-file ambiguity

Same-file ownership uses a deliberately strict, decidable rule:

1. At work-unit entry, every `modify`/`delete` request path must be clean in both index and worktree at `baseline_head`; every `create` path must be absent. If not, baseline preflight aborts. There is no expected-blob override for a pre-dirty path.
2. `baseline_head` and expected branch must remain unchanged until commit. For `modify`/`delete`, the request's `baseline_blob` must equal `git rev-parse <baseline_head>:<path>`; for `create`, it must be `null`.
3. At staged preflight, the worktree/index operation and complete post-image must match `operation` and `post_sha256`. A path changed outside the request, a requested path with a different full post-image, or a path that became dirty before its declared work-unit start aborts.
4. `git add -p`, hunk splitting, patch reconstruction, and adopting a pre-dirty shared file are prohibited.

This plan therefore requires shared dirty lifecycle paths from the Terminal UI and optimization products to be resolved by their owners under separate authority before this governance plan can start implementation. It may wait; it may not stash, absorb, or split those edits.

### 5.5 Exact path staging

All staging MUST use explicit file paths after `git add --`. `git add .`, `git add -A`, `git add --all`, pathspec magic, globs, directory arguments, `git commit -a`, and implicit staging by GUI clients are prohibited.

### 5.6 Staged diff verification

After staging and before commit, the checkpoint mechanism must verify:

- `git diff --cached --check` passes (no trailing whitespace or conflict markers)
- No denied credential path or staged added-line content heuristic match defined below
- No generated artifacts (`frontend/dist/`, `frontend/public/reviews/`, `node_modules/`, `__pycache__/`, `*.pyc`)
- Every staged path equals one request entry; no file-count tolerance is allowed
- Each staged file and the aggregate request satisfy the kind-aware size table below

Size gates are per-file plus aggregate, using exact byte counts:

| Class | Allowed paths | Per-file maximum | Aggregate treatment |
| --- | --- | ---: | --- |
| Governance text/source | Markdown, JSON, YAML, Python, shell, JS/JSX/CSS and other UTF-8 text in an allowed checkpoint scope | 1,048,576 bytes | Counts toward 26,214,400-byte checkpoint maximum |
| OPT screenshot evidence | `docs/optimization/<opt>/screenshots/*.(png|jpg|jpeg|webp)` for `opt-record` or `plan-proposal` only | 5,242,880 bytes | Counts toward the same aggregate maximum |
| Other binary | Any other binary path | denied | denied |

The live reference `docs/optimization/2026-07-19-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png` is a required positive fixture at 1,688,940 bytes and SHA-256 `57c34ea70bf7c6cab2c983b8feaedb6ad9be6f23fc02262ac7c97a48b156d3c5`. Fixtures also require rejection at 5,242,881 screenshot bytes, at 1,048,577 text bytes, and at 26,214,401 aggregate bytes.

Denied credential paths are: basename `.env`; basename beginning `.env.` except exact `.env.example`; extensions `.key`, `.pem`, `.p12`, `.pfx`; any path under `.ssh/`; and basenames `credentials.json`, `secrets.json`, or `secrets.yaml`. Added text lines are scanned for PEM private-key headers and non-placeholder assignments to case-insensitive `api_key`, `access_token`, `client_secret`, `password`, or `private_key`. Exact placeholders consisting only of `${...}`, `<...>`, `example`, `placeholder`, or `redacted` are allowed. Harmless filenames containing `token` and governance text such as `gate-token` are not denied; fixtures pin both false-positive cases.

### 5.7 Repository state guards

The checkpoint MUST abort without staging or committing if any of these conditions is detected:

- Detached HEAD
- Active merge (`MERGE_HEAD` exists)
- Active rebase (`.git/rebase-merge/` or `.git/rebase-apply/` exists)
- Active cherry-pick (`CHERRY_PICK_HEAD` exists)
- HEAD/branch drift (HEAD has moved since baseline capture)
- Branch name mismatch

### 5.8 Commit hook handling

The checkpoint MUST respect all configured Git hooks. `--no-verify` is prohibited. If a pre-commit or commit-msg hook fails, the checkpoint MUST abort and report the hook failure. No automatic retry after hook failure.

### 5.9 Prohibited checkpoint operations

The following operations are never authorized as part of the scoped local commit procedure:

- `git commit --amend`
- `git reset` (any form)
- `git stash` (any form)
- `git checkout` / `git switch` (branch operations)
- `git rebase` / `git merge` / `git cherry-pick`
- `git push` (any form)

### 5.10 Blocked checkpoint handling

When a checkpoint is formally blocked (e.g., `phase-blocked`), the blocker evidence, residual state, and recovery steps may be committed as a checkpoint. However, the commit message and trailers MUST accurately reflect the `blocked` outcome. A blocked checkpoint MUST NOT represent itself as a successful verification pass.

### 5.11 Commit failure handling

If `git commit` fails for any reason (hook failure, empty diff, lock contention, filesystem error), the actor MUST:

1. Report the exact failure
2. Unstage only the explicit checkpoint paths using `git restore --staged -- <literal paths>`; the empty pre-checkpoint index is then re-verified
3. NOT record the checkpoint as formed in any lifecycle document
4. NOT proceed to the next lifecycle action

## 6. Checkpoint Evidence: Git Trailers

### 6.1 Standard trailer format

Every durable checkpoint commit MUST include the following Git trailers:

```text
Tang-Checkpoint: <checkpoint-kind>
Tang-Subject: <plan-or-opt-slug>
Tang-Revision: <revision-or-none>
Tang-Work-Unit: <phase-N|remediation-N|none>
Tang-Outcome: <complete|blocked|approve|revise|accept|reject>
Tang-Authority: <durable-authority-reference>
Tang-Remote-Authority: none
```

`Tang-Authority` must match §3.3 exactly and must equal the request/subject metadata value. The actor supplies these trailers through the normal `git commit` message editor or repeated `-m` arguments; the checker does not construct the message or invoke Git writes.

### 6.2 Self-reference resolution

The self-reference problem (a commit cannot contain its own SHA) is resolved by the following design:

1. **Current checkpoint**: The Git commit object itself, identified by its trailers, IS the checkpoint evidence. No document needs to embed the commit's own SHA.
2. **Review targets**: A review references the prior checkpoint commit by its SHA in `Review target commit` metadata. This is possible because the review is authored after the checkpoint commit exists.
3. **Completed lifecycle**: The Completed transition commit is identified by its `Tang-Checkpoint: completed-migration` trailer. No content within the commit needs to contain the commit's own SHA.
4. **Postflight verification**: The `check-durable-checkpoint.py` audit mode reads `git log` trailers to reconstruct the checkpoint chain. No lifecycle document needs to embed circular references.
5. **v1 historical plans**: Remain frozen. The existing `Lifecycle reconciliation commit` field with its metadata-only follow-up pattern is a v1 artifact. No backfill or historical rewrite occurs.

### 6.3 Trailer validation

The checkpoint checker validates trailers in audit mode:

- All seven trailers are present with non-empty values
- `Tang-Checkpoint` matches one of the eleven defined kinds
- `Tang-Subject` matches a known plan or OPT slug
- `Tang-Outcome` is consistent with the checkpoint kind (e.g., `design-review` permits `approve`/`revise`/`reject`)
- `Tang-Remote-Authority` is always `none` (remote authority is never granted by a checkpoint)
- No duplicate trailers in a single commit

### 6.4 Enforcement modes and legacy history

- **Staged preflight** is a hard gate before every authorized checkpoint attempt. Any request, authority, scope, image, size, secret, generated-output, repository-state, or baseline mismatch exits non-zero.
- **Postflight** is a hard gate immediately after a successful commit. Missing/invalid trailers, unexpected commit paths, unrelated-dirty drift, branch/HEAD mismatch, or request mismatch exits non-zero and stops lifecycle progression. No automatic rollback or amend follows.
- **Repository audit with `--legacy-tolerated`** exits zero for trailer-less commits that predate a subject's `operating-modes-v2` opt-in and may report them as warnings. It exits non-zero for any commit containing a partial/malformed/duplicate `Tang-*` trailer set, any invalid one-shot/standing authority use, or any missing/mismatched latest checkpoint claimed by a v2 subject's `Expected checkpoint kind`.
- Historical completeness is explicitly out of scope. The audit does not require trailers on all old commits and does not infer that arbitrary code commits were lifecycle products.
- For a v2 Proposed plan, a non-`none` `Expected checkpoint kind` must resolve to the latest matching subject/revision checkpoint. For an Active plan, `Phase state: complete`, `Work state: complete`, an implementation review entry, or a lifecycle transition claim makes the corresponding expected checkpoint mandatory. If the plan has not opted into v2 or all checkpoint claim fields are `none`, missing history remains advisory.

The exact governed/PR carrier is:

```text
python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated
```

It is added verbatim to `.harness/config.json` and as the direct `run` scalar in the existing `Harness structure` job immediately after `python3 -m unittest scripts.tests.test_operating_modes`. CI therefore remains green on pre-v2 trailer-less history while failing malformed present trailers and post-opt-in v2 checkpoint gaps.

## 7. Lifecycle Schema Evaluation: operating-modes-v2

### 7.1 Current v1 gaps

| Gap | Impact | Resolution needed |
| --- | --- | --- |
| `Current phase` only supports `phase-0` through `phase-6` | Cannot represent remediation cycles cleanly | Keep it authoritative for primary phase; add a nested `Current work unit` |
| No structured separation between activation and implementation-start | Both are free prose in v1 | Add `Implementation start evidence` field |
| No `Current work unit` concept | Phase and remediation are conflated | Add `Current work unit` field |
| No structured `Blocker evidence` | Blocked phases use free prose | Add `Blocker evidence` field |
| Single `Implementation review` field | Cannot represent multiple review rounds | Retain it for v1 compatibility and add `Implementation reviews` plus `Latest implementation verdict` |
| No `Review target commit` in reviews | Reviews cannot precisely reference what they reviewed | Add to review metadata |
| `Lifecycle reconciliation commit` requires metadata-only follow-up | Self-reference problem | Retain the v1 key but require `none` in v2; identify completed migration by trailer |
| Checker does not verify durable checkpoints | Lifecycle can pass with no checkpoint evidence | New checker module |

### 7.2 Exact v2 plan metadata

V2 uses the exact live space-separated titles. It retains every current `PLAN_KEYS` item unchanged and appends the keys below; no hyphenated alias is accepted. The complete required order is:

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

`Implementation review` is not renamed or removed. It remains `none` through revise/reject rounds and becomes the compatibility pointer to the accepted review only when `Latest implementation verdict: accept`; `Implementation reviews` records every structured round. `Verified implementation commit` then equals the accepted review's `Review target commit`. `Lifecycle reconciliation commit` is retained solely so v2 is a strict key superset and must remain `none`; the completed-migration trailer is the non-circular closeout evidence. `Review target commit` is never a plan key.

### 7.3 Proposed v2 review metadata extensions

```text
# Additional final key for every v2 review
- Review target commit: `<40-hex-commit>`
```

V1 reviews keep the existing nine exact `REVIEW_KEYS`. A review of a v2 plan requires those same nine keys, in the same order, followed by `Review target commit`; `none` is not allowed. A design review targets the prior `plan-proposal` or `proposal-revision` commit. An implementation review targets the prior `phase-exit` or `remediation-complete` implementation commit. The checker verifies that the target commit is an ancestor of the review checkpoint and carries the expected subject/revision/kind trailers.

### 7.4 Work-unit state machine

`Current phase` / `Phase state` remain authoritative for the Active index row and primary phase progression. `Current work unit` / `Work state` describe the currently executable unit and may temporarily name a remediation while `Current phase` remains `phase-6`.

| Lifecycle point | Current phase / Phase state | Current work unit / Work state | Required evidence / next-gate prefix |
| --- | --- | --- | --- |
| Proposed | `none / none` | `none / none` | implementation start and blocker fields `none`; Proposed gate rules unchanged |
| Activated, not started | `phase-0 / not-started` | `none / none` | implementation start `none`; `phase-0-start` |
| Primary phase ready | `phase-N / not-started` | `none / none` | implementation start non-`none`; `phase-N-start` |
| Primary phase running | `phase-N / in-progress` | `phase-N / in-progress` | blocker `none`; `phase-N-exit` |
| Primary phase blocked | `phase-N / blocked` | `phase-N / blocked` | blocker non-`none`; `phase-N-recovery` |
| Primary phase exit recorded, next phase exists | `phase-(N+1) / not-started` | `none / none` | latest expected checkpoint `phase-exit`; `phase-(N+1)-start` |
| Implementation awaiting review | `phase-6 / complete` | `none / none` | blocker `none`; `implementation-review` |
| Review revise, remediation ready | `phase-6 / in-progress` | `remediation-N / not-started` | latest verdict `revise`; `remediation-N-start` |
| Remediation running/blocked | `phase-6 / in-progress|blocked` | `remediation-N / in-progress|blocked` | blocked requires evidence; `remediation-N-exit|remediation-N-recovery` |
| Remediation complete, awaiting re-review | `phase-6 / in-progress` | `remediation-N / complete` | expected checkpoint `remediation-complete`; `implementation-review` |
| Accepted, awaiting closeout | `phase-6 / complete` | `none / none` | latest verdict `accept`; `completed-migration` |

`phase-exit` is legal only for a primary `phase-N`; `remediation-complete` is legal only for `remediation-N`. Remediation numbering starts at 1 and increments without gaps after each `revise`. `Blocker evidence` is non-`none` iff either authoritative state is `blocked`. State-block and index formats remain v1-shaped and derive only the primary phase fields.

`Phase entry gate` remains required and records admission to the current executable unit: activation uses `activation:user-instruction:<token>`; Phase 0 implementation start uses `user-instruction:<token>`; later primary phases use `phase-(N-1)-exit`; remediation uses `remediation-N:user-instruction:<token>` and additionally requires the immediately preceding structured implementation-review verdict `revise`. It stays fixed through that unit until the next primary/remediation unit is admitted. A `revise` verdict alone never supplies the remediation user-instruction token.

### 7.5 v1 compatibility

- v2 is a literal strict key superset of v1. All seventeen live v1 plan keys remain required and retain their exact names.
- v1 Completed plans are not modified. Their `Lifecycle reconciliation commit` pattern is a historical artifact.
- The checker supports both schema versions, determined by the `Lifecycle schema` field value.
- Plans Proposed or Active under v1 when v2 takes effect may migrate via a documented transition policy (Phase 5).

## 8. Change Manifest

### 8.1 Files to create

| File | Purpose |
| --- | --- |
| `docs/decisions/2026-07-XX-durable-checkpoint-governance.md` | ADR ratifying the durable checkpoint and v2 schema decisions |
| `scripts/check-durable-checkpoint.py` | Read-only checkpoint checker with preflight/postflight/audit modes |
| `scripts/tests/test_durable_checkpoint.py` | Adversarial fixtures for the checkpoint checker |

### 8.2 Files to modify

| File | Modification scope |
| --- | --- |
| `docs/operating-modes.md` | Preserve existing §§1–8; append §9 Durable Checkpoint Contract and §10 v2 Schema/State Machine; update schema version header only when both are implemented |
| `docs/README.md` | Add checkpoint documentation link if README routing exists |
| `docs/decisions/index.md` | Add durable checkpoint ADR entry |
| `docs/optimization/SOP.md` | Reference checkpoint kind `opt-record` |
| `docs/optimization/record-template.md` | Note checkpoint eligibility |
| `docs/exec-plans/plan-template.md` | Add v2 fields to template metadata |
| `docs/exec-plans/reviews/review-template.md` | Add exact `Review target commit` field for v2 reviews |
| `docs/exec-plans/proposed/index.md` | Schema-compatible if needed |
| `docs/exec-plans/active/index.md` | Schema-compatible if needed |
| `docs/exec-plans/completed/index.md` | Schema-compatible if needed |
| `docs/exec-plans/reviews/index.md` | Schema-compatible if needed |
| `docs/exec-plans/roadmap.md` | Schema-compatible if needed |
| `scripts/check-operating-modes.py` | Add v2 schema support; recognize v2 fields; support dual-schema validation |
| `scripts/tests/test_operating_modes.py` | Add v2 fixtures alongside existing v1 fixtures |
| `scripts/check-project-harness.py` | Compose `check-durable-checkpoint.py` in governed profile |
| `.harness/config.json` | Add checkpoint checker to verification commands |
| `.github/workflows/project-harness.yml` | Add checkpoint checker step to harness job |
| `AGENTS.md` | Reference durable checkpoint contract in commit guidelines |
| `INSTRUCTIONS.md` | Add checkpoint checker to verification commands section |

The live `docs/operating-modes.md` already ends at `## 8. Data Update Verification Carrier Map`. Implementation MUST append new `## 9. Durable Checkpoint Contract` after the complete §8 table, then append `## 10. operating-modes-v2 Schema And Work-Unit State Machine`. Existing §§1–8 are not renumbered, reused, or overwritten. Necessary cross-references inside §§4, 5, and 7 may be amended explicitly, but their headings retain their current numbers.

### 8.3 Files NOT modified

- Runtime code (`backend/app/`, `frontend/src/`)
- Database (`data/sqlite/`)
- Market data (`data/seed/`)
- Strategies (`strategies/`)
- Content (`content/`)
- Daily publish runbook
- Pages publisher workflow
- The Terminal UI/Trader Registry plan or its reviews
- v1 Completed plan documents

## 9. Phases

### Phase 0 — Baseline, Dirty Ownership, And Scope Freeze

**Entry gate**: Plan is Active with `phase-0:not-started`; user has issued an implementation-start instruction; the current branch, HEAD, and worktree state are captured; every shared lifecycle/governance path in this plan's manifest is clean or absent after the Terminal UI/optimization products have been separately resolved by their owners.

**Work**:

1. Capture and record: branch name, HEAD SHA, `git status --porcelain` full output, list of all staged files (must be empty or documented).
2. Identify and document every dirty file in the worktree. Classify each as: (a) owned by this plan's scope, (b) owned by the Terminal UI plan, (c) owned by other user changes, (d) shared/ambiguous.
3. Freeze the exact file manifest for this plan (§8.1 and §8.2). Record SHA-256 of every file that will be modified.
4. Verify all existing checkers pass on the current worktree state.
5. Apply the strict same-file rule from §5.4. Any pre-dirty manifest path is a blocking conflict. Do not use a disjoint-hunk protocol, `git add -p`, stash, reset, or absorb the change. Resume only after the owning product has been resolved under separate authority and a fresh baseline proves the path clean.

**File manifest**:
- `docs/exec-plans/reviews/<plan-slug>/evidence/phase-0-baseline.md`

**Verification**:
- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 scripts/check-operating-modes.py --root .`
- `python3 scripts/check-startup-doc-budget.py`
- `git diff --check`
- All dirty file classifications recorded with SHA-256 hashes

**Exit gate**: Baseline captured, manifest frozen, all file ownerships documented, every manifest path clean/absent at work-unit entry, unrelated dirty tuples frozen, and all existing checkers pass.

**Bootstrap v1 local commit boundary**: Phase 0 evidence file only, and only if the user has separately granted this governance plan local commit authority. It is not a v2 `phase-exit` and its absence is not a v2 audit failure.
**Authority does NOT extend to**: Implementation of any subsequent phase, Git operations beyond this phase's evidence commit, any Terminal UI plan files, any runtime/data files.

### Phase 1 — Durable Checkpoint Normative Contract, ADR, Router, And Templates

**Entry gate**: Phase 0 complete; baseline and manifest frozen.

**Work**:

1. Append `## 9. Durable Checkpoint Contract` after the existing complete §8 in `docs/operating-modes.md`. Do not renumber or reuse §§1–8. The new section covers:
   - Checkpoint catalog (§4 of this plan)
   - Exclusion list (§4.2)
   - Scope and fail-closed rules (§5)
   - Git trailer format (§6)
   - Self-reference resolution (§6.2)
   - Authority model (§3)
2. Write the ADR `docs/decisions/2026-07-XX-durable-checkpoint-governance.md` ratifying the design decisions.
3. Update `docs/decisions/index.md` with the new ADR entry.
4. Update `docs/optimization/SOP.md` to reference the `opt-record` checkpoint kind.
5. Update `docs/optimization/record-template.md` to note checkpoint eligibility criteria.
6. Update `docs/exec-plans/plan-template.md` to include the exact space-separated v2 metadata fields while retaining all v1 keys.
7. Update `docs/exec-plans/reviews/review-template.md` to include the exact `Review target commit` field for v2 reviews.
8. Update `AGENTS.md` commit guidelines to reference durable checkpoint contract.
9. Update `INSTRUCTIONS.md` verification commands to include the checkpoint checker.

**File manifest**:
- `docs/operating-modes.md` (add checkpoint contract sections)
- `docs/decisions/2026-07-XX-durable-checkpoint-governance.md` (new)
- `docs/decisions/index.md`
- `docs/optimization/SOP.md`
- `docs/optimization/record-template.md`
- `docs/exec-plans/plan-template.md`
- `docs/exec-plans/reviews/review-template.md`
- `AGENTS.md`
- `INSTRUCTIONS.md`
- `docs/exec-plans/reviews/<plan-slug>/evidence/phase-1-contract-and-adr.md`

**Verification**:
- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 scripts/check-operating-modes.py --root .`
- `python3 scripts/check-startup-doc-budget.py`
- `git diff --check`
- Manual verification that the contract text in operating-modes.md is consistent with this plan
- Manual verification that ADR correctly captures all design decisions

**Exit gate**: Exact §9 contract text is normative, the ADR is ratified, templates use the exact key grammar, the live 1,688,940-byte OPT reference passes the specified size class, and all existing checkers pass.

**Bootstrap v1 local commit boundary**: All Phase 1 deliverables listed above, only under separately granted v1 local commit authority; no `Tang-Checkpoint` trailer is treated as governance evidence for this plan.
**Authority does NOT extend to**: Checker implementation, CI integration, v2 schema enforcement, any file outside the manifest.

### Phase 2 — operating-modes-v2 Lifecycle/Review Schema

**Entry gate**: Phase 1 complete; normative contract text exists in operating-modes.md.

**Work**:

1. Append `## 10. operating-modes-v2 Schema And Work-Unit State Machine` after §9 and add only the explicit cross-references needed in existing §5/§7.
2. Define the full v2 `PLAN_KEYS` tuple as all seventeen live v1 keys plus the ten exact space-separated additions in §7.2; no key is removed, renamed, or hyphenated.
3. Add the v2 review metadata extension `Review target commit` as the tenth and final exact key. Never add it to plan metadata.
4. Define dual-schema validation by exact `Lifecycle schema`, including the compatibility-pointer rules for `Implementation review`, `Verified implementation commit`, and `Lifecycle reconciliation commit`.
5. Implement the §7.4 primary-phase/remediation state machine, gate prefixes, blocker iff-rule, sequential remediation numbering, and Active-index derivation.
6. Update `scripts/check-operating-modes.py` to support both exact schemas without changing v1 acceptance.
7. Add v2 positive/adversarial fixtures to `scripts/tests/test_operating_modes.py`, including every legal state row and invalid cross-product combinations.

**File manifest**:
- `docs/operating-modes.md` (v2 schema sections)
- `scripts/check-operating-modes.py`
- `scripts/tests/test_operating_modes.py`
- `docs/exec-plans/reviews/<plan-slug>/evidence/phase-2-v2-schema.md`

**Verification**:
- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 scripts/check-operating-modes.py --root .`
- `python3 -m unittest scripts.tests.test_operating_modes`
- `python3 scripts/check-startup-doc-budget.py`
- `git diff --check`
- All existing v1 fixtures continue to pass
- New v2 fixtures validate v2 field invariants
- Dual-schema detection works correctly

**Exit gate**: Exact v2 superset and work-unit state machine are normative and enforced; all existing v1 fixtures remain unchanged/green; v2 review target commits and authority fields fail closed; new v2 tests pass.

**Bootstrap v1 local commit boundary**: All Phase 2 deliverables listed above, only under separately granted v1 local commit authority.
**Authority does NOT extend to**: Checkpoint checker implementation, CI integration, migration of existing plans.

### Phase 3 — Checkpoint Preflight/Postflight Checker And Adversarial Fixtures

**Entry gate**: Phase 2 complete; v2 schema validated.

**Work**:

1. Create `scripts/check-durable-checkpoint.py` with three modes and the exact CLI in §5.1:
   - **Preflight**: `--step baseline` emits the read-only baseline receipt; `--step staged` validates the exact staged request after the actor stages literal paths. Both check branch, HEAD, index rules, dirty tuples, kind scopes, authority, size/secret/generated rules, same-file algorithm, and repository guards.
   - **Postflight**: After a commit, validates that trailers are correct, the committed diff matches the manifest, unrelated dirty files are unchanged, no secrets/credentials/generated artifacts entered the commit, and the commit is on the expected branch. Read-only.
   - **Audit**: Scans `git log` trailers, reconstructs checkpoint chains, validates authority use and v2 expected-kind claims, warns on pre-v2 trailer-less history, and fails only under §6.4.
2. The checker MUST be read-only. It MUST NOT stage files, create commits, modify lifecycle documents, or perform any write operation.
3. Create `scripts/tests/test_durable_checkpoint.py` with adversarial fixtures covering:
   - Pre-existing staged changes → abort
   - Detached HEAD → abort
   - Active merge/rebase/cherry-pick → abort
   - Pre-dirty requested modify/delete and pre-existing create path → abort
   - Baseline blob, complete post-image, operation, branch, or HEAD mismatch → abort
   - Secrets in staged diff → abort
   - Generated artifacts in staged diff → abort
   - Exact live 1,688,940-byte OPT reference screenshot → pass
   - 5,242,881-byte screenshot, 1,048,577-byte text file, or 26,214,401-byte aggregate → abort
   - Harmless `token` filename and governance `gate-token` prose → pass
   - Denied credential path, PEM header, or non-placeholder secret assignment → abort
   - Valid checkpoint with correct trailers → pass
   - Missing expected v2 trailer → fail; pre-v2 trailer-less history under `--legacy-tolerated` → warn/exit 0
   - Partial/malformed present trailer set anywhere in history → fail
   - Invalid checkpoint kind → fail
   - Mismatched outcome for checkpoint kind → fail
   - Unrelated dirty files unchanged after commit → pass
   - Unrelated dirty files changed after commit → fail
   - HEAD drift between baseline and commit → abort
   - One-shot authority reuse or standing authority subject/kind escape → fail

**File manifest**:
- `scripts/check-durable-checkpoint.py` (new)
- `scripts/tests/test_durable_checkpoint.py` (new)
- `docs/exec-plans/reviews/<plan-slug>/evidence/phase-3-checker.md`

**Verification**:
- `python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated` (exit 0 on current pre-v2 trailer-less history; non-zero only for §6.4 hard failures)
- `python3 -m unittest scripts.tests.test_durable_checkpoint`
- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 scripts/check-operating-modes.py --root .`
- `python3 scripts/check-startup-doc-budget.py`
- `git diff --check`
- All adversarial fixtures pass

**Exit gate**: The read-only checker implements the exact request/receipt grammar and three modes; legacy audit exit semantics, real OPT size evidence, authority reuse, scope matrices, same-file decisions, and valid/invalid trailer combinations are fixture-pinned; all existing checkers continue to pass.

**Bootstrap v1 local commit boundary**: All Phase 3 deliverables listed above, only under separately granted v1 local commit authority.
**Authority does NOT extend to**: CI integration, harness configuration, migration of existing plans.

### Phase 4 — Harness/Config/GitHub Workflow Integration

**Entry gate**: Phase 3 complete; checkpoint checker validated.

**Work**:

1. Add exact command `python3 scripts/check-durable-checkpoint.py --root . --mode audit --legacy-tolerated` to `.harness/config.json` verification commands.
2. Add the same exact direct `run` scalar to `.github/workflows/project-harness.yml` in the existing `Harness structure` job, immediately after `python3 -m unittest scripts.tests.test_operating_modes`.
3. Update `scripts/check-project-harness.py` to compose `check-durable-checkpoint.py` in the governed profile.
4. Verify that the existing three CI job names remain unchanged.
5. Verify that the Pages publisher workflow is not modified.

**File manifest**:
- `.harness/config.json`
- `.github/workflows/project-harness.yml`
- `scripts/check-project-harness.py`
- `docs/exec-plans/reviews/<plan-slug>/evidence/phase-4-integration.md`

**Verification**:
- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 scripts/check-operating-modes.py --root .`
- `python3 -m unittest scripts.tests.test_operating_modes`
- `python3 -m unittest scripts.tests.test_durable_checkpoint`
- `python3 scripts/check-startup-doc-budget.py`
- `git diff --check`
- CI workflow diff shows only the added step; no job name, runner, or trigger changes
- Pages publisher workflow SHA-256 unchanged

**Exit gate**: The exact legacy-tolerated audit command runs in configured governed verification and CI; current trailer-less history exits zero; malformed-present and v2-gap fixtures exit non-zero; all existing checks continue to pass and CI job structure is preserved.

**Bootstrap v1 local commit boundary**: All Phase 4 deliverables listed above, only under separately granted v1 local commit authority.
**Authority does NOT extend to**: Migration of existing plans, schema enforcement beyond validation.

### Phase 5 — v1 Compatibility, Current Proposed/Active Migration Policy, And Bootstrap Policy

**Entry gate**: Phase 4 complete; checkpoint checker integrated into harness and CI.

**Work**:

1. Define and document the migration policy for plans that are Proposed or Active under v1 when v2 takes effect:
   - Proposed v1 plans may be migrated to v2 schema at their next revision or activation.
   - Active v1 plans may be migrated to v2 schema at their next phase transition.
   - Migration retains all v1 keys and adds the new v2 fields. Authority fields default to `none`; state fields are derived from the exact state machine rather than blindly defaulted when work is already in progress.
   - The checker accepts both `operating-modes-v1` and `operating-modes-v2` schema values.
2. Define the bootstrap policy for this governance plan itself:
   - This plan operates under v1 rules throughout its own lifecycle.
   - Its own proposal/review/activation/phase/implementation-review/completed-migration commits are governed by v1 from start to finish.
   - The user grants plan-scoped standing local commit authority separately.
   - The checkpoint rules this plan creates never apply retroactively to this plan, even if the checker and v2 contract become operational before Phase 6.
3. Document that v1 Completed plans remain frozen. No historical rewrite.
4. Update `docs/operating-modes.md` compatibility section.
5. Update `docs/exec-plans/roadmap.md` lifecycle documentation if needed.
6. Update `docs/README.md` if a checkpoint documentation routing link is appropriate.

**File manifest**:
- `docs/operating-modes.md` (compatibility section)
- `docs/README.md` (if routing link exists)
- `docs/exec-plans/reviews/<plan-slug>/evidence/phase-5-compatibility.md`

**Verification**:
- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 scripts/check-operating-modes.py --root .`
- `python3 -m unittest scripts.tests.test_operating_modes`
- `python3 -m unittest scripts.tests.test_durable_checkpoint`
- `python3 scripts/check-startup-doc-budget.py`
- `git diff --check`
- Terminal UI plan (if still Proposed or Active) validates under v1 without errors
- All v1 Completed plans validate without errors
- Migration policy is documented and testable

**Exit gate**: Migration policy is deterministic, authority/state values are derived correctly, this plan's full lifecycle is unconditionally v1, v1 compatibility is proven, and all checkers pass.

**Bootstrap v1 local commit boundary**: All Phase 5 deliverables listed above, only under separately granted v1 local commit authority.
**Authority does NOT extend to**: Actual migration of any existing plan, implementation review, closeout.

### Phase 6 — Integrated Verification, Independent Implementation Review, And Closeout

**Entry gate**: Phase 5 complete; all phases delivered.

**Work**:

1. Run the complete verification matrix:
   - All new and existing checkers in governed profile
   - All v1 and v2 fixtures
   - All checkpoint fixtures
   - Startup budget check
   - `git diff --check`
   - Manual diff review: no runtime/data/remote files modified
   - Manual verification: Terminal UI plan, its reviews, and all Completed plans are byte-exact vs pre-Phase 0 baselines (or only changed by authorized Phase operations)
2. Prepare the implementation review packet:
   - Frozen file manifest with SHA-256 hashes
   - Phase 0-5 evidence index
   - Test matrix results
   - Authority boundary confirmation
3. Request an independent implementation review. The reviewer MUST:
   - Use a different reviewer ID than `codex-plan-author-2026-07-20-durable-checkpoint`
   - Not be from the same drafting context as this plan
   - Independently inspect repository evidence
   - Return `accept`, `revise`, or `reject`
4. If `accept`: Record final disposition, update indexes/roadmap/state blocks, and reconcile lifecycle using only the v1 closeout pattern. This plan never claims a `Tang-Checkpoint: completed-migration` trailer for itself.
5. If `revise`: Enter remediation cycle. Each remediation produces its own evidence and checkpoint.

**File manifest**:
- `docs/exec-plans/reviews/<plan-slug>/evidence/implementation-review-packet-001.md`
- `docs/exec-plans/reviews/<plan-slug>/implementation-review-001.md` (external reviewer)
- Plan file (lifecycle updates: Completed, disposition, etc.)
- Applicable index/roadmap/state block updates

**Verification**:
- Full verification matrix as described in work item 1
- Independent reviewer verdict

**Exit gate**: Implementation review returns `accept`; all phases closed; lifecycle reconciled.

**Bootstrap v1 local commit boundary**: Lifecycle reconciliation files under the v1 pattern only, and only if separately authorized. The new `completed-migration` kind applies exclusively to later v2 subjects.
**Authority does NOT extend to**: Push, PR, merge, Pages, remote settings, any other plan.

## 10. Risks And Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Same-file overlap with existing dirty worktree | Phase 0 cannot cleanly scope files | Strictly block until the owning product resolves the path under separate authority; never stash, split hunks, or absorb it |
| operating-modes-v2 breaks existing v1 validation | Existing plans fail checker | Dual-schema support; v1 plans continue to validate under v1 rules |
| Checkpoint checker becomes a workflow engine | Authority creep; unattended mutation | Checker is read-only by design; one explicitly authorized human/agent actor owns Git writes; fixtures prove no checker write |
| Terminal UI plan activation concurrent with this plan's implementation | Shared index/state/governance paths interfere | Phase 0 treats those live dirty paths as blockers until separately resolved; independence is logical, not falsely assumed path-disjointness |
| v2 schema adds complexity without operational benefit | Over-engineering | v2 is a literal strict key superset; exact state/authority/checkpoint claims are fixture-pinned; v1 remains valid |
| Bootstrap paradox: this plan creates rules that should govern it | Circular dependency | Explicit bootstrap policy: this plan operates under v1 throughout its own lifecycle |

## 11. Rollback Strategy

If separately authorized, each phase may be packaged as an independent **v1 scoped local commit**. This plan never uses the v2 checkpoint/trailer rules it creates. Rollback is a new, separately authorized Git/lifecycle action and reverses implementation phases in order:

1. Phase 6 (closeout): Revert lifecycle updates; move plan back to Active
2. Phase 5 (compatibility): Remove migration policy documentation
3. Phase 4 (harness): Remove checkpoint checker from CI/config; revert harness changes
4. Phase 3 (checker): Delete `check-durable-checkpoint.py` and test file
5. Phase 2 (v2 schema): Remove v2 schema additions from operating-modes.md; revert checker to v1-only
6. Phase 1 (contract): Remove checkpoint contract sections from operating-modes.md; revert ADR, templates, AGENTS, INSTRUCTIONS
7. Phase 0 (baseline): Remove evidence file

At any point, reverting to the Phase 0 baseline restores the repository to its pre-implementation state with all governance operating under v1 only.

## 12. Dependencies

- This plan depends on `operating-modes-v1` remaining the current schema during drafting and review.
- This plan depends on the existing `check-operating-modes.py` and `check-project-harness.py` being functional.
- No external dependencies (no new packages, APIs, or services).
- The Terminal UI plan must remain independent; no implementation dependency in either direction.

## 13. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan/`
- Required verdict: Independent design review with `approve`
- Required user approval: Explicit activation instruction
- Activation is a separate lifecycle change before implementation
- Implementation start requires a later explicit start/execute instruction after activation recording
- The reviewer ID must differ from `codex-plan-author-2026-07-20-durable-checkpoint`
- The reviewer context must not have drafted this plan

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
