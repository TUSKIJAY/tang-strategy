# Teaching System Handoff

> Last updated: 2026-04-26
> Scope: teaching-system implementation handoff.

## 当前状态

- 阶段：batch 10 已落地（Plan #9 Moomoo 式 MA/VWAP 数值图例）
- 当前主产品：`dist/Tang 策略教学系统.html`
- 下一步：Plan #10（策略口径同步：MA50 必须经市场验证后才可作为有效防线/关卡）。其余剩余项是 Plan #5（adapter 性能，conditional，仅在实测闪烁时进入）/ Plan #6（新模块训练，后置，等 MA10/Signal B 完整验证生产意见后再扩）。MA10 + Signal B 训练闭环 + 数据一致性 + 图表可用性 + 数值图例都稳定。
- 已结决策：`case_ma10_reject_2026_03_09` 数据对账走方案 C（idx=53/54 @ 11:33-11:34），见 batch 8 记录。

## 2026-04-26 待执行修改计划

下一个执行 agent 应按本节计划继续实现。执行前先重新核对当前工作树与数据字段，避免基于过期状态改动。

### Plan #1 — per-step checkpoint pills ✅ 已落地（batch 8）

背景：batch 7 已把训练页改成 replay drill，旧的 7-step quiz 不再作为主交互；但 `training/checkpoints.json` 中的 step/checkpoint 仍然是很好的解释来源。当前 reason chips 主要在决策/复盘语境中出现，缺少一个轻量的“当前这一步对应哪些证据”的扫描入口。

计划：

- 在训练右栏加入 per-step checkpoint pills，只作为证据提示和结构导航，不恢复旧 quiz。
- pills 来源优先用当前训练记录的 `decision_steps[].checkpoint_keys`，再映射到 `segment.derived.checkpoints` 的 label / passed / notes。
- 只展示有用户可读 label 或 notes 的 checkpoint；`forbidden_absent` 仍按 batch 7 规则过滤，避免噪音。
- 点击/悬停 pills 的行为先保持轻量：可复用现有 `checkpointToRanges` / `stepToHighlightRanges`，但不能让它变成强制答题步骤。
- 验收：切换训练 case 后，右栏能立即看到该 case 的关键证据 pills；选择 `等待 / 做多 / 做空 / 放弃` 的主路径不被打断。

### Plan #2 — reason review noise pass ✅ 已落地（batch 8）

背景：batch 7 open follow-up 指出，长方向案例里 `forbidden_absent` 可能以“遗漏理由”形式出现，语义上可解释，但对用户有点吵。

计划：

- 复核 `buildReasonGroups` / `reviewReasons` 中 no-trade filter 与 missed-reason 的关系。
- 明确区分两类东西：用户应该主动识别的入场理由，以及系统用于排除反例的过滤证据。
- 对标准做多/做空案例，默认不要把通过的 `forbidden_absent` 当作必须选择的理由；只在反例、放弃、或 failed filter 语境中强调。
- 验收：Support MA10 标准做多复盘不再因为没有选择“无禁做项”而显得像漏了关键理由；Reject / anti / no-trade 案例仍保留过滤证据说明。

### Plan #3 — 5m submit mapping UX clarification ✅ 已落地（batch 9）

背景：当前 5m 提交逻辑符合 plan：取 5m candle start ts，映射到第一根 `>= start_ts` 的 1m bar。因此在 11:35-11:39 的 5m candle 内提交会映射到 11:35，可能被判为信号前过早。实现是正确的，但用户直觉可能会认为自己是在“这根 5m K 内”做决定。

计划：

- 不改映射规则，先补解释层。
- 在 5m 提交后的 phase line / review text 中显示“5m 提交按该 5m K 起点映射到 1m #N”。
- 如后续用户仍觉得反直觉，再另开方案评估“映射到 5m candle 当前可见决策点/收盘点”的产品含义，不能静默改评分口径。
- 验收：5m 提交案例的 review 能明确解释为什么映射到某根 1m bar，以及为什么得到 `过早 / 窗口内 / 过晚`。

### Plan #4 — case/segment data reconciliation ✅ 已落地（batch 8 · 方案 C）

背景：`case_ma10_reject_2026_03_09` 的 case manifest `decision_bar.bar_index = 31`，但 `seed_03.segment.derived.signal_bar_index = 63`。batch 7 drill init 使用 segment-truth，因此训练流程正确；但数据层不一致会影响初始滚动、案例剧场、后续检索和维护信任。

计划：

- 先做数据对账，不直接改数值：列出 `cases/index.json` 中 decision_bar、`teaching_segments.json` 中 signal/confirm/checkpoint bars、以及实际 bars timestamp。
- 判断哪个字段是源事实：如果 segment 的 signal/checkpoint 与图上策略证据一致，则 case manifest 应回填；如果 case manifest 是教学判例的真正决策点，则 segment derived 需要重算。
- 对账结论写入计划/记录后再改数据，避免只为消除 diff 而改错事实。
- 验收：Reject MA10 标准例在 case page、training page、highlight/replay 初始化中指向同一组时间/index；不再出现 case 与 segment 互相矛盾。

### Plan #5 — adapter performance check

背景：多 case 切换时，React remount engine 可能在慢机器上闪烁。目前不是功能 blocker，但若用户接下来要高频训练，会影响手感。

计划：

- 先用浏览器观察 case tab 快速切换时的 canvas 销毁/重建、白屏时间和控制状态恢复。
- 如果闪烁明显，再评估把 engine 实例稳定在 `KlineView`/adapter 内，只在 case 切换时调用 `loadData()`。
- 不在没有实测问题前重构 adapter 生命周期。
- 验收：如果执行该项，hub/module/case/mistake 的 canvas 数量仍不泄漏，训练 case 切换不会残留旧 cutoff/highlight/playback 状态。

### Plan #6 — additional modules gating

背景：`candle_body_quality`, `vwap_distance_filter`, `moving_stop`, `background_5m` 仍缺训练 steps。当前优先级应低于 MA10 + Signal B 训练闭环稳定。

计划：

- 暂不扩写新模块训练，除非 MA10 / Signal B 的 replay drill、reason review、数据一致性都稳定。
- 新模块进入前，需要先补数据最小契约：case、segment、checkpoint label/notes、expected action、valid window。
- 验收：新增模块不能只加入口或空壳；至少能完成“隐藏未来 -> 提交 -> outcome -> review”的闭环。

### Plan #7 — global K-line MA/indicator selector ✅ 已落地（batch 9）

背景：所有出现 K 线的地方都需要统一处理均线/指标显示。当前 evidence/lab 图里已经能看到 MA10、MA50、MA200、VWAP 等按钮，但后续不能把某几条线写死在单个页面里；默认可以保持干净，只出现当前攻略中的重要均线。

计划：

- 适用范围：所有 `KlineView` 场景，包括 `mode="evidence"` 的 K线证据图、`mode="lab"` 的 K线回放训练台，以及其他后续出现完整 K 线的页面。
- 默认显示当前攻略/模块最重要的均线。例如 MA10 模块默认显示 MA10；如该攻略需要关键参考线，可同时默认显示 MA50 / MA200 / VWAP 等必要指标。
- 其他均线必须可选开关，不应从界面能力中消失。候选项包括 MA5 / MA10 / MA20 / MA30 / MA50 / MA60 / MA120 / MA200；VWAP 虽不是均线，但作为同类图表指标，可放在同一组控制中。
- 均线/指标数据优先从实盘 JSON 直接加载使用。执行前必须核对 `bars_1m` / `bars_5m` 或 engine payload 中是否已有对应字段。
- 如果某条均线无法显示，必须明确说明原因：原始 JSON 没有该字段、当前 timeframe 没有该字段、数据长度不足无法计算，或前端适配层没有映射。不能只在 UI 上静默隐藏。
- 缩略图如果为了空间只显示极简线条，也要遵守同一数据规则：默认显示攻略重点线；不提供完整开关时，应把完整可选能力留给 evidence/lab 图。
- 验收：证据图和训练图都能切换均线/指标；默认视图只显示攻略重点线；打开额外均线不破坏 replay drill、highlight、future cutoff、case 切换和页面布局。

### Plan #8 — K-line hover price card behavior ✅ 已落地（batch 9）

背景：当前价格小卡片会跟随鼠标，容易遮挡正在观察的 K 线、均线、右侧价格轴和底部时间轴；鼠标不在 K 线有效区域时也可能残留显示，干扰读图。

计划：

- 小卡片不再跟随鼠标坐标移动。它只允许出现在图表画面上方的安全区域，符合看盘习惯。
- 位置规则：鼠标在图表左侧时，小卡片放在右上安全区；鼠标在图表右侧时，小卡片放在左上安全区。
- 小卡片必须避开坐标轴数字，尤其不能遮挡右侧价格轴、右侧涨跌幅文字、底部时间轴数字和当前右侧价格读数。
- 小卡片只在鼠标命中 K 线绘图区内的有效 candle/bar 附近时出现。鼠标位于工具栏、均线按钮、底部控制区、价格轴外侧、空白区域或图表容器外时，不显示小卡片。
- 十字线和右侧价格标签可以继续跟随鼠标，但 hover card 本体应锚定到上方安全区，并与鼠标附近的 candle 保持距离。
- 实现时先做命中判断，再更新 hover state；不要让 hover state 由整张 canvas 或外层容器无差别触发。
- 验收：鼠标移出 K 线绘图区或停在非 candle 区域时，小卡片立即消失；小卡片始终只出现在上方；靠左 hover 时出现在右上，靠右 hover 时出现在左上；任何时候都不遮挡坐标轴数字和当前观察点。

### Plan #9 — Moomoo-style MA/VWAP value legend ✅ 已落地（batch 10）

背景：当前 MA/VWAP selector 只显示 MA5 / MA10 / MA20 / VWAP 等名称和开关状态。用户能看到线，但不能直接读出当前对应数值；Moomoo 的体验是在图表左上角直接展示 `MA5: 404.270`、`MA10: 403.193`、`VWAP: 399.832` 这类数值，读图效率更高。

计划：

- 在所有完整 K 线图场景补充 Moomoo 式数值图例：`MA5: xxx.xxx`、`MA10: xxx.xxx`、`MA20: xxx.xxx`、`VWAP: xxx.xxx`。适用范围至少包括 `KlineView mode="evidence"` 和 `mode="lab"`；mini 缩略图不需要显示数值。
- 图例颜色必须与对应线条颜色一致，文本应紧凑展示，允许自动换行，但不能挤压主图高度或遮挡坐标轴。
- 只对当前启用且数据存在的指标显示数值。关闭的指标可只保留开关 chip，不显示数值；disabled / 数据缺失指标继续使用 Plan #7 的缺失原因提示。
- 数值取值上下文：
  - 鼠标 hover 在有效 candle/bar 上时，显示 hover bar 对应的 MA/VWAP 值。
  - 没有有效 hover 时，显示当前图表 focus bar 的值：训练 replay 用 `currentIndex` / 当前可见决策点；evidence/case 图用 engine 当前 index 或最后一个可见 bar。
  - replay hidden-future 阶段不得从 reveal cutoff 之后的 bar 取值，避免用图例泄露未来走势。
