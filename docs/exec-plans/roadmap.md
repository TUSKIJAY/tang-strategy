# Exec Plans Roadmap

本文件是 `Tang Strategy` 实施计划及评审的生命周期入口。

## Lifecycle

1. 改进想法可在用户启用记录模式后进入 `docs/optimization/`。
2. 只有用户明确要求转化的范围才能成为 `proposed/` 计划。
3. proposed 计划必须接受独立 review；review 不自动等于 activation。
4. 只有 review 通过且用户明确批准后，计划才能移动到 `active/`。
5. active 计划按 phase 执行；每次 start、complete、block、reject 或 scope change 都先更新 `PROGRESS.md`。
6. 每个 phase 记录验证证据、刷新 `HANDOFF.md`，并按仓库规则形成 scoped commit。
7. 全部范围完成、验证和收尾后，计划移动到 `completed/`。

`proposed`、`active`、`completed` 与 `review` 是不同状态，不得仅靠措辞相互替代。

## Directory Rules

- [`proposed/index.md`](./proposed/index.md)：草案或 review-only 计划，无实施权限。
- [`active/index.md`](./active/index.md)：已评审、已获用户批准、当前可按 gate 执行的计划。
- [`completed/index.md`](./completed/index.md)：已完成、终止、拒绝、被取代或归档的计划。
- [`reviews/index.md`](./reviews/index.md)：按计划 slug 保存独立评审和实施验收。
- `plan-template.md`：起草模板，不属于任何计划状态。

## Execution Discipline

- 不得静默合并 phase。
- phase 未形成状态、证据、handoff 和必要提交闭环前，不得宣布完成。
- 发现无关脏改动时保护它们；无法形成干净范围时记录阻塞并暂停。
- 决策、优化记录、review 或聊天认可不能绕过 active 状态与用户批准。

## Active Plans

- [Tang Strategy Trade Tools, Group Span, Viewport, And Data Rail](./active/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md) — Active; revision `v3-review-foldback-2026-07-21`; `phase-0:not-started`; next gate `phase-0-start`; matching `review-003: approve/high`

## Proposed Plans

None.

## Completed Plans

- [Tang Strategy Trade Points And K-line Marker Labels](./completed/2026-07-21-tang-strategy-trade-points-and-kline-marker-labels-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [Tang Strategy Trade Panel Visual Polish](./completed/2026-07-21-tang-strategy-trade-panel-visual-polish-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [Tang Strategy Data Progressive Navigation And Trade Card Density](./completed/2026-07-21-tang-strategy-data-progressive-nav-and-trade-card-density-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [Tang Strategy Review Date Navigation And Trader Filter Fusion](./completed/2026-07-20-tang-strategy-review-date-navigation-and-trader-filter-fusion-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [2026-07-18 Tang Strategy governed harness and data safety recovery](./completed/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [2026-07-19 Tang Strategy Coding And Data Update Modes](./completed/2026-07-19-tang-strategy-coding-and-data-update-modes-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [2026-07-19 Tang Strategy Multi-Trader SPY/QQQ Trade Data Refactor](./completed/2026-07-19-tang-strategy-multi-trader-spy-qqq-trade-data-refactor-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [Tang Strategy Review Workspaces And Trader Point Editing](./completed/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [Tang Strategy Durable Checkpoint And Scoped Local Commit Governance](./completed/2026-07-20-tang-strategy-durable-checkpoint-and-scoped-auto-commit-governance-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
- [Tang Strategy Terminal UI Fusion And Trader Registry](./completed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md) — Completed; canonical details: [completed index](./completed/index.md)
