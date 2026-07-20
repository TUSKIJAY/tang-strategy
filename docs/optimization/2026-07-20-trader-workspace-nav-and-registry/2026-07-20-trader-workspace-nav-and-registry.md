# Optimization Batch · 2026-07-20 UI Fusion, Color Unification, And Trader Registry

> Promoted by explicit user request to a review-only [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md), now at `v2-review-foldback-2026-07-20` after [`review-001: revise`](../../exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/review-001.md) was folded back and exact-v2 [`review-002: approve`](../../exec-plans/reviews/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan/review-002.md) closed the design gate with no findings. This record and its plan do not authorize implementation, activation, frontend change, Git, data write, provider/broker, Pages, or remote action.

| ID | Title | Area | Status | Lifecycle link | Notes |
| --- | --- | --- | --- | --- | --- |
| OPT-001 | Fuse bottom-left trader-workspace entry with the primary sidebar nav | App shell / navigation | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md) | User locked: peer chrome with upper nav; drop orange CTA |
| OPT-002 | Make adding a new trader discoverable in the registry form | Admin trader registry | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md) | Registry only edits existing rows; plan selects an inline create draft with user-entered stable slug |
| OPT-003 | Fuse Review trade-filter/list block with upper Review context chrome | Review left column / trade panel | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md) | Eligibility / Focus / Download / cards join the shared terminal tokens and Review density |
| OPT-004 | Unify Review color system with the rest of the app | App-wide visual language | promoted-to-proposed | [proposed plan](../../exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md) | User locked **A terminal-first**: promote Review charcoal/olive family app-wide |

## Visual Reference

1. Admin registry (add-trader gap + orange entry): [`./screenshots/2026-07-20-trader-workspace-admin-registry.png`](./screenshots/2026-07-20-trader-workspace-admin-registry.png) · SHA-256 `25bdeff5675b4225b544d16609bbb9ec01ad3387728bafed51976d2bac5e95ec`
2. Review page, collapsed outer rail + trade panel (nav fusion): [`./screenshots/2026-07-20-sidebar-trader-nav-mismatch-review.png`](./screenshots/2026-07-20-sidebar-trader-nav-mismatch-review.png) · SHA-256 `bfbd714306617e32a91e0465590b8b78e5c30224e27b9b24b80e443f0a155b74`
3. Trade-list close-up with orange control bleed: [`./screenshots/2026-07-20-sidebar-trader-nav-overlap-detail.png`](./screenshots/2026-07-20-sidebar-trader-nav-overlap-detail.png) · SHA-256 `fdc23fd07f52cd0b14fb10858dcc5a2d475b4cb6afa5d03f62ac8f5320db4b11`
4. Review trade-filter crop (user “这部分呢”): [`./screenshots/2026-07-20-review-trade-filter-panel.png`](./screenshots/2026-07-20-review-trade-filter-panel.png) · SHA-256 `b7207ba5483f15b4ff7e85892e8da66b01b7abc5c9b8207f82c87736713d970a`
5. Full Review + expanded shell (color mismatch): [`./screenshots/2026-07-20-review-color-vs-shell.png`](./screenshots/2026-07-20-review-color-vs-shell.png) · SHA-256 `ace946064f534785b6cbc109e7b84cef17587302798f98e7415fc5f7dc8efc08`
6. Second full Review frame: [`./screenshots/2026-07-20-review-color-second.png`](./screenshots/2026-07-20-review-color-second.png) · SHA-256 `6160264e8fc18b9d36230b96a37a46d8d8f578656b241539078a948280263223`

What these show together:

- **Two product skins:** outer shell + Data/Admin/Backtest/Teaching use warm paper tokens; Review mounts a full charcoal terminal via `.dr-shell`.
- Upper outer rail: quiet dark (warm brown) icon stack; bottom-left trader entry is still an orange CTA (OPT-001).
- Review content: cool near-black `#141413` / `#1E1E1D` with olive `#8B9A6D` accents — not the same brown family as the shell, and not the cream paper of other pages.
- Trade filter block still shows light form widgets (e.g. white Eligibility select) against dark Review (OPT-003).
- Admin registry remains edit-only for existing traders (OPT-002).

### What the pink-boxed region is (not the outer nav)

The crop in screenshot 4 is **not** the app-shell `交易记录 / 点位管理` button. It is the **Review business panel** for trade records:

