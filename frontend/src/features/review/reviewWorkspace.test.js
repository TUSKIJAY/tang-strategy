import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

import {
  compareWorkspaceDays,
  contextToken,
  datesForTicker,
  findDay,
  findDayByKey,
  formatDayHash,
  formatDaySlug,
  groupDatesByMonth,
  listTickers,
  normalizeInteractiveDays,
  normalizeStaticDays,
  parseDayHash,
  preferredTicker,
  resolveInitialWorkspace,
  selectWorkspaceDay,
  switchTicker,
} from './reviewWorkspace.js';
import { reviewHashRoute } from './tradeRecords.js';
import {
  FIXTURE_HASH_CASES,
  FIXTURE_MARKET_DAYS,
  FIXTURE_STATIC_MANIFEST_REVIEWS,
} from './reviewWorkspace.fixtures.js';

const interactiveDays = normalizeInteractiveDays(FIXTURE_MARKET_DAYS);
const staticDays = normalizeStaticDays(FIXTURE_STATIC_MANIFEST_REVIEWS);

test('asymmetric inventory normalizes to 46 SPY + 3 QQQ in canonical order', () => {
  assert.equal(interactiveDays.length, 49);
  assert.equal(interactiveDays.filter((day) => day.ticker === 'SPY').length, 46);
  assert.equal(interactiveDays.filter((day) => day.ticker === 'QQQ').length, 3);
  assert.deepEqual(
    interactiveDays.slice(0, 4).map((day) => `${day.ticker}:${day.trade_date}`),
    ['QQQ:2026-07-17', 'SPY:2026-07-17', 'SPY:2026-07-16', 'SPY:2026-07-15'],
  );
  assert.deepEqual(listTickers(interactiveDays), ['QQQ', 'SPY']);
  assert.equal(preferredTicker(listTickers(interactiveDays)), 'SPY');
  assert.equal(preferredTicker(['QQQ']), 'QQQ');
  assert.equal(preferredTicker([]), '');
  // Static and interactive normalize to the same ticker/date sequence (parity).
  assert.deepEqual(
    staticDays.map((day) => `${day.ticker}:${day.trade_date}`),
    interactiveDays.map((day) => `${day.ticker}:${day.trade_date}`),
  );
});

test('dates group by ticker and month without interleaving', () => {
  const spyDates = datesForTicker(interactiveDays, 'SPY');
  assert.equal(spyDates.length, 46);
  assert.equal(spyDates[0], '2026-07-17');
  assert.equal(spyDates.at(-1), '2026-05-12');
  assert.deepEqual(datesForTicker(interactiveDays, 'QQQ'), ['2026-07-17', '2026-07-14', '2026-07-10']);
  const spyMonths = groupDatesByMonth(interactiveDays, 'SPY');
  assert.deepEqual(spyMonths.map((group) => group.month), ['2026-07', '2026-06', '2026-05']);
  assert.equal(spyMonths[0].dates.length, 12);
  assert.equal(spyMonths[1].dates.length, 21);
  assert.equal(spyMonths[2].dates.length, 13);
  assert.deepEqual(
    groupDatesByMonth(interactiveDays, 'QQQ').map((group) => group.dates),
    [['2026-07-17', '2026-07-14', '2026-07-10']],
  );
});

test('canonical hash formatting and parsing round-trips SPY/QQQ slugs', () => {
  assert.equal(formatDaySlug('SPY', '2026-07-17', 'extended'), 'spy-2026-07-17-extended');
  assert.equal(formatDayHash('QQQ', '2026-07-17', 'extended'), '#qqq-2026-07-17-extended');
  assert.equal(formatDaySlug('SPY', '2026-07-17', 'early_close'), 'spy-2026-07-17-early-close');
  assert.equal(reviewHashRoute('SPY', '2026-07-17', 'extended'), formatDayHash('SPY', '2026-07-17', 'extended'));
  assert.deepEqual(parseDayHash('#spy-2026-07-17-extended'), {
    slug: 'spy-2026-07-17-extended',
    ticker: 'SPY',
    trade_date: '2026-07-17',
    session_mode: 'extended',
  });
  assert.deepEqual(parseDayHash('#/qqq-2026-07-10-extended')?.trade_date, '2026-07-10');
  for (const valid of FIXTURE_HASH_CASES.valid) {
    const parsed = parseDayHash(valid.hash);
    assert.equal(parsed.ticker, valid.ticker);
    assert.equal(parsed.trade_date, valid.trade_date);
    assert.equal(parsed.session_mode, valid.session_mode);
  }
  for (const invalid of FIXTURE_HASH_CASES.invalid) {
    if (invalid.reason === 'empty') continue;
    if (invalid.reason === 'unknown-day') {
      // Well-formed slug that no local day owns: parses, then resolution falls back.
      assert.notEqual(parseDayHash(invalid.hash), null, `${invalid.hash} should parse`);
      continue;
    }
    assert.equal(parseDayHash(invalid.hash), null, `${invalid.hash} (${invalid.reason}) must not parse`);
  }
});

