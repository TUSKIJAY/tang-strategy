# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md implementation and remediation at `6c108feaa0870c3c363349088b6333a3c8f51f6f`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r2`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the full baseline-to-remediation history and exact remediation diff, line-level contract/checker/fixture review, replay of every implementation-review-001 adversarial case, additional pre-review and non-implemented lifecycle fixtures, focused and composed harness checks, temporary frontend build, read-only DB checks, and frozen runtime/hash comparison
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation commit 对 `implementation-review-001` 的主要问题进行了实质修复. Duplicate constrained keys 现在 fail closed; design 和 implementation review type 已按用途绑定; review target 与 artifact path 已受约束; 当前 reviews index artifact set/latest verdict 和 Active/implemented-Completed evidence 能对账; raw AGENTS/runbook/adapter/rebuild/publisher semantic token scanning 已移除; HANDOFF 已正确区分本计划 `revise` 与 2026-07-18 旧计划的 `accept`, 也不再要求重建 Phase 5 commit. 上一轮 7 个 false-pass 均经独立 fixture 复验为 fail, comment-only adapter 与等价多行 adapter 两个案例均不再影响 lifecycle checker.

但 state-index evidence 仍对所有 lifecycle state 无条件要求一个 link, 然后只在 expected evidence 非空时比较 target. 这会拒绝两个受 schema 明确允许的真实状态, 又能被指向无关文件的伪 evidence 绕过: first-review 之前的 Proposed plan, 以及未实施便 Rejected/Terminated/Superseded 的 Completed plan. 另有一个 Proposed gate prefix 与规范文本不一致. 这些问题仍位于本计划的核心 lifecycle correctness 范围, 因此不能裁决为 `accept`; 修复范围局部且不需要推翻架构, 因此不适用 `reject`.

## 已验证项

