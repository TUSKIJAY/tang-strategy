# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md implementation at `28629a59a2eb7d0fdce362e2754d8476b7f4aa8e`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r1`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: independent inspection of the complete baseline-to-HEAD diff and six phase commits, line-level checker and fixture review, current lifecycle and migration reconciliation, clean temporary-repository positive and adversarial fixtures, local harness and build checks, read-only DB checks, and frozen runbook/publisher/DB hash comparison
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

实现的主体架构与 reviewed revision 一致. `docs/operating-modes.md` 已成为单一规范源, Coding Mode 与 Data Update Mode 保持对等, 本地验收与发布授权分离, legacy completed plan 只增加 metadata, 六个 Phase 0-5 commit 线性且其 21 个变更文件均位于 Section 2.2 manifest. Governed/minimal profile 分离, external `--root` 组合, 35 个既有 fixture, startup budget, frontend production build, DB integrity 和 read-only 边界均有正向证据.

但核心 lifecycle checker 存在可复现的 authority false-pass, 且 Data Update compatibility 检查通过未受约束的源码/散文子串判断行为. 错误 review type, 任意同名 review target, 冲突 verdict, 非法 Proposed next gate 和过期 reviews index verdict 均能返回 pass. 适配器默认 import 语句仅留在注释中也能 pass, 而行为等价的多行写法会 fail. 这些不是文档优化项, 而是 plan Section 3, 7 和 9 所要求的确定性检查未达标. 实现可在现有方向内修复, 因此不适用 `reject`, 但在补齐负向载体并重新送审前不满足 `accept`.

## 已验证项

- 固定审查范围: baseline `a4b4007a9e529d1748f7f3b9884768471751dc33`, stable HEAD `28629a59a2eb7d0fdce362e2754d8476b7f4aa8e`; 六个 Phase commit 均为单父线性历史, 审查开始前工作树干净.
- 范围与兼容性: diff 仅含 21 个 manifest 文件. `docs/daily-publish-runbook.md`, `.github/workflows/publish-static-reviews.yml`, tracked DB, 两个 fetch adapter 和 rebuild runtime 相对 baseline 均为零 diff.
- 冻结证据: runbook SHA-256 为 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`; Pages workflow 为 `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`; tracked DB 为 `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. 三者与 baseline 相同.
- 正向验证: focused checker, composed governed checker, 35/35 fixtures, startup-document budget, launcher syntax, baseline-to-HEAD whitespace check和 frontend production build通过. Frontend 构建使用临时输出目录, 1746 个 modules transformed, 未在 repo 留下 `dist`.
- DB 只读验证: `integrity_check=ok`, foreign-key violations 为 0, market day 为 46; backend suite 在现有解释器运行 19 项, 18 项通过, 1 项因缺少 pinned calendar dependency 报 prerequisite error; tracked DB before/after hash 相同.
- Legacy migration: 2026-07-18 completed plan 仅在头部新增 constrained metadata, 历史正文与 review body 未改写; implementation/reconciliation commit 均存在且祖先关系有效.
- Deferred evidence: provider fetch, IB fallback, tracked-DB update, Tang input, data commit/push, Pages run, hosted URL 与真实 publication 未执行, 计划和状态文档未将其标为 pass.

## 问题清单

### 严重问题

1. **Review 与 lifecycle 的 constrained invariants 存在多条 authority false-pass**
   - 位置: `scripts/check-operating-modes.py:135-143`, `:265-291`, `:309-381`, `:441-474`; `scripts/tests/test_operating_modes.py:432-645`.
   - 问题描述: metadata parser 对重复 key 静默覆盖. Review validator 只检查 `Review type` 属于允许词表, 未将 design review 绑定 `design`, 也未将 implementation review 绑定 `implementation`; `Review target` 只比较 basename, 未验证 repository-relative lifecycle path. Proposed state 未限制 next gate 为 revision/review/activation-recording. Reviews index 只校验 lifecycle state, 不对账 listed reviews 或 latest verdict. 独立临时 fixture 证明以下六种状态均返回 code 0 和 `passed=true`: design review 标成 `implementation`; implementation review 标成 `design`; target 改为 `unrelated/location/demo-plan.md`; 同一 review 先写 `Verdict: reject` 后写 `Verdict: approve`; reviews index latest verdict 改为 `reject`; Proposed plan 和所有 derived blocks 的 next gate 改为 `publish-now`.
   - 影响范围: 非设计评审可以满足 Active gate, 非实现评审可以满足 Completed `accept`, 矛盾 review evidence 和越权 next gate 可以进入 green harness. 这直接削弱独立评审, activation 和 closeout 的 authority 分离, 也说明 35 fixtures 尚未覆盖 Section 9.1 对 matching review 和 legal lifecycle state 的完整语义.
   - 改进建议: 拒绝所有 constrained key 重复; 按引用用途强制 review type; 将 review target 限制为 `docs/exec-plans/<proposed|active|completed>/<exact filename>`; 校验 review artifact 位于 `reviews/<plan-slug>/`; 为 Proposed next gate 建立允许类别; 对账 reviews index 的 artifact 集与 latest verdict. 为每个复现 case 增加负向 fixture, 并补 index evidence link/disposition row 的一致性检查.

