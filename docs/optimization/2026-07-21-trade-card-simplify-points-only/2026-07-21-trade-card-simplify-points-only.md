# Optimization Batch · 2026-07-21

> Record-only intake. This file does not authorize implementation.
>
> Place this file at:
> `docs/optimization/2026-07-21-trade-card-simplify-points-only/2026-07-21-trade-card-simplify-points-only.md`
> Put evidence images in the sibling `screenshots/` folder and link them as `./screenshots/<name>.png`.
>
> A finalized record and its direct index update are committed locally by default under `docs/operating-modes.md` §2. A draft, failed/incomplete record, explicit no-commit instruction, or unclear path ownership prevents that commit. This does not authorize implementation or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Trade Card Simplification: Drop Amount & Profit Rate | Review / Trade Cards UI | recorded | none | 做减法：移除卡片上的金额和盈收比例，仅保留交易时间点位 |

## Visual Reference

- User feedback screenshot: [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png)

## OPT-001 Trade Card Simplification (Points Only)

- Source evidence: User screenshot [`screenshots/2026-07-21-trade-card-amount-profit-subtraction.png`](./screenshots/2026-07-21-trade-card-amount-profit-subtraction.png) (Review Trade tools + group cards, QQQ 2026-07-17 · 沃德哥). User instruction: 做减法，不需要展示金额和盈收比例，只需要展示交易时间点位。
- Current friction: Trade cards / expanded legs still surface dollar amounts and profit ratios (or outcome % / PnL-style noise), which distracts from verifying **when** a point occurred and **at what price**. Live card chrome already carries trader name, CALL/PUT direction, date, and review status; the remaining clutter is amount/profit display rather than point timing.
- Desired outcome: Apply visual subtraction on trade cards (and their expanded legs/events presentation) so the primary reading path is **trade timestamps + price points only**. Omit amount ($) and profit rate (%) from the card UI surface.
- Boundary that must not change:
  - Underlying trade data schemas, API contracts, and reported/calculated outcome fields may continue to exist in data; this intake is **presentation-only**.
  - Shared surface family remains Review / Static / Admin where the same trade cards render.
  - CALL/PUT direction chrome, Eligibility filters, Download, and verification status are out of this subtraction item unless a later OPT says otherwise.
- Lifecycle status: recorded
