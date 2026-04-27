# 交付物评审意见

**审核对象**：training-replay-drill-redesign-plan.md

## 整体判断
**裁决**：revise
**置信度**：high

## 总体评价

方案方向正确且清晰。将 Training 页面从「7 步规则问答」重构为「隐藏未来的 K 线回放演练」，是对用户反馈 #12（"完全不知所云的感觉"）的合理回应。核心洞察——训练真实决策而非规则记忆——是一个产品层面的正确转向。方案的 scope 控制良好，明确限定只改 TrainingPage，不扩散到其他页面，符合项目的渐进式演进风格。

方案在产品模型、评估体系和技术实现三个维度都有覆盖，层次分明。对现有引擎 API（`revealCutoff`、`highlightRanges`、`onPlaybackChange`）的复用判断准确，与 HANDOFF.md 和 INTEGRATION.md 中记载的能力一致。Non-Goals 清单清晰，防止了典型的 scope creep 方向。

主要不足集中在三个方面：(1) 数据层存在概念引用但未核查其实际可用性，(2) 几个关键交互的边界条件缺乏定义，(3) 评估模型的 `confirm_bar` 依赖隐含了一个未被声明的数据可选性问题。这些问题需要修订后才能进入实施阶段。

## 问题清单

### 严重问题

1. **`preheat_count` 在多数 segment 中为固定值，初始隐藏位置逻辑未考虑实际分布**
   - 位置：§2.2 Drill Flow — Initial state
   - 问题描述：方案写道 "Start at `segment.preheat_count` when available"，fallback 为 `signal_bar_index - 6`。经核查，15 个 segment 全部具有 `preheat_count` 字段（值从 12 到 30 不等），所以 fallback 分支永远不会被触发。但实际问题是：`preheat_count=30` 意味着用户初始可见 30 根 1m 柱，而 `signal_bar_index` 通常为 31（如 seed_01）。这意味着用户只需前进 1 根柱就到达信号位置，几乎没有"观察和判断"的空间——与"让用户在不确定性中做决策"的设计意图矛盾。
   - 影响范围：drill 的核心体验——用户应该在未知中前进若干根柱再做决策，而非一开始就几乎看到信号柱。
   - 改进建议：明确 drill 的初始可见范围应如何计算。建议引入 `drill_start_offset`（如 `signal_bar_index - 15`）或在方案中定义一个"用户至少需要前进 N 根柱才能到达信号区域"的下限。如果 `preheat_count` 的语义本就是"到信号柱之前的预热区"，需要在方案中声明这一关系并确认数据一致性。

2. **`confirm_bar` checkpoint 缺失时 `valid_window` 无 fallback 定义**
   - 位置：§3.1 Standard Inputs + §3.2 Timing Labels
   - 问题描述：方案写 "`valid_window`: from `signal_bar_index` through `confirm_bar + 1`"。经核查，当前 15 个 segment 的 `derived.checkpoints` 中确实都有 `confirm_bar` key。但方案自身在 §3.1 中写 "Confirm index: checkpoint `confirm_bar.bar_index` **when present**"，暗示它可能缺失。方案未定义当 `confirm_bar` 缺失时 `valid_window` 的上界应该是什么。
   - 影响范围：如果未来新增的 segment 缺少 `confirm_bar`（方案既然考虑了 "when present"，说明预期到这种可能），评估将无法计算 `valid_window` 的结束边界，导致 `too_early` / `valid_window` / `late` 分类失败。
   - 改进建议：为 `confirm_bar` 缺失时定义明确的 fallback，例如 `valid_window` 上界为 `signal_bar_index + N`（固定偏移），或将该行为标注为 "当 confirm_bar 缺失时，valid_window 退化为单点 [signal_bar_index, signal_bar_index]"。

### 中等问题

1. **`等待` 按钮和引擎 playback 控件的交互关系未定义**
   - 位置：§2.2 Drill Flow — During replay
   - 问题描述：方案定义了 `等待`（前进一根柱并记录）和 `下一根 / play controls`（前进但不结束 drill）。但 KlineEngine 已有 `stepForward()` 和 `play()`，这些通过引擎工具栏暴露在 lab 模式中。方案未说明：(a) `等待` 按钮是否应调用 `stepForward()` + 更新 `revealCutoff`？(b) 引擎工具栏的 `play` 按钮是否也推进 `revealCutoff`？(c) 是否需要禁用引擎工具栏的 step/play 来避免与右侧 rail 上的 `等待` 按钮冲突？
   - 改进建议：明确 `等待` 与引擎 playback 的关系。建议：`等待` = `stepForward()` + `revealCutoff += 1` + 记录 wait log；引擎工具栏的 play/step 也推进 cutoff 但**不**记录 wait log（即仅是观看行为，不是决策行为）。或者：drill 模式下禁用引擎工具栏的 playback 控件，所有前进都通过右侧 rail 按钮。

2. **Reason chips 的数据来源优先级与现有代码不一致**
   - 位置：§4.3 Data Fallback
   - 问题描述：方案写 "Reason chips and review should come from `segment.derived.checkpoints` first"。但经核查，当前 `TrainingPage` 的 reason chips 实际来自 `training/checkpoints.json` 中的 `steps[i].checkpoint_keys`，然后通过 `checkpointFor(segment, key)` 回到 segment 获取 pass/fail 状态。方案的新 drill 模型移除了 step 概念，reason chips 需要直接从 segment checkpoints 提取——但 segment checkpoints 是扁平的 8-9 个 key（如 `trend_ok`, `touch_ma10` 等），没有按"显示给用户的 reason chip"分组。方案未定义哪些 checkpoint 应该作为 reason chip 暴露给用户选择、哪些应该隐藏。
   - 改进建议：定义一个 reason chip 白名单或分类映射，说明哪些 checkpoint keys 应该作为用户可选的 reason chips 出现。§3.4 中的分类（5m background / Trigger / Risk-space / No-trade filters）是个好的起点，但需要明确这是 UI 分组标签还是过滤规则。

