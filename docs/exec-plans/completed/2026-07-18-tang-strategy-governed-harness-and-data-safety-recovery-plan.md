# Tang Strategy Governed Harness And Data Safety Recovery

- Lifecycle schema: `operating-modes-legacy-v1`
- Status: Completed
- Plan slug: `2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan`
- Revision: `legacy-approved-2026-07-18`
- Plan author ID: `legacy-plan-author-2026-07-18`
- Design reviews: ../reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/review-001.md@revise@legacy-initial-2026-07-18, ../reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/review-002.md@approve@legacy-approved-2026-07-18
- Latest design verdict: approve
- Review independence: legacy-unattested
- Activation evidence: `user-instruction:2026-07-18-recovery-plan-execution`
- Current phase: none
- Phase state: none
- Phase entry gate: none
- Next gate: closed
- Implementation review: ../reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/implementation-review-001.md@accept
- Final disposition: Completed
- Verified implementation commit: `a70be643a968cc24215fe508e69b3e0496d3c34a`
- Lifecycle reconciliation commit: `2454ccb7fc1c927f2a52a3bd2db7debe41998594`
- Owner: Codex
- Created: 2026-07-18
- Completed: 2026-07-18
- Baseline: `codex/project-harness@8c6851d8f469e7a84471cd2900b00b3d9dcbdf07`
- Scope authority: this plan and its reviews are review-only; the current user prompt grants one-time local activation authority only after an independent reviewer returns `approve` for this exact plan
- Remote boundary: no stage, commit, push, merge, pull request, Pages publish, branch protection, environment approval, broker connection, or other remote mutation

## 1. Context And Evidence

The tracked SQLite database is both the interactive runtime input and the GitHub Pages export input. Read-only baseline checks established:

- `data/sqlite/tang_strategy_live_extended.db` contains 43 market days from 2026-05-12 through 2026-07-17.
- SPY 2026-05-15, 2026-06-30, and 2026-07-01 are absent; SPY 2026-07-17 is present.
- the local gitignored `live_extended` seed contains only six SPY files.
- the current rebuild script unlinks the configured DB before importing the seed.
- commit `34caa03` contains SPY 2026-05-15 with 960 1m and 192 5m bars.
- commit `1f15443` contains SPY 2026-06-30 and 2026-07-01, each with 960 1m and 192 5m bars.
- `content/trader-trades/2026-06-30.json` and `2026-07-01.json` exist but their overlays are unreachable while the market days are absent.
- the active Pages workflow exports JSON from the tracked DB into `frontend/public/reviews`, builds Vite output into `frontend/dist`, and publishes that build to `gh-pages`; tracked output under `docs/` is not a current publisher input.

The immediate risk is data loss: running the current documented rebuild against the six-day seed would replace 43 days with six. The governance risk is that product docs, lifecycle docs, generated artifacts, and current state have no reliable authority map.

## 2. Objective And Scope

### In scope

- Upgrade the repository-local harness from `minimal` to `governed` without overwriting existing startup or state files.
- Recover exactly the three missing market days from the named historical DB sources.
- Make rebuild candidate-first, validated, fail-closed, and atomic by default.
- Separate product/architecture documentation from governed lifecycle documentation.
- Correct active instructions, API/data-flow descriptions, regression dates, and lifecycle truth.
- Delete only the specifically authorized obsolete `docs/` outputs and zero-byte `.codex`, after their safety prerequisites pass.
- Expand the local harness checker and PR validation workflow for the governed profile.
- Record remaining repository-audit findings as record-only optimization intake.
- Preserve reproducible recovery, validation, and independent-review evidence.

### Out of scope

