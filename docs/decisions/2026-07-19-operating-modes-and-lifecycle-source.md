# Decision — Operating Modes And Lifecycle Source

- Status: Accepted
- Date: 2026-07-19
- Scope: repository request routing, governed lifecycle evidence, and routine market-data update authority
- Authority source: approved active plan plus explicit user instruction `user-goal-execute-plan-2026-07-19`

## Context

The repository had a governed document surface and safe rebuild path but no repository-owned execution contract separating system changes from routine data updates. Lifecycle truth was duplicated in free prose, while the structural checker could pass despite stale plan, index, and Git claims.

## Decision

- Establish Coding Mode and Data Update Mode as peer top-level modes.
- Route system changes by read-only, bounded-maintenance, or proposed-plan lanes; named governance, data, DB, publication, security, cross-contract, or broad risks require a reviewed Exec Plan.
- Make one plan file in exactly one lifecycle directory canonical; treat indexes, roadmap, `PROGRESS.md`, and `HANDOFF.md` as derived surfaces.
- Adopt `operating-modes-v1` constrained plan/review/index/roadmap/current-state formats for deterministic checking.
- Keep reviewer identity/independence and user authority partly human-verified; the checker validates only structural evidence it can prove.
- Keep routine data updates plan-free when existing tools and gates work, but separate Local Update Gate from Publish Gate and preserve TV-first/provider/publisher behavior.
- Keep transitions manual and use a read-only checker; do not create a workflow engine or second state store.

## Consequences

Repository startup can route requests without private context, stale lifecycle surfaces become checkable, and local data acceptance cannot be mistaken for publication authority. Existing daily runtime behavior remains unchanged, including fetch import before canonical rebuild.

## Alternatives Considered

- Copy the full contract into `AGENTS.md` and `INSTRUCTIONS.md`: rejected because it creates drifting policy copies.
- Infer state from prose: rejected because it is nondeterministic.
- Add a transition helper now: deferred until v1 formats have operational evidence.
- Require an Exec Plan for every data update: rejected because routine existing-system operation is not a system change.

## Activation Boundary

This accepted decision constrains the active operating-modes plan and future governed work. Its acceptance does not itself activate a plan, start implementation, fetch data, connect to a provider or broker, mutate the DB, commit, push, publish, open or merge a PR, or change remote settings. Those actions require their separately named gates and authority.
