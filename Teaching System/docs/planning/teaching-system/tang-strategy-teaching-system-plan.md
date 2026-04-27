# Tang 交易策略教学系统实施计划

> 版本：v0.3  
> 日期：2026-04-24  
> 目标：搭建一个面向已有交易基础用户的策略复习、实盘判例展示、决策训练系统。  
> 边界：本计划不审核交易策略本身，策略定义与规则由外部审核流程提供。
> 本版修订：依据 `review-002-agent01.md` 与 `review-002-agent02.md` 收敛 v0.2 残留风险，前置 Rule Contract 外置、明确视觉 token、增加 K 线引擎 Spike 与降级预案，并补充模块预览卡的 HubPage 直接渲染方式。

---

## 1. 产品定位

本系统不是零基础交易教程，也不是交易软件终端，而是一本可交互的策略教科书。

核心用户是已经懂交易、但需要提高策略执行稳定性和胜率的用户。系统目标不是灌输基础知识，而是帮助用户把策略定义、实盘样本、反例识别、决策训练串成一条可重复练习的路径。

一句话定位：

> 把交易策略变成一套可以反复校准判断力的训练路径。

设计语言已确定为：

> Academic Trading Journal + Execution Playbook

参考方向来自 `stitch/` 下的重设计稿，尤其是：

- `strategy_hub`：策略地图首页方向
- `module_detail`：模块预览卡 / 定义预览方向
- `case_analysis`：案例剧场基础布局方向
- `mistake_navigator`：错误模式与反例导航方向

整体气质应保持冷静、克制、纸质研究日志感和执行手册感。避免金融大屏、炫酷量化平台、营销页和普通课程目录风。

视觉规范决策：

- `Academic Trading Journal + Execution Playbook` 是本项目的产品气质，不等于另起一套发散的视觉规范。
- 第一版视觉 token 应回归统一规范：主文字使用 `#1A1A19`；辅助文字使用 `#6B6B66`；页面底色使用 `#FAF9F5`；卡片底色使用 `#FFFFFF`；强调色优先使用 `#8B9A6D` 橄榄系，单页色相保持克制。
- 不使用全局投影制造卡片漂浮感；用边框、分隔线、留白、字号层级表达结构。
- 字体家族保持收敛。中文优先使用既定中文正文字体，数字 / 代码 / 数据标签可使用等宽字体；不要在同一页面混用多套英文字体。
- 当前 demo 如出现 `#000`、大面积蓝红强调色、全局 `box-shadow` 或过多字体，应按本计划回归规范。

用户可见命名统一使用中文。英文可以保留在内部组件名、数据字段、文件名和开发文档中，但导航、页面标题、按钮和模块名称应优先中文，避免中英混杂造成阅读负担。

建议中文命名：

| 内部/参考名 | 用户可见中文名 | 用途 |
|---|---|---|
| Hub | 策略地图 | 系统首页，进入策略学习路径 |
| Module Detail | 模块预览卡 | 策略地图中的章节预览卡，不作为独立抽屉 |
| Module Page | 策略章节 | 完整学习某个策略模块 |
| Analysis / Case Analysis | 案例剧场 | 单个实盘案例讲解与证据展示 |
| Playbook | 规则库 | Rule Contract 的可视化速查页面 |
| Archives | 案例档案 | 全部实盘样本的检索与归档 |
| Mistake Log | 错误日志 | 错误模式、反例与纠正训练 |
| Module Training | 模块训练 | 围绕单个策略模块的分步训练 |
| KlineView mode="mini" | K线缩略图 | 列表和卡片中的轻量预览 |
| KlineView mode="evidence" | K线证据图 | 章节和案例中的删减版证据图 |
| KlineView mode="lab" | K线回放训练台 | 完整训练 / 回放实验台 |

---

## 2. 核心设计原则

### 2.1 一屏只回答一个问题

页面不应把定义、案例、K线、评分、训练题全部堆到同一屏。

每个页面或状态只解决一个认知任务：

- 我现在要学什么？
- 这个策略怎么定义？
- 标准形态长什么样？
- 看着像但为什么不能做？
- 我自己会不会判断？
- 做错后应该怎么复盘？

### 2.2 深入浅出，循序渐进

推荐路径：

```text
策略地图
  -> 单个策略章节
  -> 策略定义
  -> 标准样本
  -> 反例对照
  -> 决策训练
  -> 复盘总结
```

### 2.3 K线是教学证据，不是页面装饰

所有 K 线示例应服务于一个具体教学目的：

- 证明一个定义
- 展示一个标准形态
- 拆解一个误判
- 训练一个决策点

不应为了“看起来专业”到处堆完整 K 线终端。

---

## 3. 系统一级模块

### 3.1 策略地图

系统首页或主入口。

作用：

- 展示整套策略体系的结构
- 帮用户选择学习路径
- 避免一上来进入复杂图表

初始模块建议：

- 顺势进场
- 大空间信号
- 不做区域
- K线质量
- 关卡判断
- 出场管理

### 3.2 策略章节

每个策略模块进入后，先展示章节封面。

章节封面只讲三件事：

- 这个策略解决什么问题
- 它在实盘中避免什么错误
- 学完这一章应该能判断什么

### 3.3 策略定义卡

策略定义采用固定模板，默认简洁，细节可展开。

字段建议：

- 一句话定义
- 成立条件
- 触发条件
- 过滤条件
- 失效条件
- 最常见误判
- 对应案例入口

### 3.4 实盘判例库

从 SPY 实盘数据中筛选符合策略定义的样本。

判例至少分三类：

