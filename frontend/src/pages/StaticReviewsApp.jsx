import { useEffect, useMemo, useRef, useState } from 'react';
import { generateTrendAnnotations, scanSignals, summarizeAnnotations } from '../features/review/scanner.js';
import { setupForAnnotation, summarizeSetups, traceSetups } from '../features/review/lifecycle.js';
import { UnifiedKlineEngine } from '../kline/UnifiedKlineEngine.jsx';

function assetPath(path) {
  const base = import.meta.env.BASE_URL || './';
  return `${base.replace(/\/?$/, '/')}${path}`;
}

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

function sessionStats(bars) {
  if (!bars.length) return { change: '--', changePct: '--', high: '--', low: '--' };
  const first = bars[0];
  const last = bars[bars.length - 1];
  const high = Math.max(...bars.map((bar) => Number(bar.H)).filter(Number.isFinite));
  const low = Math.min(...bars.map((bar) => Number(bar.L)).filter(Number.isFinite));
  const pct = Number(first.O) ? (Number(last.C) - Number(first.O)) / Number(first.O) : null;
  return {
    change: signed(Number(last.C) - Number(first.O)),
    changePct: formatPct(pct, { ratio: true }),
    high: formatPrice(high),
    low: formatPrice(low),
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

function resolveAnnotationIndex(annotation, bars) {
  if (!annotation || !bars.length) return 0;
  const rawIndex = Number(annotation.bar_index);
  const targetTs = annotation.ts ? String(annotation.ts) : '';
  const targetTime = String(annotation.t || annotation.time || '').slice(0, 5);
  if (Number.isInteger(rawIndex) && rawIndex >= 0 && rawIndex < bars.length) {
    const indexed = bars[rawIndex];
    if (targetTs && indexed?.ts === targetTs) return rawIndex;
    if (targetTime && String(indexed?.t || '').slice(0, 5) === targetTime) return rawIndex;
    if (!targetTs && !targetTime) return rawIndex;
  }
  if (targetTs || targetTime) {
    const exactIndex = bars.findIndex((bar) => (
      (targetTs && bar?.ts === targetTs) ||
      (targetTime && String(bar?.t || '').slice(0, 5) === targetTime)
    ));
    if (exactIndex >= 0) return exactIndex;
  }
  if (!targetTs && !targetTime) return Math.min(Math.max(rawIndex || 0, 0), bars.length - 1);
  let nearest = 0;
  for (let index = 0; index < bars.length; index += 1) {
    const barTs = String(bars[index]?.ts || '');
    const barTime = String(bars[index]?.t || bars[index]?.time || '').slice(0, 5);
    if (targetTs ? barTs <= targetTs : barTime <= targetTime) nearest = index;
    else break;
  }
  return nearest;
}

function detailItems(annotation) {
  const conditions = annotation._conditions || annotation.checklist || [];
  if (!conditions.length) return [
    { label: 'Static review exported', ok: true, value: annotation.source || annotation.title },
    { label: 'Bar index mapped', ok: true, value: annotation.bar_index },
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

export function StaticReviewsApp() {
  const engineRef = useRef(null);
  const [manifest, setManifest] = useState(null);
  const [selectedDaySlug, setSelectedDaySlug] = useState(() => window.location.hash.replace(/^#\/?/, ''));
  const [selectedStrategySlug, setSelectedStrategySlug] = useState(() => window.localStorage?.getItem('tangStaticReviews:strategy') || '');
  const [review, setReview] = useState(null);
  const [strategyPayload, setStrategyPayload] = useState(null);
  const [activeSignalId, setActiveSignalId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(assetPath('reviews/index.json'))
      .then((response) => {
        if (!response.ok) throw new Error(`Static review manifest not found: ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setManifest(data);
        if (!selectedDaySlug && data.reviews?.[0]?.slug) {
          window.location.hash = data.reviews[0].slug;
          setSelectedDaySlug(data.reviews[0].slug);
        }
        if (!selectedStrategySlug && data.strategies?.[0]?.slug) {
          setSelectedStrategySlug(data.strategies[0].slug);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    const onHash = () => setSelectedDaySlug(window.location.hash.replace(/^#\/?/, ''));
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const selectedItem = manifest?.reviews?.find((item) => item.slug === selectedDaySlug) || manifest?.reviews?.[0] || null;
  const selectedStrategy = manifest?.strategies?.find((item) => item.slug === selectedStrategySlug) || manifest?.strategies?.[0] || null;

  useEffect(() => {
    if (!selectedItem) return;
    setError('');
    setActiveSignalId('');
    fetch(assetPath(`reviews/${selectedItem.file}`))
      .then((response) => {
        if (!response.ok) throw new Error(`Static review payload not found: ${response.status}`);
        return response.json();
      })
      .then((payload) => setReview(payload))
      .catch((err) => setError(err.message));
  }, [selectedItem?.file]);

  useEffect(() => {
    if (!selectedStrategy) return;
    setError('');
    setActiveSignalId('');
    window.localStorage?.setItem('tangStaticReviews:strategy', selectedStrategy.slug);
    fetch(assetPath(`reviews/${selectedStrategy.file}`))
      .then((response) => {
        if (!response.ok) throw new Error(`Static strategy payload not found: ${response.status}`);
        return response.json();
      })
      .then((payload) => setStrategyPayload(payload))
      .catch((err) => setError(err.message));
  }, [selectedStrategy?.file]);

  const bars1m = review?.bars_1m || [];
  const bars5m = review?.bars_5m || [];
  const strategy = strategyPayload?.json || null;
  const computed = useMemo(() => {
    if (!review || !strategy) return { annotations1m: [], annotations5m: [], setups: [] };
    const embedded = review.annotations_1m || [];
    const annotations1m = embedded.length ? embedded : scanSignals({ bars1m, bars5m, strategy });
    const annotations5m = review.annotations_5m?.length ? review.annotations_5m : generateTrendAnnotations(bars5m, strategy);
    const setups = traceSetups(bars1m, annotations1m, strategy?.exit || {});
    return { annotations1m, annotations5m, setups };
  }, [review, bars1m, bars5m, strategy]);

  const allAnnotations = [...computed.annotations1m, ...computed.annotations5m];
  const summary = summarizeAnnotations(computed.annotations1m);
  const setupSummary = summarizeSetups(computed.setups);
  const stats = sessionStats(bars1m);
  const activeSignal = allAnnotations.find((annotation) => annotation.id === activeSignalId) || computed.annotations1m[0] || computed.annotations5m[0];
  const meta = review?.meta || {};

  function chooseReview(item) {
    window.location.hash = item.slug;
    setSelectedDaySlug(item.slug);
  }

  function chooseStrategy(event) {
    setSelectedStrategySlug(event.target.value);
  }

  function selectSignal(annotation) {
    if (!annotation) return;
    setActiveSignalId(annotation.id);
    const setup = setupForAnnotation(annotation, computed.setups);
    const timeframe = annotation.timeframe === '5m' ? '5m' : '1m';
    const targetBars = timeframe === '5m' ? bars5m : bars1m;
    if (!targetBars.length) return;
    const targetIndex = resolveAnnotationIndex(annotation, targetBars);
    if (timeframe === '1m') {
      const range = setupRange({ ...annotation, bar_index: targetIndex }, setup, bars1m.length);
      engineRef.current?.setHighlightRanges({ timeframe: '1m', startIndex: range.start, endIndex: range.end, style: setup ? 'olive' : 'blue' });
    } else {
      engineRef.current?.setHighlightRanges(null);
    }
    engineRef.current?.scrollTo({
      barIndex: targetIndex,
      timeframe,
      ts: annotation.ts,
      time: annotation.t,
      highlight: true,
      center: false,
    });
  }

  function overview() {
    setActiveSignalId('');
    engineRef.current?.overview();
  }

  const enginePayload = review && strategyPayload ? {
    meta: {
      ...(review.meta || {}),
      strategy: {
        id: strategyPayload.id,
        name: strategyPayload.name,
        version: strategyPayload.version,
        slug: strategyPayload.slug,
      },
      initial_timeframe: '1m',
      initial_index_1m: Math.max(0, bars1m.length - 1),
      initial_index_5m: Math.max(0, bars5m.length - 1),
    },
    bars_1m: bars1m,
    bars_5m: bars5m,
    annotations_1m: computed.annotations1m,
    annotations_5m: computed.annotations5m,
  } : null;

  return (
    <div className="static-review-root">
      <section className="dr-shell">
        <div className="dr-app">
          <header className="dr-topbar">
            <div className="dr-title">Static Daily Review</div>
            <div className="dr-divider" />
            <Stat label="Date" value={meta.date || selectedItem?.trade_date || '--'} />
            <Stat label="Signals" value={summary.total} />
            <Stat label="Bear" value={summary.puts} tone="red" />
            <Stat label="Bull" value={summary.calls} tone="green" />
            <Stat label="Chg" value={stats.changePct} tone={String(stats.change).startsWith('-') ? 'red' : 'green'} />
            <Stat label="Setups" value={setupSummary.count} />
            <Stat label="MFE med" value={setupSummary.medianMfePct == null ? '--' : formatPct(setupSummary.medianMfePct, { ratio: true })} tone="green" />
            <Stat label="MAE med" value={setupSummary.medianMaePct == null ? '--' : formatPct(setupSummary.medianMaePct, { ratio: true, negativeSign: true })} tone="red" />
            <div className="dr-strategy-badge">{strategyPayload ? `${strategyPayload.name} v${strategyPayload.version}` : 'Static export'}</div>
          </header>

          <aside className="dr-sidebar">
            <div className="static-day-list">
              {(manifest?.reviews || []).map((item) => (
                <button key={item.slug} type="button" className={item.slug === selectedItem?.slug ? 'active' : ''} onClick={() => chooseReview(item)}>
                  <strong>{item.ticker} {item.trade_date}</strong>
                  <span>{item.bars_1m} / {item.bars_5m} bars</span>
                </button>
              ))}
            </div>
            <div className="static-strategy-picker">
              <label>Strategy</label>
              <select value={selectedStrategy?.slug || ''} onChange={chooseStrategy}>
                {(manifest?.strategies || []).map((item) => (
                  <option key={item.slug} value={item.slug}>{item.name} v{item.version}</option>
                ))}
              </select>
            </div>
            <div className="dr-sidebar-header">
              <span>Signals ({allAnnotations.length})</span>
              <button type="button" onClick={overview}>Overview</button>
            </div>
            <div className="dr-signal-list">
              {!allAnnotations.length && (
                <div className="dr-empty">
                  <div className="dr-empty-icon">K</div>
                  <div>No signals assembled for this strategy/day.</div>
                  <small>Static export loaded; scanner found no review signals.</small>
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
                    <div className="dr-signal-detail">
                      <h5>Trigger checklist</h5>
                      <ul>
                        {detailItems(annotation).map((item, index) => (
                          <li key={index}>
                            <span className={item.ok === false ? 'fail' : 'pass'}>{item.ok === false ? 'x' : 'ok'}</span>
                            <div>
                              <strong>{item.label}</strong>
                              {item.value != null && <small>{String(item.value)}</small>}
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </article>
                );
              })}
            </div>
          </aside>

          <main className="dr-chart-area">
            {error && <div className="dr-error">{error}</div>}
            {!error && !enginePayload && <div className="dr-loading">Loading static review...</div>}
            {enginePayload && (
              <UnifiedKlineEngine
                ref={engineRef}
                payload={enginePayload}
                annotations1m={computed.annotations1m}
                annotations5m={computed.annotations5m}
                replayStartTime="09:30"
                onAnnotationClick={(annotation) => selectSignal(allAnnotations.find((item) => item.id === annotation.id) || annotation)}
              />
            )}
          </main>

          <footer className="dr-upload-bar">
            <div className="dr-action-group">
              <button type="button" onClick={() => engineRef.current?.setTimeframe('1m')} disabled={!review}>1m</button>
              <button type="button" onClick={() => engineRef.current?.setTimeframe('5m')} disabled={!review}>5m</button>
              <button type="button" onClick={() => engineRef.current?.stepBack()} disabled={!review}>Back</button>
              <button type="button" onClick={() => engineRef.current?.stepForward()} disabled={!review}>Step</button>
              <button type="button" onClick={() => engineRef.current?.togglePlayback()} disabled={!review}>Play/Pause</button>
              <button type="button" onClick={overview} disabled={!review}>Overview</button>
            </div>
            <span className="dr-storage-status" data-tone={error ? 'error' : 'ok'}>{error || `Generated ${manifest?.generated_at || ''}`}</span>
          </footer>
        </div>
      </section>
    </div>
  );
}

function Stat({ label, value, tone }) {
  return <div className={`dr-stat ${tone || ''}`}><span>{label}</span><strong>{value}</strong></div>;
}
