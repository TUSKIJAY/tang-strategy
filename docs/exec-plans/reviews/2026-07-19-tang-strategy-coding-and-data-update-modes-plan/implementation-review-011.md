# 交付物评审意见

**审核对象**: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md` implementation and remediation-r10 at `ff00efdeb1c1f17d5ed6dbd89c6acf491a320bca`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r11`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent correctness inspection of the stable remediation-r10 commit, parent and exact diff, normative operating-modes contract, active plan, implementation-review-010, checker and all fixtures; exact replay of binary, underscore and leading-zero numeric branch/name, terminal-colon branch, YAML hex-escape positive, and malformed-escape negative cases; bounded adversarial inspection of single-line YAML double-quoted decoding, YAML 1.1/1.2 numeric classification, plain/single/double string consistency, workflow direct hierarchy, and operative Markdown carriers; independent YAML semantic comparison; focused, governed, auto, startup-budget, backend, syntax, whitespace, frozen-runtime, read-only DB, and isolated frontend-build verification
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r10 已关闭 `implementation-review-010` 的全部 recorded findings。Flow/block `0b10`、`0B10`、`1_000`、`008` 和 numeric required job/step names 均 fail；unquoted flow/block terminal colon 均 fail，quoted terminal colon 保持 string positive；`branches: ["\x6dain"]` 正确归一为 `main` 并 pass，malformed escape、surrogate 和 out-of-range Unicode escape 均 fail。143/143 fixtures 通过，plain/single/double string、direct hierarchy、same-job order 和 Markdown operative carrier 的既有正反例保持一致。

但新增的 bounded decoder probe 发现 single-line YAML double-quoted source 仍可包含 YAML 禁止的 raw character。将 branch flow 改为 valid `main` 加一个 double-quoted member whose interior contains raw U+007F、U+0080、U+0084、U+0086 或 U+009F，完整 focused checker 均返回 exit `0`、`errors=[]`；独立 YAML semantic parser 对每个 source 均返回 syntax error。Decoder 当前只拒绝部分 U+0000-U+001F control characters，未实现 YAML printable-character ranges。该 false-pass 允许 hosted workflow 无法解析时本地 governance 仍为 green，因此尚不能 close out。

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`，HEAD 为 `ff00efdeb1c1f17d5ed6dbd89c6acf491a320bca`。复审开始时 worktree 和 index 均干净。Baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 HEAD 为 26 个 commit、34 个变更文件。
- Review-010 replay: flow/block binary、underscore、leading-zero numeric members，numeric job/required-step names，flow/block terminal-colon source 均返回 nonzero。Quoted terminal colon、YAML `\x6d` main、valid comma inside quoted member 和 single-quoted trailing-comma flow 均 pass。Malformed `\q`、surrogate `\uD800` 和 out-of-range `\U00110000` 均返回 nonzero。
- Numeric and string boundary: declared decimal、binary、octal、hex、underscore、exponent、float、sexagesimal 和 leading-zero fixtures fail as coercions；plain/single/double ordinary strings保持 pass。Quoted whitespace、null words、boolean、date、source-comment value 和 scalar/null direct step保持 fail。
- Workflow hierarchy: duplicate top-level/event/field/job mappings、nested trigger lookalike、cross-job split、conditions、execution modifiers、wrong runner、nested run、dead shell/heredoc/early-exit 和 non-job steps 均 fail；unique direct same-job command order保持 pass。
- Markdown carriers: HTML comments、fenced/indented code、multiline code spans、closed/nested/unclosed raw HTML `code`/`pre` route, metadata, and table carriers保持 non-operative；ordinary canonical links and code-formatted real link labels保持 operative。
- Positive verification: 143/143 fixtures pass。Focused、governed 和 auto checks 返回 `errors=[]`。Startup-document budget、launcher syntax、checker/test source parsing 和 baseline-to-HEAD whitespace checks pass。Isolated frontend production build transformed 1746 modules and removed its temporary output。
- Backend: current system environment executed 19 tests，18 pass，1 prerequisite error caused only by absent `pandas_market_calendars`。Pinned Phase 5 19/19 evidence remains applicable through verified runtime zero-diff；本轮不把 prerequisite error 或 historical result记为 fresh 19/19。
- Runtime and DB freeze: `backend/`、`frontend/`、`strategies/`、`content/`、`data/`、daily runbook 和 Pages workflow 均为 baseline-to-HEAD zero diff。Runbook、publisher 和 tracked DB hashes 保持 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`、`752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d` 和 `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`。Read-only DB evidence 为 `integrity_check=ok`、foreign-key violations `0`、market days `46`。
- Authority boundary: provider、broker、tracked-DB update、Tang input、stage、commit、push、publication、hosted verification 和 remote mutation 均未执行或记录为 pass。

