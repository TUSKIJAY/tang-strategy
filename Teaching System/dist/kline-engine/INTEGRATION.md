# K 线引擎 v2 — 对接说明文档（INTEGRATION）

> 更新日期：2026-04-22
> 目标读者：需要把 K 线引擎嵌入产品页（教程 / 每日复盘 / 回测平台 / 其他自建工具）的 agent 或开发者
> 配套文档（均在 `docs/planning/kline-engine-v2/`）：
> - `INTERNALS.md` — 内部实现地图（改引擎本身时看）
> - `OPTIMIZATION.md` — 已做的瘦身记录
> - `ACCEPTANCE.md` — 验收清单

本文档只回答**一个问题**：**如何把引擎接到你的页面里并驱动它**。

---

## 一、定位与约束

- **形态**：纯前端，单文件 HTML + Canvas 2D 渲染，零外部依赖。
- **位置**：`kline-engine-v2.html`（与本文档同目录）
- **渲染目标**：宿主页面里的任意 DOM 容器（`<div>` 即可）。
- **数据源**：由调用方通过 `loadData(json)` 注入，引擎自己不拉数据。
- **标准数据管道**：`data/build_json.py`（CSV → 引擎可消费 JSON，含 HA/MA/VWAP 预计算）。

> 如果你只是想看效果，直接浏览器打开 `kline-engine-v2.html` 即可。页面末尾的 `bootstrapDemo()` 会自动加载内置 fixture。

---

## 二、快速接入（3 步）

### Step 1：在宿主页面加载引擎脚本

推荐用单文件 HTML 嵌入法。引擎的 IIFE 会把 `KlineEngine` 挂到 `window`：

```html
<!-- 方案 A：作为独立页面嵌入（iframe） -->
<iframe src="path/to/kline-engine-v2.html"
        style="width:100%; height:600px; border:0;"></iframe>

<!-- 方案 B：抽出 <script> 内联到你自己的页面 -->
<!-- 复制 kline-engine-v2.html 内的 <script>...window.KlineEngine = KlineEngine;...</script> -->
<!-- 丢弃其中的 DEMO_FIXTURES、bootstrapDemo、runIntegrationTest 区块 -->
```

> 方案 A 最简单，但跨 frame 调用 API 需要 `postMessage`。若要直接用 JS API 驱动，推荐方案 B。

### Step 2：准备一个容器节点

```html
<div id="my-chart" style="width: 100%; min-height: 560px;"></div>
```

### Step 3：实例化并加载数据

```js
const engine = new KlineEngine({ container: document.getElementById('my-chart') });

fetch('/path/to/data.json')
  .then((res) => res.json())
  .then((json) => engine.loadData(json));
```

完事。工具栏、K 线、MA、成交量、十字线、键盘快捷键全都开箱即用。

---

## 三、数据格式（必读）

引擎接受的 JSON 必须满足以下结构。所有字段都经过 `DataManager._normalizeBar` 处理，缺失字段会被补 `null`，但**为了正确渲染 HA 和 MA 请尽量齐全**。

### 3.1 顶层结构

```jsonc
{
  "meta": {
    "title": "完美单边多头阵型_Support_MA10",   // 页面标题显示
    "ticker": "SPY",                            // 标的（可选）
    "date": "2026-01-07",                       // 日期 YYYY-MM-DD（用于构造 ts fallback）
    "source": "teaching_segments.seed_01",      // 数据来源标识（可选）
    "initial_timeframe": "1m",                  // 首次加载时的激活 tf（可选，缺省 1m）
    "initial_index_1m": 30,                     // 1m 的初始播放头位置（可选，缺省 0）
    "initial_index_5m": 25,                     // 5m 的初始播放头位置（可选）
    "generated_at": "2026-04-14T15:49:44Z"      // 生成时间戳（可选）
  },
  "bars_1m": [ /* Bar[] */ ],
  "bars_5m": [ /* Bar[] 可选，没有就不提供 */ ],
  "annotations_1m": [ /* Annotation[] 可选 */ ],
  "annotations_5m": [ /* Annotation[] 可选 */ ]
}
```

