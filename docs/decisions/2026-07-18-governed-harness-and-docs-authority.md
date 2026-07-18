# Decision — Governed Harness And Documentation Authority

- Status: Accepted
- Date: 2026-07-18
- Scope: repository-local agent governance and documentation ownership
- Authority source: explicit user decisions in the 2026-07-18 execution prompt

## Context

Tang Strategy is safety-sensitive and multi-phase: tracked runtime data, a destructive rebuild path, static publication, documentation cleanup, and durable review evidence must be coordinated without conflating a review with authority. The previous `minimal` profile and flat-doc rule did not provide a plan/review/decision lifecycle or distinguish product docs from generated outputs and governance records.

## Decision

- Upgrade `.harness/config.json` to `governed`.
- Permit controlled governance directories under `docs/exec-plans/`, `docs/decisions/`, `docs/optimization/`, and `docs/progress-archive/`.
- Keep `AGENTS.md` as the single authoritative agent entry. `CLAUDE.md` is only a compatibility pointer.
- Keep product/architecture docs separate from governance lifecycle docs: `docs/roadmap.md` owns product/module direction; `docs/exec-plans/roadmap.md` owns plan lifecycle; `docs/planning.md` is a historical summary/compatibility entry; `PROGRESS.md` is current lifecycle truth; `HANDOFF.md` is the latest resume point.
- Keep optimization records record-only and decisions durable but non-executing.
- Keep generated export/build/Pages artifacts out of `docs/`.

## Consequences

The repository gains explicit proposed/active/completed/review indexes, decision records, optimization intake, a progress archive, and startup-document budgets. Existing startup/state files must be manually merged from repository evidence instead of overwritten by templates.

## Alternatives Considered

- Retain `minimal`: rejected by the user because it cannot represent the required reviewed, multi-phase, safety-gated execution.
- Keep all docs flat: rejected because it conflates product docs, governance, and legacy output.
- Copy full policy into `CLAUDE.md`: rejected because it creates a second drifting authority source.

## Activation Boundary

This accepted decision constrains the current plan and future governed artifacts, but acceptance alone does not implement changes or activate a plan. The current prompt separately grants one-time local activation of the named recovery plan only after independent review acceptance. It does not authorize commit, push, merge, PR, Pages publish, branch protection, environment approval, or other remote changes.
