# Optimization Batch · 2026-07-22 Review Mobile Chart Canvas And Floating Filter Dock

> Record-only intake. This file does not authorize product implementation, plan promotion, activation, push, data mutation, publication, or remote action.
>
> Evidence images live in `./screenshots/`. The selected generated reference is the user-confirmed visual target. A sibling `mock.html` is a design-review aid only and does not grant implementation authority.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Replace stacked desktop mobile flow with a chart-first canvas and floating filter dock | Mobile Review + Static Review responsive layout | recorded | none | User selected the second generated direction on 2026-07-22 |
| OPT-002 | De-clutter mobile K-line trade annotations with progressive disclosure | Shared K-line trade-record marker rendering | recorded | none | Preserve direction-owned shape/color and current `*QTY` facts |
| OPT-003 | Make mobile review touch-first and keep context changes near the chart | Mobile chart gestures, marker selection, header, timeframe controls, dock, detail sheet | recorded | none | Coarse-pointer interaction is primary; keyboard is an accessibility fallback |

## Scope Lock (user-confirmed 2026-07-22)

| Topic | Lock |
| --- | --- |
| Selected direction | [`selected-mobile-chart-canvas-floating-filter-dock.png`](./screenshots/selected-mobile-chart-canvas-floating-filter-dock.png) is the **single visual target**. It is the second generated direction: chart canvas + floating filter dock. The earlier sticky-detail-sheet and later tabbed-workspace alternatives are not targets. |
| Primary mobile task | A user opens one Review/Static Review day, reads the K-line without label obstruction, changes ticker/date/timeframe without scrolling away from the chart, and opens trade detail on demand. |
| Target composition | At compact mobile widths, the chart is the primary canvas and occupies approximately the upper 70% of the usable viewport. A slim context header shows ticker/date, session change, and a compact `1m / 5m` control. |
| Floating dock | A three-action dock remains near the lower chart edge: `Ticker`, `Date`, `Filters`; the current date remains visible. This replaces the permanently expanded ticker/date/strategy stack on the primary mobile screen. |
| Toolbar reduction | The primary mobile chart exposes only compact indicator and marker-visibility controls plus timeframe switching. The full moving-average control row may live behind the indicator control; it must not consume the top of the mobile chart by default. |
| Marker default | Unselected mobile trade records render as small, collision-aware direction-owned markers. Nearby marks may collapse into a count/stack indicator. They must not paint repeated full trader-name labels over candles. |
| Marker selection | Only the selected trade may expand to a readable short label/detail affordance such as `vordinkkk BUY *150`. Existing display-name preference, BUY/SELL vocabulary, direction-owned shape/color/anchor, safe quantity completeness, and same-side same-bar `*QTY` semantics remain authoritative. |
| Detail entry | Beneath the chart, show a compact truthful summary and one clear `查看交易详情` action that opens or reveals the existing trade/signal detail surfaces. The mock may illustrate the entry; it must not invent new backend facts. |
| Touch/readability | Primary mobile controls use approximately 44px minimum hit areas. Normal control/body text targets 14–16px. Price/time axes remain readable; browser chrome and safe-area overlays must not cover app-owned actions. |
| Responsive target | Freeze portrait acceptance at 360×800, 390×844, and 430×932 CSS pixels. Add one compact landscape smoke check. Breakpoints are capability/layout driven, not tied to a named phone model. |
| Surface parity | Interactive Review and Static Review stay behaviorally aligned. Shared responsive projection and shared K-line marker logic are preferred over page-local forks. |
| Desktop preservation | Existing desktop Review/Static layout, desktop sidebar information density, chart marker contract, date membership/order, strategy selection semantics, and trader/signal content remain unchanged unless a later governed plan explicitly proves a required shared change. |
| Mock boundary | `mock.html` is self-contained, uses illustrative/synthetic chart data, and demonstrates the selected mobile state only. It is not production code, a live acceptance receipt, or authority to modify `frontend/src`. |
| Out of scope unless promoted and reviewed | Product implementation; schema/API changes; trade/content/DB writes; provider/broker access; Pages/publication; auth/security; Admin editor changes; desktop redesign; new market or strategy facts. |

## Touch-first Interaction Contract (user-confirmed 2026-07-22)

This surface is designed for fingers on a phone, not for a mouse cursor scaled down to a narrow viewport. Keyboard support remains an accessibility and desktop fallback, but it is not the primary mobile interaction model.