- 标准例：看到就应该做
- 边缘例：可以做，但要降级处理
- 反例：看着像，但不能做

### 3.5 案例剧场

系统核心页面。

作用：

- 用 K 线引擎展示一个完整案例
- 分步揭示背景、触发、确认、出场和复盘
- 支持讲解模式与训练模式切换

### 3.6 训练模式

把案例变成题卡。

训练时隐藏答案和后续走势，让用户先做判断，再揭示标准答案。

题型建议：

- 做不做
- 做 CALL 还是 PUT
- 等不等下一根
- 是否减仓或出场
- 错在哪条规则

---

## 4. K线展示分级方案

为避免资源消耗过大，同时避免后续维护三套图表代码，K 线展示分三档，但工程落地统一为一个组件 / 适配层的三种模式。

工程组件建议：

```text
KlineView
  mode="mini"      // K线缩略图
  mode="evidence"  // K线证据图
  mode="lab"       // K线回放训练台
```

用户可见和设计沟通时仍使用以下中文名称：

- K线缩略图：列表和卡片中的轻量预览
- K线证据图：内联讲解 / 案例证据图
- K线回放训练台：完整训练 / 回放实验台

历史组件名 `KlineMiniPreview`、`KlineEvidenceView`、`KlineReplayLab` 可作为内部 alias 或 wrapper，但不应发展成三套互不共享的实现。

### 4.1 缩略图档

用于：

- 策略地图
- 章节卡片
- 案例列表

形式：

- 静态缩略图
- 极简 mini chart
- 无交互

目的：

- 快速识别形态
- 不加载完整 K 线引擎

### 4.2 内联讲解档

用于：

- 策略定义页
- 标准形态说明
- 反例对照说明
- 策略地图模块预览卡中的 Visual Anchor
- 策略章节中的视觉锚点
- 案例页中的证据图简化状态

形式：

- 简化版 K 线视图
- 隐藏复杂工具栏
- 只保留必要均线和关键标注
- 高度控制在 260-360px

目的：

- 像教材插图，而不是交易终端

组件模式：

```text
KlineView mode="evidence"
```

定位：

- 教学证据图
- 用于证明某个策略定义、标准形态或误判点
- 不是完整交易终端

保留能力：

- K 线主体
- 必要均线：通常只显示 MA10 / MA50 / MA200 / VWAP 中与当前案例相关的几条
- 1m / 5m 标签
- Heikin-Ashi / OHLC 状态标签
- 关键标注：Reject / Support / Break / Exit
- 简单 hover 或十字线数据
- 当前案例标题、时间与基础 OHLC 信息

隐藏或删除：

- 复杂工具栏
- 全部均线开关
- 主题切换
- 播放速度按钮
- 开发面板
- 过多指标按钮
- 全量操作控件

视觉要求：

> K线证据图应该像研究论文里的证据图，而不是 TradingView 或完整交易终端。

### 4.3 案例剧场档

用于：

- 单个案例详情
- 回放
- 训练
- 复盘

形式：

- 完整 K 线引擎
- 支持 1m/5m 切换
- 支持逐根推进
- 支持标注、答案揭示、训练反馈

资源策略：

- 同一时间尽量只维护一个完整 K 线引擎实例
- 切换案例时复用实例并调用 `loadData()`
- 列表页不创建多个完整 iframe/canvas
- K 线数据按需加载，不一次加载全部 140 天数据
- 案例优先使用切片数据，而不是整日数据

组件模式：

```text
KlineView mode="lab"
```

定位：

- 完整案例回放和训练实验台
- 只在单页案例剧场或训练页使用
- 支持逐根推进、答案隐藏、标注揭示和 1m / 5m 切换

---

## 5. 数据与内容管线

### 5.1 已有资产

- 原始策略图文页：`reference/汤总秘籍图文版.html`
- K线引擎：`dist/kline-engine/kline-engine-v2.html`
- SPY整日数据：`data/processed/SPY_YYYY-MM-DD.json`
- 教学片段集合：`data/processed/teaching_segments.json`

### 5.2 推荐管线

```text
人类审核源文件
  -> 规则转换 / 编译
  -> 机器可读 Rule Contract
  -> Pine / Scanner Config / LLM Pack / Frontend Manifest
  -> 数据扫描生成候选片段
  -> 人工精选标准例 / 边缘例 / 反例
  -> 生成教学切片 JSON
  -> 写入案例剧场与训练题
```

### 5.3 策略规则三层格式

策略规则不绑定为单一格式。建议分成三层，各层服务不同使用者。

#### 5.3.1 人类审核源文件

用途：

- 给策略审核人员阅读、批注、讨论、修订
- 保留自然语言解释、背景说明、争议点和审核意见
- 不要求前端或扫描脚本直接加载

推荐格式：

- Markdown

示例路径：

```text
rules/source/reject_ma10.md
```

#### 5.3.2 机器可读规则包

用途：

- 给前端、数据扫描脚本、案例生成脚本和 LLM 工作流加载
- 字段稳定、结构明确、可校验
- 作为运行时 Rule Contract

推荐格式：

- JSON

示例路径：

```text
rules/compiled/reject_ma10.rule.json
```

建议字段：

- `rule_id`
- `name`
- `version`
- `type`
- `status`
- `one_line_definition`
- `setup`
- `trigger`
- `filters`
- `invalid_conditions`
- `entry_rule`
- `exit_rule`
- `common_mistakes`
- `case_requirements`

第一版 Rule Contract 可以直接从当前前端 mock 的 `RULES` 字段收敛为 v0.1 schema：

- `id`
- `name`
- `type`
- `status`
- `setup`
- `trigger`
- `filter`
- `invalid`
- `module`

