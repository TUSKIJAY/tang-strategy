# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r11 at `e4a3faa45d358890515a28a812eb4a15143a3425`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r12`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent acceptance inspection of the stable remediation-r11 commit, parent and exact diff, normative operating-modes contract, active plan, implementation-review-011, checker and all fixtures; exact replay of raw DEL/C1 and escaped-value cases; bounded Unicode source-range and noncharacter probes with independent YAML semantic comparison; replay of prior YAML hierarchy and operative Markdown carriers; focused, governed, auto, startup-budget, backend, syntax, whitespace, frozen-runtime, read-only DB, and isolated frontend-build verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r11 已关闭 `implementation-review-011` 的 exact finding。Raw U+007F、U+0080、U+0084、U+0085、U+0086 和 U+009F double-quoted branch members 均 fail，escaped `\x7F` value 保持 pass。新增 helper 对 raw tab、ASCII printable、BMP scalar 与 supplementary scalar ranges 的处理和实现记录一致。Binary/underscore/leading-zero numerics、terminal colon、valid/malformed YAML escapes、direct hierarchy 与 Markdown operative carriers 的既有正反例也保持预期。145/145 fixtures 全部通过。

但 normative contract 的同一句存在无法同时满足的 Unicode policy。它明确允许 raw U+00A0-U+D7FF、U+E000-U+FFFD 和 U+10000-U+10FFFF，这些 ranges 包含 U+FDD0-U+FDEF 及每个 plane 末尾的 noncharacters；紧接着又声明 raw noncharacters fail closed。实现遵循 allowlist，raw U+FDD0、U+FDEF、U+1FFFE、U+1FFFF、U+10FFFE 和 U+10FFFF 均使完整 checker返回 exit `0`、`errors=[]`。独立 YAML semantic parse接受这些 source，因此不是 hosted parse bypass；但 checker行为与 “noncharacters fail closed” 的 normative clause 不一致。Closeout 前必须选择并固定一个 policy。

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`，HEAD 为 `e4a3faa45d358890515a28a812eb4a15143a3425`。复审开始时 worktree 和 index 均干净。Baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 HEAD 为 28 个 commit、35 个变更文件。
- Review-011 replay: raw DEL/C1 cases返回 nonzero，raw U+0085 也按 declared single-line rule fail；escaped `\x7F` retained positive pass。Raw U+FFFE/U+FFFF fail，ordinary ASCII/BMP printable source保持 pass。
- Prior YAML carriers: numeric/null/boolean/date/terminal-colon/mapping/anchor/alias/tag/malformed quote or escape均 fail；plain/single/double supported strings、quoted terminal colon、valid named/hex/Unicode escapes保持 pass。Unique direct hierarchy、same-job command order和 execution-modifier negatives保持一致。
- Markdown carriers: HTML comments、fenced/indented code、multiline code spans、closed/nested/unclosed raw HTML `code`/`pre` route, metadata, and table carriers保持 non-operative；ordinary canonical links and code-formatted real link labels保持 operative。
- Positive verification: 145/145 fixtures pass。Focused、governed 和 auto checks返回 `errors=[]`。Startup-document budget、launcher syntax、checker/test source parsing和 baseline-to-HEAD whitespace checks pass。Isolated frontend production build transformed 1746 modules and removed its temporary output。
- Backend: current system environment executed 19 tests，18 pass，1 prerequisite error caused only by absent `pandas_market_calendars`。Pinned Phase 5 19/19 evidence remains applicable through verified runtime zero-diff；本轮不把 prerequisite error或 historical result记为 fresh 19/19。
- Runtime and DB freeze: `backend/`、`frontend/`、`strategies/`、`content/`、`data/`、daily runbook 和 Pages workflow 均为 baseline-to-HEAD zero diff。Runbook、publisher 和 tracked DB hashes 保持 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`、`752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d` 和 `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`。Read-only DB evidence 为 `integrity_check=ok`、foreign-key violations `0`、market days `46`。
- Authority boundary: provider、broker、tracked-DB update、Tang input、stage、commit、push、publication、hosted verification 和 remote mutation 均未执行或记录为 pass。

## 问题清单

### 严重问题

无额外严重问题。

### 中等问题

1. **Normative raw-source ranges contradict the noncharacter fail-closed clause**
   - 位置: `docs/operating-modes.md:231`; `scripts/check-operating-modes.py:297-307`.
   - 复现: 将 canonical branch source 替换为 `branches: [main, "x<RAW U+FDD0>y"]`，完整 focused checker返回 exit `0`、`errors=[]`，独立 YAML semantic parse也接受该 source。Raw U+FDEF、U+1FFFE、U+1FFFF、U+10FFFE 和 U+10FFFF 得到相同 checker结果。
   - 问题描述: Contract 的 accepted ranges包含这些 Unicode noncharacters，但同一段随后要求 noncharacters fail closed。`yaml_single_line_source_character_allowed` 精确实现 ranges，没有实现 noncharacter exclusion。当前无法判断 accepted ranges 还是 exclusion clause 是 canonical intent。
   - 影响范围: 这不是 YAML source validity或 hosted CI bypass，因为独立 parser接受 repro；影响是 normative policy、checker和未来 fixtures无法形成单一 truth。任何一方按另一 clause实现都会与合同冲突。
   - 改进建议: 明确选择一个 source policy。若目标是 YAML printable compatibility，删除 “noncharacters” exclusion 并保留现有 allowlist；若 repository policy要额外排除 Unicode noncharacters，则在 helper中拒绝 U+FDD0-U+FDEF 及每个 plane 的 U+FFFE/U+FFFF，并增加 raw/escaped policy fixtures。Contract、checker和 tests必须同步采用同一选择。

### 轻微问题

无额外轻微问题。

## 未验证项

- Hosted workflow execution: 未授权。Local source inspection不能替代 hosted PR workflow run或 check conclusion。
- Real Data Update and publication: provider provenance、IB evidence、requested-day assemble、Tang JSON、tracked-DB mutation、push、Pages和 hosted URL需要 separate authority and actual execution。
- Reviewer identity and authority truth: constrained fields只能验证结构和 ID inequality；identity、independence、user instruction和 publication authority仍是 human-validation boundaries。
- Fresh pinned backend environment: 当前环境缺少 declared dependency，未重建已删除的 pinned environment；historical 19/19仅通过 runtime zero-diff继续适用。

## 裁决理由

remediation-r11 已关闭 implementation-review-011 的 hosted-workflow validity false-pass，并保留 145-fixture lifecycle、YAML hierarchy、Markdown masking与 frozen runtime/data evidence。当前没有新的严重 implementation defect，但 normative contract同时允许并禁止 raw Unicode noncharacters，且 checker只实现其中一条。Implemented plan需要可判定的单一合同才能获得 `accept`；该中等 policy inconsistency必须先修订并复审。问题局限于一句 contract wording或一个 bounded predicate及 fixtures，因此裁决为 `revise` 而非 `reject`，置信度为 `high`。
