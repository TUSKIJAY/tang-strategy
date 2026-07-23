# Optimization Intake SOP

本目录只记录项目摩擦、review follow-up 和候选改进。Optimization record 不授权实施，也不自动生成计划。

## Lifecycle Contract

1. 仅在用户启用优化记录模式后记录条目。
2. 记录留在 `docs/optimization/`；数量或时间累计不会自动触发 planning。
3. 只有用户明确要求转换某条记录或某个批次时，才能在 `docs/exec-plans/proposed/` 起草计划。
4. proposed 计划完成 review 并获得用户明确批准后，才能移动到 active。
5. 实施、验证与收尾完成后，计划进入 completed，并回链原记录。

形成正式、完整且范围清晰的 optimization record 后，按 [`docs/operating-modes.md` §2](../operating-modes.md#2-authority-and-task-scoped-local-commit) 默认把该记录及其直接索引更新做成一个 task-scoped local commit。用户明确说不 commit、记录仍是草稿，或文件归属不清时不提交。该默认不授权实施、push、PR、发布或远端动作。

## Batch Layout (required)

Each optimization batch is a **folder**, not a lone file at the directory root:

```text
docs/optimization/
  index.md
  SOP.md
  record-template.md
  <YYYY-MM-DD>-<NN>-<batch-slug>/
    <YYYY-MM-DD>-<NN>-<batch-slug>.md    # the record
    screenshots/                         # evidence images for this batch only
      <descriptive-name>.png
    mockups/                             # design mocks for this batch only
      <descriptive-name>.html
```

Rules:

- The batch folder name is `<YYYY-MM-DD>-<NN>-<batch-slug>`: record date, two-digit daily sequence, then the slug. The record markdown carries the identical name including `NN`.
- `NN` starts at `01` on each date and increments in creation order, so same-day batches sort chronologically instead of alphabetically by slug.
- A sequence number is assigned once. Never renumber, reuse, or close gaps — a batch that later becomes `superseded`, split, or merged keeps the number it was created with.
- Put the record markdown and its screenshots **together** under the batch folder.
- Do **not** store optimization evidence screenshots under `design/references/` or other global design trees.
- `screenshots/` may be empty for text-only batches; keep the directory (optional `.gitkeep`).
- Link images with paths relative to the record file, e.g. `[label](./screenshots/foo.png)`.
- Root-level files in `docs/optimization/` are limited to `index.md`, `SOP.md`, and `record-template.md`.

Design mocks follow the same containment rule as screenshots:

- A batch's design mocks live in the sibling `mockups/` folder as `<descriptive-name>.html`, one file per proposal surface. Do not put a mock at the batch-folder root, under `design/references/`, `frontend/`, or any global design tree.
- Omit `mockups/` entirely when the batch has no mock. Unlike `screenshots/`, it needs no placeholder.
- Each mock is a **self-contained single file**: inline CSS/JS, no CDN, remote font, remote image, or build step, so it opens from disk and hashes stably.
- Link mocks with paths relative to the record file, e.g. `[label](./mockups/foo.html)`, and cite the file the record actually relies on — not a draft.
- Drafts iterated under untracked `output/` are working material, never the record. Only the copy under `mockups/` is authoritative.
- Once a plan's evidence table pins a mock's SHA-256, that file is frozen. Later iteration creates `<descriptive-name>-v2.html` with its own pin instead of editing the pinned file in place.

Legacy note: batches created before 2026-07-23 predate `NN` and were renamed into this scheme in their original creation order, with all markdown references updated. Hash-pinned mock/mockup evidence inside those batches was left byte-identical, so a few of those HTML files still print their pre-rename path in body text while the SHA-256 values recorded in completed plans remain exactly as verifiable as they were before the rename. Two of those pins — `2026-07-20-03`'s `review-left-column.html` and `2026-07-21-09`'s `mock.html` — were already stale before 2026-07-23 because the files were edited in place after being pinned; the rename neither caused nor repaired that, and the freeze rule above exists to stop it recurring. Those batches also predate the `mockups/` rule — three of them keep a root `mock.html`, which stays where it is; the rule binds batches created from 2026-07-23 on.

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
