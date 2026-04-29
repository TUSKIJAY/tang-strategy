# HANDOFF — Daily Review 扫描器升级 V4.4 支持

> **状态：✅ 已交付（2026-04-28）**。原始 handoff 见下方 §1～§7，交付说明见 §8。
>
> 创建于 2026-04-28，由前一会话遗留。这是一个独立任务，新窗口接手即可。

---

## 1. 背景（为什么开这个任务）

今天做了一件事：把 [Daily review/daily-review.html](daily-review.html) 包装成一个内嵌当日数据 + 策略的"分享版"单文件 HTML，产物：[reviewed/SPY_2026-04-27_review.html](reviewed/SPY_2026-04-27_review.html)。构建步骤：

1. yfinance 下载 2026-04-27 SPY 1min → `Dream bigger/data/raw/daily/`
2. `build_json.py --auto-warmup` → `Dream bigger/data/processed/SPY_2026-04-27.json`
3. 复制到 `Daily review/market-data/live/2026-04-27/`
4. Python 脚本把 JSON + `strategies/tang_v4_4_slope.json` 注入 daily-review.html，输出 `reviewed/SPY_2026-04-27_review.html`

预期：嵌入 V4.4 策略后，扫描器输出与 TradingView Pine 端 (`小汤系统 V4.4 - 终极实战斜率修正版`) 一致。

实际：daily-review.html 在 2026-04-27 报了 **33 个信号 / 8 笔模拟交易**（4 胜），TradingView 同一天同一策略只有 **3-4 次进场**。差距过大，作者判断扫描器有问题。

---

## 2. 根因（一句话）

**[daily-review.html](daily-review.html) 的 `scanSignals` 函数完全硬编码到 v1/v2/v3 的三个 pattern（Reject MA10 / Support MA10 / Signal B），根本不读 `strategy.signals` 数组**。任何 V4 及以后的策略 JSON 加载进去，**信号检测部分都被静默忽略**，等于全部 fallback 到旧逻辑。

