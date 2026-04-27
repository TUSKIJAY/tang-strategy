# 交付物评审意见

**审核对象**：training-replay-drill-redesign-plan.md（第二轮）

## 整体判断

**裁决**：approve
**置信度**：high

## 总体评价

第二轮 plan 在保持原始方向不变的前提下，对上一轮评审提出的全部中等问题与多数轻微问题做了系统化吸收，方案的可执行密度明显上升。direction 评估改为「`case.grade==='anti'` → `case.answer` 含 pass 词 → `case.direction` → rule 反推 fallback」的五级解析，与 `cases/index.json` 现成字段对齐；`revealCutoffIndex` 与 `currentIndex` 在 replay 阶段的同步关系作为不变量明文写入 4.2；`等待` 与播放控件的重叠通过「无 `下一根` 按钮 + replay 期间禁用引擎播放」彻底消除；`reviewRevealTarget` 加了 `last1mIndex` 的 clamp 并强制 5m 提交时切回 1m。新增的 `review` 数据结构 4.1 与 phase invariant 段使数据契约可直接进入实现层；acceptance 第 5 节新增的 「8 bar 起点下限」「3 次等待 → 3 条日志」「5m 提交切回 1m」「reveal 上界」等检查显著提升了浏览器逐项验收的颗粒度。

剩余问题集中在两段相邻表述间的措辞协调，以及 5m 提交时 `submittedIndex` 的跨 timeframe 换算未明示。这些都是落地阶段一行代码注释即可澄清的细节，不影响方案骨架与依赖路径。

`segment.preheat_count` 改为「历史上下文 metadata」而非「drill 起点」、segments-without-cases fallback 显式标注为 replay-only 不进入打分、`Wrong-direction signal` 上提到第 1 节末尾这三处调整方向正确，与产品目标的「先动作后讲解」一致。

## 问题清单

### 严重问题

无。本轮所有方向性诉求已闭环。

### 中等问题

1. **5m 提交时 `submittedIndex` 的 timeframe 换算未明示**
   - 位置：2.2 After submission / 5 acceptance 「Submitting on 5m switches back to 1m for outcome playback」
   - 问题描述：方案要求「Force the chart back to 1m before outcome playback」并「Compute `reviewRevealTarget = min(submittedIndex + 12, last1mIndex)`」。但若用户在 5m 视图提交，提交时 `submittedIndex` 是 5m index，与 `last1mIndex` 处于不同坐标系，`submittedIndex + 12` 没有可执行语义。引擎已通过 `dataManager.switchTimeframe` 把 currentIndex 按 ts 映射到目标 tf，`KlineEngineAdapter` 也已包装 `scrollTo`；方案应明确「提交前先取 5m bar 的 ts，切回 1m 后映射到对应 1m bar 的 index 作为 `submittedIndex`」。
   - 改进建议：在 2.2 After submission 第 1-2 步之间插入「If `currentTimeframe === '5m'` at submit time, capture the 5m bar's start ts, switch to 1m, locate the first 1m bar at or after that ts, and use its 1m index as `submittedIndex` for review」。

### 轻微问题

1. **2.1 与 2.2 关于引擎播放控件的处置写法不一致**
   - 位置：2.1 Left column「Hide or disable engine play/step controls for this drill page if needed」与 2.2 During replay「If playback remains visible, it must be disabled while `phase === 'replay'`」
   - 改进建议：合并为一句确定性表述，例如「During `phase === 'replay'`, engine playback and step buttons must be disabled (visible-but-grayed) or hidden; timeframe and MA buttons remain available throughout」。"if needed" 在 2.1 出现会让执行者误以为可选。

