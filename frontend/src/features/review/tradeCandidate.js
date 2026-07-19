// Pure candidate construction for the trader point editor (plan §3.4).
// No DOM/API side effects: the editor renders these results and `node --test`
// pins them. The server stays authoritative for schema, IDs, timezone,
// projection, drift, and rollback; these helpers never bypass the admin PUT.

function array(value) {
  return Array.isArray(value) ? value : [];
}

export const EDITOR_CONSTANTS = {
  UNDERLYINGS: ['SPY', 'QQQ'],
  DIRECTIONS: ['CALL', 'PUT'],
  RECORD_STATUSES: ['active', 'voided', 'superseded'],
  REVIEW_STATUSES: ['pending', 'verified'],
  EVENT_ACTIONS: ['buy_open', 'buy_add', 'sell_partial', 'sell_close'],
  TIME_PRECISIONS: ['exact', 'minute', 'approximate'],
  FACT_PROVENANCE: ['user_provided', 'legacy_preserved', 'legacy_rule_extract', 'rule_default', 'unknown'],
  NORMALIZATION_METHODS: ['manual_normalization', 'legacy_preserve', 'legacy_rule_extract'],
};

const GROUP_ID_PATTERN = /^tg_[a-z0-9_]{3,124}$/;
const ISO_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;
const EXPLICIT_OFFSET_PATTERN = /(?:Z|[+-]\d{2}:\d{2})$/;

export function nextGroupId(dayDoc, { tradeDate, traderId, underlying }) {
  const prefix = `tg_${String(tradeDate).replaceAll('-', '')}_${traderId}_${String(underlying).toLowerCase()}_`;
  let max = 0;
  array(dayDoc?.trade_groups).forEach((group) => {
    const id = String(group?.trade_group_id || '');
    if (!id.startsWith(prefix)) return;
    const suffix = Number(id.slice(prefix.length));
    if (Number.isInteger(suffix)) max = Math.max(max, suffix);
  });
  return `${prefix}${String(max + 1).padStart(3, '0')}`;
}

export function buildNewEvent(eventId, sequence) {
  return {
    event_id: eventId,
    sequence,
    action: 'buy_open',
    occurred_at: null,
    time_precision: null,
    time_incomplete: true,
    premium: null,
    quantity: null,
    fees: null,
    note: null,
    fact_provenance: {
      occurred_at: 'unknown',
      premium: 'unknown',
      quantity: 'unknown',
      fees: 'unknown',
    },
  };
}

// Keep the timestamp contract atomic. A known timestamp must carry a precision
// and cannot remain incomplete; clearing it restores the canonical unknown-time
// triple. This pure helper is shared by the editor and regression tests so the
// candidate cannot drift from the backend validator's paired-field rules.
export function applyOccurredAt(event, value) {
  const occurredAt = String(value ?? '').trim() || null;
  if (occurredAt === null) {
    return {
      ...event,
      occurred_at: null,
      time_precision: null,
      time_incomplete: true,
      fact_provenance: { ...event.fact_provenance, occurred_at: 'unknown' },
    };
  }
  return {
    ...event,
    occurred_at: occurredAt,
    time_precision: event.time_precision || 'minute',
    time_incomplete: false,
    fact_provenance: { ...event.fact_provenance, occurred_at: 'user_provided' },
  };
}

// Every schema-required field is pinned explicitly, including the group-level
// normalization block (Kimi review-003 foldback) — a new group never carries an
// implicit or partial normalization record.
export function buildNewGroup(dayDoc, { tradeDate, traderId, underlying }) {
  const groupId = nextGroupId(dayDoc, { tradeDate, traderId, underlying });
  const legId = `${groupId}_l1`;
  return {
    trade_group_id: groupId,
    trader_id: traderId,
    underlying,
    trade_date: tradeDate,
    direction: 'CALL',
    status: 'active',
    review_status: 'pending',
    display_eligible: true,
    reported_stats_eligible: false,
    calculated_stats_eligible: false,
    supersedes_trade_group_id: null,
    legs: [
      {
        leg_id: legId,
        instrument_type: 'option',
        position_side: 'long',
        option_type: 'CALL',
        strike: null,
        expiry: tradeDate,
        expiry_provenance: 'rule_default',
        contract_multiplier: 100,
        contract_multiplier_provenance: 'rule_default',
        events: [buildNewEvent(`${legId}_e1`, 1)],
      },
    ],
    reported_outcome: null,
    calculated_outcome: null,
    result_conflict: false,
    notes: [],
    normalization: {
      method: 'manual_normalization',
      source: 'manual_entry',
      source_path: null,
      source_index: null,
      review_flags: [],
    },
  };
}

