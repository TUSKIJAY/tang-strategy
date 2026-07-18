# 设计评审意见

- Review target: `docs/exec-plans/proposed/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md`
- Review target revision: `v1-initial`
- Review type: design
- Reviewer ID: `independent-design-reviewer-2026-07-19-r1`
- Plan author ID: `codex-plan-author-2026-07-19`
- Independence declaration: `attested`
- Evidence method: independent repository baseline, plan, checker, runtime-contract, and lifecycle-surface inspection recorded in this review
- Verdict: revise
- Confidence: high

## 整体判断

**裁决**: revise
**置信度**: high

## 总体评价

方案的问题诊断真实、方向正确。Section 1 的全部基线声明经逐条独立复验属实:`PROGRESS.md`(HEAD 版本)确实把已提交的 acceptance 工作描述为未提交 diff;`HANDOFF.md`(HEAD 版本)确实把 `a70be643...` 标为 Branch/HEAD 而实际 HEAD 为 `2454ccb7...`;`docs/exec-plans/roadmap.md` 确实把已完成 recovery 计划总结为无 commit;`python3 scripts/check-project-harness.py --root . --profile governed` 与 `--profile auto` 均 exit 0、`errors=[]`,21 个必需 artifact(MINIMAL 6 + GOVERNED 15)全部 present;`check-startup-doc-budget.py` 通过;现有 checker(277 行,纯 stdlib、零 Git 调用)确实只校验路径存在性、config 形状、job 名一致性和有限链接/路由子串,不做任何生命周期发现、元数据解析或状态对账。"结构 PASS ≠ 生命周期真实"的论点成立。

架构骨架也可保留:双模式对等、权威契约 + 短路由、canonical 生命周期源不引入第二状态库、动态 Git 事实与 durable 证据分离、TV-first 与 publish 授权分离,均与仓库现有运行时契约(fetch 脚本硬门槛、rebuild fail-closed 非收缩、Pages 发布链、AGENTS.md 触发短语)逐条核对后确认如实引用、无杜撰门槛、未收紧现有授权语义。Phase 0–6 为线性链、无循环依赖,Section 12 的 commit boundary 与各 phase 措辞一致。

但方案的核心承诺——"使生命周期真实可被机械检查"——在当前修订版中存在五处实质性缺陷:检查器多项 `must` 条款所依赖的受约束元数据/检测格式尚未定义;流转助手的正常收尾路径与其调用的检查器必然冲突;Section 9 验证矩阵大量条目超出仓库级检查器能力且未标注执行主体,导致 Phase 2/3/5 的 exit gate 客观不可判定;文件清单遗漏了必然受影响的文件,使检查器上线即对现有 completed 计划 fail 而修复不在授权范围内;独立的评审者契约(reviewer contract)是悬空引用,而本计划自身的下一道门就是独立设计评审。这些问题必须在 activation 前折回方案,不能留到实施期临场处理。

## 已核实事实

以下事实由评审独立验证(读文件、只读运行命令、git 历史对照),非转述计划自述:

- `git rev-parse HEAD` = `2454ccb7fc1c927f2a52a3bd2db7debe41998594`,分支 `codex/project-harness`,与计划第 7 行 baseline 一致;当前 worktree 脏集合恰为 5 个提案产物(本计划文件 + `PROGRESS.md`/`HANDOFF.md`/`proposed/index.md`/`roadmap.md` 修改)。
- `git show HEAD:PROGRESS.md` / `HEAD:HANDOFF.md` / `HEAD:docs/exec-plans/roadmap.md` 证实 Section 1 三条漂移声明均属实;`git show --stat a70be643` 与 `2454ccb` 证实两笔 commit 的实际内容。
- `scripts/check-project-harness.py` 通读:仅 import `argparse/json/re/sys/pathlib`,无 subprocess/Git;profile `auto` 从 `.harness/config.json` 推断为 `governed`;强制 config `github.checks` 与 workflow 三个 job 显示名(`Harness structure` / `Backend checks` / `Frontend build`)按序精确相等。无任何下游消费者解析其 JSON 输出。
- `backend/scripts/fetch_tv_live_extended_day.py` 的 NYSE 日历会话解析(含 early close)、RTH 1m/派生 5m/OHLCV/VWAP 硬门槛、默认 3 次重试均真实存在;`rebuild_live_extended_db.py` 的 date-loss 拒绝与 strategy/teaching 非收缩均真实存在;IB 脚本仅有零 bar 失败这一机械门槛,960/gaps 检查属 runbook 程序性要求;IBKR_PORT 默认 4002、HMDS 2106 属实。
- fetch 脚本(TV 与 IB)在 import 阶段即直接 upsert 被跟踪 DB,candidate-first 保护只存在于 rebuild 步骤(见问题清单)。
- 三个生命周期索引表 schema 互异(proposed: Plan|Status|Review|Next gate;active 含空表占位行;completed: Plan|Disposition|Verification|Final commit);`roadmap.md` 三段摘要为格式互不一致的自由散文,内嵌完整 commit hash。
- 仓库实际有四个索引文件(含 `docs/exec-plans/reviews/index.md`,其含 `Lifecycle state` 列)。
- 现有 completed 计划(`2026-07-18-...plan.md`)头部元数据无 `Plan slug`、无 `final disposition`、无 `verified implementation commit` / `lifecycle reconciliation commit` 字段;对 implementation review 的引用为裸文件名 `implementation-review-001.md`。
- 全仓 grep 证实:"reviewer contract"/"reviewer role" 除被审计划自身与前一计划的一处同样无指称的表述外,不存在任何定义文档;历史三份评审 artifact 均未记录评审者身份。
- `scripts/tests/` 不存在;`backend/tests/` 存在且为 stdlib unittest,与新 fixture 测试目录不会互相误拾取。
- `docs/README.md` 是 harness checker 检查的权威地图(`DOCS_AUTHORITY_TARGETS`),其中未列入 `docs/operating-modes.md`。
- `plan-template.md` 头部仅 4 个字段,被审计划自带 10 个字段——受约束元数据 schema 尚无任何稳定定义。

## 问题清单

### 严重问题

- **检查器 `must` 条款所依赖的受约束格式在计划内未定义,且计划自身的停止条件已预见此情形**
  - 位置:Section 7.1 第 296-302 行、Section 3.2/3.3、Section 9 第 408/414-416 行、Section 11 第 467 行。
  - 问题描述:checker 要求比对 roadmap 摘要与索引一致、检测 `PROGRESS.md`/`HANDOFF.md` 与 canonical 计划"contradicts"、拒绝 legacy `current HEAD`/worktree 结构化声明——但 roadmap 摘要当前是自由散文,PROGRESS/HANDOFF 是自由叙述文本,计划只为 plan 文件提出元数据约束(Section 3.2),未为 roadmap 摘要、状态文档定义任何可解析格式;"历史证据"与"live 声明"的区分是语言学判断(HANDOFF.md 第 8 行"began from … clean worktree/index"是合规历史陈述,completed 计划第 198/247 行是当时陈述,PROGRESS.md 第 5 行中文"均未 stage"是当前为真的 live 声明),任何关键词朴素检测都会误伤或漏检。计划自己在 Section 11 把"checker 需解析歧义自然语言"列为停止条件,却没有在任一 phase 的交付物中列出检测格式设计。
  - 影响范围:7.1 约一半的 `must` 条款无法实现为确定性检查;Phase 2 exit gate("invalid Coding Mode lifecycle states fail with specific messages")客观不可判定;实施期必然触发 Section 11 停止条件或被迫降格为不可验证实现。
  - 改进建议:把"受约束格式包"显式列为 Phase 1 具名交付物,至少覆盖:plan 元数据字段 schema、roadmap/索引条目模板、PROGRESS/HANDOFF 的受约束状态引用块语法、legacy live-state 声明的禁用字段清单与历史证据豁免标记格式;并对仓库现存三处真实样本给出逐一处置(历史计划内的当时陈述建议按"clearly labeled historical evidence"豁免,而非改写历史)。