第一步目标不是一次定义完美 schema，而是先把内联 mock 移出 `shared.jsx`，落到 `rules/compiled/index.json`，让前端从运行时 JSON 读取规则。

#### 5.3.3 平台与脚本适配格式

用途：

- TradingView 辅助观察
- 本地 SPY 数据扫描
- LLM 解释、出题、复盘反馈
- 前端模块索引和展示顺序

可选格式：

- Pine：用于 TradingView 可视化辅助
- Python / JS config：用于扫描脚本
- LLM JSON Pack：用于 LLM 读取策略语义、生成解释和训练题
- Frontend Manifest：用于前端加载策略目录、章节顺序和案例映射

示例目录：

```text
rules/
  source/
    reject_ma10.md
  compiled/
    reject_ma10.rule.json
  pine/
    reject_ma10.pine
  llm/
    reject_ma10.llm.json
  index.json
```

关键原则：

> Markdown 是人类审核语义源，JSON 是运行契约，Pine 和其他配置是平台适配物。

### 5.4 脚本加载与转换要求

运行脚本不应直接依赖自由文本 Markdown。Markdown 标题、措辞和段落顺序可能变化，直接解析会很脆。

长期推荐做法：

1. 人类先审核 `rules/source/*.md`
2. 通过转换脚本或 LLM 辅助生成 `rules/compiled/*.rule.json`
3. 人工确认 JSON 是否忠实表达审核结果
4. 扫描脚本、前端和 LLM 工作流只加载 compiled JSON / manifest
5. Pine、LLM pack、scanner config 从 compiled JSON 派生

第一版收敛：

1. 直接人工维护 `rules/compiled/index.json`
2. 前端先 `fetch` compiled JSON，替代内联 `RULES`
3. Markdown 源文件继续作为审核语义源，但暂不做自动编译
4. Pine 先作为独立人工适配文件维护，不强行从 JSON 自动生成
5. 等 MA10 垂直线跑通后，再决定是否补自动编译脚本

后续可补充的脚本：

- `compile_rules.py` 或 `compile_rules.js`
- `validate_rule_contract.py`
- `build_frontend_manifest.py`
- `build_pine_from_rule.py`
- `build_llm_rule_pack.py`

### 5.5 案例交付字段

每个教学案例建议包含：

- `case_id`
- `rule_id`
- `grade`：standard / edge / anti
- `ticker`
- `date`
- `window_start`
- `window_end`
- `preheat_bars`
- `initial_timeframe`
- `decision_bar`
- `answer`
- `explanation`
- `mistake_tags`
- `annotations_1m`
- `annotations_5m`

### 5.6 最小前端契约与训练步骤模型

为避免前端继续停留在 mock 产品壳阶段，第一版应先补一个最小可运行的前端数据契约。它不是后端接口，也不是复杂平台化数据层，而是静态 JSON / 构建期 JSON，用来把策略文档、案例、K 线切片和训练题串成同一条链路。

第一版建议固定四类运行时数据：

```text
rules/compiled/index.json          // Rule Contract：规则定义与审核状态
cases/index.json                   // Case Manifest：案例目录、样本类型、关联规则、关联切片
data/processed/teaching_segments.json
                                   // Segment Source：K 线切片、annotations、derived.checkpoints
training/checkpoints.json          // 可选：训练题面覆盖与人工修订；没有时可先从 segment checkpoints 派生
```

前端页面的数据依赖应收敛为：

| 页面 | 主要读取 | 用途 |
|---|---|---|
| 策略地图 | `rules/compiled/index.json` + `cases/index.json` 摘要 | 展示模块、入口、样本数量与高频错误 |
| 策略章节 | Rule Contract + 相关 Case Manifest | 展示定义、规则契约、标准例 / 边缘例 / 反例 |
| 案例剧场 | Case Manifest + Segment Source | 加载 K 线证据图、讲解步骤、右侧验证栏 |
| 模块训练 | Case Manifest + Segment checkpoints / `training/checkpoints.json` | 生成 7 步题面、标准答案、错因反馈 |
| 错误详情 | mistake tags + rules + cases | 从错误反查规则、反例和纠正训练 |

核心对象关系：

```text
Rule
  -> Case.rule_ids
  -> Case.segment_id
  -> Segment.derived.checkpoints
  -> Training decision_steps
```

`teaching_segments.json` 中已有的 `derived.checkpoints` 应成为第一版训练编排的起点，而不是另起一套纯手写题库。训练页可以先把 checkpoint 映射成 7 步题面：

| 训练步骤 | 优先映射字段 |
|---|---|
| 环境判断 | `regime_5m` / `trend_ok` / `ma_alignment_ok` |
| 观察条件 | `nearest_barrier` / `barrier_distance_pct` / `vwap_side` |
| 触发判断 | `touch_ma10` / `rule_events` / `decision_bar` |
| 过滤检查 | `body_not_cross` / `reward_ok` / `forbidden_absent` |
| 执行动作 | `answer` / `entry_rule` / `stop_defined` |
| 出场计划 | `exit_rule` / `stop_price` / 目标关卡 |
| 复盘标签 | `grade` / `mistake_tags` / `teaching_focus` |

如果 `derived.checkpoints` 字段不足，第一版不要马上补复杂后端或扫描器，而是在 `training/checkpoints.json` 中人工补齐该案例的题面和解释。等 MA10 垂直链路跑通后，再决定是否把这层人工补丁反向沉淀到规则编译或切片脚本里。

第一版 Case Manifest 建议字段：

