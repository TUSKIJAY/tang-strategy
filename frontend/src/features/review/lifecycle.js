function num(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function fmt(value, digits = 3) {
  const n = num(value);
  return n == null ? '--' : n.toFixed(digits);
}

function median(values) {
  const sorted = values.map(Number).filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) return null;
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

export function traceSetups(bars1m = [], annotations = [], exitCfg = {}) {
  const officialSignals = annotations.filter((annotation) => annotation.type === 'signal' && (annotation.direction === 'CALL' || annotation.direction === 'PUT'));
  if (!bars1m.length || !officialSignals.length) return [];
  const l1 = exitCfg.L1_technical || exitCfg;
  const l2 = exitCfg.L2_hard_stops || {};
  const useMa50CloseBreak = Boolean(l2.ma50_ha_close_break);
  const maStopLine = useMa50CloseBreak ? 'm50' : (l1.ma_stop_line || 'm10');

  return officialSignals.map((signal) => {
    const entryIndex = Math.min(bars1m.length - 1, signal.bar_index + 1);
    const entryBar = bars1m[entryIndex];
    const entryPrice = num(entryBar?.hC ?? entryBar?.C) ?? 0;
    const isCall = signal.direction === 'CALL';
    let exitIndex = bars1m.length - 1;
    let invalidationType = 'eod';
    let invalidationReason = 'EOD: signal still valid at close';
    let mfe = 0;
    let mae = 0;
    let mfeIndex = entryIndex;
    let maeIndex = entryIndex;

    for (let index = entryIndex; index < bars1m.length; index += 1) {
      const bar = bars1m[index];
      const high = num(bar.hH ?? bar.H) ?? entryPrice;
      const low = num(bar.hL ?? bar.L) ?? entryPrice;
      const haOpen = num(bar.hO ?? bar.O);
      const haClose = num(bar.hC ?? bar.C);
      const ma = num(bar[maStopLine]);
      const favorable = isCall ? high - entryPrice : entryPrice - low;
      const adverse = isCall ? entryPrice - low : high - entryPrice;
      if (favorable > mfe) { mfe = favorable; mfeIndex = index; }
      if (adverse > mae) { mae = adverse; maeIndex = index; }
      if (index === entryIndex || ma == null || haOpen == null || haClose == null) continue;
      if (useMa50CloseBreak) {
        if (isCall && haClose < ma) {
          exitIndex = index;
          invalidationType = 'invalidated';
          invalidationReason = `Signal invalidated: hC ${fmt(haClose)} < MA50 ${fmt(ma)}`;
          break;
        }
        if (!isCall && haClose > ma) {
          exitIndex = index;
          invalidationType = 'invalidated';
          invalidationReason = `Signal invalidated: hC ${fmt(haClose)} > MA50 ${fmt(ma)}`;
          break;
        }
      } else {
        if (isCall && haClose < haOpen && haClose < ma && haOpen < ma) {
          exitIndex = index;
          invalidationType = 'invalidated';
          invalidationReason = `Signal invalidated: HA body crossed below ${maStopLine.toUpperCase()} ${fmt(ma)}`;
          break;
        }
        if (!isCall && haClose >= haOpen && haClose > ma && haOpen > ma) {
          exitIndex = index;
          invalidationType = 'invalidated';
          invalidationReason = `Signal invalidated: HA body crossed above ${maStopLine.toUpperCase()} ${fmt(ma)}`;
          break;
        }
      }
    }

    const exitBar = bars1m[exitIndex];
    const exitPrice = num(exitBar?.hC ?? exitBar?.C) ?? entryPrice;
    const spyMove = isCall ? exitPrice - entryPrice : entryPrice - exitPrice;
    return {
      signal_id: signal.id,
      signal_index: signal.bar_index,
      entry_index: entryIndex,
      exit_index: exitIndex,
      direction: signal.direction,
      entry_price: entryPrice,
      exit_price: exitPrice,
      spy_move: spyMove,
      spy_move_pct: entryPrice > 0 ? spyMove / entryPrice : 0,
      bars_held: exitIndex - entryIndex,
      invalidation_type: invalidationType,
      invalidation_reason: invalidationReason,
      invalidation_line: invalidationType === 'invalidated' ? maStopLine : null,
      invalidation_value: invalidationType === 'invalidated' ? num(bars1m[exitIndex]?.[maStopLine]) : null,
      mfe,
      mfe_pct: entryPrice > 0 ? mfe / entryPrice : 0,
      mfe_bar_offset: mfeIndex - entryIndex,
      mfe_index: mfeIndex,
      mae,
      mae_pct: entryPrice > 0 ? mae / entryPrice : 0,
      mae_bar_offset: maeIndex - entryIndex,
      mae_index: maeIndex,
    };
  });
}

export function summarizeSetups(setups = []) {
  const mfe = median(setups.map((setup) => setup.mfe_pct));
  const mae = median(setups.map((setup) => setup.mae_pct));
  const duration = median(setups.map((setup) => setup.bars_held));
  const invalidated = setups.filter((setup) => setup.invalidation_type === 'invalidated').length;
  return {
    count: setups.length,
    invalidated,
    eod: setups.length - invalidated,
    medianMfePct: mfe,
    medianMaePct: mae,
    medianDuration: duration,
  };
}

export function setupForAnnotation(annotation, setups = []) {
  if (!annotation) return null;
  return setups.find((setup) => setup.signal_id === annotation.id || setup.signal_index === annotation.bar_index) || null;
}