3. **`放弃` 的评估条件依赖未定义的 `forbidden_absent` 逻辑**
   - 位置：§3.3 Direction Labels + §3.4 Reason Review
   - 问题描述：方案写 "anti / forbidden cases expect `放弃` unless the case manifest explicitly says otherwise"，以及 reason chips 包括 `forbidden_absent`。经核查，`forbidden_absent` checkpoint 在所有 segment 中的 `passed` 都为 `True`，`bar_index` 为 `None`。这意味着当前数据集中没有任何 segment 的 `forbidden_absent` 为 `False`。那么 "forbidden evidence" 来自哪里？是来自 case manifest 的 `grade === '反例'` 标记，还是来自 checkpoint？方案未澄清。
   - 改进建议：明确 `放弃` 的判定条件。建议：当 `case.grade === '反例'` 时，expected action = `放弃`；`forbidden_absent` checkpoint 仅作为辅助展示，而非判定依据。

4. **review 阶段 "reveal and play the next 12 1m bars" 的行为定义不足**
   - 位置：§2.2 Drill Flow — After submission
   - 问题描述：方案写提交后 "Reveal and play the next 12 1m bars by default"。但未定义：(a) "play" 是自动播放（auto-advance）还是仅设置 `revealCutoff += 12` 让用户看到？(b) 如果自动播放，速度是多少？(c) 如果 12 根柱超出了 segment 的 bars_1m 范围怎么处理？(d) 用户是否可以在自动播放期间中断？
   - 改进建议：定义 reveal 行为的精确语义。建议：submission 后立即将 `revealCutoff` 扩展 12 根柱（`min(submittedIndex + 12, bars_1m.length - 1)`），然后以 1x 速度自动播放到新 cutoff，播放期间用户可点击暂停。

5. **State schema 缺少对 review 结果的结构定义**
   - 位置：§4.1 TrainingPage — state schema
   - 问题描述：state 中有 `review: null` 字段，但方案未定义 review 对象的结构。§3.2-3.4 定义了 timing labels、direction labels、reason review 三个维度的评估输出，但未说明它们如何组合成 `review` 对象。实施者需要猜测数据结构。
   - 改进建议：在 state schema 旁给出 review 对象的结构定义，例如 `{ timingLabel: 'valid_window' | 'too_early' | 'late' | 'no_trade_zone', directionCorrect: boolean, expectedAction: '做多' | '做空' | '放弃', reasonHits: string[], reasonMisses: string[], reasonContradictions: string[] }`。

### 轻微问题

1. **`no_trade_zone` timing label 的边界与 `late` 重叠**
   - 位置：§3.2 Timing Labels
   - 改进建议：`no_trade_zone` 描述的是"不该交易"，与 `too_early`/`valid_window`/`late` 不在同一维度。考虑将其移到 direction labels（作为 expected_action=`放弃` 的同义标记），或明确当 case 是反例时 timing label 的处理规则。

2. **Acceptance Checks 缺少对 `等待` 日志的验收条件**
   - 位置：§5 Acceptance Checks
   - 改进建议：增加一条验收："`等待` 3 次后提交 `做多`，review panel 中显示 3 条等待记录和最终提交"。

3. **Case 选择 fallback 路径 3 引入了无评估能力的 drill**
   - 位置：§4.3 Data Fallback — priority 3
   - 改进建议："Segments matching the module/category when no case manifest exists" 的 drill 会缺失 case 级别的评估数据。声明为 "replay only, no evaluation" 或要求所有参与 drill 的 segment 必须有对应的 case manifest。

## 未验证项

- **`KlineEngineAdapter` 的 `onPlaybackChange` 触发时机是否满足 drill 同步需求**：方案的 drill 需要在每次 `stepForward` 后同步更新 `revealCutoff`。经核查 `onPlaybackChange` 回调存在并返回 `index` 字段（shared.jsx L497-498），但无法仅通过代码阅读确认回调触发是同步还是异步。 -- 建议在实施阶段做 spike 验证。
- **`scrollTo({ center: true })` 在连续 stepForward 场景下的视觉体验**：drill 中用户逐根前进，每次居中会导致视口跳动。 -- 实施阶段需验证是否应改为 "keep visible but don't center" 模式。
- **频繁更新 `revealCutoff` 的渲染性能**：drill 每按一次 `等待` 就要 `setRevealCutoff(n+1)` 触发引擎重渲染。当前无 benchmark 数据。 -- 如果卡顿明显，考虑批量 reveal 或 debounce。

## 裁决理由

方案方向无争议，产品定位清晰，技术选型合理地复用了现有引擎能力。给出 **revise** 而非 approve 的主要依据：

1. **严重问题 #1**（`preheat_count` 与 drill 起始位置的语义冲突）直接影响核心体验——如果用户一开始就在信号柱旁边，drill 就失去了"在不确定性中决策"的意义。这需要在方案层面明确而非留给实施者去发现。
2. **严重问题 #2**（`confirm_bar` 缺失时的 `valid_window` fallback）是一个防御性但必要的定义，方案自身已暗示了这种可能性（"when present"），不应留到实施阶段才发现无法处理。
3. 中等问题中的 `等待` 与引擎 playback 关系（#1）和 review 结构定义（#5）虽然不阻塞方向，但缺失它们会导致实施者在核心交互上做隐式决策，增加返工风险。

修订范围可控，预计一轮即可通过。