- 数据源优先使用实盘 JSON 已加载到 engine payload 的 bar 字段，不为展示图例临时重算均线。若当前 bar 对某条指标值为 `null/undefined`，该项显示为不可用或省略，并保留可解释原因。
- 数值格式与价格轴保持一致，建议 3 位小数；VWAP 与 MA 使用同一格式。不要用涨跌幅颜色表示 MA 值，颜色只表示线条身份。
- 验收：打开 MA10 / MA20 / MA30 / MA50 / MA200 / VWAP 后，图表能显示对应当前 bar 数值；hover 不同 K 线时数值同步变化；鼠标移出有效区域时回到当前 focus bar 数值；训练页 hidden-future 状态下不会显示未来 bar 的均线值；证据图和训练图行为一致。

### Plan #10 — strategy rule sync: validated key levels / MA50 context

背景：`docs/tang-strategy-notes.md` 已更新为 2026-04-26 合并重写版。最重要的新口径是：MA50 不能被机械当成支撑、防线或关卡，必须先看它之前是否被市场验证过。即使当前实现仍以 `prepare_data.py` 为权威，教学系统也需要同步规则说明和 checkpoint 语义，避免继续教成“碰到 MA50 就天然有效”。

计划：

- 先做文档/规则口径同步，不直接重写信号检测算法。当前 MA10 / Signal B replay drill 主流程仍成立，不能因为策略口径更新而贸然改变已验证评分。
- 更新 `rules/compiled/index.json` 的相关规则说明：
  - `support_ma10` / `reject_ma10`：保留 MA10 触发核心，但补充“MA50/VWAP/MA200 等关键线是否有效，取决于前序争议、支撑/压制或回测确认”。
  - `vwap_distance_filter`：从“关卡距离”扩展为“被市场验证过的关键关卡距离”，避免把所有均线都当同等强度的阻力/支撑。
  - `background_5m`：补充“5min 优先，但关键位仍需结合 1min 前序反应确认”。
- 更新训练/复盘文案：
  - `training/checkpoints.json` 中涉及 MA50 / MA200 / VWAP 的 explanation，应从“碰到/未破某线”改成“该线是否已被前面价格验证”。
  - `cases/index.json` 的 lesson 可逐步补一句“为什么这里的 MA50 / VWAP / MA200 是有效关卡，或为什么不能机械当关卡”。
- 设计后续数据契约，不要求第一步马上实现：
  - 候选 checkpoint key：`key_level_validated` / `prior_reaction_ok` / `ma50_validated`。
  - 候选字段：关键位类型（MA50/MA200/VWAP/5m MA10）、前序测试次数、最近一次支撑/压制时间、是否有反向回测失败/成功、人工备注。
  - 这些字段可先作为 manual patch / explanation 层进入 `training/checkpoints.json` 或 case notes，等样本稳定后再进入 `prepare_data.py` 自动派生。
- 开盘 30 分钟口径保持双轨：
  - 人工交易口径：从“绝对禁入”改为“慎入”。
  - 当前项目实现：`signal_time < 10:00` 仍进入 `forbidden_flags`，除 `opening_gap` 专案外不把 10:00 前信号标成普通可交易信号。
  - 若未来要把“慎入”做进系统，应新增 risk level / caution label，而不是直接取消 `forbidden_flags`。
- 明确当前非目标：不直接把“MA50 未验证”做成自动判错；不直接取消开盘 30 分钟硬禁入；不直接改 `prepare_data.py` 的核心检测阈值，除非先有可复现字段和验收样本。
- 验收：
  - 规则库和训练文案不再把 MA50 描述成固定防线。
  - 系统说明能区分“人工复盘口径”和“项目实现口径”。
  - 新增数据契约草案能让后续 agent 明确如何采集/标注“前序争议位置 / 被市场验证过的关键位”。
  - 现有 MA10 / Signal B 训练页行为不因文案同步而回归或变成未验证状态。

### 剩余推荐执行顺序

1. ~~Plan #9 先做，作为 Plan #7 已落地 MA selector 的自然补充。~~ ✅ batch 10 落地
2. Plan #10 先做策略口径同步，优先更新规则说明、训练文案和数据契约草案，暂不改核心检测算法。
3. Plan #5 只在实测 case 切换闪烁明显时进入。
4. Plan #6 等 MA10/Signal B 稳定后再扩展；当前仍后置。

### 执行边界 / 非目标

- 不恢复旧 7-step quiz。
- 不恢复 `Aggregate5mBand`。
- 不新增后端。
- 不改全局 K-line 终端交互。
- ~~不在没有数据对账结论前直接改 `case_ma10_reject_2026_03_09` 的 bar index。~~ ✅ 已完成（batch 8 方案 C，idx=53/54 @ 11:33-11:34）。
- 不在没有核对实盘 JSON 字段前假设所有均线都已经可用。

## 2026-04-26 batch 10 — Moomoo 式 MA/VWAP 数值图例 (Plan #9)

落地 Plan #9：在 evidence/lab 模式的 MA 图例旁直接展示当前 bar 的 MA/VWAP 数值，hover 移到具体 K 时切换为 hover bar 的值，鼠标移开 K 线绘图区时回退到 focus bar，replay hidden-future 阶段不会泄露 cutoff 之后的均线值。

### 引擎层 — `hover:bar` 事件 + getter

之前引擎只 emit `playback:tick / viewport:changed / ma:visibility` 等，没有暴露"鼠标当前在哪根 candle 上"。Plan #9 要求 hover 切换数值，但又不希望前端每帧都跑 hit-test，所以在引擎渲染管线里加一次去抖：

- `state init`：`this._lastEmittedHoverIndex = null` + `this._lastEmittedHoverTf = null`
- `render()` 的 hoveredIndex 计算后立刻判断 cutoff（hover 索引若 > cutoff 则强制 null），并跟 `_lastEmittedHoverIndex/Tf` 比较；任一变化才 `emit('hover:bar', { index, timeframe })`。null→idx / idx→null / idx_a→idx_b / tf 变化都会触发，连续同帧不变则不发。
- 新增 public method `getHoveredBarIndex()`（返回 `_lastEmittedHoverIndex`），与 event 一致；外部需要主动查询时用。
- `kline-engine-v2.html` 同步镜像（hover:bar 9 处出现，与 `kline-engine.js` parity 一致），让 demo `runIntegrationTest()` 仍可作为引擎逻辑的 ground truth。

### 适配层 — adapter forwards `onHoverChange`

`KlineEngineAdapter` 新增 prop `onHoverChange`，订阅 `engine.on('hover:bar', cb)`，把 `{ index, timeframe }` 透出给上层 React 组件。卸载时 `offHover()` 一起清。`onPlaybackChange / onMaVisibilityChange` 等已存在的 callback 维持不动。

### React 层 — `KlineView` + `MaLegend`

`KlineView`：
- 新增 state `hoverState = { index, timeframe }`，case/segment/mode 切换时 reset 为 `{ index: null, timeframe: null }`，避免上一段 segment 的 hover idx 在新 segment 上误读。
- 新增 helper `resolveCutoffForTf(revealCutoff, currentTf, fallbackTf)`：处理 `revealCutoff` prop 的多形态（`null | number | { tf, idx } | array`），返回当前 tf 对应的 cutoff number 或 null。
- 新增 useMemo `legendBar`：
  1. 取当前 tf 对应的 `bars_1m / bars_5m`
  2. 如果 hover 在同 tf，使用 `bars[hoverState.index]`
  3. 否则取 `playback.index`，再按 cutoff 做 `min(focusIdx, cutoff)` 兜底（防御 — 引擎已在 visible.end 处 clamp，但避免任何 React 端单独读 stale focus bar）
  4. 边界 clamp 到 `[0, bars.length - 1]`
- 把 `legendBar` 和 `source: 'hover'|'focus'` 一起传给 `MaLegend`。

`MaLegend`：
- 新 helper `formatMaValue(v)`：3 位小数 (`v.toFixed(3)`)，与价格轴的精度对齐。
- 新增 props `bar` + `source`：active chip 在 `bar[ma.key]` 是有限数字时显示数值；inactive 或缺数据的 chip 不显示数值。数值用 `tabular-nums` + `JetBrains Mono` 风格的 `Space Grotesk` 字体；颜色与对应 MA 线条颜色一致（`style={{ color: ma.color }}`）。
- "均线" 字样的 tooltip 根据 source 提示当前数值来自 hover 还是 focus。
- 整体布局保持原有 wrap / disabled chip 行为，没有挤压主图。

### Cache-bust

`Tang 策略教学系统.html` script `?v=20260426b → 20260426c`，让 babel-standalone 重取改过的 `shared.jsx`（`KlineView` + `MaLegend` + `KlineEngineAdapter`）。引擎 JS / HTML 是直接 `<script src>`，浏览器自然按 mtime 取新版。

### Browser verification

| Acceptance | Result |
|---|---|
| `#case/case_ma10_support_2026_01_07` 默认 focus=31，legend 显示 `MA10 692.310 / MA50 692.470 / MA200 692.150 / VWAP 692.130`，与 `seed_01.bars_1m[31]` 一致 | ✓ |
| Hover 移到画面 4 个不同位置 → idx 11/16/21/27 → 4 套不同的 `MA10/MA50/MA200/VWAP` 数值，每套都与 segment 对应 bar 字段精确一致 | ✓ |
| Mouseleave 后 legend 恢复 focus 值（`MA10 692.310`）；`getHoveredBarIndex()` 返回 null | ✓ |
| `#training/ma10` (replay drill) cutoff_1m=19，focus 也=19，legend 显示 `MA10 692.500 / MA50 692.390 / MA200 692.130 / VWAP 692.120 / MA5 692.391`，与 `bars_1m[19]` 字段一致 | ✓ |
| Replay drill 阶段 hover 永远 ≤ cutoff（引擎自身 visible.end clamp + emission cutoff 双重防御）；hover 在画面右侧空白也 ≤ cutoff，不显示未来 bar 的均线值 | ✓ |
| MaLegend disabled chip（MA20/MA30/MA60/MA120 在 segment 中存在数据但默认关闭）只显示 label，不显示数值；点开后立即显示 (`MA5: 692.391` 例) | ✓ |
| Disabled-by-data chip 行为不变（无数据时灰色 + tooltip 提示） | ✓ |
| 数值字号 11px、颜色匹配 ma.color、`tabular-nums` 等宽，wrap 不挤压主图 | ✓ |
| `kline-engine-v2.html` `runIntegrationTest()` 29/29 PASS（引擎 hover 模块新加未破坏既有契约） | ✓ |

