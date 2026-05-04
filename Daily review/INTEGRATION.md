# Daily Review Agent Handoff

> 给后续 agent 的入口文档。先读这里，再读 `strategies/STRATEGY.md` 和 `strategies/strategy.schema.json`。
>
> 当前重点：把所有 Tang Strategy 策略沉淀成可校验的 JSON，并让 Daily Review 前端、Python 扫描器、回测脚本逐步围绕同一份策略配置工作。

## 1. 这是什么

`Daily review` 是一个本地静态复盘工具，不是通用交易平台。它服务于 Tang Strategy 的 SPY 日内复盘、信号标注、策略版本迭代和回测验证。

核心入口：

- `daily-review.html`：单文件静态前端。负责加载行情 JSON、展示 1m / 5m K 线、均线、VWAP、成交量、策略信号、交易区间和复盘 UI。
- `strategies/*.json`：策略机器配置。后续所有策略都应该转成这里的 JSON。
- `strategies/strategy.schema.json`：策略 JSON Schema。新增或修改策略时必须尽量通过它校验。
- `strategies/STRATEGY.md`：Tang Strategy 人工语义规范。改交易逻辑前必须先读。
- `app-data/scripts/scan_signals.py`：读取行情 JSON + 策略 JSON，输出带 annotations 的 reviewed JSON。
- `app-data/scripts/backtest.py`：SPY options scalping 回测脚本。

一句话目标：让“人工策略经验”变成“可版本化、可校验、可扫描、可复盘、可回测”的本地系统。

## 2. 现在要干什么

当前主线是策略 JSON 化和执行一致性：

1. 维护策略 JSON

   所有策略版本放在 `strategies/json/tang_*.json`。不要覆盖旧版本，新增版本用新文件名。每个文件要写清楚 `name`、`version`、`description`，并尽量加：

   ```json
   "$schema": "./strategy.schema.json"
   ```

2. 维护 JSON Schema

   `strategies/strategy.schema.json` 是策略结构的护栏。它现在已经兼容：

   - `tang_v1.json`
   - `tang_v2.json`
   - `tang_v3.json`
   - `tang_v3_3_1_flame.json`
   - `tang_v3_5_1_full.json`
   - `tang_v4_4_slope.json`
   - `tang_v4_4_activation.json`
   - `tang_v4_4_activation_wick.json`

   如果新增策略需要新模块，优先扩展 schema，而不是绕过 schema。

3. 统一执行层

   长期目标是让策略 JSON 成为唯一策略输入。前端可以展示和预览，但权威扫描结果应逐步收敛到 `scan_signals.py` 生成的 reviewed JSON。

4. 保持三层一致

   改策略时要同步检查：

   - 人工规则：`strategies/STRATEGY.md`
   - 机器配置：`strategies/json/tang_*.json`
   - 执行逻辑：`daily-review.html` / `app-data/scripts/scan_signals.py` / `app-data/scripts/backtest.py`

## 3. 怎么干

### 进入项目后的第一步

```powershell
cd "Daily review"
git status --short
Get-ChildItem strategies
```

注意：这个仓库里经常有用户或其他 agent 的未提交改动。不要回滚、不覆盖、不顺手清理和当前任务无关的文件。

### 打开前端

前端没有构建步骤，直接打开 HTML：

```powershell
Start-Process ".\daily-review.html"
```

页面主要使用三类输入：

- `market-data/live/YYYY-MM-DD/SPY_YYYY-MM-DD.json`
- `reviewed/*.json`
- `strategies/json/tang_*.json`

### 校验策略 JSON

当前用 `ajv-cli` 校验 draft 2020-12 schema：

```powershell
npx --yes ajv-cli@5 validate --spec=draft2020 `
  -s "strategies/strategy.schema.json" `
  -d "strategies/json/tang_v*.json"
```

期望所有 `tang_v*.json` 都 valid。若失败，先判断是策略文件真的缺字段，还是 schema 对已有合理结构收得太紧。

### 生成 reviewed JSON

