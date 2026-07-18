# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r9 at `b5f754b9feed272ea57dad58dfa56c5c553c613b`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r10`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent correctness inspection of the stable remediation-r9 commit, parent and exact diff, normative operating-modes contract, active plan, implementation-review-009, checker and all fixtures; exact replay of review-009 branch-flow, null-step, and null-name findings; bounded adversarial checks of plain and quoted YAML string semantics, flow tokenization, direct job and step hierarchy, and operative Markdown masking; independent YAML semantic comparison; focused, governed, auto, startup-budget, syntax, whitespace, frozen-runtime, read-only DB, and isolated frontend-build verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r9 已关闭 `implementation-review-009` 的 exact findings。Malformed flow `branches: [main,, {bad: value}]`、flow mapping member、anchor/alias/tag、bare null direct step、scalar direct step、comment-null name、null words、ordinary decimal/boolean/date value 和 quoted whitespace 均 fail。Quoted block/flow `main`、quoted comma member、single-quoted trailing-comma flow、direct job hierarchy、same-job command order，以及 nested/unclosed raw Markdown code carriers 的既有正反例保持预期结果。139/139 fixtures 全部通过。

但新增的 bounded correctness probes 显示 constrained YAML string grammar 仍未完整实现合同。Binary and underscore-separated numeric scalars (`0b10`, `1_000`) 在 flow/block branch members 和 required job/step names 中被当作 string 接受，独立 YAML 语义解析却得到 integer。Block member `- bad:` 被当作 plain string 接受，独立解析结果为 mapping `{"bad": null}`；flow member `bad:` 与合法 `main` 并列时也被 checker 接受，但独立解析为 syntax error。以上 repro 均使完整 focused repository check 返回 exit `0`、`errors=[]`。相反，合法 double-quoted YAML escape `branches: ["\x6dain"]` 语义为 string `main`，checker 返回 missing trigger。CI carrier 的 source validity 与合同声明因此仍不一致，不能 close out。

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`，HEAD 为 `b5f754b9feed272ea57dad58dfa56c5c553c613b`，parent 为 `58c58591cf36c1e1f3077fec7d9ee5dc09a56362`。复审开始时 worktree 和 index 均干净。Baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 HEAD 为 24 个 commit、33 个变更文件。
- Review-009 replay: malformed/empty/non-scalar flow members、explicit flow mapping、anchor、alias、tag、unterminated quote、block mapping form already covered by fixtures、bare null/scalar direct steps、comment/null/boolean/decimal/whitespace required-step names 和 comment-null job name 均返回 nonzero。原始两类 finding 已关闭。
- YAML and hierarchy positives: block/flow quoted `main`、single-quoted trailing-comma flow、quoted constrained keys/job IDs、quoted inline command、literal/folded command、explicit block indent、same qualifying job order 和 valid comma inside quoted branch member 均 pass。Duplicate top-level/event/field/job mappings、nested trigger lookalike、cross-job command split、conditions、execution modifiers、wrong runner、nested run、dead shell/heredoc/early-exit 和 non-job steps 保持 fail。
- Markdown carrier replay: HTML comments、fenced/indented code、multiline code spans、closed/nested/unclosed raw HTML `code`/`pre` route, metadata, and table carriers 保持 non-operative；ordinary canonical links and code-formatted real link labels 保持 operative。
- Positive verification: 139/139 fixtures pass。Focused、governed 和 auto checks 返回 `errors=[]`。Startup-document budget、launcher syntax、checker/test source parsing 和 baseline-to-HEAD whitespace checks pass。Isolated frontend production build transformed 1746 modules and removed its temporary output。
- Runtime and DB freeze: `backend/`、`frontend/`、`strategies/`、`content/`、`data/`、daily runbook 和 Pages workflow 均为 baseline-to-HEAD zero diff。Runbook、publisher 和 tracked DB hashes 保持 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`、`752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d` 和 `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`。Read-only DB evidence 为 `integrity_check=ok`、foreign-key violations `0`、market days `46`。
- Backend evidence boundary: runtime/data zero-diff 使 Phase 5 pinned 19/19 evidence 继续适用；本轮未重建已删除的 pinned environment，也不把未重跑项记录为 fresh pass。
- Authority boundary: provider、broker、tracked-DB update、Tang input、stage、commit、push、publication、hosted verification 和 remote mutation 均未执行或记录为 pass。

## 问题清单

### 严重问题

