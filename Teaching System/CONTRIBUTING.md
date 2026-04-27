# 项目协作规范

> 创建日期：2026-04-14
> 适用范围：本项目所有协作者（人类 + AI Agent）

---

## 一、目录结构

```

├── CONTRIBUTING.md             ← 本文件（协作规范）
├── src/                        ← 源代码
├── data/                       ← 数据文件
├── dist/                       ← 构建产物
├── reference/                  ← 参考资料
├── _archive/                   ← 归档文件
└── docs/                       ← 文档
    ├── ROADMAP.md              ← 版本路线图
    └── planning/               ← 版本计划
        ├── v0.2-kline-refactor/
        │   ├── kline-refactor-plan.md       ← plan
        │   ├── kline-refactor-acceptance.md ← 验收报告
        │   └── reviews/                     ← review 文件夹
        │       ├── r001-agent01.md
        │       └── r001-agent02.md
        ├── v0.3-data-fix/
        │   ├── data-fix-plan.md
        │   └── reviews/
        └── v0.4-case-quality/
            ├── case-quality-plan.md
            └── reviews/
```

**规则：**

1. 每个版本一个文件夹，命名 `v{X.Y}-{短标签}` 或 `{功能名}`
2. Plan 和 Acceptance 放在文件夹根目录
3. Review 放在 `reviews/` 子文件夹

---

## 二、文件命名

### Plan 文件

格式：`{短标签}-plan.md`

短标签 = 文件夹名中去掉版本号前缀的部分。

| 文件夹名 | Plan 文件名 |
|----------|-------------|
| `v0.2-kline-refactor` | `kline-refactor-plan.md` |
| `v0.3-data-fix` | `data-fix-plan.md` |
| `v0.4-case-quality` | `case-quality-plan.md` |
| `daily-review` | `daily-review-plan.md` |

> **目的**：单独拿出来就能识别，不需要靠路径。

### Review 文件

格式：`r{轮次}-{agent标识}.md`

- 轮次：三位数字，从 `001` 开始
- Agent 标识：`agent01` / `agent02`（固定两位数字）

| 示例 | 含义 |
|------|------|
| `r001-agent01.md` | 第 1 轮 review，Agent 01 |
| `r001-agent02.md` | 第 1 轮 review，Agent 02 |
| `r002-agent01.md` | 第 2 轮 review（针对修订稿），Agent 01 |

> **轮次定义**：同一版本的 plan 每经历一次 revise → 修订 → 再审，轮次 +1。同一轮中不同 agent 的 review 共享轮次号。

### Acceptance 文件（验收报告）

格式：`{短标签}-acceptance.md`

| 文件夹名 | Acceptance 文件名 |
|----------|-------------------|
| `v0.2-kline-refactor` | `kline-refactor-acceptance.md` |
| `v0.3-data-fix` | `data-fix-acceptance.md` |

> 验收报告在 plan 执行完成后编写，与 plan 同级存放。

---

## 三、Git 版本管理

### 核心原则

> **不要在文件名中放版本号。** 版本历史由 Git 管理。

- ❌ 错误：`plan-v1.md`, `plan-v2.md`
- ✅ 正确：只维护一个 `data-fix-plan.md`，每次修订后 `git commit`

### Commit Message 格式

```
<类型>(<范围>): <简要描述>

类型：
  feat      新功能
  fix       修复
  docs      文档变更
  review    评审意见
  refactor  重构
  chore     杂务/清理
```

### Review 提交规范

```bash
git add <file>
git commit -m "review(<agent-id>): round N - <简要说明>，裁决 <approve/revise/reject>"
```

示例：
```bash
git commit -m "review(agent01): round 2 - 合并策略硬编码风险，裁决 revise"
git commit -m "review(agent01): round 3 - 所有问题已解决，裁决 approve"
```

### 查看历史版本

```bash
# 查看某个文件的所有修订记录
git log --oneline <path-to-file>

# 查看两个版本之间的差异
git diff <commit-id-1> <commit-id-2> -- <path-to-file>

# 查看某个历史版本的完整内容
git show <commit-id>:<path-to-file>
```

---

## 四、Plan 文档结构

每份 plan **必须**包含以下章节（顺序固定）：