### 3.2 Bar 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `ts` | string (ISO 8601) | 推荐 | 带时区的时间戳，如 `2026-01-07T11:05:00-05:00`。若省略，引擎尝试用 `meta.date + t` 拼出。 |
| `t` | string | 推荐 | 显示用短时间 `HH:MM`。若省略，从 `ts` 截取。 |
| `O` `H` `L` `C` | number | **是** | 原始 OHLC（未做 HA 转换） |
| `V` | number | 否 | 成交量，缺省 0 |
| `vw` | number | 否 | VWAP |
| `hO` `hH` `hL` `hC` | number | **是** | Heikin-Ashi OHLC。引擎用 HA 画 K 线体，缺省时退回到原始 OHLC（视觉上就不是 HA 了） |
| `m5` `m10` `m20` `m30` `m50` `m60` `m120` `m200` | number \| null | 否 | SMA5 / 10 / 20 / 30 / 50 / 60 / 120 / 200。warmup 不足的 bar 填 `null`，引擎会自动跳过断点。任一字段缺失会让对应 MA 不绘制。 |

> **关键规则**：引擎**默认**用 `hO/hH/hL/hC` 绘制 K 线（Heikin-Ashi 模式）。用户可通过工具栏 `HA / OHLC` 按钮或 `setCandleType('normal')` 切到真实 OHLC 渲染 —— 两种模式共用同一份数据，只是读取字段不同。如果你只给原始 OHLC、没给 HA，HA 模式会透明回退到真实 OHLC（但那就不是 Heikin-Ashi 了）。

### 3.3 Annotation 字段（可选）

```jsonc
{
  "bar_index": 42,              // 挂在哪根 bar 上（绝对索引，从 0 起）
  "timeframe": "1m",            // 目前仅用于标识，引擎按挂入的数组分发
  "title": "Support MA10",      // 浮层标题（必填）
  "body": "MA10 首次测试...",    // 浮层正文（可选）
  "type": "info",               // 预留分类字段
  "style": "blue",              // red | green | blue | orange | purple
  "anchor_side": "top",         // top=挂在 High 上方 | bottom=挂在 Low 下方
  "score": "6/8"                // 清单分 "X/Y" 或 null，≥6 算高分，pin 会变大
}
```

### 3.4 数据生产建议

**首选**：用 `data/build_json.py`，它会完整生成 HA / MA / VWAP / warmup，产物直接丢给 `loadData()`。

```bash
# 每日数据
cd "data"
python build_json.py raw/daily/SPY_1min_YYYY-MM-DD.csv --auto-warmup

# 批量历史
python build_json.py raw/bulk/SPY_1min_<range>.csv --date 2026-01-07
```

**自制数据**：照 3.2 的 schema 构造即可。注意 MA 的 warmup（MA10 至少需要 10 根前置数据，MA200 需要 200 根）。缺数据就填 `null`，别填 0。

---

## 四、公共 API 参考

所有 API 都挂在 `KlineEngine` 实例上。按用途分组：

### 4.1 生命周期

| 方法 | 说明 |
|------|------|
| `new KlineEngine({ container })` | 构造。`container` 是任意 DOM 节点，引擎会清空其内容并注入结构。 |
| `destroy()` | 释放所有资源（timer / RAF / listener / DOM）。**跨页面切换或热替换前务必调用**，否则泄漏。 |

### 4.2 数据加载

| 方法 | 说明 |
|------|------|
| `loadData(json)` → `summary` | 加载新数据。返回 `{ meta, timeframes, counts }`。会自动 `pause()`、重置 viewport。 |

`summary` 结构：

```js
{
  meta: { /* 原样回传 */ },
  timeframes: ['1m', '5m'],           // 实际有数据的 tf
  counts: { bars_1m: 390, bars_5m: 78, annotations_1m: 12, annotations_5m: 3 }
}
```

### 4.3 时间框架

| 方法 | 说明 |
|------|------|
| `getTimeframe()` → `'1m' \| '5m'` | 当前活跃 tf |
| `setTimeframe(tf)` → `{ timeframe, index }` | 切换 tf。内部会做时间对齐（尽量保留 currentIndex 对应的时间点） |