// Full-day merge: clone the complete loaded day and apply exactly the scoped
// edit; every untouched ticker/trader group, leg, event, outcome, and note
// context is carried by reference, so the preservation diff can prove
// byte-equivalence at the semantic document boundary.
export function mergeGroupIntoDay(dayDoc, groupCandidate) {
  const groups = array(dayDoc?.trade_groups);
  const index = groups.findIndex((group) => group.trade_group_id === groupCandidate.trade_group_id);
  const merged = index >= 0
    ? groups.map((group, i) => (i === index ? groupCandidate : group))
    : [...groups, groupCandidate];
  return { ...dayDoc, trade_groups: merged };
}

// Fail-closed preservation diff: the candidate may add/replace exactly the
// target group and must not touch anything else.
export function preservationDiff(baseDoc, candidateDoc, { targetGroupId }) {
  const problems = [];
  ['schema_version', 'trade_date', 'timezone'].forEach((key) => {
    if (baseDoc?.[key] !== candidateDoc?.[key]) problems.push(`top-level ${key} changed`);
  });
  if (JSON.stringify(baseDoc?.note_contexts || []) !== JSON.stringify(candidateDoc?.note_contexts || [])) {
    problems.push('note_contexts changed');
  }
  const baseGroups = array(baseDoc?.trade_groups);
  const candidateGroups = array(candidateDoc?.trade_groups);
  const baseById = new Map(baseGroups.map((group) => [group.trade_group_id, group]));
  const candidateById = new Map(candidateGroups.map((group) => [group.trade_group_id, group]));
  baseById.forEach((group, id) => {
    if (!candidateById.has(id)) {
      problems.push(`group removed: ${id}`);
      return;
    }
    if (id !== targetGroupId && JSON.stringify(candidateById.get(id)) !== JSON.stringify(group)) {
      problems.push(`untouched group changed: ${id}`);
    }
  });
  const addedGroupIds = [...candidateById.keys()].filter((id) => !baseById.has(id));
  if (addedGroupIds.length > 1 || (addedGroupIds.length === 1 && addedGroupIds[0] !== targetGroupId)) {
    problems.push(`unexpected groups added: ${addedGroupIds.join(', ')}`);
  }
  return {
    ok: problems.length === 0,
    problems,
    addedGroupIds,
    countDelta: candidateGroups.length - baseGroups.length,
    untouchedGroupIds: baseGroups.map((group) => group.trade_group_id).filter((id) => id !== targetGroupId),
  };
}

function isNullOrNumber(value) {
  return value === null || value === undefined || Number.isFinite(Number(value));
}