| Topic | Required behavior |
| --- | --- |
| Activation model | Capability and layout checks use coarse-pointer/touch semantics (for example `pointer: coarse`) together with available layout space. Width alone must not be treated as proof of touch input. |
| Discoverability | No required action or explanation may exist only on hover. Pressed, selected, disabled, loading, and open states must have persistent visible feedback. |
| Target size | Dock actions, timeframe choices, toolbar actions, close controls, and sheet actions provide at least a 44×44 CSS-pixel hit target with enough separation to prevent adjacent accidental activation. A marker glyph may remain visually small, but its canvas hit region must be at least 44×44 CSS pixels, approximately a 22-pixel hit radius. |
| Marker tap | A single tap selects one marker and exposes one short truthful label plus a visible detail affordance. It must not require double-tap, hover, long-press, or pixel-precise contact. |
| Cluster tap | Tapping a count/stack marker opens a visible choice/list for that cluster. It must not silently cycle through overlapping trades. |
| Gesture arbitration | Use Pointer Events (`pointerdown`, `pointermove`, `pointerup`, `pointercancel`) and pointer capture for chart-owned gestures. A movement threshold distinguishes tap from drag; releasing after a drag must not activate a marker. Mouse-only `click` handling is not sufficient evidence. |
| One-finger movement | A horizontal drag pans the chart time axis. A predominantly vertical drag remains available to the page or open sheet for native scrolling and must not be swallowed by the chart canvas. Because chart pinch is app-owned below, the interactive chart uses a policy equivalent to `touch-action: pan-y`; a blanket `touch-action: none` is not acceptable. Native takeover and `pointercancel` must leave chart state clean. |
| Two-finger movement | The product decision for pinch is explicit: two pointers that begin on the chart adjust chart scale and suppress marker activation, while browser/page pinch zoom remains available outside the interactive chart region. This ownership must not be implemented with `pan-y pinch-zoom`, because that would hand the chart pinch gesture back to the browser. |
| Floating dock | `Ticker`, `Date`, and `Filters` are direct tap actions with visible pressed/open state. Their sheets or pickers must preserve the chart context and make the current value clear before selection. |
| Bottom sheet | The detail/filter sheet supports a visible close action, backdrop tap, and optional downward swipe. It does not depend on the Escape key. While open, the background is inert; the sheet uses modal semantics, accessible focus management as a fallback, and safe-area bottom padding. |
| Occlusion | The dock, expanded marker label, and sheets must not cover the active marker hit region or permanently obscure the price/time axes. Browser chrome and device safe areas must not cover app-owned actions. |
| Acceptance | Validate at 360×800, 390×844, and 430×932 portrait sizes plus compact landscape using real touch hardware or touch emulation. Exercise marker tap and hit slop, cluster selection, tap-versus-drag cancellation, horizontal chart pan, vertical page/sheet scroll, two-finger chart scale, sheet open/close, rotation, and safe-area behavior. Mouse-click-only proof does not pass. |
| Parity and regression | Interactive Review and Static Review share the same touch behavior. Desktop mouse and keyboard behavior remains a non-regression requirement, but must not dictate the mobile gesture design. |

## Visual Evidence

| File | Role | SHA-256 | Size | Dimensions |
| --- | --- | --- | ---: | ---: |
| [`current-mobile-static-review.png`](./screenshots/current-mobile-static-review.png) | User-provided current Pages/mobile friction: chart labels overlap candles and selectors sit below the chart | `95b160c87907ebe4ff9bd73834299726ef987da8952a39ac8b2549190cc65123` | 968,514 bytes | 1290×2796 |
| [`selected-mobile-chart-canvas-floating-filter-dock.png`](./screenshots/selected-mobile-chart-canvas-floating-filter-dock.png) | User-selected generated target, second ideation direction | `2618ade2830f22d779855e3352e2d6ab1e416df96fee4919ec682faf1913e161` | 1,233,963 bytes | 853×1844 |

## Current Code Anchors (read-only evidence)

| Area | Current anchor |
| --- | --- |
| Mobile page ordering | `frontend/src/styles.css:992-1010` mobile grid currently orders `chart` before `sidebar`, leaving context controls below the chart |
| Static context stack | `frontend/src/pages/StaticReviewsApp.jsx` renders `ReviewContextPanel`, Strategy, filters, trades, and signals inside `.dr-sidebar` |
| Mobile chart sizing | `frontend/src/kline/kline-engine.js:521-541` mobile media rule reduces padding and fixes chart height, but does not change annotation density |
| Full trade labels | `frontend/src/kline/kline-engine.js:2271-2285` draws a full label rectangle for every visible `trade_record` annotation |

### Touch-contract Gap Evidence (read-only, verified 2026-07-23)

Recorded because the Touch-first Interaction Contract above has no existing implementation to extend. Absence rows were established by repository-wide search under `frontend/` excluding `node_modules`; they are stated as zero-match facts, not as inferences. Nothing in this section authorizes a change.

