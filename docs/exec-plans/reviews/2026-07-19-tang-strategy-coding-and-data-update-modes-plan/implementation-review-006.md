# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r5 at `cc00bc40075b560a091b5ce30f2c60ba426b3a7e`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r6`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the complete baseline-to-remediation-r5 history and diffs, normative contract, active plan, implementation-review-005, checker and fixtures; independent replay of prior findings and all four review-005 categories; adversarial workflow, router, index, plan-metadata, and review-metadata probes; bounded local harness, build, DB, runtime-diff, hash, syntax, and worktree verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r5 正确关闭了 `implementation-review-005` 的四类指定问题. Workflow 和 router 的 comment-only carriers fail. Empty index 缺少 sentinel, reserved-word forged row, malformed header/separator/delimiter 均 fail. Reversed current-state markers fail. New-schema plan 声明的 prior-revision bare review 也 fail. `review-001` 和 `review-002` 的迁移仅补充 constrained metadata, 历史 findings 和 verdict 保持不变.

baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 stable review commit `cc00bc40075b560a091b5ce30f2c60ba426b3a7e` 的 16 个线性 commit, 29 个变更文件, 5 个 review/remediation boundary 和完整 remediation-r5 diff 已复核. 但新一轮 adversarial probes 发现 execution carrier 仍可位于不会运行的 workflow/shell context, constrained lifecycle surfaces 可整体隐藏在 HTML comment 或 fenced code 中, router 也接受 code span/code block 内并非实际 Markdown link 的文本. 这些 false-pass 会在 governed result 为 green 时移除实际 CI enforcement 或隐藏 canonical lifecycle evidence. 因此 implementation 仍不能获得 `accept`.

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`, HEAD 为 `cc00bc40075b560a091b5ce30f2c60ba426b3a7e`. 复审开始时 worktree 和 index 均干净.
- Review-005 replay: workflow/router comment-only, missing empty sentinel, reserved header word, missing terminal delimiter, reversed state markers, and new-schema bare prior review 均返回 nonzero 和 specific error.
- Prior replay: duplicate constrained key, reviewer/author identity collision, `Completed` without `accept`, empty activation token, Active `Next gate=none`, and trailing empty fifth cell 均保持 fail. 79/79 temporary-repository fixtures pass, 包含此前各轮的其余 regression carriers.
- Supported carrier forms: direct quoted inline `run` and direct folded block `run` pass. YAML anchor/alias carrier fail; contract 仅声明 inline/block forms, 因此该结果未单独归类为缺陷.
- Positive verification: focused, governed, and auto checks pass. Startup-document budget, Python syntax parsing, baseline-to-HEAD whitespace check, and isolated frontend production build pass. Build transformed 1746 modules, temporary output was deleted.
- Runtime and DB: daily runbook, Pages publisher, tracked DB, TV/IB adapters, rebuild runtime, backend/frontend runtime, strategies, content, and data surfaces have zero baseline-to-HEAD diff. Runbook, Pages, and DB hashes remain `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, and `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. Read-only DB evidence is `integrity_check=ok`, foreign-key violations `0`, market days `46`, and before/after hash identical.
- Authority boundary: provider, broker, tracked-DB update, Tang input, commit, push, publication, hosted verification, and remote mutation 均未执行, 也未写成 pass.

## 问题清单

### 严重问题

1. **Workflow command extraction 仍接受不可执行或永不执行的 carrier**
   - 位置: `scripts/check-operating-modes.py:165-232`, `:1105-1114`; `docs/operating-modes.md:221-225`.
   - 问题描述: 四个独立 fixture 均返回 focused 和 governed pass: required steps 带 `if: false`; required commands 仅位于 top-level `x-dead.steps` 而不在 `jobs.<job>.steps`; block scalar 把 command 放在 `if false; then ... fi`; block scalar 把 command 放在 heredoc body. 前两种不会调度 required command, 后两种只把 command 作为 dead branch 或数据文本. 当前 scanner 接受任何名为 `steps` 的缩进列表, 且把 block scalar 每个非 comment line 单独追加为 command, 因此 source text presence 被误当成 execution carrier.
   - 影响范围: PR workflow 可移除 focused checker 和 fixture tests 的实际执行, 仅保留 dead text, 同时 canonical governed check 仍为 green. 这重新打开 review-005 所要求关闭的 CI enforcement bypass.
   - 改进建议: 将允许形态收敛为 `jobs.<job>.steps[].run` 的 constrained subset, 并拒绝 job/step-level false condition. Inline value 必须精确等于 required command. Block value 仅在规范化后只含一个 direct required command 时计数, 不把任意 shell line 独立提升为 executable command. 增加 `if: false`, non-job `steps`, shell dead branch, heredoc, and command-after-early-exit negative fixtures.

2. **Constrained lifecycle evidence 可整体处于非 operative Markdown context**
   - 位置: `scripts/check-operating-modes.py:235-251`, `:273-315`, `:570-657`; `docs/operating-modes.md:95-149`.
   - 问题描述: 将 Proposed, Active, Completed, and Reviews 四个 canonical table 从 header 到 row/sentinel 全部包在 outer HTML comment 中, checker 仍 pass. 将 Active table 放入 fenced code 也 pass. 同样地, 将 Active plan 的全部 constrained metadata bullets 或 design review 的全部 reviewer metadata bullets 包入 HTML comment, checker 仍 pass. `parse_header_bullets` 和 `parse_table_rows` 直接扫描 raw lines, 未排除 Markdown comment/fence context.
   - 影响范围: canonical lifecycle table, plan state, and independent-review evidence 可从 rendered/operative documentation surface 完全消失, 但 directory/index/roadmap/current-block reconciliation 仍显示 valid. Exact header/sentinel grammar 只约束隐藏 text 的形状, 没有保证 canonical surface 实际存在.
   - 改进建议: 对 plan, review, template, and fixed-index constrained records 使用 context-aware Markdown preprocessing, 在解析前排除 HTML comments, fenced code, and other non-operative code contexts. Current-state 和 historical-evidence marker comments 应由专用 bounded parser 单独处理, 不应放宽普通 constrained bullets/tables. 为四个 comment-wrapped indexes, fenced index, commented plan metadata, and commented review metadata 增加 negative fixtures.

### 中等问题

1. **Router 将 code text 误判为 canonical Markdown link**
   - 位置: `scripts/check-operating-modes.py:137-162`, `:1047-1055`; `docs/operating-modes.md:225`.
   - 问题描述: AGENTS route 只保留 inline code span 中的 `[label](./docs/operating-modes.md)`, checker pass. 将同一文本放入 four-space indented code block 也 pass. 这两种 rendered form 均不是可点击的 Markdown link. 当前 preprocessor 仅移除 HTML comments 和 fenced blocks, 随后的 regex 仍扫描 code spans and indented code.
   - 影响范围: compact authority router 可失去实际 link, 但 required route check 仍为 green. 影响范围小于 workflow execution bypass, 但违反 non-comment canonical Markdown link 的 operative intent.
   - 改进建议: 在 link matching 前排除 CommonMark inline code spans and indented code blocks, 或使用受限 line grammar 只接受普通 Markdown context 中完整解析的 inline link. 增加 inline-code and indented-code negative fixtures, 保留 ordinary link positive fixture.

### 轻微问题

无额外轻微问题.

## 未验证项

- Pinned backend 19/19: stable Phase 5 evidence 来自 pinned environment. 本轮系统解释器独立运行 19 项得到 18 pass and 1 prerequisite error, 原因为缺少 `pandas_market_calendars`. Runtime zero-diff, frozen hashes, syntax, DB, and frontend evidence 使历史 pinned result 仍可作为 applicable historical evidence, 但本轮未把它声明为新的 19/19 pass.
- Hosted workflow and publication: 未授权运行. Local workflow shape and frontend build 不能替代 hosted CI, Pages publication, or URL verification.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session evidence, requested-day assemble 1m/5m, Tang JSON, data commit/push, and hosted sequence 需要独立授权与实际运行.
- Identity and authority truth: constrained fields 可验证 structure and inequality, 但 reviewer identity, independence truth, evidence quality, and user instruction truth 仍属于 human validation boundary.

## 裁决理由

remediation-r5 对上一轮四类问题的目标修复有效, 79 fixtures 和 bounded verification 也保持稳定, runtime/data/provider/publisher boundary 未漂移. 但 required CI commands 仍可只存在于 never-executed contexts, 且 canonical lifecycle and review evidence 可整体隐藏在 comments/code. 两项严重问题均有 focused/governed pass 的确定 repro, router 另有独立 false-pass. 问题可通过收紧现有 constrained parsers 和补充 fixtures 局部修复, 不需要推翻 peer modes 或 lifecycle design, 因此裁决为 `revise`, confidence 为 `high`.
