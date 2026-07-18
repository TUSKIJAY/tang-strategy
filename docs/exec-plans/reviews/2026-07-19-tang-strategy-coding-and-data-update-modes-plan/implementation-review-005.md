# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md implementation and remediation-r4 at `68f117f84e6cc72fa27bbbe90f8a2f196d404088`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r5`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the complete baseline-to-remediation-r4 history, all four remediation diffs and review boundaries, normative contract, checker and fixtures, replay of every prior finding and remediation-r4 target case, broader adversarial plan/review/index/roadmap/current-block/config/workflow probes, bounded local harness and build checks, read-only DB verification, and frozen runtime/hash comparison
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r4 正确关闭了 `implementation-review-004` 指定的三项问题. Empty `user-instruction:` 和 fully reconciled Active `Next gate: none` 均 fail. 四个 index 的 trailing empty fifth cell 均 fail. 普通 arbitrary no-link row, duplicate/mixed sentinel, nonempty extra cell, appended Plan text, second Plan link, and malformed Plan cell 均 fail. Canonical empty state/reviews sentinels pass. 此前四轮 review 的 duplicate metadata, review type/target/evidence, optional evidence, gate grammar, Completed classification, design-review consistency, Plan-cell grammar, and unconstrained runtime-source boundary findings 也保持关闭.

baseline `a4b4007a9e529d1748f7f3b9884768471751dc33` 到 remediation-r4 `68f117f84e6cc72fa27bbbe90f8a2f196d404088` 的线性历史, 14 个 commit, 26 个变更文件, 四个 review boundary, and 四个 remediation diff 均已复核. 但附加 adversarial probes 发现 required workflow/router carrier 可以只存在于 comment, empty-index/header grammar 仍可绕过, current-state markers 可以逆序, new-schema historical review 可以绕过 structured reviewer metadata. 第一项会让 CI enforcement 和 authority route 在 green governed result 下失效. 其余三项违反 constrained-format package 的 exactness. 这些问题可在现有 checker 内修复, 因此裁决为 `revise` 而非 `reject`, 但 implementation 尚不能获得 `accept`.

## 已验证项

- Stable boundary: branch 为 `codex/project-harness`, review HEAD 为 `68f117f84e6cc72fa27bbbe90f8a2f196d404088`, baseline 为 `a4b4007a9e529d1748f7f3b9884768471751dc33`. 复审开始时工作树和 index 均干净.
- Prior finding replay: 22/22 independently reconstructed cases produced the required result. Duplicate key, wrong design type, arbitrary same-basename target, stale reviews verdict, bogus optional evidence, illegal publish/implementation gates, `Completed + no accept + no commits`, contradictory no-review metadata, and reviewed new-schema plan without attestation fail. Truthful pre-review Proposed, non-implemented `Rejected`/`Terminated`/`Superseded`, all five suffixed Proposed gate families, comment-token boundary, and behavior-equivalent adapter refactor pass.
- Remediation-r4 replay: empty activation and reconciled Active `Next gate: none` fail; four trailing empty fifth-cell cases fail; ordinary no-link rows in all four indexes fail; duplicate/mixed sentinels, extra cells, and malformed Plan cells fail; canonical state/reviews sentinel forms pass.
- Positive verification: 67/67 focused fixtures pass. Focused, governed, and auto composed checks, startup-document budget, launcher syntax, Python syntax, baseline-to-HEAD whitespace check, and isolated frontend production build pass. Frontend build transformed 1746 modules and its temporary output was deleted.
- Runtime and DB: daily runbook, Pages publisher, tracked DB, TV/IB adapters, and rebuild runtime have zero baseline-to-HEAD diff. Runbook, Pages, and DB hashes are `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, and `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. DB `integrity_check=ok`, foreign-key violations 为 0, market days 为 46, before/after hash 相同.
- Authority boundary: provider, broker, tracked-DB update, Tang input, commit, push, publication, hosted verification, and remote mutation 均未执行, 也未写成 pass.

## 问题清单

### 严重问题

1. **Required workflow and router carriers 接受 comment-only token**
   - 位置: `scripts/check-operating-modes.py:886-895`, `:916-945`; active plan Section 3.6, Section 7.1, Phase 4 execution record.
   - 问题描述: temporary governed fixture 将 workflow 中 canonical harness 和 fixture test 的两个 executable `run:` steps 都改成 YAML comments, 仅保留 `# run: <command>` text. Focused checker 和 composed governed harness 均返回 code 0 和 `passed=true`. 另一个 fixture 删除 `AGENTS.md` 的实际 route, 只保留 `<!-- docs/operating-modes.md -->`, 也返回 pass. 实现使用 unrestricted substring membership and `.index`, 不区分 executable step, actual Markdown route, or comment/dead text.
   - 影响范围: PR workflow 可以不再执行 lifecycle checker/fixtures, compact authority router 也可以失去规范入口, 而 governed result 仍为 green. 这直接削弱 Phase 4 声明的 CI enforcement 和 single normative route.
   - 改进建议: 对 project workflow 只接受实际 job step 的 constrained `run` value, 明确处理 supported inline/block forms and order, 并拒绝 comment-only occurrences. Router 应验证非-comment canonical Markdown link or other explicitly constrained route form. 增加 comment-only workflow/router negative fixtures and one supported positive form per carrier.

