function num(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function timeOf(bar) {
  return bar?.t || bar?.time || '';
}

function fmt(value, digits = 3) {
  const n = num(value);
  return n == null ? '--' : n.toFixed(digits);
}

function normalizeDirection(value) {
  const raw = String(value || '').toLowerCase();
  if (['call', 'long', 'bull', 'bullish', 'support'].includes(raw)) return 'CALL';
  if (['put', 'short', 'bear', 'bearish', 'reject'].includes(raw)) return 'PUT';
  return null;
}

function isGreen(bar) {
  return num(bar?.hC ?? bar?.C) >= num(bar?.hO ?? bar?.O);
}

function isRed(bar) {
  return num(bar?.hC ?? bar?.C) < num(bar?.hO ?? bar?.O);
}

function fieldValue(bars, index, ref) {
  if (typeof ref === 'number') return ref;
  if (ref == null) return null;
  const text = String(ref);
  const match = text.match(/^([A-Za-z0-9_]+)(?:\[(\d+)\])?$/);
  if (!match) return null;
  const offset = match[2] ? Number(match[2]) : 0;
  const bar = bars[index - offset];
  return num(bar?.[match[1]]);
}

function compare(left, operator, right) {
  if (left == null || right == null) return false;
  if (operator === '>') return left > right;
  if (operator === '>=') return left >= right;
  if (operator === '<') return left < right;
  if (operator === '<=') return left <= right;
  if (operator === '==') return left === right;
  return false;
}

function inSession(time, session = {}) {
  const start = session.start || '09:30';
  const end = session.end || '16:00';
  if (!time) return true;
  return time >= start && time <= end;
}

export function detectTrendsRouted(bars5m = [], strategy = {}) {
  const trend = strategy.trend || {};
  const method = trend.method || 'relaxed';
  const lines = trend.lines || (method === 'regular_close_5m_ma_stack' ? ['m10', 'm20', 'm30'] : ['m10', 'm50']);
  return bars5m.map((bar, index) => {
    if (method === 'strict' || method === 'regular_close_5m_ma_stack') {
      const values = lines.map((line) => num(bar[line])).filter((value) => value != null);
      if (values.length < 2) return null;
      if (values.every((value, i) => i === values.length - 1 || value > values[i + 1])) return 'bullish';
      if (values.every((value, i) => i === values.length - 1 || value < values[i + 1])) return 'bearish';
      return null;
    }
    const fastKey = trend.fast_ma || 'm10';
    const slowKey = trend.slow_ma || 'm50';
    const slopeBars = Number(trend.slope_bars || 3);
    const fast = num(bar[fastKey]);
    const slow = num(bar[slowKey]);
    const prevFast = num(bars5m[index - slopeBars]?.[fastKey]);
    if (fast == null || slow == null) return null;
    const slope = prevFast == null ? 0 : fast - prevFast;
    if (fast > slow && slope >= 0) return 'bullish';
    if (fast < slow && slope <= 0) return 'bearish';
    return null;
  });
}

function trendAt(bars5m, trends5m, time) {
  if (!bars5m.length) return null;
  let current = 0;
  for (let i = 0; i < bars5m.length; i += 1) {
    if (timeOf(bars5m[i]) <= time) current = i;
    else break;
  }
  return trends5m[current] || null;
}

function maSlopeOk(bars, index, direction, lookback = 1) {
  const current = num(bars[index]?.m10);
  const prev = num(bars[index - lookback]?.m10);
  if (current == null || prev == null) return false;
  return direction === 'CALL' ? current > prev : current < prev;
}

function priorTouchesAnyLevel(bars, index, levels = ['m10']) {
  const prior = bars[index - 1];
  if (!prior) return false;
  const high = num(prior.hH ?? prior.H);
  const low = num(prior.hL ?? prior.L);
  return levels.some((level) => {
    const ma = num(prior[level]);
    return ma != null && low <= ma && high >= ma;
  });
}

function currentTouchesMa10(bar) {
  const ma = num(bar?.m10);
  const high = num(bar?.hH ?? bar?.H);
  const low = num(bar?.hL ?? bar?.L);
  return ma != null && high != null && low != null && low <= ma && high >= ma;
}

function previousCloseFilter(bars, index, direction) {
  const prior = bars[index - 1];
  if (!prior) return false;
  const close = num(prior.hC ?? prior.C);
  const ma10 = num(prior.m10);
  if (close == null || ma10 == null) return false;
  return direction === 'CALL' ? close >= ma10 : close <= ma10;
}

function notTangled(bar, strategy) {
  const cfg = strategy.filter || {};
  const threshold = num(cfg.entangle_threshold_ratio) ?? null;
  const lines = cfg.entangle_lines || ['m10', 'm20', 'm30', 'm50'];
  const values = lines.map((line) => num(bar[line])).filter((value) => value != null);
  if (values.length < 2) return true;
  const spread = Math.max(...values) - Math.min(...values);
  if (threshold != null) return spread / Math.max(1, num(bar.C) || 1) >= threshold;
  const absolute = num(cfg.entangle_threshold);
  return absolute == null ? true : spread >= absolute;
}

function spaceOk(bar, direction, strategy) {
  const cfg = strategy.space_check || strategy.filter || {};
  const thresholdRatio = num(cfg.min_distance_pct_of_price) != null ? num(cfg.min_distance_pct_of_price) / 100 : num(cfg.space_threshold_ratio);
  const thresholdAbs = num(cfg.space_threshold) ?? 0;
  const close = num(bar.C);
  if (close == null) return true;
  const minDistance = thresholdRatio != null ? close * thresholdRatio : thresholdAbs;
  const barriers = direction === 'CALL'
    ? (cfg.call_barriers_above || ['m50', 'm200', 'vw'])
    : (cfg.put_barriers_below || ['m50', 'm200', 'vw']);
  const distances = barriers.map((key) => num(bar[key])).filter((value) => value != null).map((value) => direction === 'CALL' ? value - close : close - value).filter((value) => value > 0);
  if (!distances.length) return true;
  return Math.min(...distances) >= minDistance;
}

function elitePrevious(bars, index) {
  const prior = bars[index - 1];
  if (!prior) return false;
  const high = num(prior.hH ?? prior.H);
  const low = num(prior.hL ?? prior.L);
  const touches = (line) => {
    const value = num(prior[line]);
    return value != null && low <= value && high >= value;
  };
  return touches('m10') && (touches('m50') || touches('m200') || touches('vw'));
}

function legacyConditionSignal({ bars1m, index, signal, direction, trend, strategy }) {
  const bar = bars1m[index];
  const requiredTrend = direction === 'CALL' ? 'bullish' : 'bearish';
  const levels = strategy.touch_logic?.trend_touch_levels || ['m10'];
  const checks = [
    { label: 'Session allowed', ok: true, value: timeOf(bar) },
    { label: '5m trend aligned', ok: trend === requiredTrend, value: trend || 'none' },
    { label: '1m MA10 slope aligned', ok: maSlopeOk(bars1m, index, direction, strategy.slope_filter?.lookback_bars || 1), value: `${fmt(bars1m[index - 1]?.m10)} -> ${fmt(bar.m10)}` },
    { label: 'Prior HA range touched trend level', ok: priorTouchesAnyLevel(bars1m, index, levels), value: levels.join('/') },
    { label: 'Prior close filter', ok: previousCloseFilter(bars1m, index, direction), value: direction === 'CALL' ? 'hC[1] >= m10[1]' : 'hC[1] <= m10[1]' },
    { label: 'Current HA candle color', ok: direction === 'CALL' ? isGreen(bar) : isRed(bar), value: direction === 'CALL' ? 'green' : 'red' },
    { label: 'Not tangled', ok: notTangled(bar, strategy) },
    { label: 'Space check', ok: spaceOk(bar, direction, strategy) },
  ];
  if (!strategy.slope_filter?.enabled) checks[2].ok = true;
  if (!strategy.touch_logic && signal.conditions?.wick_touch) {
    checks[3] = { label: 'Current bar touches MA10', ok: currentTouchesMa10(bar), value: `m10 ${fmt(bar.m10)}` };
    checks[4] = { label: 'HA body side of MA10', ok: direction === 'CALL' ? num(bar.hC) >= num(bar.m10) && num(bar.hO) >= num(bar.m10) : num(bar.hC) <= num(bar.m10) && num(bar.hO) <= num(bar.m10) };
  }
  const elite = elitePrevious(bars1m, index);
  if (signal.conditions && Object.prototype.hasOwnProperty.call(signal.conditions, 'previous_elite')) {
    checks.push({ label: 'Previous elite touch', ok: elite === Boolean(signal.conditions.previous_elite), value: elite ? 'elite' : 'normal' });
  }
  return checks;
}

function evaluateGenericConditions(bars, index, conditions = {}, direction) {
  const checks = [];
  const bar = bars[index];
  for (const [key, cond] of Object.entries(conditions)) {
    let ok = true;
    let value = '';
    if (key === 'candle_color') {
      ok = cond === 'green' ? isGreen(bar) : isRed(bar);
      value = cond;
    } else if (typeof cond === 'boolean') {
      ok = cond;
    } else if (typeof cond === 'string') {
      if (cond === 'green') ok = isGreen(bar);
      else if (cond === 'red') ok = isRed(bar);
      else ok = true;
      value = cond;
    } else if (cond && typeof cond === 'object' && cond.field && cond.operator) {
      const left = fieldValue(bars, index, cond.field);
      const right = fieldValue(bars, index, cond.target);
      ok = compare(left, cond.operator, right);
      value = `${fmt(left)} ${cond.operator} ${fmt(right)}`;
    }
    checks.push({ label: key.replaceAll('_', ' '), ok, value });
  }
  if (!checks.length) checks.push({ label: 'Direction color fallback', ok: direction === 'CALL' ? isGreen(bar) : isRed(bar) });
  return checks;
}

function invalidationFor(strategy, direction, bar) {
  const exitCfg = strategy.exit || {};
  const l2 = exitCfg.L2_hard_stops || {};
  const useMa50 = Boolean(l2.ma50_ha_close_break);
  const line = useMa50 ? 'm50' : (exitCfg.L1_technical?.ma_stop_line || exitCfg.ma_stop_line || 'm10');
  return {
    line,
    initial_value: num(bar?.[line]),
    rule: useMa50 ? 'ma50_ha_close_break' : 'ha_body_cross_ma_stop_line',
    human: direction === 'CALL' ? `CALL invalidates below ${line.toUpperCase()}` : `PUT invalidates above ${line.toUpperCase()}`,
  };
}

function annotationFromSignal({ signal, index, bar, direction, checks, strategy, type = 'signal', extra = {} }) {
  const passCount = checks.filter((check) => check.ok).length;
  const style = type === 'expired' ? 'purple' : signal.style || (direction === 'CALL' ? 'green' : 'red');
  return {
    id: `${type}-${signal.id || signal.name || 'signal'}-${index}`,
    bar_index: index,
    t: timeOf(bar),
    ts: bar.ts,
    type,
    direction,
    style,
    title: signal.name || signal.id || strategy.name || 'Strategy signal',
    label: signal.name || signal.id || strategy.name || 'Strategy signal',
    body: `${passCount}/${checks.length} conditions passed`,
    score: `${passCount}/${checks.length}`,
    price: bar.C,
    source: 'legacy-compatible-browser-scanner',
    checklist: checks.map((check) => ({ label: check.label, ok: check.ok, value: check.value })),
    _conditions: checks.map((check) => ({ label: check.label, pass: check.ok, detail: check.value == null ? '' : String(check.value) })),
    _invalidation: invalidationFor(strategy, direction, bar),
    _trendAligned: true,
    _signal_id: signal.id || signal.name,
    ...extra,
  };
}

function applyActivation({ rawSignals, bars1m, strategy }) {
  const cfg = strategy.entry_activation;
  if (!cfg?.enabled) return rawSignals;
  const maxWait = Number(cfg.max_wait_bars || 8);
  const strongWickMin = Number(cfg.strong_wick?.close_position_min || 0.6);
  const output = [];
  let setupId = 0;
  for (const setup of rawSignals) {
    setupId += 1;
    const setupBar = bars1m[setup.bar_index];
    const direction = setup.direction;
    const isCall = direction === 'CALL';
    const start = setup.bar_index + 1;
    const end = Math.min(bars1m.length - 1, setup.bar_index + maxWait);
    let runningHigh = num(setupBar.H);
    let runningLow = num(setupBar.L);
    let activation = null;
    let bestClose = null;
    let bestWick = null;
    for (let i = start; i <= end; i += 1) {
      const bar = bars1m[i];
      const close = num(bar.C);
      const high = num(bar.H);
      const low = num(bar.L);
      const range = Math.max(0.0001, high - low);
      const closePosition = (close - low) / range;
      const closeBreak = isCall ? close > runningHigh : close < runningLow;
      const wickBreak = isCall ? high > runningHigh && closePosition >= strongWickMin : low < runningLow && closePosition <= (1 - strongWickMin);
      bestClose = bestClose == null ? close : (isCall ? Math.max(bestClose, close) : Math.min(bestClose, close));
      bestWick = bestWick == null ? (isCall ? high : low) : (isCall ? Math.max(bestWick, high) : Math.min(bestWick, low));
      if ((cfg.confirm_price === 'close_or_strong_wick' && (closeBreak || wickBreak)) || (cfg.confirm_price !== 'close_or_strong_wick' && closeBreak)) {
        const checks = [
          ...setup.checklist,
          { label: 'Activation within window', ok: true, value: `${i - setup.bar_index}/${maxWait}` },
          { label: 'Breakout confirmation', ok: true, value: cfg.confirm_price || 'close' },
        ];
        activation = annotationFromSignal({
          signal: { id: setup._signal_id, name: setup.title, style: setup.style },
          index: i,
          bar,
          direction,
          checks,
          strategy,
          type: 'signal',
          extra: {
            _setup_id: setupId,
            _setup_bar_index: setup.bar_index,
            _setup_time: setup.t,
            _activation_bar_index: i,
            _activation_time: timeOf(bar),
            _activation_delay_bars: i - setup.bar_index,
            _activation_confirm_method: wickBreak && !closeBreak ? 'strong_wick' : 'close',
            _activation_breakout_price: isCall ? runningHigh : runningLow,
          },
        });
        break;
      }
      runningHigh = Math.max(runningHigh, high);
      runningLow = Math.min(runningLow, low);
    }
    output.push({ ...setup, id: `setup-${setupId}-${setup.bar_index}`, type: 'setup', _setup_id: setupId, _setup_bar_index: setup.bar_index, _setup_time: setup.t, _activation_window_bars: maxWait, _activation_level: isCall ? runningHigh : runningLow });
    if (activation) {
      output.push(activation);
    } else {
      const expireBar = bars1m[end] || setupBar;
      output.push({
        ...setup,
        id: `expired-${setupId}-${end}`,
        type: 'expired',
        style: 'purple',
        bar_index: end,
        t: timeOf(expireBar),
        ts: expireBar.ts,
        price: expireBar.C,
        _setup_id: setupId,
        _setup_bar_index: setup.bar_index,
        _setup_time: setup.t,
        _expire_bar_index: end,
        _expire_time: timeOf(expireBar),
        _activation_window_bars: maxWait,
        _activation_level: isCall ? runningHigh : runningLow,
        _best_close_in_window: bestClose,
        _best_wick_in_window: bestWick,
        _expiry_gate_reason: 'Activation window expired',
      });
    }
  }
  return output;
}

export function scanSignals({ bars1m = [], bars5m = [], strategy = {} }) {
  if (!strategy || !Array.isArray(strategy.signals)) return [];
  const session = strategy.filter?.session || {};
  const trends5m = detectTrendsRouted(bars5m, strategy);
  const rawSignals = [];

  bars1m.forEach((bar, index) => {
    if (index < 1) return;
    const time = timeOf(bar);
    if (!inSession(time, session)) return;
    const trend = trendAt(bars5m, trends5m, time);

    for (const signal of strategy.signals) {
      const direction = normalizeDirection(signal.direction || signal.side || signal.type || signal.action || signal.trend_required);
      if (!direction) continue;
      const requiredTrend = direction === 'CALL' ? 'bullish' : 'bearish';
      if (trend !== requiredTrend) continue;
      const checks = strategy.touch_logic || strategy.slope_filter || strategy.space_check
        ? legacyConditionSignal({ bars1m, index, signal, direction, trend, strategy })
        : [
            { label: '5m trend aligned', ok: true, value: trend },
            ...evaluateGenericConditions(bars1m, index, signal.conditions || {}, direction),
          ];
      if (!checks.every((check) => check.ok)) continue;
      rawSignals.push(annotationFromSignal({ signal, index, bar, direction, checks, strategy }));
    }
  });

  return applyActivation({ rawSignals, bars1m, strategy });
}

export function generateTrendAnnotations(bars5m = [], strategy = {}) {
  const trends = detectTrendsRouted(bars5m, strategy);
  const annotations = [];
  let previous = null;
  trends.forEach((trend, index) => {
    if (trend && previous && trend !== previous) {
      annotations.push({
        id: `trend-${index}`,
        bar_index: index,
        timeframe: '5m',
        type: 'trend',
        style: 'blue',
        title: `5m: ${previous} -> ${trend}`,
        label: `5m trend ${trend}`,
        body: `5m trend changed from ${previous} to ${trend}`,
        t: timeOf(bars5m[index]),
      });
    }
    if (trend) previous = trend;
  });
  return annotations;
}

export function summarizeAnnotations(annotations = []) {
  const signals = annotations.filter((a) => a.type === 'signal');
  const calls = signals.filter((a) => a.direction === 'CALL' || a.type === 'CALL').length;
  const puts = signals.filter((a) => a.direction === 'PUT' || a.type === 'PUT').length;
  const setups = annotations.filter((a) => a.type === 'setup').length;
  const expired = annotations.filter((a) => a.type === 'expired').length;
  return { total: signals.length, calls, puts, setups, expired };
}