1. **Numeric YAML scalars bypass the declared string-only branch and name grammar**
   - 位置: `scripts/check-operating-modes.py:297-344`, `:547-550`, `:594-597`, `:625-628`, `:660-711`, and `:821-824`; `docs/operating-modes.md:229-231`.
   - 复现: 将 branch block 改为 `branches:` followed by `- main` and `- 0b10`，或改为 `branches: [main, 1_000]`，完整 focused checker 均返回 exit `0`、`errors=[]`。独立 YAML 语义解析分别得到 integer `2` 和 `1000`，而非 string。将 required command step name 改为 `name: 0b10`，或将 qualifying job name 改为 `name: 1_000`，同样返回 exit `0`、`errors=[]`。
   - 问题描述: `constrained_yaml_string` 的 numeric regex 只覆盖 decimal、hex、octal 和部分 float 形式，遗漏 YAML binary integer 与 underscore-separated number。合同明确要求 branch members 为 non-empty string，并要求 numeric coercions 在 required names 中 fail closed。
   - 影响范围: Branch filters 可包含 workflow schema 不接受的 numeric member，同时 checker仍认定 PR-main CI carrier 有效；required job/step name 的 string-only evidence 也可被 numeric coercion 绕过。前者可能使 hosted workflow 拒绝加载，属于 CI enforcement false-pass。
   - 改进建议: 将 supported plain scalar grammar 改为 positive string grammar，或完整排除 YAML core-schema numeric forms，包括 binary、underscore grouping 及其他合法 numeric spellings。Branch members 与 job/step names 必须共用同一语义验证。加入 flow/block `0b10`、`1_000` 和 name variants 的 negative fixtures。

2. **Implicit mapping indicators remain accepted as branch strings**
   - 位置: `scripts/check-operating-modes.py:325-343`, `:660-711`, and `:814-824`; `docs/operating-modes.md:227-231`.
   - 复现: 在 block branch list 的 valid `- main` 后加入 `- bad:`，完整 focused checker 返回 exit `0`、`errors=[]`；独立 YAML 解析得到 mapping `{"bad": null}`。Flow form `branches: [main, bad:]` 也返回 exit `0`、`errors=[]`，而独立 YAML parser 报 syntax error。
   - 问题描述: Plain-scalar filter仅拒绝 colon followed by whitespace，没有拒绝 terminal colon。Block context 中 terminal colon 是 implicit mapping key，flow context 中该 source 不是完整 scalar。`constrained_yaml_string` 因而把 mapping 或 malformed source 当作普通 string。
   - 影响范围: 合同明确排除 mapping members 和 malformed workflow source，但两种 source 都能伴随 valid `main` 让 PR trigger gate 通过。Hosted workflow 可能被拒绝或具有非字符串 branch member，造成直接 CI carrier false-pass。
   - 改进建议: 在 block/flow branch context 中拒绝 plain item 的 mapping indicators，并要求 token 可由 declared YAML string subset完整消费。加入 block `- bad:`、flow `[main, bad:]` 及 quoted `"bad:"` retained-positive fixture，确保只拒绝未引用 indicator。

### 中等问题

1. **Valid YAML double-quoted escape is rejected as a branch string**
   - 位置: `scripts/check-operating-modes.py:303-308` and `:660-711`; `docs/operating-modes.md:227-231`.
   - 复现: `branches: ["\x6dain"]` 由独立 YAML 语义解析为 string `main`，但完整 focused checker 返回 missing required pull-request trigger。
   - 问题描述: Double-quoted scalars are decoded with a JSON string grammar, which excludes YAML's valid `\xNN` escape. Contract declares double-quoted YAML string members without documenting this narrower escape subset。
   - 影响范围: Harmless equivalent YAML spelling can make governance validation fail even though the workflow trigger semantically includes `main`。这是 fail-closed false-rejection，不会绕过 CI，因此分级为中等。
   - 改进建议: 明确定义并测试 double-quoted source subset，或实现 YAML-compatible escape decoding for the declared string carrier。加入 `\xNN` positive fixture 和 invalid escape negative fixture。

### 轻微问题

无额外轻微问题。

## 未验证项

- Hosted workflow execution: 未授权。Local source inspection 不能替代 hosted parser、PR workflow run 或 check conclusion。
- Real Data Update and publication: provider provenance、IB evidence、requested-day assemble、Tang JSON、tracked-DB mutation、push、Pages 和 hosted URL 需要 separate authority and actual execution。
- Reviewer identity and authority truth: constrained fields只能验证结构和 ID inequality；identity、independence、user instruction 和 publication authority 仍是 human-validation boundaries。
- Historical pinned backend evidence: 19/19 仅通过 verified runtime zero-diff 继续适用；本轮不是 fresh pinned-environment backend run。

## 裁决理由

remediation-r9 已关闭 implementation-review-009 的 recorded false-passes，并保留 139-fixture lifecycle、hierarchy、Markdown masking 和 frozen runtime/data evidence。但 binary/underscore numeric scalars 与 implicit mapping indicators 仍能进入 string-only branch carrier并让完整 checker保持 green，且 valid YAML double-quoted escape 被反向拒绝。前两项是 deterministic CI enforcement false-pass，阻止 implementation closeout。缺陷集中在 constrained YAML scalar grammar 与 fixtures，不否定 peer-mode/lifecycle architecture，因此裁决为 `revise` 而非 `reject`，置信度为 `high`。