| UI block | Component | Role |
| --- | --- | --- |
| Eligibility select | `TraderFilters` | Filter which groups count for display/stats |
| Trader checkbox + Focus | `TraderFilters` | Availability-driven trader visibility / focus |
| Download JSON + 3 CSV | `TradeExportControls` | Export current filter selection |
| Tang · PUT card / legs | `TraderTradeList` | Group list + drilldown |

It lives in `ReviewPage`’s left column under the workspace date rail and strategy controls. The orange fragment on the crop’s left edge is still OPT-001’s outer-shell control bleeding beside this panel.

## OPT-001 Fuse Bottom-Left Trader Nav With Primary Sidebar

- Source evidence:
  - User statements (2026-07-20): left `交易记录 / 点位管理` feels 格格不入 vs Data/Review; **左下角需要跟上面 UI 融合度更好一些**.
  - Screenshots 1–3 above, especially Review collapsed rail vs trade panel adjacency.
  - Implementation: `frontend/src/components/Layout.jsx` keeps Data/Review/Backtest/Teaching inside `<nav>` as peer items, then renders the trader workspace as a separate footer-ish `<button className="secondary">` with `RefreshCcw` and a role badge. CSS: `.sidebar .secondary { margin-top: auto; background: rgba(166, 83, 42, .9); }`.
- Current friction:
  - **Fusion failure:** bottom-left uses a different material (solid orange CTA) from the transparent icon buttons above.
  - **Collapsed mode:** primary items shrink to icon-only; trader entry remains a wide orange pill/badge and can visually collide with adjacent Review content.
  - **Hierarchy noise:** a first-class workspace looks like an urgent action, not a peer of Data/Review.
  - **Icon semantics:** `RefreshCcw` reads as reload/sync, not trade-record / point management.
- User-confirmed direction (locked for this record):
  - Prefer **peer-nav fusion**: same visual system as the items above (transparent dark rail button, same hover/active, same collapsed icon size/alignment).
  - Do **not** keep the orange filled CTA as the default destination chrome.
  - Role/permission cue may remain, but must not force a different button skin that breaks fusion with the upper stack.
- Desired outcome:
  - Scanning the left rail top-to-bottom feels like one continuous navigation system.
  - Expanded and collapsed states both keep trader workspace as a peer destination.
  - Icon + accessible name communicate trader/point management.
  - Admin vs readonly remains understandable without a foreign orange block.
- Planning resolution (still not authorized for implementation):
  - Move trader workspace into the primary `nav` list (or style the existing control as a true peer if it stays pinned low).
  - Replace `RefreshCcw` with a trader/records-appropriate icon.
  - Drop `.sidebar .secondary` filled orange for this destination; reuse the same button classes as Data/Review.
  - Keep a compact role hint (text, subtle badge, or title/`aria-description`) that does not reintroduce a second skin.
  - Preserve `active` highlighting when `active === 'admin'`.
- Acceptance direction:
  - Side-by-side with Data/Review, the trader entry uses the same geometry, color language, and collapsed behavior.
  - No orange solid destination chrome remains on the default nav path.
  - Active route highlighting works like other destinations.
  - Keyboard/assistive labels remain complete in expanded and collapsed modes.
- Accessibility risk:
  - Collapsed icon-only mode needs a stable accessible name (not only a color badge).
  - Role state must not rely on orange fill alone.
  - Active state should stay programmatic.
- Boundary that must not change:
  - admin-only mutation, readonly inspection, auth/session, route set;
  - no publication, provider/broker, DB schema, or remote action from a nav restyle.
- Lifecycle status: promoted-to-proposed

## OPT-002 Discoverable Path To Add A New Trader

- Source evidence:
  - User statement (2026-07-20): cannot see where to add a new trader.
  - Screenshot: registry section title is `交易者注册表（trader_id 不可变）`; only `tang` / `vordin` rows with Display name / Color / active / Sort order and `保存注册表`.
  - Implementation: `frontend/src/pages/AdminTradersPage.jsx` exposes `updateRegistryTrader` only. There is no add-row control, no blank `trader_id` field, and no “新增交易者” action. Existing ids are rendered as readonly text.
  - Backend already accepts a full registry document via admin PUT (`/api/admin/traders`); the gap is primarily product/UI discoverability and a safe create flow, not necessarily a missing storage model.
  - Page copy says admins can “通过表单新增/编辑点位”, which covers points/groups, not registering a new trader identity.
