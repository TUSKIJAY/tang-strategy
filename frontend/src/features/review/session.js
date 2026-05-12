const RTH_START = '09:30';
const RTH_END = '16:00';
const EXTENDED_K_START = '09:00';
const EXTENDED_K_END = '16:30';

export const REVIEW_SESSION_WINDOWS = {
  rth: {
    mode: 'rth',
    start: RTH_START,
    end: RTH_END,
    label: `${RTH_START}-${RTH_END} ET`,
  },
  extended_k: {
    mode: 'extended_k',
    start: EXTENDED_K_START,
    end: EXTENDED_K_END,
    label: `${EXTENDED_K_START}-${EXTENDED_K_END} ET`,
  },
};

function timeOf(item) {
  return item?.t || item?.time || '';
}

function inWindow(item, window) {
  const t = timeOf(item);
  return typeof t === 'string' && t >= window.start && t < window.end;
}

function remapAnnotations(annotations = [], indexMap, timeframe) {
  const indexFields = [
    '_setup_bar_index',
    '_activation_bar_index',
    '_expire_bar_index',
    '_activation_window_start_bar_index',
    '_activation_window_end_bar_index',
    '_last_checked_bar_index',
  ];

  return annotations
    .map((annotation) => {
      const oldIndex = Number(annotation.bar_index ?? 0);
      const nextIndex = indexMap.get(oldIndex);
      if (nextIndex == null) return null;
      const extraIndexes = {};
      indexFields.forEach((field) => {
        if (!Object.prototype.hasOwnProperty.call(annotation, field)) return;
        const rawValue = Number(annotation[field]);
        if (!Number.isInteger(rawValue)) return;
        extraIndexes[field] = indexMap.get(rawValue) ?? (nextIndex + rawValue - oldIndex);
      });
      return {
        ...annotation,
        ...extraIndexes,
        bar_index: nextIndex,
        timeframe: annotation.timeframe || timeframe,
      };
    })
    .filter(Boolean);
}

function keyForBar(bar) {
  if (!bar) return '';
  return bar.ts ? `ts:${bar.ts}` : `t:${timeOf(bar)}`;
}

export function buildBarIndexMap(sourceBars = [], targetBars = []) {
  const byKey = new Map();
  targetBars.forEach((bar, index) => {
    const key = keyForBar(bar);
    if (key) byKey.set(key, index);
  });

  const byTime = new Map();
  targetBars.forEach((bar, index) => {
    const time = timeOf(bar);
    if (time && !byTime.has(time)) byTime.set(time, index);
  });

  const indexMap = new Map();
  sourceBars.forEach((bar, index) => {
    const key = keyForBar(bar);
    const nextIndex = (key && byKey.get(key)) ?? byTime.get(timeOf(bar));
    if (nextIndex != null) indexMap.set(index, nextIndex);
  });
  return indexMap;
}

export function remapAnnotationIndexes(annotations = [], indexMap, timeframe = '1m') {
  return remapAnnotations(annotations, indexMap, timeframe);
}

export function remapSetupIndexes(setups = [], indexMap) {
  const mapIndex = (value) => {
    const index = Number(value);
    if (!Number.isInteger(index)) return value;
    return indexMap.get(index) ?? null;
  };

  return setups
    .map((setup) => {
      const signalIndex = mapIndex(setup.signal_index);
      const entryIndex = mapIndex(setup.entry_index);
      const exitIndex = mapIndex(setup.exit_index);
      if (signalIndex == null || entryIndex == null || exitIndex == null) return null;

      return {
        ...setup,
        signal_index: signalIndex,
        entry_index: entryIndex,
        exit_index: exitIndex,
        mfe_index: mapIndex(setup.mfe_index) ?? setup.mfe_index,
        mae_index: mapIndex(setup.mae_index) ?? setup.mae_index,
      };
    })
    .filter(Boolean);
}

export function reviewPayloadForWindow(payload, mode = 'rth') {
  if (!payload) {
    return payload;
  }
  const window = REVIEW_SESSION_WINDOWS[mode] || REVIEW_SESSION_WINDOWS.rth;

  const map1m = new Map();
  const map5m = new Map();
  const bars1m = [];
  const bars5m = [];

  (payload.bars_1m || []).forEach((bar, oldIndex) => {
    if (!inWindow(bar, window)) return;
    map1m.set(oldIndex, bars1m.length);
    bars1m.push(bar);
  });

  (payload.bars_5m || []).forEach((bar, oldIndex) => {
    if (!inWindow(bar, window)) return;
    map5m.set(oldIndex, bars5m.length);
    bars5m.push(bar);
  });

  return {
    ...payload,
    meta: {
      ...(payload.meta || {}),
      session_mode: window.mode,
      display_mode: window.mode,
      display_window: window.label,
      original_session_mode: payload.meta?.session_mode,
      original_counts: payload.meta?.counts,
      counts: {
        ...(payload.meta?.counts || {}),
        bars_1m: bars1m.length,
        bars_5m: bars5m.length,
      },
    },
    bars_1m: bars1m,
    bars_5m: bars5m,
    annotations_1m: remapAnnotations(payload.annotations_1m || [], map1m, '1m'),
    annotations_5m: remapAnnotations(payload.annotations_5m || [], map5m, '5m'),
  };
}

export function rthReviewPayload(payload) {
  return reviewPayloadForWindow(payload, 'rth');
}

export function preferredActivationWickStrategy(strategies = []) {
  return strategies.find((strategy) => {
    const values = [strategy.slug, strategy.name, strategy.file, strategy.version]
      .filter(Boolean)
      .map((value) => String(value).toLowerCase());
    return values.some((value) => value.includes('activation_wick') || value.includes('activation wick'));
  }) || strategies[0] || null;
}