```jsonc
{
  "case_id": "case_ma10_support_2026_01_07",
  "title": "标准 Support MA10：回踩后延续",
  "grade": "standard",
  "module_id": "ma10",
  "rule_ids": ["support_ma10"],
  "segment_id": "seed_01",
  "date": "2026-01-07",
  "window": { "start": "11:35", "end": "12:11", "preheat": 30 },
  "decision_bar": { "timeframe": "1m", "bar_index": 31, "time": "11:36" },
  "mistake_tags": [],
  "lesson": "5m 多头排列下，1m 回踩 MA10 但实体未破，确认 K 延续上涨。"
}
```

第一版训练步骤建议字段：

```jsonc
{
  "case_id": "case_ma10_support_2026_01_07",
  "steps": [
    {
      "step": "环境判断",
      "checkpoint_keys": ["trend_ok", "ma_alignment_ok"],
      "question": "5分钟方向是否清楚？",
      "options": ["趋势清晰，看多", "趋势清晰，看空", "方向不明确，不做"],
      "answer": "趋势清晰，看多",
      "rule_ids": ["support_ma10"],
      "explanation": "5m 趋势为 bullish，均线为多头排列，允许进入 1m 观察。"
    }
  ]
}
```

关键原则：

- 前端不直接解析自由文本 Markdown。
- 前端不从 `shared.jsx` 维护长期 mock 数据。
- 第一版不需要后端；静态 JSON 足够完成 MA10 垂直链路。
- `derived.checkpoints` 是训练编排起点；人工题面 JSON 是补洞层，不是另一个事实源。
- `case_id`、`rule_id`、`segment_id`、`checkpoint_key` 必须稳定，后续页面联动都靠这些 ID。

---

## 6. 案例剧场初步结构

案例剧场应是系统最重的页面，但信息仍要分步出现。

已确定的打开方式：

- 策略地图中的模块卡承担第一层章节预览，不再额外加右侧抽屉
- 完整案例学习和训练使用单页沉浸式案例剧场
- 单页剧场用于深度复盘和分步训练

基础布局参考 `stitch/case_analysis/screen.png`：

- 左侧：策略导航 / 模块入口
- 中间：案例证据区
- 右侧：Signal Validation + Execution Metrics
- 下方：Technical Context / 复盘说明

中间案例证据区应替换为自研 K 线引擎删减版：

```text
KlineView mode="evidence"
```

它用于案例讲解页的主要 K 线展示，不使用完整终端控件。完整回放和训练再进入 `KlineView mode="lab"`。

建议布局：

```text
顶部：案例标题 + 类型 + 时间 + 策略标签

左侧：讲解步骤
  1. 背景
  2. 等待
  3. 触发
  4. 确认
  5. 出场
  6. 复盘

中间：K线引擎

右侧：当前决策面板
  - 当前应该做什么
  - 依据哪条规则
  - 不能做的原因
  - 常见误判

底部：答案展开 / 复盘笔记 / 相似案例
```

更贴近当前设计稿的落地版本：

```text
左侧固定导航
  - Environment
  - MA10 Support / Reject
  - Signal B
  - Candle Quality
  - Mistake Log

顶部轻导航
  - 策略地图
  - 案例剧场
  - 规则库
  - 案例档案

主内容
  - Case Study 标题
  - KlineView mode="evidence" 证据图
  - Technical Context

右侧验证栏
  - Signal Validation
  - Execution Metrics
  - View Full Log / Enter Replay
```

右侧验证栏后续应与 K 线证据图联动：

- 点击 `Trend Confirmed`，图上高亮 5m 趋势区
- 点击 `MA10 Trigger`，图上高亮触发 K
- 点击 `VWAP Distance`，图上高亮目标空间
- 点击 `Candle Quality`，图上高亮实体 / 影线质量
- 点击 `Stop Defined`，图上高亮失效位置

### 6.1 讲解模式

讲解模式按步骤展开：

- 先显示背景
- 再显示触发前结构
- 标出关键 K
- 揭示标准决策
- 显示后续走势
- 总结复盘要点

### 6.2 训练模式

> v0.4 训练页方向更新（2026-04-25）：下一版模块训练不再以“7 步规则问答”作为主交互，而改为隐藏未来走势的盘中 Replay Drill。用户逐根推进 K 线，在任意可见 bar 做出 `等待 / 做多 / 做空 / 放弃` 动作，系统先揭示后续走势再按标准窗口和理由复盘。旧 7 步模型保留为历史设计和 checkpoint 数据来源，不再作为下一阶段实现蓝图。执行细节见 `training-replay-drill-redesign-plan.md`。

训练模式隐藏答案：

- 隐藏后续走势
- 隐藏教学标注
- 只显示到某根 K
- 用户分步作答
- 再揭示答案和错因

分步作答建议：

1. 5分钟方向是否清楚？
2. 当前是否进入观察？
3. 1分钟是否触发？
4. 目标方向空间是否足够？
5. 当前应该做、等，还是不做？
6. 如果进场，止损依据在哪里？
7. 后续出现关键 K 后，应该减仓、止盈、止损还是继续持有？

---

## 6.3 已确定设计决策

