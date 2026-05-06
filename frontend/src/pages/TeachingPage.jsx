import { useEffect, useMemo, useRef, useState } from 'react';
import { Api } from '../api/client.js';
import { UnifiedKlineEngine } from '../kline/UnifiedKlineEngine.jsx';

export function TeachingPage({ state }) {
  const engineRef = useRef(null);
  const [assets, setAssets] = useState({ rules: null, cases: null, training: null });
  const [marketDayId, setMarketDayId] = useState('');
  const [payload, setPayload] = useState(null);
  const [cutoff, setCutoff] = useState(30);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.allSettled([Api.teaching('rules'), Api.teaching('cases'), Api.teaching('training')]).then((results) => {
      setAssets({
        rules: results[0].status === 'fulfilled' ? results[0].value : null,
        cases: results[1].status === 'fulfilled' ? results[1].value : null,
        training: results[2].status === 'fulfilled' ? results[2].value : null,
      });
      const rejected = results.find((result) => result.status === 'rejected');
      if (rejected) setError('Some teaching assets are not imported yet.');
    });
  }, []);

  useEffect(() => {
    const chosen = marketDayId || state.marketDays[0]?.id;
    if (!chosen) return;
    setMarketDayId(String(chosen));
    Promise.all([Api.bars(chosen, '1m'), Api.bars(chosen, '5m')])
      .then(([one, five]) => {
        setPayload({
          meta: {
            title: `${one.market_day.ticker} ${one.market_day.trade_date} Teaching Replay`,
            ticker: one.market_day.ticker,
            date: one.market_day.trade_date,
            initial_timeframe: '1m',
            initial_index_1m: Math.min(cutoff, Math.max(0, one.bars.length - 1)),
          },
          bars_1m: one.bars,
          bars_5m: five.bars,
          annotations_1m: [],
          annotations_5m: [],
        });
      })
      .catch((err) => setError(err.message));
  }, [marketDayId, state.marketDays]);

  const trainingItems = assets.training?.training || assets.training?.items || [];
  const rules = assets.rules?.rules || [];
  const cases = assets.cases?.cases || [];
  const maxIndex = Math.max(0, (payload?.bars_1m?.length || 1) - 1);
  const effectiveCutoff = Math.min(cutoff, maxIndex);
  const currentBar = payload?.bars_1m?.[effectiveCutoff];
  const teachingHighlights = useMemo(() => payload ? [{ timeframe: '1m', startIndex: Math.max(0, effectiveCutoff - 2), endIndex: effectiveCutoff, style: 'olive' }] : [], [payload, effectiveCutoff]);

  useEffect(() => {
    if (!payload) return;
    engineRef.current?.setRevealCutoff({ timeframe: '1m', barIndex: effectiveCutoff });
    engineRef.current?.setCurrentIndex(effectiveCutoff, { follow: true });
    engineRef.current?.setHighlightRanges(teachingHighlights);
  }, [payload, effectiveCutoff, teachingHighlights]);

  function step(delta) {
    setCutoff((value) => Math.max(0, Math.min(maxIndex, value + delta)));
  }

  function revealAll() {
    setCutoff(maxIndex);
    engineRef.current?.setRevealCutoff(null);
    engineRef.current?.overview();
  }

  return (
    <section className="page engine-page">
      <div className="page-header">
        <p className="eyebrow">Teaching replay</p>
        <h2>Rules, cases, checkpoints, and replay engine</h2>
        <p>The teaching system now uses the same unified K-line engine with reveal cutoff for step-by-step training.</p>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="grid three">
        <Metric label="Rules" value={rules.length} />
        <Metric label="Cases" value={cases.length} />
        <Metric label="Training groups" value={trainingItems.length} />
      </div>
      <div className="engine-toolbar">
        <select value={marketDayId} onChange={(event) => setMarketDayId(event.target.value)}>
          {state.marketDays.slice(0, 80).map((day) => <option key={day.id} value={day.id}>{day.ticker} {day.trade_date}</option>)}
        </select>
        <button disabled={!payload} onClick={() => step(-1)}>Back one bar</button>
        <button disabled={!payload} onClick={() => step(1)}>Advance one bar</button>
        <button disabled={!payload} onClick={revealAll}>Reveal full day</button>
        <button disabled={!payload} onClick={() => engineRef.current?.togglePlayback()}>Play/Pause</button>
        <span className="engine-note">Cutoff #{effectiveCutoff} {currentBar ? `· ${currentBar.t} · C ${currentBar.C}` : ''}</span>
      </div>
      <div className="engine-grid teaching-grid">
        <aside className="engine-side panel">
          <h3>Training prompts</h3>
          {(trainingItems.length ? trainingItems : rules.slice(0, 12)).slice(0, 12).map((item, index) => (
            <article className="teaching-card" key={item.id || item.rule_id || index}>
              <strong>{item.name || item.title || item.id || item.rule_id || `Item ${index + 1}`}</strong>
              <span>{item.goal || item.desc || item.description || item.module || 'Review this rule against the current cutoff bar.'}</span>
            </article>
          ))}
        </aside>
        <div className="engine-surface panel">
          {payload ? (
            <UnifiedKlineEngine ref={engineRef} payload={payload} onReady={(engine) => {
              engine.setRevealCutoff?.({ timeframe: '1m', barIndex: effectiveCutoff });
              engine.setHighlightRanges?.(teachingHighlights);
            }} />
          ) : (
            <div className="engine-empty">Select a market day to load teaching replay.</div>
          )}
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}
