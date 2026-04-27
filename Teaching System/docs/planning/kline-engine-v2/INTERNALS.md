# K 线引擎 v2 — 内部实现地图 (INTERNALS)

> 更新日期：2026-04-15（OPT-001 ~ OPT-004 瘦身后）
> 目标文件：`dist/kline-engine/kline-engine-v2.html` (2192 行)
> DevPanel：`dist/kline-engine/kline-devpanel.js`（可选，独立模块）
> 伴随文档：`OPTIMIZATION.md`（优化记录）、`ACCEPTANCE.md`（做了什么）
> 本文档回答：**在哪里改**

---

## 一、文件结构总览

整个引擎在一个 `<script>` 块内（L16–L2190），使用 IIFE 包裹。结构如下：

```
L1-13     HTML 骨架（<html>, <body>, #demo-page, #demo-engine）
L14       <script src="kline-devpanel.js">（可选，仅 demo 页）
L16       <script> IIFE 开始
L17-20    常量 + 嵌入式 Demo 数据（DEMO_FIXTURES — 巨大 JSON blob）
L22-111   工具函数（纯函数，无副作用）
L113-427  ensureEngineStyles() — CSS 注入
L429-466  class EventBus
L468-617  class DataManager
L619-707  class ViewportManager
L709-1982 class KlineEngine（主类，含全部渲染/交互/播放/标注逻辑）
L1984     window.KlineEngine = KlineEngine
L1986-2028 bootstrapDemo() — Demo 页初始化
L2034-2190 window.runIntegrationTest() — 29 项集成测试
L2192     IIFE 结束
```

---

## 二、各模块行号 + 核心职责

### 2.1 工具函数（L22–L111）

| 函数 | 行号 | 用途 |
|------|------|------|
| `clamp(value, min, max)` | L22-24 | 通用数值钳位 |
| `isFiniteNumber(value)` | L26-28 | 安全数值检查 |
| `formatPrice(value, digits)` | L30-32 | 格式化价格显示 |
| `formatSignedPrice(value, digits)` | L34-40 | 带正负号的价格 |
| `formatPercent(value, digits)` | L42-48 | 百分比格式化 |
| `formatCompactCN(value, digits)` | L50-62 | 中文万/亿简写 |
| `formatVolume(value)` | L64-66 | 成交量格式化 |
| `escapeHtml(value)` | L68-75 | HTML 转义 |
| `getBarDirection(bar)` | L77-81 | 判断涨跌方向 |
| `parseBarDate(ts)` | L83-89 | 时间戳解析 |
| `formatBarDateLabel(ts)` | L91-101 | 日期标签 MM/DD HH:MM |
| `formatBarDateDivider(ts)` | L103-111 | 日期分隔 MM/DD |

### 2.2 CSS 注入（L113–L427）

| 函数 | 行号 | 说明 |
|------|------|------|
| `ensureEngineStyles()` | L113-427 | 幂等注入 `<style data-kline-engine>` |

CSS 变量定义在 L121-145，是**改颜色的第一站**。

### 2.3 class EventBus（L429–L466）

简易 pub/sub，约 40 行。

| 方法 | 行号 | 说明 |
|------|------|------|
| `on(eventName, handler)` | L434-440 | 订阅，返回 unsubscribe 函数 |
| `off(eventName, handler)` | L442-451 | 取消订阅 |
| `emit(eventName, payload)` | L453-461 | 触发事件 |
| `destroy()` | L463-465 | 清除所有监听器 |

### 2.4 class DataManager（L468–L617）

数据层，不触碰 DOM。

