# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r6 at `7c750c24d8b53b41260d926e7a57ae896707c322`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r7`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the stable baseline-to-remediation-r6 history and exact remediation diff, normative contract, active plan, implementation-review-006, checker and all fixtures; replay of round-6 workflow, lifecycle-Markdown, router, earlier regression, and supported-positive cases; additional CommonMark, raw-HTML, YAML-condition, execution-modifier, and block-normalization probes; bounded local harness, build, DB, runtime-diff, hash, syntax, and worktree verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r6 正确关闭了 `implementation-review-006` 记录的直接 repro. Non-job `steps`, bare job/step `if`, dead shell branch, heredoc, early exit, multi-line shell flow, comment/fenced/indented lifecycle records, ordinary single-line inline-code pseudo-link, and indented-code pseudo-link 均 fail. Direct quoted inline `run` 及 single-source-line literal/folded `run` 均 pass. 96/96 temporary-repository fixtures, focused/composed checks, startup budget, syntax, whitespace, temporary frontend build, read-only DB checks, runtime zero-diff, and frozen hashes 也通过.

但 operative-carrier 约束仍可由有效 YAML 和 Markdown 形态绕过. Quoted `if` key 不被条件检测识别. Required step 使用不执行脚本的 custom `shell` 仍被计为 direct carrier. Folded scalar 可把 source comment 与 required command 归一为一条 shell comment, checker 却丢弃 comment source line 后接受 required command. CommonMark multi-line code span 和 raw HTML `code`/`pre` context 仍可让 pseudo-link, 全部 plan metadata, 或完整 fixed index table 在非 rendered/operative 状态下计数. 这些 repro 均使 focused checker 返回 pass. 另有一个相反方向的问题: folded scalar 的两行 source 在 YAML 归一后恰好等于 required direct command, checker 仍 false-reject. 因此 remediation-r6 尚未准确实现已声明的 operative/direct formats, implementation 不能获得 `accept`.

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`, HEAD 为 `7c750c24d8b53b41260d926e7a57ae896707c322`, parent 为 `459b1d4158e376d60b8e2ed30138e6981f563d39`. 复审开始时 worktree 和 index 均干净. Baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 HEAD 为 18 个无 merge commit 的线性历史, 共 30 个变更文件.
- Review-006 replay: non-job steps, bare conditioned job/step, dead-shell, heredoc, early-exit, comment-wrapped four indexes, fenced/indented table, commented plan/review/template metadata, closed/unclosed comment, inline/indented router code 均返回 nonzero 和 specific error.
- Prior regression replay: duplicate constrained key, reviewer/author identity collision, wrong review type/target/revision, `Completed` without `accept`, contradictory no-review fields, empty activation, Active next gate `none`, bogus optional evidence, illegal Proposed gate, malformed fixed row, trailing fifth cell, missing sentinel, reversed state markers, and unstructured new-schema prior review 均保持 fail. Truthful pre-review Proposed, non-implemented Completed forms, five allowed Proposed gate prefixes, canonical sentinels, direct links, and source-scanner exclusion cases保持 pass.
- Positive verification: 96/96 fixtures pass. Focused, governed, and auto checks return `errors=[]`. Startup-document budget, launcher syntax, checker source parsing, baseline-to-HEAD whitespace, and isolated frontend production build pass; build transformed 1746 modules and temporary output was deleted.
- Runtime and DB: `backend/`, `frontend/`, `strategies/`, `content/`, `data/`, daily runbook, and Pages publisher have zero baseline-to-HEAD diff. Runbook, publisher, and tracked DB hashes remain `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, and `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. Read-only DB evidence为 `integrity_check=ok`, foreign-key violations `0`, market days `46`, and before/after hash identical.
- Backend evidence: current system environment executed 19 tests, with 18 pass and 1 prerequisite error caused by missing `pandas_market_calendars`. The historical pinned 19/19 Phase 5 result remains applicable because runtime/data zero-diff is verified, but it is not a fresh round-7 run.
- Authority boundary: provider, broker, tracked-DB update, Tang input, stage, commit, push, publication, hosted verification, and remote mutation 均未执行, 也未记录为 pass.

## 问题清单

### 严重问题

1. **Valid YAML execution semantics can satisfy a non-running or non-enforcing carrier**
   - 位置: `scripts/check-operating-modes.py:227-351`, especially `:272-345`; `docs/operating-modes.md` Section 7.
   - 问题描述: source scanner仅识别 bare `if:`. 将 required step 改为 `- "if": false` 或将 job field 改为 `"if": false` 后, valid YAML仍表示条件 false, 但 focused checker pass. Required step加入 `shell: echo {0}` 后也 pass; this custom shell only prints the script path and does not execute the required command. `continue-on-error: true` and an incompatible `working-directory` likewise pass, despite removing enforcement or runnability. A folded block containing a source comment line followed by the command is normalized by YAML to one line beginning with `#`; shell treats the entire normalized value as comment, but `normalized_run_command` discards the source comment line and accepts the command.
   - 影响范围: PR workflow 可 skip required checks or complete a no-op step while local governed validation remains green. 这直接破坏 required CI enforcement carrier, and quoted `if`/arbitrary custom shell do not fall inside the declared unconditional/direct subset.
   - 改进建议: 对 required carrier fail closed. Recognize quoted and bare `if` keys at job and step level. Reject or explicitly validate `shell`, `working-directory`, `continue-on-error`, and workflow/job defaults that change execution semantics. Normalize folded blocks according to YAML folding before testing exact command identity; do not discard a source comment in a way that changes the normalized shell program. Add quoted job/step `if`, non-executing shell, continue-on-error, wrong working directory, and folded-comment negative fixtures.

