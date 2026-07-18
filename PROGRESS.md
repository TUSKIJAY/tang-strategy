# Progress

## Current Status

2026-07-18：`codex/project-harness` 分支的 `minimal` harness 与 GitHub 联动已完成本地实现和验证。PR 指向 `main` 时可运行 harness/backend/frontend checks，并使用统一 PR 模板；不会自动更新状态文档、merge、发布 Pages 或修改每日数据。远端 feature branch 尚未 push，`main` 仍停留在 `c262ba0`。

## Navigation

| Need | Location |
| --- | --- |
| Stable project rules | `INSTRUCTIONS.md` |
| Current resume point | `HANDOFF.md` |
| Harness configuration | `.harness/config.json` |
| Detailed project docs | `docs/` |

## In Progress

- [ ] 无；本地实现与验证已完成，等待维护者决定是否 commit/push/open PR。

## Blocked

- [ ] 无；若验证或权限存在阻塞，在此记录证据和解除条件。

## To Do

- [ ] 由维护者决定是否 commit/push/open PR；若希望强制绿灯才能合并，需另行授权配置 `main` branch protection。

## Completed

- [x] 2026-07-18 — 从 `main@c262ba0` 创建 `codex/project-harness`；`main` 引用未移动。
- [x] 2026-07-18 — 完成只读 audit 与 preview，选择不破坏扁平 `docs/` 约束的 `minimal` profile。
- [x] 2026-07-18 — 安装 5 个缺失 harness 文件并手工扩展现有 `AGENTS.md`；未覆盖 `CLAUDE.md`。
- [x] 2026-07-18 — skill validator `100/100`，本地 harness checker PASS，`git diff --check` PASS。
- [x] 2026-07-18 — 后端 TradingView quality-gate tests `4/4`、`compileall`、前端 `npm run build` 全部通过。后端测试使用临时隔离环境安装 `requirements-tv.txt` 中固定的 calendar 依赖。
- [x] 2026-07-18 — 确认远端为 `TUSKIJAY/tang-strategy`、默认分支为 `main`、GitHub CLI 已登录且现有 Pages workflow 保持不变。
- [x] 2026-07-18 — 新增 PR-only/manual `Project harness` workflow 与 PR 模板；workflow 通过 `actionlint v1.7.12`，原有 Pages workflow 同时复核通过。
- [x] 2026-07-18 — GitHub 增量复验：harness `100/100`、本地 checker PASS、后端 `4/4`、compileall 与前端 build PASS、`git diff --check` PASS。

## Historical Redirects

长期历史仍由现有 Git 与项目文档承载；本文件只保留当前生命周期真相和检索指针。
