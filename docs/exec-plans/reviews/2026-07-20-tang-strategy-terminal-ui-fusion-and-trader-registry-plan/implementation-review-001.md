# Independent Implementation Review 001

- Review target: `docs/exec-plans/active/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md`
- Review target revision: `v2-review-foldback-2026-07-20`
- Review type: implementation
- Reviewer ID: `codex-independent-implementation-reviewer-2026-07-20-terminal-ui-registry-001`
- Plan author ID: `codex-plan-author-2026-07-20-terminal-ui-registry`
- Independence declaration: `attested`
- Evidence method: `read-only exact-manifest recomputation, baseline-to-working-tree source review, protected-boundary hashing, deterministic frontend tests, lifecycle checker execution, and direct visual inspection of representative accepted PNGs`
- Verdict: revise
- Confidence: high

## Exact Review Target

- Frozen target ID: `terminal-ui-registry-v1:3c73a671ab10d315dac42c0d923192638b1c1bfffa25bd6ece2cb8313a282440@3d9a67cede36496d787bf4f2b34e16f69b3ca78d`
- Baseline and current HEAD: `3d9a67cede36496d787bf4f2b34e16f69b3ca78d`
- Recomputed frozen file count: `19/19`
- Recomputed aggregate: `3c73a671ab10d315dac42c0d923192638b1c1bfffa25bd6ece2cb8313a282440`
- Manifest result: exact match

The review is independent of plan drafting and implementation. I did not modify the plan, implementation, state documents, phase evidence, packet, protected data, Git index, branch, or remotes. This review file is the sole write made by the reviewer.

## Findings

### High — the frozen target does not pass its claimed lifecycle checker

`docs/exec-plans/active/index.md:7` links the active plan's Evidence cell to the Phase 5 evidence file. Under the repository's constrained active-index contract, that cell must resolve to the latest direct review artifact, currently `review-002.md`. A fresh read-only run of `python -B scripts/check-operating-modes.py --root .` fails with:

`state index: docs\exec-plans\active\index.md row for 2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan latest evidence mismatch`

This directly contradicts the pass claims in `docs/exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/evidence/phase-5-integrated-acceptance.md:53` and `:55`, as well as the packet's verification summary. Because the plan requires the direct operating checker and governed harness to pass before independent acceptance, the exact frozen target cannot receive `accept`.

Required revision: reconcile the active-index Evidence link with the constrained contract, correct any now-stale verification claims, rerun the operating/governed/auto checks, and freeze a new exact target.

### Medium — `HANDOFF.md` contains contradictory current resume instructions

The operative state block and current snapshot correctly say `phase-6:in-progress` with next gate `independent-implementation-review`, but three later current-truth surfaces remain stale:

- `HANDOFF.md:51` says Phase 0 migrated the plan to v2 and instructs the next agent to start Phase 1; the active plan intentionally remains `operating-modes-v1` and Phases 1–5 are complete.
- `HANDOFF.md:61` reports the current plan as `phase-1:in-progress`.
- `HANDOFF.md:136` names `phase-1-exit` as the current next gate.

This violates the repository rule that `HANDOFF.md` is the latest resume index and creates a real risk that the next agent resumes an already completed phase. Required revision: reconcile all current Terminal UI resume/check/gate text to the Phase 6 review state, then include the corrected file in the new frozen target.

## Source And Contract Assessment

No implementation-code finding was found in the reviewed target.

