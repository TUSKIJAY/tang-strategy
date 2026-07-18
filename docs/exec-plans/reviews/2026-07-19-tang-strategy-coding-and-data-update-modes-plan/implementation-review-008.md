# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r7 at `9dad5a9396ecc0efd0e776707aa6f0a5a27dedaf`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r8`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the stable baseline-to-remediation-r7 history and exact remediation diff, normative contract, active plan, implementation-review-007, checker and all fixtures; independent replay of every round-7 finding, prior lifecycle/index/review regressions, and supported positive forms; additional duplicate-mapping, trigger-hierarchy, cross-job-order, quoted/flow-key, scalar-style, and nested raw-code probes; bounded local harness, build, DB, runtime-diff, hash, syntax, and worktree verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r7 正确关闭了 `implementation-review-007` 的三类 recorded finding. Bare/quoted job or step conditions, custom shell, working directory, continue-on-error, env/default modifiers, incompatible runner, folded shell-comment no-op, multiline CommonMark code span, and ordinary raw HTML code carrier 均 fail. Folded source lines that normalize to the exact command pass. Real links with code-formatted labels and quoted `ubuntu-latest` runner pass. 114/114 temporary-repository fixtures, focused/composed checks, startup budget, syntax/whitespace, temporary frontend build, read-only DB checks, runtime/data zero-diff, and frozen hashes also pass.

