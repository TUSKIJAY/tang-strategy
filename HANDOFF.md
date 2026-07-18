# Handoff

## Current Snapshot

- Last updated: 2026-07-18
- Project: `Tang Strategy`
- Branch: `codex/project-harness` (created from `main@c262ba0`)
- Harness profile: `minimal`
- Status: harness 已生成、按仓库证据定制并完成验证；业务代码和每日市场数据未改动，`main` 引用未移动。

## Resume Checklist

1. 读取 `AGENTS.md`、`INSTRUCTIONS.md`、`PROGRESS.md` 与本文件。
2. 若为 Git 仓库，运行 `git status --short --branch`，保留所有用户已有改动。
3. 运行 `.harness/config.json` 中的验证命令。
4. 若修改逻辑或数据管线，再执行 `AGENTS.md` 要求的已知交易日与页面回归。

## Verification Evidence

| Check | Command | Result | Notes |
| --- | --- | --- | --- |
| Harness structure | `python3 scripts/check-project-harness.py --root . --profile auto` | pass | 所有 minimal 文件存在，config 匹配 |
| Skill structural validator | `validate_harness.py --target . --profile auto --min-score 90` | pass | `100/100`，0 critical failures |
| Backend unit tests | `cd backend && PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'` | pass | `4/4`; 临时隔离环境安装固定 calendar 依赖后运行 |
| Backend compile | `cd backend && PYTHONPATH=. python3 -m compileall -q app scripts tests` | pass | 无输出，exit 0 |
| Frontend build | `cd frontend && npm run build` | pass | Vite build 完成，1746 modules transformed |
| Diff integrity | `git diff --check` | pass | 无 whitespace errors |

## Blockers And Risks

- 当前没有已证实阻塞。
- `docs/` 必须保持扁平，因此未采用会创建嵌套 lifecycle 目录的 `governed` profile。
- 新 Python 环境运行 TradingView tests 前需安装 `backend/requirements-tv.txt`；否则会因缺少 `pandas_market_calendars` 失败，这属于环境前置条件。

## Next Gate

- 维护者决定是否在 `codex/project-harness` 上 commit；后续如需合入 `main`，应另行明确授权并先复核分支 diff。

## Handoff Boundary

本文件是当前接手索引，不是历史日志。详细历史进入 `PROGRESS.md` 或其归档，机器运行时状态进入专门状态文件。
