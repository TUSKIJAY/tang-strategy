# Task 6 Handoff

## 完成状态
- 已审计公共 API 表面，确认所有计划中的方法和事件均已实现。
- 已在 demo 页面新增 `window.runIntegrationTest()` 集成验证函数，覆盖全部公共 API 和事件。
- 集成测试 **29/29 全部通过，0 失败**。

### 公共 API 清单（已确认）

| 方法 | 实现位置 | 状态 |
|------|----------|------|
| `engine.loadData(json)` | Task 1 | ✓ |
| `engine.setTimeframe('1m'\|'5m')` | Task 1 | ✓ |
| `engine.scrollTo({ timeframe, barIndex, highlight, center })` | Task 5 | ✓ |
| `engine.play()` | Task 4 | ✓ |
| `engine.pause()` | Task 4 | ✓ |
| `engine.setSpeed(n)` | Task 4 | ✓ |
| `engine.on(event, callback)` → returns unsubscribe fn | Task 1 | ✓ |
| `engine.off(event, callback)` | Task 1 | ✓ |
| `engine.getCurrentIndex()` | Task 1 | ✓ |
| `engine.getTimeframe()` | Task 1 | ✓ |
| `engine.destroy()` | Task 1+4+5 | ✓ |

额外方法（计划未列但已实现）：`isPlaying()`, `getSpeed()`, `stepForward()`, `stepBack()`, `togglePlayback()`

### 事件清单（已确认）

| 事件 | Payload | 触发时机 |
|------|---------|----------|
| `data:loaded` | `{ meta, timeframes, counts }` | `loadData()` |
| `viewport:changed` | `{ base, count, start, end, ... }` | 缩放/拖拽/scrollTo/播放推进 |
| `playback:tick` | `{ index }` | 每次 bar 推进（play/step） |
| `playback:state` | `{ playing, speed }` | play/pause/setSpeed |
| `annotation:click` | annotation object | 点击 pin 标记 |
| `bar:click` | `{ index, bar }` | 点击非 pin 区域 |

## 跳过或推迟
- 无。Task 6 范围为 API 封装 + 集成验证，全部完成。

## 当前文件状态
- 修改 [kline-engine-v2.html](dist/kline-engine-v2.html)：
  新增 `window.runIntegrationTest()` 函数约 130 行。
- 新建 [task-6-handoff.md](docs/planning/kline-engine-v2/handoffs/task-6-handoff.md)。

## 验证结果
- 集成测试 29/29 PASS：
  1. loadData returns summary ✓
  2. loadData sets timeframe to 1m ✓
  3. loadData sets initial index ✓
  4. data:loaded event fires ✓
  5. setTimeframe to 5m ✓
  6. setTimeframe back to 1m ✓
  7. viewport:changed fires on scrollTo ✓
  8. scrollTo(200) sets currentIndex ✓
  9. scrollTo({barIndex:150}) centers ✓
  10. scrollTo cross-tf switches to 5m ✓
  11. scrollTo cross-tf sets index ✓
  12. scrollTo highlight activates ✓
  13. play() starts playback ✓
  14. pause() stops playback ✓
  15. playback:state fires on play ✓
  16. playback:state fires on pause ✓
  17. setSpeed(4) sets speed ✓
  18. setSpeed(1) resets ✓
  19. stepForward advances index ✓
  20. stepBack decrements index ✓
  21. playback:tick fires on step ✓
  22. annotation:click event works ✓
  23. bar:click event works ✓
  24. on/off correctly binds and unbinds ✓
  25. on() returns working unsubscribe fn ✓
  26. destroy stops playback ✓
  27. destroy clears timer ✓
  28. destroy clears RAF ✓
  29. destroy clears DOM ✓

## 下一个 Task 的注意事项
- Task 7 端到端验收可直接调用 `window.runIntegrationTest()` 作为 API 回归测试。
- Task 7 的 full-day 主验收数据和 20 条合成标注已在 bootstrapDemo 中准备就绪。
- 所有 API 均经过集成测试验证，Task 7 应聚焦于视觉验收和性能验证。
