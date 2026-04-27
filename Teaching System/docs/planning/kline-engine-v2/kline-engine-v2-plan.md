# K 线引擎 v2：从零构建

> 创建日期：2026-04-14
> 状态：待确认
> 来源：daily-review 前置需求
> 关系：daily-review 的前置工作，完成后供 daily-review Phase 2 直接使用

---

## 一、背景

当前 `kline-sandbox.html` 是一个 ~1327 行的单体 HTML（其中 JS 约 1077 行），采用基于全局 state 对象和注释分区的过程式架构，无 class 封装，模块边界通过函数命名约定隐式表达。约 15–20% 的 JS 逻辑与教学场景耦合（auto-pause 注解阻断、preheat 暗化、segment 选择、分类系统），虽然占比不大，但这些逻辑散布在渲染、播放、交互等多个区域，剥离成本高于重写。daily-review 计划需要一个能独立加载数据、被动展示信号标注、支持点击跳转的 K 线引擎。与其从旧引擎剥离，不如重新构建一个架构更干净、功能更强的 v2 引擎，旧版保留不动。

---

## 二、产出与消费协议

### 产出文件

`dist/kline-engine-v2.html` — 单文件 HTML，既是独立可运行的演示页，也是可嵌入的引擎。

### 消费协议（daily-review 如何使用 v2 引擎）

v2 引擎通过 `window.KlineEngine` 暴露 class，宿主页面按以下协议集成：

```html
<!-- 宿主页面（如 daily-review.html）需要提供的 DOM 容器 -->
<div id="kline-container" style="width:100%; height:600px;"></div>

<script>
  // 引擎挂载协议
  const engine = new KlineEngine({
    container: document.getElementById('kline-container'),  // 必需：DOM 容器
  });

  // 加载数据
  engine.loadData({ bars_1m: [...], bars_5m: [...], annotations_1m: [...] });

  // 监听事件
  engine.on('annotation:click', (anno) => { /* 侧栏联动 */ });
</script>
```

**宿主职责**：提供一个有明确宽高的 DOM 容器，仅此而已。引擎负责在容器内创建 canvas、controls、overlays 等全部 DOM 结构。

**样式交付方式（已选定）**：`KlineEngine` 构造函数首次实例化时，自动向 `document.head` 注入一个带命名空间的 `<style data-kline-engine>` 标签，包含引擎所需的全部 CSS。宿主页面**不需要**手动引入任何样式文件或 `<style>` 块。多次实例化时样式只注入一次（幂等）。

**主题**：当前仅支持深色主题（dark），不暴露 theme 参数。Light theme 作为后续扩展预留，v2 阶段不实现。

**v2 demo 页**：`kline-engine-v2.html` 自身就是一个宿主页面示例，内嵌测试数据，展示引擎的全部功能。daily-review 只需提取 `<script>` 块（其中包含自动注入样式的逻辑），无需额外处理 CSS。

---

## 三、视觉规范（对标 moomoo 券商风格）

> 参考图：`docs/planning/kline-engine-v2/assets/moomoo-spy-2026-04-13-1m.png`
> ⚠️ 执行前须确认参考图已存入上述路径。该截图为视觉验收的唯一基线。

### 主题与配色（已固化，不允许执行时自由发挥）

```
--bg:           #1a1a1a        （外框背景）
--bg-chart:     #1e1e1e        （K线区背景，微亮于外框）
--grid:         rgba(255,255,255, 0.06)  （网格线，极淡）
--text:         rgba(255,255,255, 0.5)   （坐标轴标签）
--text-bright:  rgba(255,255,255, 0.85)  （OHLC 面板、高亮文字）
--green:        #00b894        （涨色 — K 线描边 + 文字）
--red:          #e74c3c        （跌色 — K 线描边 + 文字）
--vol-green:    rgba(0,184,148, 0.5)     （成交量涨柱）
--vol-red:      rgba(231,76,60, 0.5)     （成交量跌柱）
--crosshair:    rgba(255,255,255, 0.3)   （十字虚线）
--label-bg:     rgba(40,40,40, 0.9)      （十字线价格/时间标签背景）
--ma10:         #e6a23c        （MA10 — 橙黄）
--ma50:         #409eff        （MA50 — 蓝）
--ma200:        #67c23a        （MA200 — 绿）
--vwap:         #a855f7        （VWAP — 紫）
```

