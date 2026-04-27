# Task 1 Handoff

## 完成状态
- 已新建 `dist/kline-engine-v2.html`，实现单文件 demo 骨架。
- 已实现 `window.KlineEngine` class，并满足 Task 1 最小 API：
  `new KlineEngine({ container })`、`loadData(json)`、`getTimeframe()`、`getCurrentIndex()`、`setTimeframe(tf)`、`on/off/emit`、`destroy()`。
- 已实现 `EventBus`、`DataManager`、`ViewportManager`。
- 已实现样式自动注入：首次实例化时向 `document.head` 注入 `<style data-kline-engine>`，重复实例化不重复注入。
- 已实现 canvas / overlay / controls DOM 骨架，并接上正确的 DPR / resize 处理。
- 已沿用旧版思路实现 viewport 数学：
  `getVisibleWindow()`、anchor-preserving `applyZoom()`、`setFollowMode()`。
- 已新建 `src/prepare_kline_engine_v2_data.py`，生成两份 v2 fixture：
  `kline-engine-v2-seed.json`、`kline-engine-v2-full-day.json`。
- 数据脚本会同步把 seed/full-day fixture 内联注入 `dist/kline-engine-v2.html`，保证 demo 页单文件可运行，不依赖运行时 fetch。
- `seed_01` 已做 v2 适配层，只保留运行时必要字段；annotation 已补 `timeframe`，已丢弃 `auto_pause`，`score` 统一为 `null` 或源值。
- full-day fixture 已改为以 `SPY_1min_2026-04-13.csv` 为单一 canonical source，`bars_5m` 由 1m 聚合派生。
- bars 已补绝对时间字段 `ts`；full-day 价格类字段保留到 4 位小数，不强制压到 2 位。
- `preheat_count` 未进入引擎逻辑；seed fixture 仅通过 `meta.initial_index_1m=30` / `meta.initial_index_5m=25` 保留 demo 初始定位信息。
- demo 页默认恢复加载 seed fixture，并在 console 记录 seed 与 full-day 均可成功 `loadData()`。

## 跳过或推迟
- 未实现 Task 2 Renderer 正式绘制，仅保留占位 render。
- 未实现 Task 3 交互管理器的 wheel / drag / crosshair / keyboard。
- 未实现 Task 4 播放、Task 5 注解 pin、Task 6 API 集成验证的完整范围。
- 未修改 `kline-sandbox.html`、`prepare_data.py`、`build_html.py`。

## 当前文件状态
- 新建 [kline-engine-v2.html](dist/kline-engine-v2.html)：
  884 行。
- 新建 [prepare_kline_engine_v2_data.py](src/prepare_kline_engine_v2_data.py)：
  290 行。
- 新建 [kline-engine-v2-seed.json](data/processed/kline-engine-v2-seed.json)：
  1760 行。
- 新建 [kline-engine-v2-full-day.json](data/processed/kline-engine-v2-full-day.json)：
  7975 行。
- 新建本交接文档 [task-1-handoff.md](docs/planning/kline-engine-v2/handoffs/task-1-handoff.md)。
- Git 状态说明：
  `prepare_kline_engine_v2_data.py` 与两份 fixture 在 `git status` 中显示为未跟踪文件。
- Git 状态说明：
  `dist/` 当前被 `.gitignore` 忽略，因此 `kline-engine-v2.html` 不会出现在普通 `git status` 里。

## 验证结果
- 数据脚本验证：
  运行 `python src/prepare_kline_engine_v2_data.py` 成功。
- 数据计数：
  seed fixture = `bars_1m: 67`、`bars_5m: 33`。
- 数据计数：
  full-day fixture = `bars_1m: 390`、`bars_5m: 78`。
- 浏览器 smoke test：
  通过本地 `python -m http.server` + Python Playwright headless 打开 demo 页，确认：
  `window.KlineEngine` 已暴露；
  `window.__klineEngineV2Fixtures` 同时包含 `seed` / `fullDay`；
  console 记录 `loadData(seed)` 与 `loadData(fullDay)` 均成功；
  默认恢复到 seed，`getTimeframe() === '1m'`，`getCurrentIndex() === 30`；
  canvas 实际尺寸为 `1360x560`，CSS 尺寸与 DPR 变换正常。
- API smoke test：
  在浏览器上下文中调用 `setTimeframe('5m')` 后，返回索引 `25`；
  随后调用 `viewportManager.applyZoom(20, ...)`，visible window 从 `0-25 / count 33` 变为 `6-25 / count 20`，说明缩放数学链路有效。

## 已知问题
- 当前 render 是占位版本，不具备正式 K 线、均线、成交量、坐标轴、十字线视觉效果。
- demo 仍建议经由本地 HTTP 打开做后续 Playwright 验证，但运行时已不依赖 `fetch` 读取本地 JSON。

## 下一个 Task 的注意事项
- Task 2 可以直接复用 `ViewportManager` 的 `getVisibleWindow()` / `applyZoom()` 结果，不要再引入 `preheat_count`、`auto_pause`、教学阈值 glow。
- Renderer 建议直接消费 bar 上的 `ts` 与 `t`，不要退回只看 `t`。
- `DataManager.switchTimeframe()` 当前已按 `ts` / 时间顺序做映射；Task 2/3 若增加 click / scrollTo，应基于这套映射继续扩展，不要另起一套时间对齐逻辑。
- demo 目前已有 fixture 切换按钮与 timeframe / zoom / follow 控件，Task 2 可以在此基础上接正式 render，不必重搭 DOM。
- 若后续需要纳入 git 变更，请注意 `dist/` 被忽略；是否调整提交流程需要由主协作者决定，本 Task 未改 `.gitignore`。
