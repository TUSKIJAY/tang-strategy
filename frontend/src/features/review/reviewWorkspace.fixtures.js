// Phase 0 frozen fixtures for the review workspace / trader-availability contracts.
// Frozen by docs/exec-plans/reviews/2026-07-19-tang-strategy-review-workspaces-and-trader-point-editing-plan/evidence/phase-0-manifest.md
// Pure data only: no DOM, API, SQLite, or repo-file reads. Product helpers under
// test must prove themselves against these constants, not the other way around.

// --- Traders ---------------------------------------------------------------
// Mirrors content/traders/index.json at freeze time (two active traders).
export const FIXTURE_TRADERS = [
  { trader_id: 'tang', display_name: 'Tang', color: '#E45756', active: true, sort_order: 10 },
  { trader_id: 'vordin', display_name: '沃德哥', color: '#4E79A7', active: true, sort_order: 20 },
];

export const FIXTURE_TRADER_REGISTRY = {
  schema_version: 'traders-v1',
  traders: FIXTURE_TRADERS,
};

// --- Asymmetric market-day history ------------------------------------------
// The real freeze-time inventory: 46 SPY days (2026-05-12 … 2026-07-17) and the
// first 3 QQQ days. All sessions are `extended`. Bar counts are intentionally
// not pinned by these fixtures.
export const FIXTURE_SPY_DATES = [
  '2026-05-12', '2026-05-13', '2026-05-14', '2026-05-15', '2026-05-18',
  '2026-05-19', '2026-05-20', '2026-05-21', '2026-05-22', '2026-05-26',
  '2026-05-27', '2026-05-28', '2026-05-29', '2026-06-01', '2026-06-02',
  '2026-06-03', '2026-06-04', '2026-06-05', '2026-06-08', '2026-06-09',
  '2026-06-10', '2026-06-11', '2026-06-12', '2026-06-15', '2026-06-16',
  '2026-06-17', '2026-06-18', '2026-06-22', '2026-06-23', '2026-06-24',
  '2026-06-25', '2026-06-26', '2026-06-29', '2026-06-30', '2026-07-01',
  '2026-07-02', '2026-07-06', '2026-07-07', '2026-07-08', '2026-07-09',
  '2026-07-10', '2026-07-13', '2026-07-14', '2026-07-15', '2026-07-16',
  '2026-07-17',
];

export const FIXTURE_QQQ_DATES = ['2026-07-10', '2026-07-14', '2026-07-17'];

// Newest-first, ticker ascending inside one date — the observed API/manifest order.
export function orderDaysNewestFirst(entries) {
  return [...entries].sort((a, b) => {
    if (a.trade_date !== b.trade_date) return a.trade_date < b.trade_date ? 1 : -1;
    return a.ticker < b.ticker ? -1 : 1;
  });
}

const ALL_DAY_REFS = orderDaysNewestFirst([
  ...FIXTURE_SPY_DATES.map((trade_date) => ({ ticker: 'SPY', trade_date })),
  ...FIXTURE_QQQ_DATES.map((trade_date) => ({ ticker: 'QQQ', trade_date })),
]);

// Interactive `/api/market-days` item shape (bar counts intentionally zero).
export const FIXTURE_MARKET_DAYS = ALL_DAY_REFS.map((ref, index) => ({
  id: index + 1,
  ticker: ref.ticker,
  trade_date: ref.trade_date,
  session_mode: 'extended',
  source: 'live_extended',
  title: `${ref.ticker} ${ref.trade_date} extended`,
  bar_count_1m: 0,
  bar_count_5m: 0,
}));

export function fixtureDaySlug(ticker, tradeDate, sessionMode = 'extended') {
  return `${ticker.toLowerCase()}-${tradeDate}-${sessionMode}`;
}

// Static manifest `reviews[]` entry shape (export_static_reviews.py:183-201).
export const FIXTURE_STATIC_MANIFEST_REVIEWS = ALL_DAY_REFS.map((ref) => {
  const slug = fixtureDaySlug(ref.ticker, ref.trade_date);
  return {
    slug,
    file: `days/${slug}.json`,
    ticker: ref.ticker,
    trade_date: ref.trade_date,
    session_mode: 'extended',
    title: `${ref.ticker} ${ref.trade_date} extended`,
    bars_1m: 0,
    bars_5m: 0,
  };
});