```powershell
python "app-data/scripts/scan_signals.py" `
  --data "market-data/live/2026-04-22/SPY_2026-04-22.json" `
  --strategy "strategies/json/tang_v3_5_1_full.json" `
  --out "reviewed/SPY_2026-04-22.tang_v3_5_1_full.json"
```

输出文件必须能被 `daily-review.html` 加载，并保留 `annotations_1m` / `annotations_5m`。

### 跑回测

```powershell
python "app-data/scripts/backtest.py" 2026-04-14 --profile loose

python "app-data/scripts/backtest.py" 2026-04-13 2026-04-14 2026-04-15 `
  --batch --profile moderate --prem-sl 50 --prem-tp 80 --trail 35
```

`backtest.py` 默认从 `Daily review/data/` 找原始 CSV，也支持 `TANG_DATA_DIR`：

```powershell
$env:TANG_DATA_DIR = "D:\path\to\data"
```

## 4. 目录地图

```text
Daily review/
  daily-review.html                 # 静态前端入口，包含 UI、Kline Engine、浏览器端策略扫描/展示 glue
  INTEGRATION.md                    # 本文，agent handoff
  app-data/
    scripts/
      scan_signals.py               # 行情 JSON + 策略 JSON -> reviewed JSON
      backtest.py                   # SPY 期权策略回测
  market-data/
    live/YYYY-MM-DD/
      SPY_YYYY-MM-DD.json           # 日内行情 JSON
      tradytics_options_market_gex_*.json
  reviewed/
    *.json                          # 已扫描、带 annotations 的复盘数据
  strategies/
    STRATEGY.md                     # Tang Strategy 人工规范
    strategy.schema.json            # 策略 JSON Schema
    json/
      tang_v*.json                  # 策略配置版本
    pine/
      tang_*.pine                   # PineScript 实现或参考
```

## 5. 数据契约

行情 / reviewed JSON 顶层结构：

```json
{
  "meta": {
    "title": "SPY 2026-04-13 Full Day",
    "ticker": "SPY",
    "date": "2026-04-13",
    "strategy": {
      "name": "Tang v3.5.1 Full",
      "version": "3.5.1"
    }
  },
  "bars_1m": [],
  "bars_5m": [],
  "annotations_1m": [],
  "annotations_5m": []
}
```

bar 常用字段：

- 时间：`ts`, `t`
- 原始 OHLCV：`O`, `H`, `L`, `C`, `V`
- Heikin-Ashi：`hO`, `hH`, `hL`, `hC`
- 指标：`m5`, `m10`, `m20`, `m30`, `m50`, `m60`, `m120`, `m200`, `vw`

annotation 常用字段：

```json
{
  "bar_index": 123,
  "timeframe": "1m",
  "title": "Strong PUT",
  "body": "reason / detail",
  "type": "signal",
  "style": "red",
  "anchor_side": "top",
  "score": 2
}
```

前端会做宽松 normalize，但新脚本不要依赖隐式默认值。输出时尽量补齐字段。

## 6. 策略 JSON 约定

最小稳定骨架：

```json
{
  "$schema": "./strategy.schema.json",
  "name": "Tang vX",
  "version": "X.Y",
  "description": "这一版相对上一版改变了什么",
  "trend": {},
  "signals": [],
  "scoring": { "enabled": false },
  "exit": {},
  "filter": {},
  "hard_blocks": {}
}
```

策略 JSON 的设计原则：

- `description` 必须写人话，方便复盘时知道这一版为什么存在。
- `signals[].id` 保持稳定，展示层和 reviewed JSON 可能依赖它。
- 派生信号可以用 `extends + extra_conditions`，不一定要重复完整 `conditions`。
- 新增模块可以先作为普通 object 放入，但要补到 `strategy.schema.json` 的 `properties` 里。
- 不要把执行状态、当天交易情绪、临时备注写进策略 JSON。策略 JSON 只放可复用规则。

## 7. Tang Strategy 核心边界

不要把它改成普通指标交叉系统。当前策略精神是：

