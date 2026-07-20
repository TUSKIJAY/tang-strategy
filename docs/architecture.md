# Tang Strategy Architecture

## Runtime Modes

Tang Strategy has one data source of truth and two delivery modes:

- interactive: FastAPI reads the tracked SQLite DB; authenticated React pages call the API;
- static Pages: CI reads the same DB, exports JSON, builds `StaticReviewsApp`, and publishes the Vite output to `gh-pages`.

The shared runtime input is `data/sqlite/tang_strategy_live_extended.db`. The accepted local seed shape is `data/seed/market-data/live_extended/<date>/<ticker>_<date>.json`.

## Daily Data And DB Flow

1. `update_spy_qqq_market_day.py` invokes the tracked one-symbol adapters into temporary staging, using TradingView first.
2. Both tickers must pass the same NYSE/session/OHLCV/RTH/5m/VWAP and same-provider gates; otherwise accepted seeds and DB remain on the prior pair.
3. The orchestrator imports both payloads and the canonical trade repository into one candidate, verifies preservation/integrity/drift, then atomically promotes and replaces the accepted seed pair.
4. If TV retries or a named hard gate fail, the operator may separately start IB Gateway and rerun the complete pair with `--provider ibkr`; one accepted pair never mixes providers.
5. The tracked DB carries logical market days, provider datasets, bars, strategies, teaching assets, and normalized trade projections into runtime and Pages export. Canonical source remains under `content/traders` and `content/trades`.

Rebuild never deletes the current DB before candidate validation. Default replacement requires the candidate market-day set to be a superset of the current set; the daily workflow never uses the intentional date-loss override.

## Interactive API Flow

- login: `POST /api/auth/login`;
- discovery: `GET /api/tickers`, `/api/market-days`, `/api/strategies`;
- bars: `GET /api/market-days/{market_day_id}/bars?timeframe=1m|5m`;
- assembled review: `GET /api/reviews/assemble?market_day_id=<id>&strategy_id=<id>`;
- normalized trade reads: `GET /api/trade-records`;
- admin canonical reads: `GET /api/admin/traders` and `GET /api/admin/trade-records?trade_date=<date>`;
- teaching assets: `GET /api/teaching/{asset_type}`;
- controlled writes: atomic admin trader/day endpoints plus the existing import endpoints.

Readonly/admin endpoints use bearer auth. The public trade-record response is a ticker/date projection for inspection and export; it is intentionally not a canonical write base. Admin canonical reads return the write-valid registry or complete multi-ticker day document without reading the runtime DB. Admin canonical writes remain validation-, candidate-, drift-, and rollback-protected; there is no unrestricted rebuild endpoint.

## Static Pages Flow

`.github/workflows/publish-static-reviews.yml` runs only for its configured `main` push/manual trigger:

1. checkout the tracked DB;
2. run `export_static_reviews.py` into `frontend/public/reviews`;
3. build with `VITE_STATIC_REVIEWS=true` into `frontend/dist`;
4. replace the remote `gh-pages` branch with that build.

The current static format is a Vite SPA plus generated review/strategy JSON. `StaticReviewsApp` consumes the existing flat manifest client-side through the same pure ticker/date workspace contract as interactive Review. Canonical deep links remain `#<ticker>-<date>-<session>`; legacy `#/` hashes resolve to the same real manifest item, and invalid links fall back deterministically with an announcement. Static Review never exposes login, Admin reads, editing, Backtest, Teaching, or mutation actions. It is not the retired collection of standalone per-day HTML under `docs/`.

## Frontend Modules

