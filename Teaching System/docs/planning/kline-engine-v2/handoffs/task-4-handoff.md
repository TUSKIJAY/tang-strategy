# Task 4 Handoff

## 完成状态
- 已在 `dist/kline-engine-v2.html` 内实现 Task 4 PlaybackManager 全部功能。
- 已实现 `play()` / `pause()` / `togglePlayback()`：
  play 启用 followMode 后通过 `setTimeout` 链逐 bar 推进；pause 清除定时器。
- 已实现 `stepForward()` / `stepBack()`：
  仅在非播放状态下生效；stepForward 带新 bar 缩放动画，stepBack 无动画（与旧版一致）。
- 已实现 `setSpeed(n)` / `getSpeed()`：
  支持 0.5x / 1x / 2x / 4x 四档，无效值回落到 1x；播放间隔 = `500 / speed` ms。
- 已实现新 K 线缩放动画 `_animateNewBar()`：
  150ms ease-out-quad，从中点向 OHLC 四端展开，与旧版 `animateNewBar()` 逻辑一致。
- 已在 `drawCandles()` 和 `drawVolumeBars()` 中集成 `_newBarAnim` 缩放因子。
- 已在 toolbar 中新增播放控件：
  `◀◀` step-back、`▶` play/pause（图标随状态切换 ▶/⏸）、`▶▶` step-forward、0.5x/1x/2x/4x 速度按钮（is-active 高亮）。
- 已将键盘 `Space` 从仅发事件改为直接调用 `togglePlayback()`。
- 已将 `ArrowLeft` / `ArrowRight` 在播放中屏蔽，防止播放与手动步进冲突。
- `loadData()` 和 `setTimeframe()` 调用时自动 `pause()`。
- `destroy()` 清理 playback timer、newBarAnim RAF handle。
- 已在 `updatePanels()` 状态栏中显示播放状态（playing/paused + speed）。
- 已更新 message 区提示文本。
- 事件发射：
  `playback:state` — play/pause/setSpeed 时触发，payload `{ playing, speed }`。
  `playback:tick` — 每次 bar 推进时触发，payload `{ index }`。

## 跳过或推迟
- 未实现 Task 5 annotation pin / hover detail / click callback / `scrollTo()`。
- 未实现 Task 6 公共 API 收口。
- 播放期间不与标注系统交互（无 auto-pause），这是计划中的设计决策。

## 当前文件状态
- 修改 [kline-engine-v2.html](dist/kline-engine-v2.html)：
  新增 PlaybackManager 方法约 130 行，drawCandles/drawVolumeBars 各增加 ~10 行动画逻辑，toolbar 增加 7 个按钮。
- 新建 [task-4-handoff.md](docs/planning/kline-engine-v2/handoffs/task-4-handoff.md)。

## 验证结果
- 浏览器 smoke test：
  preview server + eval 打开 demo 页，页面无 `pageerror`、无 console error。
- 功能验证（11 项全部通过）：
  1. 初始状态 `isPlaying()=false, speed=1, idx=30` ✓
  2. `stepForward()` → idx=31 ✓
  3. `stepBack()` → idx=30 ✓
  4. 播放中 `stepForward()` 为 no-op ✓
  5. `setSpeed(2)` 正确高亮 2x 按钮 ✓
  6. play/pause 图标切换 ▶ ↔ ⏸ ✓
  7. `loadData()` 自动停止播放 ✓
  8. `setTimeframe()` 自动停止播放 ✓
  9. `playback:state` 事件正确触发 ✓
  10. 数据末尾 `play()` 不启动 ✓
  11. 所有测试值非 undefined ✓
- 播放推进验证：
  `play()` 后 index 正常递增，`pause()` 后停止。
  headless 环境下 setTimeout 存在浏览器后台节流（最小 ~1s），这是已知的浏览器行为，前台标签页不受影响。
- 新 bar 动画：
  `_animateNewBar()` 产生 150ms ease-out-quad 缩放动画，candle 和 volume 同时缩放，与旧版一致。

## 已知问题
- preview_screenshot 工具在此 canvas 页面上持续超时，但 preview_eval / preview_snapshot / preview_console_logs 均正常。这是工具限制，非代码问题。
- 浏览器后台标签的 setTimeout 节流会导致 headless 测试中播放速度偏慢，在前台交互式使用时不受影响。

## 下一个 Task 的注意事项
- Task 5 可直接消费 `playback:tick` 和 `playback:state` 事件来感知播放状态。
- `_newBarAnim` 是 class 级属性，Task 5 的 annotation pin 绘制不需要考虑动画缩放，pin 始终在 bar 的最终价格位置渲染。
- `scrollTo()` 实现时应先调用 `pause()` 停止播放，再跳转到目标 bar，这样不会与播放状态冲突。
- 当前 `_advanceTo()` 设置 `followMode=true`，Task 5 的 `scrollTo()` 跳转后如果需要居中显示，应直接设置 `viewStart` 而非依赖 followMode。
- 播放控件已在 toolbar 右侧分组中，Task 5 如需增加标注相关按钮，建议放在同一分组或新建分组。
- `destroy()` 已清理 playback timer 和 animation RAF，Task 5 新增的资源也需在 destroy 中清理。