1. 5m 先定大方向。
2. 1m 等 MA10 / MA20 / MA30 附近的 HA 形态。
3. 顺势做 CALL / PUT，不猜顶底，不做反手。
4. 用 MA50 / MA200 / VWAP 判断前方空间和止盈压力。
5. 入场理由消失就出场。

版本差异很重要：

- v1/v2 偏早期：严格趋势、MA10 Reject / Support、基础评分或无评分。
- v3 系列加入多周期冲突、空间、成交量、分批止盈、期权上下文。
- v3.3.1 / v3.5.1 / v4.4 是从 PineScript/消息转换来的更完整配置。
- v4.4 Slope 加入 5m MA10/20/30 顺势过滤、1m MA10 斜率、持仓状态机、10 根 K 冷却、elite Strong 判定。
- v4.4 Activation 是 v4.4 Slope 的派生版：原 v4.4 命中只产生 `setup` 候选，只有 8 根 1m K 内收盘突破 setup 后运行区间，且 HA 颜色 / MA10 斜率仍顺向，才产生正式 `signal`。
- v4.4 Activation Wick 是 Activation 的实盘友好变体：仍使用同一个 setup 生命周期，但允许 `close_or_strong_wick`，即收盘突破/跌破，或影线刺破/下破确认线且收盘位置在顺向半边。

不要把某一版的规则硬套到所有版本。执行层应读取策略 JSON，而不是用文件名猜规则。

## 8. Kline Engine 注意点

`daily-review.html` 内嵌 Kline Engine v2，并额外加了 Daily Review 的交易复盘层。

需要保留的扩展：

- `engine._trades`
- `simulateTrades()`
- `drawTradeZones(ctx, rc)`
- 渲染顺序中交易区间和 annotation pin 的叠加

常用 API：

- `setCandleType('ha' | 'normal')` / `getCandleType()`
- `setRevealCutoff(input)` / `getRevealCutoff(timeframe?)`
- `setHighlightRanges(input)` / `getHighlightRanges()`
- `setTheme('dark' | 'light')` / `getTheme()`
- `engine.maVisibility` 控制 MA/VWAP 显隐

同步上游 Kline Engine 时不能简单覆盖 `daily-review.html`，要确认这些 Daily Review 扩展还在。

## 9. 优先级路线

建议新 agent 按这个顺序推进：

1. 策略 JSON/schema

   新策略先写 JSON，再跑 schema 校验，再用真实日数据扫描。

2. 扫描一致性

   优先让 `scan_signals.py` 覆盖更多策略字段，减少前端和 Python 双实现漂移。

3. reviewed 数据质量

   用 `reviewed/*.json` 固定样例检查信号数量、关键时间、图上 pin、统计卡片是否稳定。

4. 前端拆分

   `daily-review.html` 已经很大。后续可拆成 `src/kline-engine.js`、`src/signal-scanner.js`、`src/storage.js`、`src/app.js`、`src/styles.css`。拆分前先决定是否继续支持直接打开 HTML。

5. 回测贴合策略 JSON

   `backtest.py` 目前仍有大量内置逻辑。长期目标是让它读取策略 JSON 的 exit/filter/options，而不是维护另一套参数宇宙。

## 10. 验收清单

改完至少检查：

- `daily-review.html` 能直接打开，无控制台错误。
- 加载 `market-data/live/.../SPY_*.json` 能显示 1m / 5m K 线。
- 加载 `reviewed/*.json` 不丢 annotations。
- 上传或选择策略后，图上 pin、信号列表、顶部统计一致。
- HA / OHLC、Light / Dark、MA/VWAP 显隐可切换。
- 播放、步进、缩放、Follow、Overview 可用。
- `setRevealCutoff()` 和 `setHighlightRanges()` 仍可用于教学联动。
- `scan_signals.py` 能生成 reviewed JSON，且前端可加载。
- 策略文件通过 `strategy.schema.json` 校验。
- 如果改了回测，至少跑一个单日命令和一个 batch 命令。

