# <Plan Title>

- Lifecycle schema: `operating-modes-v2`
- Status: Proposed
- Plan slug: `<unique-slug>`
- Revision: `<stable-revision-id>`
- Plan author ID: `<non-empty-id>`
- Design reviews: none
- Latest design verdict: none
- Review independence: none
- Activation evidence: none
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: `design-review`
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Implementation start evidence: none
- Current work unit: none
- Work state: none
- Blocker evidence: none
- Implementation reviews: none
- Latest implementation verdict: none
- Checkpoint authority: none
- Checkpoint authority mode: none
- Checkpoint authority kinds: none
- Expected checkpoint kind: none
- Owner: <owner>
- Created: YYYY-MM-DD
- Scope authority: review-only; this template and proposed plan do not authorize implementation

## 1. Context And Evidence

- Current state:
- Source evidence:
- Why now:

## 2. Objective

- In scope:
- Out of scope:
- Non-goals:

## 3. Constraints And Invariants

- Existing behavior that must remain unchanged:
- Safety/data/compatibility boundaries:
- Unrelated paths to preserve:

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate:
- Work:
- Verification:
- Exit gate:

### Phase 1 — Implementation

- Entry gate:
- Work:
- Verification:
- Exit gate:

### Phase 2 — Closeout

- Entry gate:
- Work:
- Verification:
- Exit gate:

## 5. Evidence And Commit Plan

- Baseline commands:
- Focused checks:
- Full checks:
- Expected state/handoff updates:
- Commit boundaries:

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/<plan-slug>/`
- Required verdict:
- Required user approval:
- Activation is a separate lifecycle change before implementation.
- Implementation start requires a later explicit start/execute instruction after activation recording.

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../operating-modes.md) for state invariants, review paths, gate-token syntax, manual transitions, and closeout fields.
