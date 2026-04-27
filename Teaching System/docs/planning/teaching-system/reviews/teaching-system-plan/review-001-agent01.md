# Tang 策略教学系统 Plan Review — agent01

> 评审人：agent01
> 日期：2026-04-24
> 评审对象：
>   - `docs/planning/tang-strategy-teaching-system-plan.md`（v0.1，1155 行）
>   - `dist/Tang 策略教学系统.html`
>   - `dist/shared.jsx`、`pages-1.jsx`、`pages-2.jsx`
> 评审范围：信息架构、页面实现完成度、设计语言一致性、数据/规则管线
> 不评审：交易策略本身、K 线引擎内部实现

---

## 一句话判断

Plan 扎实，demo shell 完成度超出预期（7 个页面全部跑通，数据 mock 就位）。但 plan 与 demo 在 **3 处直接分叉**，demo 与 `个人设计语言规范.md` 在 **5 处显著偏离**，K 线三档与 Rule Contract 管线仍为 **0%**。建议**停止摊面铺页面**，先打穿一条垂直线验证 K 线接入的真实难度。

---

## 现状盘点

### Plan 侧

- 覆盖产品定位、核心原则、一级模块、K 线展示分级、数据与内容管线、案例剧场结构、页面清单、实施阶段、待讨论问题
- 6.3 节已确定 14 条设计决策，命名统一中文
- 第 8 节 6 项 open question 未决

### Demo 侧

- HTML shell + 3 份 JSX（约 49KB 源码）
- **7 个页面全部实现**：策略地图、策略章节、案例剧场、模块训练、错误日志、规则库、案例档案
- 4 份 mock 数据写死在 `shared.jsx`：MODULES (6)、CASES (6)、RULES (6)、MISTAKES (6)
- K 线全部用 `KlinePlaceholder` 占位
- 路由：hash-based，7 条

---

## 核心发现

按严重程度排序。

### Finding 1 [high] 章节预览抽屉：plan 有，demo 没做

- plan 6.4.2 / 6.5.1 写了完整 spec（固定结构、内容要求、视觉锚点要求）
- demo `HubPage` 的 module 卡直接跳 `module/${id}`，无抽屉
- hub 卡本身已包含 `desc` + tags + "进入策略章节" 按钮 — 等于把抽屉内容铺到了 hub 卡上

**建议**：删掉抽屉，plan 同步改为「hub 卡 = 章节预览」。再加一层抽屉就是「点一下看简介 → 再点一下进去」的冗余。

### Finding 2 [high] 错误日志 → 错误详情缺一层

- plan 6.5.3 路径：错误日志 → **错误详情** → 反例证据 → 纠正训练 → 返回相关策略
- demo `MistakesPage` 直接跳 `training/${err.module}`，中间的错误详情页不存在
- 错误详情是反例系统的**证据锚点**，缺它则「错误 = 规则偏离记录」的核心理念无法落地

**建议**：补一个 `mistake/:id` 路由 + 页面，聚焦反例证据和纠正动作，不塞训练台。

### Finding 3 [high] 设计语言分叉（5 处）

demo 违反 `个人设计语言规范.md`：

| 项 | 规范要求 | demo 实际 | 影响 |
|---|---|---|---|
| 阴影 | 禁止 `box-shadow` | 全局 `shadow-[0px_4px_12px_rgba(23,22,19,0.05)]` | 违反「克制高级感」核心原则 |
| 主文字色 | `#1A1A19` | `#000`（大量使用） | 规范明文「禁止纯黑 #000」 |
| 强调色 | 橄榄 `#8B9A6D` fallback，同页 ≤ 3 色相 | 蓝 `#285fa2` + 红 `#ba1a1a` + 黑 `#000` | 同页 4 色相 |
| 页面背景 | `#FAF9F5` | `#f4f2ec` | 偏差小但未对齐 |
| 字体 | Noto Sans SC + JetBrains Mono | Newsreader + Work Sans + Space Grotesk + Inter + Material Symbols | **5 套 vs 规范 2 套** |

**建议**：强制二选一。要么让 demo 回归规范；要么更新 `个人设计语言规范.md` 承认 Academic Trading Journal 是新的视觉方向。**两份规范并存 = 后期每个新页面都要再争论一遍**。

### Finding 4 [medium] 导航双重覆盖不一致

- 左侧栏：6 模块 + 错误日志（**无**案例档案）
- 顶部导航：策略地图 / 案例剧场 / 规则库 / 案例档案（**无**错误日志）
- 用户找错误日志要看左边，找案例档案要看顶部 — 这个不对称会让人每次都先猜错

**建议**：明确语义分工
- 顶部 = 横向大区入口（站点级）
- 侧边 = 本次学习的纵向模块（会话级）

并让两者都覆盖所有入口，或显式写明为何不覆盖。

### Finding 5 [medium] K 线三档仍为 0%，且应重新定义为「一个组件 + preset」

- plan 第 4 节把 `KlineMiniPreview` / `KlineEvidenceView` / `KlineReplayLab` 描述为**三个独立组件**
- 实际上三档共享同一引擎，差异只在保留的控件、标注密度、交互范围
- demo `KlinePlaceholder` 已经隐式按一个组件 + 三 label 的思路占位