2. **Valid CommonMark and raw HTML code contexts still count as operative lifecycle and route evidence**
   - 位置: `scripts/check-operating-modes.py:137-204`, `:354-370`, `:689-776`; `docs/operating-modes.md` Sections 5 and 7.
   - 问题描述: `inline_code_span_ranges` is line-local, although CommonMark code spans can cross line endings. A router pseudo-link wholly inside a multi-line code span passes. Wrapping every constrained plan metadata bullet or the complete Active fixed table in a multi-line code span also passes. Raw HTML `<code>[pseudo-link](...)</code>` passes route enforcement, and plan metadata or a fixed table wrapped by `<pre><code>...</code></pre>` passes lifecycle validation. These forms render as code, not canonical links, metadata bullets, or tables.
   - 影响范围: canonical authority route, plan state, and lifecycle index evidence can disappear from the rendered operative documentation while the checker reports green. This is the same authority/evidence class as review-006, reached through valid code contexts not covered by current fixtures.
   - 改进建议: Extend the operative Markdown boundary to mask CommonMark code spans across lines and raw HTML `code`/`pre` contexts before route, metadata, and table parsing. Preserve the existing positive form where inline code appears only inside a real Markdown link label. Add router, plan/review/template metadata, and fixed-table negative fixtures for multi-line code spans and raw HTML code elements.

### 中等问题

1. **Folded block normalization false-rejects a declared direct command form**
   - 位置: `scripts/check-operating-modes.py:207-224`; `docs/operating-modes.md` Section 7.
   - 问题描述: A valid folded block with `python3 -m unittest` on one source line and `scripts.tests.test_operating_modes` on the next normalizes to the exact required command. The checker sees two physical non-comment lines and returns missing required command. This conflicts with the contract statement that a folded block is judged by normalized non-comment content.
   - 改进建议: Implement the constrained folded-scalar normalization actually promised by the contract, then compare the normalized value exactly. If only one physical source line is intended to be supported, change the normative contract and positive-form wording before implementation rather than false-rejecting a declared form.

### 轻微问题

无额外轻微问题.

## 未验证项

- Hosted workflow and publication: 未授权运行. Local workflow inspection and build evidence不能替代 hosted CI, Pages publication, or hosted URL verification.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session evidence, requested-day assemble 1m/5m, Tang JSON, tracked-DB update, data commit/push, Pages run, and hosted sequence require separate authority and actual execution.
- Reviewer identity and authority truth: constrained fields can validate structure and ID inequality, but identity, independence truth, user-instruction truth, and publication authority remain human-validation boundaries.
- Historical pinned backend evidence: 19/19 is applicable through verified runtime zero-diff only. The deleted pinned environment was not recreated, so round 7 does not claim a fresh 19/19 result.

## 裁决理由

remediation-r6 accurately closes every recorded implementation-review-006 fixture and preserves prior regressions, supported one-line carriers, runtime/data boundaries, and read-only verification. However, three independent adversarial groups establish deterministic mismatch with the normative contract: valid quoted conditions and execution modifiers can make non-running steps count, valid code contexts can make non-rendered lifecycle/route records count, and a valid folded scalar that normalizes to the exact command can be rejected. The first two are enforcement and authority false-passes, so implementation is not ready for closeout. The defects are localized to constrained parsing and fixtures rather than the peer-mode/lifecycle design, therefore verdict is `revise` rather than `reject`, with confidence `high`.