- Moving the DB to Git LFS, a release artifact, or an untracked/generated-only model.
- Tracking the complete seed history.
- Daily fetch, rebuild of the real DB from seed, export for publishing, push, Pages publishing, merge, pull request, or remote settings.
- Branch protection, GitHub environment approvals, or Action SHA pinning.
- Broker/Gateway access or any market-facing action.
- Implementing provider stubs, frontend dead-code cleanup, schema wiring, credential/rate-limit hardening, Docker reproducibility, or other audit follow-ups.
- Staging, committing, reverting, stashing, checking out, resetting, or overwriting unrelated user work.

## 3. Constraints And Invariants

- Until rebuild safety passes isolated tests, the current rebuild command must never target the tracked DB.
- Recovery starts from a SQLite-consistent backup snapshot of the current 43-day DB in a temporary/sibling candidate path; a raw copy of a live SQLite file is not accepted as a snapshot protocol and the real DB is not an experiment surface.
- Historical integer IDs are not portable. Recovery maps each source day by `(ticker, trade_date, session_mode)`, inserts a target market-day row without copying its historical ID, resolves the new target ID, and copies bars using that resolved ID.
- Existing 43-day logical rows, bars, strategy rows, teaching rows, and metadata must remain unchanged.
- No target day may be copied from the local seed merely because a seed file exists; the named historical DB is canonical and the seed is cross-check evidence only.
- Candidate promotion is permitted only after all hashes, counts, foreign keys, integrity, overlay/export reachability, and no-regression checks pass.
- Recovery and rebuild share one snapshot/promotion protocol: acquire the repository DB write lock, create the baseline with SQLite's backup API, record a source identity plus byte and full logical digest after journal/WAL quiescence, release the lock for candidate work, then reacquire it and require the live DB identity/digests to match immediately before promotion. Any drift rejects the candidate and preserves the new live state.
- All repository-managed DB writers (startup migration/import endpoints/fetch import/rebuild promotion) must honor the same adjacent lock. Promotion also requires no unresolved `-journal`, `-wal`, or `-shm` state, closed candidate/source verification connections, and a candidate on the same filesystem.
- Candidate promotion uses `os.replace` only while the write lock is held; the candidate and parent directory are flushed, and a verified backup remains available until post-promotion checks pass.
- The default rebuild rejects a candidate whose logical market-day key set is not a superset of the current DB key set. An explicit intentional-loss override may exist but is not used by the runbook, CI, this execution, or other default automation.
- Tracked SQLite remains the runtime and Pages publication input.
- Product docs and governance docs have different authority; generated Pages/export/build artifacts do not belong under `docs/`.
- Proposed plans, decisions, optimization records, and review verdicts do not independently grant execution authority.
- This prompt grants activation only for this plan after independent `approve`, and grants no remote authority.

## 4. Data Recovery Method

### Read-only evidence

For the current and historical DBs, record:

- market-day count and logical key;
- source and target `market_days.id` values as evidence only, never as a mapping rule;
- 1m/5m counts, first/last timestamp, OHLCV/VWAP summary, source/provenance metadata;
- normalized SHA-256 digests using the exact canonical contract below;
- normalized hashes for all existing 43 logical days plus strategies and teaching assets.

Canonical digest serialization is UTF-8 JSON with `ensure_ascii=False`, `allow_nan=False`, compact separators, `NULL` encoded as JSON `null`, SQLite REAL values encoded from Python finite floats, and rows represented as ordered arrays rather than unordered objects. The exact projections are:

- `market_days`, one logical day: `ticker, trade_date, session_mode, source, title, bar_count_1m, bar_count_5m, imported_at, meta_json`; exclude only `id`.
- `bars_1m` / `bars_5m`: `idx, ts, time, open, high, low, close, volume, vwap, ha_open, ha_high, ha_low, ha_close, m5, m10, m20, m30, m50, m60, m120, m200, m250`; exclude only `market_day_id`, order by `idx`.
- `strategies`: `id, name, version, slug, description, source_type, json_body, active, created_at, updated_at`, ordered by `id`.
- `teaching_assets`: `id, asset_type, version, slug, json_body, updated_at`, ordered by `id`.
- the full logical DB digest: ordered market-day projections by `(ticker, trade_date, session_mode)`, followed by each ordered bar projection and the ordered strategy/teaching projections.

