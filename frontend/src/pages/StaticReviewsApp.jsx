import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { generateTrendAnnotations, scanSignals, summarizeAnnotations } from '../features/review/scanner.js';
import { setupForAnnotation, summarizeSetups, traceSetups } from '../features/review/lifecycle.js';
import { DAILY_REVIEW_ENGINE_OPTIONS } from '../features/review/engineOptions.js';
import { ReviewContextPanel } from '../features/review/ReviewContextPanel.jsx';
import { ReviewSignalList } from '../features/review/ReviewSignalList.jsx';
import { TradeExportControls } from '../features/review/TradeExportControls.jsx';
import { TraderFilters } from '../features/review/TraderFilters.jsx';
import { TraderTradeList } from '../features/review/TraderTradeList.jsx';
import {
  buildTradeRecordAnnotations,
  deriveAvailableTraders,
  filterTradeGroups,
  initialTradeRecordFilters,
  reconcileTraderSelection,
} from '../features/review/tradeRecords.js';
import {
  findDayByKey,
  normalizeStaticDays,
  resolveInitialWorkspace,
  selectWorkspaceDay,
  switchTicker,
} from '../features/review/reviewWorkspace.js';
import {
  buildBarIndexMap,
  preferredActivationWickStrategy,
  remapAnnotationIndexes,
  remapSetupIndexes,
  reviewPayloadForWindow,
} from '../features/review/session.js';
import { UnifiedKlineEngine } from '../kline/UnifiedKlineEngine.jsx';

const EXTENDED_K_STORAGE_KEY = 'tangReview:extendedKBars';

function loadExtendedKBars() {
  try {
    return window.localStorage?.getItem(EXTENDED_K_STORAGE_KEY) === 'true';
  } catch (_) {
    return false;
  }
}