// --- Trade-record payloads (public projection shape, minimal pinned subset) --
// Only the fields the availability/filter contracts consume are pinned:
// group identity, trader, underlying, status, review_status, display_eligible,
// direction, plus the traders list and counts.

function publicGroup(overrides) {
  return {
    trade_group_id: overrides.trade_group_id,
    trader_id: overrides.trader_id,
    underlying: overrides.underlying,
    trade_date: overrides.trade_date,
    direction: overrides.direction,
    status: overrides.status ?? 'active',
    review_status: overrides.review_status ?? 'verified',
    display_eligible: overrides.display_eligible ?? true,
    reported_stats_eligible: overrides.reported_stats_eligible ?? false,
    calculated_stats_eligible: overrides.calculated_stats_eligible ?? false,
    normalization_method: overrides.normalization_method ?? 'manual_normalization',
  };
}

function publicPayload({ ticker, tradeDate, traders, groups, contexts = [] }) {
  return {
    schema_version: 'trade-records-v1',
    ticker,
    trade_date: tradeDate,
    traders,
    trade_groups: groups,
    note_contexts: contexts,
    counts: {
      trade_groups: groups.length,
      note_contexts: contexts.length,
    },
    export_metadata: { raw_evidence_included: false, includes_bars: false },
  };
}

const TANG = FIXTURE_TRADERS[0];
const VORDIN = FIXTURE_TRADERS[1];

export const FIXTURE_TRADE_PAYLOADS = {
  // SPY 2026-07-17: one verified tang group.
  'spy-2026-07-17': publicPayload({
    ticker: 'SPY',
    tradeDate: '2026-07-17',
    traders: [TANG],
    groups: [
      publicGroup({
        trade_group_id: 'tg_20260717_tang_spy_001',
        trader_id: 'tang',
        underlying: 'SPY',
        trade_date: '2026-07-17',
        direction: 'CALL',
        normalization_method: 'legacy_preserve',
      }),
    ],
  }),
  // QQQ 2026-07-17: two verified vordin groups.
  'qqq-2026-07-17': publicPayload({
    ticker: 'QQQ',
    tradeDate: '2026-07-17',
    traders: [VORDIN],
    groups: [
      publicGroup({
        trade_group_id: 'tg_20260717_vordin_qqq_001',
        trader_id: 'vordin',
        underlying: 'QQQ',
        trade_date: '2026-07-17',
        direction: 'PUT',
      }),
      publicGroup({
        trade_group_id: 'tg_20260717_vordin_qqq_002',
        trader_id: 'vordin',
        underlying: 'QQQ',
        trade_date: '2026-07-17',
        direction: 'CALL',
      }),
    ],
  }),
  // QQQ 2026-07-14 interactive: two PENDING vordin groups (not displayable by
  // default eligibility; static export excludes them entirely).
  'qqq-2026-07-14': publicPayload({
    ticker: 'QQQ',
    tradeDate: '2026-07-14',
    traders: [VORDIN],
    groups: [
      publicGroup({
        trade_group_id: 'tg_20260714_vordin_qqq_001',
        trader_id: 'vordin',
        underlying: 'QQQ',
        trade_date: '2026-07-14',
        direction: 'PUT',
        review_status: 'pending',
      }),
      publicGroup({
        trade_group_id: 'tg_20260714_vordin_qqq_002',
        trader_id: 'vordin',
        underlying: 'QQQ',
        trade_date: '2026-07-14',
        direction: 'CALL',
        review_status: 'pending',
      }),
    ],
  }),
  // SPY 2026-05-29: real day with zero trade groups (one tang note context) —
  // the "no visible trader" case; controls must render a neutral empty state.
  'spy-2026-05-29': publicPayload({
    ticker: 'SPY',
    tradeDate: '2026-05-29',
    traders: [TANG],
    groups: [],
    contexts: [
      {
        context_id: 'ctx_20260529_tang_spy_001',
        trader_id: 'tang',
        underlying: 'SPY',
        trade_date: '2026-05-29',
        status: 'active',
        review_status: 'verified',
        normalization_method: 'legacy_preserve',
      },
    ],
  }),
  // Static view of QQQ 2026-07-14: verified-only export leaves zero groups.
  'qqq-2026-07-14-static': publicPayload({
    ticker: 'QQQ',
    tradeDate: '2026-07-14',
    traders: [VORDIN],
    groups: [],
  }),
};

