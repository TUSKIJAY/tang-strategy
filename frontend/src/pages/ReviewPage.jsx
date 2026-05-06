import { useEffect, useMemo, useRef, useState } from 'react';
import { Api } from '../api/client.js';
import { generateTrendAnnotations, scanSignals, summarizeAnnotations } from '../features/review/scanner.js';
import { setupForAnnotation, summarizeSetups, traceSetups } from '../features/review/lifecycle.js';
import { UnifiedKlineEngine } from '../kline/UnifiedKlineEngine.jsx';

function formatPrice(value) {
  return Number.isFinite(Number(value)) ? Number(value).toFixed(2) : '--';
}

function formatPct(value, opts = {}) {
  if (!Number.isFinite(Number(value))) return '--';
  const n = Number(value) * (opts.ratio ? 100 : 1);
  const sign = opts.negativeSign ? '-' : n > 0 ? '+' : '';
  return `${sign}${Math.abs(n).toFixed(2)}%`;
}

function signed(value) {
  if (!Number.isFinite(Number(value))) return '--';
  const n = Number(value);
  return `${n > 0 ? '+' : ''}${n.toFixed(2)}`;
}

function pct(from, to) {
  if (!Number.isFinite(Number(from)) || !Number.isFinite(Number(to)) || Number(from) === 0) return '--';
  return formatPct((Number(to) - Number(from)) / Number(from), { ratio: true });
}

function sessionStats(bars) {
  if (!bars.length) return { open: '--', close: '--', change: '--', changePct: '--', high: '--', low: '--', volume: '--' };
  const first = bars[0];
  const last = bars[bars.length - 1];
  const high = Math.max(...bars.map((bar) => Number(bar.H)).filter(Number.isFinite));
  const low = Math.min(...bars.map((bar) => Number(bar.L)).filter(Number.isFinite));
  const volume = bars.reduce((sum, bar) => sum + Number(bar.V || 0), 0);
  return {
    open: formatPrice(first.O),
    close: formatPrice(last.C),
    change: signed(Number(last.C) - Number(first.O)),
    changePct: pct(first.O, last.C),
    high: formatPrice(high),
    low: formatPrice(low),
    volume: volume >= 1_000_000 ? `${(volume / 1_000_000).toFixed(1)}M` : `${Math.round(volume / 1000)}K`,
  };
}

function signalStyle(annotation) {
  if (annotation.type === 'expired') return 'purple';
  if (annotation.type === 'setup') return 'blue';
  if (annotation.direction === 'PUT') return 'red';
  if (annotation.direction === 'CALL') return 'green';
  return 'blue';
}

function directionLabel(annotation) {
  if (annotation.type === 'setup') return 'SETUP';
  if (annotation.type === 'expired') return 'EXP';
  if (annotation.type === 'trend') return '5M';
  return annotation.direction || annotation.type || 'INFO';
}

function setupRange(annotation, setup, barsLength) {
  const center = annotation?.bar_index ?? 0;
  const start = setup ? Math.min(setup.signal_index, setup.entry_index, setup.exit_index) : center - 24;
  const end = setup ? Math.max(setup.signal_index, setup.entry_index, setup.exit_index) : center + 24;
  const pad = Math.max(8, Math.round((end - start + 1) * 0.35));
  return { start: Math.max(0, start - pad), end: Math.min(Math.max(0, barsLength - 1), end + pad) };
}

function detailItems(annotation) {
  const conditions = annotation._conditions || annotation.checklist || [];
  if (!conditions.length) return [
    { label: 'Strategy selected', ok: true, value: annotation.label || annotation.title },
    { label: 'Bar index mapped', ok: true, value: annotation.bar_index },
    { label: 'DB review assembled', ok: true, value: annotation.source },
  ];
  return conditions.map((condition) => ({
    label: condition.label,
    ok: condition.pass ?? condition.ok,
    value: condition.detail ?? condition.value,
  }));
}

