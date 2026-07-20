import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import {
  buildTradeAvailability,
  buildTradeRecordAnnotations,
  buildTradeRecordDownloads,
  canEditTradeRecords,
  deriveAvailableTraders,
  DIRECTION_CALL_COLOR,
  DIRECTION_PUT_COLOR,
  displayableTradeGroups,
  exportSelectionFromFilters,
  filtersMatchWorkspace,
  filterTradeGroups,
  flattenTradeRecords,
  initialTradeRecordFilters,
  mirrorWorkspaceContext,
  reconcileTraderSelection,
  resolveTradeDate,
  reviewHashRoute,
  sameTraderIdSet,
  summarizeTradeGroups,
  traderSelectionSummary,
  TRADER_CHIP_INLINE_MAX,
  TRADER_CHIP_SUMMARY_MIN,
} from './tradeRecords.js';
import {
  FIXTURE_PRESERVATION_CASE,
  FIXTURE_TRADE_PAYLOADS,
  FIXTURE_TRADERS,
  FIXTURE_MULTI_TICKER_DAY,
} from './reviewWorkspace.fixtures.js';
import {
  applyOccurredAt,
  buildNewEvent,
  buildNewGroup,
  mergeGroupIntoDay,
  nextGroupId,
  preservationDiff,
  validateGroupForm,
} from './tradeCandidate.js';

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
  assert.equal('focusedTraderId' in reloaded, false);
  assert.equal(reloaded.ticker, 'SPY');
});