> 以上色值为最终取值。执行阶段如需微调，须截图对比后更新本文档。

### K 线绘制细节

- **实体宽度**：slot 宽度的 ~65%，不超过 8px，保证"呼吸感"
- **影线宽度**：1px（retina 下 0.5pt 效果），比实体明显更细
- **实体填充**：涨跌都用空心（仅描边），不遮挡穿过实体的均线
- **圆角**：无圆角，干净利落的矩形
- **最小实体高度**：1px（十字线 doji 保证可见）
- **间距**：相邻 K 线间隔 ≥ 2px（缩小到极限也保持间距）

### 坐标轴

- **右侧双轴**：左列=价格（如 319.147），右列=涨跌幅百分比（如 -0.09%）
- **底部时间轴**：日期 + 时间，日期变化处加竖线分隔
- **价格标签样式**：半透明背景色块 + 白色文字（十字线处的动态标签）
- **时间标签样式**：同上

### 成交量区

- **位置**：主图下方，独立区域，高度约为主图的 20%
- **分隔**：与主图有 1px 细线分隔
- **柱体颜色**：跟随对应 K 线的涨跌方向
- **柱体填充**：半透明，不与 K 线争夺视觉焦点
- **左上角标签**：「成交量 VOL: xxx」当前 bar 的成交量

### 十字线与信息面板

- **十字线**：白色虚线（dash: [4, 4]），全幅横竖线
- **价格标签**：右侧坐标轴上，深色背景小方块，显示精确价格
- **时间标签**：底部时间轴上，同样深色方块
- **OHLC 面板**：左上角常驻，显示当前 hover bar 的 开/高/低/收/涨跌/量/额
- **高低点标注**（新增功能，旧版无）：日内最高/最低价处显示价格标签 + 小箭头，在 Task 2 Renderer 中实现

### 缩放与拖拽体验

- **滚轮缩放**：丝滑无卡顿，缩放因子默认 1.08，可调范围 [1.05, 1.15]，执行阶段根据实际手感微调
- **缩放范围**：最少显示 10 根 K 线 ~ 最多显示全天 390 根
- **锚点缩放**：鼠标所在位置的 K 线保持不动（moomoo 标准行为）
- **拖拽平移**：pointer capture，1:1 像素跟手，无惯性
- **边界处理**：拖到边界时有弹性回弹或硬停止，不允许拖出数据范围

### 整体感受目标

> "打开就像在用券商软件看盘，不像在看一个网页"

---

## 四、架构设计

### 模块划分（全部在单文件内，用注释分区）