- `styles.css` owns the shared terminal-first product chrome through one 15-token root contract: charcoal app/panel/control/raised surfaces, neutral borders/text, olive interactive accent, explicit status colors, and one warm brand-only mark. Login, shell, Data, Review, Backtest, Teaching, Admin, and Static Review consume this contract; chart/signal/trader colors remain domain-owned. Review may change density, but it must not introduce a second product palette.
- `Layout` renders Data, Review, Backtest, Teaching, and the bottom-pinned trader workspace through one peer navigation contract. Expanded/collapsed geometry, hover/active state, `aria-current`, keyboard behavior, and accessible naming are shared; admin/readonly capability is metadata, not a separate CTA skin.
- `reviewWorkspace.js` owns pure interactive/static day normalization, ticker/date grouping, hash resolution, and deterministic transitions. `ReviewContextPanel` renders the shared ticker tabs and ticker-scoped date rail; child filters may mirror but never override that resolved context.
- Data/Dashboard loads tickers, days, strategies, and admin import controls. Its day selection reconciles Review to the same real ticker/day rather than a mixed flat list.
- Review requests one assembled payload, runs browser scanner/lifecycle rendering, derives visible traders from displayable groups before selection, and reconciles stale selected/focused traders after every context/filter change.
- The authenticated `交易记录 / 点位管理` workspace is one navigation action away for both roles. Readonly users inspect/export the public projection. Admin users load the canonical registry and complete day, edit a scoped group/event through `TraderPointEditor`, preview the complete candidate in one reused chart, and explicitly save through the existing atomic PUT. `traderRegistry.js` owns pure create-draft normalization/validation, append preservation, unsaved removal, and recognized server-error association for the registry form.
- Static Review shares workspace, availability, reconciliation, presentation, and engine-ownership rules while retaining the static capability boundary described above.
- Backtest loads bars for recent days, runs the browser-side backtest, and renders results through the shared engine.
- Teaching loads structured content and uses the same chart/replay surface.
- `frontend/src/kline/` owns the shared chart engine; new consumers must not create a page-specific replacement.

## Review State And Control Ownership

Ticker/date is one parent workspace identity. A real explicit selection or static hash wins; otherwise the newest SPY day is preferred when SPY exists. Switching ticker retains the date only when the target ticker owns it, otherwise it selects that ticker's newest real day. No layer fabricates a missing ticker/date.

Review/Data/Static own business context: ticker/date, strategy, session window, trader availability/focus, eligibility, Rescan, Backtest navigation, export, edit entry, and assembly status. The K-line engine alone renders chart-generic timeframe, replay, speed, zoom, follow, Overview/fit, indicators, candle rendering, and theme controls. Backtest run/result selection and Teaching cutoff/reveal remain page-specific business actions.

Trade mutation is full-document and fail-closed. The editor starts from the complete canonical date document, applies one scoped group edit, verifies every untouched group/leg/event/outcome/context and the intended count delta, then sends the complete day. Timestamp fields are an atomic tuple: known `occurred_at` requires a precision, `time_incomplete=false`, and appropriate provenance; clearing it restores the unknown-time tuple. Client validation blocks known contradictions, while backend validation remains authoritative and failures retain unsaved state.

Registry mutation follows the same full-document boundary. A new admin-only trader starts as an explicit unsaved row with user-entered immutable identity, display name, exact `#RRGGBB` color, active state, and unique non-negative integer order. The client accepts only `^[a-z][a-z0-9_]{1,63}$`, never silently rewrites identity/color, never renumbers persisted rows, and appends without dropping existing values. The existing registry PUT remains authoritative; failures retain the complete draft, recognized server paths bind only to rendered controls, and success clears create state only after canonical reload. A registry-only trader does not fabricate a market day, group, leg, event, outcome, context, or Review/Static availability option.

## Ownership Boundaries

- strategy JSON: `strategies/json`; canonical intent guide: `strategies/STRATEGY.md`;
- teaching/rules/cases/trades: `content/`;
- product direction: `docs/roadmap.md`;
- governed execution: `docs/exec-plans/`;
- generated JSON/build: `frontend/public/reviews` and `frontend/dist`;
- publication: `gh-pages`, never `docs/`.
