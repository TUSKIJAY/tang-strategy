# Optimization Intake SOP

本目录只记录项目摩擦、review follow-up 和候选改进。Optimization record 不授权实施，也不自动生成计划。

## Lifecycle Contract

1. 仅在用户启用优化记录模式后记录条目。
2. 记录留在 `docs/optimization/`；数量或时间累计不会自动触发 planning。
3. 只有用户明确要求转换某条记录或某个批次时，才能在 `docs/exec-plans/proposed/` 起草计划。
4. proposed 计划完成 review 并获得用户明确批准后，才能移动到 active。
5. 实施、验证与收尾完成后，计划进入 completed，并回链原记录。

## Batch Layout (required)

Each optimization batch is a **folder**, not a lone file at the directory root:

```text
docs/optimization/
  index.md
  SOP.md
  record-template.md
  <YYYY-MM-DD-batch-slug>/
    <YYYY-MM-DD-batch-slug>.md    # the record
    screenshots/                  # evidence images for this batch only
      <descriptive-name>.png
```

Rules:

- Put the record markdown and its screenshots **together** under the batch folder.
- Do **not** store optimization evidence screenshots under `design/references/` or other global design trees.
- `screenshots/` may be empty for text-only batches; keep the directory (optional `.gitkeep`).
- Link images with paths relative to the record file, e.g. `[label](./screenshots/foo.png)`.
- Root-level files in `docs/optimization/` are limited to `index.md`, `SOP.md`, and `record-template.md`.

## Record-Only Boundary

允许：

- 新增或更新优化记录（按上列 batch 文件夹布局）；
- 更新本目录索引；
- 按仓库规则更新 `PROGRESS.md` 与 `HANDOFF.md`。

不允许：

- 修改源码或运行时行为；
- 把 proposed 计划当成 active；
- 放宽项目安全、数据或发布边界；
- 仅因记录积累而自动实施。

## Status Terms

| Status | Meaning |
| --- | --- |
| `recorded` | 仅记录，不授权实施 |
| `needs-review` | 等待决定 |
| `promoted-to-proposed` | 已有 proposed 计划，仍无实施权限 |
| `active-plan` | 对应计划经批准并已激活 |
| `completed` | 已实施、验证并完成收尾 |
| `blocked` | 等待外部条件 |
| `superseded` | 已被其他记录、决策或计划取代 |