### 中等问题

1. **Empty-index and reserved-header grammar 仍非 exact**
   - 位置: `scripts/check-operating-modes.py:463-501`; `docs/operating-modes.md:143-147`.
   - 问题描述: 删除 empty Proposed sentinel or empty Completed sentinel 后, checker pass. 在 zero-plan fixture 中删除 empty Reviews sentinel 后也 pass. Parser 仅限制 `sentinel_count > 1` and sentinel/plan mixing, 没有在 zero rows 时要求 `sentinel_count == 1`. 另向 Active index 追加 `| Plan | forged | x | y |` or `| Decision | forged | x | y |`, 或给 canonical header 增加第五列, 均 pass, 因为 first cell 为 `Plan`/`Decision` 的任意 row 都被跳过. Missing terminal delimiter 的 plan/sentinel rows 也 pass.
   - 影响范围: remediation-r4 的 ordinary no-link fixture 已关闭, 但保留字可绕过同一规则. Empty lifecycle surface 又可以省略 contract 明示的 canonical sentinel, 使 exact fixed-table package 仍有多种 green representation.
   - 改进建议: 每个 index 应验证 exactly one canonical header and separator, then validate every remaining table-like row. Empty plan set requires exactly one state/reviews sentinel; non-empty set requires zero sentinels. `Decision` 只在定义该 header 的 table 中合法. 若 contract 要求 closing delimiter, 应对整行 full match. 为四个 index 增加 missing sentinel, reserved-header masquerade, header extra-cell, and malformed-delimiter fixtures.

2. **Current-state block 接受逆序 marker pair**
   - 位置: `scripts/check-operating-modes.py:798-820`; `docs/operating-modes.md:165-177`.
   - 问题描述: `PROGRESS.md` and `HANDOFF.md` 各包含一个 end marker followed by one start marker, with canonical five fields after start and no closing marker after those fields. 两个 fixture blocks 完全一致, checker 返回 code 0 和 `passed=true`. 实现只计算 each marker count, then takes everything after start when no later end exists.
   - 影响范围: malformed and effectively unclosed current-state blocks can satisfy canonical reconciliation. Marker pair 不再界定 parser authority boundary, 后续 prose 可能被误纳入或被 silent ignore.
   - 改进建议: require exactly one start before exactly one end, parse only the bounded interval, and reject any missing, reversed, nested, or overlapping marker form. 增加 reversed-order and no-closing-after-start negative fixtures.

3. **New-schema prior-revision review 可绕过 structured metadata**
   - 位置: `scripts/check-operating-modes.py:274-290`, `:356-432`; `docs/operating-modes.md:123-141`; active plan Section 3.2.
   - 问题描述: new-schema Active fixture 使用 bare `review-001` at old revision `r1`, 其 body 只有 prose verdict, then adds fully structured matching `review-002@approve@r2`. Reviews index lists both and Active evidence points to review-002. Checker returns code 0 and `passed=true`, because any design review whose target revision differs from plan revision gets `allow_legacy=true`. Contract 明示 bare review exception 仅适用于 explicitly migrated `operating-modes-legacy-v1` completed plans.
   - 影响范围: new-schema review history 可以省略 target, type, reviewer/author IDs, independence, evidence method, and confidence while 仍被 artifact set and plan metadata 接受. 这削弱 review audit trail 的结构完整性, 即使 matching-revision Active approve 仍为 structured.
   - 改进建议: `allow_legacy` 只能由 `plan.schema == operating-modes-legacy-v1` and completed state 触发, 不应由 revision inequality 触发. New-schema plan 的所有 declared reviews 都必须具备 complete constrained metadata. 增加 old-revision bare review in new-schema negative fixture and migrated legacy completed positive fixture.

### 轻微问题

无额外轻微问题.

## 未验证项

- Pinned backend 19/19: 2026-07-19 Phase 6 记录包含 pinned environment evidence, 但该环境不在本复审边界内. 本地解释器独立运行得到 18 pass and 1 个缺少 `pandas_market_calendars` 的 prerequisite error; backend syntax compilation pass, affected runtime 相对 baseline 为零 diff, tracked DB hash 未变化. 该项未写成 19/19 pass.
- Hosted workflow, publication, and hosted URL: 未授权运行. Local workflow shape and build result 不能替代 hosted result.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session evidence, newly requested day assemble 1m/5m, Tang JSON, commit, push, Pages, and hosted sequence 需要独立授权和实际运行.
- Historical identity, evidence quality, and authority truth: repository只能验证 constrained fields and structural relationships, 不能独立证明 reviewer identity, evidence quality, or user instruction truth. Syntax-only cases such as non-empty reviewer/evidence tokens remain human validation boundaries.

## 裁决理由

remediation-r4 完成了指定修复, 67 fixtures and every prior finding replay 均保持预期结果, runtime and DB boundary 也保持冻结. 但 comment-only workflow steps can preserve a green governed result after CI enforcement is removed, 属于 execution-carrier false-pass. Empty-index/header grammar, reversed current-state markers, and new-schema bare review exception 进一步证明 constrained-format exactness 尚未闭合. 四项都有确定 repro, direct code path, and bounded remediation path. 在新增 negative fixtures and implementation constraints 通过独立复审前, implementation 不能获得 `accept`. 裁决为 `revise`, confidence 为 `high`.