## 11. 不要做

- 不要删除历史 `tang_v*.json`。它们是策略演化记录。
- 不要覆盖 reviewed 文件，除非输出文件名明确包含日期和策略版本。
- 不要只改前端扫描逻辑而忘记 `scan_signals.py`，也不要反过来。
- 不要把 Tang Strategy 简化成 MA 金叉死叉。
- 不要在 canvas render 里塞复杂业务计算。指标和信号应来自数据或扫描层。
- 不要碰和当前任务无关的 git 改动。

## 12. 快速定位

- 入口文档：`INTEGRATION.md`
- 页面入口：`daily-review.html`
- 策略文字规范：`strategies/STRATEGY.md`
- 策略 schema：`strategies/strategy.schema.json`
- 当前最完整配置之一：`strategies/json/tang_v3_5_1_full.json`
- 当前最新斜率版配置：`strategies/json/tang_v4_4_slope.json`
- 当前入场确认派生版配置：`strategies/json/tang_v4_4_activation.json`
- 当前入场确认实盘友好版配置：`strategies/json/tang_v4_4_activation_wick.json`
- 信号扫描：`app-data/scripts/scan_signals.py`
- 分享版 HTML 生成：`app-data/scripts/build_reviewed_html.py`
- 回测：`app-data/scripts/backtest.py`
- 示例 reviewed：`reviewed/kline-engine-v2-full-day.json`
- V4.4 扫描器交付说明：`HANDOFF_v4_4_scanner.md` §8

## 13. 浏览器端扫描器架构

`daily-review.html` 内置两条扫描路径，通过特征探测路由（**不绑 version 字段**）：

### 路由规则

`isStrategyDeclarative(strategy)` 检查：
- `strategy.signals[]` 必须存在且非空
- 至少有一个 signal 的 `conditions` 字典里出现以下键之一（"V4 风格键"集合）：
  ```
  trend_5m / ma10_slope / space_ok / not_tangled /
  previous_range_touch / previous_close_filter /
  current_bar_color / previous_elite / can_trigger
  ```

任何一条匹配 → 走声明式扫描器 `scanSignalsDeclarative`；否则 fallback 到老路径
`detectRejectMA10 / detectSupportMA10 / detectSignalB`。

> **为什么不看 version**：v3 的 `signals[].conditions` 也是字典，但用
> `candle_color / wick_touch / body_below_1 / body_above_2 / confirm /
> trend_required` 这套老风格键。如果只看「conditions 是不是 dict」，v3 会被
> 误路由到声明式 scanner，所有键走 default 分支 → 每根 K 都 emit。

### 声明式扫描器（V4 路径）

每根 1m bar 计算 12 个特征（trend / slopeUp / slopeDown / isGreen / isRed /
touchPrev / closeFilterCall / closeFilterPut / spaceCall / spacePut /
notTangled / previousElite），再对每个 signal def 跑
`matchesConditions(features, def.conditions)`：

| condition 键 | 特征对应 | 取值约定 |
|---|---|---|
| `trend_5m` | features.trend | `'bullish'` / `'bearish'` |
| `ma10_slope` | features.slopeUp / slopeDown | `'up'` / `'down'` |
| `space_ok` | features.spaceCall / spacePut | `'call'` / `'put'` |
| `not_tangled` | features.notTangled | `true` / `false` |
| `previous_range_touch` | features.touchPrev | truthy 即要求触碰 |
| `previous_close_filter` | features.closeFilterCall / Put | 表达式串，含 `>=` 视为 call，含 `<=` 视为 put |
| `current_bar_color` | features.isGreen / isRed | `'green'` / `'red'` |
| `previous_elite` | features.previousElite | `true` / `false` |
| `can_trigger` | (外部 gate) | 任意值都不 block；冷却/持仓在循环外检查 |

第一个全 match 的 signal emit；维护 `activePos` + `lastSignalBar`。出场（虚拟）：
若 `exit.L2_hard_stops.ma50_ha_close_break: true`，长仓 `hC < m50` / 短仓 `hC > m50` 即触发，重置 `lastSignalBar = -Infinity` 立即解锁冷却。

