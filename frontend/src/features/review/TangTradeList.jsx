import { ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

function optionCode(side) {
  return side === 'PUT' ? 'P' : 'C';
}

function actionLabel(action) {
  if (action === 'buy_open') return 'Buy Open';
  if (action === 'sell_close') return 'Sell Close';
  return action || '--';
}

function minutesFromTime(value) {
  const match = String(value || '').match(/^(\d{1,2}):(\d{2})/);
  if (!match) return null;
  return Number(match[1]) * 60 + Number(match[2]);
}

function tradeTime(trade) {
  return String(trade?.time || trade?.t || '').slice(0, 5);
}

function barTime(bar) {
  return String(bar?.t || bar?.time || '').slice(0, 5);
}

function resolveTradeBarIndex(trade, bars) {
  const target = tradeTime(trade);
  if (!target || !bars.length) return 0;
  const exact = bars.findIndex((bar) => barTime(bar) === target);
  if (exact >= 0) return exact;

  const targetMinutes = minutesFromTime(target);
  if (targetMinutes == null) return 0;
  let nearest = 0;
  let bestDelta = Infinity;
  bars.forEach((bar, index) => {
    const delta = Math.abs((minutesFromTime(barTime(bar)) ?? targetMinutes) - targetMinutes);
    if (delta < bestDelta) {
      nearest = index;
      bestDelta = delta;
    }
  });
  return nearest;
}

function contractLabel(trade) {
  const strike = trade?.strike ?? '--';
  return `${strike}${optionCode(trade?.side)}`;
}

function strategyDirection(annotation) {
  return annotation?.direction || annotation?.type;
}

function findStrategyMatch(trade, strategyAnnotations = []) {
  const side = trade.side === 'PUT' ? 'PUT' : 'CALL';
  const tradeIndex = Number(trade.bar_index);
  const candidates = strategyAnnotations
    .filter((annotation) => annotation.type === 'signal' && strategyDirection(annotation) === side)
    .map((annotation) => ({
      annotation,
      delta: Math.abs(Number(annotation.bar_index) - tradeIndex),
    }))
    .filter((item) => Number.isFinite(item.delta))
    .sort((a, b) => a.delta - b.delta);

  const best = candidates[0];
  if (!best || best.delta > 3) return null;
  const signalTime = best.annotation.t || best.annotation.time || '--';
  const sign = Number(best.annotation.bar_index) <= tradeIndex ? '+' : '-';
  return {
    label: best.annotation.title || best.annotation.label || `${side} signal`,
    delta: best.delta,
    text: best.delta === 0 ? `策略同分钟 ${signalTime}` : `策略 ${signalTime} ${sign}${best.delta}m`,
  };
}

export function buildTangTradeRows(tangTrades, bars = [], strategyAnnotations = []) {
  const trades = Array.isArray(tangTrades) ? tangTrades : tangTrades?.trades || [];
  return trades.map((trade) => {
    const barIndex = resolveTradeBarIndex(trade, bars);
    const bar = bars[barIndex] || {};
    const normalized = {
      ...trade,
      id: trade.id || `tang-${trade.time}-${trade.strike}-${trade.side}`,
      side: trade.side === 'PUT' ? 'PUT' : 'CALL',
      bar_index: barIndex,
      t: barTime(bar) || tradeTime(trade),
      ts: bar.ts,
      price: bar.C,
      contract_label: contractLabel(trade),
    };
    return {
      ...normalized,
      strategy_match: findStrategyMatch(normalized, strategyAnnotations),
    };
  });
}

export function buildTangTradeAnnotations(tangTrades, bars = []) {
  return buildTangTradeRows(tangTrades, bars).map((trade) => ({
    id: `tang-trade-${trade.id}`,
    trade_id: trade.id,
    type: 'tang_trade',
    direction: trade.side,
    style: trade.side === 'PUT' ? 'tang-put' : 'tang-call',
    anchor_side: trade.side === 'PUT' ? 'top' : 'bottom',
    bar_index: trade.bar_index,
    t: trade.t,
    ts: trade.ts,
    title: `Tang ${trade.contract_label} ${trade.t}`,
    body: trade.note || `${actionLabel(trade.action)} SPY ${trade.contract_label}`,
    score: null,
    marker_label: `Tang ${trade.contract_label}`,
  }));
}

export function TangTradeList({ tangTrades, bars = [], strategyAnnotations = [], activeTradeId = '', onSelect }) {
  const [collapsed, setCollapsed] = useState(false);
  const rows = buildTangTradeRows(tangTrades, bars, strategyAnnotations);
  const notes = Array.isArray(tangTrades?.notes) ? tangTrades.notes : [];

  return (
    <div className="dr-tang-panel" data-collapsed={collapsed ? 'true' : 'false'}>
      <button
        type="button"
        className="dr-tang-header"
        onClick={() => setCollapsed((value) => !value)}
        aria-expanded={!collapsed}
      >
        <span className="dr-tang-header-main">
          {collapsed ? <ChevronRight size={14} strokeWidth={2.4} /> : <ChevronDown size={14} strokeWidth={2.4} />}
          <span>Tang Trades</span>
        </span>
        <strong>{rows.length}</strong>
      </button>
      {!collapsed && (
        <div className="dr-tang-body">
          {!rows.length && (
            <div className="dr-tang-empty">
              <strong>未记录 SPY 0DTE 入场</strong>
              {notes[0] && <small>{notes[0]}</small>}
            </div>
          )}
          {rows.map((trade) => (
            <button
              key={trade.id}
              type="button"
              className={`dr-tang-card ${activeTradeId === trade.id ? 'active' : ''}`}
              data-side={trade.side.toLowerCase()}
              onClick={() => onSelect?.(trade)}
            >
              <div className="dr-tang-line">
                <span className="dr-tang-time">{trade.t || trade.time}</span>
                <span className="dr-tang-badge">Tang</span>
                <strong>{trade.contract_label}</strong>
              </div>
              <div className="dr-tang-meta">
                <span>{actionLabel(trade.action)}</span>
                <span>SPY {trade.expiry}</span>
                {trade.price != null && <span>@ {Number(trade.price).toFixed(2)}</span>}
              </div>
              <div className="dr-tang-match">
                {trade.strategy_match ? trade.strategy_match.text : '未匹配到 3 分钟内同向策略进场'}
              </div>
              {trade.note && <p>{trade.note}</p>}
            </button>
          ))}
          {!!rows.length && notes.map((note) => (
            <div className="dr-tang-note" key={note}>{note}</div>
          ))}
        </div>
      )}
    </div>
  );
}
