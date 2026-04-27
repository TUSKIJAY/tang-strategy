# 交付物评审意见

**审核对象**：training-replay-drill-redesign-plan.md

## 整体判断

**裁决**：approve
**置信度**：high

## 总体评价

方案将 `#training/<module_id>` 从结构化的 7 步问答翻转为「隐藏未来 K 线 + 自由动作 + 窗口式打分」的实战 replay drill，方向与 2026-04-25 用户反馈中 "完全不知所云" 的痛点匹配。核心交互（等待 / 做多 / 做空 / 放弃）简单且贴近真实交易场景，避免了上一版两套并行导航（左 step 列表 + 右上一步/下一步）造成的注意力分散。

技术依赖侧已经基本就位：`KlineEngine#setRevealCutoff` / `setHighlightRanges` / `revealcutoff:changed` 与 `KlineEngineAdapter` 的双向控制接口在 2026-04-24 完成，方案直接复用而非要求新增引擎能力，落地风险低。范围克制（仅改 `TrainingPage`、不动 hub/module/case/mistake/archive、不复活 `Aggregate5mBand`），与 CLAUDE.md「小步快跑、单逻辑单元」的规范一致，验收清单具体可执行。

主要不足集中在交互细节的语义留白与评估模型对现成数据契约的忽视。`revealCutoffIndex` 在 replay 阶段如何随 `currentIndex` 推进、`等待` 与播放控件是否都计入 `waitLog`、`12 根揭示` 的边界 clamp 等问题未明确；direction 评估绕过了 `cases/index.json` 已有的 `direction` 字段，转而通过 rule_id 反推，与 4.3 "use existing static data" 的自陈相矛盾。这些问题不影响方向决断，但会在落地时把起草者拉回二次澄清。

## 问题清单

### 严重问题

无。方案方向正确，依赖已就位，acceptance 清单具体到可在浏览器逐项验证。

### 中等问题

1. **direction 评估逻辑放弃了现成的 `case.direction` 字段**
   - 位置：3.3 Direction Labels
   - 问题描述：方案给出 `support_ma10 → 做多`、`reject_ma10 → 做空`、`signal_b → 做空` 的 rule 反推映射。但 `cases/index.json` 中每个 case 已经携带 `direction`（`CALL` / `PUT` / `—`）、`grade`（`standard` / `edge` / `anti`）和 `answer`（`做 CALL` / `做 PUT` / `降级观察` / `不做`）字段。直接读 case 字段映射到 `做多/做空/放弃` 比按 rule 反推更稳，且 `case_ma10_edge_2026_02_03` 这类 `direction=PUT, grade=edge, answer=降级观察` 的边缘场景在反推路径下无法判定（按 rule 走会判为做空，按 answer 走应判为放弃）。
   - 影响范围：`reject_ma10 + edge` 案例的评估结果会与 case 真实 answer 冲突；当扩展到 `vwap_distance_filter`、`candle_body_quality`、`background_5m` 等已存在的 rule（cases 中已使用，方案未列入映射表）时，落地阶段需要补全或回退到 case 字段。
   - 改进建议：将 3.3 改写为「先读 `case.grade === 'anti'` → `放弃`；否则按 `case.direction` 映射 `CALL → 做多` / `PUT → 做空`；对 `grade === 'edge'` 显式标注 "降级观察" 视为 `放弃` 的同义」。把 rule → direction 映射降级为 case 字段缺失时的 fallback。

2. **`revealCutoffIndex` 与 `currentIndex` 在 replay 阶段的同步规则未明确**
   - 位置：2.2 Drill Flow / 4.1 TrainingPage 状态形状
   - 问题描述：方案声明初始 `revealCutoff` 设为「current 1m bar index」让未来不可见，但 `等待` 行为是 "advances one bar"。如果 cutoff 不随 `currentIndex` 同步前移，`等待` 之后用户依然看不到新一根 bar，交互直接卡死；如果同步前移，则 `revealCutoffIndex` 始终等于 `currentIndex`，状态形状中将其作为独立字段就是冗余。
   - 改进建议：在 2.2 明确「replay 阶段 `revealCutoffIndex = currentIndex`，二者绑定；submitted 阶段 `revealCutoffIndex = submittedIndex + 12`（clamp 到 segment 末尾），与 `currentIndex` 解绑用于动画播放」。状态形状中保留独立字段以承载 submitted 阶段的差值。

