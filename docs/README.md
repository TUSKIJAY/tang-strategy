# Tang Strategy Documentation Authority Map

## Startup And Current State

- [`../AGENTS.md`](../AGENTS.md) — single authoritative agent entry and hard operational rules.
- [`../INSTRUCTIONS.md`](../INSTRUCTIONS.md) — stable project/runtime/governance contracts.
- [`../PROGRESS.md`](../PROGRESS.md) — current lifecycle truth.
- [`../HANDOFF.md`](../HANDOFF.md) — latest resume point and next gate.

## Product And Architecture Docs

- [`architecture.md`](./architecture.md) — runtime modes, source/data flow, API boundaries, and ownership.
- [`roadmap.md`](./roadmap.md) — product/module direction for Review, Backtest, Teaching, data, and kline work.
- [`planning.md`](./planning.md) — historical planning summary and compatibility pointer; not active plan/decision authority.
- [`strategy.md`](./strategy.md) — docs entry pointing to canonical strategy intent in `strategies/STRATEGY.md`.
- [`teaching-system.md`](./teaching-system.md) — teaching content semantics and case-review guidance.
- [`kline-engine.md`](./kline-engine.md) — shared frontend chart engine and payload contract.
- [`daily-publish-runbook.md`](./daily-publish-runbook.md) — TV-first daily fetch, safe DB rebuild, and Pages publication SOP.
- [`operating-modes.md`](./operating-modes.md) — normative Coding/Data Update routing, lifecycle formats, task-scoped local commit default, reviewer evidence, and authority gates.
- [`harness-map.html`](./harness-map.html) — hand-maintained visual map of the harness layers, verification battery, and doc budgets; point-in-time snapshot, not build output.
- [`directed-agentic-graph.html`](./directed-agentic-graph.html) — hand-maintained interactive directed graph of the agentic contract (authority → mode routing → lanes/data pipeline → verification → state/artifacts); point-in-time snapshot, not build output.

## Governed Lifecycle Docs

- [`exec-plans/roadmap.md`](./exec-plans/roadmap.md) — execution-plan lifecycle and proposed/active/completed/review indexes.
- [`decisions/index.md`](./decisions/index.md) — persistent decisions; accepted decisions do not automatically execute work.
- [`decisions/2026-07-19-operating-modes-and-lifecycle-source.md`](./decisions/2026-07-19-operating-modes-and-lifecycle-source.md) — accepted source-ownership and peer-mode decision; non-executing by itself.
- [`optimization/index.md`](./optimization/index.md) — record-only improvement intake; records do not authorize implementation.
- [`progress-archive/index.md`](./progress-archive/index.md) — indexed historical lifecycle/evidence redirected out of startup files.

Product roadmap and execution-plan roadmap have different owners and must not duplicate each other. Current state belongs in `PROGRESS.md`/`HANDOFF.md`, not in a roadmap or historical summary.

## Generated Output Boundary

- static review JSON: `frontend/public/reviews`;
- Vite build: `frontend/dist`;
- published site: `gh-pages` branch root.

Generated Pages/export/build output must not be written under `docs/`. The tracked SQLite DB remains the source used by both interactive runtime and the Pages export workflow.
