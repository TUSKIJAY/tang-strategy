const RTH_START = '09:30';
const RTH_END = '16:00';

function timeOf(item) {
  return item?.t || item?.time || '';
}

function inRth(item) {
  const t = timeOf(item);
  return typeof t === 'string' && t >= RTH_START && t < RTH_END;
}

function remapAnnotations(annotations = [], indexMap, timeframe) {
  return annotations
    .map((annotation) => {
      const oldIndex = Number(annotation.bar_index ?? 0);
      const nextIndex = indexMap.get(oldIndex);
      if (nextIndex == null) return null;
      return {
        ...annotation,
        bar_index: nextIndex,
        timeframe: annotation.timeframe || timeframe,
      };
    })
    .filter(Boolean);
}

export function rthReviewPayload(payload) {
  if (!payload) {
    return payload;
  }
  if (payload.reviewed?.session?.default_mode === 'extended') {
    return payload;
  }
  if (payload.meta?.session_mode !== 'extended') {
    return payload;
  }

  const map1m = new Map();
  const map5m = new Map();
  const bars1m = [];
  const bars5m = [];

  (payload.bars_1m || []).forEach((bar, oldIndex) => {
    if (!inRth(bar)) return;
    map1m.set(oldIndex, bars1m.length);
    bars1m.push(bar);
  });

  (payload.bars_5m || []).forEach((bar, oldIndex) => {
    if (!inRth(bar)) return;
    map5m.set(oldIndex, bars5m.length);
    bars5m.push(bar);
  });

  return {
    ...payload,
    meta: {
      ...(payload.meta || {}),
      session_mode: 'rth',
      display_mode: 'rth',
      display_window: `${RTH_START}-${RTH_END} ET`,
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

export function preferredActivationWickStrategy(strategies = []) {
  return strategies.find((strategy) => {
    const values = [strategy.slug, strategy.name, strategy.file, strategy.version]
      .filter(Boolean)
      .map((value) => String(value).toLowerCase());
    return values.some((value) => value.includes('activation_wick') || value.includes('activation wick'));
  }) || strategies[0] || null;
}
