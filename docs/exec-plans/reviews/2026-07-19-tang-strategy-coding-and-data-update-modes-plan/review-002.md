# 交付物评审意见

**审核对象**: 2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v1-initial`
- Review type: design
- Reviewer ID: `independent-design-reviewer-2026-07-19-r2`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: independent second-pass repository and plan inspection plus explicit replay of review-001 findings recorded in this review
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

本评审在独立复验仓库事实后, 对同一份 proposed 方案给出二次设计裁决, 并复核 `review-001` 的关键结论. 方案问题诊断成立: HEAD `2454ccb7fc1c927f2a52a3bd2db7debe41998594` 上的 `PROGRESS.md` / `HANDOFF.md` / `docs/exec-plans/roadmap.md` 确实残留过时 Git/生命周期声明; 现有 `scripts/check-project-harness.py`(277 行, 仅 stdlib, 无 Git 调用) 在 governed/auto 下均可 `passed=true` 且 `errors=[]`; MINIMAL 6 + GOVERNED 15 = 21 个必需 artifact 全部 present; startup-doc budget 通过. "结构 PASS 不等于生命周期真实" 可直接从仓库复现.

双模式对等、权威契约与短路由分离、不引入第二状态库、动态 Git 与 durable 证据分离、TV-first 与 publish 授权分离, 均与 `AGENTS.md`、daily-publish runbook、TV/IB fetch 与 rebuild 脚本的现行行为一致, 无杜撰门槛、无静默收紧授权. Phase 0-6 线性、Section 12 commit boundary 与 phase 描述一致, 方向不构成 `reject`.

`review-001` 的五条严重问题经逐条复验仍然成立, 且足以单独支撑 `revise`. 受约束检测格式未定义、helper 与 checker 的确定性冲突、reviewer contract 悬空、Section 9 无验证载体归因、文件清单遗漏导致实施越权或现存 completed 计划红灯, 都会使 "mechanically checkable lifecycle" 的核心承诺在 activation 后无法按自身 gate 诚实落地. 计划正文自 `review-001` 起尚未修订; 本裁决针对同一 exact revision, 不因二次评审而升级为 `approve`.

## 已核实事实

以下事实由本评审独立验证, 非转述 `review-001` 或计划自述:

- `git rev-parse HEAD` = `2454ccb7fc1c927f2a52a3bd2db7debe41998594`, 分支 `codex/project-harness`; 与计划 baseline 一致.
- `git show HEAD:PROGRESS.md` 仍把已提交的 acceptance 工作描述为未 stage/未 commit; `git show HEAD:HANDOFF.md` 仍写 `Branch/HEAD: ...@a70be643...` 与 unstaged/uncommitted; `git show HEAD:docs/exec-plans/roadmap.md` Completed 摘要仍写 "no commit or remote action", 而 `a70be643` 与 `2454ccb` 的实际 commit 内容可核对.
- 当前 worktree 中 lifecycle 提案 diff 已对账上述漂移, 但 `docs/exec-plans/roadmap.md` Proposed 摘要仍写 "尚无 review", 而 `proposed/index.md` 与 `reviews/index.md` 已登记 `review-001: revise`——派生状态面之间再次分叉, 与方案要解决的问题同类.
- harness checker: 仅路径存在性、config 形状、workflow 三 job 名精确相等、有限 Markdown 链接/路由子串; `DOCS_AUTHORITY_TARGETS` 不含 `operating-modes.md`; 无下游消费者解析其 JSON 的硬依赖.
- TV fetch: NYSE 会话(含 early close 边界校验)、默认 3 次重试、RTH 1m/派生 5m/OHLCV/VWAP 硬门槛真实存在; 默认路径 `write_payload` 后调用 `import_market_json` 直接写入被跟踪 DB(`--skip-import` 才跳过). IB fetch 同样默认 import; IB 脚本侧无与 TV 对等的 960/gaps 硬失败, 程序性检查在 runbook; `IBKR_PORT` 默认 4002, HMDS 2106 见 runbook.
- rebuild: candidate-first、date/non-market shrink 拒绝、`--allow-date-loss` 仅显式放开日期集合, 与方案引用一致; candidate-first 保护在 rebuild 而非 fetch import 阶段.
- 三生命周期索引 schema 互异; `reviews/index.md` 为第四索引且含 `Lifecycle state` 列. 现有 completed 计划头部无 `Plan slug` / durable commit 字段, implementation review 引用为裸文件名 `implementation-review-001.md`.
- 全仓除被审计划与历史 completed 计划中一处同样无指称的 "reviewer role" 措辞外, 不存在 reviewer contract 定义文档; 历史 review artifact 未记录评审者身份.
- `scripts/tests/` 不存在; `backend/tests/` 为 stdlib unittest. `plan-template.md` 头部约 4 字段, 被审计划自带约 10 字段——metadata schema 未冻结.
- 被审计划 Section 7.2 写 "five status surfaces", 同节又把 helper 范围写成三索引 + roadmap, 并打印 PROGRESS/HANDOFF 清单; Section 3.1/3.2 派生面合计为三索引 + roadmap + PROGRESS + HANDOFF(至少六面, 若计入 reviews index 则更多).

## 对 review-001 的复核结论

| review-001 主张 | 本评审结论 |
| --- | --- |
| 基线漂移三条属实, checker 不查生命周期 | 成立 |
| 严重: 受约束格式未定义导致 must 条款不可实现 | 成立, 维持严重 |
| 严重: helper 收尾 rerun checker 与 PROGRESS/HANDOFF 必查矛盾 | 成立, 维持严重 |
| 严重: reviewer contract 悬空 | 成立; 独立性机检不可得, 但 "review artifact 缺失" 仍可机检——悬空引用与独立性准则缺失仍须修订 |
| 严重: Section 9 无验证载体, exit gate 不可判定 | 成立, 维持严重 |
| 严重: 文件清单遗漏 completed 本体、docs/README、reviews index、runbook 边界 | 成立, 维持严重 |
| 中等: lane/gate 混编、lane 边界不可判定、activation 自相矛盾、fetch 直写 DB 未入状态模型、索引格式不支持机械重写、Phase 2 fixture 无属主、模板 dual claim | 均成立 |
| 轻微项整体 | 成立且不单独决定裁决; 修订时应择要吸收, 避免只修严重项后留下可判定性缺口 |

`review-001` 未发现会推翻其 `revise` 的事实错误. 其 "dirty 恰为 5 个提案产物" 描述对应评审当时状态; 本评审时点已额外包含 reviews 目录与索引更新, 不影响对方案正文的裁决.

## 问题清单

### 严重问题

1. **检查器 must 条款依赖的受约束格式包未定义**
   - 位置: Section 7.1, Section 3.2/3.3, Section 9, Section 11
   - 问题描述: checker 要比对 roadmap 与索引、判定 PROGRESS/HANDOFF 与 canonical 计划 "contradicts"、拒绝 legacy live-state 声明, 但计划只对 plan 文件提出元数据字段清单, 未给出 roadmap 摘要模板、索引行模板、PROGRESS/HANDOFF 可解析状态引用块、legacy 声明禁用字段清单与历史证据豁免标记. 自然语言 "历史陈述 vs live 声明" 无法确定性机检; 计划 Section 11 已把 "解析歧义自然语言" 列为停止条件, 却未把检测格式设计列为任一 phase 交付物.
   - 影响范围: 7.1 约一半 must 无法写成确定性检查; Phase 2 exit gate 客观不可判定; 实施期必然触发停止条件或降格为不可验证实现.
   - 改进建议: 将 "受约束格式包" 列为 Phase 1 具名交付物; 对现存 completed 计划内历史陈述、以及 HANDOFF 中 labeled startup evidence, 给出豁免语法而非要求改写历史.

2. **流转助手正常收尾与其调用的 checker 构成确定性矛盾**
   - 位置: Section 7.2 对照 Section 7.1 / Section 9
   - 问题描述: helper 可移动计划、更新索引与 roadmap、仅打印 PROGRESS/HANDOFF 清单, 最后 rerun checker; checker 又要求 PROGRESS/HANDOFF 与 canonical 一致. 故每次机械流转后最终检查按设计为红, 直到人工对账.
   - 影响范围: 唯一批量改写状态面的可执行物以红灯收尾, 削弱 checker 权威; helper 安全契约(dry-run 默认、非相邻拒绝、无 activation 引用拒绝移动等)在 Section 9 无负向锚点.
   - 改进建议: (a) checker 重跑移出 helper, 改为打印清单并指示人工对账后再跑; 或 (b) helper 从受约束元数据确定性生成状态引用块并扩大契约与测试; 或 (c) 明确 transition 后红灯为预期中间态并写入操作程序. 同时要求索引/roadmap 重写为纯函数式文本变换.

3. **"applicable reviewer contract" 悬空, 独立性控制无证据要求**
   - 位置: Section 5.1, Section 3.2, Section 7.1, Section 9, Section 13
   - 问题描述: 仓库不存在 reviewer contract 定义. 计划以 "评审独立于作者" 为核心完整性控制, 但未指定归属文档、最小准则、评审 artifact 身份字段; 7.1 承认无法机证用户授权, 却未对称承认无法机证独立性. Section 9 "无独立 review → fail" 若解读为独立性则不可机检, 若解读为 artifact 缺失则可机检——计划未区分.
   - 影响范围: authority "inspectable without private state" 的关键控制无定义、无证据字段、无人工检查点.
   - 改进建议: 在计划内写明最小独立性准则(非作者、独立验证证据、评审人身份/会话分离声明); 指定并入 `docs/operating-modes.md` 或 review-template; 元数据区分 "review artifact present" 与 "independence attested"; 7.1 显式列出独立性为人工核查点.

4. **Section 9 验证矩阵缺少验证载体, 多项超出自设执行约束**
   - 位置: Section 9 对照 7.1、7.3、Phase 3/5 exit gate
   - 问题描述: roadmap 一致性、PROGRESS/HANDOFF 矛盾、"moved toward active"/"phase entry attempted" 等事件型条件、路由 bypass、Data Update 表中多数 agent 行为行、完整 daily-publish exercise(网络/push/Pages/hosted) 均无法由 7.1 checker + 7.3 禁止真实 DB/网络的 fixture 单独判定, 且全表无 "验证载体" 列. 同时遗漏 status-vs-directory、helper 负向、contract/router 存在性与只读性/退出码等行.
   - 影响范围: Phase 3/5 exit gate 无法诚实签署; "mechanically checkable" 与矩阵内容张力最大处恰是 Coding/Data 路由的牙齿.
   - 改进建议: 每行增加验证载体(new fixture / existing backend test / contract-text inspection / human review / 下次真实发布取证); 补齐遗漏行; 将完整 publish exercise 降为兼容性文本检查或推迟并标注.

5. **文件清单与迁移/Phase exit 范围矛盾**
   - 位置: Section 2 manifest 对照 Section 10、Phase 2/3
   - 问题描述: (i) 现有 completed 计划本体不在清单, 但 Section 10 与 Phase 2 要求 reconcile 后 "valid existing completed plan pass"; (ii) 新增权威契约不登记 `docs/README.md` 会使权威地图不完整; (iii) `reviews/index.md` 与 "three lifecycle indexes" 表述冲突, 流转与 design review 登记都会更新它; (iv) Phase 3 "runbook pointers" 暗示改 `docs/daily-publish-runbook.md` 却不在清单且 commit boundary 写 "contract/tests only"; (v) "five status surfaces" 与实际派生面计数不一致.
   - 影响范围: 实施被迫超 manifest、中途改计划、或对现存计划长期红灯——均破坏 scope authority 纪律.
   - 改进建议: 清单补充 completed 计划仅限 metadata reconciliation、`docs/README.md` 路由登记、reviews index 归属、runbook 仅指针或明确不动; 统一状态面枚举与 helper/人工分工; 将 completed 元数据修复排在 Phase 2 exit 之前.

### 中等问题

1. **Section 4 路由 lane 与 Section 5.1 编号条目混编**
   - 位置: Section 4 与 Section 5.1
   - 问题描述: 5.1 条目 1-3 是路由 lane, 4-8 是 proposal lane 下游阶段; 5.1.8 可被解读为任何 bounded maintenance 都需 implementation review, 与 5.1.2 减负冲突.
   - 改进建议: 拆为 "路由 lane" 与 "proposal lane 阶段" 两小节, 声明 lane 1/2 适用哪些门.

2. **lane 2/3 边界与义务措辞漂移, 例外条款无承载**
   - 位置: 5.1.2/5.1.3/5.2、Section 4、Section 9
   - 问题描述: "small/local/low-risk" 与 "multi-stage/safety-sensitive" 无判据清单; "required or strongly preferred" / "must preferentially" / 路由表无修饰 三者力度不一; 5.2 的 "equally strict reviewed process" 与矩阵 "explicit governed exception" 无文件面与格式.
   - 改进建议: 统一义务措辞; 给出 lane 3 正向判据并声明清单外默认 lane 2 且记录路由理由; 例外改为硬路由或定义 decision-record 格式并由 checker 校验引用存在.

3. **activation 定义与 Phase 0 排序自相矛盾**
   - 位置: 5.1.5 与 Phase 0 entry/state
   - 问题描述: activation 既是 "proposed→active 迁移本身", 又是 Phase 0 前置 ("user has explicitly activated"), 同时又是 Phase 0 工作内容 ("move plan to active/").
   - 改进建议: 拆分 "user activation instruction"(前置) 与 "activation lifecycle recording"(Phase 0 首个动作); 统一三处措辞.

4. **Section 6.1 状态序列掩盖 fetch 直写 runtime DB**
   - 位置: 6.1 `fetched` / `quality_passed` / `candidate_verified`
   - 问题描述: 序列暗示安全性建立在 candidate-first rebuild, 但 TV/IB 默认 import 在 rebuild 前已 upsert 被跟踪 DB; 存在 "fetch 成功、rebuild 失败" 的中间态. IB 的 `quality_passed` 相对 TV 硬门槛言过其实.
   - 改进建议: 契约承认现行适配器 fetch 即 import; 区分 TV 硬门槛与 IB 程序性检查 + rebuild 兜底; 缺口按 Section 10 列为后续 Coding 提案而非静默假装已强制.

5. **roadmap/索引格式不支持所声称的确定性机械重写**
   - 位置: Section 7.2; 已核实三索引 schema 互异、roadmap 为自由散文
   - 问题描述: 模板化迁移未列入显式工作项, 却是 helper "机械更新" 的前提.
   - 改进建议: 将条目模板化列入 Phase 1/2 与文件面; 否则 helper 必须省略.

6. **Phase 2 入口依赖无属主制品; 模板编辑 dual claim**
   - 位置: Phase 2 entry; Phase 1 vs Phase 4 对 templates
   - 问题描述: "fixture expectations are approved within the active plan" 无产出 phase 与批准主体; 模板被 Phase 1 与 Phase 4 重复认领.
   - 改进建议: 明确 fixture expectations 由 Phase 1 草案、Phase 2 入口用户 sign-off 或带证据 self-attestation; 模板字段拆分到单一 phase.

7. **本计划头部 Review status 与仓库评审登记已不一致**
   - 位置: 计划第 8-12 行; 对照 `proposed/index.md` / `reviews/index.md`
   - 问题描述: 计划仍写 "Review status: not started; no review artifact exists", 而评审目录已有 `review-001` 且索引为 revise. 对 "exact proposed plan revision" 的二次评审必须先修订计划正文与元数据, 否则下一轮 approve 无法锚定 revision.
   - 改进建议: 修订时同步更新 Review status、已存在 review 引用、next gate, 并在每次送审 revision 上给出可引用标识(日期戳或短 hash).

### 轻微问题

1. **Section 1 基线证据未标注复现方式**: 漂移只存在于 `git show HEAD:...` 时点; 对照 worktree 会得到假阴性. 建议锚定 commit 与命令.
2. **Section 9 第 410 行缺适用范围**: 字面可命中 "proposed 且已 approve 但未 activation" 的合法态. 建议限定 active 或不存在 activation 证据时保持 proposed.
3. **第 416/418 行期望为析取式**: fixture 需要单一期望; 拆为默认 fail + 例外/迁移路径行.
4. **`local_accepted` 与 optional 本地静态构建语义**: 6.1 宜区分强制(DB、assemble 1m/5m)与推荐(静态构建).
5. **状态序列未提 Tang 交易 JSON 步骤**: playbook 第 3 步介于 rebuild 与 commit 之间, 6.3 commit 范围含该文件.
6. **6.4 升级单向且含不可观测措辞**: "corrupt or unexpectedly drifting" / "any temptation to..." 建议增加可返回 Data Update 的诊断回路, 并把 temptation 改为可观测行为.
7. **dependency-free 与动态 Git**: 建议写明依赖本机 git 二进制、无 Python 包依赖; fixture 的 git identity 约定; compose 仅 governed profile.
8. **decision 记录**: 新增 `docs/operating-modes.md` 权威层是否修订/新增 decision, 计划未说明.
9. **completed 计划 review 裸文件名**: schema 应接受 "裸文件名 + slug 解析" 或列入 migration.
10. **权限全序未定义**: "must not choose the more expansive authority" 需逐维度保守规则.
11. **Section 4 row 6**: 诊断前无法预知需改契约; 建议一切数据异常诊断从 Coding read-only 起步.

## 未验证项

- 提案起草时 "worktree/index clean" 的瞬时状态: 时点已过, 仅能以当前 dirty 集合与提案自述一致性作间接佐证.
- `project-harness-engineer` governed audit 事件本身无仓内独立证据文件; 已独立复算 21 路径 present.
- 历史评审是否事实上独立于作者: 身份未记录, 无法从仓库证明.
- fixture 内 git init/commit 在 GitHub Actions runner 无 user 配置时的行为; checker compose(import vs subprocess) 对 `--root` 外置 fixture 的定位: 需实施期实测.
- `promote_candidate()` 与 `/api/reviews/assemble` 未逐行通读; 仅确认路径与测试文件存在.
- 既有 backend 测试与 Section 9 Data Update 运行时行的逐条映射: 未做完整对照.
- completed 计划在宽松 vs 严格 schema 下是否立即 fail: 依赖 Phase 1 严格度, 设计阶段不能终判.
- `docs/daily-publish-runbook.md` 全文是否另有需随模式契约调整的措辞: 本次核对关键段落与 IB/TV/rebuild 相关条款.

## 裁决理由

方案诊断经独立复验属实, 架构骨架与运行时契约引用准确, Phase 链闭合, 不适用 `reject`. `review-001` 的五条严重问题全部复核成立, 且本评审补充了 "计划头部 Review status 已与索引分叉、二次送审必须先修订锚定" 等中等项. 这些缺陷直接决定 activation 后能否按计划自身的 mechanical checkability 与 scope authority 执行, 不能留到实施期临场发明格式与验证载体.

在受约束格式包、helper/checker 顺序、评审独立性最小准则、矩阵验证载体、文件清单与状态面计数、activation/Phase 0 措辞、以及 Review status 元数据同步完成修订并再次送审之前, 不具备 `approve` 条件. 裁决为 `revise`.

本评审不激活、不执行该计划; `revise` 与任何后续 `approve` 均不构成 stage/commit/push/PR/发布授权. 下一生命周期动作仅为: 起草者按 `review-001` 与本文件修订 exact plan revision, 更新 proposed/reviews 索引与状态面, 再请求新一轮设计评审.