### 4.4 播放控制

| 方法 | 说明 |
|------|------|
| `play()` | 从当前 index 开始播放 |
| `pause()` | 暂停（`loadData` / `setTimeframe` / `scrollTo` 会自动调用） |
| `togglePlayback()` | 播放 ↔ 暂停 |
| `stepForward()` | 前进一根 bar（播放中会被忽略） |
| `stepBack()` | 后退一根 bar |
| `setSpeed(speed)` | 仅接受 `0.5 / 1 / 2 / 4`，其他值会被回落到 `1` |
| `getSpeed()` → `number` | 当前速度 |
| `isPlaying()` → `boolean` | 播放状态 |

播放节奏：实际间隔 = `500ms / speed`（L1520）。新 bar 入场有 150ms 的缩放动画。

### 4.5 视窗与跳转

| 方法 | 说明 |
|------|------|
| `getCurrentIndex()` → `number` | 当前播放头 |
| `setCurrentIndex(idx, { follow = true })` | 设置播放头。`follow=true` 时视窗跟随到尾部；`false` 保持当前视窗位置 |
| `scrollTo(target)` | **跳转到指定 bar**。见下方详解 |

**`scrollTo()` 的两种用法**：

```js
// 简单：跳到当前 tf 的第 142 根 bar，居中显示
engine.scrollTo(142);

// 完整：可跨 tf、可高亮闪烁
engine.scrollTo({
  barIndex: 42,
  timeframe: '5m',    // 可选，默认当前 tf。如果目标 tf 没数据会被忽略
  highlight: true,    // 可选，默认 false。true 时目标 bar 会蓝色闪烁 1.2s
  center: true        // 可选，默认 true。false 时视窗跳到尾部并开启 follow
});
```

### 4.6 主题（dark / light）

| 方法 | 说明 |
|------|------|
| `setTheme('dark' \| 'light')` | 切换黑白主题。CSS 变量 + Canvas 同步。用户偏好自动持久化到 `localStorage['klineEngineV2:theme']` |
| `getTheme()` → `string` | 当前主题 |

也可以直接点工具栏上的 `☼ Light / ☾ Dark` 按钮。

### 4.6b K 线类型（Heikin-Ashi / 真实 OHLC）

| 方法 | 说明 |
|------|------|
| `setCandleType('ha' \| 'normal')` | 切换 K 线渲染类型。`ha` = Heikin-Ashi（默认，Tang 策略专用）；`normal` = 真实 OHLC（对照 moomoo 等平台用）。偏好持久化到 `localStorage['klineEngineV2:candleType']` |
| `getCandleType()` → `'ha' \| 'normal'` | 当前类型 |

工具栏 `HA / OHLC` 按钮等价于 `setCandleType(...)`。切换影响 **K 线体、影线、高低点标签、Y 轴范围、标注锚点** —— 所有从 bar 读 OHLC 的地方都会一致切换。

**HUD 面板的 O/H/L/C 始终显示真实 OHLC**，不随切换变化 —— HUD 是数据视图，不是渲染视图。

**⚠️ 策略信号仍基于 HA**：Tang 策略的信号检测（Reject MA10 / 信号 B / 八步清单）在数据生产阶段（`prepare_data.py`）就已基于 HA 算好并写进 annotations。切到 `normal` 模式时，annotations 标注位置依然是按 HA 形态画的，视觉上可能和真实 K 线"错位"—— 这是预期行为，不是 bug。

### 4.7 均线可见性

`engine.maVisibility` 是可变对象，9 条线全部可独立开关：

```js
engine.maVisibility = {
  m5: true, m10: true, m20: true, m30: true,
  m50: true, m60: true, m120: true, m200: true,
  vw: true
};  // 默认全部开
```

工具栏提供 9 个按钮（MA5 / MA10 / MA20 / MA30 / MA50 / MA60 / MA120 / MA200 / VWAP）切换，偏好持久化到 `localStorage['klineEngineV2:maVisibility']`。