test('default resolution picks SPY newest even though QQQ sorts first', () => {
  const resolved = resolveInitialWorkspace({ days: interactiveDays });
  assert.equal(resolved.ticker, 'SPY');
  assert.equal(resolved.trade_date, '2026-07-17');
  assert.equal(resolved.resolution.kind, 'default-spy');
  assert.equal(resolved.context, 'SPY:2026-07-17:extended');
  const staticResolved = resolveInitialWorkspace({ days: staticDays });
  assert.equal(staticResolved.ticker, 'SPY');
  assert.equal(staticResolved.key, 'spy-2026-07-17-extended');
});

test('SPY-absent inventory falls back to the first ticker deterministically', () => {
  const qqqOnly = interactiveDays.filter((day) => day.ticker === 'QQQ');
  const resolved = resolveInitialWorkspace({ days: qqqOnly });
  assert.equal(resolved.ticker, 'QQQ');
  assert.equal(resolved.trade_date, '2026-07-17');
  assert.equal(resolved.resolution.kind, 'default-first');
  assert.equal(resolveInitialWorkspace({ days: [] }).resolution.kind, 'empty');
});

test('explicit interactive selection and valid static hash both win', () => {
  const qqqDay = interactiveDays.find((day) => day.ticker === 'QQQ' && day.trade_date === '2026-07-14');
  const explicit = resolveInitialWorkspace({ days: interactiveDays, explicitKey: qqqDay.key });
  assert.equal(explicit.ticker, 'QQQ');
  assert.equal(explicit.trade_date, '2026-07-14');
  assert.equal(explicit.resolution.kind, 'explicit');
  const fromHash = resolveInitialWorkspace({ days: staticDays, hash: '#spy-2026-07-17-extended' });
  assert.equal(fromHash.resolution.kind, 'hash');
  assert.equal(fromHash.ticker, 'SPY');
  assert.equal(fromHash.key, 'spy-2026-07-17-extended');
});

test('invalid or missing hashes fall back deterministically and report why', () => {
  const unknownDay = resolveInitialWorkspace({ days: staticDays, hash: '#spy-1999-01-01-extended' });
  assert.equal(unknownDay.resolution.kind, 'fallback');
  assert.equal(unknownDay.resolution.reason, 'unknown-day');
  assert.equal(unknownDay.ticker, 'SPY');
  assert.equal(unknownDay.trade_date, '2026-07-17');
  const malformed = resolveInitialWorkspace({ days: staticDays, hash: '#qqq-2026-07-11' });
  assert.equal(malformed.resolution.reason, 'malformed-hash');
  const wrongCase = resolveInitialWorkspace({ days: staticDays, hash: '#SPY-2026-07-17-EXTENDED' });
  assert.equal(wrongCase.resolution.reason, 'malformed-hash');
  assert.equal(wrongCase.ticker, 'SPY');
  // A fallback never fabricates the requested ticker/date.
  const qqqOnly = staticDays.filter((day) => day.ticker === 'QQQ');
  const noSpy = resolveInitialWorkspace({ days: qqqOnly, hash: '#spy-2026-07-17-extended' });
  assert.equal(noSpy.resolution.reason, 'unknown-day');
  assert.equal(noSpy.ticker, 'QQQ');
});

test('ticker switch keeps the same date only when the target owns it', () => {
  const spy0717 = resolveInitialWorkspace({ days: interactiveDays });
  const sameDate = switchTicker(interactiveDays, spy0717, 'QQQ');
  assert.equal(sameDate.resolution.kind, 'same-date');
  assert.equal(sameDate.trade_date, '2026-07-17');
  assert.equal(sameDate.ticker, 'QQQ');
  assert.equal(sameDate.contextChanged, true);
  const spy0615 = selectWorkspaceDay(interactiveDays, spy0717, { ticker: 'SPY', tradeDate: '2026-06-15' });
  const newest = switchTicker(interactiveDays, spy0615, 'QQQ');
  assert.equal(newest.resolution.kind, 'newest-date');
  assert.equal(newest.trade_date, '2026-07-17');
  assert.equal(newest.resolution.reason, 'date-not-owned');
  const backToSpy = switchTicker(interactiveDays, sameDate, 'SPY');
  assert.equal(backToSpy.resolution.kind, 'same-date');
  assert.equal(backToSpy.trade_date, '2026-07-17');
});

