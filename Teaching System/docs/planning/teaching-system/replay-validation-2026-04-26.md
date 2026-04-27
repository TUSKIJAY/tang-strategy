# Replay Validation 2026-04-26 — 新口径下现有 case 重判定

> 目的：在 Plan #10（策略口径同步）动手前，先用 `tang-strategy-notes.md` 2026-04-26 合并重写版的口径过一遍 6 个现有 case + Tang 原文 §7 5 个案例，回答两个问题：
>
> 1. 现有 case 的 grade（standard / edge / anti）在新口径下是否需要翻案？
> 2. lesson 文案、rules 描述、checkpoint 语义需要哪些改动？
>
> 方法：A 档抽样人工对照（不写回测脚本，不算胜率，纯目视读 segment 的 1m 数据）。"前序验证"判定阈值 = 信号 K 之前 25 根内有 candle 出现 `L <= MA50 <= H`（即 wick / body 至少触及 MA50），并伴随回弹或拒绝。每个 case 都列出原始数据片段，确保结论可溯源。

---

## TL;DR

- **6/6 现有 case 在新口径下结论一致，没有 grade 翻案**。
- **lesson 文案需要补"MA50 是否被前序验证"和"反向回测语义"**，但语义增量是"补充"而非"重写"，原叙事仍成立。
- **§7 5 个 Tang 原文案例展示的 3-4 个核心概念当前 checkpoint 体系完全没有覆盖**：`key_level_validated` / `role_swap` / `narrow_range` / `weakening`。这是数据契约草案要列出的候选 key，**这一批不动 schema**。
- **Plan #10 范围可以维持原计划**：rules 描述补语义 + checkpoints explanation 补"已验证"措辞 + cases lesson 补一句关键位历史 + 数据契约草案；不动 `prepare_data.py`、不动 `forbidden_flags`、不让 MA10/Signal B 训练页评分回归。

---

## 1. 6 个现有 case 逐个判定

判定字段说明：
- **MA50 验证状态**：信号 K 之前 25 根内 MA50 是否被价格触及并出现反应（wick reject / body close 跨越后回弹）。
- **反向回测语义**：是否能用 §4.4（支撑阻力互换）或 §2.2 步骤 8（反向回测失败 = 逻辑失效）解释。
- **新口径结论**：grade 是否变化、lesson 是否需要补充。

### 1.1 case_ma10_support_2026_01_07 (standard, support_ma10)

- 信号 idx 31 (11:36)：close 692.31, m10 692.31, m50 692.47
- **MA50 验证状态**：✅ 已验证。bars 15-19 (11:20–11:24) 连续 5 根 `L <= MA50 <= H`，11:20 wick 下探 692.33 close 拉回 692.45（明确 reject），11:23 close 692.35 略破后 11:24 close 692.39 拉回。后续 26-30 (11:31–11:35) 进入第二轮反复测试。
- **反向回测语义**：不适用（MA10 case，主入场线是 MA10）。
- **新口径结论**：**grade 不变 (standard)**。lesson 可补一句"MA50 在 11:20-11:24 已被多次 wick 测试并撑住，所以 11:36 的 MA10 触及具有更强的次级防线背景，做多逻辑的支撑结构更完整"。
- **改动等级**：**轻度补充**。

### 1.2 case_ma10_reject_2026_03_09 (standard, reject_ma10)

- 信号 idx 53 (11:33)：close 669.19, m10 669.53 (price BELOW MA10), m50 668.53
- **MA50 验证状态**：❌ 未验证。bars 28-52 (11:08–11:32) 价格基本在 m50 上方 +0.10%~+0.33%，m50 一路在远下方未被触及。最近的 d50 距离都在 +0.10% 以上。
- **反向回测语义**：不适用。
- **新口径结论**：**grade 不变 (standard)**。lesson 可补一句"MA50 (668.53) 在前序未被价格测试，仅作为远方的次级防线参考；空头入场依赖 MA10 反抽失败本身的形态质量，不能机械把 MA50 当强支撑"。
- **改动等级**：**轻度补充**。

### 1.3 case_ma10_edge_2026_02_03 (edge, reject_ma10)

