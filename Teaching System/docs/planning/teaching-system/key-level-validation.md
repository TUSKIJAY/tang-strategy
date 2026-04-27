# Key Level Validation — Schema 草案

> 状态：**RFC / 草案，未实施**。
>
> 来源：`tang-strategy-notes.md` 2026-04-26 合并重写版 §2.1 步骤 2、§4.3、§4.4、§4.5、§4.6、§8.3。回测对照见 `replay-validation-2026-04-26.md`。
>
> 目的：登记新口径下需要进系统的 checkpoint key + 字段，作为后续（不是这一批）schema 演进的输入。这一批 Plan #10 仅用于教学文案/规则说明，不动 `prepare_data.py`，不动 `teaching_segments.json` schema。

---

## 0. 为什么需要这层数据

旧体系（`teaching_segments.json#derived.checkpoints` 9 项）回答的是"形态触发了没"：

- `trend_ok` / `ma_alignment_ok`：5min 背景
- `touch_ma10` / `body_not_cross` / `confirm_bar`：1min 触发形态
- `stop_defined` / `reward_ok`：风险回报
- `forbidden_absent`：禁做条件
- `vwap_intercept`：VWAP 拦截

新口径（§4.3、§4.4）要求回答"**这条线为什么有效 / 什么时候逻辑失效**"，旧体系完全没有覆盖。本草案列出候选 key + 字段，等样本积累后才进 schema。

---

## 1. 候选 Checkpoint Keys

### 1.1 关键位验证类（入场判断维度）

#### `key_level_validated`（通用）

> 价格当前接近的某条关键线 / 关键价位是否已被前序验证为有效位置。

| 字段 | 类型 | 说明 |
|---|---|---|
| `level_type` | enum | `ma10` / `ma50` / `ma200` / `vwap` / `prior_high` / `prior_low` / `prev_close` / `pre_market_high` / `pre_market_low` |
| `level_value` | number | 该关键位的价格 |
| `validated` | bool | 是否已被前序验证 |
| `prior_test_count` | int | 前序触及次数（`L <= level <= H` 的 candle 数） |
| `prior_reaction_strength` | enum | `strong` / `weak` / `none`（`strong` = 触及后 close 强势回弹；`weak` = 略破后回；`none` = 仅穿过未反应） |
| `last_reaction_idx` | int | 最近一次明显反应的 bar index |
| `last_reaction_idx_distance` | int | `signal_idx - last_reaction_idx` |

**判定阈值草案**（待 sample 后调整）：

- 触及 = `L <= level <= H` 且 `|close - level| / level <= 0.05%`
- `strong reaction` = 触及后 ≤3 根内 close 反向幅度 ≥ 0.10%
- `validated` = `prior_test_count >= 2` 且 `last_reaction_idx_distance <= 30`（约半小时内）

#### `ma50_validated`（specialization）

`key_level_validated` 的 MA50 专项快捷字段，避免每次都要在通用结构里筛 `level_type='ma50'`。同字段集，只是过滤了 level_type。

#### `prior_reaction_ok`

> 信号 K 之前最近一次的关键位反应是否符合策略叙事。

| 字段 | 类型 | 说明 |
|---|---|---|
| `reaction_idx` | int | 反应发生的 bar |
| `reaction_type` | enum | `reject`（被压回）/ `support`（被撑住）/ `break_and_retest`（突破后回测）/ `break_and_continue`（突破后未回测）/ `wick_only`（仅影线触及） |
| `expected_for_signal` | enum | 当前信号预期需要哪种反应类型（如 reject_ma10 期望 `reject`） |
| `match` | bool | reaction_type 是否匹配 expected |

### 1.2 角色互换 / 反向回测类（出场判断维度）

#### `role_swap`

> 关键位是否发生了"阻力转支撑"或"支撑转阻力"的角色互换。

| 字段 | 类型 | 说明 |
|---|---|---|
| `level_type` | enum | 同上 |
| `level_value` | number | |
| `original_role` | enum | `resistance` / `support` |
| `new_role` | enum | `support` / `resistance` |
| `swap_confirmed_at` | int | 完成角色互换的 bar idx |
| `confirm_pattern` | enum | `break_and_retest_success`（突破后回测成功）/ `break_and_retest_fail`（跌破后回测失败） |

#### `reverse_retest_failed`

> 入场后，原方向的关键位被反向突破并回测失败 = 原交易逻辑已失效。这是出场触发条件，不是入场过滤。

| 字段 | 类型 | 说明 |
|---|---|---|
| `original_signal_idx` | int | 入场时的 signal_bar_index |
| `original_direction` | enum | `long` / `short` |
| `level_type` | enum | 失效的关键位 |
| `retest_idx` | int | 反向回测发生的 bar |
| `retest_outcome` | enum | `failed`（回测后无法重新站回原侧）/ `succeeded`（回测后回到原侧） |
| `should_exit` | bool | 是否触发立即出场 |

**注意**：本字段在系统层落地需要把"出场触发"机制和入场链分开，目前 `teaching_segments.json#derived.checkpoints` 全是入场维度。需要新增 `exit_checkpoints` 数组或类似结构。

### 1.3 衰减 / 窄区间 / 密集压制类（背景判断维度）

#### `narrow_range`

