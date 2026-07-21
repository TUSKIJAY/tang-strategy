const RECORD_STATUSES = new Set(['active', 'voided', 'superseded']);
const REVIEW_STATUSES = new Set(['pending', 'verified']);
const FORBIDDEN_EXPORT_FIELDS = new Set([
  'attachment', 'attachments', 'chat_export', 'chat_transcript', 'discord_export',
  'evidence_blob', 'image_base64', 'raw_chat', 'raw_evidence', 'raw_message',
  'screenshot', 'screenshots', 'source_path', 'source_index', 'review_flags',
]);

function array(value) {
  return Array.isArray(value) ? value : [];
}

function timePart(value) {
  const text = String(value || '');
  const match = text.match(/T(\d{2}):(\d{2})/);
  return match ? `${match[1]}:${match[2]}` : '';
}

function barTime(bar) {
  return String(bar?.t || bar?.time || '').slice(0, 5);
}

function barIndexForEvent(event, bars) {
  const target = timePart(event?.occurred_at);
  if (!target || !bars.length) return 0;
  const exact = bars.findIndex((bar) => barTime(bar) === target);
  if (exact >= 0) return exact;
  let prior = 0;
  bars.forEach((bar, index) => {
    if (barTime(bar) <= target) prior = index;
  });
  return prior;
}