- Current friction:
  - Admin can edit metadata of known traders but cannot invent a third trader from the UI.
  - The immutable-id wording and edit-only rows make the registry feel closed/frozen.
  - Users looking for “新增交易者” find only point editing and registry field edits.
- Desired outcome:
  - An admin can discover and complete a create-trader flow without editing raw JSON or hand-writing repository files.
  - Creating a trader asks for the required identity/metadata (`trader_id`, display name, color, active, sort order) with validation feedback.
  - After save, the new trader appears in registry and becomes available for subsequent point/group editing on relevant days.
  - Readonly users still cannot mutate the registry.
- Planning resolution:
  - Use an explicit inline **“新增交易者”** row/card in the registry. `trader_id` is user-entered and editable only before first successful save; it must satisfy the existing stable lowercase slug contract.
  - Add the valid entry to the full registry draft, then persist through the existing admin registry PUT and canonical reload. Do not add a dialog dependency or keep creation API-only in v1.
  - A new registry identity does not create fake days, groups, events, or Review availability.
- Acceptance direction:
  - Within the trader workspace, an admin can locate create-trader without leaving the page or opening raw JSON.
  - Invalid ids/duplicates/schema failures surface field-level or form-level errors and do not partially corrupt canonical content.
  - Successful create persists through the existing validated atomic registry path and reloads into the form.
  - Point editing remains distinct from trader registration: adding a trader does not invent fake trade groups.
- Accessibility risk:
  - Create flow needs labeled fields, keyboard reachability, and error focus management.
  - “trader_id 不可变” must not be the only explanation; create vs edit states should be explicit.
- Boundary that must not change:
  - admin-only registry mutation;
  - schema validation, atomic content replacement, candidate DB projection, and rollback coherence;
  - no fabrication of market days or trade points when only a trader identity is added;
  - no commit/push/publication authority from this record.
- Lifecycle status: promoted-to-proposed

## OPT-003 Fuse Review Trade-Filter/List With Upper Review Chrome

- Source evidence:
  - User follow-up (2026-07-20) pointing at the pink-boxed Review crop: **“这部分呢”** — [`./screenshots/2026-07-20-review-trade-filter-panel.png`](./screenshots/2026-07-20-review-trade-filter-panel.png).
  - Full Review context in screenshot 2: above this block sit ticker tabs, month-grouped date rail, strategy select, Ext K/RTH · Rescan · Backtest, and status text in the compact terminal language; below them the filter/list block reads as a different card stack.
  - Implementation: `frontend/src/features/review/TraderFilters.jsx`, `TradeExportControls.jsx`, `TraderTradeList.jsx`; base styles under `.trade-filter-panel` / `.trade-group-card` default to light panel tokens, with Review-only overrides under `.dr-sidebar ...` in `frontend/src/styles.css` (comment: keep shared components readable on dark Review while preserving light Admin defaults).
- Current friction:
  - **Two chrome systems in one Review column:** date rail / strategy use the Daily Review terminal controls; Eligibility / Focus / Download / cards use a generic form-card vocabulary (light select surface, bordered panel, export link row).
  - **Shared-component dark patch, not one design:** Admin keeps light defaults; Review applies partial dark overrides. Selects and some controls can still feel like system form widgets rather than engine/terminal peers.
  - **Adjacency with OPT-001:** the outer orange shell control sits immediately left of this block, amplifying the “foreign chrome” reading even when the panel itself is in-scope.
  - **Not a missing-feature complaint in this crop:** filters, focus, download, and group drilldown are present; the ask is visual/information-architecture fusion with the UI above.
- Desired outcome:
  - From ticker/date/strategy down through trade filters and group cards, the left Review column feels like one continuous Daily Review surface.
  - Controls keep current contracts (availability-driven traders, eligibility modes, export of current selection, group expand/collapse) while matching Review spacing, borders, type, and control chrome.
  - Admin light workspace may keep a distinct light skin if needed, but Review should not look like a bolted-on form.
- Planning resolution:
  - Keep the shared React components and migrate them to one app-wide terminal token set plus an optional compact Review density. Do not create separate light/dark product skins in v1.
  - Do not introduce a structural regroup unless independent review proves token/density fusion insufficient and the plan is revised; availability/export contracts remain fixed.