- 信号 idx 35 (10:05)：close 693.10, m10 693.25 (price BELOW MA10), m50 695.21
- **MA50 验证状态**：✅ 已验证。bars 10-22 (09:40–09:52) 早盘价格在 695.5–696.1 区间反复测试 m50（约 695.6–695.8），多次 `L <= MA50 <= H`。但从 09:55 开始急跌，**实体跌破 MA50 后没有回测就一路向下**，到 10:05 时已远离 MA50 -0.30%。
- **反向回测语义**：✅ 适用。前序的"价格在 MA50 上方反复测试"（9:40–9:52）→ 09:55 实体跌破 MA50 → 没有反向回测就直接下行 → MA50 多头逻辑已失效。但因为是开盘 30 分钟边缘 + 没有清晰回测，所以仍属 edge。
- **新口径结论**：**grade 不变 (edge)**。lesson 需要中度改写：
  - 旧：`触发形态存在，但背景和禁做项冲突，不应按标准例处理。`
  - 新口径方向：`MA50 早盘已被验证为支撑（09:40–09:52），09:55 实体跌破后无明显回测就一路下行，多头逻辑已失效；但 10:05 仍处人工口径"开盘 30 分钟慎入"窗口（项目实现按 forbidden_flags 硬禁入），即便形态触发也不应按标准例进场——这是 edge 的双重原因。`
- **改动等级**：**中度改写**。

### 1.4 case_signal_b_2026_03_25 (standard, signal_b)

- 信号 idx 51 (11:05)：close 658.44, m10 658.72, m50 658.46, vwap 658.32
- **MA50 验证状态**：✅ 已验证。bars 47-50 (11:01–11:04) 连续 4 根 close 与 m50 距离 ≤ +0.06%，三根 `L <= MA50 <= H`；从更早看，bars 26-46 价格在 m50 上方 +0.07%~+0.27% 范围，没触及；47 开始进入测试。
- **反向回测语义**：✅ 部分适用。MA50 经过 47-50 的反复测试后，51 信号 K 收盘 658.44 < m50 658.46，**双线（MA10 658.72 + MA50 658.46）同时被实体跌破** = 信号 B 定义。这恰好印证了"被验证的关键位被跌破"是有意义的。
- **新口径结论**：**grade 不变 (standard)**。lesson 可补一句"MA50 在 11:01-11:04 已被价格反复测试为支撑，11:05 信号 K 同时跌破 MA10 和已验证的 MA50，构成双线突破的有效信号——而非仅仅是机械碰线"。
- **改动等级**：**中度补充**。

### 1.5 case_quality_anti_2026_02_13 (anti, candle_body_quality)

- 信号 idx 48 (14:48)：close 683.65, m10 683.80, m50 684.61
- **MA50 验证状态**：✅ 早期已验证（bars 26-30, 14:26-14:30 多次触及）。但信号点附近 (idx 41-48) 价格已远在 m50 下方 -0.11%~-0.19%。
- **反向回测语义**：不直接适用——anti 的核心在 candle 实体质量。
- **新口径结论**：**grade 不变 (anti)**。lesson 主因仍是 candle 质量，新口径只补一句辅助说明"虽然 MA50 早期被测试，但当前位置已离 MA50 -0.14%，已不是有效防线区间，且实体连续缩小 + 不延续表明动能不足"。
- **改动等级**：**很轻**。

### 1.6 case_barrier_anti_2026_02_11 (anti, vwap_distance_filter)

- 信号 idx 46 (11:59)：close 692.05, m10 692.52, m50 692.63, m200 692.79, vwap 692.70
- **MA50 验证状态**：✅ 已验证。bars 22-26 (11:35-11:39) 多次 `L <= MA50 <= H`；后续 36-43 也有触及。
- **反向回测语义**：✅ 重要。bars 27-29 (11:40-11:42) 价格冲到 693.0–693.35 **突破** m200 (692.87)；但 bars 35-46 价格回落到 m200 下方 692.5–693.0 区间反复，**突破 MA200 后回测失败** → 多头逻辑已失效。但同时上方仍是 MA200 / VWAP 密集压制（692.79 / 692.70），**做空风险回报仍不成立**（下方目标空间不足，刚到 MA50 692.63 就抵达）。
- **新口径结论**：**grade 不变 (anti)**。lesson 中度改写：
  - 旧：`形态看似触发，但 MA200 关卡距离过近，风险回报不成立。`
  - 新口径方向：`11:40-11:42 多头突破 MA200 (692.87) 后未能站稳，11:48 起回到 MA200 下方反复——多头反向回测失败，逻辑已失效；但上方 MA200/VWAP 仍构成密集压制，下方仅到已验证的 MA50 (692.63)，做空风险回报不成立。这是双重原因：多头不能做（逻辑失效），空头也不能做（空间不足）。`