## 问题清单

### 严重问题

1. **Raw characters forbidden by YAML are accepted inside double-quoted branch strings**
   - 位置: `scripts/check-operating-modes.py:297-352`, especially the raw-character check at `:326-327`; `docs/operating-modes.md:231`.
   - 复现: 将 canonical branch source 替换为 `branches: [main, "x<RAW U+007F>y"]`，其中 `<RAW U+007F>` 是文件中的实际 code point 而非 escape text。完整 focused checker 返回 exit `0`、`errors=[]`，独立 YAML semantic parse 返回 syntax error。Raw U+0080、U+0084、U+0086 和 U+009F 得到相同结果。
   - 问题描述: `decode_yaml_double_quoted` 仅拒绝 `ord(character) < 0x20` 且非 tab 的 raw characters，并显式拒绝 unescaped quote。YAML raw character set 还排除 U+007F-U+0084 和 U+0086-U+009F；这些 code points 只能在允许的 escape/value rules 下表达，不能作为当前 source 中的 raw character。
   - 影响范围: Workflow source 可包含 YAML parser直接拒绝的 character，同时本地 focused/governed checker仍认定 PR-main trigger 和 ordered command carrier有效。Hosted workflow可能完全无法加载，属于 CI enforcement false-pass。
   - 改进建议: 在 single-line decoder 中实现 YAML printable-character allowlist，而不是只排除 C0 controls。Source 层允许 raw tab、U+0020-U+007E、U+00A0-U+D7FF、U+E000-U+FFFD 和 valid supplementary scalar values；按 single-line contract拒绝 line-break characters，并继续拒绝 surrogate/non-scalar values。加入 raw U+007F/U+0080/U+009F negative fixtures，同时保留 escaped `\x7F` string positive以区分 raw source validity 与 decoded value。

### 中等问题

无额外中等问题。

### 轻微问题

无额外轻微问题。

## 未验证项

- Hosted workflow execution: 未授权。Local source inspection不能替代 hosted YAML parse、PR workflow run 或 check conclusion。
- Real Data Update and publication: provider provenance、IB evidence、requested-day assemble、Tang JSON、tracked-DB mutation、push、Pages 和 hosted URL需要 separate authority and actual execution。
- Reviewer identity and authority truth: constrained fields只能验证结构和 ID inequality；identity、independence、user instruction 和 publication authority仍是 human-validation boundaries。
- Fresh pinned backend environment: 当前环境缺少 declared dependency，未重建已删除的 pinned environment；historical 19/19 仅通过 runtime zero-diff继续适用。

## 裁决理由

remediation-r10 已关闭 implementation-review-010 的 numeric、mapping-indicator 和 YAML escape findings，并保留 143-fixture lifecycle、hierarchy、Markdown masking 与 frozen runtime/data evidence。但 raw U+007F-U+009F prohibited source characters仍可进入 declared YAML double-quoted branch carrier并让完整 checker保持 green。这是 deterministic hosted-workflow validity false-pass，阻止 implementation closeout。缺陷局限于 single-line decoder 的 source-character allowlist 与 fixtures，不否定 peer-mode/lifecycle architecture，因此裁决为 `revise` 而非 `reject`，置信度为 `high`。