- 用户可见导航和页面命名统一使用中文；英文仅用于内部组件名、数据字段和文件名
- 首页采用策略地图，而不是今日训练入口
- 案例长度按策略和教学目的按需切片，不固定 60 / 90 / 120 根
- 训练题采用分步作答，而不是单次选择
- 策略审核源可以是 Markdown，但运行时规则包应转换成 JSON 或其他适配格式
- 内联 K 线讲解档主要出现在策略定义页 / 章节页
- 完整 K 线引擎主要出现在单页案例剧场
- K 线三档落地为同一个 `KlineView` 的 `mini` / `evidence` / `lab` 三种模式
- 视觉方向采用 Academic Trading Journal + Execution Playbook，但具体 token 回归统一视觉规范
- `case_analysis` 的中间 K 线区域使用 `KlineView mode="evidence"`，即 K 线引擎删减版
- 案例页不是完整交易终端，完整回放 / 训练能力进入 `KlineView mode="lab"`
- `mistake_navigator` 应作为核心模块保留，用于错误模式与反例训练
- 策略地图中的模块卡即第一版章节预览；不再增加右侧抽屉
- 策略章节负责规则学习，不承担完整案例训练
- 规则库是 Rule Contract 的可视化速查页面
- 模块训练使用分步训练流，重点诊断规则偏离
- 案例档案作为全部样本的检索与归档入口
- 错误日志卡片先进入错误详情页，不直接跳训练；纠正训练从错误详情发起
- 顶部导航承担站点级入口，侧边导航承担当前学习链路入口，二者语义分工固定

---

## 6.4 页面清单与中文命名

第一版建议保留以下用户可见页面与关键页面级组件：

### 6.4.1 策略地图

系统首页。用交易决策路径组织策略模块，而不是普通课程目录。

导航语义：

- 顶部导航：站点级入口，包含策略地图、案例剧场、规则库、案例档案、错误日志
- 侧边导航：当前学习链路入口，包含策略模块、相关规则、相关错误和当前训练进度
- 顶部与侧边不追求完全重复，但入口归属必须稳定，不让用户猜某个功能藏在哪一侧

主要入口：

- 环境判断
- MA10 核心入场
- 信号B
- K线质量
- 关卡空间
- 出场管理
- 错误日志
- 案例档案

策略地图底部可以保留「常见执行错误」区域，用 3-5 个高频错误把用户引向错误日志和反例训练。这是入口页的加分项，不应变成完整错误详情。

### 6.4.2 模块预览卡

策略地图中的模块卡承担第一版章节预览。

它不是独立路由，也不再使用右侧抽屉。用户在策略地图中完成快速判断：这个模块讲什么、长什么样、是否要进入完整策略章节。

前端实现上，模块预览卡就是 `HubPage` 中模块列表项的直接渲染内容。第一版不需要额外展开层；如后续需要更多信息，只允许在卡片内部做轻量展开态，不新增抽屉或中间路由。

内容：

- 模块标题
- 一句话副标题
- 定义与逻辑
- 视觉锚点
- 学习目标
- 进入策略章节

### 6.4.3 策略章节

完整学习某个策略模块的页面。

内容：

- 一句话定义
- Rule Contract 摘要
- K线证据图
- 标准例 / 边缘例 / 反例入口
- 相关错误
- 模块训练入口

### 6.4.4 案例剧场

单个实盘案例的证据展示页面。

内容：

- 案例标题
- K线证据图
- 信号验证
- 执行指标
- 技术背景
- 进入完整回放 / 训练

### 6.4.5 模块训练

围绕单个策略模块的分步训练页面。

内容：

- 训练进度
- 训练步骤
- K线回放训练台
- 当前问题
- 分步反馈
- 训练结果与偏差报告

### 6.4.6 错误日志

从错误模式反查策略规则的一级页面。

内容：

- 错误卡片
- 错误分类
- 违反规则
- 关联策略
- 反例证据
- 纠正训练
- 进入错误详情

### 6.4.7 错误详情

单个错误模式的证据页。

内容：

- 错误症状
- 违反规则
- 标准反例
- 看着像机会但不能做的原因
- K线证据图
- 纠正动作
- 进入纠正训练
- 返回相关策略

### 6.4.8 规则库

Rule Contract 的可视化速查页面。

内容：

- 规则搜索
- 规则分类
- 规则卡片
- 规则详情
- 相关案例
- 相关错误

### 6.4.9 案例档案

全部实盘样本的检索与归档页面。

内容：

- 按日期检索
- 按策略检索
- 按样本类型检索
- 按错误类型检索
- 进入案例剧场

---

## 6.5 关键页面详细规格

### 6.5.1 模块预览卡

定位：

> 在策略地图中用一张模块卡快速说明这个模块讲什么、长什么样、学完能解决什么问题。

它不是完整章节页，也不是训练页，也不作为额外抽屉。第一版避免「点一下看简介，再点一下进入」的冗余路径。

交互要求：

- 默认直接呈现在 `HubPage` 模块网格中
- 点击主按钮进入策略章节
- 点击卡片本身可以等同于进入策略章节，或只聚焦当前卡片，但不得打开独立抽屉
- 如需展示更多摘要，只在卡片内部轻量展开，不新增页面层级

固定结构：

```text
模块编号
模块标题
一句话副标题

定义与逻辑
视觉锚点
学习目标
进入策略章节
```

内容要求：

- 定义与逻辑控制在 4-6 行
- 视觉锚点优先使用 `KlineView mode="mini"` 或静态缩略图
- 学习目标使用可判断动作，而不是泛泛的“了解知识”
- 按钮文案使用中文，例如：`进入策略章节`
- 模块卡可展示 1-3 个标签，例如：趋势、触发、过滤
- 模块卡不展开完整 Rule Contract，完整规则进入策略章节

视觉锚点要求：

- 只展示少量 K 线
- 只保留本模块关键线，例如 MA10
- 标一个关键点
- 不出现播放器、时间轴、复杂 hover、完整均线组

### 6.5.2 策略章节

定位：

> 一页讲清一条策略的执行规则，并把用户引向标准例、边缘例、反例和训练。

它回答四个问题：