2. **Data Update 检查越过 constrained-format 边界并同时产生 false-pass 与 false-failure**
   - 位置: `scripts/check-operating-modes.py:652-731`; `scripts/tests/test_operating_modes.py:618-644`; active plan Section 3.1-3.5, 7.1, 9.2 和 Phase 5 execution record.
   - 问题描述: focused lifecycle checker 通过原始子串扫描 AGENTS, runbook, Python adapter, rebuild script 和 workflow YAML. 这些文件不是 Constrained Format Package, 子串存在不能证明执行语义或命令顺序. 独立 fixture 将 TV adapter 的 required import 行注释掉并改为 `market_day_id = None`, 因注释仍含原 token 而 pass; 将同一表达式改写为行为等价的 `if/else` 后反而 fail. 现有 Pages/runbook checks 也只证明 token 出现, 不能证明 main-to-`gh-pages` 执行结构或 TV-first 顺序.
   - 影响范围: harmless refactor 可使 governed harness 变红, 实际删除或绕过行为可通过保留注释/死文本骗过检查. Phase 5 所称的 adapter/rebuild/publisher contract enforcement 超出证据能支持的结论, 并触发 plan 的 stop condition: lifecycle truth 不得依赖对 unconstrained prose/source 的语义猜测.
   - 改进建议: lifecycle checker 仅保留受约束 metadata, fixed rows/blocks, required path 和明确结构化 route 的检查. 本 plan 的 unchanged compatibility 使用 baseline-to-HEAD exact diff/hash 证据, 不把 source token 当行为证明. 若要长期机器验证 adapter/workflow 语义, 另行定义结构化 marker, AST/YAML 级检查或行为测试, 并按 Coding Lane 3 评审后实施. 增加 comment/dead-text false-pass 与 equivalent-refactor false-failure fixtures.

### 中等问题

1. **HANDOFF 的最新 resume prose 与稳定审查边界不一致**
   - 位置: `HANDOFF.md:30`, `:52`, `:68-70`.
   - 问题描述: stable HEAD 已是 Phase 5 boundary commit, 但 resume checklist 和 Next Gate 仍要求先创建该 commit 再请求 review. 同一表中无 plan 标识的 `Independent review: accept, confidence high` 实际属于 2026-07-18 completed plan, 容易被解释为本 active plan 已有 implementation accept, 而 active metadata 明确为 `Implementation review: none`.
   - 改进建议: remediation 后将 Phase 5 commit 记录为历史 evidence, 把旧 plan 的 review 行明确标注 plan slug或移入对应历史入口, 并使 handoff 只保留真实的下一 gate. 不在受约束 block 中存放 live Git claim.

### 轻微问题

无额外轻微问题.

## 未验证项

- Pinned backend 19/19 与 compileall: Phase 5 record 声明曾在临时 pinned environment 通过, 该 environment 已删除. 独立复跑因本机缺少 `pandas_market_calendars` 得到 18 pass + 1 prerequisite error, 未重新安装依赖或把该项冒充 pass.
- Hosted workflow 和 specialized workflow lint: 未授权 remote run, 且本机无对应 hosted evidence. Local config/order/job-name 检查已通过, 不能替代 hosted result.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session, newly requested day assemble 1m/5m, optional browser smoke, Tang JSON, commit/push/Pages/hosted sequence均需未来单独授权运行.
- Human authority truth: repository fields能证明 ID 不同和 declaration 存在, 不能单独证明历史 reviewer identity 或用户指令真实性. 本 review context 未起草或实现被审 revision, independence declaration 为 attested.

## 裁决理由

正向实现, scope, read-only behavior, migration和 compatibility baseline大部分成立, 所以无需重新设计双模式架构. 但本交付的核心是把 lifecycle truth 和 authority gates 变成确定性机器检查. 多个错误 review/lifecycle 状态可稳定返回 pass, 同时 unconstrained source substring 会对合法等价实现产生 failure. 这些缺陷会让 green harness 既不能可靠阻止越权状态, 也不能可靠代表兼容性, 属于必须由执行者返工的实现偏差. 裁决为 `revise`, confidence 为 `high`.