### Activation 派生策略

如果策略顶层声明 `entry_activation.enabled: true`，声明式扫描器进入 setup -> activation 模式。
没有这个字段，或 `enabled` 为 false 时，继续走原 v4.4 Slope 行为。

Activation 模式的语义：

- 原 v4.4 match bar 只 emit `type: "setup"`，style 为 `blue`，不计入正式信号数。
- 扫描器同一时间只维护一个 pending setup。setup 不启动 `activePos`，也不写入 cooldown。
- 在 `entry_activation.max_wait_bars`（默认 8）内，严格版要求 CALL 当前 regular close 突破 `setup..上一根` 的最高价，PUT 当前 regular close 跌破 `setup..上一根` 的最低价。
- 如果 `entry_activation.confirm_price = "close_or_strong_wick"`，则 CALL 还允许当前 high 刺破确认线且 close 位于 K 线区间上半部；PUT 还允许当前 low 下破确认线且 close 位于 K 线区间下半部。默认阈值是 `strong_wick.close_position_min = 0.6`，即 CALL 收在区间 60% 以上、PUT 收在区间 40% 以下。
- 如果 `require_same_direction_bar` 为 true，activation bar 还必须保持 CALL=HA green / PUT=HA red。
- 如果 `require_ma10_slope_still_aligned` 为 true，activation bar 还必须保持 CALL=MA10 slope up / PUT=MA10 slope down。
- activation bar emit `type: "signal"`，沿用原 signal 的方向、score、style，并从这一刻启动 `activePos` 和 cooldown。
- 超过等待窗口仍未 activation 时 emit `type: "expired"`，style 为 `purple`，不计入正式信号数。过期 setup 不能被 20 分钟后的突破回头激活。

统计口径：顶部信号数、多空分布和 `scan_signals.py` 的正式信号数量只统计
`type === "signal"`。`setup` / `expired` 只用于观察当时是否存在候选机会。

### 顶层 block 都数据驱动

| JSON 字段 | 用途 |
|---|---|
| `trend.method = "regular_close_5m_ma_stack"` | 启用 stack 趋势算法 |
| `trend.lines: ["m10","m20","m30"]` | stack 算法用哪几条线 |
| `touch_logic.trend_touch_levels` | previous_range_touch 检查哪几条线 |
| `space_check.call_barriers_above` / `put_barriers_below` | space_ok 检查的屏障线 |
| `space_check.min_distance_pct_of_price` | 空间阈值百分比（0.15 → 0.0015 ratio） |
| `filter.entangle_threshold_ratio` | 缠绕阈值 ratio（默认 0.0003） |
| `filter.entangle_lines` | 缠绕检查包含的线 |
| `cooldown.enabled` / `cooldown.bars` | 信号后锁多少根 K |
| `position_state.enabled` | 是否启用虚拟持仓互斥 |
| `entry_activation.enabled` / `max_wait_bars` | 是否启用 setup -> activation 入场确认，以及最多等待几根 1m K |
| `exit.L2_hard_stops.ma50_ha_close_break` | 是否启用 V4 出场（HA close vs MA50） |
| `elite_strong.major_barriers` | （建议新增字段）elite 判定的次级屏障线，默认 `["m50","m200","vw"]` |

### 加新信号

在 `signals[]` 里加 dict，复用上表 condition 键，**0 行代码改动**就能扫到。
未识别的 condition 键会触发一次 console.warn（每个键只 warn 一次/页面），但不会 block 信号。

### Setup tracer 与扫描器一致性

`traceSetups`（曾名 `simulateTrades`）和 `scanSignalsDeclarative` 的虚拟出场用同一条规则
（`hC vs m50` 或 v3 body-cross MA10），保证「scanner 状态机虚拟解锁」的时点和
「tracer 实际出场」的 bar 对齐，避免一个允许新信号、另一个还在持仓的 race。

