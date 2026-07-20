# Review 001 — Tang Strategy Terminal UI Fusion And Trader Registry

- Review target: `docs/exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md`
- Review target revision: `v1-proposal-2026-07-20`
- Review type: design
- Reviewer ID: `grok-build-design-reviewer-2026-07-20-terminal-ui-registry-r1`
- Plan author ID: `codex-plan-author-2026-07-20-terminal-ui-registry`
- Independence declaration: `attested`
- Evidence method: Live worktree inspection of exact revision `v1-proposal-2026-07-20` (SHA-256 `c2c209275e69a7643a1bcce9577651af8e207b34e3571ac22e8b7cdd153a923f`) against current HEAD `115d2cfee1d7e408b5ecd4465db73064c0d717b5`, source optimization batch + six screenshot hashes, `Layout.jsx` / `AdminTradersPage.jsx` / shared Review trade components / `styles.css`, backend `validate_trader_registry` + schema + admin PUT path, frontend API error carrier, protected DB/registry/publisher/exporter hashes, and operating-modes design-review contract. No implementation, browser acceptance, data write, provider/broker, push, or publication was performed.
- Verdict: revise
- Confidence: high

## Scope Checked

- Plan objective, success criteria, non-goals, and single-plan bundling of OPT-001..004
- Live repository evidence claimed in §1.1–1.2 against current HEAD and worktree
- Terminal token table, contrast claims, shell/nav, Review fusion, and create-trader contracts
- Candidate file surface, phase gates, verification matrix, rollback, and protected boundaries
- Authority/lifecycle wording against `docs/operating-modes.md` (review-only; no activation/implementation)
- Source optimization locked decisions (terminal-first, peer nav, inline create, no backend contract expansion)

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| Blocking | §1.2 create-boundary claim | Plan states `trader_id` must match `^[a-z][a-z0-9_]{2,191}$`. Live Python validator and `content/schemas/traders.schema.json` both enforce `^[a-z][a-z0-9_]{1,63}$` (min length 2, max 64). Independent checks: `ab` accepted, single-char rejected, length 64 accepted, length 65 rejected. A pure frontend helper that copies the plan regex will diverge from the authoritative server boundary. | Replace every create-trader identity pattern with the live contract `^[a-z][a-z0-9_]{1,63}$`. Pin the same pattern in §1.2, §3.4, Phase 0 fixtures, and pure-helper acceptance language. |
| Medium | §1.2 / §3.4 color vocabulary | Plan says “six-digit hex color” but omits the authoritative format. Live `_COLOR_RE` / schema require `^#[0-9A-Fa-f]{6}$` (leading `#` required; case-insensitive hex). | Freeze color as exact `^#[0-9A-Fa-f]{6}$` in create-trader contract and fixtures; keep client advisory and server authoritative. |
| Medium | §3.4 server field-path association | Plan assumes errors contain a stable `registry.traders[index].field` path. Live backend raises `TradeValidationError(f"{path}: {message}")`, FastAPI wraps it as HTTP 400 `detail=str(exc)`, and `frontend/src/api/client.js` surfaces `response.text()` (JSON body, not a bare path). Substring match can still work, but path association is under-specified. | Specify that field association parses/searches the API error body (JSON `detail` or raw text) for `registry.traders[<index>].<field>` and otherwise falls back to form-level `role="alert"` without inventing success. |
| Non-blocking | §3.2 peer-nav placement | “Fifth peer destination” is clear on chrome/state, but does not freeze whether the item remains bottom-pinned (`margin-top: auto`) or moves into the upper `nav` stack order. Optimization allowed either peer treatment. | In Phase 0/1 freeze one placement: either inside the primary stack in declared order, or bottom-pinned while using the same peer item classes/state contract. |
| Non-blocking | §4.2 `frontend/package.json` | Listed as a candidate modification without naming the required carrier change. Existing style assertions live in `tradeRecords.test.js` (`#fff` Admin button pins). | Either drop `package.json` unless a script body must change, or state the exact carrier edit (name-stable script body expansion only). |

## Verdict Rationale

**Verdict: `revise` / confidence `high`.**

The proposal is directionally correct, evidence-backed, and mostly implementable. Independent inspection confirms:

1. **Provenance and evidence are real.** Optimization batch is `promoted-to-proposed`; six screenshot SHA-256 values match on-disk PNGs; live HEAD is `115d2cfee1d7e408b5ecd4465db73064c0d717b5` as claimed; protected hashes for tracked DB, registry, Pages publisher, and static exporter match §1.2 exactly; trade-day count is 22.
2. **Current UI friction matches the plan.** `Layout.jsx` still renders `交易记录 / 点位管理` outside the primary nav as `.secondary` with `RefreshCcw`; CSS still has paper root tokens, warm-brown sidebar, orange secondary CTA, and `.dr-shell` charcoal/olive island; `AdminTradersPage` only maps existing traders via `updateRegistryTrader` with no create action; shared trade-panel styles still rely on `.dr-sidebar` dark patches over light defaults.
3. **User-locked product decisions are correctly carried.** OPT-004 terminal-first; warm orange brand-only; peer-nav fusion; Review left-column continuity; create-trader via full-registry admin PUT without fabricating days/groups; no backend/schema/DB/publisher expansion.
4. **Token table and contrast math check out.** Recalculated ratios for primary/muted/accent/status/brand pairs match the stated values (e.g. primary-on-panel `13.48:1`, muted-on-panel `6.83:1`, accent-on-panel `5.51:1`).
5. **No-backend create boundary is real.** `GET/PUT /api/admin/traders` are admin-only; `handle_trader_registry_admin_write` validates the full registry, revalidates the trade repository, atomically replaces `content/traders/index.json`, and projects through the existing rollback-coherent path. A registry-only third trader does not require new routes.
6. **Phase structure, acceptance matrix, isolated temp-copy write tests, and authority ledger are coherent** with `docs/operating-modes.md`. Design approval still cannot activate or implement; activation and implementation remain separate user instructions; Git/data/remote remain unauthorized.

The blocking defect is contract accuracy, not product direction: §1.2 invents a trader_id regex that neither the runtime validator nor the JSON Schema accepts. Because Phase 4 pure helpers and client validation are supposed to mirror that boundary without silent rewrite, approving this exact revision would freeze a false create contract. Medium findings on color format and server-error association should be folded in the same revision so create-trader fixtures and field-error UX are unambiguous.

**After foldback, re-review the new stable revision.** Approval of `v1-proposal-2026-07-20` does not qualify. This review does not activate, implement, stage, commit, push, write canonical data, or grant any remote/publication authority.

## Unverified By Design-Review Boundary

- Browser/desktop-narrow visual execution and real contrast of future computed styles
- Actual create-trader temporary-copy acceptance (not authorized)
- Any sibling concurrent review output
- Hosted Pages, provider/broker, and tracked content mutation behavior
