# Decision — Market Data Rebuild Safety Contract

- Status: Accepted
- Date: 2026-07-18
- Scope: `live_extended` SQLite recovery, rebuild, and publication input
- Authority source: explicit user decisions in the 2026-07-18 execution prompt

## Context

The tracked SQLite DB is the interactive runtime and Pages export input. It currently contains 43 days but is missing three previously published days. The local seed has only six days, while the existing rebuild implementation deletes the DB before importing that incomplete seed.

## Decision

- Preserve the tracked SQLite DB as the runtime and Pages publication input in this work.
- Recover 2026-05-15 from commit `34caa03` and 2026-06-30/2026-07-01 from commit `1f15443`, subject to normalized source validation.
- Recover into a copy of the current DB and map market days by `(ticker, trade_date, session_mode)`, never by historical integer ID.
- Promote only a verified 46-day candidate after proving the original 43 days unchanged, source hashes equal, integrity clean, and runtime overlays reachable.
- Rebuild into a temporary candidate first. By default, reject any candidate whose logical market-day set is not a superset of the current DB set.
- On empty input, parse/import error, integrity failure, or date loss, return nonzero and leave original DB bytes unchanged.
- Permit intentional date loss only through an explicit manual override that is absent from daily and automated workflows.
- Use atomic replacement only after all candidate checks pass.

## Consequences

The six-day local seed can no longer silently collapse publication history. The daily runbook must describe candidate validation and the superset guard. Tests must isolate all failure paths from the tracked DB.

## Alternatives Considered

- Remove only `unlink()`: rejected because partial import or invalid candidates could still replace good data.
- Track the full seed history: deferred; outside this plan.
- Move DB to LFS/release artifacts: deferred; outside this plan.
- Treat local seed as canonical recovery input: rejected because named historical DBs provide the approved source evidence.

## Activation Boundary

This decision is binding on the active recovery plan after that plan passes independent review and lifecycle activation. It does not itself run recovery/rebuild and does not authorize daily fetch, broker fallback, export, publish, commit, push, merge, PR, or remote settings.
