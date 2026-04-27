# K 线引擎 v2 — 验收文档

> 验收日期：2026-04-14
> 计划文档：`docs/planning/kline-engine-v2/kline-engine-v2-plan.md`
> 产出文件：`dist/kline-engine-v2.html` (2361 行，单文件)

---

## 一、交付物清单

| 文件 | 行数 | 说明 |
|------|------|------|
| `dist/kline-engine-v2.html` | 2361 | v2 引擎主体，单文件 HTML，含完整 JS + CSS + demo |
| `src/prepare_kline_engine_v2_data.py` | 290 | 数据准备脚本 |
| `data/processed/kline-engine-v2-seed.json` | 1760 | Seed 测试数据 (67 bar) |
| `data/processed/kline-engine-v2-full-day.json` | 7975 | Full-day 测试数据 (390 bar) |
| `docs/planning/kline-engine-v2/handoffs/task-{1..7}-handoff.md` | 7 份 | 各 Task 交接文档 |

---

## 二、功能验收

### 2.1 消费协议 (Section 二)

| 验收项 | 状态 | 说明 |
|--------|------|------|
| `window.KlineEngine` class 暴露 | ✅ | 全局可用 |
| `new KlineEngine({ container })` 挂载 | ✅ | 仅需一个有宽高的 DOM 容器 |
| 样式自动注入 `<style data-kline-engine>` | ✅ | 首次实例化注入，幂等 |
| 宿主无需手动引入 CSS | ✅ | `<script>` 块包含全部逻辑 |
| 仅深色主题 | ✅ | 无 theme 参数，light 预留后续 |

### 2.2 视觉规范 (Section 三)

| 验收项 | 状态 | 说明 |
|--------|------|------|
| 深色配色 `#1a1a1a` / `#1e1e1e` | ✅ | 对标 moomoo 风格 |
| K 线空心描边（涨跌均空心） | ✅ | 影线分段绘制，不穿过实体 |
| 实体宽度 ~65% slot，等比缩放 | ✅ | `bodyWidth = max(2, slot*0.65)`，无上限，缩放时等比放大 |
| 影线 1px，不穿过实体 | ✅ | 上影线 high→body top，下影线 body bottom→low |
| 缩放时 K 线等比放大（宽+高） | ✅ | Y 轴仅依据可见 bar 的 H/L 计算，padding 2%，放大时 K 线充满图表 |
| 极淡网格 `rgba(255,255,255,0.06)` | ✅ | |
| 右侧双轴（价格 + 百分比） | ✅ | |
| 底部时间轴 + 日期分隔线 | ✅ | |
| 成交量独立区域（主图下方 ~20%） | ✅ | 半透明红绿柱 |
| 十字虚线 `dash [4,4]` + 深色标签块 | ✅ | |
| OHLC 面板左上角常驻 | ✅ | 含 O/H/L/C/涨跌/量 |
| 高低点价格标签 | ✅ | `drawHighLowLabels()` |
| MA10/50/200 + VWAP 均线 | ✅ | 橙/蓝/绿/紫 |
| 滚轮锚点缩放 | ✅ | 鼠标所在 bar 不动 |
| 拖拽 1:1 平移 | ✅ | pointer capture，无惯性 |
| 缩放范围 10~390 bar | ✅ | 实测 `zoom_min=10, zoom_max=390` |

### 2.3 架构 (Section 四)

| 模块 | 实现 Task | 状态 |
|------|-----------|------|
| EventBus (pub/sub) | Task 1 | ✅ `on/off/emit`，`on()` 返回 unsubscribe |
| DataManager | Task 1 | ✅ `loadData/getBars/getAnnotations/switchTimeframe` |
| ViewportManager | Task 1 | ✅ `zoom/pan/getVisibleWindow/followMode` |
| Renderer | Task 2 | ✅ 7 个 draw 方法 + `buildRenderContext` |
| InteractionManager | Task 3 | ✅ wheel/drag/crosshair/keyboard/scrubber |
| PlaybackManager | Task 4 | ✅ play/pause/step/speed/newBarAnim |
| AnnotationManager | Task 5 | ✅ canvas pin/hover tooltip/click/scrollTo |

### 2.4 公共 API (Section 六 Task 6)

| API | 状态 | 集成测试 |
|-----|------|----------|
| `engine.loadData(json)` | ✅ | PASS |
| `engine.setTimeframe('1m'\|'5m')` | ✅ | PASS |
| `engine.scrollTo({ timeframe, barIndex, highlight, center })` | ✅ | PASS |
| `engine.play()` / `pause()` / `setSpeed(n)` | ✅ | PASS |
| `engine.on(event, cb)` / `off(event, cb)` | ✅ | PASS |
| `engine.getCurrentIndex()` | ✅ | PASS |
| `engine.getTimeframe()` | ✅ | PASS |
| `engine.destroy()` | ✅ | PASS (timer/RAF/DOM 全清理) |

额外 API：`isPlaying()`, `getSpeed()`, `stepForward()`, `stepBack()`, `togglePlayback()`

### 2.5 事件列表

