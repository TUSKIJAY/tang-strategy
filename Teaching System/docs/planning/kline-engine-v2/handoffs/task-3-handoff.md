# Task 3 Handoff

## 完成状态
- 已在 [kline-engine-v2.html](dist/kline-engine-v2.html) 内实现 Task 3 交互层。
- 已实现滚轮缩放：
  复用现有 `ViewportManager.applyZoom()`，按鼠标所在 bar 做 anchor-based zoom。
- 已实现拖拽平移：
  使用 pointer capture，拖动时更新 `viewStart` 和 `followMode`，不会重写 Task 2 的 render 数学。
- 已实现进度条拖拽：
  新增 scrubber DOM，支持 pointer down/move/up 跳转 `currentIndex`。
- 已实现键盘交互：
  `ArrowLeft` / `ArrowRight` 做单步前后移动；
  `1` / `5` 切换时间框架。
- `Space` 已接入为 `playback:toggle-requested` 事件请求，但没有实际播放逻辑，这一部分明确留给 Task 4。
- render 阶段已同步接入交互状态：
  `lastRenderContext`、hover/crosshair、scrubber UI 与当前 index 保持一致。

## 跳过或推迟
- 未实现 Task 4 的 `play()` / `pause()` / `stepForward()` / `stepBack()` / 速度控制 / 新 bar 动画。
- 未实现 Task 5 annotation pin / hover detail / click callback / `scrollTo()`。
- `Space` 目前只发事件，不触发实际播放，这是有意的任务边界控制。

## 当前文件状态
- 修改 [kline-engine-v2.html](dist/kline-engine-v2.html)：
  增加了 hover / wheel / drag / keyboard / scrubber 交互。
- 新建 [task-3-handoff.md](docs/planning/kline-engine-v2/handoffs/task-3-handoff.md)。
- 生成截图 [task3-interaction-check.png](docs/planning/kline-engine-v2/assets/task3-interaction-check.png) 用于 Task 3 交互回归。

## 验证结果
- 浏览器 smoke test：
  `python -m http.server` + Playwright 打开 demo 页，页面无 `pageerror`。
- seed fixture：
  默认 `seed` 场景下滚轮缩放生效，`zoomScale` 从 `1.00` 变为 `0.625`；
  由于 seed 数据总数仅 67 根且默认已从最左侧起视，拖拽不会产生额外平移，这是符合边界条件的。
- full-day fixture：
  切到 `Full Day` 后，滚轮缩放后再向右拖拽，`viewStart` 从 `301` 变为 `287`，`followMode` 由 `true` 变为 `false`，说明拖拽平移链路有效。
- 键盘验证：
  `5` 可切到 5m，切换后 `getTimeframe() === '5m'`，`getCurrentIndex() === 25`。
- scrubber 验证：
  点击进度条后，`currentIndex` 与右侧 label 同步更新，例如 `26 / 32`。

## 已知问题
- 目前没有播放管理器，所以 `Space` 只会发 `playback:toggle-requested` 事件，请勿把它当成已完成播放。
- 拖拽平移只有在可移动窗口存在时才会显著改变 `viewStart`；在 `seed` 的默认窗口边界里，这是正常现象。
- 还没有 progress bar 与播放时钟联动，因为 Task 4 未开始。

## 下一个 Task 的注意事项
- Task 4 直接消费现有键盘 `Space` 事件或把它接到 `play()/pause()` 即可，不需要重做键盘监听。
- 当前已有 `setCurrentIndex()` 和 scrubber UI，同步播放时只要推动 `currentIndex`，进度条会自然更新。
- 拖拽平移依赖 `lastRenderContext.slotWidth` 和 `ViewportManager.viewStart`，播放逻辑不要覆盖这条链路。
- 若 Task 4 增加自动跟随新 bar，请只在播放推进时切回 `followMode=true`，不要影响手动拖拽后的视窗状态。