1. 这条策略的执行定义是什么？
2. 成立、触发、过滤、失效分别怎么判断？
3. 实盘里标准例、边缘例、反例长什么样？
4. 下一步应该看案例，还是进入训练？

推荐结构：

```text
章节标题区
  - 模块编号
  - 模块名称
  - 一句话执行原则
  - 策略标签

核心定义区
  - 一句话定义
  - 适用场景
  - 不适用场景

规则契约区
  - 成立条件
  - 触发条件
  - 过滤条件
  - 失效条件

视觉锚点区
  - K线证据图

案例入口
  - 标准例
  - 边缘例
  - 反例

相关错误
  - 错误日志入口

模块训练入口
```

设计原则：

- 先定义，再规则，再图例，再案例
- 不放完整 K 线终端
- 规则契约后续从 compiled JSON 读取
- 标准例、边缘例、反例必须并列出现，不能只展示盈利样本

### 6.5.3 错误日志与错误详情

定位：

> 从错误模式反查策略规则，用反例和纠正训练减少重复犯错。

核心理念：

> 错误不是情绪标签，而是规则偏离记录。

错误路径：

```text
错误日志
  -> 错误详情
  -> 反例证据
  -> 纠正训练
  -> 返回相关策略
```

路由建议：

```text
mistake/:id
```

错误日志列表中的卡片不应直接跳到训练页。先进入错误详情，让用户看到反例证据、违反规则和纠正动作，再从详情页进入针对性训练。

错误分类：

```text
进场错误
  - 提前进场
  - 追鱼尾
  - 没碰 MA10 就进
  - 忽略 5分钟背景

过滤错误
  - 关卡太近还做
  - 均线缠绕还做
  - K线质量差还做
  - IV 高还硬做

出场错误
  - 止损条件出现还扛
  - 到目标位不减仓
  - 衰竭出现不走
  - 卖飞后反手乱追

心态错误
  - 连亏后急着找回
  - 看到别人赚钱就重仓
  - 今天没机会也硬找机会
  - 做错后加仓摊平
```

错误卡字段：

- 错误编号
- 错误名称
- 高频程度 / 风险等级
- 一句话症状
- 违反规则
- 关联策略模块
- 典型案例数量
- 纠正入口

错误详情结构：

```text
错误名称
你在实盘里是怎么犯这个错的？

1. 症状
2. 违反的规则
3. 标准反例
4. 看着像机会但其实不能做
5. 纠正动作
6. 针对性训练
```

K 线展示：

- 使用 K线证据图
- 标出错误进场点、标准等待点、标准进场点、失效线、规则偏离位置
- 不使用完整回放训练台，除非进入纠正训练

### 6.5.4 规则库

定位：

> Rule Contract 的可视化浏览器，一本可搜索、可过滤、可复核的交易执行手册。

它不承担完整教学，不承担案例训练，只负责快速查规则。

页面结构：

```text
顶部
  - 规则库标题
  - 搜索框

左侧
  - 规则分类

中间
  - 规则卡列表

右侧
  - 选中规则详情
```

规则分类：

- 进场信号
- 过滤条件
- 出场规则
- 不做条件
- 错误纠正

规则卡字段：

- 规则编号
- 规则名称
- 规则类型
- 审核状态
- 成立条件摘要
- 触发条件摘要
- 失效条件摘要
- 关联案例数量
- 关联反例数量

右侧详情字段：

- 一句话定义
- 成立条件
- 触发条件
- 过滤条件
- 失效条件
- 出场规则
- 常见误判
- 相关案例
- 相关错误
- 版本 / 审核状态

数据来源：

```text
rules/index.json
rules/compiled/*.rule.json
```

K 线展示原则：

- 不放完整 K 线引擎
- 只允许 K线缩略图或小型静态图例
- 点击案例后进入案例剧场
- 点击训练后进入对应模块训练

### 6.5.5 模块训练

定位：

> 围绕一个策略模块，连续训练用户完成从环境判断到出场决策的完整流程。

它不是单个案例讲解，也不是题库列表。

入口：

- 从策略章节进入：标准例 + 边缘例 + 反例混合
- 从规则库进入：围绕某一条规则训练
- 从错误详情进入：围绕某个错误类型做纠正训练

页面结构：

```text
顶部
  - 训练标题
  - 当前进度

左侧
  - 训练步骤

中间
  - K线回放训练台

右侧
  - 当前问题
  - 选项 / 输入
  - 提交
  - 反馈
  - 下一步
```

训练步骤：

1. 环境判断
2. 观察条件
3. 触发判断
4. 过滤检查
5. 执行动作
6. 出场计划
7. 复盘标签

第一版题型：

- 单选：做不做、等不等、方向判断
- 多选检查：风险项、过滤项、错因判断
- 候选点选择：进场 K、止损位、减仓点

第一版不强求图上自由点击，先用候选点按钮或 bar 选择。

反馈格式：

```text
你的选择
标准判断
错因
违反规则
对应错误
建议复习
```

训练结果页：

```text
训练完成
正确率
主要偏差
建议复习
下一组训练
```

设计原则：

- 不做排行榜
- 不做游戏化徽章
- 不制造考试压力
- 重点是诊断规则偏离
- 文案保持交易复盘手册感

K 线展示：

- 使用 K线回放训练台
- 支持隐藏未来走势
- 支持逐根推进
- 支持隐藏 / 显示标注
- 支持根据答题步骤高亮不同区域

### 6.5.6 案例档案

定位：

> 全部实盘样本的检索与归档库。

它不是训练页，也不是规则页，而是用于快速定位样本。

典型使用：