| 方法 | 行号 | 说明 |
|------|------|------|
| `constructor(eventBus)` | L469-473 | 初始化空数据 |
| `_emptyData()` | L475-483 | 空数据模板 |
| `_normalizeBar(rawBar, meta)` | L485-504 | **单 bar 标准化**（字段映射在这里） |
| `_normalizeAnnotations(rawAnnotations)` | L506-517 | 标注标准化 |
| `loadData(payload)` | L519-535 | **核心加载入口**，触发 `data:loaded` |
| `getSummary()` | L537-548 | 数据摘要 |
| `getAvailableTimeframes()` | L550-552 | 可用时间框架 |
| `getTimeframe()` | L554-556 | 当前活跃时间框架 |
| `getMeta()` | L558-560 | 元数据访问 |
| `hasTimeframe(tf)` | L562-564 | 检查某 tf 是否有数据 |
| `getBars(tf)` | L566-568 | **取 bar 数组**（最常调用） |
| `getAnnotations(tf)` | L570-572 | 取标注数组 |
| `getLastIndex(tf)` | L574-576 | 最后一根 bar 的索引 |
| `findNearestIndexByTime(tf, target)` | L582-597 | 时间对齐（切换 tf 时用） |
| `switchTimeframe(tf, currentIndex)` | L599-616 | **时间框架切换**（保持时间对齐） |

### 2.5 class ViewportManager（L619–L707）

视窗计算层，不触碰 DOM。

| 方法 | 行号 | 说明 |
|------|------|------|
| `constructor(eventBus)` | L620-626 | 初始化 zoomScale=1, followMode=true |
| `reset()` | L628-632 | 重置缩放和 follow |
| `setChartWidth(width)` | L634-636 | 存储图表宽度 |
| `getViewLimits(tf, totalBars)` | L638-642 | 缩放极限 (min 10, max 390) |
| `getWindowBarCount(width, tf)` | L644-649 | **默认可见 bar 数**（基于 slot 像素宽） |
| `getResolvedViewCount(...)` | L651-658 | 考虑 zoom 后的实际 bar 数 |
| `getVisibleWindow({...})` | L660-682 | **核心方法：计算可见窗口 start/end** |
| `applyZoom(nextCount, {...})` | L684-701 | **缩放执行**（含锚点计算） |
| `setFollowMode(enabled)` | L703-706 | follow/manual 模式切换 |

### 2.6 class KlineEngine（L709–L1982）— 主类

#### 2.6.1 构造与初始化

| 方法/区域 | 行号 | 说明 |
|-----------|------|------|
| `constructor({ container })` | L710-756 | 创建 EventBus/DataManager/ViewportManager，构建 DOM，绑定事件 |
| 内部 state 声明 | L720-743 | **所有共享 state 在这里**，见第五章 |
| `_buildDOM()` | L757-823 | **DOM 结构生成**（toolbar, canvas, overlay） |
| `_bindControls()` | L824-893 | **工具栏按钮事件**（tf 切换、zoom、play、speed、follow） |
| `_bindCanvasHover()` | L895-981 | **鼠标交互**（mousemove、wheel zoom、drag pan、click、mouseleave） |
| `_bindKeyboard()` | L983-1014 | **键盘快捷键**（Space、←→、1/5） |
| `_bindResize()` | L1016-1022 | ResizeObserver |

#### 2.6.2 坐标与渲染上下文

| 方法 | 行号 | 说明 |
|------|------|------|
| `_getChartWidth()` | L1024-1026 | CSS 像素宽度 |
| `_getChartHeight()` | L1028-1031 | CSS 像素高度（min 320） |
| `_resizeCanvas()` | L1033-1047 | **Canvas DPR 处理**（高清屏适配） |
| `_resolveInitialIndex(tf)` | L1049-1060 | 从 meta 解析初始播放位置 |
| `_updateToolbarState()` | L1062-1069 | 工具栏按钮高亮状态 |
| `_getViewportPayload()` | L1071-1079 | 构建 viewport:changed 事件 payload |
| `chartArea(width, height)` | L1081-1090 | **图表区域布局常量**（margin/padding） |
| `buildRenderContext(bars, visible, w, h)` | L1092-1157 | **核心坐标系构建** — 价格 <-> 像素映射 |

