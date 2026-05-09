import { useEffect, useMemo, useRef, useState } from 'react';
import { Api } from '../api/client.js';
import { generateTrendAnnotations, scanSignals, summarizeAnnotations } from '../features/review/scanner.js';
import { setupForAnnotation, summarizeSetups, traceSetups } from '../features/review/lifecycle.js';
import { DAILY_REVIEW_ENGINE_OPTIONS } from '../features/review/engineOptions.js';
import { ReviewSignalList } from '../features/review/ReviewSignalList.jsx';
import { preferredActivationWickStrategy, rthReviewPayload } from '../features/review/session.js';
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
  let start = center - 24;
  let end = center + 24;
  if (setup) {
    start = Math.min(setup.signal_index, setup.entry_index, setup.exit_index);
    end = Math.max(setup.signal_index, setup.entry_index, setup.exit_index);
  } else if (Number.isFinite(Number(annotation?._setup_bar_index))) {
    start = Number(annotation._setup_bar_index);
    end = Number.isFinite(Number(annotation._activation_bar_index))
      ? Number(annotation._activation_bar_index)
      : Number.isFinite(Number(annotation._expire_bar_index))
        ? Number(annotation._expire_bar_index)
        : Number.isFinite(Number(annotation._activation_window_end_bar_index))
          ? Number(annotation._activation_window_end_bar_index)
          : center;
  }
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

function chartAnnotation(annotation) {
  const direction = annotation.direction || '';
  if (annotation.type === 'setup') {
    return {
      ...annotation,
      title: `${direction} 启动`,
      body: `进入 ${annotation._activation_window_bars || 8} 根观察窗口，等待进场确认`,
      style: 'blue',
    };
  }
  if (annotation.type === 'expired') {
    return {
      ...annotation,
      title: `${direction} 过期`,
      body: `观察窗口过期，未触发进场确认线 ${formatPrice(annotation._activation_level)}`,
      style: 'purple',
    };
  }
  if (annotation.type === 'signal') {
    return {
      ...annotation,
      title: `${direction} 进场`,
      body: annotation._activation_time
        ? `启动 ${annotation._setup_time || '?'} -> 进场 ${annotation._activation_time}`
        : annotation.body,
    };
  }
  return annotation;
}

