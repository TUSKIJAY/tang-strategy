import { Fragment, useMemo, useState } from 'react';
import { setupForAnnotation } from './lifecycle.js';

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

function annotationTime(annotation, bars1m, bars5m) {
  const bars = annotation?.timeframe === '5m' ? bars5m : bars1m;
  const bar = bars?.[annotation?.bar_index];
  return bar?.t || annotation?.t || `#${annotation?.bar_index ?? '?'}`;
}

function setupGroupKey(annotation) {
  if (!annotation || annotation.timeframe === '5m') return null;
  if (annotation._setup_id != null) return `setup:${annotation._setup_id}`;
  if (annotation._setup_bar_index != null) return `setup:${annotation._setup_bar_index}:${annotation._signal_id || ''}`;
  if (annotation.type === 'setup') return `setup:${annotation.bar_index}:${annotation._signal_id || ''}`;
  return null;
}

function cleanSetupTitle(annotation) {
  const raw = annotation?._setup_title || annotation?.title || annotation?.label || '';
  return translateTitle(String(raw).replace(/^#\d+\s+/, '').replace(/\s+setup$/, ''));
}

function translateTitle(title) {
  return title
    .replace(/\b5m:\s*bullish\s*->\s*bearish\b/g, '5m：多头 -> 空头')
    .replace(/\b5m:\s*bearish\s*->\s*bullish\b/g, '5m：空头 -> 多头')
    .replace(/\bNormal CALL\b/g, '普通 CALL')
    .replace(/\bStrong CALL\b/g, '强势 CALL')
    .replace(/\bNormal PUT\b/g, '普通 PUT')
    .replace(/\bStrong PUT\b/g, '强势 PUT')
    .replace(/\bCALL setup\b/g, 'CALL 启动')
    .replace(/\bPUT setup\b/g, 'PUT 启动');
}

function directionClass(direction) {
  return direction === 'PUT' ? 'put' : 'call';
}

function statusText(status) {
  if (status === 'activated') return '已进场';
  if (status === 'expired') return '已过期';
  return '观察中';
}

function signalStyle(annotation, status) {
  if (status === 'expired' || annotation?.type === 'expired') return 'purple';
  if (annotation?.type === 'setup') return 'blue';
  if (annotation?.style) return annotation.style;
  if (annotation?.direction === 'PUT') return 'red';
  if (annotation?.direction === 'CALL') return 'green';
  return 'blue';
}

function activationMethodText(method, isCall) {
  if (method === 'strong_wick') return isCall ? '强势刺破' : '强势下破';
  if (method === 'close') return isCall ? '收盘突破' : '收盘跌破';
  return isCall ? '突破' : '跌破';
}

function activationRequirementText(value, isCall) {
  if (value === 'strong_wick') return isCall ? '强势刺破' : '强势下破';
  if (value === 'close_or_strong_wick' || value === 'strong_wick_or_close') return isCall ? '收盘突破或强势刺破' : '收盘跌破或强势下破';
  return isCall ? '收盘突破' : '收盘跌破';
}

function observedBars(outcome) {
  return Number.isFinite(Number(outcome?._activation_observed_bars))
    ? Number(outcome._activation_observed_bars)
    : Number(outcome?._activation_window_bars || 8);
}

function lifecycleSummary(outcome, status) {
  const isCall = outcome?.direction !== 'PUT';
  if (status === 'activated') {
    const method = activationMethodText(outcome._activation_confirm_method, isCall);
    return `启动后观察 ${outcome._activation_delay_bars ?? '?'}min，${method}进场确认线 ${formatPrice(outcome._activation_breakout_price)} 后进场`;
  }
  if (status === 'expired') {
    const req = activationRequirementText(outcome._activation_confirm_price, isCall);
    const miss = Number.isFinite(Number(outcome._miss_by)) ? `，仍差 ${formatPrice(Math.max(0, Number(outcome._miss_by)))}` : '';
    const observed = observedBars(outcome);
    const window = outcome._activation_window_bars || 8;
    const boundary = outcome._expiry_kind === 'session_end' ? '，完整交易窗口结束' : '';
    return `启动后观察 ${observed}/${window} 根，未${req}进场确认线 ${formatPrice(outcome._activation_level)}${boundary}，过期${miss}`;
  }
  return `已启动：进入 ${outcome?._activation_window_bars || 8} 根观察窗口，等待进场确认`;
}

function lifecycleRows(outcome, status) {
  const rows = [];
  const isCall = outcome?.direction !== 'PUT';
  if (status === 'activated') {
    const method = activationMethodText(outcome._activation_confirm_method, isCall);
    rows.push(['路径', `启动 ${outcome._setup_time || '?'} -> 观察 ${outcome._activation_delay_bars ?? '?'}min -> 进场 ${outcome._activation_time || '?'}`]);
    rows.push(['观察用时', `${outcome._activation_delay_bars ?? '?'} min / ${outcome._activation_window_bars || 8} 根`]);
    rows.push(['进场确认线', `${outcome.direction || ''} ${method} ${formatPrice(outcome._activation_breakout_price)}`]);
    if (outcome._activation_confirm_method === 'strong_wick' && Number.isFinite(Number(outcome._activation_close_position))) {
      rows.push(['收盘位置', `${Math.round(Number(outcome._activation_close_position) * 100)}%`]);
    }
    rows.push(['解释', '这是进场确认线，不是目标价/止盈价']);
    rows.push(['原始信号', outcome._raw_signal_id || outcome._signal_id || '--']);
    return rows;
  }
  if (status === 'expired') {
    const req = activationRequirementText(outcome._activation_confirm_price, isCall);
    const miss = Number.isFinite(Number(outcome._miss_by)) ? Math.max(0, Number(outcome._miss_by)) : null;
    const observed = observedBars(outcome);
    const window = outcome._activation_window_bars || 8;
    rows.push(['路径', `启动 ${outcome._setup_time || '?'} -> 观察 ${observed}/${window} 根 -> 过期 ${outcome._expire_time || '?'}`]);
    rows.push(['观察窗口', `${observed}/${window} 根未进场${outcome._expiry_kind === 'session_end' ? '（完整交易窗口结束）' : ''}`]);
    rows.push(['进场确认线', `${outcome.direction || ''} ${req} ${formatPrice(outcome._activation_level)}（启动后运行区间）`]);
    rows.push(['窗口最佳收盘', `${formatPrice(outcome._best_close_in_window)}${miss == null ? '' : `，仍差 ${formatPrice(miss)}`}`]);
    if (Number.isFinite(Number(outcome._best_wick_in_window))) {
      rows.push([isCall ? '窗口最高价' : '窗口最低价', `${formatPrice(outcome._best_wick_in_window)}${outcome._wick_confirmed_count ? `（刺破 ${outcome._wick_confirmed_count} 次）` : ''}`]);
    }
    rows.push(['结果', outcome._expiry_gate_reason || '观察过期，后续突破不回头进场', 'warn']);
    rows.push(['解释', '这是进场确认线，不是目标价/止盈价']);
    return rows;
  }
  rows.push(['状态', `启动后进入观察，等待 ${outcome?._activation_window_bars || 8} 根内进场确认`]);
  rows.push(['原始信号', outcome?._raw_signal_id || outcome?._signal_id || '--']);
  return rows;
}

const LABELS = {
  'Strategy selected': '策略已选择',
  'Bar index mapped': 'K 线索引已映射',
  'DB review assembled': 'DB 复盘已组装',
  'Static review exported': '静态复盘已导出',
  'Session allowed': '交易时段允许',
  '5m trend aligned': '5m 趋势同向',
  '1m MA10 slope aligned': '1m MA10 斜率同向',
  'Prior HA range touched trend level': '前根 HA 区间触及趋势线',
  'Prior close filter': '前根收盘过滤',
  'Current HA candle color': '当前 HA K 颜色',
  'Not tangled': '均线不缠绕',
  'Space check': '目标空间检查',
  'Previous elite touch': '前根强共振触线',
  'Activation within window': '观察窗口内确认',
  'Breakout confirmation': '进场突破确认',
  'Same direction HA candle': 'HA 颜色同向',
  'MA10 slope still aligned': 'MA10 斜率仍同向',
  'Current bar touches MA10': '当前 K 触及 MA10',
  'HA body side of MA10': 'HA 实体在 MA10 同侧',
  'Direction color fallback': '方向颜色兜底',
};

function translateValue(value) {
  return String(value ?? '')
    .replace(/\bActivation window expired\b/g, '观察窗口过期')
    .replace(/\bSession ended before activation window completed\b/g, '完整交易窗口结束前未完成进场确认')
    .replace(/\b5m trend changed from\b/g, '5m 趋势切换：')
    .replace(/\bto\b/g, '->')
    .replace(/\bbullish\b/g, '多头')
    .replace(/\bbearish\b/g, '空头')
    .replace(/\bgreen\b/g, '绿 K')
    .replace(/\bred\b/g, '红 K')
    .replace(/\bnormal\b/g, '普通')
    .replace(/\bstrong_wick\b/g, '强势影线')
    .replace(/\bclose\b/g, '收盘确认');
}

function detailItems(annotation) {
  const conditions = annotation?._conditions || annotation?.checklist || [];
  if (!conditions.length) return [
    { label: '策略已选择', ok: true, value: annotation?.label || annotation?.title || '--' },
    { label: 'K 线索引已映射', ok: true, value: annotation?.bar_index },
  ];
  return conditions.map((condition) => ({
    label: LABELS[condition.label] || condition.label,
    ok: condition.pass ?? condition.ok,
    value: condition.detail ?? condition.value,
  }));
}

function TradeResult({ setup, bars1m }) {
  if (!setup) return null;
  const exitBar = bars1m[setup.exit_index];
  const resultClass = setup.invalidation_type === 'eod' ? 'eod' : setup.spy_move >= 0 ? 'favorable' : 'adverse';
  return (
    <div className={`dr-trade-result ${resultClass}`}>
      <span className={setup.spy_move >= 0 ? 'positive' : 'negative'}>{signed(setup.spy_move)}</span>
      <span>{setup.invalidation_type === 'eod' ? 'EOD' : '信号失效'} · {setup.bars_held}m · → {exitBar?.t || '?'}</span>
    </div>
  );
}

function SignalDetail({ annotation, setup, bars1m }) {
  const items = detailItems(annotation);
  return (
    <div className="dr-signal-detail">
      <section className="dr-detail-section">
        <h5>触发条件 ({items.filter((item) => item.ok !== false).length}/{items.length} 通过)</h5>
        <ul>
          {items.map((item, index) => (
            <li key={`${item.label}-${index}`}>
              <span className={item.ok === false ? 'fail' : 'pass'}>{item.ok === false ? '○' : '✓'}</span>
              <div>
                <strong>{item.label}</strong>
                {item.value != null && <small>{translateValue(item.value)}</small>}
              </div>
            </li>
          ))}
        </ul>
      </section>
      {(annotation?._invalidation || setup) && (
        <section className="dr-detail-section dr-detail-grid">
          <h5>{annotation?.type === 'signal' ? '进场后失效' : '若进场后的失效规则'}</h5>
          {annotation?._invalidation && <><span>规则</span><strong>{annotation._invalidation.human || annotation._invalidation.rule}</strong></>}
          {annotation?._invalidation && <><span>{annotation.type === 'signal' ? '进场时' : '启动时'} {annotation._invalidation.line?.toUpperCase()}</span><strong>{formatPrice(annotation._invalidation.initial_value)}</strong></>}
          {setup?.invalidation_type === 'invalidated' && <><span>失效时刻</span><strong>{bars1m[setup.exit_index]?.t || '?'}（持续 {setup.bars_held} 根 K）</strong></>}
          {setup?.invalidation_reason && <><span>失效原因</span><strong>{setup.invalidation_reason}</strong></>}
        </section>
      )}
      {setup && (
        <section className="dr-detail-section dr-detail-grid">
          <h5>期间数据（进场后到失效/EOD，仅供参考）</h5>
          <span>最大有利</span><strong className="good">+{formatPrice(setup.mfe)} ({formatPct(setup.mfe_pct, { ratio: true })})</strong>
          <span>最大不利</span><strong className="bad">-{formatPrice(setup.mae)} ({formatPct(setup.mae_pct, { ratio: true, negativeSign: true })})</strong>
          <span>进场价</span><strong>{formatPrice(setup.entry_price)}（进场 K 之后第一根 hC）</strong>
        </section>
      )}
    </div>
  );
}

function LifecycleFlow({ setup, outcome, status, bars1m, bars5m }) {
  const setupTime = setup ? annotationTime(setup, bars1m, bars5m) : outcome?._setup_time || '?';
  const outcomeTime = status === 'activated'
    ? outcome?._activation_time || annotationTime(outcome, bars1m, bars5m)
    : status === 'expired'
      ? outcome?._expire_time || annotationTime(outcome, bars1m, bars5m)
      : '观察中';
  const waitText = status === 'activated'
    ? `${outcome?._activation_delay_bars ?? '?'}min`
    : `${observedBars(outcome)}/${outcome?._activation_window_bars || 8}根`;
  return (
    <div className="dr-lifecycle-flow">
      <span className="dr-lifecycle-node setup">启</span><span>启动 {setupTime}</span>
      <span className="dr-lifecycle-arrow">-&gt;</span>
      <span className="dr-lifecycle-node watch">观</span><span>观察 {waitText}</span>
      <span className="dr-lifecycle-arrow">-&gt;</span>
      <span className={`dr-lifecycle-node ${status === 'activated' ? 'activated' : status === 'expired' ? 'expired' : 'setup'}`}>{status === 'activated' ? '进' : status === 'expired' ? '过' : '...'}</span>
      <span>{status === 'activated' ? `进场 ${outcomeTime}` : status === 'expired' ? `过期 ${outcomeTime}` : outcomeTime}</span>
    </div>
  );
}

function LifecycleCard({ group, active, expanded, onSelect, onToggle, bars1m, bars5m, setups }) {
  const setupAnnotation = group.setup;
  const outcome = group.outcome;
  const status = group.signal ? 'activated' : group.expired ? 'expired' : 'pending';
  const setup = group.signal ? setupForAnnotation(group.signal, setups) : null;
  const setupId = outcome?._setup_id || setupAnnotation?._setup_id || '?';
  const title = cleanSetupTitle(setupAnnotation || outcome);
  const rows = lifecycleRows(outcome, status);
  return (
    <article className={`dr-signal-card dr-lifecycle-card ${active ? 'active' : ''} ${expanded ? 'expanded' : ''}`} data-style={signalStyle(outcome, status)} data-life={status} onClick={() => onSelect(outcome)}>
      <div className="dr-signal-time">
        <span className="dr-lifecycle-id">#{setupId}</span>
        {annotationTime(setupAnnotation || outcome, bars1m, bars5m)} · 1m
        {outcome?.direction && <span className={`dr-signal-dir ${directionClass(outcome.direction)}`}>{outcome.direction}</span>}
        <span className={`dr-lifecycle-status ${status}`}>{statusText(status)}</span>
      </div>
      <div className="dr-signal-title">{title} 启动观察流程</div>
      <LifecycleFlow setup={setupAnnotation} outcome={outcome} status={status} bars1m={bars1m} bars5m={bars5m} />
      <div className="dr-signal-meta">{lifecycleSummary(outcome, status)}</div>
      <div className="dr-lifecycle-metrics">
        {rows.map(([label, value, tone], index) => (
          <Fragment key={`${label}-${index}`}>
            <span className="label">{label}</span>
            <span className={`value ${tone || ''}`}>{translateValue(value)}</span>
          </Fragment>
        ))}
      </div>
      <TradeResult setup={setup} bars1m={bars1m} />
      <button type="button" className="dr-signal-toggle" onClick={(event) => { event.stopPropagation(); onToggle(); }}>{expanded ? '收起详情' : '展开详情'}</button>
      <SignalDetail annotation={outcome} setup={setup} bars1m={bars1m} />
    </article>
  );
}

function RegularCard({ annotation, active, expanded, onSelect, onToggle, bars1m, bars5m, setups }) {
  const setup = setupForAnnotation(annotation, setups);
  const timeframe = annotation.timeframe || '1m';
  return (
    <article className={`dr-signal-card ${active ? 'active' : ''} ${expanded ? 'expanded' : ''}`} data-style={signalStyle(annotation)} onClick={() => onSelect(annotation)}>
      <div className="dr-signal-time">
        {annotationTime(annotation, bars1m, bars5m)} · <span className={`dr-timeframe-badge ${timeframe === '5m' ? 'blue' : ''}`}>{timeframe}</span>
        {annotation.direction && <span className={`dr-signal-dir ${directionClass(annotation.direction)}`}>{annotation.direction}</span>}
      </div>
      <div className="dr-signal-title">{translateTitle(annotation.title || annotation.label || '策略提示')}</div>
      {(annotation.score || annotation.body) && (
        <div className="dr-signal-meta">
          {annotation.score && <span className="dr-signal-score">{annotation.score}</span>}
          {annotation.body && <span>{translateValue(annotation.body)}</span>}
        </div>
      )}
      <TradeResult setup={setup} bars1m={bars1m} />
      <button type="button" className="dr-signal-toggle" onClick={(event) => { event.stopPropagation(); onToggle(); }}>{expanded ? '收起详情' : '展开详情'}</button>
      <SignalDetail annotation={annotation} setup={setup} bars1m={bars1m} />
    </article>
  );
}

function buildItems(annotations1m, annotations5m) {
  const items = [];
  const grouped = new Map();

  annotations1m.forEach((annotation) => {
    const item = { ...annotation, timeframe: annotation.timeframe || '1m' };
    const key = setupGroupKey(item);
    if (!key) {
      items.push({ kind: 'anno', annotation: item, sort: item.bar_index });
      return;
    }
    if (!grouped.has(key)) grouped.set(key, { kind: 'lifecycle', key, annotations: [] });
    grouped.get(key).annotations.push(item);
  });

  grouped.forEach((group) => {
    group.annotations.sort((a, b) => a.bar_index - b.bar_index);
    group.setup = group.annotations.find((item) => item.type === 'setup') || group.annotations[0];
    group.signal = group.annotations.find((item) => item.type === 'signal') || null;
    group.expired = group.annotations.find((item) => item.type === 'expired') || null;
    group.outcome = group.signal || group.expired || group.setup;
    group.sort = group.setup?.bar_index ?? group.outcome?.bar_index ?? 0;
    items.push(group);
  });

  annotations5m.forEach((annotation) => {
    items.push({ kind: 'anno', annotation: { ...annotation, timeframe: '5m' }, sort: annotation.bar_index });
  });

  return items.sort((a, b) => a.sort - b.sort);
}

export function ReviewSignalList({ annotations1m = [], annotations5m = [], setups = [], activeSignal, onSelect, bars1m = [], bars5m = [], emptyTitle = '当前策略/日期没有生成提示。', emptyHint = '可重新扫描或切换日期查看。' }) {
  const items = useMemo(() => buildItems(annotations1m, annotations5m), [annotations1m, annotations5m]);
  const [expandedKey, setExpandedKey] = useState('');
  const toggleExpanded = (key) => setExpandedKey((current) => current === key ? '' : key);

  return (
    <section className="dr-signal-stack" aria-label="策略讲解信号">
      <div className="stack-caption">策略讲解 · Signals</div>
      {!items.length ? (
        <div className="dr-empty">
          <div className="dr-empty-icon">K</div>
          <div>{emptyTitle}</div>
          <small>{emptyHint}</small>
        </div>
      ) : (
        items.map((item) => {
          if (item.kind === 'lifecycle') {
            const active = item.annotations.some((annotation) => annotation.id === activeSignal?.id);
            return <LifecycleCard key={item.key} group={item} active={active} expanded={expandedKey === item.key} onSelect={onSelect} onToggle={() => toggleExpanded(item.key)} bars1m={bars1m} bars5m={bars5m} setups={setups} />;
          }
          const itemKey = `anno:${item.annotation.id}`;
          return (
            <RegularCard
              key={itemKey}
              annotation={item.annotation}
              active={item.annotation.id === activeSignal?.id}
              expanded={expandedKey === itemKey}
              onSelect={onSelect}
              onToggle={() => toggleExpanded(itemKey)}
              bars1m={bars1m}
              bars5m={bars5m}
              setups={setups}
            />
          );
        })
      )}
    </section>
  );
}