- **流转助手的收尾路径与其调用的检查器构成确定性矛盾**
  - 位置:Section 7.2 第 312-319 行,对照 Section 7.1 第 301 行与 Section 9 第 414 行。
  - 问题描述:helper 被允许移动计划文件、机械更新索引和 roadmap、**打印** PROGRESS/HANDOFF 对账清单(明确不更新这两个文件),最后"rerun the lifecycle checker"。但 checker 必查"PROGRESS/HANDOFF 与 canonical 计划状态矛盾即 fail"。因此每次流转完成后 helper 的最终 checker 重跑按设计必然失败,直到人工完成对账。
  - 影响范围:helper 的正常退出状态是红灯,会训练操作者忽略 checker 失败,直接削弱整个检查器的权威;这是计划中唯一会批量改写状态面的可执行物,其安全契约还在 Section 9 中无任何测试锚点(无 dry-run 不写盘、无 activation 引用拒绝移动、非相邻目录拒绝等负向行)。
  - 改进建议:三选一——(a) 把 checker 重跑移出 helper 职责,改为"打印清单并指示人工对账后再跑 checker";(b) helper 从计划受约束元数据确定性生成 PROGRESS/HANDOFF 的状态引用块(需在 helper 契约中显式扩大范围并补对应负向测试);(c) 维持现状但在 Section 9 为 helper 增加条件性负向行并明确"transition 后 checker 红是预期中间态"的操作程序。同时把 helper 的验收标准写成"对索引与 roadmap 的重写为纯函数式文本变换"。

- **"the applicable reviewer contract" 是悬空引用,且本计划自身的评审门先于契约存在**
  - 位置:Section 5.1 第 162 行、Section 13、Section 9 第 409 行、Section 3.2 第 103-111 行、Section 7.1 第 306 行。
  - 问题描述:全仓核实不存在任何定义评审者契约/独立性准则的文件;历史评审 artifact 均未记录评审者身份。计划把"评审独立于作者"作为核心完整性控制,却未说明该契约的归属文档;3.2 的元数据清单要求记录 review verdict,但不要求评审人身份或与作者的分离证据;7.1 只承认"无法证明用户说过授权"这一机检盲区,对评审独立性这一同类盲区只字未提。本计划的下一道门(独立设计评审)即发生在任何 reviewer 契约存在之前。
  - 影响范围:计划的核心卖点是 authority "inspectable without relying on Codex-private state",而作者/评审者分离正是其最关键控制;该控制当前无定义、无证据要求、无机检或人工检查点;Section 9 第 409 行"no independent review → fail"对 checker 不可实现。
  - 改进建议:在计划内给出最小独立性准则(评审者非作者、独立验证证据、评审 artifact 元数据记录评审人身份/会话分离方式),指定契约归属文档(如并入未来的 `docs/operating-modes.md`),为 `review-template.md` 增加 reviewer identity / independence declaration 字段,并在 7.1 局限性段落显式承认该机检盲区及对应人工核查点。

- **Section 9 验证矩阵大量条目超出计划自设的执行约束,且全表无"执行主体/验证载体"归因**
  - 位置:Section 9 第 403-449 行,对照 7.1、7.3 第 328 行、Phase 3 第 364-370 行、Phase 5 第 381-387 行。
  - 问题描述:逐行对照后——生命周期表中,roadmap 一致性(第 408 行)、PROGRESS/HANDOFF 矛盾检测(第 414 行)、"moved toward active"/"phase entry attempted"等事件型条件(第 409/412 行,checker 只查仓库状态,无迁移检测机制)、路由负面行(第 417-418 行,"explicit" 落于何处无记录约定,"bypass" 需 diff/路径分类能力)均不可由 7.1 定义的 checker 机械判定;Data Update 表 13 行中,3 行由运行时脚本强制,7 行是纯运行时 agent 行为(weekday-only 解析、TV 前先查 IB、pending authority、异常升级等),同日混源行无任何执行层(seed 被 gitignore 且 7.3 禁止 CI 依赖真实 DB),而 Phase 3 声称用 "fixtures/contract tests" 验证这些行为,机制未说明;"daily-publish trigger runs after all local gates → pass"(第 436 行)的完整 exercise 需要网络/commit/push/Pages/hosted 验证,全部被计划自身约束排除。另有实质遗漏:7.1 must 第 2 条(status 元数据与目录一致性)无对应矩阵行;helper 安全契约无行;contract/router/templates 存在性与 checker 只读性/退出码无行。
  - 影响范围:Phase 3 exit gate 与 Phase 5"every required failure demonstrated fail-closed"无法诚实达成;实施者无法判断哪些行该写成 fixture、哪些注定只能人工/运行时验证。这恰是 Coding Mode 路由的"牙齿"所在,却最不可机械化,与第 17 行"mechanically checkable"目标形成张力。
  - 改进建议:给 Section 9 每行增加"验证载体"列(new fixture test / existing backend test / contract-text inspection / human review / 下次授权真实发布取证);补齐 status-vs-directory、active plan 稳态缺 review/activation 引用、helper 负向、存在性与只读性各行;把 trigger 行改写为兼容性检查(触发短语与 runbook/publisher 行为不变的文本验证)或将语义确认推迟到下次真实发布并如实标注。