```markdown
# {版本号} — {一句话标题}

> 版本：vX.Y
> 代号：{短标签}
> 状态：待确认 | 待执行 | 执行中 | 已完成
> 创建日期：YYYY-MM-DD
> 最后修订：YYYY-MM-DD（{修订原因}）
> 前置条件：{依赖版本或"无"}

---

## 一、背景
为什么要做这件事。问题来源、上游验收反馈等。

## 二、任务分解
每个 Task 独立成小节，格式：

### Task N: {任务名} {优先级 emoji}
- **问题分析**：是什么 / 为什么
- **修改方案**：怎么改（含伪代码/方案对比）
- **修改文件**：唯一修改源文件（或多文件时逐一列出）
- **验收标准**：checkbox 列表，可测试、可量化
- **预估工时**：Xh

## 三、执行顺序
ASCII 流程图或有序列表，标注串行/并行理由。

## 四、待决策项（可选）
需要人工确认的选项。决策后标注结果。

## 五、风险
表格：风险 | 概率 | 缓解措施

## 六、Review 修订记录（如有）
按轮次记录 review 反馈及处置。

## 七、变更记录
表格：日期 | 变更内容
```

**优先级标记**：🔴 P1 | 🟡 P2 | 🟢 P3

**状态流转**：待确认 → 待执行 → 执行中 → 已完成

> **简化原则**：如果某章节不适用（如没有待决策项），可以省略，但不要打乱已有章节的顺序。

---

## 五、Review 文档结构

使用 `role-reviewer` skill 的标准输出格式：

```markdown
# 交付物评审意见

**审核对象**：{plan 文件名}（{版本标识，如 v0.4 R2}）

## 整体判断
**裁决**：approve | revise | reject
**置信度**：high | medium | low

## 总体评价
2~3 段整体评价。

## 问题清单

### 严重问题
编号列表。无则写"无"。

### 中等问题
编号列表。无则写"无"。

### 轻微问题
编号列表。无则写"无"。

## 未验证项
列出因信息不足未能验证的内容。

## 裁决理由
总结裁决依据。
```

每个问题条目格式：

```markdown
N. **{问题标题}**
   - 位置：{章节/Task/行}
   - 问题描述：{具体问题}
   - 影响范围：{影响什么}
   - 改进建议：{怎么改}
```

---

## 六、Acceptance 文档结构（验收报告）

```markdown
# {版本号} — 验收报告

> 验收日期：YYYY-MM-DD
> 验收对象：{交付物文件列表}
> 验收方式：{方法概述}
> 验收结论：**通过** | **有条件通过** | **不通过**

---

## 一、验收范围
本次覆盖的内容 + 明确排除的内容。

## 二、验收方法
按方法分小节说明具体做了什么检查。

## 三、已确认通过项
按功能/模块分小节，简要说明通过情况。

## 四、未通过项 / 风险项
每项格式：

### N.M {优先级标记}：{问题标题}
- **文件**：涉及的源文件
- **问题**：具体描述
- **影响**：影响范围
- **结论**：需要怎么处理

## 五、数据抽查结果（如适用）
结构校验、数值抽查等量化结果。

## 六、验收判断
综合结论 + 升级为正式基线的退出条件。

## 七、建议的收口动作
有序列表，按优先级排序，附工时预估。

## 八、备注（可选）
补充说明、复验计划等。
```

**验收结论三选一**：
- **通过** — 可直接作为正式基线
- **有条件通过** — 可作为迭代基线，完成指定修复后升级为正式基线
- **不通过** — 需返工后重新验收

---

## 七、快速检查清单

开始写 plan 前过一遍：

- [ ] 文件名符合 `{短标签}-plan.md` 格式
- [ ] 元信息区（版本/状态/日期/前置条件）完整
- [ ] 每个 Task 都有：问题分析、修改方案、修改文件、验收标准、预估工时
- [ ] 验收标准是可测试的（不是"看起来对"）
- [ ] 执行顺序考虑了文件写入面冲突
- [ ] 风险表至少包含 2 项

写 review 前过一遍：

- [ ] 审核对象写清楚了（文件名 + 版本）
- [ ] 裁决三选一：approve / revise / reject
- [ ] 问题按严重/中等/轻微分级
- [ ] 每个问题都有改进建议

写 acceptance 前过一遍：

- [ ] 文件名符合 `{短标签}-acceptance.md` 格式
- [ ] 验收结论三选一：通过 / 有条件通过 / 不通过
- [ ] 验收范围写清楚了覆盖和排除的内容
- [ ] 未通过项标注了优先级（P1/P2/P3）
- [ ] 有条件通过时，写明了退出条件

---

## 八、变更记录

| 日期 | 变更 |
|------|------|
| 2026-04-14 | 初始版本 — Git 工作流 + commit 规范 |
| 2026-04-14 | 合并 CONVENTIONS.md — 统一文件命名、目录结构、文档模板（plan / review / acceptance） |