- Acceptance direction:
  - Screenshot comparison of the full left column shows continuous chrome from ticker tabs through trade cards.
  - Eligibility/Focus/Download remain keyboard operable with visible labels; no reliance on color alone for trader identity.
  - Availability-driven empty state and filter reconciliation behavior stay unchanged unless a separate plan revises them.
  - Static Review, if it reuses the same block, either inherits the fused skin or is explicitly accepted as a documented exception.
- Accessibility risk:
  - Restyling selects/buttons must preserve contrast, focus rings, and name computation.
  - Trader color bars remain supplementary, not the only identity cue.
- Boundary that must not change:
  - availability-driven trader visibility, selection reconciliation, export contents, normalized trade payload contracts;
  - no auth bypass, no data write from Review filters, no publication/provider changes.
- Relationship to OPT-001 / OPT-004:
  - OPT-001 = **outer app shell** destination button fusion.
  - OPT-003 = **inner Review column** trade-panel fusion with the controls above it.
  - OPT-004 = **page-level color system** so Review is not a different product skin from Data/Admin/etc.
  - Fixing only OPT-001 removes the orange bleed; fixing OPT-003 addresses the pink-boxed block; fixing OPT-004 decides the shared palette both of those restyles must join.
- Lifecycle status: promoted-to-proposed

## OPT-004 Unify Review Color System With The Rest Of The App

- Source evidence:
  - User statement (2026-07-20): **Review 界面的颜色和其他页面颜色不同，需要统一.**
  - Screenshots 5–6: expanded shell (warm dark brown rail + cream brand language) beside Review’s full charcoal workbench; Eligibility still renders a light select on dark Review.
  - Implementation dual theme in `frontend/src/styles.css`:
    - **Paper / editorial app skin (default):** `:root` tokens `--paper #f7f1e6`, `--panel #fffaf0`, `--line #dfd1bb`, `--accent #a6532a`, `--ink #181713`; `body` cream gradient; `.metric`/`.panel` warm panels. Used by Data, Admin Traders, Backtest, Teaching content inside `main`.
    - **Review terminal skin:** `.dr-shell { background: #141413; color: #E8E7E3; }` plus a large `.dr-*` token island (sidebar `#1E1E1D`, controls `#282827`, accent olive `#8B9A6D`). `ReviewPage` roots at `className="dr-shell"` and intentionally `margin: -36px` to fill `main`.
  - Outer shell sidebar is a third warm-dark brown (`rgba(31, 29, 24, .94)`), so even “dark next to dark” does not match Review charcoal.
  - Prior Review visual baseline [`../2026-07-19-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png`](../2026-07-19-review-ui-and-trader-editing/screenshots/2026-07-19-review-ui-reference-v1.png) locked a dark compact trading-terminal look for Review workspaces; it did **not** decide that Data/Admin must stay permanently on a separate cream product skin.
- Current friction:
  - Switching Data → Review feels like entering a different application, not another module of the same product.
  - Shared components (filters, export, group cards) need dual skins and still leak light widgets on Review (feeds OPT-003).
  - Nav/brand (warm brown + orange accent) clash with Review olive/charcoal accents and with the orange secondary CTA (feeds OPT-001).
  - No single token set documents “the Tang Strategy UI palette.”
- Desired outcome:
  - One coherent product color language across shell + Data + Review + Backtest + Teaching + Admin, with intentional chart-area darkness if needed for candles, not a second whole-page brand.
  - Page switches keep layout/role differences but stop re-theming the entire chrome family.
- Candidate directions considered:
  | Direction | Meaning | Status |
  | --- | --- | --- |
  | **A. Terminal-first** | Promote Review charcoal/olive (or a refined version) to shell + all pages; K-line stays dark by nature | **User-locked 2026-07-20** |
  | B. Paper-first | Keep cream paper for app pages; restyle Review chrome toward warm paper while keeping chart canvas dark | Rejected for this batch |
  | C. Hybrid shell + dark chart | Shared warm-dark shell; only chart well pure dark | Rejected for this batch |
  | D. Explicit dual theme | Keep two skins | Rejected (conflicts with 需要统一) |