test('missing ticker or same ticker never fabricates a transition', () => {
  const spy0717 = resolveInitialWorkspace({ days: interactiveDays });
  const missing = switchTicker(interactiveDays, spy0717, 'TSLA');
  assert.equal(missing.resolution.kind, 'missing-ticker');
  assert.equal(missing.ticker, 'SPY');
  assert.equal(missing.trade_date, '2026-07-17');
  const unchanged = switchTicker(interactiveDays, spy0717, 'SPY');
  assert.equal(unchanged.resolution.kind, 'unchanged');
  assert.equal(unchanged.contextChanged, false);
});

test('explicit day selection reconciles real days and rejects missing ones', () => {
  const initial = resolveInitialWorkspace({ days: interactiveDays });
  const selected = selectWorkspaceDay(interactiveDays, initial, { ticker: 'QQQ', tradeDate: '2026-07-10' });
  assert.equal(selected.resolution.kind, 'selected');
  assert.equal(selected.ticker, 'QQQ');
  assert.equal(selected.contextChanged, true);
  const byKey = selectWorkspaceDay(interactiveDays, initial, { key: selected.key });
  assert.equal(byKey.trade_date, '2026-07-10');
  const missing = selectWorkspaceDay(interactiveDays, initial, { ticker: 'SPY', tradeDate: '1999-01-01' });
  assert.equal(missing.resolution.kind, 'missing-date');
  assert.equal(missing.ticker, 'SPY');
  assert.equal(missing.trade_date, '2026-07-17');
  const missingKey = selectWorkspaceDay(interactiveDays, initial, { key: '9999' });
  assert.equal(missingKey.resolution.kind, 'missing-date');
  assert.equal(missingKey.context, initial.context);
});

test('context tokens and transitions stay internally consistent', () => {
  const day = findDay(interactiveDays, { ticker: 'QQQ', tradeDate: '2026-07-14' });
  assert.equal(contextToken(day), 'QQQ:2026-07-14:extended');
  assert.equal(findDayByKey(interactiveDays, day.key).trade_date, '2026-07-14');
  const sorted = [...interactiveDays].sort(compareWorkspaceDays);
  assert.equal(sorted[0].ticker, 'QQQ');
  const initial = resolveInitialWorkspace({ days: interactiveDays });
  const reselect = selectWorkspaceDay(interactiveDays, initial, { ticker: 'SPY', tradeDate: '2026-07-17' });
  assert.equal(reselect.contextChanged, false);
  const moved = selectWorkspaceDay(interactiveDays, initial, { ticker: 'SPY', tradeDate: '2026-07-16' });
  assert.equal(moved.contextChanged, true);
  assert.equal(moved.context, 'SPY:2026-07-16:extended');
});