The same implementation and column contract must hash the original 43 days, historical source days, candidate, pre-promotion live DB, and promoted DB. Recovery copies `imported_at` and `meta_json` exactly so historical and candidate day hashes are comparable.

### Candidate construction

1. Extract `34caa03:data/sqlite/tang_strategy_live_extended.db` and `1f15443:data/sqlite/tang_strategy_live_extended.db` to a temporary directory.
2. Under the shared repository DB write lock, use SQLite's backup API to create a consistent adjacent candidate snapshot, resolve/checkpoint journal mode as needed, verify no unresolved sidecars, and record the baseline path identity, main-file SHA-256, and full logical digest. Release the lock only after the snapshot and tokens are complete.
3. Attach/read the historical DBs read-only.
4. For each target logical day, insert only its `market_days` attributes into the candidate, resolve the candidate's new day ID by logical key, then insert ordered `bars_1m` and `bars_5m` with the resolved ID.
5. Do not update or replace an existing logical day; duplicate targets are an error.
6. Commit a candidate transaction only after both bar tables and declared counts agree.

### Candidate acceptance

- exactly 46 market days and exactly the three new logical days;
- all original 43 per-day normalized hashes unchanged;
- each recovered day matches the normalized source hashes and 960/192 counts;
- strategies and teaching assets unchanged;
- `PRAGMA integrity_check` returns `ok` and `PRAGMA foreign_key_check` returns no rows;
- 2026-06-30 and 2026-07-01 Tang trade overlays load through assemble/export code;
- 2026-07-17 still assembles with a known active strategy and non-empty 1m/5m bars.

Only then may promotion begin. Reacquire the shared write lock, re-check source identity, absence of unresolved journal/WAL sidecars, main-file SHA-256, and full logical digest against the recorded baseline, and reject on any mismatch. Close source/candidate verification connections, re-check the source identity once more, then atomically replace the tracked DB while the lock remains held. Repeat integrity, day-count, hash, and reachability checks after replacement.

## 5. Rebuild Fail-Closed Design

- Resolve DB and seed paths at call time; importing the rebuild module performs no filesystem mutation.
- Discover and validate seed inputs before creating a candidate. Empty input is an error with nonzero exit.
- Build a fresh candidate DB in an adjacent temporary directory, leaving the original unopened for writes.
- Import/parse failures, empty results, integrity failures, or subprocess failures abandon only the candidate and return nonzero.
- Parse each discovered market-day seed to a unique logical key before import; duplicate keys, non-finite values, missing/non-list bar collections, or empty 1m/5m bars are errors. Require discovered-file count, discovered-key count, imported-key count, and candidate market-day count to agree.
- For every candidate day, require actual 1m/5m row counts to be nonzero and equal both `market_days.bar_count_*` and the parsed seed counts; require unique ordered bar indexes and valid foreign keys.
- Compare logical market-day key sets, not row IDs. By default require `candidate_keys >= current_keys`; the explicit date-loss override relaxes only this date-set rule, not semantic completeness or non-market-table rules.
- Prevent non-market shrink independently: when a current DB exists, require candidate strategy slugs and teaching `(asset_type, version, slug)` keys to be supersets of the current sets and require at least one active strategy. For a fresh DB, require all discovered non-schema strategy JSON and all present required teaching source files to import one-for-one. Content may change through canonical reimport, but silent key loss is rejected.
- When keys would disappear, print the complete sorted missing-key/date list, return nonzero, and prove the original DB bytes are unchanged.
- Permit intentional shrink only through a clearly named CLI flag such as `--allow-date-loss`; the daily runbook and automated path must omit it.
- Use the same consistent-snapshot, shared-write-lock, source-drift token, sidecar, closed-connection, same-filesystem, flush, and `os.replace` promotion protocol defined for recovery.
- Isolated tests cover no seed, subset seed, import failure, superset success, integrity failure, date keys with empty/count-mismatched bars, strategy/teaching shrink, and original-byte preservation. A concurrent-drift test mutates the source after candidate validation and proves promotion refuses while preserving the new write. Tests use temporary DBs only.

