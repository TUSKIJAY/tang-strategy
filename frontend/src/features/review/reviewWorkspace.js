// Pure ticker/date workspace contract for Data, Review, Admin inspection, and
// Static Review. No DOM, API, storage, or timer side effects: every function is
// deterministic data-in/data-out so interactive and static Review share exactly
// one selection contract (plan §3.1, frozen by phase-0-manifest.md).
//
// A workspace day item is normalized as:
//   { key, ticker, trade_date, session_mode, ref }
// where `key` is the interactive market-day id (string) or the static day slug,
// and `ref` is the untouched source entry.

function array(value) {
  return Array.isArray(value) ? value : [];
}

function cleanText(value) {
  return String(value || '').trim();
}

export function compareWorkspaceDays(a, b) {
  // Canonical workspace order: newest date first, ticker ascending within a date.
  if (a.trade_date !== b.trade_date) return a.trade_date < b.trade_date ? 1 : -1;
  return a.ticker < b.ticker ? -1 : 1;
}

function normalizeDay(entry, key) {
  const ticker = cleanText(entry?.ticker).toUpperCase();
  const tradeDate = cleanText(entry?.trade_date);
  if (!ticker || !tradeDate) return null;
  return {
    key,
    ticker,
    trade_date: tradeDate,
    session_mode: cleanText(entry?.session_mode) || 'session',
    ref: entry,
  };
}

export function normalizeInteractiveDays(marketDays = []) {
  return array(marketDays)
    .map((entry) => normalizeDay(entry, cleanText(entry?.id)))
    .filter((day) => day && day.key)
    .sort(compareWorkspaceDays);
}

export function normalizeStaticDays(reviews = []) {
  return array(reviews)
    .map((entry) => normalizeDay(entry, cleanText(entry?.slug)))
    .filter((day) => day && day.key)
    .sort(compareWorkspaceDays);
}

export function listTickers(days = []) {
  return [...new Set(array(days).map((day) => day.ticker))].sort();
}

export function preferredTicker(tickers = []) {
  const ordered = [...array(tickers)].sort();
  return ordered.includes('SPY') ? 'SPY' : ordered[0] || '';
}

export function datesForTicker(days = [], ticker = '') {
  const wanted = cleanText(ticker).toUpperCase();
  return array(days)
    .filter((day) => day.ticker === wanted)
    .map((day) => day.trade_date)
    .sort()
    .reverse();
}

export function groupDatesByMonth(days = [], ticker = '') {
  const dates = datesForTicker(days, ticker);
  const months = [];
  dates.forEach((date) => {
    const month = date.slice(0, 7);
    const current = months[months.length - 1];
    if (current && current.month === month) current.dates.push(date);
    else months.push({ month, dates: [date] });
  });
  return months;
}

export function findDay(days = [], { ticker = '', tradeDate = '' } = {}) {
  const wantedTicker = cleanText(ticker).toUpperCase();
  const wantedDate = cleanText(tradeDate);
  return array(days).find((day) => day.ticker === wantedTicker && day.trade_date === wantedDate) || null;
}

export function findDayByKey(days = [], key = '') {
  const wanted = cleanText(key);
  return array(days).find((day) => day.key === wanted) || null;
}

// --- Canonical static hash contract ------------------------------------------
// `#<ticker>-<date>-<session>` with lowercase ticker and `_`->`-` session, e.g.
// `#spy-2026-07-17-extended`. Compatible with the export manifest slug.

export function formatDaySlug(ticker, tradeDate, sessionMode = 'extended') {
  const session = cleanText(sessionMode).toLowerCase().replaceAll('_', '-') || 'session';
  return `${cleanText(ticker).toLowerCase()}-${cleanText(tradeDate)}-${session}`;
}

export function formatDayHash(ticker, tradeDate, sessionMode = 'extended') {
  return `#${formatDaySlug(ticker, tradeDate, sessionMode)}`;
}

const DAY_HASH_PATTERN = /^([a-z]+)-(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)$/;