- **改动等级**：**中度改写**。

### 1.7 6 个 case 总结表

| Case | Grade | MA50 验证 | 反向回测 | 新口径结论 | Lesson 改动 |
|---|---|---|---|---|---|
| case_ma10_support_2026_01_07 | standard | ✅ 已验证 | n/a | 不翻案 | 轻度补 |
| case_ma10_reject_2026_03_09 | standard | ❌ 未验证 | n/a | 不翻案 | 轻度补 |
| case_ma10_edge_2026_02_03 | edge | ✅ 早期验证 | ✅ 跌破后无回测 | 不翻案 | 中度改写 |
| case_signal_b_2026_03_25 | standard | ✅ 已验证 | ✅ 双线被跌破 | 不翻案 | 中度补 |
| case_quality_anti_2026_02_13 | anti | ✅ 早期验证 | n/a | 不翻案 | 很轻 |
| case_barrier_anti_2026_02_11 | anti | ✅ 已验证 | ✅ 突破回测失败 | 不翻案 | 中度改写 |

**结论 1**：**6/6 case 不翻案**。新口径不会让任何现有 case 的 grade 改变，意味着不需要重做训练评分逻辑、不会让 MA10 / Signal B 训练页行为回归。

**结论 2**：**lesson 文案改动量分布**：轻度 4 / 中度 2 / 翻案 0。可以一次性起草，不需要重新设计 case 结构。

**结论 3**：**反向回测语义首次进入 lesson 叙事**。3 个 case (edge / anti / signal_b) 都涉及"突破/跌破后是否被回测确认"这个判断维度。当前 checkpoint 体系没有 `reverse_retest_failed` / `role_swap` 这类 key，需要进数据契约草案。

---

## 2. §7 五个 Tang 原文案例的概念覆盖度

§7 案例没有 segment 数据（来自 Tang 复盘原文），无法做精确数据回测。这一节做"概念符号映射"——看新口径展示的核心概念，当前规则 / checkpoint 体系覆盖了多少。

| 案例 | 新口径核心概念 | 现有规则 / checkpoint 覆盖度 | 缺口 |
|---|---|---|---|
| A. MA50 作为下午分界线 | (1) MA50 被验证后才作为分界线<br>(2) VWAP 突破后回测确认（阻力转支撑）<br>(3) 9:56/10:24/10:41 三个低点抬高 = 力量衰减 | trend_ok / vwap_intercept 部分覆盖 (1)；(2) 和 (3) 完全没有 | **需要 `key_level_validated`、`role_swap`、`weakening`** |
| B. MA200 决战窄区间 | (1) 11:30-13:14 被压在 MA200 下方 = 窄区间<br>(2) 突破后 13:25 回测确认<br>(3) 13:02 跌不下去 = 空方衰减 | 完全没有"窄区间"概念 | **需要 `narrow_range`、`role_swap`、`weakening`** |
| C. 上方均线密集不能强行做多 | 多条均线压在上方时空间不足 | vwap_distance_filter 单线覆盖；没有"密集均线压制"概念 | **需要 `density_blocked`（多线压制）** |
| D. 做空设想的前置条件 | 顺势 + 5min 被压住 + MA20 reject = 反抽失败 | trend_ok / ma_alignment_ok 覆盖顺势；reject_ma10 覆盖反抽（但是针对 MA10，不是 MA20） | **需要"反抽失败"通用化**（不限于 MA10） |
| E. 多头力量衰减 | 697.80 大阴线 / 冲高失败 = 早期衰减信号 | 完全没有 | **需要 `momentum_loss` / `weakening`** |

**结论 4**：当前 checkpoint 体系（§8.2 表格 9 项）覆盖度只够说"形态触发"层（MA10 触及、实体未破、确认 K、止损、空间），不够说"为什么这条线有效"和"什么时候逻辑失效"。Plan #10 数据契约草案应该列出这些候选 key，但**这一批不实施**——优先级低于 lesson 文案同步。