// Client-side required/format checks mirroring the server contract; the server
// remains authoritative and these checks never replace it.
export function validateGroupForm(group) {
  const errors = {};
  const fail = (path, message) => { errors[path] = message; };
  if (!GROUP_ID_PATTERN.test(String(group?.trade_group_id || ''))) fail('trade_group_id', 'invalid tg_ id');
  if (!EDITOR_CONSTANTS.UNDERLYINGS.includes(group?.underlying)) fail('underlying', 'SPY or QQQ required');
  if (!EDITOR_CONSTANTS.DIRECTIONS.includes(group?.direction)) fail('direction', 'CALL or PUT required');
  if (!ISO_DATE_PATTERN.test(String(group?.trade_date || ''))) fail('trade_date', 'ISO date required');
  if (!EDITOR_CONSTANTS.RECORD_STATUSES.includes(group?.status)) fail('status', 'invalid status');
  if (!EDITOR_CONSTANTS.REVIEW_STATUSES.includes(group?.review_status)) fail('review_status', 'invalid review status');
  if (['voided', 'superseded'].includes(group?.status)
    && (group?.display_eligible || group?.reported_stats_eligible || group?.calculated_stats_eligible)) {
    fail('status', 'voided/superseded groups must clear all eligibility flags');
  }
  if (group?.reported_stats_eligible && !group?.reported_outcome) {
    fail('reported_outcome', 'reported eligibility requires a reported outcome');
  }
  if (group?.calculated_stats_eligible && !group?.calculated_outcome) {
    fail('calculated_outcome', 'calculated eligibility requires a calculated outcome');
  }
  const legs = array(group?.legs);
  if (legs.length !== 1) fail('legs', 'exactly one leg required');
  const leg = legs[0] || {};
  if (leg.option_type !== group?.direction) fail('leg.option_type', 'option type must match direction');
  if (!(leg.strike === null || Number.isFinite(Number(leg.strike)))) fail('leg.strike', 'strike must be a number or empty');
  if (!ISO_DATE_PATTERN.test(String(leg.expiry || ''))) fail('leg.expiry', 'ISO expiry required');
  if (!Number.isFinite(Number(leg.contract_multiplier))) fail('leg.contract_multiplier', 'multiplier required');
  const events = array(leg.events);
  if (!events.length) fail('leg.events', 'at least one event required');
  events.forEach((event, index) => {
    const path = `leg.events[${index}]`;
    if (event.sequence !== index + 1) fail(`${path}.sequence`, 'sequence must be contiguous from 1');
    if (!EDITOR_CONSTANTS.EVENT_ACTIONS.includes(event.action)) fail(`${path}.action`, 'invalid action');
    if (index === 0 && event.action !== 'buy_open') fail(`${path}.action`, 'first event must be buy_open');
    if (event.action === 'buy_open' && index !== 0) fail(`${path}.action`, 'buy_open allowed only once');
    if (typeof event.time_incomplete !== 'boolean') {
      fail(`${path}.time_incomplete`, 'boolean required');
    }
    if (event.occurred_at === null || event.occurred_at === undefined) {
      if (event.time_incomplete !== true || event.time_precision !== null) {
        fail(path, 'missing occurred_at requires time_incomplete=true and time_precision=null');
      }
    } else {
      const text = String(event.occurred_at);
      if (!EXPLICIT_OFFSET_PATTERN.test(text) || Number.isNaN(Date.parse(text))) {
        fail(`${path}.occurred_at`, 'ISO datetime with explicit offset required');
      }
      if (event.time_incomplete !== false) {
        fail(`${path}.time_incomplete`, 'must be false when occurred_at is present');
      }
      if (!EDITOR_CONSTANTS.TIME_PRECISIONS.includes(event.time_precision)) {
        fail(`${path}.time_precision`, 'must describe the known timestamp');
      }
    }
    if (event.time_precision !== null && !EDITOR_CONSTANTS.TIME_PRECISIONS.includes(event.time_precision)) {
      fail(`${path}.time_precision`, 'invalid precision');
    }
    if (!isNullOrNumber(event.premium)) fail(`${path}.premium`, 'number or empty');
    if (!isNullOrNumber(event.quantity)) fail(`${path}.quantity`, 'number or empty');
    if (!isNullOrNumber(event.fees)) fail(`${path}.fees`, 'number or empty');
    Object.values(event.fact_provenance || {}).forEach((provenance) => {
      if (!EDITOR_CONSTANTS.FACT_PROVENANCE.includes(provenance)) {
        fail(`${path}.fact_provenance`, 'invalid provenance');
      }
    });
  });
  const normalization = group?.normalization || {};
  if (!EDITOR_CONSTANTS.NORMALIZATION_METHODS.includes(normalization.method)) {
    fail('normalization.method', 'invalid normalization method');
  }
  if (!String(normalization.source || '').trim()) fail('normalization.source', 'source required');
  const flags = array(normalization.review_flags);
  if (new Set(flags).size !== flags.length) fail('normalization.review_flags', 'flags must be unique');
  return errors;
}