| 事件 | Payload | 触发时机 | 状态 |
|------|---------|----------|------|
| `data:loaded` | `{ meta, timeframes, counts }` | `loadData()` | ✅ |
| `viewport:changed` | `{ base, count, start, end, ... }` | 缩放/拖拽/scrollTo/播放 | ✅ |
| `playback:tick` | `{ index }` | 每次 bar 推进 | ✅ |
| `playback:state` | `{ playing, speed }` | play/pause/setSpeed | ✅ |
| `annotation:click` | annotation object | 点击 pin | ✅ |
| `bar:click` | `{ index, bar }` | 点击 K 线区域 | ✅ |

---

## 三、与旧版差异确认 (Section 四表格)

| 维度 | 旧版 sandbox | v2 引擎 | 验收 |
|------|-------------|---------|------|
| 数据加载 | 内嵌 JSON, hardcode 3 segment | `engine.loadData(json)` 外部传入 | ✅ |
| 标注系统 | auto-pause 阻断式 | 被动展示 + 可选高亮，不阻断播放 | ✅ |
| 标注颜色 | 固定 green/red/blue | 5 色映射 (red/green/blue/orange/purple) | ✅ |
| Preheat | 调暗前 N 根 | 不存在，全量展示 | ✅ |
| 信号交互 | 无 | pin 可点击 → `annotation:click`；`scrollTo()` | ✅ |
| 播放 | auto-pause 耦合 | 纯净播放，不与标注耦合 | ✅ |
| 时间框架 | 1m/5m + 时间对齐 | 保留，基于 `ts` 映射 | ✅ |
| 模块化 | 全局 state 过程式 | class 内部分模块，pub/sub 解耦 | ✅ |
| 外部 API | 无 | 8 个公共方法 + 6 个事件 | ✅ |

---

## 四、性能验收

| 场景 | 平均帧时间 | 最大帧时间 | 预算 (60fps) | 余量 |
|------|-----------|-----------|------------|------|
| 85 bars (默认视窗) | 0.39ms | 0.70ms | 16ms | 96% |
| 390 bars + 4 MA + Volume + 20 annotations | 0.88ms | 1.60ms | 16ms | 90% |
| 10 bars (最小缩放) | 0.17ms | 0.40ms | 16ms | 98% |

结论：**性能远超预算，60fps 完全保证。**

---

## 五、自动化测试

### `window.runIntegrationTest()` — 29 项全部通过

```
[PASS] loadData returns summary
[PASS] loadData sets timeframe to 1m
[PASS] loadData sets initial index
[PASS] data:loaded event fires
[PASS] setTimeframe to 5m
[PASS] setTimeframe back to 1m
[PASS] viewport:changed fires on scrollTo
[PASS] scrollTo(200) sets currentIndex
[PASS] scrollTo({barIndex:150}) centers
[PASS] scrollTo cross-tf switches to 5m
[PASS] scrollTo cross-tf sets index
[PASS] scrollTo highlight activates
[PASS] play() starts playback
[PASS] pause() stops playback
[PASS] playback:state fires on play
[PASS] playback:state fires on pause
[PASS] setSpeed(4) sets speed
[PASS] setSpeed(1) resets
[PASS] stepForward advances index
[PASS] stepBack decrements index
[PASS] playback:tick fires on step
[PASS] annotation:click event works
[PASS] bar:click event works
[PASS] on/off correctly binds and unbinds
[PASS] on() returns working unsubscribe fn
[PASS] destroy stops playback
[PASS] destroy clears timer
[PASS] destroy clears RAF
[PASS] destroy clears DOM
```

---

## 六、已知限制与后续

| 项目 | 说明 | 优先级 |
|------|------|--------|
| Light theme | 当前仅 dark，light 作为后续扩展 | 低 |
| 高密度标注折叠 | 未实现 "×3" 计数标记 | 中 (当前 20 条无拥挤) |
| 抗锯齿优化 | K 线 wick/body 可进一步微调 | 低 |
| `dist/` 被 `.gitignore` | `kline-engine-v2.html` 不在 git 跟踪中 | 需决策 |

---

## 七、执行记录

| Task | 内容 | 执行 Session | 状态 |
|------|------|-------------|------|
| Task 1 | 骨架 + EventBus + DataManager + ViewportManager | Session 1 | ✅ |
| Task 2 | Renderer (moomoo 风格核心渲染) | Session 2 | ✅ |
| Task 3 | InteractionManager (缩放/拖拽/键盘/进度条) | Session 3 | ✅ |
| Task 4 | PlaybackManager (播放/步进/速度/动画) | Session 4 | ✅ |
| Task 5 | AnnotationManager (pin/hover/click/scrollTo) | Session 4 | ✅ |
| Task 6 | API 封装 + 集成验证 (29/29) | Session 4 | ✅ |
| Task 7 | 端到端验收 | Session 4 | ✅ |
| 补丁 1 | K 线影线不穿过空心实体 | Session 4 | ✅ |
| 补丁 2 | 缩放等比放大（移除 bodyWidth 8px 上限） | Session 4 | ✅ |
| 补丁 3 | Y 轴更激进（仅用可见 bar H/L，padding 2%） | Session 4 | ✅ |

> Task 4–7 + 3 个补丁在同一个 session 中完成（上下文充足）。
> 全部 7 份交接文档位于 `docs/planning/kline-engine-v2/handoffs/`。

---

**验收结论：K 线引擎 v2 全部功能实现完毕，性能达标，API 表面完整，可供 daily-review Phase 2 集成使用。**