但 workflow source scanner 仍未建立唯一 YAML mapping 和实际 execution order. Appending a second top-level `on:` that contains only `workflow_dispatch`, a second top-level `jobs:` without required commands, or a duplicate `jobs.harness` whose later value omits required commands all produce focused pass. A normal YAML mapping parse retains the later value in each repro. Moving the two required commands into separate eligible jobs also passes even though those jobs run concurrently and do not preserve the declared order. The trigger parser additionally accepts `pull_request` nested under an unrelated `x-dead` key. Markdown masking also stops at the first same-tag raw HTML close: nested `<code>` can expose a pseudo-link or all constrained plan metadata while the checker passes. These false-passes prevent closeout. Valid equivalent YAML spellings are false-rejected in the opposite direction, so implementation does not yet accurately enforce the declared format.

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`, HEAD 为 `9dad5a9396ecc0efd0e776707aa6f0a5a27dedaf`, parent 为 `3ffe9bbcd39f55b158c9f9d1e0587541f6dd0473`. 复审开始时 worktree 和 index 均干净. Baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 HEAD 为 20 个无 merge commit 的线性历史, 共 31 个变更文件.
- Review-007 replay: quoted job/step `if`, `shell: echo {0}`, `continue-on-error`, incompatible `working-directory`, folded source comment, multiline code-span route/metadata, and raw HTML route/table carriers均返回 nonzero. Folded split command normalizes后 pass.
- Workflow modifier and positive replay: job/workflow defaults or env, unsupported runner, duplicate direct `run`, non-job steps, dead branch, heredoc, early exit, ordinary multi-line shell flow, comment-only command/trigger, and missing PR-main trigger fail. Direct inline, quoted inline, single-line literal/folded, folded split command, quoted runner, and current same-job command order pass.
- Prior lifecycle regression replay: duplicate constrained metadata, author/reviewer collision, wrong review type/target/revision, `Completed` without `accept`, contradictory no-review state, empty activation, Active next gate `none`, bogus optional evidence, illegal Proposed gate, malformed fixed table, trailing fifth cell, missing/mixed sentinel, reversed state markers, and unstructured new-schema prior review remain fail. Truthful optional states, allowed Proposed gate prefixes, canonical sentinels, and fixed links remain pass.
- Positive verification: 114/114 fixtures pass. Focused, governed, and auto checks return `errors=[]`. Startup-document budget, launcher syntax, checker source parsing, baseline-to-HEAD whitespace, and isolated frontend production build pass; build transformed 1746 modules and temporary output was deleted.
- Runtime and DB: `backend/`, `frontend/`, `strategies/`, `content/`, `data/`, daily runbook, and Pages publisher have zero baseline-to-HEAD diff. Runbook, publisher, and tracked DB hashes remain `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, and `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. Read-only DB evidence is `integrity_check=ok`, foreign-key violations `0`, market days `46`, and before/after hash identical.
- Backend evidence: current system environment executed 19 tests, with 18 pass and 1 prerequisite error caused by missing `pandas_market_calendars`. The historical pinned 19/19 Phase 5 result remains applicable because runtime/data zero-diff is verified, but it is not a fresh round-8 run.
- Authority boundary: provider, broker, tracked-DB update, Tang input, stage, commit, push, publication, hosted verification, and remote mutation were not executed or recorded as pass.

## 问题清单

### 严重问题

1. **Duplicate or structurally unrelated workflow mappings can satisfy trigger and command enforcement**
   - 位置: `scripts/check-operating-modes.py:312-519`, especially `:322-327`, `:346-480`, and `:483-519`; `docs/operating-modes.md` Section 7.
   - 问题描述: Four independent false-pass repros return focused exit `0`: append a second top-level `on:` containing only `workflow_dispatch`; append a second top-level `jobs:` containing only a replacement job without required commands; append a duplicate `jobs.harness` whose later value contains no required commands; or move the canonical and fixture commands into two separate otherwise eligible jobs. The scanner retains candidates from earlier mappings and never checks uniqueness of top-level keys or job IDs. It flattens candidates across jobs, so source order is misreported as execution order although the jobs are concurrent. A fifth repro replaces the direct `on.pull_request` mapping with `on.x-dead.pull_request`; the trigger parser accepts the nested text because it does not require direct parent-child indentation.
   - 影响范围: The repository can report green local governance while the operative workflow has no valid PR-main trigger, no operative required-command job, or no guaranteed canonical-before-fixture execution. Duplicate YAML may be rejected by a workflow parser or resolve to a later shadowing value; neither state satisfies the contract. This is a CI enforcement false-pass.
   - 改进建议: Parse the declared constrained workflow hierarchy with exact parent indentation and reject duplicate top-level mappings, duplicate job IDs, and duplicate event keys before extracting evidence. Require `on.pull_request.branches` to be direct. Require both commands to appear in ordered steps of the same qualifying job, or define and validate an explicit dependency relation if cross-job carriers are intended. Add all five repros as negative fixtures.

2. **Nested same-tag raw HTML code can expose non-operative route and lifecycle records**
   - 位置: `scripts/check-operating-modes.py:190-208`, `:237-246`, and `:522-538`; `docs/operating-modes.md` Sections 5 and 7.
   - 问题描述: `operative_markdown_text` uses a non-greedy same-tag expression. In `<code><code>x</code>[dead](./docs/operating-modes.md)</code>`, masking stops at the inner close and the pseudo-link is accepted as the canonical route. The same shape placed before all Active plan metadata masks only the prefix, leaves every bullet inside the outer code element visible to the scanner, and returns pass. Both repros produce focused exit `0`.
   - 影响范围: Authority routing or canonical lifecycle state can remain inside a raw HTML code context while rendered/operative evidence is absent, recreating the review-007 Markdown authority false-pass through nesting.
   - 改进建议: Replace same-tag regex masking with a bounded scanner that tracks nested `code`/`pre` elements and masks through the matching outer close, including unclosed forms. Add nested route, plan/review/template metadata, and fixed-table negative fixtures while retaining the real code-formatted link-label positive.

### 中等问题

1. **Valid equivalent YAML spellings are rejected outside any declared source restriction**
   - 位置: `scripts/check-operating-modes.py:249-309`, `:346-378`, and `:483-519`; `docs/operating-modes.md` Section 7.
   - 问题描述: Four valid equivalent forms return nonzero: `branches: [main]`; a block sequence item `- "main"`; quoted top-level `"jobs":` or quoted job ID `"harness":`; and folded `>2-` with the exact required command. Parsing these samples as YAML yields the same `main`, `jobs`, job ID, and run scalar values accepted by the contract. Quoted `runs-on: "ubuntu-latest"` already passes, showing that source quoting is not globally excluded.
   - 影响范围: Harmless YAML formatting changes can make the governed checker red even when workflow trigger and execution semantics are unchanged. This is fail-closed but conflicts with the format contract and creates avoidable CI churn.
   - 改进建议: Either normalize the supported YAML scalar/key/sequence forms before comparison, including explicit block indentation indicators, or revise Section 7 to state an exact source grammar and reject all undeclared variants consistently. Add positive fixtures for the forms retained by the contract.

### 轻微问题

无额外轻微问题.

## 未验证项

- Hosted workflow and publication: not authorized. Local workflow inspection and build evidence cannot substitute for hosted CI, Pages publication, or hosted URL verification.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session evidence, requested-day assemble 1m/5m, Tang JSON, tracked-DB update, data commit/push, Pages run, and hosted sequence require separate authority and actual execution.
- Reviewer identity and authority truth: constrained fields can validate structure and ID inequality, but identity, independence truth, user-instruction truth, and publication authority remain human-validation boundaries.
- Historical pinned backend evidence: 19/19 is applicable through verified runtime zero-diff only. The deleted pinned environment was not recreated, so round 8 does not claim a fresh 19/19 result.

## 裁决理由

remediation-r7 closes every implementation-review-007 finding, preserves prior lifecycle regressions, and keeps runtime/data/provider/publisher boundaries frozen. However, duplicate and nested workflow mappings can remove the operative trigger or job while leaving the checker green, cross-job flattening claims an execution order that does not exist, and nested raw HTML can again hide route or lifecycle evidence. These are deterministic enforcement and authority false-passes. Valid equivalent YAML forms also produce false-rejection. The defects remain local to constrained source parsing and fixtures rather than the peer-mode or lifecycle architecture, therefore verdict is `revise` rather than `reject`, with confidence `high`.