- 找所有信号B标准例
- 找某个交易日的教学片段
- 找所有追鱼尾反例
- 找某个策略模块的边缘样本

筛选维度建议：

- 日期
- 策略模块
- 样本类型：标准例 / 边缘例 / 反例 / 待审核
- 错误类型
- 时间段：开盘 / 午盘 / 尾盘
- K 线周期：1m / 5m
- 审核状态

列表字段建议：

- 案例标题
- 日期与时间窗口
- 策略模块
- 样本类型
- 关联错误
- 审核状态
- 进入案例剧场

默认排序建议：

1. 已审核标准例
2. 已审核反例
3. 边缘例
4. 待审核候选
5. 最近新增

---

## 7. 实施阶段

### Phase 1：信息架构与视觉收敛

目标：

- 搭出策略地图
- 搭出章节页
- 搭出定义卡
- 搭出案例剧场静态结构
- 模块预览使用策略地图卡片，不做右侧抽屉
- 补出错误详情页骨架
- 统一顶部导航与侧边导航语义
- 视觉 token 回归本计划确定的克制规范

不做：

- 不做策略自动识别
- 不做真实训练评分
- 不做复杂数据管线

### Phase 2：数据契约预备与 MA10 垂直线

目标：

Step 0：Kline Engine 能力验证 Spike（0.5-1 天）

- 在 React 组件里挂载一次 `kline-engine-v2.html`
- 测试挂载、销毁、复用、`loadData()` 切换案例
- 测试外部调用高亮指定 K、区间、均线、止损位和错误点
- 测试隐藏未来走势与逐根推进能力
- 输出能力清单与缺失项清单
- 通过后进入 MA10 链路搭建

降级预案：

- 如果 React 挂载成本过高，先把 `KlineView mode="evidence"` 降级为静态证据图或预渲染轻量图，`mode="lab"` 延后
- 如果外部高亮 API 不存在，先补引擎 annotation 接口，或在数据层生成静态标注图
- 如果隐藏未来走势 / 逐根推进不可用，训练页先使用候选 bar 分步揭示，不做连续回放

Step 1：Rule Contract JSON 外置（day-0 预备）

- 将当前内联 `RULES` 抽出为 `rules/compiled/index.json`
- 前端从 compiled JSON 读取规则
- 固化 v0.1 Rule Contract schema
- 新建最小 Case Manifest：`cases/index.json`
- 明确 MA10 垂直链路的 `rule_id`、`case_id`、`segment_id`、`checkpoint_key` 映射
- 先让前端从静态 JSON 读取规则和案例目录，替代 `shared.jsx` 中长期 mock
- 保留 Markdown 源文件作为人工审核语义源
- 暂不实现 Markdown 到 JSON 的自动编译

Step 2：MA10 垂直链路

- 选择 MA10 核心入场作为第一条垂直链路
- 跑通 `策略章节 -> 案例剧场 -> 模块训练`
- 用一个真实案例接入 `KlineView mode="evidence"`
- 在训练页接入 `KlineView mode="lab"` 的最小回放能力
- 验证 1m / 5m 数据加载、标注高亮、隐藏未来走势、逐根推进
- 验证 `teaching_segments.json` 的字段是否支撑 7 步分步训练
- 验证 `derived.checkpoints` 能否映射为 `decision_steps`；不足字段先通过 `training/checkpoints.json` 人工补齐
- 验证规则 JSON、案例 JSON、annotation JSON 之间的 ID 映射
- 其他模块继续保留 placeholder，不扩大范围

### Phase 3：案例数据接入

目标：

- 将 `teaching_segments.json` 或教学切片接入案例剧场
- 支持案例切换
- 支持基础 annotations
- 案例档案第一版只接入已审核教学片段
- 140 天 SPY 数据作为候选池，不直接暴露给第一版案例档案

### Phase 4：训练模式

目标：

- 隐藏答案
- 用户分步作答
- 展示标准答案
- 记录错因标签
- 补齐 7 步训练题面，不再使用占位选项
- 引入错因反馈流：你的选择、标准判断、违反规则、对应错误、建议复习

### Phase 5：规则编译与样本库扩展

目标：

- 评估是否补 `compile_rules.py` 或 `compile_rules.js`
- 评估是否生成 LLM rule pack 和 frontend manifest
- Pine 先保持人工适配，除非出现明确重复维护成本
- 从 140 天 SPY 数据中持续补充标准例、边缘例和反例
- 建立样本质量评分
- 建立策略定义到样本的映射关系

### 7.6 Handoff Design：跨窗口交接设计

本项目必须按“随时可中断、随时可续跑”的方式组织执行，不能依赖单个 AI 窗口长期持有上下文。任何进入 Phase 2 之后的实作，都应同时维护一个轻量 handoff 文件，保证下一个窗口能在 5-10 分钟内恢复判断。

推荐固定交接文件：

```text
docs/planning/teaching-system/HANDOFF.md
```

如果进入较长阶段或多人并行，也可以追加阶段性文件：

```text
docs/planning/teaching-system/handoff-phase2-ma10.md
docs/planning/teaching-system/handoff-phase3-cases.md
```

#### 7.6.1 触发时机

以下情况必须更新 handoff：

- 完成一个 Phase / Step
- 改动了数据契约、路由、核心组件或 K 线引擎接入方式
- 验证出 K 线引擎能力缺口或降级方案
- 新增、删除或重命名 `rule_id`、`case_id`、`segment_id`、`checkpoint_key`
- 窗口即将结束，或当前上下文已经很长
- 开始交给另一个 agent / 另一个窗口继续

#### 7.6.2 Handoff 必填内容

