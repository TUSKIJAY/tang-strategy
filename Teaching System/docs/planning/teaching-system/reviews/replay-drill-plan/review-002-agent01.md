# 交付物评审意见

**审核对象**：training-replay-drill-redesign-plan.md（修订版）

## 整体判断
**裁决**：approve
**置信度**：high

## 总体评价

修订版针对 review-001-agent01 的 2 个严重问题和 5 个中等问题做了系统性回应。所有严重问题已解决，5 个中等问题中 4 个已充分修复、1 个部分修复但不影响实施。修订没有引入新的严重或中等问题。方案现在具备足够的精确度进入实施阶段。

## 问题清单

### 严重问题

无。

### 中等问题

无。

### 轻微问题

1. **`drillStartIndex` 的最小间距条件仅在注释中约束** 修订引入
   - 位置：§2.2 Initial state，L58-59
   - 改进建议：`clamp(signalIndex - 12, 0, last1mIndex)` 已经确保至少 12 根柱的决策空间（严重问题 #1 的核心诉求），但 L59 的 "do not use it as the drill start if it places the user within fewer than 8 bars of the signal" 是自然语言约束，没有伪代码对应。建议在实施时将 `8` 提取为常量 `MIN_DRILL_DISTANCE`。

2. **`not_scored` timing label 与 `null expectedAction` 的交叉未覆盖** 修订引入
   - 位置：§4.1 review structure，L166-167
   - 改进建议：当 `expectedAction === null` 时，`actionCorrect` 和 `timingCorrect` 均为 `null`（L168-169），`timingLabel` 应为 `not_scored`。这个推导是隐含的。建议在 review 结构旁加一句 "when `expectedAction` is null, the drill is replay-only: `timingLabel = 'not_scored'`, both `*Correct` fields are null"。

## 修订审对照表

| review-001 问题 | 级别 | 修订状态 | 说明 |
|---|---|---|---|
| 严重 #1: `preheat_count` 与信号柱距离过近 | 严重 | ✅ 已解决 | §2.2 引入 `drillStartIndex = clamp(signalIndex - 12, 0, last1mIndex)`，将 `preheat_count` 降级为历史上下文元数据，不再用作 drill 起始位置（L57-60）。 |
| 严重 #2: `confirm_bar` 缺失时 `valid_window` 无 fallback | 严重 | ✅ 已解决 | §3.2 L101 定义 `validWindowEnd = min((confirmIndex ?? signalIndex) + 1, last1mIndex)`；§3.1 L90 定义 `confirmIndex` fallback 为 `signalIndex`。窗口退化为 `[signalIndex, signalIndex + 1]`，语义清晰。 |
| 中等 #1: `等待` 与引擎 playback 关系未定义 | 中等 | ✅ 已解决 | §2.1 L41 明确 "Replay progression during the decision phase is controlled by the right rail... Hide or disable engine play/step controls"；§2.2 L65-67 定义 `等待` 为唯一的 one-bar advance，引擎工具栏 playback 在 `phase === 'replay'` 时禁用。 |
| 中等 #2: Reason chips 白名单缺失 | 中等 | ✅ 已解决 | §3.4 L124-133 定义了 4 个可见分组（Background / Trigger / Risk-space / No-trade filters）并明确"不暴露每个原始 checkpoint"，无标签的 keys 隐藏但可出现在 review 解释中。 |
| 中等 #3: `放弃` 判定条件模糊 | 中等 | ✅ 已解决 | §3.3 L108-120 给出了 5 级优先级链：`case.grade === 'anti'` → case answer 含 pass 措辞 → `case.direction` → category fallback → 无法解析则 replay-only。 |
| 中等 #4: reveal 12 bars 行为不精确 | 中等 | ✅ 已解决 | §2.2 L74-77 精确定义：强制切回 1m、`reviewRevealTarget = min(submittedIndex + 12, last1mIndex)`、先设 cutoff 再 1x 播放、用户可暂停。 |
| 中等 #5: review 对象结构缺失 | 中等 | ✅ 已解决 | §4.1 L162-178 给出完整 review 结构定义，包含 `timingLabel`、`expectedAction`、`actionCorrect`、`timingCorrect`、`validWindow`、reason 三分类、`reviewText`。 |
| 轻微 #1: `no_trade_zone` 维度归属 | 轻微 | ✅ 已解决 | `no_trade_zone` 已从 timing labels 中移除。§3.2 L104 将 anti/no-trade 案例的 timing 定义为"secondary explanatory text, not a separate grade"。 |
| 轻微 #2: wait log 验收缺失 | 轻微 | ✅ 已解决 | §5 L232 增加 "Waiting 3 times and then submitting shows 3 wait-log entries in the review panel"。 |
| 轻微 #3: segment-only fallback 无评估能力 | 轻微 | ✅ 已解决 | §4.3 L212 明确 "Segments matching the module/category only as replay-only fallback, not as scored drill"。 |

## 未验证项

- **前轮未验证项（`onPlaybackChange` 同步性、`scrollTo` 连续前进体验、`revealCutoff` 频繁更新性能）**：方案层面无法解决，仍需实施阶段验证。修订未引入新的未验证依赖。

## 裁决理由

所有严重和中等问题均已充分回应。修订引入的 2 个轻微问题是实施层面的细节，不影响方案可行性。方案现在对核心交互（drill 起始位置、等待机制、提交后行为、评估窗口计算、review 数据结构）都有精确定义，实施者不再需要在关键路径上做隐式决策。给出 **approve**。