function assetPath(path, cacheKey = '') {
  const base = import.meta.env.BASE_URL || './';
  const suffix = cacheKey ? `${path.includes('?') ? '&' : '?'}v=${encodeURIComponent(cacheKey)}` : '';
  return `${base.replace(/\/?$/, '/')}${path}${suffix}`;
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

export function StaticReviewsApp() {
  const engineRef = useRef(null);
  const utilityPanelId = useId();
  const utilityTriggerRef = useRef(null);
  const [utilityOpen, setUtilityOpen] = useState(false);
  const [manifest, setManifest] = useState(null);
  const [selectedDaySlug, setSelectedDaySlug] = useState(() => window.location.hash.replace(/^#\/?/, ''));
  const [routeNotice, setRouteNotice] = useState('');
  const [selectedStrategySlug, setSelectedStrategySlug] = useState('');
  const [review, setReview] = useState(null);
  const [strategyPayload, setStrategyPayload] = useState(null);
  const [activeSignalId, setActiveSignalId] = useState('');
  const [activeTradeGroupId, setActiveTradeGroupId] = useState('');
  const [tradeFilters, setTradeFilters] = useState(() => initialTradeRecordFilters());
  const [error, setError] = useState('');
  const [showExtendedKBars, setShowExtendedKBars] = useState(loadExtendedKBars);

  useEffect(() => {
    try {
      window.localStorage?.setItem(EXTENDED_K_STORAGE_KEY, showExtendedKBars ? 'true' : 'false');
    } catch (_) {
      // localStorage can be unavailable in restricted browser contexts.
    }
  }, [showExtendedKBars]);

  useEffect(() => {
    setActiveSignalId('');
    setActiveTradeGroupId('');
    engineRef.current?.overview();
  }, [showExtendedKBars]);

  useEffect(() => {
    fetch(assetPath('reviews/index.json', Date.now()), { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error(`Static review manifest not found: ${response.status}`);
        return response.json();
      })
      .then((data) => {
        setManifest(data);
        if (!selectedStrategySlug && data.strategies?.length) {
          setSelectedStrategySlug(preferredActivationWickStrategy(data.strategies)?.slug || data.strategies[0].slug);
        }
      })
      .catch((err) => setError(err.message));
  }, []);

  const workspaceDays = useMemo(() => normalizeStaticDays(manifest?.reviews), [manifest?.reviews]);

  useEffect(() => {
    if (!workspaceDays.length) return undefined;
    const onHash = () => {
      const next = resolveInitialWorkspace({ days: workspaceDays, hash: window.location.hash });
      if (!next.day) return;
      setSelectedDaySlug(next.key);
      setRouteNotice(next.resolution.kind === 'fallback'
        ? `链接未匹配本地静态数据（${next.resolution.reason}），已回到 ${next.ticker} ${next.trade_date}。`
        : '');
      const canonicalHash = `#${next.key}`;
      if (window.location.hash !== canonicalHash) {
        window.history.replaceState(null, '', canonicalHash);
      }
    };
    onHash();
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, [workspaceDays]);

  const selectedWorkspaceDay = useMemo(
    () => findDayByKey(workspaceDays, selectedDaySlug),
    [workspaceDays, selectedDaySlug],
  );
  const workspace = selectedWorkspaceDay ? {
    ticker: selectedWorkspaceDay.ticker,
    trade_date: selectedWorkspaceDay.trade_date,
    session_mode: selectedWorkspaceDay.session_mode,
  } : { ticker: '', trade_date: '', session_mode: '' };
  const selectedItem = selectedWorkspaceDay?.ref || null;
  const selectedStrategy = manifest?.strategies?.find((item) => item.slug === selectedStrategySlug) || manifest?.strategies?.[0] || null;

  useEffect(() => {
    if (!selectedItem) return;
    setError('');
    setReview(null);
    setActiveSignalId('');
    setActiveTradeGroupId('');
    fetch(assetPath(`reviews/${selectedItem.file}`, manifest?.generated_at || Date.now()), { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error(`Static review payload not found: ${response.status}`);
        return response.json();
      })
      .then((payload) => {
        setReview(payload);
        const records = payload.trade_records;
        if (records) {
          const { availableTraderIds } = deriveAvailableTraders(records, records.traders);
          setTradeFilters((previous) => {
            const contextChanged = !previous
              || previous.ticker !== records.ticker
              || previous.tradeDate !== records.trade_date;
            const reconciled = reconcileTraderSelection({
              previousSelectedIds: previous?.traderIds ?? null,
              availableTraderIds,
              contextChanged,
            });
            return {
              ...initialTradeRecordFilters(records.traders),
              ticker: records.ticker,
              tradeDate: records.trade_date,
              traderIds: reconciled.selectedTraderIds,
            };
          });
        } else {
          setTradeFilters(initialTradeRecordFilters());
        }
      })
      .catch((err) => setError(err.message));
  }, [selectedItem?.file]);

  useEffect(() => {
    if (!selectedStrategy) return;
    setError('');
    setActiveSignalId('');
    window.localStorage?.setItem('tangStaticReviews:strategy', selectedStrategy.slug);
    fetch(assetPath(`reviews/${selectedStrategy.file}`, manifest?.generated_at || Date.now()), { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) throw new Error(`Static strategy payload not found: ${response.status}`);
        return response.json();
      })
      .then((payload) => setStrategyPayload(payload))
      .catch((err) => setError(err.message));
  }, [selectedStrategy?.file]);

  const scanReview = useMemo(() => reviewPayloadForWindow(review, 'rth'), [review]);
  const displayReview = useMemo(
    () => reviewPayloadForWindow(review, showExtendedKBars ? 'extended_k' : 'rth'),
    [review, showExtendedKBars],
  );
  const scanBars1m = scanReview?.bars_1m || [];
  const scanBars5m = scanReview?.bars_5m || [];
  const bars1m = displayReview?.bars_1m || [];
  const bars5m = displayReview?.bars_5m || [];
  const strategy = strategyPayload?.json || null;
  const computed = useMemo(() => {
    if (!scanReview || !strategy) return { annotations1m: [], annotations5m: [], setups: [] };
    const embedded = scanReview.annotations_1m || [];
    const annotations1m = embedded.length ? embedded : scanSignals({ bars1m: scanBars1m, bars5m: scanBars5m, strategy });
    const annotations5m = scanReview.annotations_5m?.length ? scanReview.annotations_5m : generateTrendAnnotations(scanBars5m, strategy);
    const setups = traceSetups(scanBars1m, annotations1m, strategy?.exit || {});
    return { annotations1m, annotations5m, setups };
  }, [scanReview, scanBars1m, scanBars5m, strategy]);

  const displayIndexMap1m = useMemo(() => buildBarIndexMap(scanBars1m, bars1m), [scanBars1m, bars1m]);
  const displayIndexMap5m = useMemo(() => buildBarIndexMap(scanBars5m, bars5m), [scanBars5m, bars5m]);
  const displayComputed = useMemo(() => ({
    annotations1m: remapAnnotationIndexes(computed.annotations1m, displayIndexMap1m, '1m'),
    annotations5m: remapAnnotationIndexes(computed.annotations5m, displayIndexMap5m, '5m'),
    setups: remapSetupIndexes(computed.setups, displayIndexMap1m),
  }), [computed, displayIndexMap1m, displayIndexMap5m]);

  const allAnnotations = [...displayComputed.annotations1m, ...displayComputed.annotations5m];
  const chartAnnotations1m = useMemo(
    () => displayComputed.annotations1m
      .filter((annotation) => ['setup', 'signal', 'expired'].includes(annotation.type))
      .map(chartAnnotation),
    [displayComputed.annotations1m],
  );
  const tradeRecords = displayReview?.trade_records || null;
  const traderAvailability = useMemo(
    () => (tradeRecords
      ? deriveAvailableTraders(tradeRecords, tradeRecords.traders, tradeFilters)
      : { availableTraderIds: [], displayableGroups: [] }),
    [tradeRecords, tradeFilters],
  );
  useEffect(() => {
    setTradeFilters((previous) => {
      if (!previous) return previous;
      const reconciled = reconcileTraderSelection({
        previousSelectedIds: previous.traderIds,
        availableTraderIds: traderAvailability.availableTraderIds,
        contextChanged: false,
      });
      const sameSelection = reconciled.selectedTraderIds.join(',') === (previous.traderIds || []).join(',');
      if (sameSelection) return previous;
      return { ...previous, traderIds: reconciled.selectedTraderIds };
    });
  }, [tradeRecords, traderAvailability.availableTraderIds]);
  const filteredTradeGroups = useMemo(
    () => filterTradeGroups(tradeRecords, tradeFilters),
    [tradeRecords, tradeFilters],
  );
  const tradeRecordAnnotations1m = useMemo(
    () => buildTradeRecordAnnotations(filteredTradeGroups, tradeRecords?.traders, bars1m),
    [filteredTradeGroups, tradeRecords?.traders, bars1m],
  );
  const engineAnnotations1m = useMemo(
    () => [...chartAnnotations1m, ...tradeRecordAnnotations1m],
    [chartAnnotations1m, tradeRecordAnnotations1m],
  );
  const chartAnnotations5m = useMemo(() => [], []);
  const summary = summarizeAnnotations(computed.annotations1m);
  const setupSummary = summarizeSetups(computed.setups);
  const stats = sessionStats(bars1m);
  const activeSignal = allAnnotations.find((annotation) => annotation.id === activeSignalId) || displayComputed.annotations1m[0] || displayComputed.annotations5m[0];
  const meta = displayReview?.meta || {};

  function commitWorkspace(next) {
    if (!next?.day) return;
    setSelectedDaySlug(next.key);
    setRouteNotice('');
    const nextHash = `#${next.key}`;
    if (window.location.hash !== nextHash) window.location.hash = next.key;
  }

  function chooseTicker(ticker) {
    commitWorkspace(switchTicker(workspaceDays, { day: selectedWorkspaceDay }, ticker));
  }

  function chooseDate(tradeDate) {
    commitWorkspace(selectWorkspaceDay(
      workspaceDays,
      { day: selectedWorkspaceDay },
      { ticker: workspace.ticker, tradeDate },
    ));
  }

  function chooseStrategy(event) {
    setSelectedStrategySlug(event.target.value);
  }

  function selectSignal(annotation) {
    if (!annotation) return;
    setActiveSignalId(annotation.id);
    setActiveTradeGroupId('');
    const timeframe = annotation.timeframe === '5m' ? '5m' : '1m';
    const targetBars = timeframe === '5m' ? bars5m : bars1m;
    if (!targetBars.length) return;
    const targetIndex = resolveAnnotationIndex(annotation, targetBars);
    engineRef.current?.setHighlightRanges(null);
    if (timeframe === '1m') {
      const setup = setupForAnnotation(annotation, displayComputed.setups);
      const range = setupRange({ ...annotation, bar_index: targetIndex }, setup, targetBars.length);
      engineRef.current?.fitRange({ timeframe, startIndex: range.start, endIndex: range.end });
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

  function selectTradeGroup(group) {
    if (!group) return;
    const annotation = tradeRecordAnnotations1m.find((item) => item.trade_group_ids?.includes(group.trade_group_id));
    setActiveTradeGroupId(group.trade_group_id);
    setActiveSignalId('');
    if (!annotation) return;
    const targetIndex = resolveAnnotationIndex(annotation, bars1m);
    engineRef.current?.setHighlightRanges({
      timeframe: '1m',
      startIndex: targetIndex,
      endIndex: targetIndex,
      style: 'marker',
    });
    if (bars1m.length) {
      const radius = targetIndex < 16 ? 12 : 10;
      engineRef.current?.fitRange({
        timeframe: '1m',
        startIndex: Math.max(0, targetIndex - radius),
        endIndex: Math.min(bars1m.length - 1, targetIndex + radius),
        paddingRatio: 0,
        minPadding: 0,
      });
    }
    engineRef.current?.scrollTo({
      barIndex: targetIndex,
      timeframe: '1m',
      ts: annotation.ts,
      time: annotation.t,
      highlight: true,
      center: true,
    });
  }

  const enginePayload = useMemo(() => {
    if (!displayReview || !strategyPayload) return null;
    return {
      meta: {
        ...(displayReview.meta || {}),
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
      annotations_1m: engineAnnotations1m,
      annotations_5m: chartAnnotations5m,
      _trades: displayComputed.setups,
    };
  }, [displayReview, strategyPayload, bars1m, bars5m, engineAnnotations1m, chartAnnotations5m, displayComputed.setups]);

  return (
    <div className="static-review-root">
      <section className="dr-shell">
        <div className="dr-app dr-app--no-upload">
          <header className="dr-topbar">
            <div className="dr-title">Static Daily Review</div>
            <div className="dr-divider" />
            <Stat label="日期" value={meta.date || selectedItem?.trade_date || '--'} />
            <Stat label="进场" value={summary.total} />
            <Stat label="空" value={summary.puts} tone="red" />
            <Stat label="多" value={summary.calls} tone="green" />
            <Stat label="涨跌" value={stats.changePct} tone={String(stats.change).startsWith('-') ? 'red' : 'green'} />
            <Stat label="窗口" value={setupSummary.count} />
            <Stat label="MFE中位" value={setupSummary.medianMfePct == null ? '--' : formatPct(setupSummary.medianMfePct, { ratio: true })} tone="green" />
            <Stat label="MAE中位" value={setupSummary.medianMaePct == null ? '--' : formatPct(setupSummary.medianMaePct, { ratio: true, negativeSign: true })} tone="red" />
            <div className="dr-strategy-badge">{strategyPayload ? `${strategyPayload.name} v${strategyPayload.version}` : '静态导出'}</div>
            <div className="dr-review-utility">
              <button
                ref={utilityTriggerRef}
                type="button"
                className="dr-review-utility-trigger"
                aria-expanded={utilityOpen}
                aria-controls={utilityPanelId}
                onClick={() => setUtilityOpen((open) => !open)}
              >
                Review 工具
              </button>
              {utilityOpen && (
                <div
                  className="dr-review-utility-panel"
                  id={utilityPanelId}
                  onKeyDown={(event) => {
                    if (event.key === 'Escape') {
                      event.stopPropagation();
                      setUtilityOpen(false);
                      utilityTriggerRef.current?.focus();
                    }
                  }}
                >
                  <button
                    type="button"
                    className={`dr-toggle-switch ${showExtendedKBars ? 'active' : ''}`}
                    role="switch"
                    aria-checked={showExtendedKBars}
                    onClick={() => setShowExtendedKBars((value) => !value)}
                    disabled={!review}
                    title="Toggle 09:00-16:30 extended K bars"
                  >
                    Ext K <span>{showExtendedKBars ? '09:00-16:30' : 'RTH'}</span>
                  </button>
                </div>
              )}
            </div>
          </header>

          <aside className="dr-sidebar">
            <ReviewContextPanel
              days={workspaceDays}
              workspace={workspace}
              onSwitchTicker={chooseTicker}
              onSelectDate={chooseDate}
              dateNavigation="progressive"
            >
              <div className="review-context-actions">
                <label className="review-context-field">
                  Strategy
                  <select value={selectedStrategy?.slug || ''} onChange={chooseStrategy}>
                    {(manifest?.strategies || []).map((item) => (
                      <option key={item.slug} value={item.slug}>{item.name} v{item.version}</option>
                    ))}
                  </select>
                </label>
                {routeNotice && <p className="static-route-notice" role="status">{routeNotice}</p>}
              </div>
            </ReviewContextPanel>
            <div className="dr-sidebar-header">
              <span>提示 {summary.setups || summary.expired ? `(${summary.total} 进场 · ${summary.setups} 启动 / ${summary.expired} 过期)` : `(${allAnnotations.length})`}</span>
            </div>
            <div className="dr-signal-list">
              {tradeRecords && (
                <>
                  <TraderFilters
                    traders={tradeRecords.traders}
                    value={tradeFilters}
                    onChange={setTradeFilters}
                    context={{ ticker: tradeRecords.ticker, tradeDate: tradeRecords.trade_date }}
                    availableTraderIds={traderAvailability.availableTraderIds}
                  />
                  <TradeExportControls payload={tradeRecords} groups={filteredTradeGroups} filters={tradeFilters} />
                </>
              )}
              <TraderTradeList
                groups={filteredTradeGroups}
                traders={tradeRecords?.traders}
                activeGroupId={activeTradeGroupId}
                onSelect={selectTradeGroup}
              />
              <ReviewSignalList
                annotations1m={displayComputed.annotations1m}
                annotations5m={displayComputed.annotations5m}
                setups={displayComputed.setups}
                activeSignal={activeSignal}
                onSelect={selectSignal}
                bars1m={bars1m}
                bars5m={bars5m}
                emptyTitle="当前策略/日期没有生成提示。"
                emptyHint="静态数据已加载，扫描器没有找到进场信号。"
              />
            </div>
          </aside>

          <main className="dr-chart-area">
            {error && <div className="dr-error" role="alert">{error}</div>}
            {!error && !enginePayload && <div className="dr-loading" role="status" aria-live="polite">正在加载静态复盘...</div>}
            {enginePayload && (
              <UnifiedKlineEngine
                ref={engineRef}
                payload={enginePayload}
                annotations1m={engineAnnotations1m}
                annotations5m={chartAnnotations5m}
                engineOptions={DAILY_REVIEW_ENGINE_OPTIONS}
                replayStartTime={showExtendedKBars ? '09:00' : '09:30'}
                onAnnotationClick={(annotation) => {
                  if (annotation.type === 'trade_record') {
                    const groupId = annotation.trade_group_ids?.[0] || annotation.trade_group_id;
                    selectTradeGroup(filteredTradeGroups.find((group) => group.trade_group_id === groupId));
                    return;
                  }
                  selectSignal(allAnnotations.find((item) => item.id === annotation.id) || annotation);
                }}
              />
            )}
          </main>

        </div>
      </section>
    </div>
  );
}

function Stat({ label, value, tone }) {
  return <div className={`dr-stat ${tone || ''}`}><span>{label}</span><strong>{value}</strong></div>;
}
