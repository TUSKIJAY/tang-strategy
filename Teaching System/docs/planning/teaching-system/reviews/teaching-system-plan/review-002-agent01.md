# Tang 策略教学系统 Plan Review — agent01 · round 2

> 评审人：agent01
> 日期：2026-04-24
> 评审对象：
>   - `docs/planning/teaching-system/tang-strategy-teaching-system-plan.md`（v0.2，1265 行）
> 评审范围：v0.2 相对 v0.1 的吸收度、残留风险、Phase 排序合理性
> 前置 review：`reviews/review-001-agent01.md`

---

## 一句话判断

v0.2 吸收得彻底，review-001 的 9 条 finding 全部有响应。但 **Phase 排序存在一次执行陷阱**、**视觉规范留了灰色地带**、**Phase 2 缺降级预案**。3 条 residual 全部可在 30 分钟内拍板。

---

## v0.2 吸收情况

review-001 → v0.2 响应映射：

| # | Finding | v0.2 落点 | 状态 |
|---|---|---|---|
| 1 | 删章节预览抽屉 | 6.4.2 改为「模块预览卡」；6.3 决策；8.1 | ✅ |
| 2 | 补错误详情页 | 新 6.4.7 + 6.5.3 路由 `mistake/:id`；6.3 决策 | ✅ |
| 3 | 设计语言回归规范 | §1 新增视觉规范决策段；8.1 | ⚠ 措辞模糊（见 Finding 2） |
| 4 | 导航语义分工 | 6.4.1「顶部=站点级 / 侧边=学习链路」；8.1 | ✅ |
| 5 | K线三档 = 一个组件 + mode | 第 4 节统一 `KlineView mode="*"`；命名表同步 | ✅ |
| 6 | Rule Contract 外置 | 5.3.2 v0.1 schema = demo 字段；5.4 第一版收敛；Phase 3 | ⚠ Phase 排序错（见 Finding 1） |
| 7 | Training 题面 | Phase 5 + 8.2 #4 | ✅ |
| 8 | CasePage 联动 | 8.2 #2 标待验证 | ✅ |
| 9 | Hub 底部常见错误 | 6.4.1 收入正文 | ✅ |

---

## 核心发现

按严重程度排序。

### Finding 1 [high] Phase 3 排序风险 — Rule Contract 外置应跟 Phase 2 并行或前置

**现状**：v0.2 Phase 3 = "Rule Contract JSON 外置"，排在 Phase 2 "MA10 垂直线与 K 线真实接入" 之后。

**为什么是风险**：

- Phase 2 要跑通"策略章节 → 案例剧场 → 模块训练"的 MA10 链路
- 其中策略章节页要展示规则契约，训练页要给"违反哪条规则"反馈
- 如果 Phase 3 还没做，MA10 链路会继续从 `shared.jsx` 内联 `RULES` 读
- Phase 3 真开始时，要把已经写进 React 组件的 MA10 规则字段回头拆出来——等于 Phase 2 的代码有一部分要重写

**成本对比**：

| 方案 | 实际工作量 |
|---|---|
| Phase 3 前置（Phase 2 前 10 分钟） | 抽 `RULES` 数组到 `rules/compiled/index.json`，前端加一次 `fetch`。1 小时内搞定 |
| Phase 3 后置（v0.2 现状） | Phase 2 完成后回头拆 MA10 相关字段；涉及 `ModulePage`、`TrainingPage` 读取路径修改；~3-4 小时 |

**建议**：

- Phase 3 降级为 Phase 2 的 **day-0 预备**（或明确并入 Phase 2 第一步）
- 理由：它不产生新能力，只是"把写死的 JS 对象换成 fetch JSON"，但会改变 Phase 2 所有数据读取路径

### Finding 2 [medium] 视觉规范"接近"措辞留了灰色地带

**现状**：v0.2 §1 视觉规范决策段写道：

> 主文字避免纯黑，使用**接近** `#1A1A19` 的墨色；页面底色**接近** `#FAF9F5`；

`个人设计语言规范.md` 里这两个值是精确的：

```
页面背景：  #FAF9F5     卡片背景：  #FFFFFF
主文字：    #1A1A19     辅助文字：  #6B6B66
```

**为什么是问题**：

- "接近"两个字会让下一个写样式的人自己拿捏—— `#1a1a1a`? `#1c1b1b`? `#171613`?
- demo 里已经存在 `#171613`、`#1c1b1b`、`#000` 三种"接近黑"共存的情况，正是"接近"留下的空间
- 设计语言的意义就是消除拿捏，精确值才能机械执行

**建议**：

- 改成精确值："主文字使用 `#1A1A19`；页面底色使用 `#FAF9F5`；卡片底色 `#FFFFFF`；辅助文字 `#6B6B66`"
- 如果是有意的妥协空间（比如 `Academic Trading Journal` 气质需要略不同的墨色），显式说明"为支撑 X 气质，主文字从 `#1A1A19` 调整为 Y"——有理由的偏离可以接受，无理由的"接近"会一直漂

### Finding 3 [medium] Phase 2 缺降级预案

**现状**：

- 8.2 待验证项 #1-2 把 kline-engine 的 React 生命周期、外部高亮能力列为待验证
- Phase 2 目标直接假设这些能力可用（"验证 1m / 5m 数据加载、标注高亮、隐藏未来走势、逐根推进"）
- 如果 #1 或 #2 证伪（引擎 React 挂载成本过高 / 外部高亮 API 不存在），Phase 2 怎么办？

**建议**：

Phase 2 开头加一条 **Spike（0.5-1 天）**：

```
Phase 2 - Step 0: Kline Engine 能力验证
  - 在 React 组件里挂载一次 kline-engine-v2.html
  - 测试：挂载 / 销毁 / 复用 / loadData 切换案例
  - 测试：外部调用高亮指定 K / 区间 / 均线
  - 测试：隐藏未来走势 + 逐根推进 API
  - 输出：能力清单 + 缺失项清单
  - 通过才进入 MA10 链路搭建；否则先补引擎能力，或用静态证据图降级
```

这不是官僚主义。是避免"MA10 搭一半发现引擎不支持高亮，回头改数据层"的返工。

---

## 开放问题

无新增。review-001 的 open question A/B/C 在 v0.2 已全部收敛。

---

## 推荐下一步

按优先级：

1. **立即** — 把 Phase 3 并入 Phase 2 day-0（改 plan 一行即可，代码 1 小时）
2. **本周** — §1 视觉规范改精确值
3. **Phase 2 启动前** — 加 Spike 条目

如果 3 条全部采纳，v0.2 → v0.3 的 diff 极小（plan 改 5-10 行），但实施阶段会少一次回炉。

---

## 变更一览（如采纳本 review）

### Plan 侧

- Phase 2 开头插入 Step 0: Kline Engine 能力验证（Spike 0.5-1 天）
- Phase 3 "Rule Contract JSON 外置" 合并为 Phase 2 Step 1
- §1 视觉规范决策段："接近 `#1A1A19`" → "`#1A1A19`"；底色同理
- 8.2 #1-2 从"待验证"升级为"Phase 2 Step 0 的完成标准"

### Demo 侧

- 无新增要求（review-001 已列）

---

*本 review 由 agent01 出品，聚焦 v0.2 相对 v0.1 的残留风险与 Phase 排序。不重复 review-001 已解决项。*
