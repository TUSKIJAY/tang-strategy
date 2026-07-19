import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import {
  buildTradeAvailability,
  buildTradeRecordAnnotations,
  buildTradeRecordDownloads,
  canEditTradeRecords,
  exportSelectionFromFilters,
  filterTradeGroups,
  flattenTradeRecords,
  initialTradeRecordFilters,
  resolveTradeDate,
  reviewHashRoute,
  summarizeTradeGroups,
} from './tradeRecords.js';

const traders = [
  { trader_id: 'alice', display_name: 'Alice', color: '#3366CC', active: true, sort_order: 10 },
  { trader_id: 'bob', display_name: 'Bob', color: '#DC3912', active: true, sort_order: 20 },
  { trader_id: 'retired', display_name: 'Retired', color: '#999999', active: false, sort_order: 30 },
];

function event(eventId, sequence, occurredAt, action = 'buy_open') {
  return {
    event_id: eventId,
    sequence,
    action,
    occurred_at: occurredAt,
    time_precision: 'minute',
    time_incomplete: false,
    premium: 1,
    quantity: 1,
    fees: null,
    note: null,
    fact_provenance: { occurred_at: 'user_provided' },
  };
}

function group({ id, traderId, direction, reported = null, calculated = null, events = [] }) {
  return {
    trade_group_id: id,
    trader_id: traderId,
    underlying: 'SPY',
    trade_date: '2026-07-17',
    direction,
    status: 'active',
    review_status: 'verified',
    display_eligible: true,
    reported_stats_eligible: reported != null,
    calculated_stats_eligible: calculated != null,
    supersedes_trade_group_id: null,
    legs: [{
      leg_id: `${id}_l1`,
      instrument_type: 'option',
      position_side: 'long',
      option_type: direction,
      strike: 600,
      expiry: '2026-07-17',
      expiry_provenance: 'user_provided',
      contract_multiplier: 100,
      contract_multiplier_provenance: 'rule_default',
      events,
    }],
    reported_outcome: reported == null ? null : { return_pct: reported, gross_pnl: null, net_pnl: null },
    calculated_outcome: calculated == null ? null : {
      return_pct: calculated,
      gross_pnl: calculated,
      net_pnl: null,
    },
    result_conflict: reported != null && calculated != null && reported !== calculated,
    notes: [],
    normalization_method: 'manual_normalization',
  };
}

const groups = [
  group({
    id: 'tg_20260717_alice_spy_001',
    traderId: 'alice',
    direction: 'CALL',
    reported: 25,
    events: [
      event('tg_20260717_alice_spy_001_l1_e1', 1, '2026-07-17T10:00:00-04:00'),
      event('tg_20260717_alice_spy_001_l1_e2', 2, '2026-07-17T10:00:00-04:00', 'buy_add'),
    ],
  }),
  group({
    id: 'tg_20260717_bob_spy_001',
    traderId: 'bob',
    direction: 'PUT',
    calculated: -10,
    events: [event('tg_20260717_bob_spy_001_l1_e1', 1, '2026-07-17T10:01:00-04:00')],
  }),
];

const payload = {
  schema_version: 'trade-records-v1',
  ticker: 'SPY',
  trade_date: '2026-07-17',
  traders,
  trade_groups: groups,
  note_contexts: [],
  counts: {
    trade_groups_total: 2,
    display_eligible_groups: 2,
    reported_stats_eligible_groups: 1,
    calculated_stats_eligible_groups: 1,
    note_contexts_total: 0,
  },
  export_metadata: {
    selection: {
      ticker: 'SPY',
      trade_date: '2026-07-17',
      trader_ids: [],
      statuses: ['active'],
      review_statuses: ['verified'],
      display_only: false,
    },
    json_filename: 'trade_records_spy_2026-07-17.json',
    csv_filenames: ['trade_groups.csv', 'trade_legs.csv', 'trade_events.csv'],
    includes_bars: false,
    raw_evidence_included: false,
  },
};

