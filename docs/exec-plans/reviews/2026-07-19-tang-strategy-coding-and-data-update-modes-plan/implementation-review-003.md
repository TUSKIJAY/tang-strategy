# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md implementation and remediation-r2 at `8a93fcd20ea32ed8d09049091b9f16bd8445dbd0`

- Review target: `docs/exec-plans/active/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: implementation
- Reviewer ID: `independent-implementation-reviewer-2026-07-19-r3`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: fresh independent inspection of the baseline-to-remediation-r2 history, both remediation diffs, normative lifecycle contract, checker and fixture implementation, replay of all prior adversarial cases, additional metadata and fixed-row probes, bounded local harness and build checks, read-only DB verification, and frozen runtime/hash comparison
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

remediation-r2 正确关闭了 `implementation-review-002` 指定的 optional-evidence 和 gate-prefix 问题. 首次 review 前且无 review directory 的 Proposed plan 可以使用 `none` evidence; bogus evidence link 会 fail. 未实施且 `Final disposition: Rejected` 的 Completed lifecycle plan 可以使用 `none` verification; bogus verification link 会 fail. Reviews index 现在要求每个 plan 一行, empty artifact set 使用 canonical plan link 加 `none` / `none`. 五类 Proposed gate 均接受带 delimiter 的 suffix, `publish-now` 和 `implementation-start` 均被拒绝.

上一轮之前的 duplicate key, wrong review type, arbitrary same-basename target, wrong artifact directory, stale reviews verdict/artifact set, stale Active evidence, wrong Completed evidence 和 unconstrained source scanning findings 也继续保持关闭. 但 fresh adversarial probes 发现 checker 仍可让 `Final disposition: Completed` 在没有 implementation review 和两个 commit evidence 均为 `none` 时通过. 该条件与 active plan 明示的 Completed disposition 必须先取得 `accept` 相冲突. 另有 plan metadata 组合与 fixed index row grammar 的 false-pass. 这些缺口可在现有设计内局部修复, 因此不适用 `reject`, 但 closeout authority 尚不足以支持 `accept`.

## 已验证项

- Stable boundary: baseline 为 `a4b4007a9e529d1748f7f3b9884768471751dc33`, remediation-r1 为 `6c108feaa0870c3c363349088b6333a3c8f51f6f`, remediation-r2 HEAD 为 `8a93fcd20ea32ed8d09049091b9f16bd8445dbd0`. 历史线性, 复审开始时工作树和 index 均干净.
- Prior finding replay: 两轮评审列出的 authority, evidence, path, index, gate 和 constrained-boundary cases 均得到预期结果. Comment-only adapter token 与 behavior-equivalent multiline adapter 均不影响 lifecycle result.
- Remediation-r2 replay: truthful pre-review Proposed, canonical empty reviews row, truthful non-implemented Rejected Completed 和五类 suffixed Proposed gate 均 pass; bogus Proposed/Completed links, empty reviews row 指向 directory, missing reviews row, `publish-now` 和 `implementation-start` 均 fail with specific errors.
- Positive verification: 55/55 fixtures, focused checker, governed/auto composed checks, startup-document budget, launcher syntax, Python syntax, baseline-to-HEAD whitespace 和临时目录 frontend production build均通过. Frontend build transformed 1746 modules, 临时输出已删除.
- Runtime and DB: daily runbook, Pages publisher, tracked DB, TV/IB adapters 和 rebuild runtime 相对 baseline 均为零 diff. Frozen runbook, Pages 和 DB hashes 分别为 `bc7f2fe36b9f5be06ff1fcd43b2f81ea053b64784a2532cfe0a4bf6806ee3aac`, `752459988433320587963c33f18cff6c572bcb2598be94cc610b64d61599277d`, `76a885c2c04749e9cc5d7b5d6f75bfd15fff9939cb47d2b05c806b4c68ba28f8`. DB `integrity_check=ok`, foreign-key violations 为 0, market days 为 46, before/after hash 相同.
- Authority boundary: provider, broker, tracked-DB update, Tang input, push, Pages, hosted verification 和其他 remote action 均未执行, 也未写成 pass.

## 问题清单

### 严重问题

1. **Completed disposition 可绕过必需的 implementation accept**
   - 位置: `scripts/check-operating-modes.py:310-315`; `docs/operating-modes.md:117-122`; active plan `Section 7.1`, `Section 9.1`, `Section 13`.
   - 问题描述: checker 仅在 `Verified implementation commit != none` 或 `Implementation review != none` 时将 Completed lifecycle plan 视为 implemented. 独立 fixture 从合法 non-implemented Rejected case 出发, 只把 plan 和 completed index 的 disposition 改为 `Completed`, 保持 `Implementation review: none`, `Verified implementation commit: none`, `Lifecycle reconciliation commit: none`, verification `none`; checker 返回 code 0 和 `passed=true`. 该 implemented predicate 使用 review evidence 自身判断是否需要 review, 形成循环. Plan 又允许未授权 commit 时 commit field 为 `none`, 所以 commit absence 不能证明没有实施.
   - 影响范围: 已实施但未获 commit authority 的工作可以声明 `Final disposition: Completed`, 省略独立 `accept`, 并取得 green lifecycle closeout. 这直接绕过本计划 Phase 6 的核心 authority gate.
   - 改进建议: 使用不依赖 review/commit evidence 的 implemented classification. 在现有 schema 下至少将 `Final disposition: Completed` 确定为 implemented 并强制 `<path>@accept`, 即使两个 commit fields 为 `none`; 若其他 disposition 也可能包含实施工作, 应增加受约束的 implementation-outcome 字段并经过 plan revision. 增加 `Completed + no review + no commits` 必须 fail, `Rejected/Terminated/Superseded + explicit non-implemented state` 才可使用 `none` 的 fixtures.

### 中等问题

1. **无 design review 时的 plan metadata 可声明虚假 verdict 和 independence**
   - 位置: `scripts/check-operating-modes.py:229-260`, `:281-293`; `docs/operating-modes.md:93-121`.
   - 问题描述: `Design reviews: none` 的 Proposed fixture 分别改为 `Latest design verdict: approve` 或 `Review independence: attested` 后, 两者都返回 pass. Checker 只在 reviews 非空时对账 latest verdict, Proposed state 也不约束这两个字段的组合.
   - 改进建议: 新 schema 中 `Design reviews: none` 必须同时要求 `Latest design verdict: none` 和 `Review independence: none`. Reviews 非空时应要求 latest verdict 与最后 entry 一致, 并使 independence 与 qualifying structured review evidence 一致. 增加两类矛盾 metadata 的 negative fixtures.

2. **Fixed index Plan cell 只解析首个 link, 不执行 exact row grammar**
   - 位置: `scripts/check-operating-modes.py:440-452`, `:479-580`; `docs/operating-modes.md:142-160`; active plan `Section 7.1`.
   - 问题描述: empty reviews row 的 Plan cell 使用 canonical plan link 后再追加指向 `plan-template.md` 的第二个 link, checker 仍 pass. Proposed state row 的 Plan cell 使用相同方式也 pass. Parser 只用 `LINK_RE.search` 提取首个 link, 因此没有实现 each plan link exactly once 和 exact plan-link set.
   - 改进建议: 对每类 fixed row 强制 exact cell count 与 cell-specific full match. Plan cell 必须恰有一个 canonical link且无附加文本或第二个 link. 增加 no-review reviews row 和 state-index row 的 extra-link negative fixtures.

### 轻微问题

无额外轻微问题.

## 未验证项

- Pinned backend 19/19: 2026-07-19 Phase 6 evidence记录 pinned environment 通过, 但该临时环境已删除. 当前解释器独立运行得到 18 pass 加 1 个缺少 `pandas_market_calendars` 的 prerequisite error; backend compile通过, tracked DB hash 未变化. 该项未写成独立 19/19 pass.
- Hosted workflow, publication 和 hosted URL: 未授权运行. Local workflow shape 与 job names通过, 不能替代 hosted result.
- Real Data Update receipt: provider provenance, IB whole-day/gap/session, newly requested day assemble 1m/5m, Tang JSON, push, Pages 和 hosted sequence 仍需未来单独授权.
- Historical identity and authority truth: repository可以验证 reviewer/author IDs 不同和 attestation 结构, 不能单独证明历史身份或用户指令真实性. 本复审 context 未起草或实现被审 revision/remediations.

## 裁决理由

remediation-r2 的指定目标已完成, 两轮已知 findings 也保持关闭. 但 `Final disposition: Completed` 无 implementation review 仍可 green, 会绕过实施完成前必需的独立 `accept`; metadata 和 fixed-row false-pass 也与 deterministic constrained-format 目标不符. 修复不需要重新设计 peer modes 或 Data Update contract, 但必须先补足 classification, consistency 和 exact-row fixtures 后再复审. 裁决为 `revise`, confidence 为 `high`.
