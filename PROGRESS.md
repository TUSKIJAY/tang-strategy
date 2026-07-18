# Progress

## Current Status

2026-07-18：`codex/project-harness` 分支的 `minimal` harness 改造已完成并通过验证。现有 `AGENTS.md`、`CLAUDE.md` 和扁平 `docs/` 结构均保留；本次范围只包含 agent 启动、稳定章程、进度、handoff、机器配置和结构检查，没有修改业务逻辑或每日数据。`main` 仍停留在改造起点 `c262ba0`。

## Navigation

| Need | Location |
| --- | --- |
| Stable project rules | `INSTRUCTIONS.md` |
| Current resume point | `HANDOFF.md` |
| Harness configuration | `.harness/config.json` |
| Detailed project docs | `docs/` |

## In Progress

- [ ] 无；改造与验证已完成，等待维护者决定是否 commit/merge。

## Blocked

- [ ] 无；若验证或权限存在阻塞，在此记录证据和解除条件。

## To Do

- [ ] 由维护者决定是否提交 `codex/project-harness` 上的改造；不要直接改动 `main`。

## Completed

- [x] 2026-07-18 — 从 `main@c262ba0` 创建 `codex/project-harness`；`main` 引用未移动。
- [x] 2026-07-18 — 完成只读 audit 与 preview，选择不破坏扁平 `docs/` 约束的 `minimal` profile。
- [x] 2026-07-18 — 安装 5 个缺失 harness 文件并手工扩展现有 `AGENTS.md`；未覆盖 `CLAUDE.md`。
- [x] 2026-07-18 — skill validator `100/100`，本地 harness checker PASS，`git diff --check` PASS。
- [x] 2026-07-18 — 后端 TradingView quality-gate tests `4/4`、`compileall`、前端 `npm run build` 全部通过。后端测试使用临时隔离环境安装 `requirements-tv.txt` 中固定的 calendar 依赖。

## Historical Redirects

长期历史仍由现有 Git 与项目文档承载；本文件只保留当前生命周期真相和检索指针。