1. OPT-001 through OPT-004 are implemented within the frozen frontend/docs surface. The working tree adds only the two planned registry helper/test files and modifies the planned Layout, Admin page, shared stylesheet, stable test carrier, source-contract tests, architecture, plan, index, and state/evidence surfaces. No backend, API client, schema, canonical content, DB, publisher, exporter, or runbook source changed.
2. The exact fifteen root tokens are present. `var(--brand-warm)` has one runtime consumer, `.brand-mark`. All five destinations use one `NavItem` renderer; the trader workspace remains bottom-pinned, uses `UsersRound`, retains an accessible capability name, and exposes `aria-current`. Shared trade components own the palette and the three `.dr-sidebar` exceptions are spacing-only density rules.
3. `traderRegistry.js` enforces exact `^[a-z][a-z0-9_]{1,63}$` and `^#[0-9A-Fa-f]{6}$` contracts, surrounding-whitespace-only normalization, blank-name rejection, case-insensitive color uniqueness, exact ID/order uniqueness, non-negative safe-integer order, next-free-multiple-of-ten defaulting, append preservation, and unsaved removal. `AdminTradersPage.jsx` keeps persisted IDs readonly, revalidates the staged row before complete-document PUT, retains state on failure, and clears create/staged state only after `Api.adminTraders()` reload succeeds.
4. Server-path association accepts only recognized `registry.traders[index].field` paths whose row exists and whose field is backed by a currently rendered control. Persisted `trader_id`, unknown/root/out-of-range paths, malformed JSON, and no-path bodies remain form-level. Readonly conditionally renders neither editor nor registry, and Static source has no Admin/API mutation surface.
5. Availability remains derived from displayable groups rather than registry membership. The isolated receipt and visual evidence show `codex_demo` persisted only in the temporary registry/DB copy with zero groups, legs, events, and outcomes and absent from interactive/static trader controls.
6. Protected boundaries and authority claims are truthful. Current HEAD is still the Phase 0 commit; no later implementation commit exists. The protected tree is byte-identical to baseline, and the only successful third-trader write occurred in the documented isolated copy. No push, PR, Pages, provider/broker, canonical-data, or remote action is claimed or evidenced.
7. The Windows SQLite `TemporaryDirectory` teardown lock is acceptable as a baseline environment observation: it was present before frontend implementation, occurs after product assertions, reproduces under the alternate pinned runtime, and the backend tree is unchanged. It does not excuse the independent lifecycle-checker failure above.

## Checks Performed

| Check | Independent result |
| --- | --- |
| 19 frozen file SHA-256 values | pass, `19/19` exact |
| ordered aggregate recomputation | pass, `3c73a671ab10d315dac42c0d923192638b1c1bfffa25bd6ece2cb8313a282440` |
| baseline-to-working-tree intended-scope inspection | pass for implementation scope; no protected source/data change |
| `npm run test:trade-records` | pass, `46/46` |
| direct operating-modes checker | **fail**, active-index latest-evidence mismatch |
| `git diff --check` | pass |
| protected file SHA-256 values | pass for DB, registry, backend routes/service, trader schema, publisher, exporter, and runbook |
| canonical trade tree | pass, 22 files / 87,403 bytes and byte-equal to baseline |
| SQLite | pass, 25,702,400 bytes, 49 market days, `integrity_check=ok`, foreign-key findings `0` |
| accepted PNG digests | pass for the Phase 1–5 evidence entries checked against files outside the worktree |
| direct visual inspection | pass for baseline Admin, final narrow Admin, invalid create, successful reload, interactive Review drilldown, readonly collapsed inspection, Static legacy QQQ, and Login error/focus receipts |

The governed/auto harness checks were not relabeled as pass after the direct composed lifecycle prerequisite failed. The failure is deterministic and belongs to the frozen documentation/index target, not to an unavailable environment.

## Authority Assessment And Verdict

The implementation respected the no-backend/no-canonical-write/no-remote boundary, and the two pre-existing local commits are accurately separated from the uncommitted Phase 1–6 implementation. The reviewer performed no stage, commit, push, publication, provider/broker, or remote action.

Verdict is `revise` with `high` confidence. The frontend implementation is functionally acceptable on the evidence inspected, but the exact frozen target contains a failing mandatory lifecycle check and contradictory handoff resume truth. Closeout is not authorized until both findings are corrected, a new exact manifest is frozen, and an independent follow-up implementation review returns `accept`.