## 6. Documentation Authority Map

- `AGENTS.md`: single authoritative agent entry and non-negotiable operational rules.
- `INSTRUCTIONS.md`: stable project facts, boundaries, directory map, and verification contract.
- `PROGRESS.md`: current lifecycle truth and bounded completion status.
- `HANDOFF.md`: latest resume point, verified evidence, blockers, and next gate only.
- `docs/roadmap.md`: product/module direction.
- `docs/exec-plans/roadmap.md`: governed execution-plan lifecycle and indexes.
- `docs/decisions/`: durable accepted/proposed decisions; decisions do not activate work.
- `docs/optimization/`: record-only follow-up intake.
- `docs/progress-archive/`: indexed historical state/evidence.
- `docs/planning.md`: historical planning summary/compatibility pointer, not current plan or decision authority.
- `strategies/STRATEGY.md`: canonical strategy intent; `docs/strategy.md` becomes a clear pointer/summary.
- `docs/daily-publish-runbook.md`: TV-first daily publication SOP; its rebuild step describes the new candidate/superset guard.
- `frontend/public/reviews`, `frontend/dist`, and `gh-pages`: generated/static publication surfaces; none write back to `docs/`.

## 7. Phases And Acceptance Gates

### Phase 0 — Governed bootstrap, plan, decisions, review, activation

- Entry: exact clean baseline confirmed.
- Work: run governed audit/preview; install only 14 missing artifacts; set profile to governed; create this plan and two decision records.
- Verify: existing startup/state/docs/config were not template-overwritten; indexes resolve; worktree changes are only authorized additions/merges.
- Exit: independent reviewer returns `approve`. The pre-authorized local activation then moves the plan from proposed to active and synchronizes roadmap, indexes, `PROGRESS.md`, and `HANDOFF.md`.

### Phase 1 — Recover the three missing market days

- Entry: active plan; historical DBs readable and non-conflicting.
- Work: create full read-only evidence; build/validate a 46-day candidate; atomically promote only after every acceptance check.
- Verify: 43-day digest preservation, three source digest matches, integrity/foreign-key checks, overlays and 07-17 assemble/export reachability.
- Exit: recovery evidence is saved under the plan review/evidence directory with commands and an explicit no-Pages statement.

### Phase 2 — Rebuild safety repair

- Entry: recovered tracked DB is verified; all development/tests remain isolated.
- Work: implement the shared DB write lock, SQLite-consistent snapshot/drift-checked promotion, candidate-first rebuild, semantic-completeness gates, and explicit intentional-loss override; add isolated unit/integration tests; update runbook.
- Verify: empty/subset/error/integrity/empty-bars/count-mismatch/non-market-shrink/concurrent-drift failures leave original bytes or the concurrent new write unchanged and return nonzero; a complete superset atomically succeeds; six-day seed against a copy of the 46-day DB is refused.
- Exit: no default or runbook path can silently reduce date coverage.

### Phase 3 — Instruction chain and current-state truth

- Entry: data and rebuild contracts are stable.
- Work: shrink `CLAUDE.md` to a compatibility pointer; update `AGENTS.md`/`INSTRUCTIONS.md` to governed, 2026-07-17, TV-first, authority boundaries, and generated-output rules; correct `PROGRESS.md`/`HANDOFF.md` commit/branch facts.
- Verify: no active startup instruction retains minimal profile, 2026-04-22, IB-first, or waiting-to-commit drift.
- Exit: all startup documents agree on authority, data, publication, and next gate.

### Phase 4 — Documentation information architecture and cleanup

