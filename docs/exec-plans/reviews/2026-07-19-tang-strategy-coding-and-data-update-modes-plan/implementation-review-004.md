# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md implementation and remediation-r3 at `b3625e907c4ce843f3b9dc52c7376a0bfebb5fca`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r4`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the complete baseline-to-remediation-r3 history, all three remediation diffs, normative lifecycle contract, checker and fixture implementation, replay of every prior finding and specified remediation-r3 case, broader adversarial state and index-row probes, bounded local harness and build checks, read-only DB verification, and frozen runtime/hash comparison
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r3 正确关闭了 `implementation-review-003` 指定的三组问题. `Final disposition: Completed` 即使没有 commit evidence 也必须取得 matching-revision implementation `accept`. `Rejected`, `Terminated` 和 `Superseded` 的明确未实施状态仍可使用 `none` verification. `Design reviews: none` 强制 latest verdict 和 independence 同为 `none`, new-schema design reviews 强制 independence 为 `attested`. 四个 fixed index 的已解析 plan row 也会拒绝非四列结构, Plan cell 的附加文本和第二个 link.

baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 remediation-r3 `b3625e907c4ce843f3b9dc52c7376a0bfebb5fca` 的完整历史和 24 个变更文件均已复核. 三轮 remediation 对应的 prior findings 均保持关闭. 但附加 adversarial probes 发现 Active activation evidence 可以缺少 durable reference, Active next gate 可以为 `none`, fixed index row 的四列约束还可被 empty fifth cell 或无 link 的伪造 row 绕过. 第一项会削弱 activation authority evidence, 后两项会让 canonical lifecycle truth 在 green check 下违反明示 contract. 这些缺口可在现有 schema 和 checker 内局部修复, 因此裁决为 `revise` 而非 `reject`, 但尚不能给出 `accept`.

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`, review HEAD 为 `b3625e907c4ce843f3b9dc52c7376a0bfebb5fca`, baseline 为 `a4b4007a9e529d1748f7f3b9884768471751dc33`. 复审开始时工作树和 index 均干净.
- Specified remediation-r3 replay: `Completed + no review + no commits` fail; non-implemented `Rejected`, `Terminated`, `Superseded` with exact `none` verification pass; `Design reviews: none` with non-none latest or independence fail; reviewed new-schema plan without `attested` fail; all four indexes reject nonempty fifth cells, appended Plan text, and second Plan links.
- Prior finding replay: duplicate metadata key, wrong review type, arbitrary same-basename review target, stale review verdict, stale Active evidence, wrong Completed evidence, bogus optional evidence, invalid gate prefix, and constrained source-boundary cases all produced the required result. Five allowed suffixed Proposed gate families pass, while publish and implementation gates fail.
- Positive verification: 62/62 focused fixtures pass. Governed and auto composed harness checks, startup-document budget, Python syntax, baseline-to-HEAD whitespace check, and isolated frontend production build pass. Frontend build transformed 1746 modules and its temporary output was deleted.
- Runtime and DB: daily runbook, Pages publisher, tracked DB, TV/IB adapters, and rebuild runtime have zero baseline-to-HEAD diff. Runbook, Pages, and DB hashes are `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, and `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. DB `integrity_check=ok`, foreign-key violations 为 0, market days 为 46, before/after hash 相同.
- Authority boundary: provider, broker, tracked-DB update, Tang input, commit, push, publication, hosted verification, and remote mutation均未执行, 也未写成 pass.

## 问题清单

### 严重问题

1. **Active activation evidence 接受空 durable reference**
   - 位置: `scripts/check-operating-modes.py:292-318`; `docs/operating-modes.md:104`, `:115-120`.
   - 问题描述: 合法 Active fixture 的 `Activation evidence` 改为 `user-instruction:` 后, checker 返回 code 0 和 `passed=true`. 实现仅检查 `startswith("user-instruction:")`, 没有验证 colon 后存在 non-empty durable reference, 也没有对整个 value 执行约束匹配.
   - 影响范围: Active lifecycle 可以在没有任何可追溯用户指令 reference 的情况下取得 green result. 这会把 authority evidence 的固定前缀误当成实际 activation evidence, 削弱 proposal-to-activation 的人类授权边界.
   - 改进建议: 对 Active activation 使用 full match, 要求 `user-instruction:` 后为 non-empty, non-`none`, constrained durable reference. 增加 empty suffix, whitespace-only suffix, `none` suffix 的 negative fixtures, 并保留一个合法 durable reference positive fixture.

### 中等问题

1. **Active next gate 的 non-none invariant 未实现**
   - 位置: `scripts/check-operating-modes.py:305-320`; `docs/operating-modes.md:108`, `:117-121`.
   - 问题描述: fixture 将 Active plan, active index, `PROGRESS.md`, and `HANDOFF.md` 的 next gate 全部对账为 `none`, checker 仍返回 code 0 和 `passed=true`. Active branch 只检查 current phase, phase state, and phase entry gate, 没有检查 next gate.
   - 影响范围: canonical truth sources 可以一致地声明没有下一 gate, 同时保持 Active state 和 green lifecycle check. 该结果违反明示的 Active invariant, 并削弱 phase resume point 的确定性.
   - 改进建议: 将 `Next gate` 纳入 Active non-none gate-token validation. 增加 fully reconciled `Active + Next gate: none` negative fixture, 并验证具体错误定位.

2. **Fixed index exact-four row grammar 仍可绕过**
   - 位置: `scripts/check-operating-modes.py:455-476`; `docs/operating-modes.md:142-160`.
   - 问题描述: Active, Proposed, Completed, and Reviews 四个 index 的合法 row 追加 empty fifth cell, 形成 trailing `||`, 四种 fixture 均返回 pass. `line.strip().strip("|")` 会先删除所有 trailing delimiters, 再进行 cell count, 因此 empty fifth cell 消失. 另向四个 index 分别追加 `| Bogus | state | none | gate |` 这类无 Markdown link 的非 header row, 四种 fixture 也均返回 pass, 因为 parser 只验证 `links` 非空的 row.
   - 影响范围: checker 声称的 each fixed state/reviews index row exactly four cells 不是 complete grammar. Extra empty cells 和任意无 link lifecycle rows 可以存在于 canonical indexes 而不被报告.
   - 改进建议: 只移除一个 required leading delimiter 和一个 required trailing delimiter, 保留 interior empty cells 后再执行 exact-four count. 对每个非 header, separator, or exact canonical placeholder row 都执行完整 row validation; 无 standalone canonical Plan link 的 data row 必须 fail. 为四个 index 各增加 empty fifth cell 和 malformed no-link row fixtures.

### 轻微问题

无额外轻微问题.

## 未验证项

- Pinned backend 19/19: 2026-07-19 Phase 6 记录包含 pinned environment evidence, 但该环境不在本复审边界内. 本地解释器独立运行得到 18 pass 和 1 个缺少 `pandas_market_calendars` 的 prerequisite error; backend syntax compilation pass, affected runtime 相对 baseline 为零 diff, tracked DB hash 未变化. 该项未写成 19/19 pass.
- Hosted workflow, publication, and hosted URL: 未授权运行. Local workflow shape 和 build result 不能替代 hosted result.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session evidence, newly requested day assemble 1m/5m, Tang JSON, commit, push, Pages, and hosted sequence 需要独立授权和实际运行.
- Historical identity and authority truth: repository只能验证 reviewer/author IDs 不同和 attestation 结构, 不能独立证明历史身份或用户指令真实性. 本复审 context 未起草或实现被审 revision 和 remediations.

## 裁决理由

remediation-r3 完成了指定修复, 所有 prior findings 在 replay 中保持关闭, 运行时和 DB boundary 也保持冻结. 但 empty activation reference 仍可让 Active state 缺少 durable user instruction, 属于 authority evidence false-pass. Active next gate 和 fixed-row grammar 的 false-pass 则使 canonical lifecycle state 与明示 contract 不一致. 三项均有确定 repro, code-path 原因和局部修复路径. 在这些 negative fixtures 和实现约束补齐前, implementation 不能获得 `accept`. 裁决为 `revise`, confidence 为 `high`.
