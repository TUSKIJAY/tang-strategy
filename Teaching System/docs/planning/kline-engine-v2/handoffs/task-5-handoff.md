# Task 5 Handoff

## 完成状态
- 已在 `dist/kline-engine-v2.html` 内实现 Task 5 AnnotationManager 全部功能。
- 已实现 `drawAnnotationPins()`：
  Canvas 上绘制 pin 标记（竖线 + 三角箭头），颜色按 `anno.style` 映射（red/green/blue/orange/purple）。
  高分信号（score ≥ 6/8）pin 更大（7px）、更亮（alpha=1.0）；低分信号更小（5px）、更淡（alpha=0.6）。
  `anchor_side` 控制 pin 方向：`top` 在 K 线上方向上指，`bottom` 在下方向下指。
- 已实现 Hover 详情面板（DOM tooltip）：
  每帧重建 `_annoHitZones[]` 用于 hit testing。
  鼠标悬停 pin 时显示 `kline-engine__anno-tooltip`，含 title + body + score badge。
  Score badge 颜色跟随 pin 的 style 色系。
  Tooltip 自动避免溢出 viewport 边界。
- 已实现 Click → 事件发射：
  点击 pin → `engine.emit('annotation:click', anno)`。
  点击非 pin 区域 → `engine.emit('bar:click', { index, bar })`。
  拖拽后不触发 click（`_wasDragging` 防抖，阈值 3px）。
- 已实现 `scrollTo()` 契约（完全符合计划定义）：
  - `scrollTo(142)` 简写：跳转到 bar 142，居中显示。
  - `scrollTo({ barIndex, timeframe, highlight, center })` 完整形式。
  - 跨时间框架跳转：当 `timeframe` 与当前不同时自动切换。
  - `center: true`（默认）：目标 bar 居中，`currentIndex` 设为目标 bar。
  - `highlight: true`：目标 bar 闪烁蓝色高光动画 1.2 秒。
  - 跳转前自动 `pause()` 停止播放。
- 已修改 `ViewportManager.getVisibleWindow()`：
  `followMode=false` 时不再以 `currentIndex` 作为右边界，允许 viewport 显示任意位置数据。
  `followMode=true` 时行为不变（仍以 `currentIndex` 为右边界，保持播放模式语义）。
- 已在 `bootstrapDemo()` 中为 full-day fixture 注入 20 条合成标注（涵盖 red/green/blue/orange/purple 5 种颜色、top/bottom 两种方向、有/无 score 等变体），用于视觉验证和性能测试。

## 跳过或推迟
- 未实现高密度区域自动折叠（如 "×3" 计数标记）——计划标注为"中"风险，当前 20 个标注分布均匀无拥挤。
- 未实现 Task 6 公共 API 收口和集成验证。

## 当前文件状态
- 修改 [kline-engine-v2.html](dist/kline-engine-v2.html)：
  新增 AnnotationManager 方法约 200 行（drawAnnotationPins、hitTest、tooltip、scrollTo）。
  新增 CSS 样式约 40 行（anno-tooltip）。
  新增 DOM 元素 1 个（anno-tooltip）。
  修改 ViewportManager.getVisibleWindow（followMode=false 时不 clip maxEnd）。
  bootstrapDemo 新增 20 条合成标注注入。
- 新建 [task-5-handoff.md](docs/planning/kline-engine-v2/handoffs/task-5-handoff.md)。

## 验证结果
- 浏览器 smoke test：
  preview server + eval 打开 demo 页，页面无 pageerror、无 console error。
- 功能验证（全部通过）：
  1. Seed fixture 加载 3 条 1m 标注，visible range 内 1 条 pin 可见 ✓
  2. Full-day fixture 加载 20 条合成标注 ✓
  3. `scrollTo({ barIndex: 200, center: true })` → centerBar=200，精确居中 ✓
  4. `scrollTo(100)` → currentIndex=100，centerBar=100 ✓
  5. `scrollTo({ barIndex: 142, highlight: true })` → highlight 动画激活 ✓
  6. 跨时间框架 `scrollTo({ timeframe: '5m', barIndex: 30 })` → tf='5m', idx=30 ✓
  7. 边界 scrollTo(0) 和 scrollTo(389) 正常 ✓
  8. Hit zone 重建正确：bar 142 区域有 5 个 pin（100, 120, 142, 160, 180）✓
  9. Tooltip 显示 title="Reject MA10", body="得分 6/8", score="6/8" (red) ✓
  10. `_hideAnnoTooltip()` 正确隐藏 ✓
  11. `annotation:click` 事件正确触发 ✓
  12. `bar:click` 事件正确触发 ✓
  13. `_parseScore('6/8')` → {num:6, den:8}，`_isHighScore({score:'7/8'})` → true ✓
  14. Play after scrollTo 正常启动 ✓
  15. Destroy 后 container 清空 ✓

## 已知问题
- preview_screenshot 工具在此 canvas 页面上持续超时（与 Task 4 相同），但所有 eval 和 snapshot 验证正常。
- `scrollTo` 设置 `followMode=false` 后，用户手动拖拽到末尾时会自动切回 `followMode=true`（ViewportManager 自动恢复逻辑），这是已有行为，不影响功能。

## 下一个 Task 的注意事项
- Task 6 公共 API 汇总中，`scrollTo` 已完整实现，可直接集成验证。
- 事件列表确认：
  - `annotation:click` — payload 为完整 anno 对象
  - `bar:click` — payload 为 `{ index, bar }`
  - 这两个事件已在 Task 5 实现，Task 6 只需验证。
- `destroy()` 已清理播放和渲染资源。Tooltip DOM 会随 `container.innerHTML = ''` 一同移除，不需要额外清理。
- `getVisibleWindow` 的 followMode=false 不 clip maxEnd 的改动是向后兼容的——followMode=true 行为不变，所有既有交互（拖拽、缩放、播放）不受影响。
- Full-day 合成标注仅在 demo 页 `bootstrapDemo()` 中注入，不影响 JSON fixture 文件。Task 7 验收时可直接使用。