2. **`drillStartIndex` 与 `revealCutoff` 初值关系未显式写出**
   - 位置：2.2 Initial state
   - 改进建议：在「Set `revealCutoff` to the current 1m bar index」前补一句「Initialize `currentIndex = drillStartIndex; revealCutoffIndex = drillStartIndex;」，与 4.2 invariant 「`revealCutoffIndex === currentIndex` during replay」前后呼应。

3. **`review.reasonContradictions` 的判定口径未给出**
   - 位置：3.4 Reason Review / 4.1 review 结构
   - 改进描述：方案列出 contradictions 字段但未说明何为「contradicted by failed checkpoints」。建议补一条：「user 选中的 reason 对应的 checkpoint 在 `segment.derived.checkpoints` 中 `passed === false`，归入 contradictions」。

4. **3.1 Confirm index fallback 到 `signalIndex` 的影响未提示**
   - 位置：3.1 Standard Inputs
   - 改进建议：当 `confirm_bar` 缺失时，`validWindowEnd = signalIndex + 1`，仅给 2 根 bar 的有效窗口。对部分要求等待多根 confirm 的策略偏紧。可在该项后加注「该 fallback 倾向更严的 timing 评分；如果未来引入更长 confirm 等待，需扩展为 `signalIndex + N`」。

## 未验证项

- 引擎在 `phase === 'submitted'` 阶段从 `currentIndex = submittedIndex` 播放至 `reviewRevealTarget` 的行为：方案要求 `revealCutoffIndex` 已超前，`play()` 应可正常推进至 cutoff。HANDOFF 2026-04-24 验证表第 5 行显示 `play()` 在 cutoff 处会停（这是期望行为），但「cutoff 已抬高、play 应能跑到 cutoff 才停」这一组合未单独验证。-- 建议执行阶段先用最小复现脚本确认。
- `segment.derived.checkpoints` 在所有 6 个 case 上对 3.4 列举的 reason chip groups 的覆盖度（trend_ok / ma_alignment_ok / touch_ma10 / confirm_bar / body_not_cross / stop_defined / reward_ok / vwap_* / forbidden_absent）：方案承诺「Checkpoint keys without a user-facing label or useful reason text should be hidden from chips」但未列出现状缺失矩阵。-- 建议执行阶段补一份「checkpoint key × case」覆盖表，确保 reason chips 不会在某些 case 上空空如也。
- 引擎工具栏在 `phase === 'replay'` 时禁用播放按钮的具体接入方式：当前 `KlineEngineAdapter` 已暴露 `playPause` / `stepForward` 等控件给 `KlineView` footer 使用，但「禁用引擎自带工具栏的播放按钮」是否需要新增 `disablePlayback(boolean)` API 还是用 CSS 屏蔽点击事件，方案未指明。-- 落地时倾向新增窄接口而非 DOM 选择器禁用，与方案 4.2 「extend `KlineEngineAdapter` with a narrow callback instead of mutating engine private fields」原则一致。

## 裁决理由

选择 approve 的主要依据：

- 上一轮评审中 5 项中等问题（direction 字段、cutoff 同步、等待与播放重叠、reveal clamp、no_trade_zone 边界）全部得到结构化回应，且回应方式与建议一致或更优。
- 上一轮 5 项轻微问题（reason chips 多选、waitLog 用途、segment fallback 措辞、preheat_count 防御、Wrong-direction signal 位置）全部吸收，仅 segment fallback 的措辞做了显式收紧（限定为「local constants 中明确声明的 module → category 关系」），合理。
- 新增的 `review` 数据结构（4.1）与 phase invariant（4.2）把方案与实现的契约边界画得很清楚，执行者可以直接拿这两段当 props/state 类型注释；acceptance 新增的 4 条具体检查使浏览器验证不再含糊。
- 剩余的 1 个中等问题（5m 提交跨 tf 换算）与 4 个轻微问题都属于「执行阶段一句话即可澄清」的措辞细节，不影响方案骨架。

未选择 revise 的依据：剩余问题中没有任何一条会改变 `TrainingPage` 的状态形状、引擎接入方式、或评估模型的拓扑结构。要求起草者再返修一轮的边际收益小于直接进入执行后由执行者补丁澄清的成本。

未选择 reject 的依据：方案与 v1 一致地遵守 Wrong-direction signal、依赖单向流动、不复活已否决组件、不引入第二套规则源等约束，且与 CLAUDE.md「显式优于隐式」「禁止静默失败」原则一致。

置信度评定为 high 的依据：评审同时核对了被审方案的两个版本差异、上一轮 review 与本轮 plan 的逐项对应关系、`pages-2.jsx#TrainingPage` 现状、`shared.jsx` 中 `checkpointToRanges` / `stepToHighlightRanges` 实现、`cases/index.json` 与 `teaching_segments.json` 数据契约。所有遗留问题均有源码或字段层面的具体证据。
