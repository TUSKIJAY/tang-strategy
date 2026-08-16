# Tang Strategy EOD Pending Activation Hotfix

- Lifecycle schema: `operating-modes-v1`
- Status: Proposed
- Plan slug: `2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan`
- Revision: `v2-proposed-2026-08-16`
- Plan author ID: `codex-root-01a00adc`
- Design reviews: `../reviews/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan/review-001.md`
- Latest design verdict: revise
- Review independence: attested
- Activation evidence: none
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: `design-review`
- Implementation review: none
- Final disposition: none
- Verified implementation commit: none
- Lifecycle reconciliation commit: none
- Owner: Codex
- Created: 2026-08-16
- Scope authority: user instruction `直接接手干吧` continues the authorized repair, publication, and existing-transaction recovery requested in task `01a00a96-8edd-7f63-82e9-89c179ae72d9`
- Local commit: task-scoped commits are authorized; push, Pages verification, and existing-transaction recovery are explicitly authorized by the same user instruction chain

## 1. Context And Evidence

- Production run `production-d4f7bd7fb26e4960b1a5b5f00e242093` published trade date `2026-08-14` at commit `6f9a87c75f06a0ad03ec77b642a989d3cd22dae6`; transaction `production-d4f7bd7fb26e4960b1a5b5f00e242093-1` is preserved at `stage=pages_verified`, `push_confirmed=true`, Pages workflow `31853873121`, and `delivered_message_ids={}`.
- Live hosted acceptance reproduces one QQQ lifecycle card at `setup_time=15:59`, `status=pending`, with no outcome time. All other SPY/QQQ lifecycle cards are `activated` or `expired`.
- `scanSignals()` retains a pending activation when the supplied RTH bar array ends before `max_wait_bars` elapses. The 2026-08-14 QQQ dataset is a complete 390-bar RTH session ending at 15:59, so this is an end-of-session lifecycle gap rather than missing market data.
- Hosted acceptance correctly rejects pending public lifecycle cards. This plan fixes the scanner lifecycle and keeps that fail-closed acceptance rule unchanged.
- Failure notification `1537982342549872730` is the only Discord message recorded for this run. The daily report has not been sent.

## 2. Objective

- In scope:
  - finalize a still-pending activation only when the scanner proves a complete, contiguous configured session, using an explicit session-end expiry outcome at the final in-session bar;
  - record actual observed bars separately from the configured maximum so a shortened observation window is truthful;
  - render session-end expiry copy truthfully in Review and Static Review lifecycle surfaces;
  - add direct scanner regression tests for ordinary activation-window expiry, session-end expiry, and activation-before-end preservation;
  - publish the code-only fix to `main`, verify the new Pages build, and extend the publisher recovery path so an explicit expected renderer SHA is checked inside the hosted capture path and persisted before delivery;
  - reset the already-open circuit only after the hotfix build, renderer gate, and bounded duplicate precheck pass, then resume only the preserved 2026-08-14 transaction;
  - prove no duplicate Discord daily report through bounded precheck and exact receipt readback.
- Out of scope:
  - changing strategy JSON, signal eligibility, `max_wait_bars`, market data, tracked SQLite, normalized trade content, cron schedule/config, Discord adapter limits, or lifecycle acceptance criteria;
  - rerunning the already-confirmed 2026-08-14 data commit or creating a second transaction;
  - deleting or resending the existing failure notification.
- Non-goal: suppressing late-session setups. The setup remains visible evidence; only its unresolved outcome is finalized.

## 3. Constraints And Invariants

- Existing full-window `activated` and `expired` outcomes must remain byte-semantically equivalent except for additive observed-window metadata.
- End-of-input alone is not completion evidence. Session-end expiry is allowed only when the in-session 1m timestamps are contiguous from the configured/default start through the minute immediately before the configured/default end and every bar required for an activation probe is numerically valid. Partial, gapped, early-close-without-calendar-proof, and intraday inputs remain `pending`.
- The configured activation window remains eight bars; `_activation_observed_bars` is an explicit counter of valid, processed, later in-session activation probes. It is never derived from array-index distance. Normal timeout is `8/8`; the QQQ 15:59 boundary is `0/8`.
- A session-end expiry carries a distinct `_expiry_kind=session_end` and reason; normal timeout expiry remains `_expiry_kind=activation_window`.
- Hosted acceptance continues to require `activated|expired`, zero pending public lifecycle cards, and 1920x1080 capture. The publisher command accepts an explicit 40-hex expected renderer SHA; browser capture fetches live provenance before and after SPY/QQQ capture and refuses delivery unless both equal that SHA.
- The tracked SQLite hash and all unrelated untracked `output/` trees must remain unchanged.
- Recovery must reuse manifest commit `6f9a87c...`, its original data-publication workflow `31853873121`, and any persisted delivery IDs. Before the first Discord daily item, a redundant checksummed renderer receipt records distinct `data_commit_sha`, `data_workflow_run_id`, `renderer_commit_sha`, `renderer_workflow_run_id`, capture bounds, and screenshot hashes. Ambiguous provenance or duplicate Discord state fails closed.

## 4. Phases

### Phase 0 — Baseline And Scope Freeze

- Entry gate: design review approves revision `v2-proposed-2026-08-16` and the current user instruction activates execution.
- Work: preserve manifest/failure/cron evidence; record HEAD, status, DB hash, hosted QQQ pending reproduction, and Discord failure ID.
- Verification: transaction remains `pages_verified`, daily delivery IDs remain empty, cron declaration remains `tang-publisher-daily-v1`.
- Exit gate: `phase-0-exit`.

### Phase 1 — Scanner And Lifecycle Copy