- User-confirmed direction (locked):
  - **A · Terminal-first.** One product skin derived from the Review terminal family (charcoal surfaces, cool neutrals, olive/sage interactive accent — refined into shared tokens), applied to app shell, Data, Review, Backtest, Teaching, and Admin.
  - Data/Admin lose the cream paper editorial look as the default product chrome.
  - Chart/K-line remains high-contrast dark; it is no longer a second brand, only the densest region of the same skin.
  - OPT-001 and OPT-003 must implement **inside this terminal palette** (peer nav, no orange CTA as destination chrome; trade filters match Review controls — no light paper selects).
  - Warm `--accent` orange may remain only as a deliberate semantic/brand mark if mapped into the token set; it must not define a second page skin.
- Acceptance direction:
  - Side-by-side screenshots of Data, Review, Admin, Backtest, Teaching share one recognizable palette family (surfaces, borders, text, accent).
  - Review no longer introduces an unrelated accent (e.g. olive-only vs accent-only) without mapping into the shared tokens.
  - Shared filter/list components need at most one product skin + optional chart-adjacent density, not divergent brand colors.
  - Static Review either inherits the same product tokens or is explicitly listed as a remaining exception with rationale.
- Accessibility risk:
  - Unification must re-check contrast for text, active tabs, focus rings, win/loss, and trader color bars on both chart-dark and panel surfaces.
  - Color alone must not carry ticker, role, or verification state.
- Boundary that must not change:
  - no auth/data/provider/publisher change from a theme pass;
  - K-line engine behavior and review assembly contracts remain;
  - prior dark Review reference informs chart/workbench density but does not by itself authorize leaving the rest of the app on a permanent second brand without an explicit dual-theme decision.
- Lifecycle status: promoted-to-proposed

## Relationship To Earlier Same-Day Draft

An earlier same-day draft ([`2026-07-20-data-coverage-presentation/`](../2026-07-20-data-coverage-presentation/2026-07-20-data-coverage-presentation.md)) explored Data-page market-day coverage density after external FreqUI/Jesse research. User follow-ups with screenshots clarified the intended friction is **nav fusion**, **Review trade-panel fusion**, **app-wide color unification**, and **missing add-trader**, not primarily the month-grouped date rail. That coverage draft is superseded by this batch; coverage remains a possible future intake only if the user re-raises it.

## How The Visual Items Nest

```
OPT-004  page-level color / product skin unification
├── OPT-001  outer shell trader nav peer fusion (no orange CTA)
└── OPT-003  Review trade-filter/list fusion with Review chrome
OPT-002  functional: discoverable add-trader (can ship with or after visual work)
```

## Planning Decisions Captured

1. **OPT-004 remains A terminal-first.** The proposed plan freezes a shared charcoal/neutral/olive token table and keeps warm orange as a brand-only mark unless design review approves one named exception.
2. OPT-001 uses one peer nav model with no orange destination CTA; role capability survives through restrained text/accessibility rather than a second skin.
3. OPT-003 keeps shared components, moves them to the same product tokens, and uses only an optional Review density rather than a second brand palette.
4. OPT-002 uses an inline admin create draft. `trader_id` is user-entered, matches exact `^[a-z][a-z0-9_]{1,63}$`, is never silently generated, and becomes immutable after successful persistence; color matches exact `^#[0-9A-Fa-f]{6}$`, and server errors associate fields only from JSON `detail` or raw error-body paths with a form-level fallback.
5. OPT-001 through OPT-004 are bundled into one plan with separate visual, Review, registry, and integrated-acceptance phases.
6. The created plan remains Proposed and review-only. Exact-v2 design review is approved; activation, implementation start, Git, data, publication, provider/broker, and remote authority remain separate.

## Promotion Boundary

This batch has been promoted by the user's explicit request to [`Tang Strategy Terminal UI Fusion And Trader Registry`](../../exec-plans/proposed/2026-07-20-tang-strategy-terminal-ui-fusion-and-trader-registry-plan.md). The batch layout remains this markdown file plus sibling `screenshots/` under `docs/optimization/2026-07-20-trader-workspace-nav-and-registry/`.

Current path: optimization record → **Proposed v2, design-approved** → explicit activation instruction/recording (next) → separate implementation-start authority. `review-001` targets v1; `review-002` approves exact v2 but does not activate it. No runtime, Git, remote, data, provider/broker, or publication action is authorized by promotion or review approval.