**数据缺失 ≠ 视觉 bug**：如果某条 MA 的数据字段未在 JSON 中提供（或 warmup 不足填了 null），即使 `maVisibility` 是 `true`，线也不会绘制。引擎不会报错。

**程序化修改**：

```js
engine.maVisibility.m50 = false;
engine._updateToolbarState();  // 同步按钮状态
engine.scheduleRender();        // 重绘
```

（当前没有专用 `setMAVisibility` 方法 — 直接改属性 + 手动触发 render 即可。如果你的产品频繁调用，建议后续补一个。）

### 4.7b Reveal cutoff（隐藏未来走势）

| 方法 | 说明 |
|------|------|
| `setRevealCutoff(input)` → `{ '1m', '5m' }` | 设置「允许显示/播放的最大 bar index」。bar index > cutoff 的 K 线、成交量、均线、标注都不渲染；Y 轴范围仅参考 cutoff 内的 bar；`currentIndex`、`play()`、`stepForward()`、`setCurrentIndex()` 都按 cutoff 截断。`loadData()` 会清空。|
| `getRevealCutoff(timeframe?)` → `number \| null` | 读取当前或指定 timeframe 的 cutoff；`null` = 无限制 |

**`setRevealCutoff` 的三种调用方式**：

```js
// 1. 清空所有 cutoff
engine.setRevealCutoff(null);

// 2. 设当前 timeframe 的 cutoff 到 bar 31
engine.setRevealCutoff(31);

// 3. 显式指定 timeframe
engine.setRevealCutoff({ timeframe: '1m', barIndex: 31 });
engine.setRevealCutoff({ timeframe: '5m', barIndex: null }); // 清空某一个 tf
```

**行为约定**：

- `cutoff` 是**当前 timeframe 的绝对 bar index**（0 起，和 `setCurrentIndex`/`scrollTo` 一致）。两个 tf 各自独立存。
- 内部只压缩视窗的 `end`（不改 `count` / 槽位宽度），cutoff 之后的位置留白，视觉上等同于播放还没推进到。
- `currentIndex > cutoff` 时自动 clamp 到 cutoff；正在 `play()` 会先暂停。
- 触碰 cutoff 后再 `play()` / `stepForward()` 直接 no-op；若 `_playbackTick()` 推进到 cutoff 也会自动 `pause()`。
- HUD / 十字线对 cutoff 之后的 bar 不显示数据（focus bar 也会 clamp 到 cutoff）。
- 事件：`setRevealCutoff()` 实际变更时会 emit `revealcutoff:changed`，payload 是 `{ '1m': number|null, '5m': number|null }` 的快照。

**典型教学场景**：

```js
// 训练模式：只让用户看到决策 K 及之前
engine.setRevealCutoff({ timeframe: '1m', barIndex: 31 });

// 用户答完题，揭示后续走势
engine.setRevealCutoff(null);
```

### 4.7c Highlight ranges（外部联动高亮）

| 方法 | 说明 |
|------|------|
| `setHighlightRanges(input)` → `Range[]` | 替换当前高亮集。`null`/`[]` 清空；单个对象会被包进数组。每个 range = `{ timeframe, startIndex, endIndex, style? }`，`style` ∈ `'olive' \| 'red' \| 'blue'`（默认 `olive`）。Ranges 的 `timeframe` 不等于当前 tf 时会被存起来但不绘制，等切 tf 后自动露出。|
| `getHighlightRanges()` → `Range[]` | 读当前高亮（浅拷贝） |

**行为约定**：

- 在 K 线背后绘制半透明带（candle/volume 之前），用 `rc.xForIndex(start) - slotWidth/2` 到 `rc.xForIndex(end) + slotWidth/2` 覆盖整个 price 区域。
- 若 range 超出当前 viewport，直接不画（调用方可配合 `scrollTo` 居中）；若部分出屏，按 viewport clamp。
- 若 cutoff 已设，band 的 `end` 会被 cutoff 截断，`start > cutoff` 时整条跳过。
- `loadData()` 清空当前高亮。
- 事件：`setHighlightRanges()` 实际变更时 emit `highlight:changed`，payload 是 `Range[]` 的快照。