**结论 5**：§7 案例 D "做空前置条件"暴露了一个潜在 schema 问题：当前 `reject_ma10` 是针对 MA10 的强类型规则，没有通用的 "reject_ma_X" 规则定义。如果未来要把"5min MA20 reject"做进系统，需要先讨论 schema 是否要泛化。**这一批不动**。

---

## 3. 对 Plan #10 范围的影响

基于以上判定，Plan #10 的执行范围保持原计划，分两层：

### 3.1 文案 / 规则口径同步层（这一批做）

| 文件 | 改动量 | 重点 |
|---|---|---|
| `rules/compiled/index.json` | 4 个规则的 description 补"已验证关键位"语义 | `support_ma10` / `reject_ma10` / `vwap_distance_filter` / `background_5m` |
| `training/checkpoints.json` | 涉及 MA50/MA200/VWAP 的 explanation 补"该线是否已被前序验证" | 估计 6-10 处 |
| `cases/index.json` | 6 个 case 的 lesson 补"前序验证 + 反向回测"语义 | 4 轻 / 2 中 |
| `tang-strategy-notes.md` | 不动（已经是源） | — |

### 3.2 数据契约草案层（这一批起草，不实施）

新建 `docs/planning/teaching-system/key-level-validation.md`，列出候选 checkpoint key + 字段：

| 候选 key | 用途 | 字段草案 |
|---|---|---|
| `key_level_validated` | 通用关键位验证 | level_type (m50/m200/vwap), prior_test_count, last_reaction_time |
| `ma50_validated` | MA50 专用细分 | （上面的 specialization） |
| `prior_reaction_ok` | 前序反应记录 | reaction_type (reject/support/break), reaction_strength |
| `role_swap` | 角色互换（阻力转支撑等） | original_role, new_role, swap_confirmed_at |
| `reverse_retest_failed` | 反向回测失败 = 逻辑失效 | original_signal_idx, retest_idx, fail_reason |
| `narrow_range` | 窄幅震荡区间 | range_high, range_low, bound_count, lines_in_range |
| `weakening` / `momentum_loss` | 力量衰减 | direction (up/down), pattern (lower_high / fail_to_break / shrinking_body) |
| `density_blocked` | 上方/下方多线密集压制 | side (above/below), lines, distance_pct |

**这些 key 在草案文档里讨论字段、判定阈值和数据采集方式，等样本积累 + 与 prepare_data.py 兼容性验证后才进 schema。**

### 3.3 这一批明确不做

- ❌ 不改 `prepare_data.py` 检测算法
- ❌ 不取消 `forbidden_flags`（开盘 30 分钟保持双轨说明）
- ❌ 不新增 checkpoint key 到 `teaching_segments.json` schema
- ❌ 不重写 §7 案例 D 暗示的 reject_ma_X 通用化
- ❌ 不让任何 case 的 grade 翻案

---

## 4. 数据来源（可溯源）

每个 case 的判定依据都来自 `data/processed/teaching_segments.json` 实际 bar 数据。判定时取信号 K 之前 25 根，列出 O/H/L/C + m10/m50/m200/vw + d50（close 距 m50 百分比）+ 是否触及 m50（`L <= m50 <= H`）。

完整数据脚本：

```python
import json
with open('data/processed/teaching_segments.json') as f: segs = json.load(f)
with open('cases/index.json') as f: cases = json.load(f)['cases']
seg_by_id = {s['id']: s for s in segs['segments']}

def pct(a, b):
    if b is None or b == 0: return None
    return (a - b) / b * 100

for case in cases:
    seg = seg_by_id[case['segment_id']]
    sig_idx = seg.get('derived', {}).get('signal_bar_index') or case['decision_bar']['bar_index']
    # ... 读取 bars[sig_idx-25 : sig_idx+2] 并打印
```

---

## 5. 下一步

如果用户确认本报告结论：

1. 起草 `docs/planning/teaching-system/key-level-validation.md` 数据契约草案
2. 起草 4 个规则的 description 补丁（`rules/compiled/index.json`）
3. 起草 6 个 case 的 lesson 补丁（`cases/index.json`）
4. 起草 6-10 处 checkpoint explanation 补丁（`training/checkpoints.json`）
5. 所有 diff 先给用户看，不直接 commit

如果用户对某个 case 的判定有不同意见（特别是 case_ma10_edge_2026_02_03 和 case_barrier_anti_2026_02_11 两个中度改写），先校准后再动文案。