export function parseDayHash(hash = '') {
  const text = cleanText(hash).replace(/^#\/?/, '');
  const match = text.match(DAY_HASH_PATTERN);
  if (!match) return null;
  return {
    slug: text,
    ticker: match[1].toUpperCase(),
    trade_date: match[2],
    session_mode: match[3],
  };
}

export function contextToken(day) {
  return day ? `${day.ticker}:${day.trade_date}:${day.session_mode}` : '';
}

function transition(day, resolution, previousContext = '') {
  const context = contextToken(day);
  return {
    day,
    key: day?.key || '',
    ticker: day?.ticker || '',
    trade_date: day?.trade_date || '',
    session_mode: day?.session_mode || '',
    context,
    contextChanged: Boolean(context) && context !== previousContext,
    resolution,
  };
}

// Deterministic initial resolution shared by interactive and static Review:
//   1. an explicit existing selection (interactive day key) wins;
//   2. a valid static hash wins;
//   3. otherwise SPY's newest day when SPY is present;
//   4. otherwise the first available ticker's newest day (deterministic).
// Invalid or missing requests fall back to the same deterministic default and
// report the resolution instead of fabricating a ticker/date.
export function resolveInitialWorkspace({ days = [], explicitKey = '', hash = '' } = {}) {
  const ordered = [...array(days)].sort(compareWorkspaceDays);
  if (!ordered.length) {
    return transition(null, { kind: 'empty', requested: '', reason: 'no-days' });
  }
  const explicit = findDayByKey(ordered, explicitKey);
  if (explicit) {
    return transition(explicit, { kind: 'explicit', requested: explicit.key, reason: '' });
  }
  const hashText = cleanText(hash);
  if (hashText) {
    const parsed = parseDayHash(hashText);
    if (parsed) {
      const matched = findDayByKey(ordered, parsed.slug)
        || findDay(ordered, { ticker: parsed.ticker, tradeDate: parsed.trade_date });
      if (matched) {
        return transition(matched, { kind: 'hash', requested: hashText, reason: '' });
      }
      return transition(defaultDay(ordered), {
        kind: 'fallback', requested: hashText, reason: 'unknown-day',
      });
    }
    return transition(defaultDay(ordered), {
      kind: 'fallback', requested: hashText, reason: 'malformed-hash',
    });
  }
  return transition(defaultDay(ordered), { kind: defaultKind(ordered), requested: '', reason: '' });
}

function defaultDay(days) {
  const ticker = preferredTicker(listTickers(days));
  const day = days.find((item) => item.ticker === ticker) || days[0] || null;
  return day;
}

function defaultKind(days) {
  return preferredTicker(listTickers(days)) === 'SPY' ? 'default-spy' : 'default-first';
}

// Ticker switch: keep the same date only when the target ticker owns it,
// otherwise select the target ticker's newest real date. A ticker without days
// is never fabricated; the current context is kept and reported.
export function switchTicker(days = [], current = {}, nextTicker = '') {
  const ordered = [...array(days)].sort(compareWorkspaceDays);
  const wanted = cleanText(nextTicker).toUpperCase();
  const previousContext = cleanText(current.context) || contextToken(current.day);
  const currentDay = current.day || findDay(ordered, {
    ticker: current.ticker,
    tradeDate: current.trade_date,
  }) || null;
  if (!wanted || wanted === currentDay?.ticker) {
    return transition(currentDay, { kind: 'unchanged', requested: wanted, reason: '' }, previousContext);
  }
  const targetDays = ordered.filter((day) => day.ticker === wanted);
  if (!targetDays.length) {
    return transition(currentDay, { kind: 'missing-ticker', requested: wanted, reason: 'no-days-for-ticker' }, previousContext);
  }
  const sameDate = currentDay
    ? targetDays.find((day) => day.trade_date === currentDay.trade_date)
    : null;
  if (sameDate) {
    return transition(sameDate, { kind: 'same-date', requested: wanted, reason: '' }, previousContext);
  }
  return transition(targetDays[0], { kind: 'newest-date', requested: wanted, reason: 'date-not-owned' }, previousContext);
}

// Explicit day selection (Data -> Review reconciliation or a date-rail click):
// only a real day may be selected; a missing ticker/date keeps the current
// context and is reported instead of silently substituting another day.
export function selectWorkspaceDay(days = [], current = {}, { ticker = '', tradeDate = '', key = '' } = {}) {
  const previousContext = cleanText(current.context) || contextToken(current.day);
  const currentDay = current.day || null;
  const target = key
    ? findDayByKey(days, key)
    : findDay(days, { ticker, tradeDate });
  if (!target) {
    return transition(currentDay, {
      kind: 'missing-date',
      requested: key || `${cleanText(ticker).toUpperCase()}:${cleanText(tradeDate)}`,
      reason: 'no-such-day',
    }, previousContext);
  }
  return transition(target, { kind: 'selected', requested: target.key, reason: '' }, previousContext);
}