### Wheel handler 读 live viewport（Round 3 修复，2026-04-28）

旧实现里 wheel handler 用 `lastRenderContext.visible.count` 计算 `nextCount = count * 1.12`。
当外部代码（如 Daily Review 的 `viewSetupRange`）直接修改 `viewportManager.zoomScale` 后，
`lastRenderContext` 是异步 rAF 才更新的，下一帧前的 wheel 事件读到 stale count。

实际后果：刚点完信号卡（视图 96 根）立即滚轮 → 用 stale 的 390 算 nextCount = 437 →
clamp 到 maxCount → 整张图弹回全天。

修复：wheel handler 改读 `viewportManager.getVisibleWindow(...)` 的 live 状态，
不再依赖 render 缓存。已应用到：
- [Daily review/daily-review.html](daily-review.html) inline 引擎
- [Dream bigger/dist/kline-engine/kline-engine.js](../Dream bigger/dist/kline-engine/kline-engine.js)
- [Teaching System/dist/kline-engine/kline-engine.js](../Teaching System/dist/kline-engine/kline-engine.js)
- [Fragment Lab/dist/kline-engine/kline-engine.js](../Fragment Lab/dist/kline-engine/kline-engine.js)

四份引擎文件 byte-identical。同步修改时务必：

```bash
cp "Dream bigger/dist/kline-engine/kline-engine.js" "Teaching System/dist/kline-engine/kline-engine.js"
cp "Dream bigger/dist/kline-engine/kline-engine.js" "Fragment Lab/dist/kline-engine/kline-engine.js"
md5sum [3 files]  # 验证一致
```

如果只在一处改动而忘了另外两处，运行时表现会不一致 — Daily Review 里测试通过、
Teaching System 实际是旧逻辑。

## 14. 复盘语义（不是回测）

**Daily Review 是复盘工具，不是回测器**。这个边界由代码强制：

| 能力 | 状态 | 原因 |
|---|---|---|
| 策略止损/失效检测 | ✅ 有 | 策略 JSON 声明的，机器替你看条件 |
| MFE / MAE / 时长 | ✅ 有 | 客观数据，给人判断止盈节奏的参考 |
| 止盈逻辑 | ❌ 不做 | 止盈是人决定的事，机器不替你按 |
| 胜率 | ❌ 不算 | 假设固定出场点 = 假装是回测 |
| 移动止损 / Trailing | ❌ 不做 | 同上 |
| Premium % SL/TP | ❌ 不做 | 期权语境下机器没法准确预估 |
| 时间止损 | ❌ 不做 | 任意拍脑门 |

`traceSetups` 输出的字段：

```js
{
  signal_index, entry_index, exit_index, direction,
  entry_price, exit_price, spy_move, spy_move_pct, bars_held,
  invalidation_type,       // 'invalidated' / 'eod'
  invalidation_reason,     // human label (e.g. "信号失效: hC 712.95 < MA50 712.85")
  invalidation_line,       // 'm50' / 'm10' / null
  invalidation_value,      // line value at invalidation bar
  mfe, mfe_pct, mfe_bar_offset,
  mae, mae_pct, mae_bar_offset,
}
```

**注意**：`spy_move` 在新模型里只是「失效那一刻是否仍在有利方向」的描述
（用于 UI 着色），**不代表赢亏**。

### 信号详情 panel

`scanSignalsDeclarative` 在 emit 每个 annotation 时，附 `_conditions` 数组和
`_invalidation` 对象：

- `_conditions: [{key, label, pass, detail}, ...]` — 9 个条件每条带具体数值
- `_invalidation: {line, rule, direction, initial_value, human}` — 失效规则 + 入场时的 MA50 值

UI 的 `buildSignalDetail()` 渲染成三块（触发条件 / 信号失效 / 期间数据）。
新增 condition key 时步骤是：
1. `computeBarFeatures` 算出对应 boolean
2. `matchesConditions` switch 加 case 做求值
3. `explainConditions` switch 加 case 生成「人话 label + 实际数值 detail」