合成 mousemove 事件测试时发现 preview 里 rAF 节流明显，需要 `live.render()` 强制提交后才会 emit；真实用户连续移动鼠标时 rAF 会被持续触发，不存在该问题。

### Files touched

- `dist/kline-engine/kline-engine.js` — `_lastEmittedHoverIndex/Tf` 状态；render() 内 hover index cutoff clamp + transition emit；新 `getHoveredBarIndex()`
- `dist/kline-engine/kline-engine-v2.html` — 镜像同样改动（demo / parity）
- `dist/shared.jsx` — `KlineEngineAdapter` 加 `onHoverChange` prop + `hover:bar` 监听；新 helper `resolveCutoffForTf` + `formatMaValue`；`KlineView` 加 `hoverState` + `legendBar` useMemo + 重置；`MaLegend` 加 `bar` / `source` props 渲染数值
- `dist/Tang 策略教学系统.html` — cache-bust `?v=20260426b → 20260426c`
- `docs/planning/teaching-system/HANDOFF.md` — 本批次记录 + 标记 Plan #9 完成 + 9 MA rebuild 已完成的修正

### Open follow-ups (not in this batch)

- Plan #5 (adapter 性能) 仍 conditional
- Plan #6 (新模块训练) 仍后置
- mini 缩略图（hub）按 Plan #9 范围明确不显示数值，保持现状不变

## 2026-04-26 batch 9 — K线 hover card 重构 + MA 选择器全验收 + 5m 映射解释

Three Plan items landed: #8 (hover card), #7 (MA selector — most was already in place from batch 2/3, this batch ran the full acceptance and refined disabled tooltip), #3 (5m → 1m mapping copy).

### Plan #8 — hover card 行为重写

之前 hover card 跟着鼠标坐标移动，容易遮挡 K 线 / 坐标轴 / 当前价格读数；鼠标在工具栏或外侧空白也会残留 card。

改 `_updateHoverCard()` + `_showHoverCard()`：

- **严格命中判断**：`hover.x` 必须在 `[area.x, chartRight]` 之间，`hover.y` 必须在 `[area.y, volumeY + volumeHeight]` 之间。鼠标在右侧坐标轴 / 底部时间轴 / 工具栏 / 上下空白 → 直接 `_hideHoverCard()`。十字线 + 右侧价格标签的鼠标跟随路径不变（plan 允许）。
- **位置锚定上方安全区**：`top = chartArea.y + 8`（图表绘图区顶部 + 8px 安全间隙），不再跟 `screenY` 跑。
- **左右镜像**：以 chart drawing area 中心 `(area.x + chartRight) / 2` 划分；鼠标在左半边 → card 贴右上 `left = chartRight - cardWidth - 8`；鼠标在右半边 → card 贴左上 `left = area.x + 8`。Defensive viewport clamp 保留作 fallback。
- API: `_showHoverCard(bar, hoverX)`，`screenY` 参数移除。

引擎 source `kline-engine.js` + 镜像 `kline-engine-v2.html` 同步改动（保持 parity）。`runIntegrationTest()` 29/29 PASS 无回归。

### Plan #7 — MA/指标选择器（batch 2/3 已实现 + batch 9 验收 + tooltip 细化）

batch 2 / batch 3 已实现：
- `MA_LEGEND` 9 个 key + 颜色与引擎 toolbar 同步
- `MaLegend` 组件含 active/disabled 双态，disabled 用淡色 + cursor:not-allowed
- `computeAvailableMaSet(segment)` 探测每个 MA key 是否在 `bars_1m`/`bars_5m` 实际有数据
- `KlineView` 在 evidence/lab 模式都渲染 MaLegend，mini 模式只画 m10
- `KlineEngineAdapter.applyTeachingChrome` 在 case load 时按 `CASE_RELEVANT_MA[moduleId]` prune 默认显示集
- `engineControls.setMaOn(key, on)` 直写 `engine.maVisibility[key]` + emit `ma:visibility` 事件

batch 9 完成 plan 验收（全绿）：