#### 2.6.3 绘制方法

| 方法 | 行号 | 说明 |
|------|------|------|
| `drawGrid(ctx, rc)` | L1159-1189 | 网格线（横向 + 纵向） |
| `drawVolumeBars(ctx, rc)` | L1191-1210 | **成交量柱**（含新 bar 动画） |
| `drawCandles(ctx, rc)` | L1212-1272 | **K 线绘制**（HA 空心描边，影线不穿体） |
| `drawSeriesLine(ctx, rc, field, color)` | L1274-1299 | 通用折线（MA/VWAP 共用） |
| `drawMALines(ctx, rc)` | ~L1320-1340 | **MA5/10/20/30/50/60/120/200 + VWAP**（9 条，按 `this.maVisibility` 开关） |
| `drawAxes(ctx, rc)` | L1313-1343 | **坐标轴**（右侧价格+百分比，底部时间，VOL 标签） |
| `drawHighLowLabels(ctx, rc)` | L1345-1385 | **高低点标签** + 引导线 |
| `drawCrosshair(ctx, rc, hoveredIndex)` | L1387-1431 | **十字线** + 价格/时间标签 |
| `updatePanels(rc, focusBar, crosshair)` | L1433-1453 | **HUD 面板**更新（OHLC、MA 值） |

#### 2.6.4 PlaybackManager 区域（L1455–L1579）

| 方法 | 行号 | 说明 |
|------|------|------|
| `play()` | L1458-1467 | 开始播放 |
| `pause()` | L1469-1478 | 暂停 |
| `togglePlayback()` | L1480-1482 | 切换播放/暂停 |
| `stepForward()` | L1484-1490 | 前进一步 |
| `stepBack()` | L1492-1501 | 后退一步 |
| `setSpeed(speed)` | L1503-1508 | 设置速度（0.5/1/2/4） |
| `getSpeed()` | L1510-1512 | 获取当前速度 |
| `isPlaying()` | L1514-1516 | 播放状态查询 |
| `_schedulePlaybackTick()` | L1518-1522 | 定时器调度（delay = 500/speed） |
| `_playbackTick()` | L1524-1534 | 单次 tick（推进 + 重新调度） |
| `_advanceTo(idx)` | L1536-1545 | **核心推进**（设 index + 触发动画 + emit 事件） |
| `_animateNewBar(idx)` | L1547-1567 | **新 bar 缩放动画**（ease-out-quad, 150ms） |
| `_updatePlaybackUI()` | L1569-1578 | 播放按钮图标 + 速度按钮高亮 |

#### 2.6.5 AnnotationManager 区域（L1581–L1830）

| 方法/属性 | 行号 | 说明 |
|-----------|------|------|
| `ANNO_COLORS` (static) | L1584-1590 | **五色映射表**（red/green/blue/orange/purple） |
| `_annoColor(style)` | L1592-1594 | 颜色查找 |
| `_parseScore(score)` | L1596-1603 | 解析 "6/8" 格式分数 |
| `_isHighScore(anno)` | L1605-1608 | 高分判定（>=6） |
| `drawAnnotationPins(ctx, rc)` | L1610-1704 | **标注 pin 绘制**（stem + triangle + hit zone + 高亮闪烁） |
| `_hitTestAnnotation(mx, my)` | L1706-1714 | 鼠标命中测试 |
| `_showAnnoTooltip(zone)` | L1716-1757 | 浮层显示 |
| `_hideAnnoTooltip()` | L1759-1762 | 浮层隐藏 |
| `_updateAnnoHover()` | L1764-1778 | hover 状态管理 |
| `scrollTo(target)` | L1780-1830 | **跳转 + 居中 + 高亮闪烁**（支持跨 tf） |

#### 2.6.6 公共 API 与生命周期（L1832–L1982）