3. **`等待` 与播放控件的语义重叠未澄清**
   - 位置：2.2 Drill Flow
   - 问题描述：方案同时存在「`等待` advances one bar and records the wait」与「`下一根` / play controls advance the chart without ending the drill」。两者都推进 bar，但前者 record、后者不 record，区别仅在 `waitLog` 是否累加。这会让用户用播放绕过 `waitLog`、最终只留下一次 `submittedAction` 而无任何观望记录，与「训练真实决策」目标背离。
   - 改进建议：二选一。要么 replay 阶段所有前进（含播放每 tick）都计入 `waitLog`；要么把「等待」从按钮改为隐式状态（每次推进 bar 自动累加 wait_count），把 `下一根 / play` 作为唯一推进入口。

4. **`12 根 bar 揭示` 缺边界 clamp 与跨 timeframe 的语义说明**
   - 位置：2.2 Drill Flow
   - 问题描述：方案写「Reveal and play the next 12 1m bars by default」，但 `seed_01`（MA10 support）只有约 36 根 1m bar，提交时若 `submittedIndex = 31`，剩余 5 根不足 12，缺乏 clamp 描述。另外当前 view 在 5m 时提交，"12 根 1m bars" 的含义需要换算到当前 timeframe 还是强制切回 1m 揭示。
   - 改进建议：补充「`revealCutoff = min(submittedIndex + 12, bars_1m.length - 1)`；进入 review 前若当前在 5m，强制切回 1m 后再揭示，与 case `decision_bar.timeframe='1m'` 的主交易时间框对齐」。

5. **`no_trade_zone` 与 `late` 的判定边界未给出**
   - 位置：3.2 Timing Labels
   - 问题描述：`late` 定义为 "after valid window but before outcome has fully played out"，但 outcome 边界未给出（segment 末尾？某个 checkpoint？提交时的 `currentIndex + 12`？）。`no_trade_zone` 与 `too_early` / `late` 的关系也不清——anti case 中是否任何 timing 提交 `做多/做空` 都判 `no_trade_zone`，与 timing window 是 OR 还是 AND？
   - 改进建议：给出二维矩阵 `(timing, direction) → label`。建议直接以 `case.grade==='anti'` 为前置：anti case 提交方向动作即 wrong direction，timing 不再单独评；非 anti case 才走 `too_early / valid_window / late` 三态，`late` 上界以 `bars_1m.length - 1` 兜底。

### 轻微问题

1. **`reason chips` 选择是多选还是单选未声明**
   - 位置：2.1 右栏 / 3.4 Reason Review
   - 改进建议：在 2.1 明确「reason chips 多选，提交后保留选中集合用于 review diff」；review 中按 set diff（user ∩ standard / standard - user / user - standard）给三类反馈。

2. **`waitLog` 在 review 中如何使用未说明**
   - 位置：4.1 状态形状 / 2.2 提交后逻辑
   - 改进建议：明确 `waitLog` 是仅做行为日志展示，还是会参与评分（如「等待次数过多直至错过 valid_window」时给出额外标签）。倾向前者，避免引入第二套打分维度。

3. **4.3 "segments matching the module/category" 措辞模糊**
   - 位置：4.3 Data Fallback
   - 改进建议：`teaching_segments.json` 当前只有 `category`、`scenario` 字段，没有 module 概念。建议改为「fallback 到 `category` 与模块约定的 category 前缀匹配的 segment」并在方案中给出 `module_id → category prefix` 的对照（如 `ma10` → `ma10_*`）。

4. **`preheat_count` 的 "when available" 防御过度**
   - 位置：2.2 Initial state
   - 改进建议：实测所有 15 个 segment 都带 `preheat_count`（来自 `slice_teaching_segment.py` 默认产出），fallback 路径 `signal_bar_index - 6` 几乎不会触发。可保留为兜底但在方案中注明「主路径恒走 preheat_count，fallback 仅用于历史遗留 seg」。

