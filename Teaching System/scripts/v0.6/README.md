# v0.6 执行 harness

为 [v0.6 data-foundation plan](../../docs/planning/v0.6-data-foundation/data-foundation-plan.md) 提供可中断、可断点续跑、跨 Claude 窗口接手的执行载体。

## 接手入口

**接手者读 [`state/HANDOFF.md`](state/HANDOFF.md)** — 自带当前阶段、已完成清单、下一步具体命令、待用户确认事项。

新窗口一句话指令：
```
看 scripts/v0.6/state/HANDOFF.md，按里面「如果你是接手的 Claude」那一节继续
```

## 命令

```bash
./run.sh status              # 查看当前状态（HANDOFF.md 头部）
./run.sh task0               # Task 0：Polygon 拉取（断点续跑）
./run.sh task0 --force       # 全部重拉
./run.sh task1               # Task 1：build_json.py --batch
./run.sh task2               # Task 2：切片工具冒烟测试
./run.sh task3               # Task 3：demo seed 打包 + 集成测试
./run.sh all                 # 串行跑全部
./run.sh help                # 用法
```

## 目录结构

```
.
├── README.md           本文件
├── run.sh              入口脚本
├── .gitignore          忽略 state/
├── tasks/              每个 task 一个 Python 文件（接手 Claude 实现）
│   ├── task0_fetch.py
│   ├── task0_audit.py
│   ├── task1_batch.py
│   ├── task2_smoke.py
│   └── task3_demo_pack.py
└── state/              gitignored
    ├── HANDOFF.md      接手 Claude 的入口文档（每步完成自动 update）
    ├── acceptance.md   各 task 跑完后的累积报告
    └── *.json          程序读的状态文件（断点续跑用）
```

## 设计原则

1. **HANDOFF.md 是真实状态来源** — 每个 task 完成、每 ~10% 进度都要 update
2. **task0 单日级断点续跑** — 每日 fetch 完立即 flush state JSON，1-2h 限速过程中 Ctrl+C 零浪费
3. **失败显式登记** — 不静默跳过；BLOCKED 项写到 HANDOFF.md "待协调/暂缓事项" 段
4. **跨 task 串行** — 后任务依赖前任务输出（Polygon → batch JSON → 切片 → fixture）
5. **A+ 分层落盘** — 成功重拉落 `data/processed/`（扫描器默认池），fallback 落 `processed/synthetic_fallback/`（隔离）
6. **凭据从 env var 读** — 严格按 plan 0a 节，不 hardcode 不打印不粘 acceptance

## 决策记录（H1-H6）

| # | 决策 | 选定 |
|---|---|---|
| H1 | 入口 | `run.sh` |
| H2 | 位置 | `scripts/v0.6/` |
| H3 | task0 断点粒度 | 单日级 |
| H4 | fail 策略 | 主路径重试 3 次 → fallback；都失败 → HANDOFF.md 标 BLOCKED |
| H5 | 跨 task 并行 | 串行 |
| H6 | HANDOFF 更新粒度 | 每 task + 每 task 内 ~10% 进度 |
