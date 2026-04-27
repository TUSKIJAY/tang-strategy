# JSON 数据格式规范

> **版本**: v1.2  
> **日期**: 2026-04-22  
> **适用范围**: `data/processed/` 下所有 JSON 文件  

---

## 1. 设计原则

| 原则 | 说明 |
|---|---|
| **单字段缩写** | Bar 内高频字段用 1~3 字母缩写（`O/H/L/C/V`），节省体积 |
| **命名惯例** | 顶层 meta 字段用 `snake_case`，Bar 内字段用 **大写缩写**，中间结构用 `snake_case` |
| **null 合法** | 均线字段在数据点不足时为 `null`，解析器必须处理 |
| **时间字段冗余** | `ts`（完整时间戳）用于精确定位，`t`（HH:MM）用于 UI 显示，两者并存 |
| **向后兼容** | 新增字段不得破坏旧解析器；废弃字段先标注 deprecated，隔一个版本再移除 |

---

## 2. 文件类型总览

`data/processed/` 下目前存在 **3 种** JSON 文件类型：

| 文件类型 | 命名模式 | 用途 | 示例 |
|---|---|---|---|
| **full-day** | `SPY_YYYY-MM-DD.json` | 整日 1m+5m 数据，引擎消费 | `SPY_2026-04-13.json` |
| **seed** | `kline-engine-v2-seed.json` | 单个教学片段的完整数据 | seed_01 |
| **teaching-segments** | `teaching_segments.json` | 所有教学片段集合 | 15 个 segment |

---

## 3. Bar 对象（核心数据单元）

每根 K 线是一个 JSON 对象，字段定义如下：

### 3.1 字段清单

| 字段 | 类型 | 必填 | 说明 | 示例 |
|---|---|---|---|---|
| `ts` | `string` | ✅ | ISO 8601 时间戳，含时区 | `"2026-01-07T11:05:00-05:00"` |
| `t` | `string` | ✅ | 显示用时间 `HH:MM` | `"11:05"` |
| `O` | `number` | ✅ | 开盘价（Open） | `692.72` |
| `H` | `number` | ✅ | 最高价（High） | `692.75` |
| `L` | `number` | ✅ | 最低价（Low） | `692.61` |
| `C` | `number` | ✅ | 收盘价（Close） | `692.66` |
| `V` | `integer` | ✅ | 成交量（Volume） | `118274` |
| `vw` | `number` | ✅ | VWAP¹ | `692.08` |
| `hO` | `number` | ✅ | Heikin-Ashi 开盘 | `692.71` |
| `hH` | `number` | ✅ | Heikin-Ashi 最高 | `692.75` |
| `hL` | `number` | ✅ | Heikin-Ashi 最低 | `692.61` |
| `hC` | `number` | ✅ | Heikin-Ashi 收盘 | `692.69` |
| `m5` | `number \| null` | ✅ | MA5（5 周期均线） | `692.68` |
| `m10` | `number \| null` | ✅ | MA10 | `692.62` |
| `m20` | `number \| null` | ✅ | MA20 | `692.55` |
| `m30` | `number \| null` | ✅ | MA30 | `692.40` |
| `m50` | `number \| null` | ✅ | MA50 | `692.03` |
| `m60` | `number \| null` | ✅ | MA60 | `691.95` |
| `m120` | `number \| null` | ✅ | MA120 | `691.50` |
| `m200` | `number \| null` | ✅ | MA200 | `692.08` |
| `m250` | `number \| null` | ✅ | MA250 | `691.85` |

> ¹ **`vw` 语义待确认**：当前推测为累积 VWAP（从开盘到当前 Bar 的成交量加权均价），而非单根 Bar 的 VWAP。待后续对照数据源确认后更新本行。
>
> **注意**：`ts` 在所有文件类型中均为必填字段。现有 `teaching_segments.json` 中缺失 `ts`，需在下次数据重新生成时补回。

