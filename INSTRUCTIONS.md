# Tang Strategy

## Objective

Keep coding-agent work restartable, scope-bounded, and verifiable while preserving the DB-first review runtime and TradingView-first daily publish contract.

## Project Type

FastAPI backend and React/Vite frontend workspace with a SQLite-backed market-review runtime.

## Harness Profile

`minimal`

## Directory Structure

- `AGENTS.md` — agent 入口地图与硬规则。
- `INSTRUCTIONS.md` — 本项目稳定章程。
- `PROGRESS.md` — 当前状态与生命周期索引。
- `HANDOFF.md` — 当前接手索引。
- `backend/app/` — FastAPI API、SQLite 访问、导入与 review payload 组装。
- `backend/scripts/`、`backend/tests/` — 数据抓取/重建/导出工具与后端测试。
- `frontend/src/` — Review、Backtest、Teaching 页面和共享图表/扫描逻辑。
- `strategies/`、`content/` — 策略定义、教学内容、案例与 Tang 交易记录。
- `data/seed/market-data/live_extended/` — 当前 pipeline 唯一接受的 seed 格式。
- `data/sqlite/tang_strategy_live_extended.db` — 页面和 Pages workflow 使用的运行时数据源。
- `docs/` — 架构、策略、roadmap 与日常发布手册；按仓库约定保持扁平。
- `scripts/` — 项目级 harness 检查工具。
- `.github/workflows/project-harness.yml` — PR 与手工触发的 harness/backend/frontend 校验。
- `.github/pull_request_template.md` — GitHub PR 范围、数据影响、验证和安全清单。

## AI Behavior Rules

1. 先读入口与当前状态，再修改文件。
2. 以目标仓库事实为准，不从模板虚构架构、历史或完成状态。
3. 修改范围保持窄；保护用户已有和无关改动。
4. 每次重要状态变化同步 `PROGRESS.md`；当前接手点、验证证据或下一闸门变化时同步 `HANDOFF.md`。
5. 详细证据使用索引和归档保存，避免启动四件套无限增长。
6. 项目存在更严格的本地规则时，以更严格规则为准。

## Verification Commands

以下命令已根据仓库测试、README、`AGENTS.md` 与 CI 核对：

- `python3 scripts/check-project-harness.py --root . --profile auto`
- `cd backend && PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'`
- `cd backend && PYTHONPATH=. python3 -m compileall -q app scripts tests`
- `cd frontend && npm run build`

TradingView 测试需要当前 Python 环境已安装 `backend/requirements-tv.txt` 中的固定依赖；缺依赖属于环境未就绪，不应误报成代码回归。

逻辑或数据管线变化还必须按 `AGENTS.md` 做 `SPY 2026-04-22` assemble 与 Review/Backtest 手工回归。每日发布则完整执行 `docs/daily-publish-runbook.md`，不能用上述基础检查替代。

## Project-Specific Constraints

- `AGENTS.md` 是唯一权威 agent 入口；保留 `CLAUDE.md` 作为指针，不复制完整规则。
- 活跃代码/数据边界是 `backend/app`、`frontend/src`、`strategies/`、`content/` 与 `data/`；`legacy/` 不属于活跃路径。
- 运行时真相是提交进 Git 的 SQLite DB；gitignored seed JSON 不是 Pages 发布输入，重建步骤不可跳过。
- 日常发布默认先用仓库内 TradingView adapter。TV 重试耗尽或硬质量门失败前，不检查、不打开、也不要求 IB Gateway。
- 只有完整通过质量门的数据日才可写入/发布；同一交易日不得混合 TradingView 与 IB bars。
- `docs/` 保持扁平；本项目使用 `minimal` harness，不凭空增加 plan/review/decision 生命周期。
- GitHub Actions 只验证提交内容；不会自动修改 `PROGRESS.md` / `HANDOFF.md`，也不授予 merge、Pages 发布或每日数据发布权限。
- `.env`、provider credentials、admin token、运行时 secrets 和未脱敏生产数据不得提交或写入状态文档。
- 保留用户已有与无关改动；未经明确请求不自动把 harness 改造扩展为每日发布、数据重建、提交或推送。