// --- Multi-ticker canonical day preservation case ---------------------------
// Compact but schema-faithful `trades-day-v1` document mirroring the real
// content/trades/2026-07-17.json two-ticker/two-trader/three-group shape.

function fixtureEvent(overrides) {
  return {
    event_id: overrides.event_id,
    sequence: overrides.sequence,
    action: overrides.action,
    occurred_at: overrides.occurred_at,
    time_precision: overrides.time_precision ?? 'minute',
    time_incomplete: overrides.time_incomplete ?? false,
    premium: overrides.premium ?? null,
    quantity: overrides.quantity ?? null,
    fees: overrides.fees ?? null,
    note: overrides.note ?? null,
    fact_provenance: overrides.fact_provenance ?? {
      occurred_at: 'user_provided',
      premium: 'user_provided',
      quantity: 'user_provided',
      fees: 'unknown',
    },
  };
}

function fixtureGroup(overrides) {
  return {
    trade_group_id: overrides.trade_group_id,
    trader_id: overrides.trader_id,
    underlying: overrides.underlying,
    trade_date: '2026-07-17',
    direction: overrides.direction,
    status: 'active',
    review_status: 'verified',
    display_eligible: true,
    reported_stats_eligible: false,
    calculated_stats_eligible: false,
    supersedes_trade_group_id: null,
    legs: [
      {
        leg_id: `${overrides.trade_group_id}_l1`,
        instrument_type: 'option',
        position_side: 'long',
        option_type: overrides.direction,
        strike: overrides.strike ?? null,
        expiry: '2026-07-17',
        expiry_provenance: 'rule_default',
        contract_multiplier: 100,
        contract_multiplier_provenance: 'rule_default',
        events: overrides.events,
      },
    ],
    reported_outcome: overrides.reported_outcome ?? null,
    calculated_outcome: null,
    result_conflict: false,
    notes: overrides.notes ?? [],
    normalization: overrides.normalization ?? {
      method: 'manual_normalization',
      source: 'chat_screenshot',
      source_path: 'records/2026/2026-07-17-day03/record.md',
      source_index: null,
      review_flags: [],
    },
  };
}

export const FIXTURE_MULTI_TICKER_DAY = {
  schema_version: 'trades-day-v1',
  trade_date: '2026-07-17',
  timezone: 'America/New_York',
  trade_groups: [
    fixtureGroup({
      trade_group_id: 'tg_20260717_tang_spy_001',
      trader_id: 'tang',
      underlying: 'SPY',
      direction: 'CALL',
      events: [
        fixtureEvent({
          event_id: 'tg_20260717_tang_spy_001_l1_e1',
          sequence: 1,
          action: 'buy_open',
          occurred_at: '2026-07-17T11:27-04:00',
          fact_provenance: {
            occurred_at: 'legacy_preserved',
            premium: 'unknown',
            quantity: 'unknown',
            fees: 'unknown',
          },
        }),
      ],
      notes: [{ text: '11:27 call；未提供具体 strike。', provenance: 'legacy_preserved' }],
      normalization: {
        method: 'legacy_preserve',
        source: 'manual_note',
        source_path: 'content/trader-trades/2026-07-17.json',
        source_index: 0,
        review_flags: [],
      },
    }),
    fixtureGroup({
      trade_group_id: 'tg_20260717_vordin_qqq_001',
      trader_id: 'vordin',
      underlying: 'QQQ',
      direction: 'PUT',
      strike: 681,
      events: [
        fixtureEvent({
          event_id: 'tg_20260717_vordin_qqq_001_l1_e1',
          sequence: 1,
          action: 'buy_open',
          occurred_at: '2026-07-17T09:42-04:00',
          premium: 0.84,
          quantity: 150,
        }),
        fixtureEvent({
          event_id: 'tg_20260717_vordin_qqq_001_l1_e2',
          sequence: 2,
          action: 'sell_close',
          occurred_at: '2026-07-17T10:43-04:00',
          premium: 0.15,
          quantity: null,
          fact_provenance: {
            occurred_at: 'user_provided',
            premium: 'user_provided',
            quantity: 'unknown',
            fees: 'unknown',
          },
        }),
      ],
      normalization: {
        method: 'manual_normalization',
        source: 'chat_screenshot',
        source_path: 'records/2026/2026-07-17-day03/record.md',
        source_index: null,
        review_flags: ['message_time_not_fill_time', 'missing_close_quantity'],
      },
    }),
    fixtureGroup({
      trade_group_id: 'tg_20260717_vordin_qqq_002',
      trader_id: 'vordin',
      underlying: 'QQQ',
      direction: 'CALL',
      strike: 691,
      events: [
        fixtureEvent({
          event_id: 'tg_20260717_vordin_qqq_002_l1_e1',
          sequence: 1,
          action: 'buy_open',
          occurred_at: '2026-07-17T09:42-04:00',
          premium: 1.8,
          quantity: 70,
        }),
        fixtureEvent({
          event_id: 'tg_20260717_vordin_qqq_002_l1_e2',
          sequence: 2,
          action: 'sell_close',
          occurred_at: '2026-07-17T10:01-04:00',
          premium: 5.5,
          quantity: null,
          fact_provenance: {
            occurred_at: 'user_provided',
            premium: 'user_provided',
            quantity: 'unknown',
            fees: 'unknown',
          },
        }),
      ],
      reported_outcome: {
        return_pct: null,
        gross_pnl: null,
        net_pnl: 13760,
        provenance: 'user_provided',
        note: '10:05 EDT 用户口述 call 侧盈利。',
      },
    }),
  ],
  note_contexts: [
    {
      context_id: 'ctx_20260717_vordin_qqq_001',
      trader_id: 'vordin',
      underlying: 'QQQ',
      trade_date: '2026-07-17',
      text: '10:05 EDT Call 侧盈利 $13,760、Put 侧成本 $12,600。',
      status: 'active',
      review_status: 'verified',
      normalization: {
        method: 'manual_normalization',
        source: 'chat_screenshot',
        source_path: 'records/2026/2026-07-17-day03/record.md',
        source_index: null,
        review_flags: [],
      },
    },
  ],
};

