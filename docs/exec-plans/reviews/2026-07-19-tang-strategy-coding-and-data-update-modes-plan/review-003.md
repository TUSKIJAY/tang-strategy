# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v2-review-foldback-2026-07-19`
- Review type: design
- Reviewer ID: `design-reviewer-r3-2026-07-19`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: independent re-read of exact v2 plan; re-run governed harness and startup-doc budget; re-anchor Section 1 drift claims via `git show 2454ccb7...` on PROGRESS/HANDOFF/roadmap; re-check TV/IB import-before-rebuild and rebuild fail-closed paths against prior baseline; map every Section 9 matrix row to a declared carrier; compare foldback against review-001 and review-002 severe/medium findings
- Verdict: approve
- Confidence: high

## 整体判断

**裁决**: approve
**置信度**: high

## 总体评价

revision `v2-review-foldback-2026-07-19` 把 v1 两份 `revise` 的阻塞点折成可执行设计, 而不是换措辞回避. Constrained Format Package(Section 3.2-3.4)给出 checker 唯一可解析面; transition helper 整段移出范围并改 manual + read-only checker(Section 7.2); Section 3.5 给出最小 reviewer-independence 合同及机检/人检边界; Section 9 全部 40 行矩阵均有 Verification carrier; 文件清单覆盖 authority map、四索引、completed 元数据-only reconcile、新 decision, 并明确 runbook/runtime 只读. Coding lane 与 proposal stage 拆分, 5.3 硬路由, activation recording 与 Phase 0 implementation start 分离, fetch 直写 tracked DB 与 IB quality 证据分层均已写入契约.

基线诊断仍可独立复现: HEAD `2454ccb7fc1c927f2a52a3bd2db7debe41998594` 上 PROGRESS/HANDOFF/roadmap 的过时 Git/生命周期声明属实; 现有 harness checker governed 下 `passed=true`、`errors=[]`、21 artifact present; startup-doc budget 通过. 双模式骨架、TV-first/publish 分离、非第二状态库、动态 Git vs durable 证据等与仓库现行契约一致.

残留项均为实施期可在 gate 内消化的细节(测试包导入路径、多计划 concurrent 时 current-plan 单槽语义、gate-token 词表封闭性等), 不构成 activation 前必须再改方案正文的严重或成组中等问题. 裁决为 `approve`.

## 已核实事实

- 计划 `Revision` = `v2-review-foldback-2026-07-19`; `Plan author ID` = `codex-plan-author-2026-07-19`; 本评审 `Reviewer ID` 与之不同, 且本上下文未起草该 v2 正文.
- `git show 2454ccb7...:PROGRESS.md` / `HANDOFF.md` / `docs/exec-plans/roadmap.md` 复现 Section 1 三条漂移锚点; `a70be643` 与 `2454ccb7` 的 commit 存在性此前已核对.
- `python3 scripts/check-project-harness.py --root . --profile governed` → passed, errors=[]; startup-doc budget hard limit 未超.
- Section 9.1: 21 行, 均有 carrier; Section 9.2: 19 行, 均有 carrier; 无空载体行.
- 严重问题折回对照:
  - 受约束格式: Section 3.2-3.4 完整定义, Phase 1 具名交付, checker 禁 prose 推断.
  - helper/checker 冲突: Section 7.2 明确不包含 helper; 人工相邻迁移 + 全表面同步 + checker.
  - reviewer contract: Section 3.5 最小准则 + 字段 + 机检/人检边界; 对本 revision 立即适用.
  - 矩阵载体: Section 9 全表三列; Phase 5 允许 deferred 且禁止把 not-run 当 pass.
  - 文件清单: Section 2.2 含 docs/README、decision、四索引、completed metadata-only、本 plan、PROGRESS/HANDOFF、checker compose、config/workflow; runbook 只读.
- 中等项折回对照: 5.1/5.2 拆分; Lane 2 全条件清单 + 5.3 硬规则且无未文档化 exception; activation recording 非 Phase 0; fetch import 中间态写入 6.1; Phase 1 模板归属、Phase 4 不再改模板; fixture carrier attestation 在 Phase 1 exit; 计划头部含 Revision 与 v1 review 登记.

## 问题清单

### 严重问题

无.

### 中等问题

无. 下列实施注意项不阻止 `approve`, 不要求 activation 前再改方案.

### 轻微问题

1. **stdlib 测试模块路径**
   - 位置: Section 7.3 / 2.2 (`python3 -m unittest scripts.tests.test_operating_modes`)
   - 改进建议: Phase 2 实现时确认 `scripts`/`scripts/tests` 包导入方式(必要时补空 `__init__.py`, 或改用 `unittest discover -s scripts/tests`), 并在 harness config 写最终可运行命令.

2. **`Current plan` 单槽与多 proposed 并存**
   - 位置: Section 3.4
   - 改进建议: Phase 1 在 `docs/operating-modes.md` 写明 "current-state block 只追踪当前焦点计划; 其他 proposed 仅靠索引/目录存在性校验", 避免多计划时误读.

3. **gate-token 非封闭词表**
   - 位置: Section 3.2 `Next gate` / `Phase entry gate`
   - 改进建议: 实施 checker 时对非空与字符集做最小约束即可; 若后续漂移, 再收紧枚举而不必阻塞本 revision.

4. **Design reviews 使用裸文件名**
   - 位置: 计划头部 `review-001.md@...`
   - 改进建议: 与 3.2 对 legacy bare name 的解析规则一致; 迁移完成后优先相对路径. 不阻塞.

5. **approve 后计划元数据与索引须同轮同步**
   - 位置: Section 3.2 / 12 / 13
   - 改进建议: 登记本 `approve` 后更新 `Design reviews`、`Latest design verdict`、`Review independence`、`Next gate` 与四索引/roadmap/状态块(实施前可用人工同步); 避免再出现 "正文未评审 / 索引已 approve" 分叉.

## 未验证项

- v2 正文的起草会话身份: 仓内无独立会话证据文件; 独立性依据为 Plan author ID 与 Reviewer ID 不同, 且本评审上下文未生成 v2 方案正文 -- 激活前人工仍应抽查 attestation.
- fixture 在 GitHub Actions 上的 git identity 与 external `--root` compose: 需 Phase 2/4 实测.
- existing backend test 与 9.2 行的逐条文件级映射: 留给 Phase 3 记录, 本次未重跑 backend suite.
- completed 计划 metadata-only 迁移后的严格 schema 通过: 依赖 Phase 2 实施, 设计上顺序正确(先 migrate 再 strict).
- 真实 daily publish 全链路: 明确标为 future authorized run, 本计划不改 runtime, 不在本次验证范围.

## 裁决理由

`review-001`/`review-002` 的五条严重问题在 v2 均有对应闭合设计, 且可映射到 phase 交付物与 checker 边界; 验证矩阵不再把不可机检行为伪装成 fixture 必过项; 范围清单与 "runbook/runtime 只读" 消除了实施越权压力. 剩余轻微项属于实现与运维收口, 可在 Phase 1-2 gate 内解决, 符合 `approve` 标准(方案可行, 无严重问题, 中等/轻微可在执行阶段消化).

`approve` 不等于 activation, 不等于 implementation start, 不等于 stage/commit/push/PR/publish 或任何远端变更. 按 Section 5.2/8, 下一外部门是用户对 exact revision `v2-review-foldback-2026-07-19` 的 activation instruction; 其后仅允许 activation lifecycle recording, 再需要单独的 start/execute 才进入 Phase 0.
