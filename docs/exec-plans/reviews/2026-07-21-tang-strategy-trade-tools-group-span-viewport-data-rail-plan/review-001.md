# Review 001 — Tang Strategy Trade Tools, Group Span, Viewport, And Data Rail

- Review target: `docs/exec-plans/proposed/2026-07-21-tang-strategy-trade-tools-group-span-viewport-data-rail-plan.md`
- Review target revision: `v1-proposal-2026-07-21`
- Review type: design
- Reviewer ID: `codex-reviewer-2026-07-21-trade-tools-group-span-viewport-data-rail-r1`
- Plan author ID: `grok-plan-author-2026-07-21-trade-tools-group-span-viewport-data-rail`
- Independence declaration: `attested`
- Evidence method: `Independent inspection of the exact plan and OPT source, all six visual-evidence files, live Review/Static/Admin filter and export consumers, group-selection and K-line viewport/highlight code, Data/Review progressive-rail composition and CSS, canonical QQQ fixture, related tests, and lifecycle checks. All six listed evidence SHA-256 values matched. Exact reviewed plan SHA-256: 8d179e57d356214dbe9f6ca80d8ab4142b21cd9cf37f43dafbae6721b6bb16b9. Repository HEAD: fb3eae63adc508ff77695f45cf6baa3b299eeee2.`
- Verdict: revise
- Confidence: high

## Scope Checked

- OPT-003…006 objective, product locks, non-goals, and completed OPT-001/002 boundary
- Review, Static, and Admin list, availability, filter-state, and four-file export behavior
- Group event aggregation, span fitting, highlight rendering, timeline meta, and secondary event focus
- K-line timeframe transition, viewport state, first-frame rendering, and available verification seams
- Data progressive rail versus Review sidebar cascade, accessibility, and visual evidence
- Frozen manifest, phase gates, lifecycle wording, unrelated-change protection, and authority limits

## Findings