| Acceptance | Result |
|---|---|
| Lab 训练页 toggle MA50 off → drill cutoff 不变 | ✓ cutoff_1m 维持 19 |
| Lab 切换 case (support → reject) → MA 重置默认 (m10/m50/m200/vw) + cutoff 重算 | ✓ cutoff_1m 41 / cutoff_5m 22 |
| Lab toggle MA50 后点 pill「K线触及 MA10」→ highlight `[1m: 53,53]` 同时 m50=false | ✓ |
| Evidence 页 (#case/...) toggle MA + 点 checkpoint → highlight + MA toggle 共存 | ✓ |
| Evidence 页 disabled span 不可点 (cursor:not-allowed, tag=SPAN) | ✓ |
| Mini 缩略图 (#hub) 6 SVG 默认只画 m10 (stroke=#8B9A6D) | ✓ canvas_count=0 |
| MaLegend 布局 wrap 不挤压 (~60px 高 / 9 chip) | ✓ |

batch 9 唯一新增改动：`MaLegend` disabled chip tooltip 文案细化。

之前是泛文案"该均线在当前教学切片中暂无数据"。plan §7 要求"明确说明原因，不能静默隐藏"。改为针对当前唯一可能原因（segment JSON 不含字段）说明：`教学切片 JSON 的 bars_1m / bars_5m 不含 MA{X} 字段。重跑 slice_teaching_segment.py 可补充。`

`MaLegend` 同时新增 `unavailableReasons` 可选 prop，未来如果区分多种原因（5m 缺字段 / 数据长度不足 / adapter 未映射）可由 caller 传具体 reason map 覆盖。

**已知后续 work（不在 plan #7 范围）**：当前 15 个 segments 实际只含 m10/m50/m200/vw 4 个 MA 字段（HANDOFF batch 3 #9 提到的 9 MA rebuild 看似没落入 git，所有 segments 仍是 4 个 MA）。MA5/MA20/MA30/MA60/MA120 在所有 case 永远显示为 disabled chip。要让用户能真正切到这些线，需重跑 `slice_teaching_segment.py` 让全部 9 MA 进 segment。这属于数据 pipeline 工作，与 plan #7 前端选择器解耦。

> **2026-04-26 后续修正**：上述 9 MA rebuild 已通过一次性 patch 落地（commit `6a2e823 fix(teaching-data): 教学切片 backfill 5 条均线字段`）。15 segments / 1265 1m bars / 519 5m bars 全部按 ts join 对应 daily `SPY_<date>.json` 把 m5/m20/m30/m60/m120/m250 backfill 完成；`derived` 严格保留不变。当前 MaLegend 的 9 个 chip 全部可点击。Slicer 本身未改（之前问题是历史 segments 的字段而非 slicer 逻辑），未来用 `slice_teaching_segment.py` 切新 segment 会自然带上全部 MA。

### Plan #3 — 5m → 1m 映射 UX 解释

不改映射规则（仍是 5m 提交按 5m bar **起点 ts** 映射到第一根 `>= start_ts` 的 1m bar）。新增解释层让用户不再误以为"在这根 5m K 内 = 在它代表的 5min 时段内任意一刻"。

实现：

- `handleSubmit` 在提交时记录 `submittedTimeframe = playbackSnap.timeframe === '5m' ? '5m' : '1m'` + `submitted5mIndex = (5m 时的) playbackSnap.index`。
- 这两个字段同时传入 `buildReviewText` 和写进 `reviewState`。
- `buildReviewText` 在 5m 提交分支追加：`5m 提交按该 5m K 起点 {fiveStartT} 映射到 1m #{submittedIndex} ({mappedT})；评分以这根 1m bar 的位置为准。`
- TrainingPage 当前状态卡片在 phase=submitted/review 且是 5m 提交时显示一行：`5m 提交按 11:20 起点映射到 1m #15 (11:20)`，与 review text 形成两处呼应。

1m 提交路径完全不变，只在 5m 提交时显示这两行。

### Cache-bust + tooling

`Tang 策略教学系统.html` script `?v=20260426a → 20260426b`，让 babel-standalone 重取改过的 `shared.jsx` (MaLegend tooltip) + `pages-2.jsx` (5m mapping)。

### Files touched

- `dist/kline-engine/kline-engine.js` — `_updateHoverCard` 严格命中、`_showHoverCard` 锚定上方安全区 + 左右镜像
- `dist/kline-engine/kline-engine-v2.html` — 镜像同样改动
- `dist/shared.jsx` — `MaLegend` 加 `unavailableReasons` prop + 细化默认 tooltip 文案
- `dist/pages-2.jsx` — `buildReviewText` 加 5m mapping 分支；`handleSubmit` 记录 `submittedTimeframe` + `submitted5mIndex`；当前状态卡片加 5m mapping 一行
- `dist/Tang 策略教学系统.html` — cache-bust `?v=20260426a → 20260426b`

### Open follow-ups (not in this batch)

- ~~teaching_segments.json 9 MA rebuild（数据 pipeline 工作，让 MA5/20/30/60/120 真正可切）~~ ✅ 已落地 commit `6a2e823`，所有 segments 现含 m5/m10/m20/m30/m50/m60/m120/m200/m250 + vw
- Plan #5 (adapter 性能) 仍 conditional
- Plan #6 (新模块) 仍后置

## 2026-04-26 batch 8 — Data reconciliation + per-step pills + reason noise pass

Three Plan items from `2026-04-26 待执行修改计划` landed: #4 (data reconciliation), #1 (per-step checkpoint pills), #2 (reason review noise pass).

### Plan #4 — case/segment data reconciliation (方案 C, idx=53/54 @ 11:33-11:34)

调研后发现 `case_ma10_reject_2026_03_09` 三层数据**全部互相矛盾**：

- case manifest 自己 `bar_index=31` 与 `time="11:09"` 不一致（实际 `bars_1m[31]` 是 11:11，对应 11:09 的是 idx=29）
- segment `signal_bar_index=63` 是算法跑出的"最后一个上影靠近 MA10 的 bar"，但 idx=63 (11:43) 是 GREEN HA，与 lesson 文案"反抽后压回，确认 K 给出继续做空依据"完全不符（绿 HA 是反弹起点不是压回）
- 真正符合教学叙事的位置在 idx=53 (11:33)：HA 实体首次跌破 MA10（hC=669.20 < m10=669.53），前序 11:28-11:32 反抽至高点 669.85 后被压回，下一根 idx=54 (11:34) 继续 RED 延续下行

走方案 C 全层对账到 idx=53/54：

- `cases/index.json#case_ma10_reject_2026_03_09`：`bar_index 31→53`, `time 11:09→11:33`, `window 10:38-11:42→11:00-11:42`, `stop "信号K高点上方"→"信号K反抽高点上方（约 669.85）"`, `lesson` 重写
- `data/processed/teaching_segments.json#seed_03.derived`：`signal_bar_index 63→53`, `stop_price 668.91→669.85`, `rule_events[0].bar_index 63→53` + reason 重写, 5 个 checkpoint (touch_ma10/body_not_cross/confirm_bar/stop_defined/reward_ok) 的 `bar_index` + `reason` 重写, `reward_ok.metrics.barrier_distance_pct 0.38→0.51`, `stop_defined.metrics.stop_price 668.91→669.85`
- `training/checkpoints.json` reject case：两处 explanation 数值同步 (0.38%→0.51%, 668.91→669.85)

数据一致性脚本验证 `case.bar_index ↔ segment.signal_bar_index ↔ bars_1m[idx].ts` 三方一致。

### Plan #2 — `reviewReasons.misses` 仅来自 visible reason chips

`buildReasonGroups` 已经 filter 掉无 flags 且 `passed=true` 的 `forbidden_absent`，但 `reviewReasons.misses` 是直接遍历 `segment.derived.checkpoints` 全集，所以 standard long/short case 的 review 仍把 `forbidden_absent` 列为"遗漏理由"。

改 `reviewReasons` 复用 `buildReasonGroups` 输出的 visible items，misses 只从可见 chips 里挑没选中的。anti / no-trade case 的 `forbidden_absent`（`passed=false` 或带 flags）仍保留过滤证据说明。

### Plan #1 — per-step checkpoint pills（决策步骤 · 证据导航 卡片）

新增 helper `buildDecisionStepPills(caseObj, segment)`：从 `TRAINING_ITEMS` 取当前 case 的 `record.steps`，每 step 映射到 `segment.derived.checkpoints`，过滤规则与 `buildReasonGroups` 同（无 label/notes 跳过；`forbidden_absent` 无 flags 且 passed=true 跳过）。

新增 state `pillHighlightKey`（与 `selectedReasonKeys` 完全分离 — pill **不参与计分**）+ useMemo `pillHighlightRanges` 通过 `window.checkpointToRanges` 解析 → 引擎 highlight。`highlightRangesProp` 集成：pill highlight 优先级最高，覆盖 replay 阶段的 clean state 与 review 阶段的默认 [signal..confirm window] + submitted marker。

新增右栏卡片"决策步骤 · 证据导航"，位于"理由（多选）"卡片之上：每 step 一行（step 名称 + pills 横排）；pill 选中态高对比；右上角"清除高亮"按钮（仅在有 pillHighlight 时出现）。case/module 切换 → `pillHighlightKey` + `pillHighlightRanges` 自动 reset。

设计上 pills 卡片解决 batch 7 open follow-up "切换 case 时缺少证据扫描入口"；同时刻意与 reason chips 分层：pills 是结构性导航（按训练步骤），chips 是语义性多选（按 background/trigger/risk/no_trade）。两者共享 checkpoint 数据但交互目的不同。

### Cache-bust + tooling

- `Tang 策略教学系统.html` script `?v=20260425f → 20260426a`
- `.claude/launch.json` 改为 `bash -c "exec python3 -m http.server \"${PORT:-8765}\""` 配合 `autoPort: true`，让 preview MCP 注入的 `PORT` env 真正传给 python（之前 `python -m http.server` 不读 PORT env，默认占 8000，preview 报告的端口是空壳，eval 全部 chrome-error）

### Browser verification (preview server, post-reload)

| Acceptance check | Result |
|---|---|
| `#case/case_ma10_reject_2026_03_09` lesson/stop 文案出现 11:33 + 669.85，无 11:09 / 668.91 | ✓ |
| Case 页点 `K线触及 MA10` 行 → engine highlight `[1m: 53,53]` | ✓ |
| Case 页点 `确认K延续方向` → highlight `[1m: 53,54]`（confirm bar = signal+1） | ✓ |
| `#training/ma10` reject chip 引擎 title = "标准 Reject MA10：反抽后压回" | ✓ |
| Training drill cutoff_1m=41 (= signal 53 − 12，匹配 `MIN_DRILL_DISTANCE`) | ✓ |
| Training drill cutoff_5m=22（包含 1m cutoff 的 5m 桶） | ✓ |
| 数据三层一致性脚本 case.bar_index ↔ segment.signal_bar_index ↔ bars_1m[idx].ts | ✓ |
| Training 右栏出现"决策步骤 · 证据导航"卡片，7 step 全显示 | ✓ |
| 点 pill「K线触及 MA10」→ engine highlight `[1m: 53,53]` + "清除高亮"按钮出现 | ✓ |
| 点同 pill 第二次 / 点"清除高亮" → highlight 清除，按钮消失 | ✓ |
| 切换到 Support MA10 case → pillHighlightKey + highlight 自动 reset | ✓ |
| Support MA10 标准做多提交后 review misses **不含**「不在禁止条件内」（forbidden_absent） | ✓ |
| Support MA10 review misses 仍含 7 条入场理由（趋势/均线/触线/确认/实体/止损/空间） | ✓ |
| 主路径（等待/做多/做空/放弃）按钮无变化、不被打断 | ✓ |
| 引擎实例切 case 不泄漏（沿用 batch 7 验证） | ✓ |

### Files touched

- `cases/index.json` — case_ma10_reject 全层对账
- `data/processed/teaching_segments.json` — seed_03.derived 全部重写
- `training/checkpoints.json` — reject case 两处 explanation 数值同步
- `dist/pages-2.jsx` — `buildDecisionStepPills` 新增；`reviewReasons` 复用 `buildReasonGroups` visible set；`TrainingPage` 新增 `pillHighlightKey` state + 决策步骤卡片 + `togglePillHighlight` handler；`highlightRangesProp` 集成 pill 优先级
- `dist/Tang 策略教学系统.html` — cache-bust `?v=20260425f → 20260426a`
- `.claude/launch.json` — bash 包裹让 python 接受 preview 注入的 PORT（不在 git，仅工具修复）

### Open follow-ups (not in this batch)

- Plan #3 (5m submit mapping UX clarification) — 未做
- Plan #7 (global K-line MA/indicator selector) — 未做，需 batch 9 处理
- Plan #8 (K-line hover price card behavior) — 未做，与 Plan #7 同 batch 9
- Plan #5 (adapter performance check) — 仍 conditional
- Plan #6 (additional modules gating) — 仍后置

## 2026-04-25 batch 7 — Training Replay Drill landed

Implemented `training-replay-drill-redesign-plan.md`. `#training/<module_id>` now is a hidden-future intraday replay drill — the 7-step quiz UI is gone.

**TrainingPage rewrite (`dist/pages-2.jsx`)**
- Replaced the 7-step quiz with a drill state machine: `phase: 'replay' | 'submitted' | 'review'`, plus `currentIndex`, `revealCutoffIndex`, `selectedReasonKeys`, `waitLog`, `submittedAction`, `submittedIndex`, `reviewState`, `playbackSnap`.
- Drill init (per plan §2.2): `signalIndex = segment.derived.signal_bar_index ?? case.decision_bar.bar_index`; `drillStartIndex = clamp(signalIndex - 12, 0, last1mIndex)`; `MIN_DRILL_DISTANCE = 8` falls back to `clamp(0,…)` only when distance < 8. `preheat_count` is metadata only — never the drill start.
- Right-rail actions: `等待 / 做多 / 做空 / 放弃`. `等待` is the authoritative one-bar advance (no separate `下一根`). It increments `currentIndex` + bumps `revealCutoffIndex` + appends to `waitLog` + scrolls engine without centering.
- Wait-handler advance uses a `currentIndexRef` so rapid clicks don't lose updates from stale closures (initial impl using `setState(prev=>…)` worked for `currentIndex` but not for the related `setRevealCutoffIndex` / `setWaitLog`, so all three reads now go through the ref).
- Reason chips (plan §3.4) are grouped (background / trigger / risk-space / no-trade-filter) and filtered: a checkpoint without a label or notes is hidden; `forbidden_absent` is hidden unless it has flags or `passed===false`. Multi-select; never required to advance replay.
- Submission resolves `submittedIndex` via `playbackSnap.timeframe`: when on 5m, capture the 5m bar's start ts and locate the first 1m bar at or after — then force engine back to 1m for outcome playback (plan §2.2).
- Outcome playback: cutoff bumps to `min(submittedIndex + 12, last1mIndex)`, engine `scrollTo` centers on the submitted bar, then `playPause()` after a 60ms tick (so `setRevealCutoff`'s auto-pause doesn't race the play call). A useEffect watches `playbackSnap.index` against the reveal target — when reached, engine pauses and phase → `review`. The user can interrupt with `直接看复盘` (visible while playing) or `继续播放` (visible while paused).
- Review object exactly matches plan §4.1: `timingLabel` (`too_early|valid_window|late|not_scored`), `expectedAction` (resolved per §3.3), `actionCorrect`, `timingCorrect`, `submittedIndex`, `signalIndex`, `validWindow`, `reasonHits/Misses/Contradictions`, `reviewText`. Anti / answer-pass cases set `timingLabel = 'not_scored'` and `timingCorrect = null`. When no expected action can be resolved, the case is marked replay-only with a banner ("仅作为只读复盘 — 提交后不计分").
- Highlight: replay phase keeps the chart clean (no highlight). Submitted/review phase shows the standard window (olive band over `signalIndex…validWindowEnd`) plus a single-bar marker at `submittedIndex` (red when wrong/timing off, blue when within window).
- Replay-phase reveal cutoff is computed for both 1m AND 5m (the 5m cutoff is the last 5m bar whose start ts ≤ the 1m cutoff bar's ts), so switching to 5m mid-drill doesn't expose unintended future.
- Case-picker tabs preserved but expanded: `drillCases` = TRAINING_ITEMS first (the trained ones), then any module-matching cases from `findCasesForModule(moduleId)` (replay-only fallback). `DRILL_MODULE_RULES` is the explicit module → rule_ids map (e.g. `ma10` → `support_ma10 + reject_ma10`); plan §4.3 forbids inferring categories from display text.

**Engine playback lock-out**
- Added a `lockPlayback` prop to `KlineView` → forwarded to `KlineEngineAdapter` → toggles a `kline-host--replay-locked` modifier on the host div.
- Product CSS in `dist/Tang 策略教学系统.html` hides `data-action="play|step-back|step-forward|speed|follow|zoom-in|zoom-out"` while the modifier is present. Timeframe / HA / theme / MA buttons stay visible — the user can still review structure during the decision phase. The class drops automatically when phase moves to `submitted` / `review`, restoring the playback row for outcome playback.

**Adapter narrow extension (plan §4.2 allowance)**
- `KlineEngineAdapter` now also accepts `revealCutoff` as an array of `{ timeframe, barIndex }` items. When given an array, it calls `engine.setRevealCutoff` once per item (so 1m and 5m cutoffs can be applied together without clearing each other). The same array path is honored on `applyTeachingChrome` so the loadData-clear → re-apply cycle keeps both cutoffs.
- `KlineView` now forwards `onPlaybackChange` and `onEngineReady` from the parent so TrainingPage can read playback snapshots (timeframe + index) and call `scrollTo / playPause / pause` via the engineApi without poking engine private fields.

**CSS / cache**
- Cache-busting query param on `<script src="…?v=20260425e">` bumped to `…?v=20260425f` for `shared.jsx`, `pages-1.jsx`, and `pages-2.jsx` so Babel-standalone re-fetches the rewritten files.

**Browser verification (preview server, `#training/ma10`)**
| Acceptance check | Result |
|---|---|
| 7-step quiz panel gone | ✓ |
| Future bars hidden at start; chart shows only past + drill-start | ✓ |
| Drill start is 11:24 (signal 11:36, distance 12 ≥ 8) for `case_ma10_support_2026_01_07` | ✓ |
| `等待` advances exactly one 1m bar; 3 sequential clicks → 3 wait-log entries (`11:25/11:26/11:27`) | ✓ |
| Submit `做多` at idx 31 (signal): timing `窗口内`, 标准动作 `做多`, 命中理由 chips render | ✓ |
| Submit `做多` at idx 19 (before signal): timing `过早` ("信号 K 在 11:36 才出现") | ✓ |
| Reject case + `做多`: 标准动作 `做空` ("方向不符：标准是「做空」") | ✓ |
| Edge case (`降级观察`): expected `放弃`, submitted `放弃` → 时机 `未评分` + "已正确识别" | ✓ |
| Submit on 5m (engine toolbar 5m, idx 25 = 11:35-11:39 bar): phase line switches `5m → 1m`, submitted maps to 1m #30 (11:35), classified `过早` per plan §2.2 mapping | ✓ |
| Engine toolbar `play / step-back / step-forward / speed / follow / zoom` hidden during replay (`computed display: none`); 1m/5m/HA/theme stay visible | ✓ |
| `Aggregate5mBand` strip absent (0 hits in DOM); `window.Aggregate5mBand` still exported as dormant function | ✓ |
| Outcome playback button `直接看复盘` skips to review when paused; review panel renders with hit/miss/contradiction reason groups + `继续播放到结尾 / 重做本案例 / 换一个案例` | ✓ |
| Regression: `#hub` shows 0 canvas (mini SVG only); `#case/case_ma10_support_2026_01_07` is `kline-host--evidence` only (no replay-locked leak) | ✓ |
| Regression: `kline-engine-v2.html` `runIntegrationTest()` 29/29 PASS | ✓ |

**Files touched**
- `dist/pages-2.jsx` — TrainingPage rewrite + drill helpers (`computeDrillInit`, `compute5mCutoffFor1m`, `map5mTo1mIndex`, `findCasesForModule`, `resolveExpectedAction`, `getConfirmIndex`, `classifyTiming`, `buildReasonGroups`, `reviewReasons`, `buildReviewText`).
- `dist/shared.jsx` — `KlineEngineAdapter` accepts `lockPlayback` + array-form `revealCutoff`; `KlineView` accepts + forwards `lockPlayback`, `onPlaybackChange`, `onEngineReady`.
- `dist/Tang 策略教学系统.html` — added `.kline-host--replay-locked` CSS rules; bumped script cache-busting `?v=20260425e → f`.

**Open follow-ups (not in this batch)**
- Reason `遗漏理由` for `forbidden_absent` shows on long-trade cases as a "missed reason" — semantically OK (it's a passed checkpoint the user didn't claim) but slightly noisy. Worth a UX pass once more cases land.
- The 5m-submit → 1m mapping is plan-faithful (uses 5m bar's *start* ts, so a 5m commit at 11:35-11:39 bar maps to 1m #30 = 11:35). For users who think they're acting "in the same 5m candle as the signal", the `过早` label may surprise — flagged in the review text but consider a small tooltip explaining the mapping.
- `KlineEngine` still has no public `setMaVisibility(key, on)` method; `KlineEngineAdapter.setMaOn` mutates `engine.maVisibility` directly + calls `_updateToolbarState()`. Same caveat as before (pre-existing).
- `case_ma10_reject_2026_03_09` `decision_bar.bar_index = 31` vs `seed_03.signal_bar_index = 63` divergence — drill init uses segment-truth (`signal_bar_index`), so the drill is correct, but case-manifest still disagrees with the segment. Worth reconciling at the data layer.

## 2026-04-25 batch 6 — Training Replay Drill plan

Saved the next training-page direction in `training-replay-drill-redesign-plan.md`.

- Decision: do **not** keep expanding the visible 7-step quiz page. Next version of `#training/<module_id>` should become a hidden-future intraday replay drill.
- Core interaction: user advances K lines, chooses `等待 / 做多 / 做空 / 放弃` at any visible bar, then the app reveals follow-up bars and reviews timing, direction, and selected reasons.
- Evaluation model: free action is allowed, but grading is window-based using `segment.derived.signal_bar_index`, `confirm_bar`, case rule/category, and `derived.checkpoints`.
- Scope: first implementation pass only changes TrainingPage / lab integration. Do not spread this redesign into hub, module, case, mistake, archive, or global K-line UX.
- Explicit no-go: do not restore `Aggregate5mBand`; the 5m strip was rejected as visually noisy.
- Updated `tang-strategy-teaching-system-plan.md#6.2` with a short v0.4 direction note that points to the new plan.
- Review follow-up: incorporated `replay-drill-plan/review-001-agent01.md` + `review-001-agent02.md` into the plan. Key clarifications now locked: signal-relative drill start instead of raw `preheat_count`, `confirm_bar` fallback, case-field-first expected action, authoritative `等待` control, 12-bar reveal clamp, and explicit review object shape.
- Second review follow-up: `replay-drill-plan/review-002-agent01.md` and `review-002-agent02.md` both approve. Remaining polish was folded into the plan: `MIN_DRILL_DISTANCE`, explicit drill index initialization, 5m-submit-to-1m index mapping, deterministic playback disablement during replay, `not_scored` semantics, and reason contradiction rules.

## 2026-04-25 batch 5 — Training redesign + 5m live-aggregation band

Plan file: `~/.claude/plans/training-page-kline-ux-nifty-ember.md`

**Phase 1 — Training page redesign (HANDOFF #12)**
- TrainingPage now uses 2-col layout: chart 8/12 + rail 4/12
- Page header collapsed to a single row: back-link + breadcrumb + case-picker tabs (right-aligned, underlined-tab style). Tabs replace the old chip row that sat above the progress bar.
- Left column dropped — the redundant left step list is gone. Progress is shown as a horizontal dot row at the top of the rail (clickable hit area `py-2.5` so the 8px dot has a 22px tall click target).
- **Step navigation is one-way**: clicking a future locked dot is a no-op (`disabled={!reachable}`). Past + current are clickable for review. Tooltip explains lock state.
- Question / options / feedback panel now occupies the rail middle. Clicking an option still triggers chart highlight via `stepToHighlightRanges` — kept the existing flow.
- Prev/next + reveal toggle compacted into a single bottom card on the rail. Reveal is now an icon button (`visibility` / `visibility_off`) shown only when `step < AUTO_REVEAL_STEP`. Caption text moved below the buttons.
- Touched: `dist/pages-2.jsx#TrainingPage` (lines 3–159 → ~150 lines of new layout).

**Phase 2 — 1m/5m broker-style switching (HANDOFF #13)**

First attempt — `Aggregate5mBand` (a 72px SVG strip above the 1m chart with live OHLCV aggregation of the current 5m bar) — was rejected by the user as visually noisy. The two-strip layout cluttered the chart card and felt unlike a real broker terminal. **Reverted**: band rendering removed from `KlineView`; helper functions `aggregate5mAt`, `first1mIndexAtOrAfter`, and the `Aggregate5mBand` component are still defined in `shared.jsx` (dormant) in case Phase 3 wants live-MA aggregation later, but they are not invoked anywhere.

Replacement design — **classic broker-style switching, with viewport time-anchoring**:

- Engine 1m/5m toolbar buttons are **visible again** in lab mode. The `.kline-host--lab .kline-engine__button[data-action="timeframe"] { display: none }` rule was removed.
- `KlineEngine#setTimeframe(tf)` patched to re-center the viewport on the time-aligned `currentIndex` after switching. Previously, `dataManager.switchTimeframe` mapped `currentIndex` by ts (so the wall-clock moment was preserved on the new tf), but `viewportManager.viewStart` stayed at its previous value — meaning the same moment could fall off-screen after a switch. The patch now ends with `this.scrollTo({ timeframe, barIndex: nextIndex, center: true })`, which centers the viewport on the new index. Previously-explicit `emit('viewport:changed') + scheduleRender()` removed since `scrollTo` already does both.
- New adapter API: `engineControls.scrollTo({ timeframe, index, center })` exposed via `KlineEngineAdapter` (kept from the band attempt — useful for future cross-tf jumps).
- Engine code touched: `kline-engine.js#setTimeframe` (~line 2490) + same hunk mirrored in `kline-engine-v2.html` for parity.
- Verification: `runIntegrationTest()` 29/29 PASS post-patch. Browser test with the teaching segment (1m bars 11:05–12:11, 5m bars 09:30–12:10):
  - 1m at idx 32 (11:37) → switch to 5m: cur becomes idx 25 (11:35, the 5m bar containing 11:37) ✓
  - Switch back to 1m: cur becomes idx 30 (11:35) ✓
  - Viewport centered around the new index in both cases ✓

**Cache-busting**: `<script type="text/babel" src="...?v=20260425c">` added because Babel-standalone caches transformed output by URL; without a version bump, browsers held stale `shared.jsx`/`pages-2.jsx` after edits and the new `Aggregate5mBand` was undefined despite being on disk.

## Current Phase

Plan: `tang-strategy-teaching-system-plan.md` v0.3. MA10 vertical slice now runs with the **real `KlineEngine` v2** embedded in `KlineView` evidence/lab modes. Signal validation panel in CasePage is now wired to chart via `setHighlightRanges`.

Current phase boundary:

- Runtime data contracts stable (rules / cases / segments / training).
- `dist/Tang 策略教学系统.html` loads `kline-engine/kline-engine.js` + mode-aware CSS before React.
- `shared.jsx` has `KlineEngineAdapter`:
  - mounts `window.KlineEngine`, calls `destroy()` on unmount
  - routes `mini` → SVG (list pages don't spawn engines)
  - routes `evidence` → real engine with toolbar/HUD hidden via `.kline-host--evidence`, plus compact external playback controls in the KlineView footer
  - routes `lab` → real engine with full engine controls, compacted toolbar, hidden HUD, and case-relevant MA buttons
  - on `data:loaded`, prunes MA visibility to case-relevant lines and `scrollTo({ timeframe, barIndex: decisionIndex, highlight: true, center: true })`
- 2026-04-25 visual pass fixed the embedded engine height contract: product pages now override the standalone engine's 560px default canvas height so evidence/lab charts are not clipped by `KlineView` containers.
- `MistakeDetailPage` ranks evidence case by mistake-tag → rule → module → anti-grade bonus; anti cases with mistake-tag win over unrelated standards.
- MA10 / Signal B / barrier / quality paths all verified in the browser.

## Engine Extraction

`dist/kline-engine/kline-engine.js` is the product-safe extract of the engine IIFE inside `kline-engine-v2.html`. The extractor:

- Takes the engine IIFE body (the `<script>((() => { ... })();</script>` block containing `window.KlineEngine = KlineEngine`).
- Replaces the inline `DEMO_FIXTURES` payload with `{}`.
- Strips `bootstrapDemo()`, the auto-bootstrap call, and `runIntegrationTest`.

As of 2026-04-24 the two files are in parity (verified via `diff` after dedent + DEMO normalization — only the 204-line demo tail differs). When the engine changes, edit `.html` first (so `runIntegrationTest` can exercise the change), then regenerate `.js`. Or edit both in tandem and re-run the diff check to confirm parity.

## Completed Data-Contract Work

- `rules/compiled/index.json` (schema 0.1, 7 rules, MA10 = `support_ma10` + `reject_ma10`)
- `cases/index.json` (schema 0.1, 6 cases, maps case → rule → segment → decision bar)
- `data/processed/teaching_segments.json` (15 segments, each with `derived.checkpoints`, `bars_1m`, `bars_5m`, `annotations_1m`, `annotations_5m`)
- `training/checkpoints.json` (7-step override for `case_ma10_support_2026_01_07` only)

Contract order is unchanged:

```text
Rule → Case.rule_ids → Case.segment_id → Segment.derived.checkpoints → Training decision_steps
```

## Engine API Additions (2026-04-24)

- `KlineEngine#setRevealCutoff(input)` — hide bars beyond `cutoff`. Accepts `null` (clear all), `number` (set current tf), or `{ timeframe, barIndex }`.
- `KlineEngine#getRevealCutoff(timeframe?)` — read cutoff for tf or current.
- `revealcutoff:changed` event — payload `{ '1m': number|null, '5m': number|null }`.
- All playback and render paths respect cutoff: `play()`, `stepForward()`, `setCurrentIndex()`, `_playbackTick()`, Y-axis range, annotations, HUD focus, `setTimeframe` clamp on switch.
- `loadData()` clears cutoff.
- Documented in `dist/kline-engine/INTEGRATION.md` §4.7b + event table + version record.

- `KlineEngine#setHighlightRanges(input)` — translucent band behind candles. Accepts `null`, single `{ timeframe, startIndex, endIndex, style? }`, or array. Three styles: `olive` (pass, default) / `red` (fail) / `blue` (info).
- `KlineEngine#getHighlightRanges()` — shallow copy of current ranges.
- `highlight:changed` event — payload is the range array snapshot.
- Drawn between `drawGrid` and `drawVolumeBars` in render pipeline; respects viewport + cutoff.
- `loadData()` clears highlights.
- Documented in `INTEGRATION.md` §4.7c + event table + version record.

Adapter integration:

- `KlineView({ mode, segmentId, caseId, height, revealCutoff, highlightRanges })` now forwards both props to `KlineEngineAdapter`.
- Adapter auto-switches `timeframe` to match the first range's tf, then calls `setHighlightRanges` + `scrollTo` to center the middle of the range (so off-screen ranges become visible).
- Adapter keeps `revealCutoffRef` and `highlightRangesRef` in sync with props so `applyTeachingChrome` (inside `data:loaded` callback) can re-apply the latest values after mount — otherwise loadData's state clear would wipe them.
- Adapter now exposes a small control surface back to `KlineView` (`playPause`, `stepBack`, `stepForward`, `resetTo`, `toggleTheme`, `pause`, `snapshot`) and streams playback state (`playing`, `speed`, `timeframe`, `index`, `theme`) through `onPlaybackChange`. This powers evidence-mode footer controls without showing the full engine toolbar.
- `TrainingPage` lab cutoff is **step-aware**: steps 0-3 (环境 / 观察 / 触发 / 过滤) keep future bars hidden at `decision_bar.bar_index`; steps 4-6 (执行 / 出场 / 复盘) auto-reveal (cutoff = null). The manual `揭示后续走势 / 重新隐藏` toggle is visible only pre-decision as an escape hatch; at steps 4+ it's hidden and the caption reads `本步骤已揭示后续走势（<step label>）`. Manual state resets when switching case. Highlight is auto-derived from the current step's `checkpoint_keys` via `stepToHighlightRanges`. `AUTO_REVEAL_STEP` constant in `pages-2.jsx` controls the threshold (currently 4).
- `CasePage` right-side `信号验证` panel rows are clickable buttons; click toggles `selectedCpKey` which flows into `checkpointToRanges(cp, segment, case) → highlightRanges`. Second click or case switch clears.
- `shared.jsx#checkpointToRanges(checkpoint, segment, caseObj)` maps checkpoint → range(s):
  - `trend_ok` / `ma_alignment_ok` → full 5m window
  - `touch_ma10` / `body_not_cross` / `stop_defined` / `vwap_*` → single 1m bar at `checkpoint.bar_index`
  - `confirm_bar` → decision + next bar
  - `reward_ok` → decision → end of 1m window
  - `forbidden_absent` + checkpoints without `bar_index` → no range (row is disabled).
- `shared.jsx#stepToHighlightRanges(step, segment, caseObj)` — TrainingPage helper. Unions all `checkpoint_keys` of the step through `checkpointToRanges`; when result mixes 1m and 5m, prefers 1m (primary teaching tf). Returns `null` when no range exists.

## Frontend Files Touched This Phase

- `dist/Tang 策略教学系统.html`
  - Loads `kline-engine/kline-engine.js`
  - Adds CSS for `.kline-host--evidence` (hides toolbar + HUD)
  - 2026-04-25: product embed CSS sets `.kline-host`, `.kline-engine`, viewport, canvas-wrap, and canvas to a controlled 100% height/min-height 0 contract so the standalone engine default does not clip inside evidence/lab cards.
  - 2026-04-25: `.kline-host--lab` hides HUD, compacts toolbar spacing/buttons, and hides off-case MA buttons to keep the replay chart readable.
- `dist/shared.jsx`
  - `segmentToEnginePayload(segment, caseObj)` builds engine-consumable JSON (meta + bars + annotations)
  - `KlineEngineAdapter` handles mount / destroy / `loadData` / `scrollTo` / MA pruning / compact playback control callbacks
  - `KlineView` dispatches `mini` → SVG, `evidence`/`lab` → adapter
  - 2026-04-25: evidence mode renders footer controls for previous bar, play/pause, next bar, and a `tf · #bar` readout; lab mode continues to rely on the engine toolbar.
  - 2026-04-25: evidence footer now also includes `复位`, `提示开/关`, and `背景` controls. `复位` restores the captured initial visual snapshot for that chart (`timeframe`, `index`, `theme`, and marker toggle state) instead of hard-jumping to a fixed decision bar. The background control calls the engine's public `setTheme/getTheme`. The marker toggle controls internally generated 1m checkpoint ranges; long ranges are filtered out so default hints stay point-like instead of covering the whole future path. Markers default off for a quieter first view.
  - 2026-04-25: `MiniKlineSvg` computes compact chart Y-domain from visible candles + MA10 only, so thumbnails are not flattened by hidden MA200/VWAP values.
  - Exposes `KlineEngineAdapter` and `segmentToEnginePayload` on `window`
- `dist/pages-2.jsx`
  - `MistakeDetailPage` evidence ranking: mistake-tag (+4) → rule overlap (+2) → module match (+1) → anti-grade bonus (+1)
  - `TrainingPage` shows a case-picker chip row when a module has multiple trainings; clicking resets step/answer state.
  - 2026-04-25: `TrainingPage` gives the replay chart a wider center column and passes `height={540}` to `KlineView` so the toolbar and chart fit without clipping.
- `dist/kline-engine/kline-engine.js`
  - 2026-04-25: `chartArea()` reserves a wider right gutter for price and percent labels so the right-side axis text is not clipped.
  - 2026-04-25: `drawHighlightRanges()` supports a refined `marker` style for teaching hints: a narrow warm glow, dashed hairline, and small dot. It avoids in-chart text labels and the earlier heavy blue vertical band.
- `dist/kline-engine/kline-engine-v2.html`
  - 2026-04-25: mirrored the same `chartArea()` right-gutter change in the demo/source HTML to keep the extracted JS and demo source aligned for this hunk.
  - 2026-04-25: mirrored the refined `marker` style in the demo/source HTML.
- `training/checkpoints.json`
  - 3 training records: Support MA10 (7 steps), Reject MA10 (7 steps, `module_id: "ma10"`), Signal B (7 steps, `module_id: "signal-b"`).
- `dist/shared.jsx`
  - Adapter now patches `.kline-engine__title` DOM with the case title after `data:loaded`; the engine's `[data-role="meta"]` subtitle is still engine-driven (date | tf).

## MA10 Vertical Slice ID Mapping

| Layer | Support MA10 standard | Reject MA10 standard | Reject MA10 edge |
|---|---|---|---|
| Rule | `support_ma10` | `reject_ma10` | `reject_ma10` |
| Case | `case_ma10_support_2026_01_07` | `case_ma10_reject_2026_03_09` | `case_ma10_edge_2026_02_03` |
| Segment | `seed_01` | `seed_03` | `seed_04` |
| Decision bar | `1m:31 @ 11:36` | `1m:53 @ 11:33` | `1m:31 @ 11:09` |
| Grade | `standard` | `standard` | `edge` |

## Kline Engine Capability — As Used

Verified in the browser via the adapter:

- `new KlineEngine({ container })` → mounts in host `<div>`
- `loadData(payload)` → returns summary, resets viewport, emits `data:loaded`
- `setTimeframe('1m' | '5m')` → via toolbar in lab mode
- Playback: `play()`, `pause()`, `stepForward()`, `stepBack()`, `setSpeed()` → toolbar-driven in lab
- `scrollTo({ timeframe, barIndex, highlight: true, center: true })` → adapter calls in `data:loaded` callback
- `maVisibility` mutation + `_updateToolbarState()` + `scheduleRender()` → adapter prunes MA lines per module
- `destroy()` → verified: navigating between hub/case/mistake pages leaves 0 canvas on list pages, 1 canvas on detail pages; no leaks across 3 consecutive case switches
- `on('data:loaded', cb)` → readiness signal (preferred over setTimeout)

Persistent caveats:

- **~~No public future-bar masking API.~~** ✅ Fixed 2026-04-24: engine now exposes `setRevealCutoff(input)` / `getRevealCutoff(tf?)` / `revealcutoff:changed` event. Clamps render visible.end, Y-axis range, annotations, HUD focus, `play()`, `stepForward()`, `setCurrentIndex()`, `_playbackTick()`. `loadData()` resets. See INTEGRATION.md §4.7b.
- **~~No public persistent range-highlight API.~~** ✅ Fixed 2026-04-24: engine now exposes `setHighlightRanges(input)` / `getHighlightRanges()` / `highlight:changed` event. CasePage 信号验证 panel wired up via `checkpointToRanges` helper. See INTEGRATION.md §4.7c.
- **Engine title is hardcoded in the toolbar HTML.** The adapter now overwrites `.kline-engine__title` after `data:loaded` to show the case title, but this is a DOM patch on top of engine internals — if the engine re-templates its toolbar, this will break. Upstream fix: have the engine honor `meta.title` when rendering its own title.
- **~~`kline-engine.js` is diverging from `kline-engine-v2.html`.~~** ✅ Fixed 2026-04-24: backported 10 code hunks (state init, loadData reset, setRevealCutoff/getRevealCutoff/_cutoffForCurrent, setHighlightRanges/getHighlightRanges/drawHighlightRanges, play/stepForward/_playbackTick cutoff clamps, setCurrentIndex clamp, setTimeframe clamp, render viewport clamp, HUD focusBar clamp, drawHighlightRanges call). Engine logic now 1:1. Demo HTML `runIntegrationTest()` still 29/29 PASS. Teaching page (via `.js`) verified.
- **~~Data consistency: `cases/index.json#decision_bar.bar_index` vs `segment.derived.signal_bar_index`.~~** ✅ Fixed 2026-04-26 (batch 8, 方案 C). All three layers now agree at idx=53/54 @ 11:33-11:34 for `case_ma10_reject_2026_03_09`. See batch 8 record for full reconciliation details.

## Verification (2026-04-24)

Local preview: `python3 -m http.server` (preview harness auto-launches).

URL: `http://localhost:PORT/Dream%20bigger/dist/Tang%20%E7%AD%96%E7%95%A5%E6%95%99%E5%AD%A6%E7%B3%BB%E7%BB%9F.html`

Browser-evaluated checks (all green):

| Route | Expectation | Result |
|---|---|---|
| `#hub` | 6 mini SVG thumbnails, 0 canvas | ✓ |
| `#module/ma10` | 1 canvas, host class `kline-host--evidence`, toolbar `display:none` | ✓ |
| `#case/case_ma10_support_2026_01_07` | 1 canvas, evidence mode, HUD hidden | ✓ |
| `#training/ma10` | 1 canvas, host class `kline-host--lab`, full toolbar (1m/5m/▶/▶▶/speeds/MA toggles/HA/theme) | ✓ |
| `#mistake/err-05` (关卡太近还做) | Evidence = `case_barrier_anti_2026_02_11` (anti, tag-match) | ✓ |
| `#mistake/err-06` (K线质量差还做) | Evidence = `case_quality_anti_2026_02_13` (anti, tag-match) | ✓ |
| Navigate `case → hub → reject → edge` | Canvas count 1 → 0 → 1 → 1; no leaks | ✓ |
| `#training/ma10` | Case-picker chips for Support + Reject; engine title reads "标准 Support MA10：回踩后延续" | ✓ |
| `#training/ma10` → click Reject chip | Engine title switches to "标准 Reject MA10：反抽后压回"; 7-step list re-renders | ✓ |
| `#training/signal-b` | Engine title "信号B：双线跌破直达 MA200"; 7 steps loaded from `case_signal_b_2026_03_25` | ✓ |
| `setRevealCutoff({ timeframe: '1m', barIndex: 31 })` | `getRevealCutoff('1m')` returns 31; state snapshot `{ '1m': 31, '5m': null }` | ✓ |
| `stepForward()` at cutoff | `currentIndex` stays at 31 (no-op) | ✓ |
| Clear cutoff + `stepForward()` | `currentIndex` advances to 32 | ✓ |
| `loadData()` with cutoff set | Cutoff resets to `{ '1m': null, '5m': null }` | ✓ |
| `play()` at cutoff | `isPlaying()` stays false (no-op) | ✓ |
| Training page "揭示后续走续" toggle | Button label flips to "重新隐藏"; caption switches to "已揭示后续走势" | ✓ |
| `#case/case_ma10_support_2026_01_07` → click 信号验证 · K线触及 MA10 | Ranges `[{tf:'1m',start:31,end:31,style:'olive'}]`; chart scrolls to center bar 31; olive band drawn | ✓ |
| Same case → click 5min 趋势确认 | Engine auto-switches to 5m; full 5m window highlighted | ✓ |
| Same case → click 确认K延续方向 | Multi-bar range `[31,32]`; back to 1m; wider band | ✓ |
| Click same row twice | Range cleared; row returns to inactive | ✓ |
| Navigate to another case | Highlight state resets; no stale selection | ✓ |
| `#training/ma10` fresh mount (step 1 环境判断) | Engine on 5m; ranges = [{5m 0-32 olive}×2] for `trend_ok + ma_alignment_ok`; cutoff_1m=31 | ✓ |
| Click step 3 触发判断 | Switches to 1m; ranges = [{1m 31-31 olive}, {1m 31-32 olive}] for `touch_ma10 + confirm_bar` | ✓ |
| Switch to 标准 Reject MA10 chip | Engine title updates; ranges update to reject's 5m full window (0-26); cutoff preserved | ✓ |
| Click 揭示后续走势 | `cutoff_1m` becomes null; ranges preserved; toggle label flips to 重新隐藏 | ✓ |
| Regression: CasePage checkpoint click | Still works (single 1m bar highlight) | ✓ |
| Regression: demo HTML `runIntegrationTest()` | 29/29 PASS after engine loadData ordering fix | ✓ |
| Step 3 触发判断 (index 2) | cutoff_1m=31; caption reads `已隐藏决策 K 之后的走势...`; toggle visible as `揭示后续走势` | ✓ |
| Step 5 执行动作 (index 4) | cutoff_1m=null auto; caption reads `本步骤已揭示后续走势（执行动作）`; toggle hidden | ✓ |
| Pre-decision manual reveal (step 3 + toggle) | cutoff_1m=null; caption reads `已手动揭示后续走势 · 完整片段可见`; toggle flips to `重新隐藏` | ✓ |

Console status: expected Tailwind CDN + in-browser Babel warnings only. No runtime errors. Favicon 404 expected.

## Verification (2026-04-25)

Local preview used:

`http://127.0.0.1:8766/Dream%20bigger/dist/Tang%20%E7%AD%96%E7%95%A5%E6%95%99%E5%AD%A6%E7%B3%BB%E7%BB%9F.html`

Browser-evaluated checks:

| Route | Expectation | Result |
|---|---|---|
| `#hub` | Mini SVG thumbnails use readable candle proportions after compact Y-domain change | ✓ visual check via screenshot |
| `#case/case_ma10_support_2026_01_07` | Evidence host 440px, canvas 412px, toolbar/HUD hidden; chart no longer uses the old 560px canvas that was clipped by the card | ✓ |
| `#case/case_ma10_support_2026_01_07` | Right-side price + percent axis labels have enough gutter and are readable | ✓ |
| `#training/ma10` | Lab host 540px, HUD hidden, compact toolbar, off-case MA buttons hidden, canvas visible below controls | ✓ |
| `#module/ma10` visual anchor | Evidence footer shows compact controls: previous bar, play/pause, next bar, `1m · #bar` readout | ✓ |
| `#module/ma10` compact controls | Next changes `1m · #31` → `1m · #32`; Previous changes `#32` → `#31` | ✓ |
| `#module/ma10` compact controls | Play changes button title/text to pause and advances to `#32`; Pause restores play state | ✓ |
| `#module/environment` compact controls | Reset appears and restores the captured initial visual state; in local verification, `1m · #32` returned to initial `1m · #31` and restored initial marker/theme state | ✓ |
| `#module/environment` markers | Marker button toggles `提示关` → `提示开`; visible hints use a refined warm hairline/glow/dot marker instead of a broad blue band or in-chart label text | ✓ |
| `#module/environment` background | Background button calls engine theme API and toggles the chart theme | ✓ |

Console status: expected Tailwind CDN + in-browser Babel warnings only. Favicon 404 expected. No app runtime errors observed.

## Pending UI Issues (2026-04-25 user review)

User-reviewed the live page and called out 8 issues. Tackling them in this batch:

1. **Detail pages have no obvious back affordance.** `ModulePage` / `CasePage` / `TrainingPage` lack a "返回" entry; users can only escape via top-nav or sidebar. `MistakeDetailPage` already has one.
   - Decided: plan A (in-page back button on detail pages), with **static parent mapping**:
     - `module/<id>` → `hub`
     - `case/<id>` → `module/<case.module>`
     - `training/<id>` → `module/<id>`
     - `mistake/<id>` → already exists, keep
2. **Account button (top-right `account_circle`) unused right now.** Comment out (`shared.jsx#TopNav`).
3. **Settings button (left-bottom `settings`) unused right now.** Comment out (`shared.jsx#Sidebar`). 术语表 entry kept untouched (decision: low signal but harmless).
4. **K-line evidence chart has no MA legend / toggles.** Adapter's `CASE_RELEVANT_MA` prunes off-case MAs and the engine toolbar is hidden in evidence mode, so the user can't see which color is which MA, nor opt back into MA50/200/VWAP.
   - Decided: keep the prune as the *default* MA visibility, but add a compact MA legend + toggle row in `KlineView`'s footer (or above the chart). Each chip shows MA name + color swatch and toggles `engine.maVisibility[k]` on click. Lab mode also unhides the engine toolbar's off-MA buttons (currently `display:none`).
5. **Marker hint style still ugly.** The 2026-04-25 refined marker (warm glow + dashed hairline + dot) is still too noisy and not on brand.
   - Decided: simpler treatment — remove the dashed leader line, keep only a small triangle/dot anchored above the candle with a soft circular halo. Less vertical chrome, more like a callout.
6. **Annotation triangles (the small `▲`/`▼` pins) are too inconspicuous.** `pinSize = 5–7px`, alpha 0.6 for non-high-score; gets buried by candles and MAs.
   - Decided: bump default `pinSize`/`stemLen` and alpha; add a 1px outline ring so the pin remains visible against MA lines.
7. **Y-axis price labels overlap with the candle high/low leader labels.** When a candle's high is near a Y-axis tick, the black `693.640` leader text and the green `693.674 +0.15%` axis text collide.
   - Decided: when a high/low leader label's Y is within ±10px of an axis tick, suppress that axis tick's text (the leader is more informative for that bar). Alternative we rejected: shrinking leader fonts — would still overlap.
8. **No OHLCV hover tooltip.** The crosshair only labels the y-axis price; no per-bar OHLCV info on hover. The HUD bar exists but is hidden by product CSS (it's also too cluttered to re-enable as-is).
   - Decided: add a new lightweight floating tooltip (`kline-engine__hover-card`) inside the engine. Shows date + time, O/H/L/C, change ± / change %, volume. Positions near cursor with edge detection (same pattern as `_showAnnoTooltip`). HUD bar removed/kept hidden.

## Pending Issues — Defer to Next Session (2026-04-25 batch 4)

User flagged after the layout widening landed; both are bigger redesigns, not patches:

12. **Training page (`#training/<id>`) needs a structural rethink — "完全不知所云的感觉".** Current layout: back button → page title chip-row → progress bar → 12-col grid `[steps | chart-card | question]`. Even with the wider chart (batch 3 below), the user feels the page doesn't communicate what to do or what the current state is. Suspected pain points worth investigating before redesign:
    - The 7 step labels on the left are decorative — clicking is the only way to advance, but the right-side "上一步/下一步" buttons are the actual driver. Two parallel navigation surfaces confuse intent.
    - The chart card has its own internal title + meta + toolbar + checkpoint chips + reveal status row — too many sub-headers fighting for attention.
    - The question pane on the right is small, and the answer feedback (checkpoint pills) appears in a third location after answering. The mental model "see chart → answer → check" isn't visually scaffolded.
    - The case-picker chips (e.g. 标准 Support MA10 / 标准 Reject MA10) sit above the progress bar, but they affect the chart and questions below — proximity is wrong.
   Action next session: redesign the page layout from scratch (probably a 2-col `[chart wide | side panel]` with steps, question, and feedback consolidated; case picker becomes a header tab).

13. **K-line display + 1m/5m timeframe switching needs rework everywhere it appears.** The user called out the timeframe switching specifically as part of a broader "redo the K-line UX" pass. Open angles to think through:
    - Today the timeframe button is inside the engine toolbar (`1m` / `5m`); switching does `engine.setTimeframe()` which keeps `currentIndex` heuristically aligned but visually jumps. There's no animated transition or visual "this is the same moment in time" cue across the switch.
    - Educational story: the strategy is 5min trend → 1min trigger. The page should make this two-frame relationship feel natural — not a button toggle. Possible directions: a stacked dual-pane (5m on top, 1m below, both linked); a primary/secondary inset; an explicit "now switching to 1m for trigger" beat.
    - The `cutoff` semantics are per-timeframe; switching frames doesn't visually preserve the same wall-clock moment. Worth thinking about whether cutoff should be expressed in time, not bar index.
    - Evidence vs lab vs mini: today they all feel like the same engine in different containers. Maybe each mode should *look* different so users know what they can do.
   Action next session: do a UX redesign pass on the K-line surface as a whole, including timeframe switching. Probably one design doc, then implementation in a follow-up.

## Pending UI Issues (2026-04-25 batch 3)

User feedback after batch 2:

9. **MA toggles for MA5/MA20/MA30/MA60/MA120 had no effect on chart.** Root cause: `data/processed/teaching_segments.json` only carried `m10/m50/m200/vw` per bar even though the daily SPY JSONs in `data/processed/SPY_<date>.json` have all MAs (`m5/m10/m20/m30/m50/m60/m120/m200/m250` + `vw`). The slicer pre-dated the full-MA build, so the segments were stale.
   - Fix: ran a one-shot Python rebuild that reads each segment's date, loads `SPY_<date>.json`, joins by `ts`, and replaces each segment bar with the full daily bar. Result: 1784 / 1784 bars matched, all MAs now present in `teaching_segments.json`. No code change to `slice_teaching_segment.py` needed (it preserves whatever fields are in the source); long-term, just re-running `slice_teaching_segment.py` against the current daily files would have produced the same outcome.
   - Follow-up: when adding new teaching segments via `slice_teaching_segment.py` from the up-to-date daily files, all MAs will be carried automatically.
10. **`MaLegend` had a disabled "数据缺失" branch.** Rolled back to a single enabled state — every MA is clickable and reflects engine visibility 1:1. The `available` prop is still computed defensively so a future segment without a MA would still degrade gracefully.
11. **Training page chart canvas felt cramped.** The lab toolbar was occupying ~80px (two rows + a redundant title block). Compacted via product CSS:
    - `.kline-host--lab .kline-engine__toolbar-group:first-child` hidden — the React-side header already shows the case title and timeframe.
    - Buttons shrunk: `min-height: 26px; padding: 3px 8px; font-size: 12px`.
    - `gap` and `padding` on the toolbar tightened.
   Result: lab toolbar fits in one row, chart canvas gains ~70px vertical.
11b. **Follow-up: training page still felt too small overall.** Container + grid widened in `pages-2.jsx#TrainingPage`:
    - `max-w-[1280px] p-12` → `max-w-[1440px] px-8 py-10`
    - Grid `xl:col-span-2 / xl:col-span-7 / xl:col-span-3` → `xl:col-span-2 / xl:col-span-8 / xl:col-span-2` (steps / chart / question).
    - `KlineView` lab `height={540}` → `height={580}`.
    - Question pane padding `p-6` → `p-5` to recover horizontal breathing room.
    Measured at 1366px viewport: chart canvas now 701×506px (was ~531×380px); +170 × +126px. The user accepted this layout but flagged that the training page still needs a structural rework — see issue #12 in the deferred section above.

## Verification (2026-04-25 batch 2)

Local preview: `python3 -m http.server 8765` (preview harness).

URL: `http://localhost:8765/Dream%20bigger/dist/Tang%20%E7%AD%96%E7%95%A5%E6%95%99%E5%AD%A6%E7%B3%BB%E7%BB%9F.html`

Browser-evaluated checks:

| Route | Expectation | Result |
|---|---|---|
| `#hub` | Top-right account button gone; sidebar 设置 gone; sidebar 术语表 still present | ✓ |
| `#module/environment` | Back button reads "← 返回策略地图"; MA legend has 9 chips with MA10/50/200/VWAP active by default | ✓ |
| `#module/environment` | Click MA5 chip → enabled (state mirrors engine); click again → disabled | ✓ |
| `#module/environment` | Hover canvas → OHLCV card appears with date+time, 开/高/低/收/涨跌额/涨跌幅/成交量 | ✓ |
| `#module/environment` | mouseleave → hover card hides | ✓ |
| `#case/case_ma10_support_2026_01_07` | Back button reads "← 返回MA10核心入场"; click "K线触及 MA10" → olive band on bar 31 | ✓ |
| `#case/...` | High-price leader label flips to left side when high candle is near right edge — no overlap with right-axis price/percent labels | ✓ |
| `#case/...` | Annotation triangles render with halo ring + larger pin (pinSize 7/9, stemLen 14/18, alpha 0.9/1.0) — visible against MA lines | ✓ |
| `#training/ma10` | Back button reads "← 返回MA10核心入场"; engine toolbar's MA buttons hidden (computed `display: none`); React MA legend handles toggling | ✓ |
| Marker mode | New marker style: soft halo + dot at top of chart, no dashed leader line | ✓ |
| `kline-engine-v2.html` standalone | `runIntegrationTest()` returns 29/29 PASS — no engine logic regression | ✓ |
| `kline-engine-v2.html` standalone | Hover card appears with 7 rows (OHLCV + change + volume) | ✓ |
| Engine parity | `kline-engine.js` and `kline-engine-v2.html` match on hover-card markers (26 hits each) and halo/flip-leader markers (8 hits each) | ✓ |

Console: expected Tailwind/Babel warnings only. No app runtime errors.

## Next Steps

1. **~~Per-step checkpoint pills~~** ✅ Done 2026-04-26 (batch 8). New "决策步骤 · 证据导航" card in TrainingPage right rail; pills resolve via `buildDecisionStepPills` + `checkpointToRanges`; nav-only, doesn't affect drill scoring.
2. **Adapter performance check.** On slow hosts, re-mounting engine on every case switch may flash. Optional follow-up: hoist a single engine instance out of React and `loadData()` on case switch.
3. **Additional modules.** `candle_body_quality`, `vwap_distance_filter`, `moving_stop`, `background_5m` still lack training steps; add them only once MA10 + Signal B flow is stable.
4. **~~Reconcile case `decision_bar.bar_index` with segment `signal_bar_index`.~~** ✅ Done 2026-04-26 (batch 8, 方案 C). All three layers (case manifest / segment derived / training explanation) now agree at idx=53/54 @ 11:33-11:34 for `case_ma10_reject_2026_03_09`.

## ID Mapping Table

| rule_id | case_id | segment_id | checkpoint_key (training trigger) | 页面入口 |
|---|---|---|---|---|
| `support_ma10` | `case_ma10_support_2026_01_07` | `seed_01` | `trend_ok`, `touch_ma10`, `confirm_bar`, `stop_defined` | `#module/ma10`, `#case/…`, `#training/ma10` |
| `reject_ma10` | `case_ma10_reject_2026_03_09` | `seed_03` | `trend_ok`, `touch_ma10`, `confirm_bar` | `#module/ma10`, `#case/…` |
| `reject_ma10` | `case_ma10_edge_2026_02_03` | `seed_04` | partial | `#case/…` |
| `signal_b`, `vwap_distance_filter` | `case_signal_b_2026_03_25` | `seed_06` | `trend_ok`, `confirm_bar`, `reward_ok` | `#case/…` |
| `candle_body_quality` | `case_quality_anti_2026_02_13` | `seed_14` | `body_not_cross`, `confirm_bar` | `#mistake/err-06`, `#case/…` |
| `vwap_distance_filter` | `case_barrier_anti_2026_02_11` | `seed_09` | `reward_ok` | `#mistake/err-05`, `#case/…` |

## Wrong Directions

- Do not parse free-text Markdown rules at runtime.
- Do not put long-term mock data back into `shared.jsx`.
- Do not make a backend before the static JSON vertical slice proves the product loop.
- Do not create multiple full Kline engine instances on list/card pages — `mini` mode must stay SVG.
- Do not build separate `KlineMiniPreview`, `KlineEvidenceView`, `KlineReplayLab` implementations — one adapter + three modes.
- Do not turn the case page into a full trading terminal; evidence must stay teaching-focused.
- Do not treat `training/checkpoints.json` as a second source of truth.
- Do not expand all strategy modules before MA10 rule/case/segment/training linkage is working.
- Do not mutate engine private fields (`_scrollToHighlight`, `_playbackTimerId`, etc.) — prefer public API, and raise a gap when the API is missing.