**建议**：落地时保持一个 `<KlineView mode="mini"|"evidence"|"lab">`。plan 侧统一「档 = mode」，避免后续开发者误解为三份代码库。

### Finding 6 [medium] Rule Contract 仍为内联 mock — 但导出成 JSON 几乎零成本

- `shared.jsx` 的 `RULES` 数组字段 `{id, name, type, status, setup, trigger, filter, invalid, module}`
- 这些字段与 plan 5.3.2 建议字段高度对齐
- **下一步成本极低**：把 `RULES` 抽出到 `rules/compiled/index.json`，前端 `fetch`。schema v0.1 自然浮现，Phase 4 提前启动

**建议**：本周内做。量级是 10 分钟到 1 小时。

### Finding 7 [medium] TrainingPage 只有 step 0-1 有真实题面

- step 2-6 硬编码 `['选项 A', '选项 B', '选项 C']`
- plan 6.5.5 写了 7 步分步作答流程，但每步具体题干内容并未产出
- 这是**内容设计工作量**，不是技术工作量

**建议**：不急。先处理 Finding 1-6，内容设计应在接入一个真实案例之后反推。

### Finding 8 [low] CasePage 右侧联动未实现

- plan 第 6 节末段承诺"点击 Trend Confirmed，图上高亮 5m 趋势区"等 5 条联动
- demo 右侧 `SignalValidation` 是静态 ✓ 列表
- 落地依赖 K 线引擎 annotation 能力

**建议**：K 线接入时一起做，不单独排期。

### Finding 9 [low] Hub 页「常见执行错误」section 是 plan 之外的加分项

- plan 6.4.1 未提
- demo 在 hub 底部加了 3 条高频错误，是很好的「从入口就暴露反例」设计
- 建议 plan 补上

---

## 开放问题

### 从 plan 第 8 节继承（agent01 推荐答案）

| # | 问题 | agent01 推荐 |
|---|------|------|
| 1 | 策略地图布局：流程线 / 模块网格 / 结合 | 现状（3 列卡片网格）够用，不再投入 |
| 2 | 内联 K 线讲解档是否需要真引擎 | 真引擎，但只跑一份实例，preset 切换 |
| 3 | Rule Contract JSON schema v1 字段 | 按 demo 现有 `RULES` 字段直接导出，后续按需扩 |
| 4 | Markdown → JSON 编译：脚本 vs LLM | 第一版直接写 JSON，不做编译管线 |
| 5 | Pine：JSON 自动生成 vs 手写 | 手写，Pine 是平台适配物，自动生成 ROI 低 |
| 6 | 案例档案第一版：140 天全量 vs 已审核片段 | 已审核片段，140 天候选池另设一表 |

### Review 新增待决策

| # | 问题 |
|---|------|
| A | **设计语言分叉**：让 demo 回归规范，还是更新规范承认 Academic Trading Journal 分支？ |
| B | **章节预览抽屉**：删掉并更新 plan，还是补回 demo？ |
| C | **导航双重覆盖**：统一都含所有入口，还是明确语义分工？ |

---

## 推荐下一步

**不是继续摊面铺页面，而是挑一条垂直线打穿。**

建议选 **MA10 核心入场** 一个模块，把「策略章节 → 案例剧场 → 模块训练」这条链上的 K 线证据图**真接入 v2 引擎**（单 case、单时间框架即可）。

理由：

1. 当前每个页面「看起来像」，但 K 线接入会立刻暴露一批 plan 里看不见的决策
2. `KlineEvidenceView` 要隐藏哪些控件、annotation 数据结构长什么样、5m/1m 切换触发什么事件 — 这些只有跑通一次才知道
3. 另外 5 个模块继续用 placeholder 等着，不是浪费

顺手任务（低成本高价值）：

- 把 `RULES` 数组导出成 `rules/compiled/index.json`
- 决策 A/B/C 并落成一次性的 plan 补丁

---

## 变更一览（如采纳本 review）

### Plan 侧

- 6.4.2 / 6.5.1 删除或改写为「章节预览 = hub 卡形态」
- 6.5.3 错误日志新增「错误详情」子页 spec
- 第 4 节 K 线三档：澄清为「一个组件 + 三 preset」
- 6.4.1 补充 Hub 页「常见执行错误」section
- 第 8 节 open question 按上表结论收敛
- 新增附录：视觉规范分叉说明（如选择更新规范路径）

### Demo 侧

- **视觉规范对齐（全局）**：移除 shadow / 替换 `#000` → `#1A1A19` / 色相收敛到 3 个以内
- 新增 `mistake/:id` 路由 + `MistakeDetailPage`
- `RULES` → `rules/compiled/index.json`（fetch 替代内联）
- `KlinePlaceholder` 接入 v2 引擎（先 MA10 案例，其他继续 placeholder）

---

*本 review 由 agent01 出品，范围限定于 plan v0.1 与 demo 当前快照。策略本身不做评审。*