| Area | Current anchor |
| --- | --- |
| Gesture ownership | No `touch-action` declaration exists anywhere under `frontend/` (0 matches). The interactive canvas therefore runs on the default `auto`, so the browser may claim a drag and implicitly cancel the pointer stream mid-pan. The contract requires an explicit `pan-y`-equivalent policy. |
| Pointer lifecycle | `frontend/src/kline/kline-engine.js` binds `pointerdown` (`:1292`), `pointermove` (`:1242`), and `pointerup` (`:1309`), but no `pointercancel` handler exists under `frontend/` (0 matches). Only `lostpointercapture` (`:1318`) clears `dragState`, and it does not reset `_wasDragging`, so native-takeover cleanup is incomplete. |
| Multi-pointer | `pointerdown` (`:1292-1308`) keeps a single `dragState` and overwrites it when a second pointer arrives (`:1297`). Chart scale is bound to `wheel` only (`:1260-1291`); no two-pointer scale path exists. The canvas binds eight listeners total (`:1087`, `:1241`, `:1242`, `:1260`, `:1292`, `:1309`, `:1321`, `:1334`) and none are touch or gesture events. |
| Tap versus drag | Activation runs on `click` (`:1321-1333`), not `pointerup`. The drag threshold is 3 CSS px (`:1313`), below normal finger tremor for a stationary tap. |
| Marker hit region | `_hitTestAnnotation` (`:2379-2387`) tests the exact label rectangle with no slop. The zone is built at `:2287-2299` from a marker radius of 8/10 px (`:2239`) plus an 18 px-tall label (`:2274`), against the contract's 44×44 CSS px / ~22 px radius requirement. |
| Hover-only information | The annotation tooltip and the OHLC hover card are driven by `mousemove` / `mouseleave` (`:1241`, `:1334`) via `_updateAnnoHover` (`:2437`) and `_updateHoverCard` (`:2453`). On a coarse pointer neither surface is reachable, so per-bar OHLC readout and per-marker detail have no touch path. Any pointer-driven replacement is a shared change and engages the Desktop preservation lock. |
| Touch target size | Toolbar controls use `min-height: 32px` with 12 px labels (`:262-273`); the MA value readout renders at 10 px (`:300-306`). |
| Capability detection | No `pointer: coarse`, `hover: hover`, `matchMedia`, or any touch-capability check exists under `frontend/src` (0 matches). All responsive behavior keys on width alone, which the Activation model lock disallows as sole proof of touch input. |
| Responsive breakpoints | Width-only breakpoints are 820 px (`frontend/src/styles.css:103`), 980 px (`:992`, `:1106`), and 1100 px (`:1226`), plus 900 px in `frontend/src/kline/kline-engine.js:521`. No rule targets the locked 360 / 390 / 430 acceptance widths, and there is no landscape rule. |
| Fixed mobile chart height | The 900 px rule pins `.kline-engine__viewport`, `.kline-engine__canvas-wrap`, and `.kline-engine__canvas` to `min-height: 420px; height: 420px` (`frontend/src/kline/kline-engine.js:538-539`) — a fixed pixel height, not a share of the viewport. The outer `.unified-kline-engine` wrapper separately floors at `min-height: 560px` (`frontend/src/styles.css:1110-1114`) with no compact override. |
| Safe area | `frontend/index.html:5` declares `width=device-width, initial-scale=1.0` with no `viewport-fit=cover`, and no `env(safe-area-inset-*)` usage exists under `frontend/src` (0 matches). |

## OPT-001 Chart-first Mobile Canvas And Floating Filter Dock

- Source evidence: current mobile screenshot and the user-selected generated target above.
- Current friction:
  - The compact breakpoint mainly stacks the desktop workbench into one column.
  - Context controls remain in the former sidebar below the chart, so a date/ticker/strategy change separates the action from the resulting chart.
  - The expanded indicator toolbar and selector stack compete with the K-line for the mobile viewport.
- Desired outcome:
  - A compact context header and chart dominate the primary mobile screen.
  - Ticker/date/filter changes remain one tap away in a floating dock near the chart.
  - The detailed trade/signal content stays available through one clear disclosure action rather than being permanently expanded on the primary screen.
- Boundary that must not change:
  - No desktop redesign, no date inventory/order change, no strategy-assembly change, and no loss of Review/Static functionality.
- Lifecycle status: `recorded`; no proposed plan.

## OPT-002 Progressive Disclosure For Mobile Trade Markers

- Source evidence: repeated `vordinkkk BUY/SELL` labels overlap candles in the current mobile screenshot; selected target uses compact markers and one selected label.
- Code evidence: see Touch-contract Gap Evidence above — the unconditional label rectangle (`kline-engine.js:2271-2285`), the no-slop exact-rectangle hit test (`:2379-2387`), and the hover-only annotation tooltip (`:1241`, `:2437`) are the current anchors for marker density, marker tap, and marker detail respectively.
- Current friction:
  - Every visible trade annotation receives a full label, even when the chart width cannot accommodate the labels.
  - Clamped labels overlap each other and the candle field, obscuring the market move the page exists to review.
