# Review 002 — Tang Strategy Terminal UI Fusion And Trader Registry

- Review target: `docs/exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md`
- Review target revision: `v2-review-foldback-2026-07-20`
- Review type: design
- Reviewer ID: `grok-build-design-reviewer-2026-07-20-terminal-ui-registry-r2`
- Plan author ID: `codex-plan-author-2026-07-20-terminal-ui-registry`
- Independence declaration: `attested`
- Evidence method: Independent re-read of exact revision `v2-review-foldback-2026-07-20` at SHA-256 `40afdcfd1eb98594a8f4816ad652411ca8957c371cfc8a315b975bcaf3dad12e`; closure check of every `review-001` finding against operative v2 sections; live re-check of `_TRADER_ID_RE` / `_COLOR_RE` / `content/schemas/traders.schema.json`, admin registry PUT path and API client error carrier, `Layout.jsx` bottom-secondary structure, `frontend/package.json` `test:trade-records` carrier, protected DB/registry/publisher/exporter hashes, token contrast pairs, optimization batch status, and operating-modes Proposed-gate wording. No implementation, browser acceptance, data write, provider/broker, push, or publication was performed.
- Verdict: approve
- Confidence: high

## Scope Checked

- Frozen v2 identity and foldback provenance (§1.4) against claimed SHA and revision id
- Every `review-001` blocking/medium/non-blocking finding against v2 operative contracts
- Objective, success criteria, non-goals, token table, shell/nav, Review fusion, create-trader, and protected boundaries
- File surface, phases 0–6, verification matrix, rollback, authority/activation gates
- Live repository evidence for create-boundary regexes, no-backend path, and current UI friction still present

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| None | — | — | — |

## Prior Finding Closures

Independently re-verified against live code and operative v2 text:

1. **Blocking — wrong `trader_id` regex (review-001).** Live `_TRADER_ID_RE` and schema remain `^[a-z][a-z0-9_]{1,63}$`. V2 §1.2, §1.4, success criterion 8, §3.4, Phase 0 fixtures, and pure-helper language all use that exact pattern, pin 2/64-character bounds (`ab` / length 64 accept; one-char / length 65 / uppercase / leading digit / hyphen reject), and remove the invented `{2,191}` range entirely.

2. **Medium — color format (review-001).** Live `_COLOR_RE` / schema remain `^#[0-9A-Fa-f]{6}$`. V2 freezes the same exact regex, requires the leading `#`, forbids silent auto-prefix, and keeps server validation authoritative.

3. **Medium — server field-path association (review-001).** Live client still surfaces `response.text()` as `Error.message`; FastAPI still wraps validation as HTTP 400 `detail=str(exc)`. V2 §3.4 requires parse-JSON-`detail` first, raw-text fallback second, associate only recognized `registry.traders[<index>].<field>` paths that map to a rendered control, and otherwise form-level `role="alert"` without inventing success or requiring API/backend changes.

4. **Non-blocking — peer-nav placement (review-001).** V2 freezes bottom-pinned placement after the flexible spacer, peer renderer/classes/state only, not insertion into the upper Data→Teaching order. Matches current `Layout.jsx` structure (`</nav>` then secondary button) while removing the orange CTA / refresh semantics.

5. **Non-blocking — `package.json` rationale (review-001).** V2 keeps the `test:trade-records` script name stable and only appends `src/features/review/traderRegistry.test.js` to the existing `node --test` file list. Live carrier currently lists `tradeRecords.test.js` and `reviewWorkspace.test.js`, so the planned one-file append is coherent.

## Verdict Rationale

**Verdict: `approve` / confidence `high`.**

V2 is a complete, implementable foldback of `review-001`. No blocking or medium contract gap remains for design approval of this exact revision.

**Current-contract coherence against live evidence:**

- Protected baselines still match: tracked SQLite `125fcc9d…05b0`, registry `9668400f…3734`, Pages publisher `baaf5ad0…5b37`, static exporter `e3f66de6…00cb`; trade-day count remains 22.
- Live UI friction still matches the plan: orange `.secondary` trader entry with `RefreshCcw`, paper/root vs `.dr-shell` dual skin, Admin registry edit-only, shared trade components with `.dr-sidebar` dark patches.
- Create path remains no-backend: admin-only full-registry PUT, repository revalidation, atomic replacement, rollback-coherent projection; pure frontend helpers must mirror live slug/color regexes without silent rewrite.
- Single-plan bundling of OPT-001..004, terminal-first token table, contrast claims, phase gates, isolated temp-copy mutation tests, and authority ledger remain consistent with `docs/operating-modes.md`.
- §9 correctly states that `review-001` cannot approve v2 and that activation/implementation remain separate user instructions.

**Residual non-blocking implementation freezes (do not reopen design):**

- Phase 0 may still choose whether the bottom-pinned peer item lives inside or immediately after the navigation landmark, provided accessible name, `aria-current`, keyboard order, and collapsed geometry stay peer-equivalent.
- §3.1’s phrase “v1 implementation target” refers to the token table generation, not the plan revision id; implementation should freeze the table as written for this approved revision.

**Authority boundary:** This matching-revision design `approve` does **not** activate the plan, start implementation, stage/commit/push, write canonical data, open PR/merge, publish Pages, or grant provider/broker/remote authority. After this review, the next legal user action is an explicit activation instruction that must stop at `phase-0:not-started`; implementation requires a later explicit start instruction.

## Unverified By Design-Review Boundary

- Browser/desktop-narrow visual execution and future computed-style contrast
- Actual temporary-copy create-trader acceptance
- Hosted Pages, provider/broker, and tracked content mutation behavior
- Sibling concurrent review output for this same revision