### 3.2 精度规则

| 字段类别 | 精度要求 |
|---|---|
| 价格（`O/H/L/C/hO/hH/hL/hC/m5/m10/m20/m30/m50/m60/m120/m200/m250/vw`） | 保留源数据精度，不做额外截断。通常 2~4 位小数 |
| 成交量（`V`） | 整数，不保留小数 |

### 3.3 Bar 对象示例

```json
{
  "ts": "2026-01-07T11:05:00-05:00",
  "t": "11:05",
  "O": 692.72,
  "H": 692.75,
  "L": 692.61,
  "C": 692.66,
  "V": 118274,
  "vw": 692.08,
  "hO": 692.71,
  "hH": 692.75,
  "hL": 692.61,
  "hC": 692.69,
  "m5":   692.68,
  "m10":  692.62,
  "m20":  692.55,
  "m30":  692.40,
  "m50":  692.03,
  "m60":  691.95,
  "m120": 691.50,
  "m200": 692.08,
  "m250": 691.85
}
```

---

## 4. 文件结构定义

### 4.1 full-day 文件

整日数据，引擎可直接加载渲染。**按交易日期命名存档**。

**命名规则**：`SPY_YYYY-MM-DD.json`（如 `SPY_2026-04-13.json`）

```jsonc
{
  "meta": {
    "title": "SPY 2026-04-13 Full Day",   // 人类可读标题
    "ticker": "SPY",                       // 标的代码
    "date": "2026-04-13",                  // 交易日期 YYYY-MM-DD
    "source": "SPY_1min_2026-04-13.csv",   // 数据来源文件名
    "generated_at": "2026-04-14T15:49:45", // 生成时间 ISO 8601
    "counts": {
      "bars_1m": 390,                      // 1m Bar 总数
      "bars_5m": 78                        // 5m Bar 总数
    }
  },
  "bars_1m": [ /* Bar 对象数组 */ ],
  "bars_5m": [ /* Bar 对象数组 */ ]
}
```

### 4.2 seed 文件

单个教学片段的完整数据，包含引擎初始化参数。

```jsonc
{
  "meta": {
    "title": "完美单边多头阵型_Support_MA10",
    "ticker": "SPY",
    "date": "2026-01-07",
    "source": "teaching_segments.seed_01",  // 来源片段 ID
    "initial_timeframe": "1m",             // 引擎启动默认时间框架
    "initial_index_1m": 30,                // 1m 图表初始可见起点索引
    "initial_index_5m": 25,                // 5m 图表初始可见起点索引
    "generated_at": "2026-04-14T15:49:44"
  },
  "bars_1m": [ /* Bar 对象数组，含 ts */ ],
  "bars_5m": [ /* Bar 对象数组，含 ts */ ]
}
```

**seed 特有字段：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `initial_timeframe` | `"1m" \| "5m"` | 引擎启动时的默认时间框架 |
| `initial_index_1m` | `integer` | 1m 图表的初始可见范围起点索引 |
| `initial_index_5m` | `integer` | 5m 图表的初始可见范围起点索引 |

### 4.3 teaching-segments 文件

所有教学片段的集合，是教学系统的**单一数据源**。

```jsonc
{
  "meta": {
    "generated_at": "2026-04-14T11:19:35",
    "version": "4.0",                     // 数据格式版本
    "total_segments": 15                   // 片段总数
  },
  "categories": [ /* Category 对象数组 */ ],
  "segments": [ /* Segment 对象数组 */ ]
}
```

---

## 5. 教学片段子系统

### 5.1 Category 对象