| 方法 | 行号 | 说明 |
|------|------|------|
| `setCurrentIndex(nextIndex, opts)` | L1832-1844 | 设置当前索引 |
| `loadData(json)` | L1847-1858 | **数据加载入口**（pause -> normalize -> reset viewport） |
| `getTimeframe()` | L1860-1862 | 获取当前 tf |
| `getCurrentIndex()` | L1864-1866 | 获取当前 index |
| `setTimeframe(tf)` | L1868-1878 | **切换时间框架** |
| `scheduleRender()` | L1880-1888 | **RAF 防抖渲染调度** |
| `render()` | L1890-1948 | **主渲染循环**（协调所有 draw 方法） |
| `destroy()` | L1950-1982 | **释放全部资源**（timer/RAF/listener/DOM） |

---

## 三、Render Loop 数据流图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        scheduleRender()                             │
│                   L1880 — RAF 防抖，保证每帧只渲染一次               │
└────────────────────────────┬────────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          render()  L1890                             │
│                                                                     │
│  1. ctx.clearRect() — 清空画布                                       │
│  2. 填充背景 #1e1e1e + 基础网格                                      │
│  3. bars = DataManager.getBars(currentTimeframe)     ← 取数据        │
│  4. visible = ViewportManager.getVisibleWindow({     ← 计算可见窗口   │
│       totalBars, currentIndex, timeframe, chartWidth                 │
│     })                                                              │
│  5. rc = buildRenderContext(bars, visible, w, h)     ← 坐标系构建    │
│     ┌─────────────────────────────────────────────┐                 │
│     │ rc 包含：                                    │                 │
│     │  - bars, visibleBars, visible                │                 │
│     │  - priceMin/Max, volumeMax                  │                 │
│     │  - slotWidth, bodyWidth                     │                 │
│     │  - xForIndex(i), yForPrice(p)               │                 │
│     │  - yForVolume(v), priceForY(y)              │                 │
│     │  - barIndexForX(x)                          │                 │
│     └─────────────────────────────────────────────┘                 │
│  6. hoveredIndex = barIndexForX(hover.x)           ← 鼠标→bar 索引  │
│  7. focusBar = bars[hoveredIndex ?? currentIndex]                    │
│                                                                     │
│  ┌─── 按此顺序调用绘制方法 ──────────────────────┐                 │
│  │  drawGrid(ctx, rc)               L1159        │ ← 最底层          │
│  │  drawVolumeBars(ctx, rc)          L1191        │                  │
│  │  drawCandles(ctx, rc)             L1212        │ ← 核心 K 线       │
│  │  drawMALines(ctx, rc)             L1301        │ ← 穿过空心 K 线   │
│  │  drawAxes(ctx, rc)                L1313        │                  │
│  │  drawHighLowLabels(ctx, rc)       L1345        │                  │
│  │  drawAnnotationPins(ctx, rc)      L1610        │                  │
│  │  drawCrosshair(ctx, rc, idx)      L1387        │ ← 最顶层          │
│  └───────────────────────────────────────────────┘                  │
│                                                                     │
│  8. updatePanels(rc, focusBar, crosshairState)    ← DOM 面板更新     │
│  9. _updateAnnoHover()                            ← 标注浮层管理     │
└─────────────────────────────────────────────────────────────────────┘
```

**触发 `scheduleRender()` 的路径**：

```
用户操作                          → 中间处理            → scheduleRender()
─────────────────────────────────────────────────────────────────────
mousemove / pointermove           → hover 更新          → L901
wheel                             → applyZoom()         → L943
drag (pointermove)                → viewStart 更新      → L922
keydown (arrows/space/1/5)        → step/play/setTf     → 各自调用
ResizeObserver                    → _resizeCanvas()     → L1046
loadData()                        → reset + redraw      → L1856
setTimeframe()                    → switchTF + redraw   → L1876
scrollTo()                        → viewport 调整       → L1829
playbackTick → _advanceTo()       → 动画 + 推进         → L1558
```

---

## 四、常见修改场景速查

### 4.1 视觉调整

| 改什么 | 去哪里 | 行号 |
|--------|--------|------|
| **K 线颜色**（涨绿跌红） | `drawCandles()` 内 `ctx.strokeStyle` | L1237 |
| **K 线宽度**（实体/影线） | `buildRenderContext()` 内 `bodyWidth` 计算 | L1124 |
| **K 线影线宽度** | `drawCandles()` 内 `ctx.lineWidth` | L1238 |
| **CSS 主题变量** | `ensureEngineStyles()` 内 `:root` 块 | L121-145 |
| **背景色** | CSS 变量 `--kline-bg` / `--kline-chart` | L123-124 |
| **均线颜色** | CSS 变量 `:root` 块（--kline-ma5/10/20/30/50/60/120/200 + --kline-vwap）+ `drawMALines()` 里 9 条 `drawSeriesLine` 调用 | CSS 变量与 Canvas 硬编码值**必须一一对应**，改一处要改两处 |
| **成交量柱颜色** | `drawVolumeBars()` 内 `ctx.fillStyle` | L1197 |
| **K 线区域 vs 成交量区占比** | `buildRenderContext()` 内 `priceHeight` / `volumeHeight` | L1094-1095 |
| **十字虚线样式** | `drawCrosshair()` 内 `ctx.setLineDash` | L1400 |
| **高低点标签样式** | `drawHighLowLabels()` 内 | L1367-1381 |
| **网格线透明度** | `drawGrid()` 内 `ctx.strokeStyle` | L1161 |
| **坐标轴字体** | `drawAxes()` 内 `ctx.font` | L1316 |
| **图表区域 margin** | `chartArea()` 函数 | L1081-1090 |
| **标注 pin 颜色** | `ANNO_COLORS` 静态属性 | L1584-1590 |
| **标注 pin 大小** | `drawAnnotationPins()` 内 `pinSize` / `stemLen` | L1633-1634 |

### 4.2 行为调整

| 改什么 | 去哪里 | 行号 |
|--------|--------|------|
| **缩放因子** | `_bindCanvasHover()` 内 wheel handler | L930（1.12） |
| **缩放范围**（min/max bar 数） | `ViewportManager.getViewLimits()` | L638-642 |
| **默认可见 bar 数** | `ViewportManager.getWindowBarCount()` | L644-649 |
| **播放速度列表** | `setSpeed()` 内 `validSpeeds` | L1504 |
| **播放间隔** | `_schedulePlaybackTick()` 内 `delay` | L1520 |
| **新 bar 动画时长** | `_animateNewBar()` 内 `duration` | L1550 |
| **新 bar 动画曲线** | `_animateNewBar()` 内 ease-out-quad | L1557 |
| **键盘快捷键** | `_bindKeyboard()` | L983-1014 |
| **高分标注阈值** | `_isHighScore()` 内 `parsed.num >= 6` | L1607 |
| **scrollTo 高亮持续时间** | `scrollTo()` 内 `1200` | L1824 |
| **Y 轴 padding 比例** | `buildRenderContext()` 内 `0.02` | L1119 |

### 4.3 添加新指标

1. **数据层**：`DataManager._normalizeBar()` L485-504 — 添加新字段映射
2. **渲染层**：`drawMALines()` L1301-1311 — 添加新的 `drawSeriesLine()` 调用
3. **HUD 面板**：`updatePanels()` L1433-1453 — 添加新指标显示
4. **CSS 变量**：`ensureEngineStyles()` L121-145 — 添加新颜色变量
5. **图例**：如需图例，在 HUD 的 HTML 模板中添加

### 4.4 添加新标注类型

1. **颜色映射**：`ANNO_COLORS` L1584-1590 — 添加新颜色
2. **渲染差异**：`drawAnnotationPins()` L1610-1704 — 根据 `anno.type` 分支
3. **浮层内容**：`_showAnnoTooltip()` L1716-1757 — 定制显示

---

## 五、内部 State 关系（Source of Truth）

```
┌───────────────── KlineEngine 实例 ─────────────────┐
│                                                     │
│  Source of Truth:                                   │
│  ────────────────                                   │
│  currentTimeframe  (string: '1m'|'5m')              │  → 当前活跃 timeframe
│  currentIndex      (number)                         │  → 当前"播放头"位置
│                                                     │
│  hover = { x, y, inside }                           │  → 鼠标位置（实时）
│  dragState                                          │  → 拖拽中间态
│  lastRenderContext (rc)                             │  → 上一帧的坐标映射（只读缓存）
│                                                     │
│  委托给 DataManager:                                 │
│  ─────────────────                                  │
│  dataManager.data      → 标准化后的全量数据          │
│  dataManager.timeframe → 与 currentTimeframe 同步    │
│                                                     │
│  委托给 ViewportManager:                             │
│  ──────────────────────                              │
│  viewportManager.zoomScale   → 缩放倍率             │
│  viewportManager.followMode  → 追踪模式（true=跟尾） │
│  viewportManager.viewStart   → 手动模式下的起始 bar  │
│  viewportManager.chartWidth  → 图表 CSS 像素宽       │
│                                                     │
│  播放状态:                                           │
│  ─────────                                          │
│  _playing            → 是否播放中                    │
│  _playbackSpeed      → 当前速度 (0.5/1/2/4)         │
│  _playbackTimerId    → setTimeout ID                │
│  _newBarAnim         → { index, progress } 动画态   │
│  _newBarAnimHandle   → RAF ID                       │
│                                                     │
│  标注状态:                                           │
│  ─────────                                          │
│  _hoveredAnno        → 当前 hover 的标注对象         │
│  _annoHitZones[]     → 每帧重建的 hit zone 列表     │
│  _scrollToHighlight  → 闪烁高亮 { index, until }    │
│                                                     │
│  生命周期:                                           │
│  ─────────                                          │
│  _destroyed          → 是否已销毁（不可逆）          │
│  _renderHandle       → RAF ID (scheduleRender 防抖)  │
│  boundKeydown        → keydown handler ref（destroy 用）│
│  resizeObserver      → ResizeObserver ref            │
└─────────────────────────────────────────────────────┘
```

### 关键 State 同步规则

1. **`currentTimeframe` 与 `dataManager.timeframe` 必须同步**：
   - `loadData()` 中 L1849 同步
   - `setTimeframe()` 中 L1871 同步
   - `scrollTo()` 中 L1800 同步

2. **`currentIndex` 是播放头的唯一 Source of Truth**：
   - 修改路径：`loadData()`、`setTimeframe()`、`scrollTo()`、`stepForward/Back()`、`setCurrentIndex()`、`_advanceTo()`
   - 每次修改后必须调用 `scheduleRender()`

3. **`viewportManager.followMode` 决定视窗行为**：
   - `true` = 视窗自动跟踪 `currentIndex`（播放/步进时）
   - `false` = 视窗由 `viewStart` 固定（拖拽/scrollTo 居中时）
   - `getVisibleWindow()` 内部会在 `viewStart >= maxStart` 时自动恢复 `followMode=true`（L675-678）

---

## 六、CSS 变量速查

所有变量定义在 `ensureEngineStyles()` 的 `:root` 块中（L121-145）：

| 变量 | 值 | 用途 |
|------|-----|------|
| `--kline-bg` | `#1a1a1a` | 外框背景 |
| `--kline-chart` | `#1e1e1e` | K 线区背景 |
| `--kline-panel` | `rgba(24,27,33,0.92)` | 面板背景 |
| `--kline-panel-alt` | `rgba(35,40,48,0.98)` | 面板备选 |
| `--kline-grid` | `rgba(255,255,255,0.06)` | 网格线 |
| `--kline-grid-strong` | `rgba(255,255,255,0.12)` | 强网格线 |
| `--kline-border` | `rgba(255,255,255,0.08)` | 边框 |
| `--kline-text` | `rgba(255,255,255,0.5)` | 普通文字 |
| `--kline-text-strong` | `rgba(255,255,255,0.85)` | 强调文字 |
| `--kline-text-bright` | `rgba(255,255,255,0.95)` | 高亮文字 |
| `--kline-accent` | `#00b894` | 涨色（绿） |
| `--kline-danger` | `#e74c3c` | 跌色（红） |
| `--kline-vol-up` | `rgba(0,184,148,0.5)` | 成交量涨柱 |
| `--kline-vol-down` | `rgba(231,76,60,0.5)` | 成交量跌柱 |
| `--kline-crosshair` | `rgba(255,255,255,0.3)` | 十字线 |
| `--kline-label-bg` | `rgba(40,40,40,0.9)` | 标签背景 |
| `--kline-ma5` | `#eab308` | MA5（金黄） |
| `--kline-ma10` | `#e6a23c` | MA10（橙） |
| `--kline-ma20` | `#ec4899` | MA20（玫红） |
| `--kline-ma30` | `#14b8a6` | MA30（青） |
| `--kline-ma50` | `#409eff` | MA50（蓝） |
| `--kline-ma60` | `#6366f1` | MA60（靛） |
| `--kline-ma120` | `#f43f5e` | MA120（绯红） |
| `--kline-ma200` | `#67c23a` | MA200（绿） |
| `--kline-vwap` | `#a855f7` | VWAP（紫） |
| `--kline-muted` | `rgba(255,255,255,0.32)` | 弱化文字 |
| `--kline-shadow` | `0 24px 80px rgba(0,0,0,0.35)` | 外框阴影 |