- **文件清单遗漏必然受影响的文件,与迁移策略和 Phase 3 存在实质范围矛盾**
  - 位置:Section 2 第 68-81 行,对照 Section 10 第 454 行、Section 3.2、Phase 2 exit gate 第 359 行、Phase 3 第 365/370 行。
  - 问题描述:(i) 现有 completed 计划文件本体不在清单内,但 Section 10 要求用 durable commit 字段 reconcile 其元数据,且 Phase 2 exit gate 要求"valid existing completed plan pass"——一旦 Phase 1 schema 要求结构化字段,checker 上线即对其 fail,而修复编辑不在授权清单内;(ii) `docs/README.md` 是 harness 检查的权威地图,新增"single normative mode contract"而不登记会使权威地图不完整;(iii) `docs/exec-plans/reviews/index.md` 归属不明——仓库实际有四个索引,7.2 只说"three lifecycle indexes",该文件含 `Lifecycle state` 列,任何流转都会使其过期,且本计划的设计评审创建后即需更新它和 proposed index 的 Review 列,这些编辑发生在 activation 之前、清单未覆盖;(iv) Phase 3 scoped work 提到"existing templates/runbook pointers"暗示编辑 `docs/daily-publish-runbook.md`,但该文件不在清单且 Phase 3 commit boundary 写明"Data Update contract/tests only"。另外"five status surfaces"无从对应(三索引 + roadmap + PROGRESS + HANDOFF = 六)。
  - 影响范围:实施时被迫超 manifest 工作、中途修订计划,或对现存计划保持红灯——三种结局都破坏计划自己的 scope authority 纪律。
  - 改进建议:清单显式补充"edit 现有 completed 计划文件仅限元数据 reconciliation"(并排序在 Phase 2 exit gate 之前)、`docs/README.md` 一行路由登记、runbook 仅限加指针(或明确 Phase 3 不动 runbook);显式枚举四个索引并划分 helper/人工各自负责的更新面;修正状态面计数。

### 中等问题

- **Section 4 三条 Coding lane 与 Section 5.1 八个条目无显式映射,lane 与 gate 混编**
  - 位置:Section 4 第 129-136 行 vs Section 5.1 第 144-183 行。
  - 问题描述:5.1 的 8 个编号条目中 1-3 是路由 lane,4-8 实为 proposal lane 的下游生命周期阶段,标题"Lanes and gates"把两类概念编入同一列表且无任何文字说明 4-8 仅属 proposal lane。5.1.8"implementation review recorded when implementation occurred"可被解读为任何 bounded maintenance 都需独立实施评审,与 5.1.2"proportionate verification"的减负意图直接冲突。
  - 改进建议:拆为"路由 lane"(1-3)与"proposal lane 阶段"(4-8)两小节,显式声明 lane 1/2 适用哪些阶段门。

- **lane 2 与 lane 3 的边界判据不可判定,义务力度措辞三处漂移,路由表覆盖不全**
  - 位置:5.1.2/5.1.3/5.2、Section 4 路由表 row 2/3。
  - 问题描述:边界依赖"small, local, reversible, low-risk" vs "multi-stage, cross-module, safety-sensitive"等无量化阈值限定词;义务力度在"required or strongly preferred"/"must preferentially"/路由表无修饰间漂移;5.2 中的 multi-phase/destructive 等非契约类变更在路由表中没有对应行。5.2 的"unless the user explicitly defines an equally strict reviewed process"例外条款无定义、无格式、无登记处,Section 9 第 418 行引用的"explicit governed exception"在文件面中没有任何承载文件。
  - 改进建议:统一义务措辞;给 lane 3 列与 5.2 对齐的正向判据清单并声明清单外默认 lane 2 但须记录路由理由;例外条款改为硬路由,或定义例外记录格式与存放位置(如 decision record)并要求 checker 校验引用存在。