test('admin workspace pins capability labels, no raw JSON, and form editor gate', () => {
  const pageSource = readFileSync(new URL('../../pages/AdminTradersPage.jsx', import.meta.url), 'utf8');
  // Raw JSON editing is gone; capability is explicit for both roles.
  assert.doesNotMatch(pageSource, /textarea/);
  assert.doesNotMatch(pageSource, /registryText|dayText|JSON\.parse/);
  assert.match(pageSource, /只读：可检查与导出交易记录；新增\/编辑点位需要管理员权限。/);
  assert.match(pageSource, /管理员：通过表单新增\/编辑点位并保存/);
  // Inspection mirrors the workspace; the editor renders only for admins.
  assert.match(pageSource, /<ReviewContextPanel/);
  assert.match(pageSource, /availableTraderIds=\{traderAvailability\.availableTraderIds\}/);
  assert.match(pageSource, /\{isAdmin && \(\s*<TraderPointEditor/);
  assert.match(pageSource, /保存注册表/);
  assert.match(pageSource, /createTraderDraft\(registryDraft\)/);
  assert.match(pageSource, /appendTraderDraft\(registryDraft, createDraft\)/);
  assert.match(pageSource, />\s*新增交易者\s*</);
  assert.match(pageSource, />添加到草稿</);
  assert.match(pageSource, /isUnsaved && \(\s*<div className="tp-unsaved-actions">/);
  assert.match(pageSource, /await onSaveRegistry\(candidate\);\s*const reloaded = await Api\.adminTraders\(\);/);
  assert.match(pageSource, /associateRegistryServerError\(err\.message/);
  assert.doesNotMatch(pageSource, /删除交易者|deleteTrader|Api\.delete/);

  const editorSource = readFileSync(new URL('./TraderPointEditor.jsx', import.meta.url), 'utf8');
  // Canonical admin reads are the only write base; pure candidate contract used.
  assert.match(editorSource, /Api\.adminTradeDay\(workspace\.trade_date\)/);
  assert.doesNotMatch(editorSource, /Api\.tradeRecords/);
  assert.match(editorSource, /mergeGroupIntoDay\(dayDoc, stripMeta\(form\)\)/);
  assert.match(editorSource, /preservationDiff\(dayDoc, candidate, \{ targetGroupId: stripMeta\(form\)\.trade_group_id \}\)/);
  assert.match(editorSource, /validateGroupForm\(form\)/);
  assert.match(editorSource, /buildNewGroup\(dayDoc/);
  // Save is explicit, confirm-gated, fail-closed, and never auto-retried.
  assert.match(editorSource, /disabled=\{!canSave\}/);
  assert.match(editorSource, /window\.confirm\(summary\)/);
  assert.match(editorSource, /errorCount === 0 && diff\?\.ok/);
  assert.match(editorSource, /catch \(err\) \{\s*\/\/ Unsaved form state is retained/);
  // Direction change keeps the leg option_type in sync; 404 maps to the
  // explicit missing-day branch via the client error status.
  assert.match(editorSource, /direction: event\.target\.value,\s*\n\s*legs: \[\{ \.\.\.previous\.legs\[0\], option_type: event\.target\.value \}\]/);
  assert.match(editorSource, /err\.status === 404/);
  assert.match(editorSource, /updateEvent\(index, applyOccurredAt\(event, e\.target\.value\)\)/);
  // Missing day requires an explicit user action; readonly renders nothing.
  assert.match(editorSource, /新建该日期文档/);
  assert.match(editorSource, /if \(!isAdmin\) return null;/);

  const styleSource = readFileSync(new URL('../../styles.css', import.meta.url), 'utf8');
  assert.match(styleSource, /\.tp-group-picker button \{[^}]*background: var\(--surface-control\); color: var\(--text-primary\);/);
  assert.match(styleSource, /\.tp-missing-day button \{[^}]*background: var\(--surface-control\); color: var\(--text-primary\);/);
  assert.match(styleSource, /\.tp-field input, \.tp-field select, \.tp-field textarea \{[^}]*background: var\(--surface-control\);[^}]*color: var\(--text-primary\);/);
  assert.match(styleSource, /\.tp-form-grid \{[^}]*grid-template-columns: repeat\(auto-fit, minmax\(min\(160px, 100%\), 1fr\)\);/);
  assert.match(styleSource, /\.tp-error \{ color: var\(--status-danger\);/);
  assert.match(styleSource, /\.tp-success \{ color: var\(--status-success\);/);
  assert.doesNotMatch(styleSource, /background:\s*(?:#fff\b|white\b)/i);
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

test('multi-select, status, review, and eligibility filter at group level without focus override', () => {
  const selected = filterTradeGroups(payload, {
    ticker: 'SPY',
    tradeDate: '2026-07-17',
    traderIds: ['alice'],
    statuses: ['active'],
    reviewStatuses: ['verified'],
    eligibility: 'reported',
  });
  assert.deepEqual(selected.map((item) => item.trade_group_id), ['tg_20260717_alice_spy_001']);
  assert.deepEqual(filterTradeGroups(payload, { traderIds: [] }), []);
  // Subset selection is pure set membership — no hidden focus override.
  const both = filterTradeGroups(payload, { traderIds: ['alice', 'bob'] });
  assert.deepEqual(both.map((item) => item.trader_id).sort(), ['alice', 'bob']);
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

test('marker color is direction-owned while CALL and PUT shapes stay independent', () => {
  const bars = [{ t: '10:00' }, { t: '10:01' }];
  const markers = buildTradeRecordAnnotations(groups, traders, bars);
  assert.equal(markers.length, 2);
  assert.equal(markers[0].marker_color, DIRECTION_CALL_COLOR);
  assert.equal(markers[0].marker_color, '#6F9F7A');
  assert.equal(markers[0].marker_shape, 'triangle_up');
  assert.equal(markers[0].grouped_marker_count, 2);
  assert.equal(markers[0].marker_label, 'alice CALL ×2');
  assert.deepEqual(markers[0].event_ids, [
    'tg_20260717_alice_spy_001_l1_e1',
    'tg_20260717_alice_spy_001_l1_e2',
  ]);
  assert.equal(markers[1].marker_color, DIRECTION_PUT_COLOR);
  assert.equal(markers[1].marker_color, '#E06B66');
  assert.equal(markers[1].marker_shape, 'triangle_down');
  // Same trader CALL+PUT would differ only by direction color, not registry hue.
  const sameTrader = [
    groups[0],
    { ...groups[1], trader_id: 'alice', trade_group_id: 'tg_20260717_alice_spy_put' },
  ];
  const sameMarkers = buildTradeRecordAnnotations(sameTrader, traders, bars);
  assert.equal(sameMarkers[0].marker_color, DIRECTION_CALL_COLOR);
  assert.equal(sameMarkers[1].marker_color, DIRECTION_PUT_COLOR);
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
    traderIds: ['alice'],
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
  // Export order remains alphabetical even when UI selection order differs.
  const reversed = exportSelectionFromFilters(payloadWithContexts, {
    ...filters,
    traderIds: ['bob', 'alice'],
  });
  assert.deepEqual(reversed.trader_ids, ['alice', 'bob']);
  assert.equal(sameTraderIdSet(['bob', 'alice'], reversed.trader_ids), true);
});

// --- Availability-driven trader contract (plan §3.3) -------------------------

test('availability derives only traders with displayable groups in registry order', () => {
  assert.deepEqual(
    deriveAvailableTraders(FIXTURE_TRADE_PAYLOADS['spy-2026-07-17'], FIXTURE_TRADERS).availableTraderIds,
    ['tang'],
  );
  assert.deepEqual(
    deriveAvailableTraders(FIXTURE_TRADE_PAYLOADS['qqq-2026-07-17'], FIXTURE_TRADERS).availableTraderIds,
    ['vordin'],
  );
  // Registry order wins over group order: vordin (sort_order 20) follows tang (10).
  const vordinSpyGroup = {
    ...FIXTURE_TRADE_PAYLOADS['qqq-2026-07-17'].trade_groups[0],
    underlying: 'SPY',
    trade_date: '2026-07-17',
  };
  const bothPayload = {
    ...FIXTURE_TRADE_PAYLOADS['spy-2026-07-17'],
    trade_groups: [vordinSpyGroup, ...FIXTURE_TRADE_PAYLOADS['spy-2026-07-17'].trade_groups],
  };
  assert.deepEqual(
    deriveAvailableTraders(bothPayload, FIXTURE_TRADERS).availableTraderIds,
    ['tang', 'vordin'],
  );
});

test('pending-only and empty days expose no visible trader option', () => {
  // QQQ 2026-07-14 is pending-only: invisible under the default display contract.
  const pending = deriveAvailableTraders(FIXTURE_TRADE_PAYLOADS['qqq-2026-07-14'], FIXTURE_TRADERS);
  assert.deepEqual(pending.availableTraderIds, []);
  assert.equal(pending.displayableGroups.length, 0);
  // An explicit pending review filter makes the same groups displayable again.
  const pendingIncluded = deriveAvailableTraders(
    FIXTURE_TRADE_PAYLOADS['qqq-2026-07-14'],
    FIXTURE_TRADERS,
    { reviewStatuses: ['pending', 'verified'] },
  );
  assert.deepEqual(pendingIncluded.availableTraderIds, ['vordin']);
  // SPY 2026-05-29 has zero trade groups: no trader renders even though the
  // registry lists two active traders.
  const emptyDay = deriveAvailableTraders(FIXTURE_TRADE_PAYLOADS['spy-2026-05-29'], FIXTURE_TRADERS);
  assert.deepEqual(emptyDay.availableTraderIds, []);
  // Static view of the pending day is equally empty.
  assert.deepEqual(
    deriveAvailableTraders(FIXTURE_TRADE_PAYLOADS['qqq-2026-07-14-static'], FIXTURE_TRADERS).availableTraderIds,
    [],
  );
});

test('selection reconciliation honors context change and intentional empty without focus', () => {
  // Initial load selects every available trader.
  assert.deepEqual(
    reconcileTraderSelection({ previousSelectedIds: null, availableTraderIds: ['tang', 'vordin'] }),
    { selectedTraderIds: ['tang', 'vordin'] },
  );
  // Context change keeps the intersection with availability.
  assert.deepEqual(
    reconcileTraderSelection({
      previousSelectedIds: ['tang', 'vordin'],
      availableTraderIds: ['vordin'],
      contextChanged: true,
    }),
    { selectedTraderIds: ['vordin'] },
  );
  // Context change with an empty intersection re-selects all available traders.
  assert.deepEqual(
    reconcileTraderSelection({
      previousSelectedIds: ['tang'],
      availableTraderIds: ['vordin'],
      contextChanged: true,
    }).selectedTraderIds,
    ['vordin'],
  );
  // Within the same context an intentional empty selection stays empty.
  assert.deepEqual(
    reconcileTraderSelection({
      previousSelectedIds: [],
      availableTraderIds: ['tang', 'vordin'],
      contextChanged: false,
    }).selectedTraderIds,
    [],
  );
  // Context change into an empty-availability day selects nothing.
  assert.deepEqual(
    reconcileTraderSelection({
      previousSelectedIds: ['tang'],
      availableTraderIds: [],
      contextChanged: true,
    }),
    { selectedTraderIds: [] },
  );
});

test('Review and Static assemble derive contextChanged from ticker/date only', () => {
  const reviewSource = readFileSync(new URL('../../pages/ReviewPage.jsx', import.meta.url), 'utf8');
  const staticSource = readFileSync(new URL('../../pages/StaticReviewsApp.jsx', import.meta.url), 'utf8');
  for (const source of [reviewSource, staticSource]) {
    assert.match(source, /const contextChanged = !previous/);
    assert.match(source, /previous\.ticker !== records\.ticker/);
    assert.match(source, /previous\.tradeDate !== records\.trade_date/);
    // Must not hard-code contextChanged: true on the assemble reconcile path.
    assert.doesNotMatch(source, /contextChanged:\s*true/);
  }
  // Same-context empty selection stays empty even if availability is full.
  assert.deepEqual(
    reconcileTraderSelection({
      previousSelectedIds: [],
      availableTraderIds: ['tang', 'vordin'],
      contextChanged: false,
    }).selectedTraderIds,
    [],
  );
});

test('filter ticker/date may only mirror the resolved workspace context', () => {
  const workspace = { ticker: 'QQQ', trade_date: '2026-07-17' };
  const divergent = { ticker: 'SPY', tradeDate: '2026-06-15', traderIds: ['tang'] };
  assert.equal(filtersMatchWorkspace(divergent, workspace), false);
  const mirrored = mirrorWorkspaceContext(divergent, workspace);
  assert.equal(mirrored.ticker, 'QQQ');
  assert.equal(mirrored.tradeDate, '2026-07-17');
  assert.deepEqual(mirrored.traderIds, ['tang']);
  assert.equal(filtersMatchWorkspace(mirrored, workspace), true);
});

test('reconciled filters drive markers, lists, and exports from one resolved object', () => {
  // Switch QQQ 2026-07-17 -> SPY 2026-07-17: availability drops vordin.
  const spyPayload = FIXTURE_TRADE_PAYLOADS['spy-2026-07-17'];
  const { availableTraderIds } = deriveAvailableTraders(spyPayload, FIXTURE_TRADERS);
  const reconciled = reconcileTraderSelection({
    previousSelectedIds: ['vordin'],
    availableTraderIds,
    contextChanged: true,
  });
  assert.deepEqual(reconciled.selectedTraderIds, ['tang']);
  assert.equal('focusedTraderId' in reconciled, false);
  const filters = mirrorWorkspaceContext({
    ...initialTradeRecordFilters(FIXTURE_TRADERS),
    traderIds: reconciled.selectedTraderIds,
  }, { ticker: 'SPY', trade_date: '2026-07-17' });
  assert.equal(filtersMatchWorkspace(filters, { ticker: 'SPY', trade_date: '2026-07-17' }), true);
  const selection = exportSelectionFromFilters(spyPayload, filters);
  assert.deepEqual(selection.trader_ids, ['tang']);
  // List / export share the same canonical trader-ID set membership.
  const filtered = filterTradeGroups(spyPayload, filters);
  const listIds = filtered.map((group) => group.trader_id);
  assert.equal(sameTraderIdSet(listIds, selection.trader_ids), true);
  assert.deepEqual(listIds, ['tang']);
  // Markers consume the same membership set when groups have timed events.
  const subsetFilters = {
    ticker: 'SPY',
    tradeDate: '2026-07-17',
    traderIds: ['alice'],
    statuses: ['active'],
    reviewStatuses: ['verified'],
    eligibility: 'display',
  };
  const subsetGroups = filterTradeGroups(payload, subsetFilters);
  const subsetExport = exportSelectionFromFilters(payload, subsetFilters);
  const subsetMarkers = buildTradeRecordAnnotations(subsetGroups, traders, [{ t: '10:00' }, { t: '10:01' }]);
  assert.ok(subsetMarkers.length > 0);
  assert.equal(sameTraderIdSet(
    subsetGroups.map((group) => group.trader_id),
    subsetExport.trader_ids,
  ), true);
  assert.equal(sameTraderIdSet(
    subsetMarkers.map((marker) => marker.trader_id),
    subsetExport.trader_ids,
  ), true);
});

test('trader filter component pins B chips, availability, and no focus override', () => {
  const source = readFileSync(new URL('./TraderFilters.jsx', import.meta.url), 'utf8');
  // Resolved context omits ticker/date mirror; workspace owns day authority.
  assert.match(source, /!context && \(/);
  assert.doesNotMatch(source, /trade-context-mirror/);
  assert.doesNotMatch(source, /focusedTraderId/);
  assert.doesNotMatch(source, />Focus</);
  // Availability-driven rendering plus one neutral empty state.
  assert.match(source, /availableTraderIds\.includes\(trader\.trader_id\)/);
  assert.match(source, /className="trade-trader-empty" role="status"/);
  // B chips use aria-pressed; drawer thresholds follow frozen constants.
  assert.match(source, /aria-pressed=\{pressed\}/);
  assert.match(source, /className=\{\`trade-trader-chip \$\{pressed \? 'active' : ''\}\`\}/);
  assert.match(source, /TRADER_CHIP_INLINE_MAX/);
  assert.match(source, />\s*编辑\s*</);
  assert.match(source, />\s*全选\s*</);
  assert.match(source, />\s*清空\s*</);
  assert.equal(TRADER_CHIP_INLINE_MAX, 6);
  assert.equal(TRADER_CHIP_SUMMARY_MIN, 7);
  const styles = readFileSync(new URL('../../styles.css', import.meta.url), 'utf8');
  assert.doesNotMatch(styles, /--trader-color/);
  assert.match(styles, /--direction-call: #6F9F7A;/);
  assert.match(styles, /--direction-put: #E06B66;/);
  const listSource = readFileSync(new URL('./TraderTradeList.jsx', import.meta.url), 'utf8');
  assert.doesNotMatch(listSource, /--trader-color|focusedTraderId/);
  assert.match(listSource, /trade-trader-name/);
  assert.match(listSource, /trade-direction-word/);
  const summary = traderSelectionSummary(
    [
      { trader_id: 'a', display_name: 'Alice' },
      { trader_id: 'b', display_name: 'Bob' },
      { trader_id: 'c', display_name: 'Cara' },
      { trader_id: 'd', display_name: 'Dan' },
    ],
    ['a', 'b', 'c', 'd'],
  );
  assert.equal(summary.selectedCount, 4);
  assert.deepEqual(summary.names, ['Alice', 'Bob', 'Cara']);
  assert.equal(summary.overflow, 1);
});

// --- Trader point editor candidate contract (plan §3.4) -----------------------

test('new group factory pins every schema-required field with a stable next id', () => {
  assert.equal(
    nextGroupId(FIXTURE_MULTI_TICKER_DAY, { tradeDate: '2026-07-17', traderId: 'vordin', underlying: 'QQQ' }),
    'tg_20260717_vordin_qqq_003',
  );
  assert.equal(
    nextGroupId(FIXTURE_MULTI_TICKER_DAY, { tradeDate: '2026-07-17', traderId: 'tang', underlying: 'SPY' }),
    'tg_20260717_tang_spy_002',
  );
  const group = buildNewGroup(FIXTURE_MULTI_TICKER_DAY, {
    tradeDate: '2026-07-17',
    traderId: 'vordin',
    underlying: 'QQQ',
  });
  assert.equal(group.trade_group_id, 'tg_20260717_vordin_qqq_003');
  assert.equal(group.review_status, 'pending');
  assert.equal(group.legs.length, 1);
  assert.equal(group.legs[0].option_type, group.direction);
  assert.equal(group.legs[0].events[0].action, 'buy_open');
  // The normalization block is explicit, never implicit (review-003 foldback).
  assert.deepEqual(group.normalization, {
    method: 'manual_normalization',
    source: 'manual_entry',
    source_path: null,
    source_index: null,
    review_flags: [],
  });
  assert.deepEqual(validateGroupForm(group), {});
});

test('full-day merge preserves every untouched group, leg, event, and context', () => {
  const base = FIXTURE_PRESERVATION_CASE.document;
  const targetId = FIXTURE_PRESERVATION_CASE.scopedEditTargetGroupId;
  const edited = structuredClone(base);
  const target = edited.trade_groups.find((group) => group.trade_group_id === targetId);
  target.notes.push({ text: 'Edited note.', provenance: 'user_provided' });
  const editedTarget = target;
  const candidate = mergeGroupIntoDay(base, editedTarget);
  const diff = preservationDiff(base, candidate, { targetGroupId: targetId });
  assert.equal(diff.ok, true);
  assert.equal(diff.countDelta, 0);
  assert.deepEqual(diff.addedGroupIds, []);
  assert.deepEqual(diff.untouchedGroupIds, FIXTURE_PRESERVATION_CASE.expectedUntouchedGroupIds);
  // Untouched records are carried by reference (byte-equivalent at the boundary).
  for (const id of FIXTURE_PRESERVATION_CASE.expectedUntouchedGroupIds) {
    const before = base.trade_groups.find((group) => group.trade_group_id === id);
    const after = candidate.trade_groups.find((group) => group.trade_group_id === id);
    assert.equal(after, before);
  }
  assert.equal(candidate.note_contexts, base.note_contexts);

  const added = buildNewGroup(base, { tradeDate: '2026-07-17', traderId: 'vordin', underlying: 'QQQ' });
  const addedCandidate = mergeGroupIntoDay(base, added);
  const addDiff = preservationDiff(base, addedCandidate, { targetGroupId: added.trade_group_id });
  assert.equal(addDiff.ok, true);
  assert.equal(addDiff.countDelta, 1);
  assert.deepEqual(addDiff.addedGroupIds, ['tg_20260717_vordin_qqq_003']);
});

test('preservation diff fails closed on any out-of-scope change', () => {
  const base = FIXTURE_PRESERVATION_CASE.document;
  const targetId = FIXTURE_PRESERVATION_CASE.scopedEditTargetGroupId;

  const tampered = mergeGroupIntoDay(base, (() => {
    const copy = structuredClone(base.trade_groups.find((group) => group.trade_group_id === 'tg_20260717_tang_spy_001'));
    copy.notes.push({ text: 'Tampered.', provenance: 'user_provided' });
    return copy;
  })());
  const tamperDiff = preservationDiff(base, tampered, { targetGroupId: targetId });
  assert.equal(tamperDiff.ok, false);
  assert.match(tamperDiff.problems.join('\n'), /untouched group changed: tg_20260717_tang_spy_001/);

  const removed = { ...base, trade_groups: base.trade_groups.slice(1) };
  const removeDiff = preservationDiff(base, removed, { targetGroupId: targetId });
  assert.equal(removeDiff.ok, false);
  assert.match(removeDiff.problems.join('\n'), /group removed: tg_20260717_tang_spy_001/);

  const contextChanged = { ...base, note_contexts: [] };
  const contextDiff = preservationDiff(base, contextChanged, { targetGroupId: targetId });
  assert.equal(contextDiff.ok, false);
  assert.match(contextDiff.problems.join('\n'), /note_contexts changed/);

  const twoAdds = [buildNewGroup(base, { tradeDate: '2026-07-17', traderId: 'vordin', underlying: 'QQQ' })];
  const doc1 = mergeGroupIntoDay(base, twoAdds[0]);
  const doc2 = mergeGroupIntoDay(doc1, buildNewGroup(doc1, { tradeDate: '2026-07-17', traderId: 'tang', underlying: 'SPY' }));
  const twoAddDiff = preservationDiff(base, doc2, { targetGroupId: twoAdds[0].trade_group_id });
  assert.equal(twoAddDiff.ok, false);
  assert.match(twoAddDiff.problems.join('\n'), /unexpected groups added/);
});

test('group form validation flags contract violations with field paths', () => {
  const valid = buildNewGroup(FIXTURE_MULTI_TICKER_DAY, { tradeDate: '2026-07-17', traderId: 'tang', underlying: 'SPY' });

  const voidedEligible = { ...valid, status: 'voided' };
  assert.match(validateGroupForm(voidedEligible).status, /eligibility/);

  const reportedNoOutcome = { ...valid, reported_stats_eligible: true };
  assert.match(validateGroupForm(reportedNoOutcome)['reported_outcome'], /reported outcome/);

  const wrongOptionType = structuredClone(valid);
  wrongOptionType.direction = 'PUT';
  assert.match(validateGroupForm(wrongOptionType)['leg.option_type'], /match direction/);

  const secondBuyOpen = structuredClone(valid);
  secondBuyOpen.legs[0].events.push({ ...buildNewEvent('tg_20260717_tang_spy_002_l1_e2', 2), action: 'buy_open' });
  assert.match(validateGroupForm(secondBuyOpen)['leg.events[1].action'], /buy_open/);

  const noOffset = structuredClone(valid);
  noOffset.legs[0].events[0].occurred_at = '2026-07-17T10:00';
  assert.match(validateGroupForm(noOffset)['leg.events[0].occurred_at'], /offset/);

  const knownButIncomplete = structuredClone(valid);
  knownButIncomplete.legs[0].events[0].occurred_at = '2026-07-17T10:00-04:00';
  assert.match(validateGroupForm(knownButIncomplete)['leg.events[0].time_incomplete'], /must be false/);
  assert.match(validateGroupForm(knownButIncomplete)['leg.events[0].time_precision'], /known timestamp/);

  const missingButComplete = structuredClone(valid);
  missingButComplete.legs[0].events[0].time_incomplete = false;
  assert.match(validateGroupForm(missingButComplete)['leg.events[0]'], /missing occurred_at/);

  const badProvenance = structuredClone(valid);
  badProvenance.legs[0].events[0].fact_provenance.premium = 'guessed';
  assert.match(validateGroupForm(badProvenance)['leg.events[0].fact_provenance'], /provenance/);

  const noSource = structuredClone(valid);
  noSource.normalization.source = '';
  assert.match(validateGroupForm(noSource)['normalization.source'], /source required/);

  const dupFlags = structuredClone(valid);
  dupFlags.normalization.review_flags = ['a', 'a'];
  assert.match(validateGroupForm(dupFlags)['normalization.review_flags'], /unique/);
});

test('occurred-at edits atomically reconcile timestamp completeness and provenance', () => {
  const initial = buildNewEvent('tg_20260717_vordin_qqq_003_l1_e1', 1);
  const known = applyOccurredAt(initial, ' 2026-07-17T09:42-04:00 ');
  assert.equal(known.occurred_at, '2026-07-17T09:42-04:00');
  assert.equal(known.time_precision, 'minute');
  assert.equal(known.time_incomplete, false);
  assert.equal(known.fact_provenance.occurred_at, 'user_provided');

  const cleared = applyOccurredAt({ ...known, time_precision: 'exact' }, '');
  assert.equal(cleared.occurred_at, null);
  assert.equal(cleared.time_precision, null);
  assert.equal(cleared.time_incomplete, true);
  assert.equal(cleared.fact_provenance.occurred_at, 'unknown');
});

test('no live focusedTraderId or shared registry-hue chip/card binding remains', () => {
  const roots = [
    './tradeRecords.js',
    './TraderFilters.jsx',
    './TraderTradeList.jsx',
    '../../pages/ReviewPage.jsx',
    '../../pages/StaticReviewsApp.jsx',
    '../../pages/AdminTradersPage.jsx',
    '../../styles.css',
  ];
  for (const rel of roots) {
    const source = readFileSync(new URL(rel, import.meta.url), 'utf8');
    assert.doesNotMatch(source, /focusedTraderId/);
    if (rel.endsWith('styles.css') || rel.includes('Trader')) {
      assert.doesNotMatch(source, /--trader-color/);
    }
  }
  assert.doesNotMatch(
    readFileSync(new URL('../../pages/ReviewPage.jsx', import.meta.url), 'utf8'),
    />Focus</,
  );
});
