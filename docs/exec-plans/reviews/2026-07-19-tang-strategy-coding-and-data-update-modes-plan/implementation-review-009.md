# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r8 at `fbc3729c35e55f8f28e383c5ed7dc2b475f4f3ef`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r9`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the stable remediation-r8 commit, its parent and exact diff, normative contract, active plan, implementation-review-008, checker, and all fixtures; replay of every round-8 finding and earlier regression carrier; additional invalid and non-scalar flow-sequence, null-step, null-name, quoted-key, block-scalar, hierarchy, and nested raw-code probes; independent YAML semantic comparison; bounded focused/composed harness, startup-budget, syntax, whitespace, runtime-diff, frozen-hash, read-only DB, and isolated frontend-build verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r8 正确关闭了 `implementation-review-008` 记录的 duplicate top-level/event/field/job mappings、nested trigger lookalike、cross-job order、nested raw HTML code，以及 quoted/flow YAML 和 explicit block-indent 等价写法问题。133/133 temporary-repository fixtures 全部通过，focused/governed/auto checks、startup budget、source syntax、baseline whitespace、临时 frontend build、runtime/data zero-diff、frozen hashes 和 read-only DB checks 也通过。

但新一轮 source-grammar probes 仍得到两个独立 false-pass。`branches: [main,, {bad: value}]` 在独立 YAML 解析时为 syntax error，合法 YAML 形式 `branches: [main, {bad: value}]` 则包含 contract 明确排除的 mapping item；两者都被 focused checker 接受。另一个 repro 在 qualifying job 的 `steps:` 下插入 bare `-` null item，focused checker 仍接受完整 workflow；把 required command step 写成 `- name: # YAML null` 也通过，虽然解析后的 `name` 为 null，不满足 optional non-empty `name`。这些 false-pass 允许不可解析、hosted schema 可能拒绝、或超出 declared scalar/step grammar 的 workflow 被记录为有效 CI enforcement evidence，因此尚不能 close out。

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`，HEAD 为 `fbc3729c35e55f8f28e383c5ed7dc2b475f4f3ef`，parent 为 `5ae7601e420346ab821971c2cf30b6b61924f888`。复审开始时 worktree 和 index 均干净。Baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 HEAD 为 22 个 commit、32 个变更文件。
- Review-008 replay: duplicate top-level `on`/`jobs`、duplicate direct event/field/job ID、inline job shadow、second YAML document、nested trigger lookalike、required commands split across jobs、nested raw HTML route/metadata carriers 均返回 nonzero。Direct/quoted/flow branches、quoted constrained keys/job IDs、same-job order 和 `>2-` block scalar positive forms 均 pass。
- Positive verification: 133/133 fixtures pass。Focused、governed 和 auto checks 返回 `errors=[]`。Startup-document budget、launcher syntax、checker/test source parsing、baseline-to-HEAD whitespace 和 isolated frontend production build pass；build transformed 1746 modules and temporary output was removed.
- Runtime and DB: `backend/`、`frontend/`、`strategies/`、`content/`、`data/`、daily runbook 和 Pages publisher 均为 baseline-to-HEAD zero diff。Runbook、publisher 和 tracked DB hashes 分别保持 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`、`752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d` 和 `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`。Read-only DB evidence 为 `integrity_check=ok`、foreign-key violations `0`、market days `46`。
- Backend evidence boundary: runtime/data zero-diff 使 Phase 5 pinned 19/19 evidence 继续适用；本轮未重建已删除的 pinned environment，也不把当前系统环境缺少 `pandas_market_calendars` 的 prerequisite state 记为 fresh pass。
- Authority boundary: provider、broker、tracked-DB update、Tang input、stage、commit、push、publication、hosted verification 和 remote mutation 均未执行或记录为 pass。

## 问题清单

### 严重问题