- **activation 的定义与 Phase 0 排序自相矛盾**
  - 位置:5.1.5 第 165-168 行 vs Phase 0 entry gate 第 338 行与 state/handoff 第 342 行,另见 Section 13。
  - 问题描述:5.1.5 把 activation 定义为"移动 plan proposed→active 并记录 activation evidence"的迁移本身;Phase 0 entry gate 要求"user has explicitly activated this exact plan"(迁移应已完成);Phase 0 的 state/handoff 却又执行"move plan to active/, record activation evidence"。同一次迁移既是 Phase 0 前置条件又是其工作内容。
  - 改进建议:拆分为"user activation instruction"(Phase 0 前置)与"activation lifecycle transition recording"(Phase 0 首个动作),统一三处措辞;Phase 0 state/handoff 改为"confirm the plan is in active/ with activation evidence and phase metadata set"。

- **Section 6.1 状态序列掩盖了 fetch 步骤直接写被跟踪 DB 的事实**
  - 位置:第 222、230、232-233 行。
  - 问题描述:`fetched -> quality_passed -> candidate_verified` 的排序暗示 DB 安全性在 candidate-first rebuild 处建立,但运行时 TV/IB fetch 脚本在 import 阶段即直接 upsert 被跟踪 DB。存在契约未承认的中间态:fetch/import 成功而 rebuild 失败时,被跟踪 DB 已含当日直接导入的数据。
  - 改进建议:在 6.1 注明"现行适配器在 fetch 时即导入 runtime DB,rebuild 负责 canonicalize 与 fail-closed 校验",并相应调整 `fetched` 的定义;`quality_passed` 对 IB 路径言过其实(IB 脚本仅机械零 bar 失败,960/gaps 属程序性检查),应注明 IB 的质量证据来自 runbook 程序性检查 + rebuild 兜底,或按 Section 10 机制列为待补运行时缺口。

- **roadmap/索引当前格式不支持所声称的确定性机械重写**
  - 位置:Section 7.2 第 317 行;已核实三个索引 schema 互异、roadmap 三段格式互不一致且内嵌自由散文 commit hash。
  - 问题描述:helper 要"机械"更新,须先把条目约束为固定模板,但格式模板化迁移未列为显式工作项,而改写 roadmap 格式本身是 governed 文档契约变更。计划的放弃条款(7.2 末尾)是有效兜底,但未承认当前格式已经不满足确定性重写前提。
  - 改进建议:把"roadmap/索引条目格式模板化"显式列入 Phase 1/2 范围与文件面。

- **Phase 2 入口闸门依赖一个无属主、无产出环节的制品**
  - 位置:第 356 行。
  - 问题描述:"fixture expectations are approved within the active plan"——批准主体未定义,且"fixture expectations"这一制品没有任何前置 phase 负责产出(Phase 1 只交付 contract 与 metadata schema)。
  - 改进建议:明确 fixture expectations 的产出责任与批准方式(用户 sign-off 或带证据的 self-attestation 记入 active plan)。

- **模板编辑被 Phase 1 与 Phase 4 重复认领**
  - 位置:第 348 行 vs 第 375 行;Section 2 manifest 只列一次。
  - 改进建议:明确拆分(Phase 1 = metadata/evidence 字段,Phase 4 = status-surface 约定)或归并到单一 phase。

### 轻微问题