> 注意：部分绘制方法内直接写死了颜色值（如 `drawCandles()` 的 `'#00b894'`），**没有**引用 CSS 变量（Canvas API 不支持 CSS 变量）。修改颜色时须同时修改 CSS 变量和 Canvas 绘制函数。

---

## 七、嵌入式数据与 Demo 区域

| 区域 | 行号 | 说明 |
|------|------|------|
| `DEMO_FIXTURES` JSON blob | L20 | 两个 fixture（seed + fullDay），占文件约 60% 体积 |
| `bootstrapDemo()` | L1986-2028 | Demo 页初始化（创建引擎 + 加载 seed fixture） |
| `runIntegrationTest()` | L2034-2190 | 29 项集成测试函数 |

> `DEMO_FIXTURES` 被包裹在 `/*__KLINE_ENGINE_V2_DEMO_DATA_START__*/` 和 `/*__KLINE_ENGINE_V2_DEMO_DATA_END__*/` magic comment 中（L20），方便外部脚本替换数据。

---

## 八、DevPanel（可选模块）

独立文件 `kline-devpanel.js`，仅在 demo 页通过 `<script src>` 引入。

| 功能 | 说明 |
|------|------|
| Engine State | 实时显示 tf / index / bars / zoom / mode / playback |
| Demo Fixtures | 自动检测 `window.__klineEngineV2Fixtures`，按钮切换 |
| Data Import | 拖拽/点击选择 JSON 文件，带 `bars_1m`/`bars_5m` 格式校验 |
| Keyboard Shortcuts | 快捷键速查（从引擎中剥离） |