- Entry gate: `phase-0-exit`.
- Work: add a complete-session gate in `scanner.js`; finalize only a proven session; explicitly count valid activation probes; add observed-window/session-end metadata; update lifecycle copy; add scanner tests and include them in the focused frontend test command.
- Verification: synthetic tests cover normal expiry, proven-session expiry at delay 0 and partial delay, activation before end, and incomplete/gapped/non-session inputs remaining pending; existing frontend tests remain green.
- Exit gate: `phase-1-exit`.

### Phase 2 — Local And Hosted-Equivalent Acceptance

- Entry gate: `phase-1-exit`.
- Work: add the publisher's explicit expected-renderer argument, in-browser provenance bracket, pre-delivery renderer receipt, and tests; run focused tests/builds; reproduce the 2026-08-14 SPY/QQQ lifecycle snapshots against local code and the published payload.
- Verification: QQQ 15:59 becomes `expired` at 15:59 with `0/8`; a normalized before/after annotation comparison allows only additive observed/expiry metadata and that new outcome; publisher tests prove mismatch stops before delivery and matching evidence is persisted; no pending action remains; DB hash is unchanged.
- Exit gate: `phase-2-exit`.

### Phase 3 — Independent Implementation Review And Publish

- Entry gate: `phase-2-exit`.
- Work: create the scoped implementation commit; obtain independent implementation review; push `main`; wait for the authorized Pages workflow and validate provenance plus hosted SPY/QQQ snapshots.
- Verification: review verdict `accept`; remote `main` equals the implementation commit; the new Pages workflow succeeds; live `build-manifest.json` equals the hotfix commit; hosted acceptance passes without relaxing gates.
- Exit gate: `phase-3-exit`.

### Phase 4 — Existing Transaction Recovery

- Entry gate: `phase-3-exit`.
- Work: bounded 20-message duplicate check; create a circuit-reset receipt bound to the current open-circuit checksum after recovery readiness is verified; run `bin/tang-publish reset-circuit --receipt <exact-receipt> --json`; then run only `bin/tang-publish run --mode production --trade-date auto --expected-renderer-sha <hotfix-sha> --json`; read every persisted Discord and renderer receipt ID exactly.
- Verification: reset is bound to the pre-reset circuit; result is `transaction_recovered`/`finalized`; the original data evidence remains intact; the pre-delivery renderer receipt binds screenshots to the hotfix workflow/SHA; summary/SPY/QQQ bodies, author, order, and attachments match; no duplicate daily report; post-success circuit is closed with no last failure.
- Exit gate: `phase-4-exit`.

### Phase 5 — Closeout

- Entry gate: `phase-4-exit`.
- Work: reconcile plan/index/progress/handoff records and retain production receipts.
- Verification: lifecycle checker, harness checker, staged diff check, final Git/cron/transaction/circuit readback.
- Exit gate: `closed`.

## 5. Evidence And Commit Plan

- Baseline commands: both Git repos' status/HEAD; DB SHA-256; live cron JSON; manifest/failure/circuit JSON; hosted Playwright snapshot.
- Focused checks: `node --test frontend/src/features/review/scanner.test.js`; `npm --prefix frontend run test:trade-records`; normal and static frontend builds.
- Full checks: repository verification battery as proportionate runtime permits; lifecycle and harness checks are mandatory.
- Expected state/handoff updates: proposed -> reviewed -> active -> completed; only the current resume point remains in `HANDOFF.md`.
- Task-owned product paths: `frontend/src/features/review/scanner.js`, `frontend/src/features/review/scanner.test.js`, `frontend/src/features/review/ReviewSignalList.jsx`, `frontend/package.json`.
- Task-owned publisher paths in `/Users/neowang/.openclaw/workspaces/tang-publisher`: `runner/tang_publish.py`, `runner/production.py`, `runner/hosted_acceptance.py`, and their focused existing test files. The cron declaration, deployment JSON, collector, pair/data pipeline, Discord formatting/adapter, and transaction data fields stay unchanged.
- Task-owned lifecycle paths: this plan, its review directory, the four lifecycle indexes/roadmap, `PROGRESS.md`, `HANDOFF.md`, and any required progress archive index/file.
- No-commit condition: any failure to separate these paths from unrelated changes or any test showing altered earlier lifecycle outcomes.

## 6. Review And Activation Gate

- Review location: `docs/exec-plans/reviews/2026-08-16-tang-strategy-eod-pending-activation-hotfix-plan/`
- Required verdict: `approve` from an independent reviewer of exact revision `v2-proposed-2026-08-16`.
- Required user approval: already supplied by `修复一下然后发布吧` followed by `直接接手干吧`; activation is recorded only after design approval.
- Implementation start is authorized after activation recording; no additional confirmation is required.
- Remote publication and preserved-transaction recovery are authorized, but duplicate delivery and gate weakening remain forbidden.

The constrained metadata above is authoritative. Follow [`docs/operating-modes.md`](../../operating-modes.md) for lifecycle transitions, review evidence, scoped commits, and closeout fields.

## 7. Review-001 Resolution

- Input completeness: resolved with a scanner-owned contiguous-session and valid-probe gate; arbitrary input end no longer implies session end, and negative fixtures must remain pending.
- Observed count: resolved with an explicit valid-probe counter rather than index distance.
- Renderer binding: resolved with an explicit CLI SHA, in-browser before/after provenance bracket, successful workflow lookup, and a redundant checksummed receipt written before Discord delivery.
- Baseline preservation: resolved with a normalized field-level annotation comparison for the actual 2026-08-14 SPY/QQQ payload.
- Evidence naming: data publication and renderer deployment receive separate field names and workflow IDs; the original transaction manifest fields are not rewritten.