**典型教学场景**：

```js
// 信号验证面板 → 图表联动
// 点击 "MA10 Trigger" 行 → 高亮决策 K 那一根
engine.setHighlightRanges({ timeframe: '1m', startIndex: 31, endIndex: 31 });

// 点击 "Trend Confirmed" 行 → 切 5m 并覆盖整段
engine.setTimeframe('5m');
engine.setHighlightRanges({ timeframe: '5m', startIndex: 0, endIndex: 32 });

// 再点一次清空
engine.setHighlightRanges(null);
```

### 4.8 事件订阅

| 方法 | 说明 |
|------|------|
| `on(event, handler)` → `unsubscribe` | 订阅事件。返回值是取消订阅的函数 |
| `off(event, handler)` | 手动取消订阅 |

```js
const off = engine.on('bar:click', ({ index, bar }) => {
  console.log('clicked bar', index, bar);
});
// 稍后：off();
```

---

## 五、事件清单

引擎通过内置 EventBus 对外广播以下事件：

| 事件名 | Payload | 触发时机 |
|--------|---------|----------|
| `data:loaded` | `summary` 对象（同 `loadData` 返回值） | 每次 `loadData()` 成功后 |
| `viewport:changed` | `{ start, end, count, minCount, maxCount, ... }` | viewport 变动（缩放 / 拖拽 / tf 切换 / scrollTo / 播放推进） |
| `playback:tick` | `{ index }` | 播放推进一根 bar 或手动 `stepForward/Back` |
| `playback:state` | `{ playing, speed }` | `play()` / `pause()` / `setSpeed()` |
| `bar:click` | `{ index, bar }` | 用户点 K 线图空白处（非标注 pin） |
| `annotation:click` | `annotation` 对象（原始的，非 hit zone） | 用户点了标注 pin |
| `theme:changed` | `{ theme }` | `setTheme()` 实际发生切换时 |
| `candletype:changed` | `{ candleType: 'ha' \| 'normal' }` | `setCandleType()` 实际发生切换时 |
| `ma:visibility` | `{ m5, m10, m20, m30, m50, m60, m120, m200, vw }`（快照，全部 9 个键） | MA 开关被切换 |
| `revealcutoff:changed` | `{ '1m': number\|null, '5m': number\|null }` | `setRevealCutoff()` 实际变更时 |
| `highlight:changed` | `Range[]` 快照 | `setHighlightRanges()` 实际变更时 |

---

## 六、典型集成场景

### 6.1 教程页 — 静态数据 + 场景标注

```js
const engine = new KlineEngine({ container: el });
const data = await fetch('case-01.json').then((r) => r.json());
engine.loadData(data);

// 点标注时显示对应讲解
engine.on('annotation:click', (anno) => {
  showTeachingCard(anno.title, anno.body);
});
```

### 6.2 每日复盘 — 拉当天数据 + 推进回放

```js
const engine = new KlineEngine({ container: el });
const todayData = await fetchDailyReviewData();
engine.loadData(todayData);

// 自动播放到当前时刻
engine.setSpeed(2);
engine.play();

engine.on('playback:tick', ({ index }) => {
  updateSidePanel(index);
});
```

### 6.3 回测平台 — 外部驱动 index + 注入信号标注

```js
const engine = new KlineEngine({ container: el });
engine.loadData({
  meta: { date: '2026-01-07' },
  bars_1m: allBars,
  annotations_1m: backtestSignals,    // 由回测产生
});

// 回测逐 bar 推进
for (let i = 0; i < allBars.length; i++) {
  engine.setCurrentIndex(i, { follow: true });
  await runBacktestStep(i);
}

// 回测完跳到第一个触发点
engine.scrollTo({ barIndex: backtestSignals[0].bar_index, highlight: true });
```

### 6.4 多图页 — 多实例并存

每个容器独立 new 一份即可，引擎实例之间完全隔离（EventBus 各自独立）。CSS 样式通过 `ensureEngineStyles()` 幂等注入，只会插一次。

```js
const engines = containers.map((el) => new KlineEngine({ container: el }));
// 页面卸载时
engines.forEach((e) => e.destroy());
```