```json
{
  "id": "support_ma10",
  "name": "Support MA10",
  "desc": "价格回调触及MA10后反弹"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | `string` | 唯一标识符，`snake_case` |
| `name` | `string` | 显示名称 |
| `desc` | `string` | 一句话描述 |

**现有 category 枚举值：**

| id | 含义 |
|---|---|
| `reject_ma10` | 价格反弹触及 MA10 后被压回 |
| `support_ma10` | 价格回调触及 MA10 后反弹 |
| `signal_b` | 价格同时跌破 MA10 和 MA50 |
| `trend_accumulation` | 多空转换（首次反转不会一次成功） |
| `ma_tangle` | 均线缠绕 |
| `kline_quality` | K 线质量（形态判断趋势强弱） |
| `barrier_test` | 关卡测试（MA50/MA200/VWAP） |
| `violent_reversal` | 暴力反转（深 V） |
| `opening_gap` | 开盘跳空 |
| `bear_attack` | 空头总攻（均线扇形发散） |

### 5.2 Segment 对象

```json
{
  "id": "seed_01",
  "title": "完美单边多头阵型_Support_MA10",
  "category": "support_ma10",
  "date": "2026-01-07",
  "source_interval": "1m",
  "is_seed": true,
  "chapter": "03",
  "scenario": "bullish",
  "variant_label": "单边顺延型",
  "teaching_focus": "标准 Support MA10，重点看多头单边和确认K。",
  "background_note": "",
  "preheat_count": 30,

  "regime_5m": { },
  "regime_15m": { },
  "derived": { },

  "bars_1m": [],
  "bars_5m": [],
  "annotations_1m": [],
  "annotations_5m": []
}
```

**Segment 字段详解：**

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | `string` | 唯一标识，格式 `seed_NN` 或未来的 `seg_NNNN` |
| `title` | `string` | 片段标题 |
| `category` | `string` | 对应 `categories[].id` |
| `date` | `string` | 原始交易日期 `YYYY-MM-DD` |
| `source_interval` | `"1m" \| "5m"` | 信号所在的时间框架 |
| `is_seed` | `boolean` | 是否为种子数据（手工标注的教学案例） |
| `chapter` | `string` | 对应教材章节号（两位字符串如 `"03"`） |
| `scenario` | `"bullish" \| "bearish"` | 多空方向 |
| `variant_label` | `string` | 变体标签（如 "标准瀑布型"） |
| `teaching_focus` | `string` | 教学重点说明 |
| `background_note` | `string` | 背景备注（可为空字符串） |
| `preheat_count` | `integer` | 预热 Bar 数量（回放起点前的可见 Bar 数） |

### 5.3 Regime 对象（市场状态描述）

每个 Segment 包含 `regime_5m` 和 `regime_15m` 两个 Regime：

```json
{
  "trend": "bullish",
  "ma_alignment": "bull_排列",
  "ma_spread": 0.1178,
  "nearest_barrier": "VWAP",
  "barrier_distance_pct": 0.2,
  "vwap_side": "above",
  "candle_quality": "strong"
}
```

| 字段 | 类型 | 可选值 | 说明 |
|---|---|---|---|
| `trend` | `string` | `"bullish" \| "bearish" \| "neutral"` | 趋势方向 |
| `ma_alignment` | `string` | `"bull_排列" \| "bear_排列" \| "tangled"` | 均线排列状态 |
| `ma_spread` | `number` | — | MA10-MA50 间距百分比 |
| `nearest_barrier` | `string` | `"VWAP" \| "MA50" \| "MA200"` | 最近支撑/阻力位 |
| `barrier_distance_pct` | `number` | — | 距最近关卡的百分比 |
| `vwap_side` | `string` | `"above" \| "below"` | 价格在 VWAP 上方/下方 |
| `candle_quality` | `string` | `"strong" \| "mixed" \| "weak"` | K 线质量评级 |

### 5.4 Derived 对象（计算衍生数据）

```json
{
  "viewport_1m": {
    "price_min": 691.84,
    "price_max": 694.04,
    "volume_max": 344541
  },
  "viewport_5m": {
    "price_min": 687.64,
    "price_max": 694.2,
    "volume_max": 2083871
  },
  "rule_events": [],
  "checkpoints": [],
  "signal_bar_index": 31,
  "stop_price": 692.22
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `viewport_1m` | `Viewport` | 1m 图表的价格/量能边界（渲染视口用） |
| `viewport_5m` | `Viewport` | 5m 图表的价格/量能边界 |
| `rule_events` | `RuleEvent[]` | 规则触发事件列表 |
| `checkpoints` | `Checkpoint[]` | 交易决策检查点 |
| `signal_bar_index` | `integer` | 信号 K 在 bars 数组中的索引 |
| `stop_price` | `number` | 止损价格 |

#### 5.4.1 Viewport 对象

```json
{
  "price_min": 691.84,
  "price_max": 694.04,
  "volume_max": 344541
}
```

#### 5.4.2 RuleEvent 对象

```json
{
  "type": "support_ma10",
  "timeframe": "1m",
  "bar_index": 31,
  "passed": true,
  "reason": "HA 下影线与 MA10 距离 0.01%"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `type` | `string` | 规则类型（与 category id 对应或更细粒度） |
| `timeframe` | `"1m" \| "5m"` | 触发所在时间框架 |
| `bar_index` | `integer` | 触发的 Bar 索引 |
| `passed` | `boolean` | 是否通过 |
| `reason` | `string` | 人类可读原因 |

#### 5.4.3 Checkpoint 对象

```json
{
  "key": "trend_ok",
  "label": "5min 趋势确认",
  "passed": true,
  "bar_index": 0,
  "reason": "5m 趋势: bullish",
  "metrics": {
    "stop_price": 692.22
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `key` | `string` | ✅ | 机器可读标识 |
| `label` | `string` | ✅ | UI 显示标签 |
| `passed` | `boolean` | ✅ | 是否通过 |
| `bar_index` | `integer \| null` | ✅ | 关联的 Bar 索引（无关联则 `null`） |
| `reason` | `string` | ✅ | 结论说明 |
| `metrics` | `object \| undefined` | ❌ | 附加指标（按需存在） |

**标准 Checkpoint key 枚举：**

| key | 含义 |
|---|---|
| `trend_ok` | 5min 趋势确认 |
| `ma_alignment_ok` | 均线排列方向 |
| `touch_ma10` | K 线触及 MA10 |
| `body_not_cross` | 实体未穿越 |
| `confirm_bar` | 确认 K 延续方向 |
| `stop_defined` | 止损位明确 |
| `reward_ok` | 目标空间足够 |
| `forbidden_absent` | 不在禁止条件内 |
| `vwap_intercept` | VWAP 拦截确认（Signal B 专用） |

### 5.5 Annotation 对象（标注系统）

```json
{
  "bar_index": 31,
  "type": "signal",
  "title": "Support MA10!",
  "body": "HA 下影线触及 MA10（距离 0.01%），实体仍稳在 MA10 上方",
  "anchor_side": "bottom",
  "auto_pause": true,
  "style": "green"
}
```

| 字段 | 类型 | 可选值 | 说明 |
|---|---|---|---|
| `bar_index` | `integer` | — | 标注锚定的 Bar 索引 |
| `type` | `string` | `"info" \| "signal"` | 标注类型 |
| `title` | `string` | — | 标注标题 |
| `body` | `string` | — | 标注正文（可为空字符串） |
| `anchor_side` | `string` | `"top" \| "bottom"` | 标注相对于 K 线的位置 |
| `auto_pause` | `boolean` | — | 回放到此处是否自动暂停 |
| `style` | `string` | `"blue" \| "green" \| "red"` | 标注颜色主题 |

**Annotation 约定：**

- 每个 Segment 至少包含 3 个 1m 标注：**回放开始**、**信号触发**、**回放结束**
- 回放结束标注的 `auto_pause` 固定为 `false`
- `style` 语义：`blue` = 信息提示，`green` = 多头信号，`red` = 空头信号
- 5m 标注通常只有 1 个，用于提示切换时间框架

---

## 6. 通用约定

### 6.1 索引规则

所有 `bar_index`、`signal_bar_index`、`initial_index_*` 均为 **0-indexed**，对应所在数组的下标。

### 6.2 文件命名规范

| 场景 | 命名模式 | 示例 |
|---|---|---|
| 整日数据（按日存档） | `SPY_YYYY-MM-DD.json` | `SPY_2026-04-13.json` |
| 引擎用种子数据 | `kline-engine-v2-seed.json` | — |
| 教学片段集合 | `teaching_segments.json` | — |

> **历史兼容**：旧文件 `kline-engine-v2-full-day.json` 仍可保留，但新生成的整日数据一律使用 `SPY_YYYY-MM-DD.json` 命名。

### 6.3 日常数据归档流程

```
收盘后操作:
1. 下载 SPY 1min 数据 → raw/daily/SPY_1min_YYYY-MM-DD.csv
2. 聚合 5min           → python aggregate_5min.py raw/daily/SPY_1min_YYYY-MM-DD.csv
3. 生成 processed JSON → processed/SPY_YYYY-MM-DD.json
                         (包含 bars_1m + bars_5m，所有 Bar 含 ts)
```

### 6.4 版本演进规则

1. **当前版本**：`teaching_segments.json` 的 `meta.version` 标识
2. **新增字段**：追加即可，解析器应用 optional chaining 或 fallback
3. **废弃字段**：先在本文档标注 `[DEPRECATED]`，保留一个版本后移除
4. **破坏性变更**：`meta.version` 主版本号 +1，CHANGELOG 记录

---

## 7. 解析器实现指南

```javascript
// 最小安全解析示例
function parseBar(bar) {
  return {
    time:   bar.t,
    open:   bar.O,
    high:   bar.H,
    low:    bar.L,
    close:  bar.C,
    volume: bar.V,
    vwap:   bar.vw,
    ha:     { o: bar.hO, h: bar.hH, l: bar.hL, c: bar.hC },
    ma10:   bar.m10 ?? null,   // 处理 null
    ma50:   bar.m50 ?? null,
    ma200:  bar.m200 ?? null,
    timestamp: bar.ts,
  };
}
```

**关键注意事项：**

- `m5/m10/m20/m30/m50/m60/m120/m200/m250` 在前 N 根 Bar 为 `null`（数据点不足以计算均线，window 越大 null 段越长）
- `V` 始终为整数，但 JSON 规范不区分 int/float，解析时建议 `Math.round()`
- `vw` 推测为**累积 VWAP**（从开盘到当前 Bar），待确认（见 §3.1 脚注¹）
- `ts` 为所有文件类型的必填字段，不再有条件省略

---

## 8. 快速参考卡

```
文件层级:

full-day / seed:
  ├── meta                    # 元信息
  ├── bars_1m[]               # 1分钟 Bar 数组 (含 ts)
  └── bars_5m[]               # 5分钟 Bar 数组 (含 ts)

teaching_segments:
  ├── meta                    # 元信息 + version
  ├── categories[]            # 策略分类定义
  └── segments[]              # 教学片段数组
       ├── 基础字段            # id, title, category, date...
       ├── regime_5m / 15m    # 市场状态快照
       ├── derived            # 计算衍生 (viewport, checkpoints...)
       ├── bars_1m[]          # 1分钟 Bar 数组 (含 ts)
       ├── bars_5m[]          # 5分钟 Bar 数组 (含 ts)
       ├── annotations_1m[]   # 1分钟标注
       └── annotations_5m[]   # 5分钟标注
```

---

## CHANGELOG

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.1 | 2026-04-15 | `ts` 改为全文件类型必填；full-day 改为按日期命名 `SPY_YYYY-MM-DD.json`；新增日常归档流程；`vw` 语义标注待确认 |
| v1.0 | 2026-04-15 | 初始版本，从现有 3 个 JSON 文件逆向提炼 |