**隔离方式**：通过引擎公共 API（`loadData()` / `getCurrentIndex()` / `getTimeframe()` / `isPlaying()` / `getSpeed()`）和 EventBus 事件（`viewport:changed` / `playback:tick` / `playback:state` / `data:loaded`）通信，不依赖内部实现。

---

## 九、修改注意事项

### 不要踩的坑

1. **Canvas 不支持 CSS 变量**：`ctx.fillStyle = 'var(--kline-accent)'` 是无效的。Canvas 绘制函数里必须写死颜色字符串。如果要统一管理，需在 JS 层定义颜色常量。

2. **`lastRenderContext` 是上一帧的快照**：不要在 render 前依赖它的值做逻辑判断（除了交互事件 handler 中短暂使用）。

3. **`_annoHitZones` 每帧重建**：不要缓存它——它在 `drawAnnotationPins()` 的开头被清空。

4. **播放 timer 和动画 RAF 是两套独立系统**：
   - `_playbackTimerId` = `setTimeout`，控制 bar 推进节奏
   - `_newBarAnimHandle` = `requestAnimationFrame`，控制新 bar 的缩放入场动画
   - `destroy()` 必须清理两者

5. **`followMode` 自动恢复**：`getVisibleWindow()` 内部会在 `viewStart >= maxStart` 时自动设 `followMode = true`（L675-678）。不要假设手动设了 `followMode = false` 就一定保持。