`HANDOFF.md` 使用固定结构，避免下一窗口重新考古：

```markdown
# Tang Teaching System Handoff

## 当前阶段
- Phase:
- Step:
- 当前目标:
- 当前裁决: continue / blocked / needs-review

## 本轮已完成
- [文件] 做了什么
- [验证] 跑了什么，结果是什么

## 当前真实状态
- 规则数据:
- 案例数据:
- K线引擎:
- 前端页面:
- 训练题:

## ID 映射表
| rule_id | case_id | segment_id | checkpoint_key | 页面入口 |
|---|---|---|---|---|

## 下一窗口第一步
1. 先读什么文件
2. 先跑什么命令
3. 先验证什么页面或数据

## 不要走错的方向
- 不要把 mock 数据继续写进 `shared.jsx`
- 不要从自由文本 Markdown 直接驱动前端
- 不要在列表页创建多个完整 K 线引擎实例
- 不要在 MA10 垂直链路跑通前扩展所有模块

## 未解决问题
- 问题:
- 影响:
- 建议下一步:
```

#### 7.6.3 窗口恢复读取顺序

新窗口接手时，默认按以下顺序读取：

1. `docs/planning/teaching-system/HANDOFF.md`
2. `docs/planning/teaching-system/tang-strategy-teaching-system-plan.md`
3. `rules/compiled/index.json`（如果已存在）
4. `cases/index.json`（如果已存在）
5. `data/processed/teaching_segments.json`
6. 当前被改动的前端文件，如 `shared.jsx`、`pages-1.jsx`、`pages-2.jsx`
7. K 线引擎对接文档 `dist/kline-engine/INTEGRATION.md`

如果 `HANDOFF.md` 与 plan 冲突，以 plan 的已收敛决策为准；如果 `HANDOFF.md` 与当前代码冲突，以当前代码和实际验证结果为准，并立即更新 handoff。

#### 7.6.4 Handoff 与验收关系

每个 Phase 完成时，交付物至少包括：

- 实际代码 / 数据 / 页面改动
- 对应验证结果
- 最新 `HANDOFF.md`

没有 handoff 的阶段，不视为可交接完成。特别是 Phase 2 的 MA10 垂直链路，必须在 handoff 中明确：

- 当前使用的 `rule_id`
- 当前使用的 `case_id`
- 当前使用的 `segment_id`
- 训练步骤是否来自 `derived.checkpoints` 还是 `training/checkpoints.json`
- K 线引擎哪些能力已验证，哪些能力降级处理

---

## 8. 已收敛决策与待验证项

### 8.1 已收敛决策

| 问题 | 决策 |
|---|---|
| 策略地图布局 | 第一版使用模块卡片网格，底部补常见执行错误入口；不再投入流程线复杂设计 |
| 内联 K 线讲解档 | 使用真实引擎适配层，但通过 `KlineView mode="evidence"` 限制控件和交互 |
| K 线三档 | 三档是 mode，不是三套组件：`mini` / `evidence` / `lab` |
| Rule Contract v0.1 | 先按现有 `RULES` 字段导出 `rules/compiled/index.json`，作为 Phase 2 Step 1 的 day-0 预备 |
| 最小前端契约 | 第一版使用静态 JSON 串起 `Rule -> Case -> Segment -> Checkpoint -> Training`，不引入后端 |
| 训练步骤来源 | 优先从 `teaching_segments.json` 的 `derived.checkpoints` 派生；不足时用 `training/checkpoints.json` 人工补洞 |
| Markdown -> JSON | 第一版直接人工维护 JSON；自动编译延后到 MA10 垂直线跑通后评估 |
| Pine 适配 | 第一版手写维护，不从 JSON 自动生成 |
| 案例档案数据范围 | 第一版只接入已审核教学片段；140 天 SPY 数据作为候选池 |
| 章节预览 | 模块卡即章节预览；直接渲染在 `HubPage` 模块网格中，不做右侧抽屉或中间路由 |
| 错误路径 | 错误日志先进入错误详情，再进入纠正训练 |
| 视觉规范 | 保留 Academic Trading Journal 气质，但 demo 应回归精确 token：`#1A1A19`、`#6B6B66`、`#FAF9F5`、`#FFFFFF`、`#8B9A6D` |
| 导航结构 | 顶部是站点级入口，侧边是当前学习链路入口 |

### 8.2 Phase 2 完成标准与待验证项

1. Step 0 必须输出 `kline-engine-v2.html` 的挂载、销毁、复用和数据重载能力清单。
2. Step 0 必须确认外部高亮指定 K、区间、均线、止损位和错误点是否可行；不可行时记录缺失项与降级方案。
3. Step 0 必须确认隐藏未来走势与逐根推进是否可行；不可行时训练页先降级为候选 bar 分步揭示。
4. Step 1 必须完成 `rules/compiled/index.json` 外置，并让前端从 compiled JSON 读取规则。
5. Step 1 必须完成 MA10 垂直链路的 `cases/index.json` 最小 Case Manifest，并建立 `rule_id`、`case_id`、`segment_id` 的稳定映射。
6. Step 2 必须验证 `teaching_segments.json` 是否包含足够支撑 MA10 垂直线和 7 步分步训练的真实切片字段。
7. Step 2 必须验证 `derived.checkpoints` 到训练 `decision_steps` 的映射；不足字段必须落到 `training/checkpoints.json`，不能回到页面内硬编码。
8. Step 2 必须验证规则 JSON、案例 JSON、annotation JSON 之间的 ID 映射。
9. 训练模式 7 步题面需要从真实案例反推，不能长期停留在通用占位选项。