---

## 七、常见坑

1. **容器宽高要给够**。引擎依赖 `container.clientWidth/clientHeight`。容器是 `display: none` 或 0 宽时，首帧可能画空。`ResizeObserver` 会在可见后自动纠正。

2. **loadData 前不要调用其它数据相关 API**。`setTimeframe('5m')` 在空数据上是 no-op。先 `loadData`。

3. **HA K 线要填 `hO/hH/hL/hC`**。否则画的是普通 K 线。

4. **MA warmup 缺失要填 `null`**，不要填 0。null 会被 `drawSeriesLine` 跳过（L1282），折线会在缺口处断开。0 会把线拉到底部。

5. **destroy 后实例不可复用**。需要重新挂图请新建实例。

6. **DevPanel 是可选的**。`<script src="kline-devpanel.js">` 只在 demo 页引入，产品页不要带它。引擎本体不依赖 DevPanel。

7. **iframe 嵌入时**，主题/MA 偏好的 `localStorage` 是 frame 源域的，宿主页切换时需要跨 frame 通信：

   ```js
   iframe.contentWindow.demoKlineEngine.setTheme('light');
   ```

8. **Canvas 不认 CSS 变量**。如果你要魔改 K 线/MA 颜色，必须同时改 `ensureEngineStyles()` 里的 `--kline-*` 和对应 draw 方法里写死的颜色字符串。详见 `docs/planning/kline-engine-v2/INTERNALS.md` §六。

---

## 八、集成检查清单

接入新产品时，按此清单自检：

- [ ] 容器节点存在且有尺寸
- [ ] `loadData(json)` 的 JSON 通过 `DataManager._normalizeBar` 的字段要求（至少 O/H/L/C + hO/hH/hL/hC）
- [ ] annotations 的 `bar_index` 在 `bars.length` 范围内
- [ ] 页面卸载路径调用了 `engine.destroy()`
- [ ] 没误把 `kline-devpanel.js` 带到产品页
- [ ] 如果是 iframe 集成，确认 URL 路径正确（尤其中文目录名要 URL encode）
- [ ] 宿主页样式没强制覆盖 `.kline-engine__*` 的布局属性（可以覆盖颜色，不要覆盖 `display/position/overflow`）
- [ ] 用 `on('data:loaded', ...)` 作为"引擎就绪"的信号，不要 setTimeout 等

---

## 九、版本记录

| 日期 | 变更 |
|------|------|
| 2026-04-22 | 初始版本 — 基于引擎当前 2250+ 行源码整理；新增 `setTheme` / `maVisibility` / `theme:changed` / `ma:visibility` 文档 |
| 2026-04-23 | 新增 K 线类型切换 — `setCandleType` / `getCandleType` / `candletype:changed` 事件 / toolbar `HA ↔ OHLC` 按钮 |
| 2026-04-24 | 新增 Reveal cutoff — `setRevealCutoff` / `getRevealCutoff` / `revealcutoff:changed` 事件；`play()` / `stepForward()` / `setCurrentIndex()` / `_playbackTick()` / HUD 全部接入 cutoff；`loadData()` 会清空 cutoff |
| 2026-04-24 | 新增 Highlight ranges — `setHighlightRanges` / `getHighlightRanges` / `highlight:changed` 事件；半透明带在 candle/volume 之前绘制，支持 olive/red/blue 三色；respect viewport + cutoff；`loadData()` 会清空 |
| 2026-04-24 | `kline-engine-v2.html` 与 `kline-engine.js` 重新对齐：Reveal cutoff + Highlight ranges 两组改动回写到 HTML 源；demo 页 `runIntegrationTest()` 29/29 通过 |
| 2026-04-24 | `loadData()` 顺序修正：`revealCutoff` / `highlightRanges` 的 clear 提前到 `dataManager.loadData()` 之前。因为 `data:loaded` 事件在 `dataManager.loadData()` 内部同步 emit，之前的顺序会在事件处理器（例如教学适配层）setCutoff/setHighlight 之后再清空，导致状态被反向清除 |