- 固定边界: baseline 为 `a4b4007a9e529d1748f7f3b9884768471751dc33`, remediation HEAD 为 `6c108feaa0870c3c363349088b6333a3c8f51f6f`. Phase 5 后先由 `8dfc7686f24e97f5e29e0cc64d9e607091ea1377` 登记 review, 再由 stable HEAD 提交 bounded remediation; 历史线性, 复审开始时工作树干净.
- 原 finding closure: duplicate plan/review/state/template key, wrong design type, wrong implementation type, arbitrary same-basename target, wrong direct artifact directory, stale reviews-index verdict/artifact set, stale Active evidence, wrong implemented-Completed evidence 和 illegal `publish-now` gate 均返回非零且有 specific error.
- Constrained boundary: comment-only import token 和等价 `if/else` adapter 都返回 lifecycle pass; 删除 runbook, Pages publisher 和 runtime adapter/rebuild fixture files 也不再造成 lifecycle semantic judgment. Required constrained paths, routers, config 和 project-harness workflow checks 保留.
- 正向验证: focused, governed composed 和 auto composed checks 通过; 49/49 repository fixtures 通过; governed wrapper 对 child nonzero + empty error list 能 fail closed; startup budget, launcher syntax, baseline-to-HEAD whitespace 和 Python syntax 均通过.
- Runtime 兼容: runbook, Pages publisher, tracked DB, TV/IB adapters 和 rebuild runtime 相对 baseline 均为零 diff. Frozen runbook, Pages 和 DB SHA-256 分别为 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`, 与 baseline 一致.
- Native/read-only: frontend production build在临时输出目录完成, 1746 modules transformed; DB `integrity_check=ok`, foreign-key violations 为 0, market day 为 46; backend system environment 运行 19 项时 18 项通过, 1 项因缺少 pinned calendar dependency 报 prerequisite error, tracked DB before/after hash相同.
- Authority boundary: provider, broker, tracked-DB update, Tang input, data commit/push, Pages run, hosted verification 和其他 remote action 未执行, 也未在 lifecycle evidence 中冒充 pass.

## 问题清单

### 严重问题

1. **Optional lifecycle evidence 同时产生 false-failure 与可绕过的 false-pass**
   - 位置: `scripts/check-operating-modes.py:479-572`, `:575-663`; `docs/operating-modes.md:101-121`, `:142-150`; active plan Section 3.2, 3.3 和 5.2.
   - 问题描述: `check_indexes` 在识别 state-specific expected evidence 前, 对每个 row 调用 `state_index_evidence`, 强制 `cells[2]` 恰有一个 link. 独立 fixture 证明: (a) Proposed plan 使用合法的 `Design reviews: none`, `Latest design verdict: none`, `Review independence: none`, next gate `activation-recording`, state-index evidence `none`, 且尚无 review artifact 时, checker 因缺少 evidence link 而 fail; (b) 将同一 cell 改为无关的 `[none](../plan-template.md)` 并省略 reviews-index plan row, checker 反而 pass; (c) 未实施便以 `Final disposition: Rejected`, `Implementation review: none`, commits `none` 进入 Completed 的 plan, verification `none` 时 fail; (d) 把 verification 换成指向 `plan-template.md` 的伪 link 后 pass. `check_reviews_index` 的 expected rows 还只来自已存在 review directory 的 plan, 与 normative text 的 one-row-per-plan 规则不一致.
   - 影响范围: proposal drafting 在首次独立 review 之前无法形成 truthful green state; 未实施的终止/拒绝/取代路径也无法 truthful closeout. 操作者可以用任意 repo file link 消除红灯, 使 state-index evidence 不再证明 review evidence. 这破坏 governed lifecycle 的入口和非实施终态, 属于核心正确性偏差.
   - 改进建议: 先从 plan metadata 计算 expected evidence, 再按 state 强制 cell 形状. Proposed 有 design review 时要求 exact latest link/verdict, 无 review 时要求 exact `none` sentinel 且禁止 link; Active 始终要求 exact latest review link; Completed 有 implementation review 时要求 exact link, 无 implementation review 时要求定义明确的 sentinel或合法 disposition evidence, 且禁止任意 link. Reviews index 应按最终 contract 对每个 plan 建行, 并定义 empty artifact set 的合法 row. 增加 first-review Proposed 和 non-implemented Completed 的 truthful-pass + bogus-link-fail fixtures.

### 中等问题

1. **`design-review` gate 的 prefix grammar 与规范不一致**
   - 位置: `docs/operating-modes.md:117-121`; `scripts/check-operating-modes.py:149-156`; `scripts/tests/test_operating_modes.py:671-680`.
   - 问题描述: normative state invariant 允许 Proposed next gate 以 `design-review` 开头. Regex 对 `review`, `revision`, `plan-revision` 和 `activation-recording` 都允许 suffix, 但 `design-review` 仅允许 exact token. 独立 fixture 中合法的 `design-review-r2` 被拒绝, 而 `publish-now` 被拒绝的负向 case 正常.
   - 改进建议: 为 `design-review` 使用与其他 gate category 相同的 delimiter + suffix规则, 并为五类 allowed prefix 各增加至少一个 positive fixture, 保留 publish/implementation 类 negative fixture.

### 轻微问题

无额外轻微问题.

## 未验证项

- Pinned backend 19/19 与 compileall: plan 记录 2026-07-19 的临时 pinned environment 已通过并清理. 复审未重新安装依赖; 现有解释器缺少 `pandas_market_calendars`, 因此只独立确认 18 pass + 1 prerequisite error, 未将其写成 19/19 pass.
- Hosted workflow, publication 和 hosted URL: 未授权执行. Local workflow shape/job names/check order 通过, 不能替代 hosted result.
- Real Data Update evidence: provider provenance, IB whole-day/gap/session, newly requested day assemble 1m/5m, optional browser smoke, Tang JSON 和 commit/push/Pages/hosted sequence 仍需未来单独授权.
- Historical identity and user instruction truth: repository能验证 fields, ID inequality 和 attestation 结构, 不能单独证明历史会话身份或用户指令真实性. 本复审 context 未起草或实现被审 revision/remediation.

## 裁决理由

remediation 已关闭上一轮全部已列 authority false-pass, constrained-vs-unconstrained boundary 和 HANDOFF 问题, 实现方向正确且正向验证充分. 但 fresh adversarial review 证明 checker 仍无法 truthful 表达 proposal-before-review 和 non-implemented Completed 两类计划 schema 允许的生命周期, 同时接受无关 file link 作为伪 evidence. `design-review` prefix 还存在明确的 contract/code false-failure. 这些偏差需要执行者完成小范围返工并新增 fixtures 后再次复审. 裁决为 `revise`, confidence 为 `high`.