```
┌─────────────────────────────────────────────┐
│  KlineEngine class                          │
│  ┌───────────────┐  ┌───────────────────┐   │
│  │ DataManager   │  │ ViewportManager   │   │
│  │ - loadData()  │  │ - zoom / pan      │   │
│  │ - getBars()   │  │ - getVisibleWindow│   │
│  │ - switchTF()  │  │ - followMode      │   │
│  └───────────────┘  └───────────────────┘   │
│  ┌───────────────┐  ┌───────────────────┐   │
│  │ Renderer      │  │ InteractionMgr    │   │
│  │ - drawCandles │  │ - wheel zoom      │   │
│  │ - drawMA      │  │ - drag pan        │   │
│  │ - drawVolume  │  │ - crosshair       │   │
│  │ - drawGrid    │  │ - keyboard        │   │
│  │ - drawAxes    │  │ - progress bar    │   │
│  └───────────────┘  └───────────────────┘   │
│  ┌───────────────┐  ┌───────────────────┐   │
│  │ PlaybackMgr   │  │ AnnotationMgr     │   │
│  │ - play/pause  │  │ - passive markers │   │
│  │ - step ±1     │  │ - signal bubbles  │   │
│  │ - speed ctrl  │  │ - click-to-jump   │   │
│  │ - newBar anim │  │ - color by type   │   │
│  └───────────────┘  └───────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │ EventBus (pub/sub)                   │   │
│  │ - 'data:loaded' / 'viewport:changed' │   │
│  │ - 'playback:tick' / 'bar:click'      │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### 与旧版的关键差异

| 维度 | 旧版 sandbox | 新 v2 引擎 |
|------|-------------|-----------|
| 数据加载 | 内嵌 JSON，hardcode 3 个 segment | `engine.loadData(json)` API，外部传入 |
| 标注系统 | auto-pause 阻断式 | 被动展示 + 可选高亮，不阻断播放 |
| 标注颜色 | 固定 green/red/blue | 支持任意颜色，按信号类型映射 |
| Preheat | 调暗前 N 根 K 线 | 不存在，全量展示 |
| 信号交互 | 无 | 标注可点击 → 触发回调；外部可调用 `engine.scrollTo({ timeframe, barIndex })` |
| 播放 | 有，auto-pause 耦合 | 有，纯净播放，不与标注耦合 |
| 时间框架 | 1m/5m 切换 + 时间对齐 | 保留，数据层支持 |
| 模块化 | 基于全局 state 的过程式架构，注释分区 | class 内部分模块，pub/sub 解耦 |
| 外部 API | 无 | `loadData()`, `scrollTo()`, `on()`, `setTimeframe()`, `play()`, `pause()` |

---

## 五、任务分解

### Task 1: 骨架 + EventBus + DataManager + ViewportManager
- HTML/CSS 骨架（canvas-wrap、controls、overlays），全部使用深色主题变量
- `EventBus`：简易 pub/sub（`on`/`off`/`emit`），约 20 行，作为 class 基础设施**最先实现**，后续 Task 2–5 均可直接使用
- `KlineEngine` class 初始化，挂载到 `window.KlineEngine`
- `DataManager`: `loadData(json)`, `getBars()`, `switchTimeframe()`
- `ViewportManager`: zoom/pan state, `getVisibleWindow()`, `applyZoom()`, `setFollowMode()`
- **测试数据准备**：编写提取脚本从 `teaching_segments.json` 中导出 seed_01 为 v2 数据格式，同时用 `data/SPY_1min_2026-04-13.csv` 构造一份 full-day 390 根 bar 的测试 fixture（含合成 MA 和 VWAP），作为后续 Task 7 的主验收数据
- **验证**：页面加载后 canvas 正确尺寸，`console.log` 确认两份数据（seed_01 + full-day）均加载成功

### Task 2: Renderer（核心渲染，moomoo 风格）
- `buildRenderContext()` — 价格/成交量坐标变换
- `drawGrid()` — 极淡横向网格线（参照第三章视觉规范）
- `drawVolumeBars()` — 独立成交量区，半透明红绿柱，左上角 VOL 标签
- `drawCandles()` — 空心描边 HA K 线，实体宽 ~65% slot，影线 1px，保证呼吸感
- **绘制顺序**：先画 K 线（空心），再画均线，均线穿过 K 线实体时清晰可见
- `drawMALines()` — MA10/50/200 + VWAP
- `drawAxes()` — 右侧双轴（价格 + 百分比）、底部时间轴、日期分隔线
- `drawCrosshair()` — 白色虚线十字线 + 坐标轴上深色标签块
- `drawHighLowLabels()` — 日内最高/最低价标签（新增功能）
- `scheduleRender()` — RAF 防抖
- **深色主题 UI 适配**：除 canvas 绘制外，还需设计注解气泡、OHLC overlay、进度条、控制按钮等所有 DOM 元素的深色主题样式
- 复用旧版的坐标变换和 DPR 处理算法，视觉层面全部重写为券商风格
- **验证**：深色主题 K 线图渲染正确，视觉上接近 moomoo 截图效果；完成后立即截图对比审查小字号标签的可读性

### Task 3: InteractionManager
- 滚轮缩放（anchor-based）
- 拖拽平移（pointer capture）
- 鼠标追踪 → crosshair + OHLC overlay
- 进度条拖拽
- 键盘：Space（播放/暂停）、←→（步进前进/后退）、`1`（切 1m）、`5`（切 5m）— 与旧版一致
- **验证**：缩放、拖拽、十字线、OHLC 面板全部正常

### Task 4: PlaybackManager
- `play()` / `pause()` / `stepForward()` / `stepBack()`
- 速度控制（0.5x, 1x, 2x, 4x）
- 新 K 线动画（ease-out-quad）
- followMode 联动
- **不做** auto-pause（与教学解耦）
- **验证**：播放流畅，速度切换正常，新 K 线有缩放动画

### Task 5: AnnotationManager（被动信号标注）

**标注数据格式**：
```json
{
  "bar_index": 142,
  "timeframe": "1m",
  "title": "Reject MA10",
  "body": "得分 6/8",
  "type": "reject_ma10",
  "style": "red",
  "anchor_side": "top",
  "score": "6/8"
}
```

**渲染策略（已选定）**：采用 Canvas 图元 + Hover 详情面板的混合方案，而非旧版的 DOM 气泡重建：
- 在 Canvas 上绘制轻量 **pin 标记**（小三角 + 竖线），颜色按信号类型区分
- 高分信号（≥6/8）的 pin 标记更大/更亮，低分信号更小/更淡
- **Hover 时**显示详情浮层（DOM），含 title + body + score badge
- **Click** 触发 `engine.emit('annotation:click', anno)`
- 好处：Canvas pin 渲染性能稳定，不会因标注密集导致 DOM 重排或视觉拥挤

**scrollTo 契约**：
```javascript
engine.scrollTo({
  timeframe: '1m',     // 目标时间框架，如与当前不同则自动切换
  barIndex: 142,       // 目标 bar 在该时间框架下的索引
  highlight: true,     // 可选：高亮目标 bar（闪烁动画）
  center: true         // 可选：目标 bar 居中显示（默认 true）
});