> 价格被多条关键线挤在窄区间内，方向不明，不应提前猜方向。

| 字段 | 类型 | 说明 |
|---|---|---|
| `range_high` | number | 区间上界 |
| `range_low` | number | 区间下界 |
| `range_pct` | number | `(high - low) / mid` |
| `bars_in_range` | int | 在区间内停留的 bar 数 |
| `lines_in_range` | array | 当前在区间内的关键线 keys |
| `is_squeeze` | bool | 多条线在区间内挤压 |

**判定阈值草案**：

- `range_pct <= 0.30%` 且 `bars_in_range >= 20` 且 `lines_in_range.length >= 3`

#### `weakening` / `momentum_loss`

> 力量衰减信号：低点逐渐抬高 / 高点逐渐降低 / 第三次推进失败 / 大阴阳线打破节奏。

| 字段 | 类型 | 说明 |
|---|---|---|
| `direction` | enum | `up_weakening`（多方衰减）/ `down_weakening`（空方衰减） |
| `pattern` | enum | `lower_high` / `higher_low` / `fail_to_break` / `large_counter_candle` / `shrinking_body_chain` |
| `evidence_idx` | array | 关键 bar 索引 |
| `confirmed` | bool | 是否构成衰减确认 |

#### `density_blocked`

> 入场方向上方/下方有多条关键线密集压制，目标空间不足。

| 字段 | 类型 | 说明 |
|---|---|---|
| `side` | enum | `above`（在价格上方）/ `below`（在价格下方） |
| `lines` | array | `[{type, value, distance_pct}, ...]` |
| `total_distance_to_first_line` | number | 距离最近的一条线（百分比） |
| `target_space_sufficient` | bool | 是否仍满足风险回报 |

---

## 2. 数据采集方式 — 三阶段

### 阶段 1：人工标注（这一批不实施）

直接在 `cases/index.json` 的某个 case 上加 `manual_validation_notes` 字段，文字描述："MA50 在 11:20-11:24 被验证（5 次 wick reject）"。这是低成本试点，等积累 5-10 个 case 后再进阶段 2。

### 阶段 2：派生字段（中期）

把上面的 candidate keys 接入 `prepare_data.py` 的派生计算：

- `key_level_validated` 用滑动窗口扫描 + 触及判定
- `narrow_range` 用区间检测算法
- `weakening` 用形态识别（lower high / higher low / 实体序列）
- `role_swap` 需要先识别"突破事件"再判断后续回测

### 阶段 3：教学场景集成（长期）

- 教学训练页加入"验证维度" reason chips：用户除了选触发理由，还要选"为什么这条线有效"
- 出场维度在 replay drill 中独立体现：到达 reverse_retest_failed 时强制提示

---

## 3. 与现有 schema 的关系

| 现有 checkpoint key | 是否动它 | 备注 |
|---|---|---|
| `trend_ok` | 不动 | 5min 趋势 |
| `ma_alignment_ok` | 不动 | 均线排列 |
| `touch_ma10` | 不动 | MA10 触及 |
| `body_not_cross` | 不动 | 实体未穿越 |
| `confirm_bar` | 不动 | 确认 K |
| `stop_defined` | 不动 | 止损位 |
| `reward_ok` | **可能升级** | 长期可改为读 `density_blocked` 派生 |
| `forbidden_absent` | 不动 | 禁做条件汇总 |
| `vwap_intercept` | **可能升级** | 长期可改为读 `key_level_validated[level_type=vwap]` 派生 |

**这一批不动任何现有 key**。Plan #10 的现有 explanation 文案改写仍用现有 key 名，只是用更精准的话语描述同一个判定。

---

## 4. 不进系统的内容

以下来自 `tang-strategy-notes.md` 的策略要素，**判断为不适合系统化**或**优先级低于 §1 候选 key**：

| 策略要素 | 不进系统的原因 |
|---|---|
| §2.1 步骤 5 "前路阻力或支撑" | 已被 `vwap_distance_filter` + `density_blocked`（候选）覆盖 |
| §4.6 窄区间末期"跌不下去 / 涨不上去" | 主观判断，难以阈值化；可作为 `weakening.pattern.fail_to_break` 的子集 |
| §5.1 人工"慎入" vs §5.2 项目"禁入" | **保持双轨**——这一批 plan 明确不取消 forbidden_flags，只在文案上分层 |
| §7 案例 D "5min MA20 reject" | 当前 `reject_ma10` 是 MA10 强类型规则，要支持需要把规则结构泛化为 `reject_ma_X(level)`。这是 schema 重构，不在 Plan #10 范围 |

---

## 5. 验收 / 退出条件

本文档作为 Plan #10 数据契约层的产出。验收标准：

1. ✅ 列出新口径下需要表达的所有判断维度（入场关键位验证、出场反向回测、背景衰减/窄区间/密集压制）。
2. ✅ 每个候选 key 有字段草案 + 判定阈值方向。
3. ✅ 明确什么不做（§4）。
4. ✅ 与现有 9 个 checkpoint key 的关系说明清楚（§3）。

后续 Plan：当样本积累到 ≥10 个 case 且至少 3 个 case 在 lesson 文案中明确用到新维度时，启动阶段 2（派生字段）。