1. **Flow branch parsing accepts syntactically invalid and non-scalar sequence members**
   - 位置: `scripts/check-operating-modes.py:597-605` and `:607-715`; `docs/operating-modes.md:227-231`.
   - 复现: 将 `.github/workflows/project-harness.yml` 的 block branch list 替换为 `branches: [main,, {bad: value}]`，focused checker 返回 exit `0`、`errors=[]`。独立 YAML 解析返回 flow-node syntax error。再替换为合法 YAML `branches: [main, {bad: value}]`，focused checker仍返回 exit `0`、`errors=[]`；独立解析结果包含 scalar `main` 和 mapping `{"bad": "value"}`。
   - 问题描述: `flow_sequence_values` 只检查首尾方括号并按逗号切分，既不拒绝 empty token，也不验证每个 token 是 declared plain/quoted scalar。`workflow_has_pull_request_main` 随后只检查结果中是否包含字符串 `main`，所以 syntax error、mapping item，以及同类 anchor/alias or undeclared flow member 都可伴随 `main` 绕过 gate。
   - 影响范围: Focused/governed harness 可把 hosted workflow 无法解析或 contract 明确排除的 trigger source 报为有效 PR-main carrier。该状态会让本应保护 lifecycle 的 CI workflow 缺失或拒绝加载，是直接 enforcement false-pass。
   - 改进建议: 对 declared branch flow sequence 做完整、fail-closed 的 constrained tokenization，要求 full consumption、至少一个 item、每个 item 仅为 supported plain/single-quoted/double-quoted scalar，并显式拒绝 empty member、mapping、nested collection、anchor、alias、tag 和 malformed quoting。加入上述两个 exact repro 及 anchor/alias variants 的 negative fixtures。

2. **Null sequence items and semantically null names are skipped inside a qualifying command job**
   - 位置: `scripts/check-operating-modes.py:515-577`，especially `:515-518`、`:533-536`、`:551-566`，以及 qualification at `:578-594`; `docs/operating-modes.md:229-231`.
   - 复现: 在 qualifying job 的 `steps:` 后、现有 command steps 前插入一个同级 bare `-`，focused checker 返回 exit `0`、`errors=[]`；独立 YAML 解析显示 direct steps sequence 的第一个 item 为 null。另将 required fixture step 改为 `- name: # YAML null` followed by its exact `run`，focused checker同样返回 exit `0`、`errors=[]`；独立解析显示该 required step 的 `name` 为 null。
   - 问题描述: Direct-step detection 只识别 `- `，bare `-` 因而被静默忽略，既不建立 step record 也不 disqualify job。`clean_yaml_scalar` 又把未剥离的 source comment `# YAML null` 当作 truthy name，而 YAML semantic value 实际为 null。这违反 required step 只含 optional non-empty `name` 和 one `run` 的 declared grammar，也违反 undeclared workflow source forms fail closed 的边界。
   - 影响范围: Checker 可从包含 hosted schema 可能拒绝的 null step 的 job 提取 required commands，也可把 semantically absent/null name 当作 non-empty。CI carrier 的 source validity 与 checker verdict 再次分离。
   - 改进建议: 枚举并验证 qualifying job 的每个 direct sequence item，bare/null/scalar item 必须 fail closed；对 constrained scalar values 应处理 YAML comments/null semantics and quoted whitespace before the non-empty check。为 bare `-`、comment-null name、quoted-whitespace name 和 malformed direct step 加 negative fixtures。

### 中等问题

无额外中等问题。

### 轻微问题

无额外轻微问题。

## 未验证项

- Hosted workflow and publication: 未授权。Local source inspection 和 build evidence 不能替代 hosted workflow parse、CI execution、Pages publication 或 hosted URL verification。
- Real Data Update receipt: provider provenance、IB whole-day/gap/session evidence、requested-day assemble 1m/5m、Tang JSON、tracked-DB update、data commit/push、Pages run 和 hosted sequence 需要 separate authority and actual execution。
- Reviewer identity and authority truth: constrained fields只能验证结构和 ID inequality；identity、independence truth、user-instruction truth 和 publication authority 仍是 human-validation boundaries。
- Historical pinned backend evidence: 19/19 仅通过 verified runtime zero-diff 继续适用；本轮不是 fresh pinned-environment backend run。

## 裁决理由

remediation-r8 已关闭 implementation-review-008 的全部 recorded findings，并保留此前 lifecycle regressions 和 frozen runtime/data boundaries。但 declared branch flow grammar 仍可接受 syntax error 或 mapping member，qualifying job 又可静默跳过 null step 并误判 null name。两类 repro 都在完整 repository state 上稳定返回 `errors=[]`，且直接削弱 PR-main 和 ordered-command CI evidence。缺陷局限于 constrained workflow parser 和 fixtures，不否定 peer-mode/lifecycle architecture，因此裁决为 `revise` 而非 `reject`，置信度为 `high`。
