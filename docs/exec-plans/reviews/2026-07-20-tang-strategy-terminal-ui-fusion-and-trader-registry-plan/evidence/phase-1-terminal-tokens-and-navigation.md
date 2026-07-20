# Phase 1 — Terminal Tokens And Peer Navigation Evidence

- Plan revision: `v2-review-foldback-2026-07-20`
- Phase disposition: `complete`
- Implementation authority: `user-instruction:2026-07-20-execute-terminal-ui-registry-plan`
- Remote/data/publication authority: `none`

## Implemented Scope

- Installed the exact fifteen-token terminal product-chrome contract at `:root`.
- Migrated body, shared controls, Login, shell, metrics, panels, rows, generic feedback, and shared form defaults away from the legacy paper variables.
- Replaced the special orange trader-workspace CTA with the same `NavItem` renderer and `.nav-item` state contract used by Data, Review, Backtest, and Teaching.
- Kept the trader workspace bottom-pinned through `.nav-bottom-stack { margin-top: auto; }`; Logout remains a separate muted utility action.
- Replaced refresh semantics with `UsersRound`, added `aria-current="page"`, and retained complete capability text in `aria-label`/`title` while hiding only visible metadata in collapsed mode.
- Restricted `var(--brand-warm)` to the `TS` brand mark; chart, signal, and trader colors remain domain-owned.

## Source Contracts

`npm run test:trade-records` passed `39/39`. The added contracts assert:

- every exact token/value pair;
- removal of legacy `--ink`, `--muted`, `--paper`, `--panel`, and `--line` declarations and cream chrome values;
- exactly one `var(--brand-warm)` consumer at `.brand-mark`;
- one shared nav renderer, five peer route identities, bottom placement, `UsersRound`, programmatic current state, stable capability text, and absence of `RefreshCcw`/`.secondary` semantics;
- terminal surfaces for the existing point-picker and missing-day controls.

Normal and static Vite builds both passed with 1,754 modules transformed.

## Browser Matrix

Playwright CLI exercised the live authenticated app at `1672x941` and `820x1180`. Eight screenshots were written outside the Git worktree under:

`C:\Users\LENOVO\.codex\visualizations\2026\07\20\019f7e98-6c47-76f1-829e-7c1764c47f9c\terminal-ui-registry-phase1-20260720`

| Surface | Viewport | Nav | SHA-256 |
| --- | --- | --- | --- |
| Data | desktop | expanded | `5D8A2869315AE0ACCECC0FFD0F8A410792F3D847D33DBE14E8933D68FCD64EF2` |
| Data | desktop | collapsed | `9E6B3352EB51C4E6CF86A509A7621D15FF9C5D508D62E182076BCE3E5E724FB6` |
| Data | narrow | expanded | `5C1E3F2602523F6A38EA020A5987A78B26DDD141E2690742851E33409D736C4B` |
| Data | narrow | collapsed | `CC5B8E2DBC055BAFE7E89DD379FDBC80DECB9E48A46E8443490E7FFED94A15AC` |
| Admin | desktop | expanded | `68C86A3E1039F33B4B027F5006B729C37755EAB687F47F83E0C2060E72E8B54D` |
| Admin | desktop | collapsed | `75DA54EE7B9B9C955633C9680BCBDA4313797E74F4D63E264E707CDBD76770EB` |
| Admin | narrow | expanded | `37F6CA7DFAAF48DEA89C5ACB23FBDE716EC67C5FA27DCD29309599188E26BEBA` |
| Admin | narrow | collapsed | `44DD5DC0C55D8EAA3057FE5FAC9D2E2EFD8168B89505FF9227EA4B076CB8BE0D` |

Computed-style probes returned all fifteen frozen values exactly. Body and sidebar resolved to `rgb(20, 20, 19)` and `rgb(30, 30, 29)`. Data and Admin exposed the correct current accessible name in expanded and collapsed modes. The sidebar had zero horizontal overflow in every shell state. Data had zero main/document overflow at narrow width. One real keyboard `Tab` moved focus to Data and produced a solid `2px rgb(139, 154, 109)` focus outline.

The only console error was the pre-existing missing `/favicon.ico` request. Admin editor internals still showed white native controls and `696px` main scroll overflow at narrow width; both are explicitly carried into Phase 2 page-level migration and are not classified as Phase 1 shell failures.

## Repository Verification

- `python scripts/check-project-harness.py --root . --profile auto`: pass.
- `python scripts/check-operating-modes.py --root .`: pass.
- `git diff --check`: pass.
- Stale product-chrome scan: no runtime matches for legacy variables, named cream colors, `RefreshCcw`, or `className="secondary"`; only negative test literals remain.
- No backend, API client, schema, content, DB, route, publisher, exporter, K-line, or excluded page-component path changed.

Phase 1 exits complete. Phase 2 owns remaining page-specific controls, feedback states, and narrow Admin editor overflow.
