# Claude Code project memory

This repo's contributor guide is [`AGENTS.md`](./AGENTS.md). Read it before doing anything substantive.

## High-frequency trigger: daily publish

If the user's first message matches any of these patterns, run the **Daily publish playbook** in [`AGENTS.md`](./AGENTS.md) verbatim, using the date they specify (or the latest completed US trading day if omitted):

- `发布 SPY <date>` / `拉<date>的SPY` / `更新页面` / `push <date> SPY`
- `publish SPY <date>` / `publish today's review` / `daily publish`

Full SOP with troubleshooting: [`docs/daily-publish-runbook.md`](./docs/daily-publish-runbook.md).

Do not ask the user to re-confirm port, host, ticker, or strategy families — those are fixed (IB Gateway live `127.0.0.1:4002`, ticker `SPY`, strategy families `v3,v4,v5`). Only ask if the IB Gateway pre-flight fails or the user gives a date that conflicts with what's already in the DB.

## Other repo conventions

- Source of truth for runtime data: `data/sqlite/tang_strategy_live_extended.db`.
- Seed JSON under `data/seed/market-data/live_extended/<date>/` is gitignored — never commit it.
- `scripts/publish_spy_review.ps1` is a personal helper and is also gitignored. The equivalent commands are in AGENTS.md.
- Docs live flat under `docs/` — do not create subdirectories.