- Desired outcome:
  - Default mobile markers stay compact and collision-aware; nearby events may use a truthful count/stack affordance.
  - A forgiving single tap selects one marker and reveals that trade's readable display name, BUY/SELL side, and safe `*QTY` fact.
  - A cluster tap opens a visible choice/list rather than silently cycling through overlapping trades.
  - The price scale, time scale, candles, volume, and accessible focus fallback remain legible and available while touch gestures follow the contract above.
- Boundary that must not change:
  - Preserve direction-owned marker shape/color/anchor, normalized action vocabulary, display-name preference, same-side same-bar grouping semantics, safe quantity completeness, and source trade facts.
- Lifecycle status: `recorded`; no proposed plan.

## OPT-003 Touch-first Mobile Review Interaction

- Source evidence: the current compact date and toolbar controls are visually dense; the selected target promotes three large dock actions and a compact timeframe control.
- Code evidence: see Touch-contract Gap Evidence above. No clause of the Touch-first Interaction Contract currently has an implementation to extend: gesture ownership, pointer-cancel cleanup, two-finger scale, tap-versus-drag, forgiving hit regions, capability detection, target size, and safe-area handling are all either absent (0 matches) or bound to a mouse-only path. The contract therefore describes new engine behavior, not a refinement of existing behavior.
- Current friction:
  - Date chips and secondary chart controls are small and crowded on a touch viewport.
  - Browser chrome can cover lower-page controls while the long page requires repeated scrolling.
  - A mouse-style `click` model does not define tap-versus-pan cancellation, vertical scroll ownership, multi-touch behavior, forgiving marker hit regions, or touch-visible state feedback.
- Desired outcome:
  - Primary actions and canvas markers meet the locked hit-area, gesture, and readable-type targets.
  - Pointer-based gesture arbitration keeps marker taps, horizontal chart pan, vertical page/sheet scroll, and two-finger chart scale distinct.
  - The app-owned detail entry remains clear above safe-area/browser overlays.
  - Secondary options use a touch-native drawer/sheet/menu pattern without becoming permanent primary-screen chrome or depending on hover, Escape, or precision input.
- Boundary that must not change:
  - Do not remove supported controls or data; this is responsive disclosure and touch behavior, not a reduced product contract. Keyboard and mouse support remain available for accessibility and desktop regression coverage.
- Lifecycle status: `recorded`; no proposed plan.

## Kimi Mock Task

- User instruction: create this OPT batch, then notify Kimi to generate a self-contained `mock.html` from the selected visual target.
- Kimi is authorized only to create `./mock.html` within this batch.
- The mock must not modify product source, runtime data, lifecycle plans, indexes, state files, or unrelated `output/` artifacts.
- The interrupted Kimi session's initial `apply_patch` materialized as `./mock.html` after the interruption and failed the first touch review. The resumed session replaced its interaction layer against this record's touch-first contract.
- The mock must use Pointer Events for marker selection and chart gestures, demonstrate tap-versus-drag cancellation and forgiving marker hit regions, preserve vertical page/sheet scrolling, expose visible touch state feedback, and include an in-page touch acceptance checklist. A set of `click` handlers alone is not acceptable.
- Touch review of the initial file: `revise`. It activates a marker immediately on `pointerdown`, provides no `pointermove` / `pointerup` / `pointercancel` or pointer capture, uses `touch-action: manipulation`, leaves timeframe/tools on `click`, and does not implement chart pan, two-finger chart scale, cluster choice, or the required dock/detail sheets.
- Touch review of the revised file: `pass`. A coarse-pointer Playwright context verified 1m/5m tap, 22px-radius marker hit slop, visible cluster choice, drag-release cancellation, horizontal pan after zoom, vertical-drag arbitration, `pointercancel` cleanup, two-pointer chart scale, modal/inert sheet behavior, visible close, backdrop close, downward-swipe close, and the all-trades detail entry. Layout checks passed at 360×800, 390×844, 430×932, and 844×390 with no horizontal page overflow, primary targets at least 44px high, and a compact-landscape chart height of at least 180px. Final 390×844 screenshot inspection and browser console were clean.
- Final mock: [`mock.html`](./mock.html), 47,529 bytes, SHA-256 `3bb5fd93c0190d2d467405ddd32dde6f219b3e2a63b9df8eb5e0fbd9a50101d6`.
- Mock review status: complete for record-only design review; no product implementation authority.

## Explicit Non-Authorization

This record and its mock do **not** authorize implementation, proposed-plan creation, design review, activation, product/data/DB mutation, push, PR, merge, Pages, provider/broker access, hosted verification, or any remote action.