test('reload defaults select all active traders without persisted filter state', () => {
  const first = initialTradeRecordFilters(traders);
  first.traderIds.pop();
  const reloaded = initialTradeRecordFilters(traders);
  assert.deepEqual(reloaded.traderIds, ['alice', 'bob']);
  assert.equal(reloaded.focusedTraderId, '');
  assert.equal(reloaded.ticker, 'SPY');
});

test('admin workspace hydrates async trader payloads once without overwriting later edits', () => {
  const source = readFileSync(new URL('../../pages/AdminTradersPage.jsx', import.meta.url), 'utf8');
  assert.match(source, /useEffect\(\(\) => \{/);
  assert.match(source, /initializedFromPayloads\.current \|\| !traders\.length/);
  assert.match(source, /setFilters\(initialTradeRecordFilters\(traders\)\)/);
  assert.match(source, /setRegistryText\(JSON\.stringify\(\{ schema_version: 'traders-v1', traders \}/);
});

test('only admin role can enable frozen-contract editors', () => {
  assert.equal(canEditTradeRecords('admin'), true);
  assert.equal(canEditTradeRecords('readonly'), false);
  assert.equal(canEditTradeRecords('anonymous'), false);
});

test('asymmetric ticker history controls date availability and preserves hash routes', () => {
  const availability = buildTradeAvailability([
    payload,
    { ...payload, trade_date: '2026-07-16' },
    { ...payload, ticker: 'QQQ', trade_date: '2026-07-17' },
  ]);
  assert.deepEqual(availability, {
    SPY: ['2026-07-16', '2026-07-17'],
    QQQ: ['2026-07-17'],
  });
  assert.equal(resolveTradeDate(availability, 'SPY', '2026-07-17'), '2026-07-17');
  assert.equal(resolveTradeDate(availability, 'QQQ', '2026-07-16'), '2026-07-17');
  assert.equal(reviewHashRoute('SPY', '2026-07-17', 'extended'), '#spy-2026-07-17-extended');
  assert.equal(reviewHashRoute('QQQ', '2026-07-17', 'extended'), '#qqq-2026-07-17-extended');
});

test('multi-select, focus, status, review, and eligibility filter at group level', () => {
  const selected = filterTradeGroups(payload, {
    ticker: 'SPY',
    tradeDate: '2026-07-17',
    traderIds: ['alice', 'bob'],
    focusedTraderId: 'alice',
    statuses: ['active'],
    reviewStatuses: ['verified'],
    eligibility: 'reported',
  });
  assert.deepEqual(selected.map((item) => item.trade_group_id), ['tg_20260717_alice_spy_001']);
  assert.deepEqual(filterTradeGroups(payload, { traderIds: [] }), []);
});

test('group-first statistics never blend reported and calculated series', () => {
  const summary = summarizeTradeGroups(groups);
  assert.equal(summary.group_count, 2);
  assert.deepEqual(summary.reported, {
    groups: 1,
    wins: 1,
    losses: 0,
    win_rate: 1,
    average_return_pct: 25,
  });
  assert.deepEqual(summary.calculated, {
    groups: 1,
    wins: 0,
    losses: 1,
    win_rate: 0,
    average_return_pct: -10,
  });
});

test('marker color is trader-owned while CALL and PUT shapes stay independent', () => {
  const bars = [{ t: '10:00' }, { t: '10:01' }];
  const markers = buildTradeRecordAnnotations(groups, traders, bars);
  assert.equal(markers.length, 2);
  assert.equal(markers[0].marker_color, '#3366CC');
  assert.equal(markers[0].marker_shape, 'triangle_up');
  assert.equal(markers[0].grouped_marker_count, 2);
  assert.equal(markers[0].marker_label, 'alice CALL ×2');
  assert.deepEqual(markers[0].event_ids, [
    'tg_20260717_alice_spy_001_l1_e1',
    'tg_20260717_alice_spy_001_l1_e2',
  ]);
  assert.equal(markers[1].marker_color, '#DC3912');
  assert.equal(markers[1].marker_shape, 'triangle_down');
});

test('kline renderer exposes only normalized trade color and shape hooks', () => {
  const source = readFileSync(new URL('../../kline/kline-engine.js', import.meta.url), 'utf8');
  assert.doesNotMatch(source, /anno\.type === 'tang_trade'/);
  assert.match(source, /anno\.type === 'trade_record'/);
  assert.match(source, /anno\.marker_shape/);
  assert.match(source, /_annoColor\(anno\.style, anno\.marker_color\)/);
});

test('JSON and three CSV downloads reconcile group, leg, and event keys', () => {
  const downloads = buildTradeRecordDownloads(payload, groups);
  assert.deepEqual(Object.keys(downloads).sort(), [
    'trade_events.csv',
    'trade_groups.csv',
    'trade_legs.csv',
    'trade_records_spy_2026-07-17.json',
  ]);
  const flat = flattenTradeRecords(groups);
  assert.equal(downloads['trade_groups.csv'].trim().split('\n').length - 1, groups.length);
  assert.equal(downloads['trade_legs.csv'].trim().split('\n').length - 1, flat.legs.length);
  assert.equal(downloads['trade_events.csv'].trim().split('\n').length - 1, flat.events.length);
  flat.legs.forEach((leg) => assert.ok(downloads['trade_groups.csv'].includes(leg.trade_group_id)));
  flat.events.forEach((item) => assert.ok(downloads['trade_legs.csv'].includes(item.leg_id)));
});

test('downloads fail closed on private or raw evidence fields', () => {
  assert.throws(
    () => buildTradeRecordDownloads({ ...payload, raw_evidence: 'forbidden' }, groups),
    /forbidden/,
  );
  const privateGroup = { ...groups[0], source_path: '/private/source' };
  assert.throws(() => buildTradeRecordDownloads(payload, [privateGroup]), /forbidden/);
});

test('downloads synchronize current filters, groups, contexts, counts, and selection metadata', () => {
  const contexts = traders.slice(0, 2).map((trader) => ({
    context_id: `ctx_20260717_${trader.trader_id}_spy_001`,
    trader_id: trader.trader_id,
    underlying: 'SPY',
    trade_date: '2026-07-17',
    text: `${trader.display_name} context`,
    status: 'active',
    review_status: 'verified',
    normalization_method: 'manual_normalization',
  }));
  const payloadWithContexts = {
    ...payload,
    note_contexts: contexts,
    counts: { ...payload.counts, note_contexts_total: contexts.length },
  };
  const filters = {
    ticker: 'SPY',
    tradeDate: '2026-07-17',
    traderIds: ['alice', 'bob'],
    focusedTraderId: 'alice',
    statuses: ['active'],
    reviewStatuses: ['verified'],
    eligibility: 'display',
  };
  const selection = exportSelectionFromFilters(payloadWithContexts, filters);
  const downloads = buildTradeRecordDownloads(payloadWithContexts, groups, selection);
  const exported = JSON.parse(downloads['trade_records_spy_2026-07-17.json']);

  assert.deepEqual(exported.export_metadata.selection, {
    ticker: 'SPY',
    trade_date: '2026-07-17',
    trader_ids: ['alice'],
    statuses: ['active'],
    review_statuses: ['verified'],
    display_only: true,
  });
  assert.deepEqual(exported.trade_groups.map((item) => item.trader_id), ['alice']);
  assert.deepEqual(exported.note_contexts.map((item) => item.trader_id), ['alice']);
  assert.equal(exported.counts.trade_groups_total, 1);
  assert.equal(exported.counts.note_contexts_total, 1);
  assert.equal(downloads['trade_groups.csv'].trim().split('\n').length - 1, 1);
});