- Entry: missing-day recovery evidence complete.
- Work: rewrite `docs/README.md`; correct `README.md`, `backend/README.md`, `docs/architecture.md`, `docs/planning.md`, `docs/roadmap.md`, `docs/strategy.md`, and `docs/kline-engine.md`; re-prove publication paths and consumers; delete only authorized stale docs outputs and zero-byte `.codex`; remove the contradictory ignore rule.
- Verify: current Pages workflow reads DB, exports to `frontend/public/reviews`, builds to `frontend/dist`, and publishes `gh-pages`; no active consumer references deleted paths; strategy/API/auth/TV-first descriptions match code.
- Exit: `docs/` contains active product docs plus controlled governance/evidence, not legacy generated publication output.

### Phase 5 — Governed checker and CI surface

- Entry: final authority paths are known.
- Work: complete all generated indexes/templates/SOPs; expand `scripts/check-project-harness.py` to validate the complete 15-path governed surface below, config GitHub paths, checks/job-name contract, and core lifecycle links; run startup-doc budget in `.github/workflows/project-harness.yml` while preserving backend/frontend jobs and Pages behavior.
- Governed surface: `docs/README.md`; `docs/decisions/index.md`; `docs/decisions/decision-template.md`; `docs/exec-plans/roadmap.md`; `docs/exec-plans/proposed/index.md`; `docs/exec-plans/active/index.md`; `docs/exec-plans/completed/index.md`; `docs/exec-plans/plan-template.md`; `docs/exec-plans/reviews/index.md`; `docs/exec-plans/reviews/review-template.md`; `docs/optimization/index.md`; `docs/optimization/SOP.md`; `docs/optimization/record-template.md`; `docs/progress-archive/index.md`; `scripts/check-startup-doc-budget.py`.
- Verify: dependency-light checker gives specific failures; workflow names match config; governed skill validator scores at least 90; startup-doc budget passes.
- Exit: local and PR checks cover the governed structural contract without granting publish/merge authority.

### Phase 6 — Record-only optimization intake

- Entry: implemented scope is settled.
- Work: record audit follow-ups for schema/v5, providers, frontend duplication/scanner/chart, kline provenance, credentials/rate limits, Docker reproducibility, DB growth, pine/JSON provenance, branch protection, and Actions pins.
- Verify: every item includes evidence, impact, addressed/remaining state, disposition, plan need, and exclusion reason.
- Exit: no follow-up is accidentally implemented or described as approved.

### Phase 7 — Full verification, independent implementation review, closeout

- Entry: implementation and docs changes complete.
- Work: run the validation matrix; clean only known generated test/build artifacts; commission independent final diff review; remediate and repeat until accept; move plan to completed and synchronize all indexes/state.
- Verify: commands and results below plus independent accept; final status/diff checks; no stage/commit/push.
- Exit: completed plan, truthful `PROGRESS.md`/`HANDOFF.md`, and local unstaged/untracked diff ready for user review.

## 8. Validation Matrix

### Harness and repository

- `python3 scripts/check-project-harness.py --root . --profile governed`
- `python3 /Users/neowang/.codex/skills/project-harness-engineer/scripts/validate_harness.py --target . --profile governed --min-score 90`
- `python3 scripts/check-startup-doc-budget.py`
- lifecycle/index link checks
- `git diff --check`

### Backend and data safety

- focused rebuild/data-recovery tests
- `cd backend && PYTHONPATH=. python3 -m unittest discover -s tests -p 'test_*.py'`
- `cd backend && PYTHONPATH=. python3 -m compileall -q app scripts tests`
- `PRAGMA integrity_check` and `PRAGMA foreign_key_check`
- 46 market days; 2026-05-15, 2026-06-30, 2026-07-01, and 2026-07-17 present
- original 43-day hashes unchanged and recovered-day source hashes equal
- six-day seed rebuild against a temporary 46-day DB copy refuses and preserves original bytes
- date-complete but empty/count-mismatched bars, strategy/teaching shrink, and concurrent source drift all refuse promotion while preserving the live/new state