5. **`Wrong-direction signal` 段位置稍弱**
   - 位置：第 7 节末尾
   - 改进建议：把"如果实施开始添加更多 quiz step 或解释面板就是回退"这条 guard 上提到第 1 节 Direction 末尾，作为执行期自查的明显信号，不至于被读到第 7 节才看到。

## 未验证项

- `KlineEngine#play()` 在 `revealCutoff = currentIndex` 且二者同步推进时是否会持续播放：方案隐含播放可推进 cutoff，但当前引擎实现中 `play()` 在 cutoff 处会停（HANDOFF 2026-04-24 验证表第 5 行：`play()` at cutoff → `isPlaying()` stays false）。-- 建议在执行前用一段最小复现脚本验证 `revealCutoff` 跟随 `currentIndex` 同步前移时 `_playbackTick` 的行为。
- `segment.derived.checkpoints` 对方案 3.4 列举的 reason chip 类型（`trend_ok`、`ma_alignment_ok`、`touch_ma10`、`confirm_bar`、`body_not_cross`、`stop_defined`、`reward_ok`、`vwap_*`、`forbidden_absent`）的覆盖度：每个 segment 的 checkpoints 数量与 keys 不一致，部分 anti / edge 场景可能缺失 `confirm_bar` 等 key。-- 建议执行阶段对 15 个 segment 跑一次「checkpoint key × segment」覆盖矩阵，把缺失项落到方案 5 的 acceptance 中。
- `KlineView mode="lab"` 对 `highlightRanges` 在 phase 切换时的清理行为：方案要求 review 阶段叠加 standard window 与 review evidence 高亮，但未说明 replay 阶段是否要保留当前 step 的 highlight。-- 建议执行时确认 `highlightRanges = null` 与具体值切换时引擎渲染无残留。

## 裁决理由

选择 approve 的主要依据：

- 方向决断正确。隐藏未来 + 自由动作 + 窗口打分的模式与 Tang 策略「实时判断、不能事后回看」的训练核心一致，比 7 步问答更贴合真实交易决策的认知负荷。
- 范围克制。方案明确仅改 `TrainingPage`、保留 hub / module / case / mistake / archive 与全局 K 线 UX，与 HANDOFF 中第 12 项「训练页结构性重设计」对应，未越界到第 13 项「K 线 UX 整体重做」。
- 依赖就位。`setRevealCutoff` / `setHighlightRanges` / `KlineEngineAdapter` 已在 2026-04-24 完成并通过浏览器逐项验证；不要求新增引擎 API，落地路径短。
- 验收清晰。第 5 节给出的 11 条手动检查 + 3 条回归检查覆盖了主流程、边界（`too_early` / `late` / anti 场景）与不破坏既有页面。

未选择 revise 的依据：以上中等问题中，问题 1（direction 字段）属于 mapping 表选择，落地时改用 `case.direction` 即可，不动方案骨架；问题 2、3、4 是交互细节留白，可在执行阶段由起草者补丁式澄清一句；问题 5 是评估矩阵的具体化，属于实现展开。这些都不构成方向性缺陷或返工成本，符合 approve「方案可行，无严重问题，中等问题可在执行阶段自然解决」的标准。

未选择 reject 的依据：方案没有触及任何被明确否决的回退方向（未复活 `Aggregate5mBand`、未引入第二套规则源、未要求后端、未把 `training/checkpoints.json` 视为权威），且与 CLAUDE.md 中「依赖单向流动」「显式优于隐式」的原则一致。

置信度评定为 high 的依据：评审同时核对了被审方案、HANDOFF 上下文、`pages-2.jsx#TrainingPage` 现状、`shared.jsx#stepToHighlightRanges` 与 `checkpointToRanges` 实现、`cases/index.json` 与 `teaching_segments.json` 数据契约，所有中等问题均有源码或数据层证据支撑，未停留在表面文字层面的措辞分析。