function canonicalCsvValue(value) {
  if (value == null) return '';
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  const text = String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function csv(columns, rows) {
  return [columns, ...rows.map((row) => columns.map((column) => canonicalCsvValue(row[column])))]
    .map((row) => row.join(','))
    .join('\n') + '\n';
}

function assertPublicExport(value, path = 'root') {
  if (Array.isArray(value)) {
    value.forEach((item, index) => assertPublicExport(item, `${path}[${index}]`));
    return;
  }
  if (!value || typeof value !== 'object') return;
  Object.entries(value).forEach(([key, item]) => {
    if (FORBIDDEN_EXPORT_FIELDS.has(key.toLowerCase().replaceAll('-', '_'))) {
      throw new Error(`${path}.${key}: private or raw evidence field is forbidden`);
    }
    assertPublicExport(item, `${path}.${key}`);
  });
}

export const DIRECTION_CALL_COLOR = '#6F9F7A';
export const DIRECTION_PUT_COLOR = '#E06B66';
export const TRADER_CHIP_INLINE_MAX = 6;
export const TRADER_CHIP_SUMMARY_MIN = 7;

export function directionColor(direction) {
  return String(direction || '').toUpperCase() === 'PUT'
    ? DIRECTION_PUT_COLOR
    : DIRECTION_CALL_COLOR;
}

export function initialTradeRecordFilters(traders = []) {
  return {
    ticker: 'SPY',
    tradeDate: '',
    traderIds: array(traders).filter((trader) => trader.active).map((trader) => trader.trader_id),
    statuses: ['active'],
    reviewStatuses: ['verified'],
    eligibility: 'display',
  };
}

/**
 * Shared Trade tools path always forces display-only eligibility.
 * Stale or omitted eligibility cannot widen list / availability / export.
 */
export function canonicalizeTradeToolsFilters(filters = {}) {
  return {
    ...filters,
    eligibility: 'display',
  };
}

export function canEditTradeRecords(role) {
  return role === 'admin';
}

export function exportSelectionFromFilters(payload, filters = {}) {
  const canonical = canonicalizeTradeToolsFilters(filters);
  const traderIds = array(canonical.traderIds);
  return {
    ticker: String(canonical.ticker || payload?.ticker || '').toUpperCase(),
    trade_date: String(canonical.tradeDate || payload?.trade_date || ''),
    trader_ids: [...new Set(traderIds.map(String))].sort(),
    statuses: [...new Set(array(canonical.statuses).map(String))].sort(),
    review_statuses: [...new Set(array(canonical.reviewStatuses).map(String))].sort(),
    display_only: true,
  };
}

/** Canonical set-membership equality for list / markers / export consumers. */
export function sameTraderIdSet(a = [], b = []) {
  const left = [...new Set(array(a).map(String))].sort();
  const right = [...new Set(array(b).map(String))].sort();
  return left.length === right.length && left.every((id, index) => id === right[index]);
}

export function traderSelectionSummary(traders = [], selectedIds = [], maxNames = 3) {
  const selected = new Set(array(selectedIds).map(String));
  const ordered = array(traders).filter((trader) => selected.has(String(trader.trader_id)));
  const names = ordered.map((trader) => trader.display_name || trader.trader_id);
  const shown = names.slice(0, maxNames);
  const overflow = Math.max(0, names.length - shown.length);
  return {
    selectedCount: ordered.length,
    names: shown,
    overflow,
    label: ordered.length === 0
      ? '未选择交易者'
      : `${ordered.length} 已选 · ${shown.join('、')}${overflow ? ` 等${overflow}人` : ''}`,
  };
}

export function buildTradeAvailability(payloads = []) {
  const availability = {};
  array(payloads).forEach((payload) => {
    const ticker = String(payload?.ticker || '').toUpperCase();
    const tradeDate = String(payload?.trade_date || '');
    if (!ticker || !tradeDate) return;
    availability[ticker] ||= [];
    if (!availability[ticker].includes(tradeDate)) availability[ticker].push(tradeDate);
  });
  Object.values(availability).forEach((dates) => dates.sort());
  return availability;
}

export function resolveTradeDate(availability, ticker, requestedDate = '') {
  const dates = array(availability?.[ticker]);
  if (dates.includes(requestedDate)) return requestedDate;
  return dates.at(-1) || '';
}

export function reviewHashRoute(ticker, tradeDate, sessionMode = 'extended') {
  return `#${String(ticker).toLowerCase()}-${tradeDate}-${String(sessionMode).toLowerCase().replaceAll('_', '-')}`;
}

export function filterTradeGroups(payload, filters = {}) {
  const canonical = canonicalizeTradeToolsFilters(filters);
  const hasTraderSelection = Array.isArray(canonical.traderIds);
  const traderIds = new Set(array(canonical.traderIds));
  const statuses = new Set(array(canonical.statuses).length ? canonical.statuses : RECORD_STATUSES);
  const reviewStatuses = new Set(
    array(canonical.reviewStatuses).length ? canonical.reviewStatuses : REVIEW_STATUSES,
  );
  // Shared tools path is always display-only after canonicalize.
  return array(payload?.trade_groups).filter((group) => (
    (!canonical.ticker || group.underlying === canonical.ticker) &&
    (!canonical.tradeDate || group.trade_date === canonical.tradeDate) &&
    (!hasTraderSelection || traderIds.has(group.trader_id)) &&
    statuses.has(group.status) &&
    reviewStatuses.has(group.review_status) &&
    Boolean(group.display_eligible)
  ));
}

export function summarizeTradeGroups(groups = []) {
  const complete = array(groups);
  const reported = complete.filter((group) => (
    group.reported_stats_eligible && Number.isFinite(Number(group.reported_outcome?.return_pct))
  ));
  const calculated = complete.filter((group) => (
    group.calculated_stats_eligible && Number.isFinite(Number(group.calculated_outcome?.return_pct))
  ));
  const summarize = (selected, field) => {
    const returns = selected.map((group) => Number(group[field].return_pct));
    return {
      groups: returns.length,
      wins: returns.filter((value) => value > 0).length,
      losses: returns.filter((value) => value < 0).length,
      win_rate: returns.length ? returns.filter((value) => value > 0).length / returns.length : null,
      average_return_pct: returns.length
        ? returns.reduce((sum, value) => sum + value, 0) / returns.length
        : null,
    };
  };
  return {
    group_count: complete.length,
    displayed_groups: complete.filter((group) => group.display_eligible).length,
    reported: summarize(reported, 'reported_outcome'),
    calculated: summarize(calculated, 'calculated_outcome'),
  };
}

/** Exact schema action → BUY/SELL. Empty/unknown → null (omit marker). */
export function tradeEventActionSide(action) {
  const value = String(action || '');
  if (value === 'buy_open' || value === 'buy_add') return 'BUY';
  if (value === 'sell_partial' || value === 'sell_close') return 'SELL';
  return null;
}

/** Compact timeline action: BUY / SELL / PART (sell_partial → PART). */
export function tradeEventActionLabel(action) {
  const value = String(action || '');
  if (value === 'buy_open' || value === 'buy_add') return 'BUY';
  if (value === 'sell_close') return 'SELL';
  if (value === 'sell_partial') return 'PART';
  return null;
}

/**
 * Chronological min/max of complete leg event times across a group.
 * Incomplete/missing times are ignored; array order is irrelevant.
 * knownCount 0 → no label; 1 → HH:MM; ≥2 → HH:MM → HH:MM.
 */
export function groupEventTimeRange(group) {
  const stamps = [];
  array(group?.legs).forEach((leg) => {
    array(leg?.events).forEach((event) => {
      if (!event?.occurred_at || event.time_incomplete) return;
      const hhmm = timePart(event.occurred_at);
      if (!hhmm) return;
      stamps.push({ at: String(event.occurred_at), hhmm });
    });
  });
  stamps.sort((left, right) => left.at.localeCompare(right.at));
  if (stamps.length === 0) {
    return { knownCount: 0, start: null, end: null, label: null };
  }
  const start = stamps[0].hhmm;
  const end = stamps[stamps.length - 1].hhmm;
  if (stamps.length === 1) {
    return { knownCount: 1, start, end: start, label: start };
  }
  return { knownCount: stamps.length, start, end, label: `${start} → ${end}` };
}

/** Card meta: span label + complete-timed point count (`N pts`). */
export function groupCardMeta(group) {
  const range = groupEventTimeRange(group);
  const pointsLabel = range.knownCount > 0 ? `${range.knownCount} pts` : null;
  return {
    ...range,
    pointsLabel,
    metaSuffix: range.label
      ? (pointsLabel ? `${range.label} · ${pointsLabel}` : range.label)
      : null,
  };
}

/**
 * Compact complete-timed timeline rows for expanded card UI.
 * Shape: TIME | ACTION | QTY @ PX with BUY/SELL/PART; no fees.
 */
export function groupTimelineEvents(group) {
  const rows = [];
  array(group?.legs).forEach((leg) => {
    array(leg?.events).forEach((event) => {
      if (!event?.occurred_at || event.time_incomplete) return;
      const hhmm = timePart(event.occurred_at);
      if (!hhmm) return;
      const actionLabel = tradeEventActionLabel(event.action);
      if (!actionLabel) return;
      rows.push({
        event_id: event.event_id,
        leg_id: leg.leg_id,
        trade_group_id: group.trade_group_id,
        occurred_at: String(event.occurred_at),
        time: hhmm,
        action: event.action,
        actionLabel,
        quantity: event.quantity,
        premium: event.premium,
      });
    });
  });
  rows.sort((left, right) => left.occurred_at.localeCompare(right.occurred_at));
  return rows;
}

/**
 * Min/max bar indices for all complete-timed events on the given bars.
 * Incomplete times ignored; single event → min===max.
 */
export function groupBarSpan(group, bars = []) {
  const barList = array(bars);
  const indices = [];
  array(group?.legs).forEach((leg) => {
    array(leg?.events).forEach((event) => {
      if (!event?.occurred_at || event.time_incomplete) return;
      if (!timePart(event.occurred_at)) return;
      indices.push(barIndexForEvent(event, barList));
    });
  });
  if (!indices.length) {
    return {
      knownCount: 0,
      startIndex: null,
      endIndex: null,
      minIndex: null,
      maxIndex: null,
    };
  }
  const minIndex = Math.min(...indices);
  const maxIndex = Math.max(...indices);
  return {
    knownCount: indices.length,
    startIndex: minIndex,
    endIndex: maxIndex,
    minIndex,
    maxIndex,
  };
}

/**
 * Event-row focus payload: single-bar highlight, not full-day span.
 */
export function eventFocusPayload(event, bars = [], options = {}) {
  if (!event?.occurred_at || event.time_incomplete) return null;
  if (!timePart(event.occurred_at)) return null;
  const barList = array(bars);
  const index = barIndexForEvent(event, barList);
  const timeframe = options.timeframe === '5m' ? '5m' : '1m';
  return {
    timeframe,
    startIndex: index,
    endIndex: index,
    style: 'blue',
    barIndex: index,
    event_id: event.event_id || null,
  };
}

export function buildTradeRecordAnnotations(groups = [], traders = [], bars = []) {
  // Direction owns marker shape/color; registry color is intentionally unused.
  // Display names come from the traders map (display_name || trader_id).
  const traderMap = new Map(array(traders).map((trader) => [trader.trader_id, trader]));
  const markers = [];
  array(groups).forEach((group) => {
    const trader = traderMap.get(group.trader_id) || {};
    const displayName = trader.display_name || group.trader_id;
    array(group.legs).forEach((leg) => {
      array(leg.events).forEach((event) => {
        if (!event.occurred_at || event.time_incomplete) return;
        const actionSide = tradeEventActionSide(event.action);
        if (!actionSide) return;
        const direction = group.direction === 'PUT' ? 'PUT' : 'CALL';
        const sideText = `${displayName} ${actionSide}`;
        markers.push({
          id: `trade-record-${event.event_id}`,
          type: 'trade_record',
          trade_group_id: group.trade_group_id,
          event_id: event.event_id,
          trader_id: group.trader_id,
          direction,
          action_side: actionSide,
          marker_shape: direction === 'PUT' ? 'triangle_down' : 'triangle_up',
          marker_color: directionColor(direction),
          anchor_side: direction === 'PUT' ? 'top' : 'bottom',
          bar_index: barIndexForEvent(event, bars),
          t: timePart(event.occurred_at),
          title: sideText,
          body: event.note || `${leg.expiry} ${leg.strike ?? '--'} ${leg.option_type}`,
          marker_label: sideText,
          score: null,
        });
      });
    });
  });
  const groupedMarkers = new Map();
  markers.forEach((marker) => {
    const key = `${marker.bar_index}|${marker.trader_id}|${marker.direction}|${marker.action_side}`;
    const existing = groupedMarkers.get(key);
    if (!existing) {
      groupedMarkers.set(key, {
        ...marker,
        event_ids: [marker.event_id],
        trade_group_ids: [marker.trade_group_id],
        grouped_marker_count: 1,
      });
      return;
    }
    existing.event_ids.push(marker.event_id);
    if (!existing.trade_group_ids.includes(marker.trade_group_id)) {
      existing.trade_group_ids.push(marker.trade_group_id);
    }
    existing.grouped_marker_count += 1;
    // title stays displayName + BUY|SELL; ×N is label-only.
  });
  return [...groupedMarkers.values()].map((marker) => {
    const count = marker.grouped_marker_count;
    return {
      ...marker,
      marker_label: count > 1 ? `${marker.marker_label} ×${count}` : marker.marker_label,
    };
  });
}

export function flattenTradeRecords(groups = []) {
  const legs = [];
  const events = [];
  array(groups).forEach((group) => {
    array(group.legs).forEach((leg) => {
      legs.push({ ...leg, trade_group_id: group.trade_group_id });
      array(leg.events).forEach((event) => {
        events.push({ ...event, leg_id: leg.leg_id, trade_group_id: group.trade_group_id });
      });
    });
  });
  return { groups: array(groups), legs, events };
}

export function buildTradeRecordDownloads(
  payload,
  groups = payload?.trade_groups || [],
  selection = payload?.export_metadata?.selection,
) {
  assertPublicExport(payload);
  assertPublicExport(groups);
  const inputSelection = selection && typeof selection === 'object' ? selection : {};
  const hasTraderFilter = Array.isArray(inputSelection.trader_ids);
  const hasStatusFilter = Array.isArray(inputSelection.statuses);
  const hasReviewFilter = Array.isArray(inputSelection.review_statuses);
  const normalizedSelection = {
    ticker: String(inputSelection.ticker || payload?.ticker || '').toUpperCase(),
    trade_date: String(inputSelection.trade_date || payload?.trade_date || ''),
    trader_ids: hasTraderFilter
      ? [...new Set(inputSelection.trader_ids.map(String))].sort()
      : [...new Set(array(groups).map((group) => group.trader_id).filter(Boolean))].sort(),
    statuses: hasStatusFilter
      ? [...new Set(inputSelection.statuses.map(String))].sort()
      : [...new Set(array(groups).map((group) => group.status).filter(Boolean))].sort(),
    review_statuses: hasReviewFilter
      ? [...new Set(inputSelection.review_statuses.map(String))].sort()
      : [...new Set(array(groups).map((group) => group.review_status).filter(Boolean))].sort(),
    display_only: Boolean(inputSelection.display_only),
  };
  if (normalizedSelection.ticker !== String(payload?.ticker || '').toUpperCase()) {
    throw new Error('export selection ticker must match payload ticker');
  }
  if (normalizedSelection.trade_date !== String(payload?.trade_date || '')) {
    throw new Error('export selection trade_date must match payload trade_date');
  }
  const traderFilter = new Set(normalizedSelection.trader_ids);
  const statusFilter = new Set(normalizedSelection.statuses);
  const reviewFilter = new Set(normalizedSelection.review_statuses);
  const selectedGroups = array(groups).filter((group) => (
    group.underlying === normalizedSelection.ticker
    && group.trade_date === normalizedSelection.trade_date
    && (!hasTraderFilter || traderFilter.size === 0 || traderFilter.has(group.trader_id))
    && (!hasStatusFilter || statusFilter.has(group.status))
    && (!hasReviewFilter || reviewFilter.has(group.review_status))
    && (!normalizedSelection.display_only || group.display_eligible)
  ));
  const selectedContexts = array(payload?.note_contexts).filter((context) => (
    context.underlying === normalizedSelection.ticker
    && context.trade_date === normalizedSelection.trade_date
    && (!hasTraderFilter || traderFilter.size === 0 || traderFilter.has(context.trader_id))
    && (!hasStatusFilter || statusFilter.has(context.status))
    && (!hasReviewFilter || reviewFilter.has(context.review_status))
  ));
  const { legs, events } = flattenTradeRecords(selectedGroups);
  const publicPayload = {
    ...payload,
    trade_groups: selectedGroups,
    note_contexts: selectedContexts,
    counts: {
      ...payload.counts,
      trade_groups_total: selectedGroups.length,
      display_eligible_groups: selectedGroups.filter((group) => group.display_eligible).length,
      reported_stats_eligible_groups: selectedGroups.filter((group) => group.reported_stats_eligible).length,
      calculated_stats_eligible_groups: selectedGroups.filter((group) => group.calculated_stats_eligible).length,
      note_contexts_total: selectedContexts.length,
    },
    export_metadata: {
      ...payload.export_metadata,
      selection: normalizedSelection,
    },
  };
  const groupColumns = [
    'trade_group_id', 'trader_id', 'underlying', 'trade_date', 'direction', 'status',
    'review_status', 'display_eligible', 'reported_stats_eligible',
    'calculated_stats_eligible', 'reported_return_pct', 'calculated_return_pct', 'result_conflict',
  ];
  const groupRows = selectedGroups.map((group) => ({
    ...group,
    reported_return_pct: group.reported_outcome?.return_pct,
    calculated_return_pct: group.calculated_outcome?.return_pct,
  }));
  const legColumns = [
    'leg_id', 'trade_group_id', 'instrument_type', 'position_side', 'option_type', 'strike',
    'expiry', 'expiry_provenance', 'contract_multiplier', 'contract_multiplier_provenance',
  ];
  const eventColumns = [
    'event_id', 'leg_id', 'trade_group_id', 'sequence', 'action', 'occurred_at',
    'time_precision', 'time_incomplete', 'premium', 'quantity', 'fees', 'note',
  ];
  return {
    [payload.export_metadata.json_filename]: `${JSON.stringify(publicPayload, null, 2)}\n`,
    'trade_groups.csv': csv(groupColumns, groupRows),
    'trade_legs.csv': csv(legColumns, legs),
    'trade_events.csv': csv(eventColumns, events),
  };
}

// --- Availability-driven trader contract (plan §3.3) --------------------------
// Availability is computed from the resolved payload BEFORE trader selection:
// 1. match the resolved ticker/date (the payload is the resolved context);
// 2. keep groups allowed by the current status/review-status/eligibility contract;
// 3. derive ordered available trader IDs from those groups and the registry order;
// 4. a registry entry without a displayable group is never a visible option.

export function displayableTradeGroups(payload, filters = {}) {
  const canonical = canonicalizeTradeToolsFilters(filters);
  const statuses = new Set(array(canonical.statuses).length ? canonical.statuses : ['active']);
  const reviewStatuses = new Set(
    array(canonical.reviewStatuses).length ? canonical.reviewStatuses : ['verified'],
  );
  // Shared tools path is always display-only after canonicalize.
  return array(payload?.trade_groups).filter((group) => (
    (!payload?.ticker || group.underlying === payload.ticker)
    && (!payload?.trade_date || group.trade_date === payload.trade_date)
    && statuses.has(group.status)
    && reviewStatuses.has(group.review_status)
    && Boolean(group.display_eligible)
  ));
}

export function deriveAvailableTraders(payload, registryTraders = null, filters = {}) {
  const displayableGroups = displayableTradeGroups(payload, filters);
  const withGroups = new Set(displayableGroups.map((group) => group.trader_id));
  const registry = array(registryTraders ?? payload?.traders);
  const ordered = [...registry]
    .sort((a, b) => (
      (Number(a.sort_order) - Number(b.sort_order))
      || String(a.trader_id).localeCompare(String(b.trader_id))
    ))
    .filter((trader) => withGroups.has(trader.trader_id))
    .map((trader) => trader.trader_id);
  // Defensive: groups referencing a trader missing from the registry keep a
  // deterministic tail order instead of disappearing silently.
  const extras = [...withGroups].filter((id) => !ordered.includes(id)).sort();
  return { availableTraderIds: [...ordered, ...extras], displayableGroups };
}

// Reconcile previous selection against availability. A real context change with
// an empty intersection selects all available traders; within the same context
// an intentional empty selection stays empty. traderIds is the sole visibility
// authority — no focus override remains.
export function reconcileTraderSelection({
  previousSelectedIds = null,
  availableTraderIds = [],
  contextChanged = false,
} = {}) {
  const available = array(availableTraderIds);
  const availableSet = new Set(available);
  if (previousSelectedIds === null || previousSelectedIds === undefined) {
    return { selectedTraderIds: [...available] };
  }
  const intersection = array(previousSelectedIds).filter((id) => availableSet.has(id));
  if (contextChanged && intersection.length === 0) {
    return { selectedTraderIds: [...available] };
  }
  return { selectedTraderIds: intersection };
}

// Trader filter ticker/date may only mirror the resolved workspace context
// (plan §3.1); child filters can never diverge from the resolved market day.
export function mirrorWorkspaceContext(filters = {}, workspace = {}) {
  const workspaceDate = workspace.trade_date || workspace.tradeDate || '';
  return {
    ...filters,
    ticker: workspace.ticker || filters.ticker || '',
    tradeDate: workspaceDate || filters.tradeDate || '',
  };
}

export function filtersMatchWorkspace(filters = {}, workspace = {}) {
  const mirrored = mirrorWorkspaceContext(filters, workspace);
  return (
    mirrored.ticker === String(filters.ticker || '')
    && mirrored.tradeDate === String(filters.tradeDate || '')
  );
}
