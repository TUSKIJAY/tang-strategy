# Tang Strategy Documentation Hub

## What to read first

1. [`architecture.md`](./architecture.md) – runtime design and source-of-truth flow.
2. [`strategy.md`](./strategy.md) – strategy versions and default runtime strategy choice.
3. [`roadmap.md`](./roadmap.md) – milestones and module-level plan.
4. [`planning.md`](./planning.md) – current planning state and open decisions.
5. [`teaching-system.md`](./teaching-system.md) – teaching flow, strategy notes, and pattern digest.
6. [`kline-engine.md`](./kline-engine.md) – shared chart engine contract.
7. [`daily-publish-runbook.md`](./daily-publish-runbook.md) – SOP for fetch → DB rebuild → push → Pages.

## Documentation structure

- `architecture.md` defines the runtime design, data flow, API boundaries, and module ownership.
- `roadmap.md` tracks product direction for review, backtest, teaching, and engine work.
- `planning.md` summarizes historical plans and active decisions without nested folders.
- `strategy.md` describes strategy versions and default selection.
- `teaching-system.md` owns teaching content semantics and chart-pattern guidance.
- `kline-engine.md` owns the shared kline engine API and payload contract.
- `daily-publish-runbook.md` is the SOP for the daily IBKR fetch → SQLite rebuild → push → GitHub Pages flow.

## Documentation rule

- Keep `docs/` aligned with live-extended DB-first runtime.
- Keep all files directly under `docs/`; do not add subdirectories.
- Put Daily Review and Backtest details in `roadmap.md` and `architecture.md`.
- Put planning history and open decisions in `planning.md`.