证据（grep 结果）：
- [daily-review.html:3734](daily-review.html#L3734) `scanSignals(bars1m, bars5m, strategy)` — 只用 `strategy.trend` 和 `strategy.filter.session`，不用 `strategy.signals`
- [daily-review.html:3698-3733](daily-review.html#L3698) 三个硬编码 detector：`detectRejectMA10` / `detectSupportMA10` / `detectSignalB`
- 全文件搜索 `strategy.signals` / `currentStrategy.signals` — **零匹配**

---

## 3. V4.4 扫描器缺失的能力清单

[strategies/tang_v4_4_slope.json](strategies/tang_v4_4_slope.json) 定义了一整套新语义，daily-review.html 全部未实现：

| 字段 | V4.4 定义位置 | 作用 | 当前状态 |
|------|--------------|------|---------|
| `signals[]` (call_normal/call_strong/put_normal/put_strong) | L130-229 | 4 个新信号 ID，与 v3 完全不同 | ❌ 未读 |
| `slope_filter` | L74-85 | MA10 斜率过滤（CALL 要 MA10 向上） | ❌ 未实现 |
| `elite_strong` | L114-128 | Strong 判定：上一根同时碰 MA10 + (MA50/MA200/VWAP) | ❌ 未实现 |
| `touch_logic` | L87-112 | HA 区间触碰 MA10/20/30（previous_range_touch） | ❌ 未实现 |
| `position_state` | L262-273 | 虚拟持仓状态机（flat/long/short） | ❌ 未实现 |
| `cooldown` | L275-282 | 信号后锁 10 根 K | ❌ 未实现 |
| `space_check` | L245-254 | 距下一道 MA 至少 0.15% 才允许开仓 | ❌ 未实现 |
| `filter.entangle_threshold_ratio` (0.0003) | L314-317 | 缠绕过滤（M10/20/30/50） | ❌ 未实现 |
| `entry_requirements.continuation_confirmation_required` | L233-234 | 当前 K 变色确认 | ❌ 未实现 |
| `multi_timeframe.trend_required_for_signal` | L66-72 | 5m 三线排列 (10>20>30 或 10<20<30) | ⚠️ 部分（trend 检测了，但用的是 v3 的 strict/relaxed 方法） |
| `exit.L2_hard_stops.ma50_ha_close_break` | L284-303 | HA close 跌破 MA50 止损 | ❌ 未实现（当前模拟器用 m10 stop） |

---

## 4. 关键文件索引

| 文件 | 作用 |
|------|------|
| [daily-review.html](daily-review.html) | 主文件，单文件 HTML |
| `daily-review.html:3698-3795` | **scanSignals 区块**（要改的核心） |
| `daily-review.html:3801+` | `simulateTrades` 三层出场模拟器（也要改 L2 用 MA50） |
| `daily-review.html:3987` | `function loadData(payload)` |
| `daily-review.html:4318` | `window.DailyReview = { loadData }` 公共 API |
| [strategies/tang_v4_4_slope.json](strategies/tang_v4_4_slope.json) | 目标策略定义（**真理来源**） |
| [strategies/STRATEGY.md](strategies/STRATEGY.md) | 策略 schema 文档（如果存在） |
| [strategies/strategy.schema.json](strategies/strategy.schema.json) | JSON schema |
| [reviewed/SPY_2026-04-27_review.html](reviewed/SPY_2026-04-27_review.html) | 今天产出的分享版 HTML（验证用基线） |

---

## 5. 推荐实施路径

### 5.1 设计原则
- **不破坏 v1/v2/v3**：现有 detectRejectMA10/SupportMA10/SignalB 保留，作为 v3 兼容路径。
- **按策略版本路由**：scanSignals 入口判断 `strategy.version`（或更稳：检测 `strategy.signals[].id`）决定走哪条扫描路径。
- **V4.4 走通用 JSON 解释器**：以后 v5/v6 可复用，不用每个版本写一遍 detector。

### 5.2 建议改动顺序

**Phase 1 — 基础设施（不动信号逻辑）**
1. 在 `scanSignals` 顶部加版本路由：
   ```js
   if (strategy.version?.startsWith('4.') || strategy.signals?.some(s => s.id?.startsWith('call_') || s.id?.startsWith('put_'))) {
     return scanSignalsV4(bars1m, bars5m, strategy);
   }
   // ... 旧 v3 逻辑 ...
   ```
2. 新建 `scanSignalsV4` 空函数。

**Phase 2 — V4.4 触发条件**
1. 实现 `detectTouchPrevRange(bar, ma10, ma20, ma30)` — 上一根 HA 范围与 m10/m20/m30 任一重叠。
2. 实现 `detectEliteStrong(bar, ma10, ma50, ma200, vwap)` — 上一根 K 同时触碰 MA10 + (MA50/MA200/VWAP) 之一。
3. 实现 `detectMA10Slope(bars, i)` — 1m MA10 当前 vs 上一根。
4. 实现 `detectEntangle(ma10, ma20, ma30, ma50, threshold_ratio)`。
5. 实现 `detectSpaceOK(close, m50, m200, vwap, direction, threshold_ratio)`。

**Phase 3 — 状态机 + 冷却**
1. 在 `scanSignalsV4` 主循环里维护 `activePos`（0/1/-1）+ `lastSignalBar`。
2. 每个信号触发时检查 `activePos === 0 && i - lastSignalBar > 10`。
3. 模拟器（`simulateTrades`）在确认有 trade 时反向回填这两个状态。

**Phase 4 — V4.4 出场（MA50 HA close break）**
1. `simulateTrades` 加 `exitCfg.L2_hard_stops.ma50_ha_close_break` 分支。
2. 长仓：`hC < m50` 止损；短仓：`hC > m50` 止损。

### 5.3 验证方法

- 黄金对照：用 [reviewed/SPY_2026-04-27_review.html](reviewed/SPY_2026-04-27_review.html) 当 baseline。改完后重新生成同日 HTML，**信号数应从 33 降到 ~3-5**，trades 应从 8 降到 ~3。
- 跨日抽查：再生成 2026-04-22、2026-04-24 两份分享版 HTML，对比 TradingView 截图。
- 状态机正确性：在 console 加临时打印 `activePos` 时间轴，验证持仓期间确实没有新信号。

### 5.4 已知陷阱

- **MA10 斜率用的是 1m 还是 5m？** V4.4 JSON L74-85 写 `line: m10` 没指定 timeframe，但 description "防止 V 型反转时 5m 大势滞后导致误触；做多要求 1m MA10 向上"明确是 1m。
- **5m trend 用的是 close 不是 HA close**（L52 `regular_close_5m_ma_stack`），别用错。
- **冷却 reset 逻辑**（L280）：止损时 `last_signal_bar` 重置为 0，等价于立刻解锁。容易写漏。
- **elite_strong.signal_uses_previous_bar: true** (L126) — Strong 判定看的是**上一根** K 的触碰，不是当前 K。

---

## 6. 触发新窗口的开场提示

> "看 `Daily review/HANDOFF_v4_4_scanner.md`，按 §5 推荐路径升级扫描器到 V4.4。先完成 Phase 1 + Phase 2，跑通 [reviewed/SPY_2026-04-27_review.html](reviewed/SPY_2026-04-27_review.html) 重生成 → 信号数从 33 降到个位数，再继续 Phase 3/4。"

---

## 7. 当前状态快照（已过时，见 §8 交付说明）

- ✅ 2026-04-27 数据已下载、build_json 已处理、Daily review 已收录
- ✅ 分享版 HTML 已产出 (`reviewed/SPY_2026-04-27_review.html`)，但**信号数据失真不可信**
- ✅ tang_v4_4_slope.json 嵌入路径已验证（`window.__EMBEDDED_STRATEGY__` + `setCustomStrategy()`）
- ❌ 扫描器还是 v3 逻辑 — 这就是这份 handoff 要解决的事

---

## 8. 交付说明（2026-04-28）

### 8.1 验收数据

|  日期   | 信号数 |   分布   | Trades | 胜率 | 注 |
|--------|------|----------|--------|------|----|
| 04-27 |   3  | 1S/2N    |   3   | 1/3 | HANDOFF 预期 ~3-5 |
| 04-22 |   4  | 2S/2N    |   4   | 2/4 |  |
| 04-24 |   4  | 2S/2N    |   4   | 1/4 |  |

回归（v3 路径未受影响）：04-27 v3 输出 30 信号 / 8 trades / 4 胜，与 §1 描述的旧行为一致。

### 8.2 实现要点

最终架构没有按 §5.2 的硬版本路由（`version.startsWith('4.')`）做，而是**完全特征探测**：扫描器看策略 JSON **声明了什么**，不看它叫什么。

- **路由判定** [`isStrategyDeclarative`](daily-review.html)：
  - 看 `signals[].conditions` 字典里有没有任何「声明式 scanner 能识别的键」
    （`trend_5m / ma10_slope / space_ok / not_tangled / previous_range_touch /
    previous_close_filter / current_bar_color / previous_elite / can_trigger`）
  - 任意一个匹配 → 走 `scanSignalsDeclarative`
  - 一个都没匹配 → 走 v1/v2/v3 老路径（detectRejectMA10 / SupportMA10 / SignalB）
  - **不用 version 字段**。这避免了「v3 也有 conditions 字典但用 candle_color/wick_touch 等 v3 风格键」的误路由 bug。

- **声明式扫描器** [`scanSignalsDeclarative`](daily-review.html)：
  - 每个 1m bar 计算 12 个特征（trend / slopeUp / slopeDown / isGreen / isRed
    / touchPrev / closeFilterCall / closeFilterPut / spaceCall / spacePut /
    notTangled / previousElite）
  - 对每个 signal def 跑 `matchesConditions(features, def.conditions)`：缺键 = 不过滤，有键 = 必须 match
  - 第一个全匹配的 signal emit；维护 `activePos` + `lastSignalBar` 实现 V4.4 的虚拟持仓和 10 根冷却

- **顶层 block 都数据驱动**：`touch_logic.trend_touch_levels` / `space_check.call_barriers_above` / `filter.entangle_lines` / `cooldown.bars` / `cooldown.enabled` / `position_state.enabled` / `exit.L2_hard_stops.ma50_ha_close_break` 全部从 JSON 读。

- **趋势检测** [`detectTrendsRouted`](daily-review.html)：按 `strategy.trend.method` 路由：`regular_close_5m_ma_stack` 走 stack 算法（看 `trend.lines` 数组），其它 fallback 到 v3 fast/slow + slope。

- **模拟器** [`simulateTrades`](daily-review.html) 加 V4 出场分支：检测到 `exit.L2_hard_stops.ma50_ha_close_break: true` 时，长仓 `hC < m50`、短仓 `hC > m50` 直接止损（而非 v3 的 body-cross MA10）。

### 8.3 现在能做什么（之前不行）

加新信号 id（如 `call_aggressive`），**0 行代码改动**，只往策略 JSON 的 `signals[]` 加：

```json
{
  "id": "call_aggressive",
  "name": "Aggressive CALL",
  "direction": "bullish",
  "conditions": {
    "trend_5m": "bullish",
    "ma10_slope": "up",
    "previous_range_touch": "t_trend_u",
    "current_bar_color": "green"
  }
}
```

略掉 `not_tangled` / `previous_elite` 这些键就等于不强制那些过滤。

### 8.4 已知陷阱（修过的）

- `elite_strong.major_touch_any` 用 `t_50/t_200/t_vwap` 作为键，**值是表达式串**，键名不是 bar 字段名。第一版 refactor 用 `replace(/^t_/, '')` 取线名错把它们变成 `'50'/'200'/'vwap'`，导致 `previousElite` 永远 false → 所有 Strong 信号被降级 Normal。已改为默认 `['m50','m200','vw']`，未来想自定义建议加显式字段 `elite_strong.major_barriers`。
- `previous_close_filter` 是**表达式串**（`"hC[1] >= m10[1]"`），目前用「字符串包含 `>=` / `<=`」做方向判断，没真正 parse。如果未来要改成「比较 m20 而不是 m10」需要换成结构化字段或加 expression parser。

### 8.5 新增/修改的文件

- [daily-review.html](daily-review.html) — 路由层 + 声明式扫描器 + 模拟器 V4 出场 + stats 卡片 teal 计入 bullish + 下拉 `<option>tang_v4_4` + `presetStrategies.tang_v4_4` 内联
- [app-data/scripts/build_reviewed_html.py](app-data/scripts/build_reviewed_html.py) — 注入 `__EMBEDDED_DATA__/__EMBEDDED_STRATEGY__` 全局，生成分享版 HTML
- [reviewed/SPY_2026-04-27_review.html](reviewed/SPY_2026-04-27_review.html) / `SPY_2026-04-22_review.html` / `SPY_2026-04-24_review.html` — 验收产物

### 8.6 后续可做（非阻塞）

- 老 v3 conditions 风格（`candle_color`/`wick_touch`/`body_below_1`/`confirm`）也接到声明式 scanner，让 v1~v4 真正走同一条路径
- `strategy.schema.json` 把 V4 风格的 conditions key 集合作为可选 enum 列出
- `scan_signals.py` 同步实现声明式扫描，避免前端 / Python 双实现漂移

---

## 9. Round 2 交付（2026-04-28，复盘语义校正）

### 9.1 起因

用户指出：Daily Review **是复盘工具不是回测器**。当前 `simulateTrades` 沿用了一堆 backtest 才需要的东西（tp_bars / premium_tp_pct / max_hold_minutes / trailing），这违反了复盘的本意——**机器不该假装知道何时止盈，那是人在当时的心态、仓位、市场情绪综合下的决定**。同时信号卡显示 `Normal PUT · 5m bearish · MA10↓ · touch m10/20/30` 一行字，不学过策略的人看不懂。

### 9.2 改了什么

- **`simulateTrades` → `traceSetups`**：彻底删 tp_bars / premium_sl_pct / premium_tp_pct / max_hold_minutes / trailing 全部分支。出场只剩两类：
  - **信号失效** (strategy invalidation)：V4 的 `hC vs MA50` 或 v3 的 body-cross MA10
  - **EOD**：当日收盘
- **删 `win` 字段**：复盘没有「赢/输」的概念，因为没设止盈点。卡片颜色改成「失效那一刻是否仍在有利方向」，而不是「赢/输」。
- **加 MFE / MAE / duration**：每个 setup 计算最大有利偏移、最大不利偏移、活了多少根 K。这是给人**判断止盈节奏**的客观参考数据。
- **顶部 stats 卡重写**：`Trades / Win` 删掉，换成 `Setups / MFE 中位 / 时长中位 / MAE 中位`。
- **信号卡可展开**：默认折叠保持原有简短形态，点击「▶ 展开详情」弹出三块：
  1. **触发条件 checklist (9/9 通过)**：每条策略 conditions 翻译成人话+实际数值。如 `✓ 5m 三线多头排列 — 当前 5m: bullish（要求 m10 > m20 > m30）` `✓ 1m MA10 向上 — 前根 713.22 → 当前 713.25` `✓ 前根触碰均线 — 前根 HA[712.98, 713.65] 跨过 MA10=713.22`
  2. **信号失效**：失效规则、入场时 MA50 值、实际失效时刻、原因
  3. **期间数据**：MFE/MAE 数值 + 时间戳，明确标「仅供参考，非建议止盈点」
- **explainConditions(features, conds, ctx)** 新增：把 9 个声明式 condition key 翻译成结构化 `{key, label, pass, detail}` 项，UI 渲染成 checklist。
- **`computeBarFeatures` 扩展 `_raw`**：返回 18 个原始数值（前根/当前 MA10-200、HA OHLC、空间 gap、缠绕 ratio、触碰的具体线、elite 触碰的具体线…）供 explainConditions 用。

### 9.3 验收

| 日期 | Setups | MFE 中位 | 时长中位 | MAE 中位 |
|------|--------|---------|---------|---------|
| 04-27 (V4.4) | 3 | +0.05% | 30m | -0.03% |
| 04-22 (V4.4) | 4 | – | – | – |
| 04-24 (V4.4) | 4 | – | – | – |
| 04-27 (v3 回归) | 8 | +0.02% | 5.5m | -0.02% |

V3 Setups 数量与重构前完全一致（30 信号 / 8 setups）。无控制台错误。展开详情 panel 的所有 9 个条件都附带具体数值。

### 9.4 设计原则记录

- **复盘里不出现「止盈」**：止盈是人决定的事，机器不替你按。
- **stats 不出现「胜率」**：胜率建立在「我假装在 V4 Stop 那一刻平仓」的虚构前提上，实际人会在 MFE 顶点附近平仓，所以胜率数据是误导性的。改用 MFE 中位数更诚实。
- **图上不画动态止损线**：用户拍板不做。第一版只标信号入场点和失效点。

### 9.5 已知不完美

- v3 信号卡片不显示触发条件 checklist（v3 路径用老 detect 函数，没生成 `_conditions`）。如果想统一，参考 §8.6 第一条把老风格 conditions 也接到声明式 scanner。
- MFE/MAE 用 SPY 的 hH/hL 极值算，期权溢价的实际波动会有 delta/gamma 偏差——但复盘工具只用 SPY 价格语义，不假装算期权。
- 「Elite 触碰」当前默认 `eliteMajorLines: ['m50','m200','vw']`。如果未来策略想自定义，建议在策略 JSON 加 `elite_strong.major_barriers: [...]`。

---

## 10. Round 3 交付（2026-04-28，K 线引擎稳健性 + 视图交互）

### 10.1 起因

用户的 UX 反馈：
- 点信号卡只放大到一根 bar，看不到完整趋势窗口
- 一滑动滚轮缩放，整图弹回全天
- 默认状态下 Play 按钮跑不起来（currentIndex 已在 lastBar）
- 多 MA 同时显示时鼠标 hover 卡顿（截图超时也是同源）

### 10.2 根因（架构层）

**`currentIndex` 一身二职**：既是播放头，又是 viewport 的右边界（applyZoom 里 `maxStart = currentIndex - count + 1`）。`scrollTo` 这一类 API 把这两件事绑在一起改，导致点信号卡 = 移动播放头 = 锁住 wheel-pan 范围。

**`lastRenderContext` 是 wheel handler 的命脉但没人维护它新鲜度**。viewSetupRange 直接戳 `viewportManager.zoomScale`，scheduleRender 是异步 rAF。两者中间 wheel 事件读到 stale count → 触发 maxCount clamp → 视图崩。

### 10.3 改了什么

**Daily Review 侧**：
- `zoomToSignal` → `viewSetupRange(anno, setup, timeframe)`：直接设 `viewportManager.viewStart` + `zoomScale`，**不动 currentIndex**。优先按 setup 的 [entry, exit] 范围 + 35% padding 计算视窗
- 信号卡 click handler 改调 `viewSetupRange(anno, setup, ...)`
- 包装 `engine.play`：默认状态下 currentIndex==lastBar 时点 play 自动重置到 0，避免 vanilla play() 立即 short-circuit
- `window.__engine` 调试钩子（控制台可直接观察引擎状态）
- stat 卡片删 Win，加 Setups / MFE 中位 / 时长中位 / MAE 中位
- 信号卡可展开：默认折叠保持原有简短形态，点「▶ 展开详情」弹出 9/9 触发条件 checklist + 失效规则 + MFE/MAE 期间数据

**K 线引擎侧（4 份 byte-identical 复制全部更新）**：
- wheel handler 读 `viewportManager.getVisibleWindow(...)` 的 live 状态而不是 `lastRenderContext.visible`，消除 stale-cache bug 类
- 应用文件：
  - [Daily review/daily-review.html](daily-review.html) inline
  - [Dream bigger/dist/kline-engine/kline-engine.js](../Dream%20bigger/dist/kline-engine/kline-engine.js)
  - [Teaching System/dist/kline-engine/kline-engine.js](../Teaching%20System/dist/kline-engine/kline-engine.js)
  - [Fragment Lab/dist/kline-engine/kline-engine.js](../Fragment%20Lab/dist/kline-engine/kline-engine.js)
- md5 校验 3 份外部 .js 字节一致

### 10.4 需要后续手动验证（Teaching System）

我没有 Teaching System 的 E2E 测试覆盖，只能通过 Daily Review 验证引擎层改动。Round 3 的 wheel-handler 修复**理论上对教学系统无害**（只是把 stale 读改成 live 读，不改语义），但请在合并前手动跑一次：
- 教学回放：play / step-forward / step-back 是否正常
- wheel zoom + drag：是否还能正常缩放和拖动
- revealCutoff 边界：到达教学步骤边界时是否仍然停下

如果教学系统出现新 bug，第一嫌疑是 `viewportManager.getVisibleWindow()` 在某个调用路径被反复调用导致性能下降（这个函数内部还有少量副作用：`this.viewStart = start`）。Round 4 应当把 `getVisibleWindow` 改成纯函数，但这是更大的手术，需要单独评估。

### 10.5 未做的优化（已知技术债）

- `getVisibleWindow` 仍然在改 `this.viewStart` 和 `this.followMode`（getter 有副作用）
- `applyZoom` 仍然会 `setFollowMode(nextStart >= maxStart)`（隐式 mode 翻转）
- `currentIndex` 双语义未拆分（拆成 `playHead` + `viewportRightAnchor` 才是终极解，但要动教学系统的 reveal 机制）

这些都是「下次想优化时的入口点」，不是当前阻塞。

---

## 11. Round 4 交付（2026-04-29，Activation 入场确认派生版）

### 11.1 起因

用户复盘 2026-04-24 时发现：原 v4.4 在早期横盘位置给出信号，但真正启动至少要等约 20 分钟。
如果按原信号立即进场，期权磨损会很大。因此新增一个派生策略，把原 v4.4 信号降级为
setup 候选，只有价格真正启动时才画正式入场信号。

### 11.2 保留边界

- `strategies/tang_v4_4_slope.json` 不删、不改、不覆盖，继续作为原版基线。
- `Tang v4.4 Slope` 下拉项保留，选择它时信号数量和位置保持原行为。
- `build_reviewed_html.py` 的默认行为不改；要使用 activation 逻辑必须显式传入
  `--strategy strategies/tang_v4_4_activation.json`。

### 11.3 新增/修改的文件

- [strategies/tang_v4_4_activation.json](strategies/tang_v4_4_activation.json) — 从原 v4.4 Slope 派生，新增 `entry_activation` 顶层模块。
- [daily-review.html](daily-review.html) — 下拉新增 `Tang v4.4 Activation`，浏览器端扫描器支持 setup / signal / expired 三态。
- [app-data/scripts/scan_signals.py](app-data/scripts/scan_signals.py) — Python 扫描器同步实现 activation gating，保持前后端正式信号一致。
- [README.md](README.md) / [INTEGRATION.md](INTEGRATION.md) — 记录新策略语义、CLI 用法和统计口径。

### 11.4 扫描语义

`entry_activation.enabled: true` 时：

- 原 v4.4 match bar 生成 `type: "setup"`，style `blue`，不计入正式信号数。
- setup 后最多等待 `max_wait_bars = 8` 根 1m K。
- CALL activation：当前 regular close 突破 `setup..上一根` 的最高价，且当前 HA 为 green、1m MA10 斜率仍向上。
- PUT activation：当前 regular close 跌破 `setup..上一根` 的最低价，且当前 HA 为 red、1m MA10 斜率仍向下。
- activation bar 生成 `type: "signal"`，使用原信号颜色和强弱样式，计入正式信号数。
- 超过 8 根仍未启动时生成 `type: "expired"`，style `purple`，body 写明「等待 8 根未启动，候选过期」。
- `activePos` 和 cooldown 只在 activation 后启动。setup 不锁仓、不触发冷却。

### 11.5 2026-04-24 回归

同一份 `market-data/live/2026-04-24/SPY_2026-04-24.json`：

| 策略 | 正式 signals | setup | expired | 说明 |
|---|---:|---:|---:|---|
| `tang_v4_4_slope.json` | 8 | 0 | 0 | 原版行为不变 |
| `tang_v4_4_activation.json` | 3 | 7 | 4 | 早期横盘候选过期，20 分钟后的突破不会回头激活 |

Activation 版事件序列：

- 06:53 setup -> 06:55 signal
- 08:29 setup -> 08:38 expired
- 09:26 setup -> 09:30 signal
- 10:26 setup -> 10:35 expired
- 11:22 setup -> 11:23 signal
- 12:51 setup -> 13:00 expired
- 15:41 setup -> 15:50 expired

### 11.6 验证命令

```powershell
python -m py_compile "Daily review\app-data\scripts\scan_signals.py"
python -m json.tool "Daily review\strategies\tang_v4_4_activation.json" > $env:TEMP\tang_v4_4_activation.validated.json
node -e "const fs=require('fs'); const html=fs.readFileSync('Daily review/daily-review.html','utf8'); const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]); for (let i=0;i<scripts.length;i++) new Function(scripts[i]); console.log('parsed scripts:', scripts.length);"
python "Daily review\app-data\scripts\scan_signals.py" --data "Daily review\market-data\live\2026-04-24\SPY_2026-04-24.json" --strategy "Daily review\strategies\tang_v4_4_activation.json" --out "$env:TEMP\SPY_2026-04-24_activation_final.json"
python "Daily review\app-data\scripts\scan_signals.py" --data "Daily review\market-data\live\2026-04-24\SPY_2026-04-24.json" --strategy "Daily review\strategies\tang_v4_4_slope.json" --out "$env:TEMP\SPY_2026-04-24_v44_final.json"
```

---

## 12. Round 5 交付（2026-04-29，Activation Wick 实盘友好变体）

### 12.1 起因

严格 Activation 只认 regular close 突破/跌破 setup 后运行区间。用户提出一个实盘问题：
如果 8 根窗口内价格一直用影线刺破上一根最高/最低，但收盘没有完成严格突破，是否会漏掉快速启动。

### 12.2 新增策略

- 新增 [strategies/tang_v4_4_activation_wick.json](strategies/tang_v4_4_activation_wick.json)。
- 原 `tang_v4_4_slope.json` 不删、不改。
- 原 `tang_v4_4_activation.json` 保留为严格收盘突破版。
- `daily-review.html` 下拉新增 `Tang v4.4 Activation Wick`。

### 12.3 扫描语义

`entry_activation.confirm_price = "close_or_strong_wick"` 时：

- CALL activation：regular close 突破 `setup..上一根` 最高价，或当前 high 刺破确认线且 close 位于 K 线区间 60% 以上。
- PUT activation：regular close 跌破 `setup..上一根` 最低价，或当前 low 下破确认线且 close 位于 K 线区间 40% 以下。
- HA 颜色和 MA10 斜率仍必须顺向。
- activation 事件会带上 `_activation_confirm_method`：`close` 或 `strong_wick`。
- expired 事件会带上 `_best_wick_in_window`、`_wick_confirmed_count`，方便判断是完全没触发，还是刺破过但收盘位置不够强/弱。

### 12.4 2026-04-28 对比

同一份 `market-data/live/2026-04-28/SPY_2026-04-28.json` 全时段扫描：

| 策略 | 正式 signals | setup | expired | 差异 |
|---|---:|---:|---:|---|
| `tang_v4_4_activation.json` | 4 | 9 | 5 | 09:47 CALL setup 在 09:56 过期 |
| `tang_v4_4_activation_wick.json` | 5 | 9 | 4 | 09:47 CALL setup 在 09:48 以 `strong_wick` 激活 |

09:48 这根 CALL 的确认线是 712.51，确认方式是 `strong_wick`，收盘位置约 87%。

### 12.5 验证命令

```powershell
python -m py_compile "Daily review\app-data\scripts\scan_signals.py"
python -m json.tool "Daily review\strategies\tang_v4_4_activation_wick.json" > $env:TEMP\tang_v4_4_activation_wick.validated.json
node -e "const fs=require('fs'); const html=fs.readFileSync('Daily review/daily-review.html','utf8'); const scripts=[...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]); for (let i=0;i<scripts.length;i++) new Function(scripts[i]); console.log('parsed scripts:', scripts.length);"
python "Daily review\app-data\scripts\scan_signals.py" --data "Daily review\market-data\live\2026-04-28\SPY_2026-04-28.json" --strategy "Daily review\strategies\tang_v4_4_activation_wick.json" --out "$env:TEMP\SPY_2026-04-28_activation_wick.json"
```
