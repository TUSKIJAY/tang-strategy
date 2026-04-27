# Task 2 Handoff

## 完成状态
- 已在 `dist/kline-engine-v2.html` 内用正式 Renderer 替换 Task 1 的 placeholder render。
- 已实现 `buildRenderContext()`，基于现有 `ViewportManager` 输出价格区/成交量区坐标、slot 宽度、价格范围与体积范围。
- 已实现 `drawGrid()`、`drawVolumeBars()`、`drawCandles()`、`drawMALines()`、`drawAxes()`、`drawCrosshair()`、`drawHighLowLabels()`。
- 已沿用 Task 1 的 viewport / timeframe / DPR 数据链路，没有重新造缩放或时间映射逻辑。
- 已将深色主题 HUD/状态条/说明浮层接上正式渲染结果，当前 toolbar、overlay、status 与 canvas 风格统一为券商深色面板。
- 已增加最小 hover 状态采集，仅用于 Task 2 的 crosshair 渲染；未实现 Task 3 的 wheel/drag/keyboard/progress 交互。
- 已补充 Task 2 验证截图：`docs/planning/kline-engine-v2/assets/task2-render-check.png`。

## 跳过或推迟
- 未实现 Task 3 的滚轮缩放、拖拽平移、键盘快捷键和进度条拖拽。
- 未实现 Task 4 播放、Task 5 annotation pin、Task 6 公共 API 收口。
- 当前 K 线实体按计划保持空心描边，尚未进一步做更细的 wick/body 微调或券商级抗锯齿优化。

## 当前文件状态
- 修改 [kline-engine-v2.html](dist/kline-engine-v2.html)：
  Task 2 渲染逻辑与 hover crosshair 已落在同文件内。
- 新建 [task-2-handoff.md](docs/planning/kline-engine-v2/handoffs/task-2-handoff.md)。
- 生成截图 [task2-render-check.png](docs/planning/kline-engine-v2/assets/task2-render-check.png) 用于快速视觉复核。

## 验证结果
- 浏览器 smoke test：
  本地 `python -m http.server` + Playwright 打开 `dist/kline-engine-v2.html`，页面无 `pageerror`。
- seed fixture：
  默认加载 `seed`，`getTimeframe() === '1m'`，`getCurrentIndex() === 30`，HUD/右轴/成交量/高低点标签/crosshair 正常可见。
- full-day fixture：
  点击 `Full Day` 后能渲染 full-day 数据；再切 `5m` 后 `getTimeframe() === '5m'`，`getCurrentIndex() === 77`，无报错。
- 视觉对照：
  已对照 `assets/moomoo-spy-2026-04-13-1m.png` 复核整体方向：
  深色背景、极淡网格、右轴双列、底部时间轴、成交量独立区域、hover 十字线和高低点标签均已具备。
- 小字号可读性：
  当前右轴与底部时间标签在 1440px 视口下可读；若后续要进一步贴近 moomoo，优先微调的是右轴文字颜色/间距，而不是继续加粗网格。

## 已知问题
- 当前 crosshair 只依赖 hover，没有 Task 3 的交互管理器支持；离开 canvas 后 crosshair 会正常消失，但还没有拖拽/滚轮联动。
- 右侧百分比列在窄视口下会显得偏紧，Task 2 先保证信息完整，细节压缩留给后续联调。
- full-day 场景下当前默认视窗仍偏工程化，离最终“打开像券商软件”还有一些手感差距，主要是交互和动画层面未到位。

## 下一个 Task 的注意事项
- Task 3 直接复用当前 hover crosshair 状态即可，新增 wheel/drag 时不要重写 `buildRenderContext()`。
- 鼠标命中逻辑已经有 `barIndexForX()`，拖拽平移和 anchor-based zoom 应围绕它继续扩展。
- 当前 HUD/状态条已经消费了 focus bar，Task 3 增加交互时要注意不要让 hover bar 与播放 current bar 的优先级打架。
- 渲染函数已形成稳定顺序：
  `drawGrid -> drawVolumeBars -> drawCandles -> drawMALines -> drawAxes -> drawHighLowLabels -> drawCrosshair`。
  后续新增交互或动画不要轻易打乱这个顺序。