// 简写（不切换时间框架）
engine.scrollTo(142);  // 等价于 { barIndex: 142, center: true }
```
- 当 `timeframe` 与当前不同时，先调用 `setTimeframe()` 切换，再定位
- 跳转后同步更新 `currentIndex`，播放从新位置继续

- **验证**：标注 pin 在正确位置渲染，hover 显示详情，click 触发回调；scrollTo 跨时间框架跳转正常；390 根 bar + 20 个标注无性能问题

### Task 6: 公共 API 封装 + 集成验证

> EventBus 已在 Task 1 实现，本 Task 聚焦 API 表面封装和跨模块集成。

- 事件列表确认：`data:loaded`, `viewport:changed`, `playback:tick`, `playback:state`, `annotation:click`, `bar:click`
- 公共 API 汇总：
  - `engine.loadData(json)` — 加载数据
  - `engine.setTimeframe('1m'|'5m')` — 切换时间框架
  - `engine.scrollTo({ timeframe, barIndex })` — 跳转（详见 Task 5 契约）
  - `engine.play()` / `pause()` / `setSpeed(n)` — 播放控制
  - `engine.on(event, callback)` / `engine.off(event, callback)` — 事件监听
  - `engine.getCurrentIndex()` — 获取当前位置
  - `engine.getTimeframe()` — 获取当前时间框架
  - `engine.destroy()` — 清理资源，需释放：RAF handle、所有事件监听器、pointer capture、interval/timeout、DOM 元素
- **集成验证**：在 demo 页面写一段外部 JS，依次调用所有 API，验证事件正确触发
- **验证**：外部 JS 可通过 API 控制引擎，destroy 后无内存泄漏（事件监听器全部移除）

### Task 7: 端到端验证

使用两份数据分别验证：

**Smoke test（seed_01，67 根 bar）**：快速回归基础功能
- [ ] K 线渲染正确（HA + MA + VWAP + Volume）
- [ ] 1m ↔ 5m 切换正常
- [ ] 播放 / 步进 / 速度切换正常

**Full-day 主验收（SPY 2026-04-13，390 根 bar + 合成标注）**：覆盖真实使用场景
- [ ] 全天 390 根 K 线渲染流畅，缩放/拖拽无卡顿
- [ ] 缩放到极限（10 根 / 390 根）后渲染和交互仍正常
- [ ] 十字线 + OHLC 面板 + 高低点标注正常
- [ ] 20 个合成标注同时可见，pin 标记不拥挤，hover 详情正常
- [ ] `scrollTo({ timeframe: '1m', barIndex: 200 })` 跳转 + 居中正常
- [ ] `scrollTo({ timeframe: '5m', barIndex: 30 })` 跨时间框架跳转正常
- [ ] 窗口 resize 自适应
- [ ] 外部 JS 通过 API 控制引擎（loadData → play → scrollTo → destroy 全链路）

**验收标准拆分**：
1. **行为对齐旧版**：缩放数学、坐标变换、bar 对齐、DPR 处理、时间框架切换逻辑
2. **视觉对齐 moomoo**：深色主题配色、K 线呼吸感、双轴坐标、十字线标签、整体券商质感

> 注意：v2 是全新深色主题，不与旧版浅色 sandbox 做视觉对比。行为层面复用旧版算法保证一致性。

---

## 六、数据格式（v2 引擎期望的输入）

```javascript
engine.loadData({
  bars_1m: [
    { t: "09:30", O, H, L, C, hO, hH, hL, hC, V, m10, m50, m200, vw },
    ...
  ],
  bars_5m: [...],          // 可选，不提供则禁用 5m 切换
  annotations_1m: [...],   // 可选
  annotations_5m: [...],   // 可选
  meta: {                  // 可选元数据
    title: "SPY 2026-04-13",
    ticker: "SPY",
    date: "2026-04-13"
  }
});
```

与旧版 bar 格式完全兼容，降低迁移成本。

---

## 七、关键文件

| 文件 | 作用 |
|------|------|
| `dist/kline-sandbox.html` | 旧版引擎（保留不动，参考渲染算法） |
| `dist/kline-engine-v2.html` | **新建** — v2 引擎 |
| `data/processed/teaching_segments.json` | seed_01 测试数据来源 |
| `data/SPY_1min_2026-04-13.csv` | full-day 390 bar 测试 fixture 来源 |
| `docs/planning/kline-engine-v2/assets/moomoo-spy-2026-04-13-1m.png` | **待存入** — moomoo 视觉验收参考图 |

---

## 八、执行顺序

```
Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7
骨架+Bus   渲染      交互      播放      标注    API封装   验收
```

严格线性，**每个 Task 由独立的 agent session 执行**，不允许一个 session 跑完全部 Task。

**Handoff 机制**：每个 Task 完成后，执行 agent 必须在 `docs/planning/kline-engine-v2/handoffs/` 下写一份交接文档 `task-N-handoff.md`，包含：

```markdown
# Task N Handoff