- **Section 1 基线证据的时点与复现方式未标注**:三条漂移声明所述状态只存在于 git 历史(HEAD 提交版本)中,且已在随附的未提交提案 diff 内对账;评审者对照当前 worktree 复验会得到"声明不成立"的假象。建议注明证据锚定方式(如 "verified via `git show HEAD:PROGRESS.md` at 2454ccb7")。
- **Section 9 第 410 行丢失适用范围限定**:按字面会命中"带 approve 但尚未激活的 proposed 计划"这一合法状态。建议改写为"Active plan cites an approve review but no activation evidence reference | fail"。
- **第 416/418 行期望结果为析取式**("fail or require migration"/"fail or require an explicit governed exception"),fixture 需要单一期望结果。建议拆为默认 fail 行 + 显式例外/迁移路径行。
- **`local_accepted` 定义与现行"可选"本地构建语义有出入**(第 233 vs 253 行):6.1 读起来页面验收为必需,runbook/AGENTS.md 明确本地静态构建为 optional but recommended。建议在 6.1 标注强制项(DB 落地、assemble 1m/5m)与推荐项。
- **状态序列漏掉 Tang 交易记录步骤**(playbook 第 3 步,位于 rebuild 与 commit 之间,6.3 commit 范围又包含该 JSON)。建议在 `candidate_verified`/`local_accepted` 描述中提及。
- **6.4 升级是单向门且含不可观测措辞**(第 276/282 行):"corrupt or unexpectedly drifting"会把可重试的瞬时 drift 推入 Coding Mode 而无返回路径;"any temptation to use `--allow-date-loss`"的"temptation"不可观测。建议增加"诊断后无系统缺陷则返回 Data Update Mode 重试"回路,把"temptation"改为可观测行为。
- **"dependency-free"与动态 Git 依赖存在措辞张力**,fixture 的 git 初始化协议(CI runner 无默认 user 身份)与 `--profile minimal` 下 compose 行为未规定。建议写明"依赖本机 git 二进制、无 Python 包依赖"、fixture git 约定、compose 仅在 governed profile 激活。
- **被审计划自身元数据已偏离 `plan-template.md`**(10 字段 vs 模板 4 字段),佐证 schema 未冻结;建议在 7.1 开头注明其能力清单以 Phase 1 冻结的 schema 为前提。
- **decision 记录归属未说明**:新增权威契约改变了已 Accepted 的 `docs/decisions/2026-07-18-governed-harness-and-docs-authority.md` 确立的文档权威划分,计划未说明是否新增/修订 decision。
- **现有 completed 计划的 review 引用为裸文件名**,若 schema 要求可解析相对路径则会 fail;建议 schema 明确接受"裸文件名 + 按 slug 解析"或把修正列入 migration。
- **易变 Git 主张的检测语法与扫描范围未定义**(哪些文件、什么算 structured claim);"must not choose the more expansive authority"预设了未定义的权限全序(建议逐维度保守规则:任何含 Git/remote 权限的解释一律视为更广)。
- **Section 4 row 6 判据预设诊断结论**(诊断之前无法知道是否需要改契约),实践中退化为 row 1 + 6.4;建议明确"一切诊断一律从 Coding read-only lane 开始"。

## 未验证项

- "启动时 worktree/index clean" 的基线声明:时点已过,无法直接复验;仅有 dirty 集合与提案自述的一致性作为间接佐证,无反证。
- "project-harness-engineer governed audit" 审计事件本身在仓内无独立证据文件;已独立复算 21 = 6 + 15 且全部 present 这一结果。
- 历史评审 artifact 的实际独立性:评审者身份未记录,无法从仓库验证"独立于作者"是否成立。
- fixture 测试中 git 初始化/commit 在 GitHub Actions runner 上的实际行为、checker compose 的具体形态(import vs subprocess)对 `--root` 外部 fixture 仓库的定位影响:需实施期实测。
- `promote_candidate()` 的漂移重查实现细节(`/api/reviews/assemble` 的 1m/5m 行为同理):前者代码路径存在,未逐行验证。
- 既有 backend 测试(`test_rebuild_live_extended_db.py` 等)的 case 与 Section 9 Data Update 运行时行的逐条映射:已确认测试文件存在,未逐条对照。
- 现有 completed 计划在宽松解读下不会立即 fail(有 `Status: Completed`、review 引用、散文式 disposition),严格结构化解读下会 fail——最终判定依赖 Phase 1 schema 严格度,设计评审阶段无法终判。
- `docs/daily-publish-runbook.md` 全文是否含需随模式契约更新的措辞:本次仅核对关键段落。

## 裁决理由

方案的问题陈述经独立复验全部属实,双模式架构、权限分离骨架、TV-first/非收缩等运行时契约引用准确,Phase 链条线性闭合,不适用 `reject`。但五处严重问题——受约束格式缺失使检查器半数能力不可实现、流转助手与检查器确定性冲突、reviewer contract 悬空且本计划自身评审门先于契约、验证矩阵无执行主体归因导致多个 exit gate 不可判定、文件清单遗漏使实施时被迫越权或对现存计划亮红灯——都直接决定该计划 activation 后能否按其自身的 gate 纪律执行,不能留到实施阶段。将受约束格式包、helper/checker 顺序冲突、评审独立性最小准则、矩阵执行载体归因、文件清单补全折回方案并更新对应 exit gate 后,方具备 `approve` 条件。

本评审不激活、不执行该计划;评审通过与否均不构成 stage/commit/push/PR/发布授权。