export function ReviewPage({ state, setState }) {
  const engineRef = useRef(null);
  const [review, setReview] = useState(null);
  const [activeSignalId, setActiveSignalId] = useState('');
  const [runVersion, setRunVersion] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const selectedDay = state.marketDays.find((day) => day.id === Number(state.selectedDayId)) || state.marketDays[0];
  const selectedStrategy = state.strategies.find((strategy) => strategy.id === Number(state.selectedStrategyId)) || preferredActivationWickStrategy(state.strategies);

  useEffect(() => {
    if (!selectedDay || !selectedStrategy) return;
    setLoading(true);
    setError('');
    Api.review(selectedDay.id, selectedStrategy.id)
      .then((payload) => {
        setReview(rthReviewPayload(payload));
        setActiveSignalId('');
        setRunVersion((value) => value + 1);
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
  const chartAnnotations1m = useMemo(
    () => computed.annotations1m
      .filter((annotation) => ['setup', 'signal', 'expired'].includes(annotation.type))
      .map(chartAnnotation),
    [computed.annotations1m],
  );
  const chartAnnotations5m = useMemo(() => [], []);
  const stats = sessionStats(bars1m);
  const summary = summarizeAnnotations(computed.annotations1m);
  const setupSummary = summarizeSetups(computed.setups);
  const activeSignal = allAnnotations.find((annotation) => annotation.id === activeSignalId) || computed.annotations1m[0] || computed.annotations5m[0];
  const activeSetup = setupForAnnotation(activeSignal, computed.setups);
  const meta = review?.meta || {};

  function selectSignal(annotation) {
    if (!annotation) return;
    setActiveSignalId(annotation.id);
    const timeframe = annotation.timeframe === '5m' ? '5m' : '1m';
    const targetBars = timeframe === '5m' ? bars5m : bars1m;
    if (!targetBars.length) return;
    const targetIndex = resolveAnnotationIndex(annotation, targetBars);
    engineRef.current?.setHighlightRanges(null);
    if (timeframe === '1m') {
      const setup = setupForAnnotation(annotation, computed.setups);
      const range = setupRange({ ...annotation, bar_index: targetIndex }, setup, targetBars.length);
      engineRef.current?.fitRange({ timeframe, startIndex: range.start, endIndex: range.end });
    }
    engineRef.current?.scrollTo({
      barIndex: targetIndex,
      timeframe,
      ts: annotation.ts,
      time: annotation.t,
      highlight: false,
      center: false,
    });
  }

  function runBacktest() {
    setRunVersion((value) => value + 1);
    setActiveSignalId('');
  }

  function overview() {
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
      annotations_1m: chartAnnotations1m,
      annotations_5m: chartAnnotations5m,
      _trades: computed.setups,
    };
  }, [review, bars1m, bars5m, chartAnnotations1m, chartAnnotations5m, computed.setups]);

  return (
    <section className="dr-shell">
      <div className="dr-app">
        <header className="dr-topbar">
          <div className="dr-title">Daily Review</div>
          <div className="dr-divider" />
          <Stat label="日期" value={meta.date || selectedDay?.trade_date || '--'} />
          <Stat label="进场" value={summary.total} />
          <Stat label="空" value={summary.puts} tone="red" />
          <Stat label="多" value={summary.calls} tone="green" />
          <Stat label="涨跌" value={stats.changePct} tone={String(stats.change).startsWith('-') ? 'red' : 'green'} />
          <Stat label="窗口" value={setupSummary.count} />
          <Stat label="MFE中位" value={setupSummary.medianMfePct == null ? '--' : formatPct(setupSummary.medianMfePct, { ratio: true })} tone="green" />
          <Stat label="持续中位" value={setupSummary.medianDuration == null ? '--' : `${setupSummary.medianDuration}m`} />
          <Stat label="MAE中位" value={setupSummary.medianMaePct == null ? '--' : formatPct(setupSummary.medianMaePct, { ratio: true, negativeSign: true })} tone="red" />
          <div className="dr-strategy-badge">{review?.strategy ? `${review.strategy.name} v${review.strategy.version}` : '未选择策略'}</div>
        </header>

        <aside className="dr-sidebar">
          <div className="dr-sidebar-header">
            <span>提示 {summary.setups || summary.expired ? `(${summary.total} 进场 · ${summary.setups} 启动 / ${summary.expired} 过期)` : `(${allAnnotations.length})`}</span>
            <button type="button" onClick={overview}>总览</button>
          </div>
          <div className="dr-signal-list">
            <ReviewSignalList
              annotations1m={computed.annotations1m}
              annotations5m={computed.annotations5m}
              setups={computed.setups}
              activeSignal={activeSignal}
              onSelect={selectSignal}
              bars1m={bars1m}
              bars5m={bars5m}
              emptyTitle="当前策略/日期没有生成提示。"
              emptyHint="可以切换日期或点击重扫，查看启动、观察、进场或过期。"
            />
          </div>
        </aside>

        <main className="dr-chart-area">
          {error && <div className="dr-error">{error}</div>}
          {loading && <div className="dr-loading">正在从 SQLite 组装复盘...</div>}
          {!loading && enginePayload && (
            <UnifiedKlineEngine
              ref={engineRef}
              payload={enginePayload}
              annotations1m={chartAnnotations1m}
              annotations5m={chartAnnotations5m}
              engineOptions={DAILY_REVIEW_ENGINE_OPTIONS}
              replayStartTime="09:30"
              onAnnotationClick={(annotation) => selectSignal(allAnnotations.find((item) => item.id === annotation.id) || annotation)}
            />
          )}
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