## 完成状态
- 已完成的具体工作项（逐条列出）
- 跳过或推迟的工作项（说明原因）

## 当前文件状态
- 修改/新建了哪些文件
- 当前代码行数

## 验证结果
- preview 截图或测试结果
- 已知问题（如有）

## 下一个 Task 的注意事项
- 前置条件是否已满足
- 需要特别注意的实现细节
- 本 Task 中发现的、可能影响后续 Task 的信息
```

新 agent session 启动时，须先阅读本计划 + 上一个 Task 的 handoff 文档，再开始工作。

**依赖关系说明**：
- EventBus 在 Task 1 实现，后续 Task 2–5 均可直接 `emit()`/`on()`
- Task 5（标注）的 `scrollTo()` 依赖 Task 1 的 ViewportManager + Task 2 的 Renderer
- Task 6 是 API 表面封装，不引入新逻辑，只做集成验证
- Task 7 的 full-day 测试数据在 Task 1 准备好

---

## 九、风险

| 风险 | 概率 | 缓解 |
|------|------|------|
| 重写后渲染行为与旧版不一致 | 中 | 复用旧版核心算法（坐标变换、slot 计算），逐步对比 |
| 单文件过大不好维护 | 低 | 用注释清晰分区，class 内部按模块组织，为后续拆分留接口 |
| 新 bar 动画重写可能闪烁 | 低 | 保持旧版 RAF + ease-out-quad 逻辑 |
| **全屏 390 根 K 线渲染超 16ms** | 中 | 性能预算：390 bar + 4 MA + Volume + 标注 pin 必须在 16ms 内完成（60fps）；Task 7 用 `performance.now()` 实测，超标则减少最大可见 bar 数或简化 MA 绘制 |
| **深色主题下小字号标签可读性不足** | 中 | Task 2 完成后立即截图审查，对比 moomoo 参考图，必要时调大字号或提高对比度 |
| **多标注拥挤导致视觉噪声** | 中 | 采用 canvas pin 而非 DOM 气泡（已在 Task 5 选定）；高密度区域自动折叠为计数标记（如 "×3"） |
| **缩放因子 1.08 手感不佳** | 低 | 已定义可调范围 [1.05, 1.15]，执行阶段可快速微调 |

---

## 十、变更记录

| 日期 | 变更 |
|------|------|
| 2026-04-14 | 初始版本 — K 线引擎 v2 重构计划 |
| 2026-04-14 | 新增第三章"视觉规范"，对标 moomoo 券商风格（深色主题、K 线呼吸感、双轴坐标、丝滑缩放） |
| 2026-04-14 | **R1 修订**：根据双 agent review 反馈修订 8 项问题 |
|  | — 修正背景描述：教学代码占比 40% → 15–20%，补充旧版架构的准确描述 |
|  | — 新增第二章"消费协议"：定义 `window.KlineEngine` + mount 协议 + 宿主职责 |
|  | — 色值固化为唯一取值，去掉二选一写法；缩放因子改为可调范围 [1.05, 1.15] |
|  | — EventBus 从 Task 6 提前到 Task 1，解除 Task 4/5 的执行依赖 |
|  | — scrollTo 契约完善：`scrollTo({ timeframe, barIndex, highlight, center })`，支持跨时间框架跳转 |
|  | — Task 5 标注渲染策略选定：Canvas pin + Hover 详情面板，替代旧版 DOM 气泡重建 |
|  | — Task 7 验收标准拆分为"行为对齐旧版 + 视觉对齐 moomoo"，消除自相矛盾；增加 full-day 390 bar 主验收数据 |
|  | — 风险表补充：性能预算（16ms/帧）、深色可读性、多标注拥挤 |
| 2026-04-14 | **R2 修订**：根据 r002 review 反馈修订 3 项问题 |
|  | — 样式交付闭环：构造函数自动注入 `<style data-kline-engine>`，宿主只需提取 `<script>` |
|  | — moomoo 参考图固化路径 `assets/moomoo-spy-2026-04-13-1m.png`，标注为执行前置条件 |
|  | — 删除 `theme: 'light'` 参数，当前仅支持 dark，light 作为后续扩展预留 |
|  | — 关键文件表补充 `SPY_1min_2026-04-13.csv` 和参考图 |
| 2026-04-14 | **R3 补充**：新增 Handoff 机制 — 每个 Task 由独立 agent session 执行，完成后写交接文档 |