| Severity | Location | Finding | Required change |
| --- | --- | --- | --- |
| P1 | §1.4 OPT-003 filter default; §2.2 criteria 2 and 11; §2.4 `N-Eligibility-default`; §3.1 items 1–3 and 10; Phase 1 WU-A | Removing the control does not freeze one display-only authority for list, availability, and export. Live behavior is inconsistent for an omitted or stale value: `displayableTradeGroups` defaults a missing `eligibility` to display, while `filterTradeGroups` treats it as no eligibility filter and `exportSelectionFromFilters` emits `display_only: false`; a stale `reported` or `calculated` value likewise remains meaningful after the UI disappears. The proposed pure default fixture can pass by checking only `initialTradeRecordFilters().eligibility === 'display'` while Review, Static, or Admin still exports non-display groups from hidden state. | Define a canonical, non-user-changeable display-only contract for the shared tools path. Either normalize every incoming filter state to `display` before availability/list/export consumption or remove the runtime dimension and make all three helpers default and fail closed to display-only. Add fixtures with omitted, `reported`, and `calculated` legacy inputs plus a non-display group; prove identical display-only group IDs and `display_only: true` exports on Review, Static, and Admin while preserving the separate Admin editor eligibility fields. |
| P1 | §1.4 OPT-005 group select/highlight; §2.2 criteria 5–9; §2.4 `N-Group-span`, `B-Group-span`, and `N-Event-focus`; §3.1 items 2–6; Phase 1 WU-B | The span-fit contract can still pass its helper test while failing in the live integration. Both consumers currently call `fitRange` and then `scrollTo(... center: true)`, which can recenter on one event and undo the fitted span. The plan also permits a `marker` band, but the live engine intentionally renders both `marker` and `olive` multi-bar ranges as one dot; only red/blue styles paint bands. `B-Group-span` remains an interaction-or-screenshot choice, and event-row focus is simultaneously an objective/criterion and optional in the manifest. The displayed `N pts` count is also not defined for incomplete-time events even though the time-span helper excludes them. | Freeze one integration sequence for both Review and Static: derive all mappable group event indices, set a real neutral multi-bar band, call `fitRange` once, and do not follow it with a centering operation that changes the fitted viewport. Add the required neutral-band engine behavior to the exact manifest or choose another explicit rendering contract. Decide whether event-row focus is required; if required, freeze the callback and focused-event behavior. Define `N pts` as all rendered events or explicitly as known timed events. Make one mandatory interaction carrier assert the stored highlight start/end, final visible window containing the full group span, single-event behavior, and Review/Static parity; screenshots remain visual evidence, not an interaction substitute. |
| P1 | §1.4 OPT-004 outcome; §2.2 criterion 4; §2.4 `N-TF-viewport` and `B-TF-first-paint`; §3.1 items 6 and 10; Phase 1 WU-C | The first-paint gate is not frozen to an executable carrier. The matrix says to use a pure helper if extractable, otherwise a browser or engine harness; WU-C again allows either carrier. The current test suite has no runtime K-line test, the engine is a browser-owned script rather than an importable pure module, and V4 cannot prove that the captured image is the first requested frame or that no wheel event occurred. A source-only transition helper can also pass while `setTimeframe`, `scheduleRender`, or retained `zoomScale`/`followMode` still produces the reported first frame. | Select one mandatory carrier before approval. Either add a named importable viewport-transition seam and an integration check that drives the real `setTimeframe`, or freeze a deterministic browser carrier with an exact fixture, no-wheel event log, timeframe click, first animation-frame boundary, and assertions over the rendered visible `start/end/count`, slot occupancy, `zoomScale`, and `followMode`. Require 1m→5m and 5m→1m. Keep V4 supplemental and add every required tracked test seam to the manifest. |
| P2 | §1.4 OPT-006 layout; §2.2 criterion 10; §2.3 V3; §2.4 `N-Data-rail-source`; §3.1 items 7–9; Phase 1 WU-D | The plan asks source inspection plus a Data-only screenshot to protect the Review sidebar. That cannot detect computed cascade regressions in the shared `.ticker-tabs` and `.date-rail-mode` controls. The suggested `.page .panel .review-context-panel` selector is more specific than several shared rules and is tied to generic layout classes rather than an explicit Data density variant; a future or nested `.page .panel` composition could inherit it. No visual or computed-style carrier checks the required Review desktop/narrow behavior after the override. | Freeze an explicit Data host or density class and scope all flex/max-width overrides under it. Add deterministic computed-layout assertions for content-sized Data controls and unchanged Review sidebar controls, plus visual coverage for Data desktop and Review sidebar desktop/narrow. Preserve the existing tab/group roles and progressive state behavior. |

## Verified Strengths

- All six SHA-256 values in §1.2 match the repository files, and the visuals reproduce the four stated UI failures.
- The source OPT truthfully promotes only OPT-003…006; completed points-only cards and display-name BUY/SELL markers remain protected.
- Current source confirms the stated shared consumers, first-annotation group selection, timeframe transition surface, and global flex rules.
- QQQ `2026-07-17` contains two real multi-event `vordin` groups, including a six-event CALL group, so the V1/V2 fixture is suitable.
- The frozen production paths contain the known implementation surfaces and exclude backend, DB, content, provider, broker, publisher, and remote changes.
- Baseline lifecycle and harness checks passed before reconciliation.

## Unverified Items

- No product implementation or runtime acceptance was performed because this is a design review.
- Final chart aesthetics and first-frame behavior remain unverified until a revised plan defines and later executes the mandatory carriers above.

## Verdict Rationale

The product direction and authority boundaries are sound, but exact revision `v1-proposal-2026-07-21` can pass its named source tests and screenshots while exporting the wrong eligibility set, recentering away from a group span, drawing a dot instead of the required band, or capturing a repaired rather than first timeframe frame. The Data-only evidence also does not protect the shared Review rail. These are bounded design and verification corrections, so `revise` is appropriate rather than `reject`. This review does not activate or implement the plan and grants no content, DB, provider, broker, publication, push, or remote authority.