### Runtime and frontend

- SPY 2026-07-17 assemble with a known active strategy returns non-empty 1m and 5m bars
- 2026-06-30 and 2026-07-01 assemble/export payloads include reachable Tang overlays
- `cd frontend && npm run build`
- manual Review and Backtest one-day regression for 2026-07-17 when a browser runtime is available; otherwise record the exact unexecuted item, never a false pass

### Documentation and cleanup

- search active instructions/docs for obsolete endpoints, IB-first wording, `2026-04-22`, `minimal`, and waiting-to-commit statements
- allow clearly labeled historical evidence only
- verify deleted legacy docs outputs are absent and unreferenced
- ensure `frontend/dist`, `frontend/public/reviews`, and test caches are absent in final status

## 9. Deletion And Retention List

Delete only after recovery and consumer proof: `docs/index.html`, `docs/assets/`, `docs/reviews/`, `docs/reference.html`, `docs/reviewed/`, zero-byte `.codex`, and its contradictory ignore rule. These paths remain recoverable from Git history; do not create an in-repository archive.

Retain the tracked DB, gitignored seed model and its tracked README, active Pages publisher, DB-first export contract, backend provider stubs, frontend helpers/scanner/chart assets, Playwright, all other unapproved code, product roadmap, and canonical `strategies/STRATEGY.md`.

## 10. Rollback And Recovery Strategy

- Stop on baseline drift, historical-source conflict, inability to prove original-day preservation, candidate immutability failure, live consumer of a deletion target, secret exposure risk, repeated independent-review failure, or need for remote authority.
- Before DB promotion, rollback is candidate abandonment; the tracked DB remains unchanged.
- During promotion, use the shared repository write lock and require the current source identity/byte/full-logical digests to match the consistent-snapshot baseline. Any drift abandons the candidate and preserves the current live state. With the lock held, use a same-directory verified candidate and atomic replace. Retain a verified backup until post-promotion verification succeeds; if verification fails, atomically restore the backup under the same lock and stop.
- Source DBs remain available in commits `34caa03` and `1f15443`; deleted legacy docs remain recoverable from Git history.
- Code/doc changes remain an uncommitted local diff; this execution performs no destructive Git rollback.

## 11. Evidence And Review Locations

- Plan reviews: `docs/exec-plans/reviews/2026-07-18-tang-strategy-governed-harness-and-data-safety-recovery-plan/`
- Recovery/verification evidence: the `evidence/` child of that directory
- Decisions: `docs/decisions/2026-07-18-governed-harness-and-docs-authority.md` and `docs/decisions/2026-07-18-market-data-rebuild-safety-contract.md`
- Optimization follow-ups: `docs/optimization/2026-07-18-01-repository-audit-followups/2026-07-18-01-repository-audit-followups.md`

No evidence may contain credentials, secret values, tokens, or unredacted private configuration.

## 12. Review And Activation Gate

The proposed plan requires an independent reviewer verdict of `approve` (the plan-review term required by the repository's reviewer role). The reviewer must examine ID remapping, 43-day preservation, fail-closed defaults, atomic replacement, SPA/static-output distinctions, governed artifact completeness, deletion prerequisites, remote-authority boundaries, and scope control.

## 13. Final Acceptance And Closeout

- Independent implementation review: `implementation-review-001.md`
- Verdict: `accept`
- Confidence: `high`
- Lifecycle result: all locally authorized phases completed; plan moved from active to completed on 2026-07-18
- Residual record-only risks: future evidence value-level secret detection and an explicit dual-writer lock contention test
- Remote result: no stage, commit, push, PR, merge, Pages publish, branch protection, environment approval, or other remote mutation

If the reviewer returns `revise`, findings must be folded into this file and a new independent review produced until `approve`. Review approval is not normally activation. For this exact plan, the current user prompt has already granted one-time local activation authority after independent approval; activation changes lifecycle state only and grants none of the excluded remote actions.