// A scoped edit to tg_20260717_vordin_qqq_001 must preserve every other record.
export const FIXTURE_PRESERVATION_CASE = {
  document: FIXTURE_MULTI_TICKER_DAY,
  scopedEditTargetGroupId: 'tg_20260717_vordin_qqq_001',
  expectedUntouchedGroupIds: ['tg_20260717_tang_spy_001', 'tg_20260717_vordin_qqq_002'],
  expectedUntouchedLegIds: ['tg_20260717_tang_spy_001_l1', 'tg_20260717_vordin_qqq_002_l1'],
  expectedUntouchedEventIds: [
    'tg_20260717_tang_spy_001_l1_e1',
    'tg_20260717_vordin_qqq_002_l1_e1',
    'tg_20260717_vordin_qqq_002_l1_e2',
  ],
  expectedUntouchedContextIds: ['ctx_20260717_vordin_qqq_001'],
  expectedCounts: { trade_groups: 3, legs: 3, events: 5, note_contexts: 1 },
};

// --- Hash cases ---------------------------------------------------------------
export const FIXTURE_HASH_CASES = {
  valid: [
    { hash: '#spy-2026-07-17-extended', ticker: 'SPY', trade_date: '2026-07-17', session_mode: 'extended' },
    { hash: '#qqq-2026-07-17-extended', ticker: 'QQQ', trade_date: '2026-07-17', session_mode: 'extended' },
    { hash: '#qqq-2026-07-10-extended', ticker: 'QQQ', trade_date: '2026-07-10', session_mode: 'extended' },
  ],
  invalid: [
    // Unknown day: must resolve deterministically to a valid local item and report the resolution.
    { hash: '#spy-1999-01-01-extended', reason: 'unknown-day' },
    // Malformed: no session segment / not a real slug shape.
    { hash: '#qqq-2026-07-11', reason: 'malformed' },
    // Case-sensitive slug mismatch (manifest slugs are lowercase).
    { hash: '#SPY-2026-07-17-EXTENDED', reason: 'case-mismatch' },
    // Empty hash: default selection path.
    { hash: '', reason: 'empty' },
  ],
};

// --- Layout fixtures -----------------------------------------------------------
export const FIXTURE_VIEWPORTS = {
  referenceDesktop: { width: 1672, height: 941 },
  narrow: { width: 820, height: 900 },
  collapsedSidebar: { collapsed: true },
};