test('fit/overview is owned once by the engine toolbar with accessible labeling', () => {
  const engineSource = readFileSync(new URL('../../kline/kline-engine.js', import.meta.url), 'utf8');
  // Exactly one engine-owned overview control, keyboard-reachable with a label.
  assert.equal(engineSource.match(/data-action="overview"/g)?.length, 1);
  assert.match(engineSource, /data-action="overview"[^>]*aria-label="[^"]+"/);
  assert.match(engineSource, /overview\(\) \{/);
  assert.match(engineSource, /action === 'overview'/);
  // The engine overview action resets the viewport (zoom/follow) to the
  // default window, not just the cursor position.
  assert.match(engineSource, /this\.viewportManager\.reset\(\);\s*\n\s*return this\.setCurrentIndex\(bars\.length - 1, \{ follow: true \}\);/);
  // Embedding the reused engine must not restyle the host application. Theme
  // variables belong to the engine container; the standalone demo may style
  // its own wrapper without a global html/body selector.
  assert.match(engineSource, /\.kline-engine \{\s*\n\s*color-scheme: dark;/);
  assert.doesNotMatch(engineSource, /html, body \{/);
  // The wrapper delegates to the single engine owner instead of re-implementing it.
  const wrapperSource = readFileSync(new URL('../../kline/UnifiedKlineEngine.jsx', import.meta.url), 'utf8');
  assert.match(wrapperSource, /overview: \(\) => engineRef\.current\?\.overview\?\.\(\)/);
  assert.doesNotMatch(wrapperSource, /setHighlightRanges\?\.\(null\)/);
});

test('pages render no visible duplicates of engine-generic controls', () => {
  const reviewSource = readFileSync(new URL('../../pages/ReviewPage.jsx', import.meta.url), 'utf8');
  // The duplicate bottom control bar is gone from interactive Review.
  assert.doesNotMatch(reviewSource, /dr-upload-bar/);
  assert.doesNotMatch(reviewSource, /setTimeframe\('1m'\)/);
  assert.doesNotMatch(reviewSource, /stepBack\(\)/);
  assert.doesNotMatch(reviewSource, /stepForward\(\)/);
  assert.doesNotMatch(reviewSource, /togglePlayback\(\)/);
  // Rescan recomputes in place; Backtest is a distinct navigation action.
  assert.match(reviewSource, /function rescan\(\)/);
  assert.match(reviewSource, /function openBacktest\(\)/);
  assert.match(reviewSource, /onNavigate\?\.\('backtest'\)/);
  assert.doesNotMatch(reviewSource, /onClick=\{runBacktest\}/);
  // The workspace panel owns ticker/date; trader filters mirror it.
  assert.match(reviewSource, /<ReviewContextPanel/);
  assert.match(reviewSource, /context=\{\{ ticker: tradeRecords\.ticker, tradeDate: tradeRecords\.trade_date \}\}/);
  assert.match(reviewSource, /availableTraderIds=\{traderAvailability\.availableTraderIds\}/);
  const backtestSource = readFileSync(new URL('../../pages/BacktestPage.jsx', import.meta.url), 'utf8');
  assert.doesNotMatch(backtestSource, /togglePlayback/);
  assert.doesNotMatch(backtestSource, /stepBack\(\)/);
  assert.doesNotMatch(backtestSource, /overview\(\)/);
  assert.match(backtestSource, /Run latest 10 days/);
  const teachingSource = readFileSync(new URL('../../pages/TeachingPage.jsx', import.meta.url), 'utf8');
  assert.doesNotMatch(teachingSource, /togglePlayback/);
  assert.match(teachingSource, /Reveal full day/);
  const dashboardSource = readFileSync(new URL('../../pages/DashboardPage.jsx', import.meta.url), 'utf8');
  assert.match(dashboardSource, /<ReviewContextPanel/);
  assert.match(dashboardSource, /onNavigate\?\.\('review'\)/);
  assert.doesNotMatch(dashboardSource, /slice\(0, 20\)/);
});

test('context panel exposes programmatic tabs, rail, and selected states', () => {
  const panelSource = readFileSync(new URL('./ReviewContextPanel.jsx', import.meta.url), 'utf8');
  assert.match(panelSource, /role="tablist" aria-label="Ticker workspace"/);
  assert.match(panelSource, /role="tab"/);
  assert.match(panelSource, /aria-selected=\{ticker === value\}/);
  assert.match(panelSource, /aria-pressed=\{date === value\}/);
  assert.match(panelSource, /groupDatesByMonth\(days, ticker\)/);
});

test('shared terminal tokens and all five peer destinations own the application chrome', () => {
  const styles = readFileSync(new URL('../../styles.css', import.meta.url), 'utf8');
  const layout = readFileSync(new URL('../../components/Layout.jsx', import.meta.url), 'utf8');
  const tokens = {
    'surface-app': '#141413',
    'surface-panel': '#1E1E1D',
    'surface-control': '#282827',
    'surface-raised': '#333331',
    'border-subtle': '#3B3B38',
    'border-control': '#74746E',
    'text-primary': '#E8E7E3',
    'text-secondary': '#C9C8C2',
    'text-muted': '#A7A69F',
    accent: '#8B9A6D',
    'accent-ink': '#0F0F0E',
    'status-success': '#4CAF50',
    'status-danger': '#E06B66',
    'status-warning': '#C9A45C',
    'brand-warm': '#A6532A',
  };

  for (const [name, value] of Object.entries(tokens)) {
    assert.match(styles, new RegExp(`--${name}: ${value};`));
  }
  assert.doesNotMatch(styles, /--(?:ink|muted|paper|panel|line):/);
  assert.doesNotMatch(styles, /#f7f1e6|#fffaf0|#fffdf7|#fff7db|#eadcc6/i);
  assert.equal(styles.match(/var\(--brand-warm\)/g)?.length, 1);
  assert.match(styles, /\.brand-mark \{[^}]*background: var\(--brand-warm\);/);

  assert.match(layout, /function NavItem\(/);
  assert.match(layout, /aria-current=\{active === id \? 'page' : undefined\}/);
  assert.match(layout, /<nav aria-label="Primary navigation">/);
  assert.match(layout, /className="nav-bottom-stack"/);
  assert.match(layout, /Icon=\{UsersRound\}/);
  assert.match(layout, /只读检查，编辑需要管理员/);
  assert.doesNotMatch(layout, /RefreshCcw|className="secondary"/);
  assert.equal([...layout.matchAll(/<NavItem\b/g)].length, 2);
  assert.equal([...layout.matchAll(/id: '(dashboard|review|backtest|teaching)'/g)].length, 4);
});

test('static Review consumes shared workspace and trader contracts with one engine control owner', () => {
  const staticSource = readFileSync(new URL('../../pages/StaticReviewsApp.jsx', import.meta.url), 'utf8');
  assert.match(staticSource, /normalizeStaticDays\(manifest\?\.reviews\)/);
  assert.match(staticSource, /resolveInitialWorkspace\(\{ days: workspaceDays, hash: window\.location\.hash \}\)/);
  assert.match(staticSource, /switchTicker\(workspaceDays/);
  assert.match(staticSource, /selectWorkspaceDay\(/);
  assert.match(staticSource, /<ReviewContextPanel/);
  assert.match(staticSource, /deriveAvailableTraders\(tradeRecords, tradeRecords\.traders, tradeFilters\)/);
  assert.match(staticSource, /reconcileTraderSelection\(/);
  assert.match(staticSource, /availableTraderIds=\{traderAvailability\.availableTraderIds\}/);
  assert.match(staticSource, /context=\{\{ ticker: tradeRecords\.ticker, tradeDate: tradeRecords\.trade_date \}\}/);
  assert.doesNotMatch(staticSource, /static-day-list/);
  assert.doesNotMatch(staticSource, /dr-upload-bar/);
  assert.doesNotMatch(staticSource, /setTimeframe\('1m'\)/);
  assert.doesNotMatch(staticSource, /stepBack\(\)/);
  assert.doesNotMatch(staticSource, /stepForward\(\)/);
  assert.doesNotMatch(staticSource, /togglePlayback\(\)/);
  assert.doesNotMatch(staticSource, />Overview</);
  assert.doesNotMatch(staticSource, /AdminTradersPage|\/api\/admin|编辑交易者点位/);
  const styles = readFileSync(new URL('../../styles.css', import.meta.url), 'utf8');
  assert.match(styles, /\.trade-filter-panel \{[^}]*background: var\(--surface-panel\);/);
  assert.match(styles, /\.dr-sidebar \.trade-filter-panel \{ padding: 10px 12px; \}/);
  assert.match(styles, /\.dr-sidebar \.trade-record-list \{ gap: 8px; \}/);
  assert.doesNotMatch(styles, /\.dr-sidebar \.trade-filter-panel,\s*\.dr-sidebar \.trade-group-card/);
  assert.doesNotMatch(styles, /\.dr-sidebar \.trade-context-mirror-item|\.dr-sidebar \.trade-leg/);
  assert.match(styles, /\.review-context-field select \{[^}]*background: var\(--surface-control\);[^}]*border: 1px solid var\(--border-control\);/);
  assert.match(styles, /\.dr-control-group select \{[^}]*background: var\(--surface-control\);[^}]*border: 1px solid var\(--border-control\);/);
});

test('interactive, static, and editor async states expose announcements', () => {
  const reviewSource = readFileSync(new URL('../../pages/ReviewPage.jsx', import.meta.url), 'utf8');
  const staticSource = readFileSync(new URL('../../pages/StaticReviewsApp.jsx', import.meta.url), 'utf8');
  const editorSource = readFileSync(new URL('./TraderPointEditor.jsx', import.meta.url), 'utf8');
  assert.match(reviewSource, /className="dr-error" role="alert"/);
  assert.match(reviewSource, /className="dr-loading" role="status" aria-live="polite"/);
  assert.match(reviewSource, /className="dr-storage-status"[^>]*role="status" aria-live="polite"/);
  assert.match(staticSource, /className="dr-error" role="alert"/);
  assert.match(staticSource, /className="dr-loading" role="status" aria-live="polite"/);
  assert.match(editorSource, /dayState === 'loading'.*role="status" aria-live="polite"/s);
});