function lifecycleText(annotation, setup, bars1m) {
  if (annotation.type === 'setup') return `Candidate at ${annotation.t}; waiting for activation if strategy requires it.`;
  if (annotation.type === 'expired') return `Expired at ${annotation.t}; no activation inside strategy window.`;
  if (!setup) return annotation.body || '';
  const exitBar = bars1m[setup.exit_index];
  const tag = setup.invalidation_type === 'eod' ? 'EOD' : 'Invalidated';
  return `${tag} after ${setup.bars_held} bars -> ${exitBar?.t || '#'} · move ${signed(setup.spy_move)}`;
}

export function ReviewPage({ state, setState }) {
  const engineRef = useRef(null);
  const [review, setReview] = useState(null);
  const [activeSignalId, setActiveSignalId] = useState('');
  const [focusRange, setFocusRange] = useState(null);
  const [runVersion, setRunVersion] = useState(0);
  const [lastRunLabel, setLastRunLabel] = useState('Auto scan pending');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const selectedDay = state.marketDays.find((day) => day.id === Number(state.selectedDayId)) || state.marketDays[0];
  const selectedStrategy = state.strategies.find((strategy) => strategy.id === Number(state.selectedStrategyId)) || state.strategies[0];

  useEffect(() => {
    if (!selectedDay || !selectedStrategy) return;
    setLoading(true);
    setError('');
    Api.review(selectedDay.id, selectedStrategy.id)
      .then((payload) => {
        setReview(payload);
        setActiveSignalId('');
        setFocusRange(null);
        setRunVersion((value) => value + 1);
        setLastRunLabel('Auto assembled from SQLite');
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [selectedDay?.id, selectedStrategy?.id]);

  const bars1m = review?.bars_1m || [];
  const bars5m = review?.bars_5m || [];
  const strategy = review?.strategy?.json || null;
  const computed = useMemo(() => {
    if (!review) return { annotations1m: [], annotations5m: [], setups: [] };
    const embedded = review.annotations_1m || [];
    const annotations1m = embedded.length ? embedded : scanSignals({ bars1m, bars5m, strategy });
    const annotations5m = review.annotations_5m?.length ? review.annotations_5m : generateTrendAnnotations(bars5m, strategy);
    const setups = traceSetups(bars1m, annotations1m, strategy?.exit || {});
    return { annotations1m, annotations5m, setups };
  }, [review, bars1m, bars5m, strategy, runVersion]);

  const visibleAnnotations = computed.annotations1m;
  const allAnnotations = [...computed.annotations1m, ...computed.annotations5m];
  const stats = sessionStats(bars1m);
  const summary = summarizeAnnotations(computed.annotations1m);
  const setupSummary = summarizeSetups(computed.setups);
  const activeSignal = allAnnotations.find((annotation) => annotation.id === activeSignalId) || computed.annotations1m[0] || computed.annotations5m[0];
  const activeSetup = setupForAnnotation(activeSignal, computed.setups);
  const meta = review?.meta || {};

  function selectSignal(annotation) {
    if (!annotation) return;
    setActiveSignalId(annotation.id);
    const setup = setupForAnnotation(annotation, computed.setups);
    const timeframe = annotation.timeframe || '1m';
    if (timeframe === '1m') {
      const range = setupRange(annotation, setup, bars1m.length);
      setFocusRange(range);
      engineRef.current?.setTimeframe('1m');
      engineRef.current?.setHighlightRanges({ timeframe: '1m', startIndex: range.start, endIndex: range.end, style: setup ? 'olive' : 'blue' });
    }
    engineRef.current?.scrollTo({ barIndex: annotation.bar_index, timeframe, highlight: true, center: true });
  }

  function runBacktest() {
    setRunVersion((value) => value + 1);
    setLastRunLabel(`Backtest run ${new Date().toLocaleTimeString()}`);
    setFocusRange(null);
    setActiveSignalId('');
  }

  function overview() {
    setFocusRange(null);
    setActiveSignalId('');
    engineRef.current?.overview();
  }

  const enginePayload = useMemo(() => {
    if (!review) return null;
    return {
      meta: {
        ...(review.meta || {}),
        initial_timeframe: '1m',
        initial_index_1m: Math.max(0, bars1m.length - 1),
        initial_index_5m: Math.max(0, bars5m.length - 1),
      },
      bars_1m: bars1m,
      bars_5m: bars5m,
      annotations_1m: computed.annotations1m,
      annotations_5m: computed.annotations5m,
    };
  }, [review, bars1m, bars5m, computed.annotations1m, computed.annotations5m]);

  return (
    <section className="dr-shell">
      <div className="dr-app">
        <header className="dr-topbar">
          <div className="dr-title">Daily Review</div>
          <div className="dr-divider" />
          <Stat label="Date" value={meta.date || selectedDay?.trade_date || '--'} />
          <Stat label="Signals" value={summary.total} />
          <Stat label="Bear" value={summary.puts} tone="red" />
          <Stat label="Bull" value={summary.calls} tone="green" />
          <Stat label="Chg" value={stats.changePct} tone={String(stats.change).startsWith('-') ? 'red' : 'green'} />
          <Stat label="Setups" value={setupSummary.count} />
          <Stat label="MFE med" value={setupSummary.medianMfePct == null ? '--' : formatPct(setupSummary.medianMfePct, { ratio: true })} tone="green" />
          <Stat label="Dur med" value={setupSummary.medianDuration == null ? '--' : `${setupSummary.medianDuration}m`} />
          <Stat label="MAE med" value={setupSummary.medianMaePct == null ? '--' : formatPct(setupSummary.medianMaePct, { ratio: true, negativeSign: true })} tone="red" />
          <div className="dr-strategy-badge">{review?.strategy ? `${review.strategy.name} v${review.strategy.version}` : 'No Strategy'}</div>
        </header>

        <aside className="dr-sidebar">
          <div className="dr-sidebar-header">
            <span>Signals {summary.setups || summary.expired ? `(${summary.total} signals · ${summary.setups} setup / ${summary.expired} expired)` : `(${allAnnotations.length})`}</span>
            <button type="button" onClick={overview}>Overview</button>
          </div>
          <div className="dr-signal-list">
            {!allAnnotations.length && (
              <div className="dr-empty">
                <div className="dr-empty-icon">K</div>
                <div>No signals assembled for this strategy/day.</div>
                <small>Use Backtest to rerun browser scan from SQLite bars.</small>
              </div>
            )}
            {allAnnotations.map((annotation) => {
              const active = annotation.id === activeSignal?.id;
              const setup = setupForAnnotation(annotation, computed.setups);
              return (
                <article key={annotation.id} className={`dr-signal-card ${active ? 'active expanded' : ''}`} data-style={signalStyle(annotation)} onClick={() => selectSignal(annotation)}>
                  <div className="dr-signal-time">{annotation.t || annotation.ts || `#${annotation.bar_index}`} · {annotation.timeframe || '1m'}</div>
                  <div className="dr-signal-title">
                    <span className={`dr-signal-dir ${annotation.direction === 'PUT' ? 'put' : 'call'}`}>{directionLabel(annotation)}</span>
                    {annotation.title || annotation.label || 'Strategy signal'}
                  </div>
                  <div className="dr-signal-meta">bar #{annotation.bar_index} · {lifecycleText(annotation, setup, bars1m)}</div>
                  {setup && (
                    <div className={`dr-trade-result ${setup.invalidation_type === 'eod' ? 'eod' : setup.spy_move >= 0 ? 'favorable' : 'adverse'}`}>
                      <span className={setup.spy_move >= 0 ? 'positive' : 'negative'}>{signed(setup.spy_move)}</span>
                      <span>{setup.invalidation_type === 'eod' ? 'EOD' : 'Signal invalidated'} · {setup.bars_held}m · → {bars1m[setup.exit_index]?.t || '?'}</span>
                    </div>
                  )}
                  <div className="dr-signal-toggle">Details</div>
                  <div className="dr-signal-detail">
                    <h5>Trigger checklist</h5>
                    <ul>
                      {detailItems(annotation).map((item, index) => (
                        <li key={index}>
                          <span className={item.ok === false ? 'fail' : 'pass'}>{item.ok === false ? '×' : '✓'}</span>
                          <div>
                            <strong>{item.label}</strong>
                            {item.value != null && <small>{String(item.value)}</small>}
                          </div>
                        </li>
                      ))}
                    </ul>
                    {(annotation._invalidation || setup) && (
                      <div className="dr-detail-grid">
                        <h5>Invalidation / excursion</h5>
                        {annotation._invalidation && <><span>Rule</span><strong>{annotation._invalidation.human || annotation._invalidation.rule}</strong></>}
                        {annotation._invalidation && <><span>Line</span><strong>{annotation._invalidation.line?.toUpperCase()} {formatPrice(annotation._invalidation.initial_value)}</strong></>}
                        {setup && <><span>MFE</span><strong className="good">+{formatPrice(setup.mfe)} ({formatPct(setup.mfe_pct, { ratio: true })})</strong></>}
                        {setup && <><span>MAE</span><strong className="bad">-{formatPrice(setup.mae)} ({formatPct(setup.mae_pct, { ratio: true, negativeSign: true })})</strong></>}
                        {setup && <><span>Entry</span><strong>{bars1m[setup.entry_index]?.t || '?'} @ {formatPrice(setup.entry_price)}</strong></>}
                        {setup && <><span>Exit</span><strong>{bars1m[setup.exit_index]?.t || '?'} @ {formatPrice(setup.exit_price)}</strong></>}
                      </div>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        </aside>

        <main className="dr-chart-area">
          {error && <div className="dr-error">{error}</div>}
          {loading && <div className="dr-loading">Assembling daily review from SQLite...</div>}
          {!loading && enginePayload && (
            <UnifiedKlineEngine
              ref={engineRef}
              payload={enginePayload}
              annotations1m={computed.annotations1m}
              annotations5m={computed.annotations5m}
              onAnnotationClick={(annotation) => selectSignal(allAnnotations.find((item) => item.id === annotation.id) || annotation)}
            />
          )}
          <div className="dr-review-panel">
            <div><span>Range</span><strong>{stats.low} / {stats.high}</strong></div>
            <div><span>1m / 5m Bars</span><strong>{bars1m.length} / {bars5m.length}</strong></div>
            <div><span>Lifecycle</span><strong>{setupSummary.count} setups · {setupSummary.invalidated} invalidated · {setupSummary.eod} EOD</strong></div>
            <div><span>Run status</span><strong>{lastRunLabel}</strong></div>
          </div>
        </main>

        <footer className="dr-upload-bar">
          <div className="dr-control-group">
            <label>Market day</label>
            <select value={selectedDay?.id || ''} onChange={(event) => setState((prev) => ({ ...prev, selectedDayId: event.target.value }))}>
              {state.marketDays.map((day) => <option key={day.id} value={day.id}>{day.ticker} {day.trade_date} · {day.session_mode} (live_extended)</option>)}
            </select>
          </div>
          <div className="dr-upload-divider" />
          <div className="dr-control-group">
            <label>Strategy</label>
            <select value={selectedStrategy?.id || ''} onChange={(event) => setState((prev) => ({ ...prev, selectedStrategyId: event.target.value }))}>
              {state.strategies.map((item) => <option key={item.id} value={item.id}>{item.name} v{item.version}</option>)}
            </select>
          </div>
          <div className="dr-upload-divider" />
          <div className="dr-action-group">
            <button type="button" onClick={() => engineRef.current?.setTimeframe('1m')}>1m</button>
            <button type="button" onClick={() => engineRef.current?.setTimeframe('5m')}>5m</button>
            <button type="button" onClick={() => engineRef.current?.stepBack()} disabled={!review || loading}>Back</button>
            <button type="button" onClick={() => engineRef.current?.stepForward()} disabled={!review || loading}>Step</button>
            <button type="button" onClick={() => engineRef.current?.togglePlayback()} disabled={!review || loading}>Play/Pause</button>
            <button type="button" onClick={runBacktest} disabled={!review || loading}>Backtest</button>
            <button type="button" onClick={runBacktest} disabled={!review || loading}>Rescan</button>
            <button type="button" onClick={overview}>Overview</button>
          </div>
          <span className="dr-storage-status" data-tone={error ? 'error' : 'ok'}>{error ? 'Assembly failed' : 'SQLite review assembled automatically'}</span>
        </footer>
      </div>
    </section>
  );
}

function Stat({ label, value, tone }) {
  return <div className={`dr-stat ${tone || ''}`}><span>{label}</span><strong>{value}</strong></div>;
}
