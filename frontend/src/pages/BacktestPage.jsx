import { useMemo, useRef, useState } from 'react';
import { Api } from '../api/client.js';
import { runBacktest } from '../features/backtest/backtest.js';
import { generateTrendAnnotations } from '../features/review/scanner.js';
import { UnifiedKlineEngine } from '../kline/UnifiedKlineEngine.jsx';

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

export function BacktestPage({ state }) {
  const engineRef = useRef(null);
  const [results, setResults] = useState([]);
  const [selectedResultId, setSelectedResultId] = useState('');
  const [barsByDay, setBarsByDay] = useState({});
  const [strategy, setStrategy] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  async function run() {
    setRunning(true);
    setError('');
    try {
      const strategyMeta = state.strategies.find((item) => Number(item.id) === Number(state.selectedStrategyId)) || state.strategies[0];
      const loadedStrategy = (await Api.strategy(strategyMeta.id)).json;
      const days = state.marketDays.slice(0, 10);
      const nextBarsByDay = {};
      for (const day of days) {
        nextBarsByDay[`${day.id}:1m`] = (await Api.bars(day.id, '1m')).bars;
        nextBarsByDay[`${day.id}:5m`] = (await Api.bars(day.id, '5m')).bars;
      }
      const nextResults = runBacktest({ days, barsByDay: nextBarsByDay, strategy: loadedStrategy });
      setStrategy(loadedStrategy);
      setBarsByDay(nextBarsByDay);
      setResults(nextResults);
      setSelectedResultId(String(nextResults[0]?.day.id || ''));
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

  const selectedResult = results.find((result) => String(result.day.id) === String(selectedResultId)) || results[0];
  const bars1m = selectedResult ? barsByDay[`${selectedResult.day.id}:1m`] || [] : [];
  const bars5m = selectedResult ? barsByDay[`${selectedResult.day.id}:5m`] || [] : [];
  const annotations1m = selectedResult?.annotations || [];
  const annotations5m = useMemo(() => strategy ? generateTrendAnnotations(bars5m, strategy) : [], [bars5m, strategy]);
  const payload = selectedResult ? {
    meta: {
      ticker: selectedResult.day.ticker,
      date: selectedResult.day.trade_date,
      title: `${selectedResult.day.ticker} ${selectedResult.day.trade_date} Backtest`,
      initial_timeframe: '1m',
      initial_index_1m: Math.max(0, bars1m.length - 1),
      initial_index_5m: Math.max(0, bars5m.length - 1),
    },
    bars_1m: bars1m,
    bars_5m: bars5m,
    annotations_1m: annotations1m,
    annotations_5m: annotations5m,
  } : null;
  const total = results.reduce((sum, item) => sum + item.summary.total, 0);

  function selectResult(result) {
    setSelectedResultId(String(result.day.id));
    engineRef.current?.setHighlightRanges(null);
  }

  function selectAnnotation(annotation) {
    const source = annotations1m.find((item) => item.id === annotation.id) || annotation;
    const timeframe = source.timeframe === '5m' ? '5m' : '1m';
    const targetBars = timeframe === '5m' ? bars5m : bars1m;
    if (!targetBars.length) return;
    const targetIndex = resolveAnnotationIndex(source, targetBars);
    engineRef.current?.scrollTo({
      barIndex: targetIndex,
      timeframe,
      ts: source.ts,
      time: source.t,
      highlight: true,
      center: false,
    });
  }

  return (
    <section className="page engine-page">
      <div className="page-header">
        <p className="eyebrow">Browser backtest</p>
        <h2>Run strategy across imported days</h2>
        <p>Backtest results are rendered in the unified K-line engine with annotations, replay, MA toggles, and single-bar stepping.</p>
      </div>
      {error && <div className="error">{error}</div>}
      <div className="engine-toolbar">
        <button disabled={running || !state.strategies.length || !state.marketDays.length} onClick={run}>{running ? 'Running...' : 'Run latest 10 days'}</button>
        <button disabled={!payload} onClick={() => engineRef.current?.stepBack()}>Back</button>
        <button disabled={!payload} onClick={() => engineRef.current?.stepForward()}>Step</button>
        <button disabled={!payload} onClick={() => engineRef.current?.togglePlayback()}>Play/Pause</button>
        <button disabled={!payload} onClick={() => engineRef.current?.overview()}>Overview</button>
        <div className="metric inline"><span>Total signals</span><strong>{total}</strong></div>
      </div>
      <div className="engine-grid">
        <aside className="engine-side panel">
          <h3>Results</h3>
          {results.map((result) => (
            <button className={String(result.day.id) === String(selectedResult?.day.id) ? 'active' : ''} key={result.day.id} onClick={() => selectResult(result)}>
              <span>{result.day.ticker} {result.day.trade_date}</span>
              <strong>{result.summary.total}</strong>
            </button>
          ))}
        </aside>
        <div className="engine-surface panel">
          {payload ? (
            <UnifiedKlineEngine ref={engineRef} payload={payload} annotations1m={annotations1m} annotations5m={annotations5m} replayOnLoad onAnnotationClick={selectAnnotation} />
          ) : (
            <div className="engine-empty">Run a backtest to load results into the unified K-line engine.</div>
          )}
        </div>
      </div>
    </section>
  );
}