6. **DPR 处理**：Canvas 的物理像素尺寸 = CSS 尺寸 x `devicePixelRatio`（L1036-1042）。`render()` L1892-1893 会除以 DPR 得到逻辑尺寸。所有坐标计算基于逻辑像素。

7. **绘制顺序影响层叠**：`render()` L1938-1947 中的调用顺序决定了视觉层叠。十字线 (`drawCrosshair`) 必须最后画。

---

## 十、已移除项（OPT-001 ~ OPT-004）

以下组件已在瘦身中移除，如需参考旧实现请查看 git 历史：

| 移除项 | 原因 |
|--------|------|
| 底部进度条（scrubber） | 鼠标拖拽已覆盖导航 |
| 底部状态栏（status panel） | 调试信息迁移至 DevPanel |
| 右上角快捷键提示（message panel） | 迁移至 DevPanel |
| 工具栏 Seed/Full Day 按钮 | Demo 功能迁移至 DevPanel |
| `currentFixtureName` state | 引擎不再管理 fixture 身份 |
| `progressDragState` state | 随进度条一起移除 |
| `_bindProgressBar()` 方法 | 随进度条一起移除 |
| `updateScrubber()` 方法 | 随进度条一起移除 |

---

## 十一、变更记录

| 日期 | 变更 |
|------|------|
| 2026-04-15 | 初始版本 — 基于全量源码分析生成 |
| 2026-04-15 | OPT-001~004 瘦身后更新 — 行号全量刷新，新增 DevPanel 章节，新增已移除项章节 |
| 2026-04-22 | 新增黑白主题切换 + MA 可见性开关；均线扩展至 9 条（MA5/10/20/30/50/60/120/200 + VWAP）；新增 CSS 变量 `--kline-ma5/20/30/60/120` 与主题变量 `--kline-hud-bg/tooltip-bg/chip-bg/button-bg*/swatch-ring` 等；新增 `engine.setTheme()` / `engine.maVisibility` 公共 API 及 `theme:changed` / `ma:visibility` 事件。行号因插入代码整体下移约 60 行，如需精确定位以源码为准。 |
| 2026-04-23 | 新增 K 线类型切换（HA ↔ Normal OHLC）：新增 `this.candleType` state、`_resolveOHLC(bar)` 辅助方法（所有从 bar 读 OHLC 的渲染路径统一经此）、`setCandleType()` / `getCandleType()` 公共 API、toolbar `HA / OHLC` 按钮、`candletype:changed` 事件、localStorage key `klineEngineV2:candleType`。修改点：构造器 state、`_buildDOM` toolbar HTML、`_bindControls` 新 handler、`_updateToolbarState` 新按钮同步、`buildRenderContext`/`drawCandles`/`drawHighLowLabels`/`drawAnnotationPins`/scrollTo 高亮 全部改为调 `_resolveOHLC`。顺手删除死代码 `getBarDirection`（原 L77-81，无调用方）。 |
