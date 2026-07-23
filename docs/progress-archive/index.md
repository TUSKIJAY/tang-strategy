# Progress Archive Index

本目录保存从 `PROGRESS.md` / `HANDOFF.md` 启动路径迁出的长期历史。归档不改变当前状态，也不授予任何计划权限。

| Period or topic | Source coverage | Archive path | Current-state redirect |
| --- | --- | --- | --- |
| 2026-07-21 → 2026-07-22 closed-plan lifecycles | Per-step entries of the date-rail plan (final summary retained) plus full lifecycles of the three 2026-07-21 completed plans and their OPT batch session records | [`2026-07-21-to-2026-07-22-plan-lifecycle-history.md`](./2026-07-21-to-2026-07-22-plan-lifecycle-history.md) | `../../PROGRESS.md` / `../../HANDOFF.md` |

## Archive Triggers

归档不是可选动作，满足任一触发条件即为当次 `PROGRESS.md` 更新任务的一部分：

1. **Plan 关闭触发**：一个 plan 迁入 `completed/`（或最终处置为 Rejected/Superseded/Terminated）后，下一次更新 `PROGRESS.md` 时必须把该 plan 的逐步 lifecycle 条目（proposal、review、foldback、activation、phase 记录）原文迁入本目录，`PROGRESS.md` 只保留最终 disposition 总结一条。
2. **体量触发**：`PROGRESS.md` 正文条目超过 10 条时，先把最旧的已关闭条目（含已被更新 plan 取代的旧 disposition 总结）迁入本目录，再追加新条目。机器信号：`python scripts/check-startup-doc-budget.py` 对 `PROGRESS.md` 输出 `archive_required=true` 即视为本条触发——它是归档义务，不是可忽略的 advisory。
3. 每次归档同步更新上表，并随所属任务一起提交。

## Archive Rules

- 先保持当前状态文档中的索引和 redirect，再迁移长历史。
- 保存原始事实、日期和证据路径，不把归档摘要当作当前真相。
- `HANDOFF.md` 只保留当前恢复点；历史会话叙述进入本目录。
