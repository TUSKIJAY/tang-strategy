const WIDTH = 1200;
const HEIGHT = 620;
const PRICE_HEIGHT = 470;
const VOLUME_TOP = 500;
const VOLUME_HEIGHT = 90;
const PAD_L = 54;
const PAD_R = 72;
const PAD_T = 24;

function finite(value) {
  return Number.isFinite(Number(value));
}

function priceOf(bar, key) {
  return finite(bar?.[key]) ? Number(bar[key]) : null;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function buildPath(bars, key, xOf, yOf) {
  let path = '';
  bars.forEach((bar, localIndex) => {
    const value = priceOf(bar, key);
    if (value == null) return;
    path += `${path ? 'L' : 'M'}${xOf(localIndex).toFixed(2)},${yOf(value).toFixed(2)}`;
  });
  return path;
}

function formatPrice(value) {
  return finite(value) ? Number(value).toFixed(2) : '--';
}

function compactVolume(value) {
  if (!finite(value)) return '--';
  const n = Number(value);
  if (Math.abs(n) >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
  return String(Math.round(n));
}

function markerColor(annotation) {
  if (annotation.type === 'expired') return '#9B6FCC';
  if (annotation.type === 'setup') return '#5B9BD5';
  if (annotation.direction === 'PUT') return '#C94040';
  return '#4CAF50';
}

function markerText(annotation) {
  if (annotation.type === 'expired') return 'X';
  if (annotation.type === 'setup') return 'S';
  return annotation.direction || annotation.type || 'I';
}

export function DailyReviewChart({ bars = [], annotations = [], activeAnnotationId, onSelectAnnotation, focusRange = null }) {
  const total = bars.length;
  const focusStart = focusRange ? clamp(focusRange.start, 0, Math.max(0, total - 1)) : 0;
  const focusEnd = focusRange ? clamp(focusRange.end, focusStart, Math.max(0, total - 1)) : Math.max(0, total - 1);
  const visibleStart = total ? focusStart : 0;
  const visibleEnd = total ? focusEnd : -1;
  const visible = total ? bars.slice(visibleStart, visibleEnd + 1) : [];
  const visibleAnnotations = annotations.filter((annotation) => annotation.bar_index >= visibleStart && annotation.bar_index <= visibleEnd);
  const prices = visible.flatMap((bar) => [bar.H, bar.L, bar.hH, bar.hL, bar.m10, bar.m50, bar.m200, bar.vw]).map(Number).filter(Number.isFinite);
  const minPrice = prices.length ? Math.min(...prices) : 0;
  const maxPrice = prices.length ? Math.max(...prices) : 1;
  const pricePad = Math.max((maxPrice - minPrice) * 0.08, 0.5);
  const lo = minPrice - pricePad;
  const hi = maxPrice + pricePad;
  const maxVolume = Math.max(1, ...visible.map((bar) => Number(bar.V || bar.volume || 0)));
  const step = visible.length > 1 ? (WIDTH - PAD_L - PAD_R) / (visible.length - 1) : 8;
  const candleW = Math.max(2, Math.min(8, step * 0.62));
  const xOf = (localIndex) => PAD_L + localIndex * step;
  const yOf = (price) => PAD_T + ((hi - price) / (hi - lo)) * (PRICE_HEIGHT - PAD_T);
  const volumeY = (volume) => VOLUME_TOP + VOLUME_HEIGHT - (Number(volume || 0) / maxVolume) * VOLUME_HEIGHT;
  const gridPrices = Array.from({ length: 6 }, (_, index) => lo + ((hi - lo) * index) / 5).reverse();
  const timeMarks = visible.length ? [...new Set([0, Math.floor(visible.length * 0.25), Math.floor(visible.length * 0.5), Math.floor(visible.length * 0.75), visible.length - 1])] : [];

  return (
    <svg className="dr-chart-svg" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Daily review candlestick chart">
      <defs>
        <linearGradient id="chartShade" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor="#22221f" />
          <stop offset="100%" stopColor="#181817" />
        </linearGradient>
        <clipPath id="chartClip"><rect x={PAD_L} y={PAD_T} width={WIDTH - PAD_L - PAD_R} height={PRICE_HEIGHT - PAD_T} /></clipPath>
      </defs>
      <rect width={WIDTH} height={HEIGHT} fill="url(#chartShade)" />
      {gridPrices.map((price) => (
        <g key={price}>
          <line x1={PAD_L} x2={WIDTH - PAD_R} y1={yOf(price)} y2={yOf(price)} stroke="rgba(255,255,255,.06)" />
          <text x={WIDTH - 62} y={yOf(price) + 4} fill="#8A8A85" fontSize="11" fontFamily="monospace">{formatPrice(price)}</text>
        </g>
      ))}
      {timeMarks.map((localIndex) => visible[localIndex] && (
        <g key={localIndex}>
          <line x1={xOf(localIndex)} x2={xOf(localIndex)} y1={PAD_T} y2={VOLUME_TOP + VOLUME_HEIGHT} stroke="rgba(255,255,255,.04)" />
          <text x={xOf(localIndex)} y={HEIGHT - 13} fill="#5A5A56" fontSize="11" textAnchor="middle" fontFamily="monospace">{visible[localIndex].t || visible[localIndex].time}</text>
        </g>
      ))}
      <g clipPath="url(#chartClip)">
        {visible.map((bar, localIndex) => {
          const open = priceOf(bar, 'hO') ?? priceOf(bar, 'O') ?? 0;
          const close = priceOf(bar, 'hC') ?? priceOf(bar, 'C') ?? 0;
          const high = priceOf(bar, 'hH') ?? priceOf(bar, 'H') ?? Math.max(open, close);
          const low = priceOf(bar, 'hL') ?? priceOf(bar, 'L') ?? Math.min(open, close);
          const up = close >= open;
          const x = xOf(localIndex);
          const bodyTop = Math.min(yOf(open), yOf(close));
          const bodyHeight = Math.max(1, Math.abs(yOf(open) - yOf(close)));
          return (
            <g key={`${bar.ts || bar.t}-${localIndex}`}>
              <line x1={x} x2={x} y1={yOf(high)} y2={yOf(low)} stroke={up ? '#4CAF50' : '#C94040'} strokeWidth="1" opacity=".82" />
              <rect x={x - candleW / 2} y={bodyTop} width={candleW} height={bodyHeight} rx="1" fill={up ? '#4CAF50' : '#C94040'} opacity=".9" />
            </g>
          );
        })}
        <path d={buildPath(visible, 'm10', xOf, yOf)} fill="none" stroke="#E8A838" strokeWidth="1.3" opacity=".9" />
        <path d={buildPath(visible, 'm50', xOf, yOf)} fill="none" stroke="#5B9BD5" strokeWidth="1.2" opacity=".86" />
        <path d={buildPath(visible, 'm200', xOf, yOf)} fill="none" stroke="#8B9A6D" strokeWidth="1.2" opacity=".86" />
        <path d={buildPath(visible, 'vw', xOf, yOf)} fill="none" stroke="#9B6FCC" strokeWidth="1.1" strokeDasharray="4 4" opacity=".84" />
        {visibleAnnotations.map((annotation) => {
          const localIndex = annotation.bar_index - visibleStart;
          const bar = visible[localIndex];
          if (!bar) return null;
          const put = annotation.direction === 'PUT';
          const y = put ? yOf(priceOf(bar, 'hH') ?? bar.H) - 18 : yOf(priceOf(bar, 'hL') ?? bar.L) + 18;
          const active = annotation.id === activeAnnotationId;
          return (
            <g key={annotation.id} className="dr-signal-marker" onClick={() => onSelectAnnotation?.(annotation.id)}>
              <circle cx={xOf(localIndex)} cy={y} r={active ? 8 : 5} fill={markerColor(annotation)} stroke="#E8E7E3" strokeWidth={active ? 2 : 1} />
              <text x={xOf(localIndex)} y={put ? y - 10 : y + 20} textAnchor="middle" fill={markerColor(annotation)} fontSize="10" fontFamily="monospace">{markerText(annotation)}</text>
            </g>
          );
        })}
      </g>
      <line x1={PAD_L} x2={WIDTH - PAD_R} y1={VOLUME_TOP - 12} y2={VOLUME_TOP - 12} stroke="rgba(255,255,255,.09)" />
      {visible.map((bar, localIndex) => {
        const up = Number(bar.C) >= Number(bar.O);
        const v = Number(bar.V || bar.volume || 0);
        return <rect key={`v-${localIndex}`} x={xOf(localIndex) - candleW / 2} y={volumeY(v)} width={candleW} height={VOLUME_TOP + VOLUME_HEIGHT - volumeY(v)} fill={up ? 'rgba(76,175,80,.34)' : 'rgba(201,64,64,.34)'} />;
      })}
      <text x={PAD_L} y={VOLUME_TOP - 22} fill="#8A8A85" fontSize="11" fontFamily="monospace">VOL max {compactVolume(maxVolume)} · bars {visibleStart + 1}-{visibleEnd + 1}/{total}</text>
      <g className="dr-legend">
        <text x={PAD_L} y="18" fill="#E8A838" fontSize="11" fontFamily="monospace">MA10</text>
        <text x={PAD_L + 48} y="18" fill="#5B9BD5" fontSize="11" fontFamily="monospace">MA50</text>
        <text x={PAD_L + 96} y="18" fill="#8B9A6D" fontSize="11" fontFamily="monospace">MA200</text>
        <text x={PAD_L + 152} y="18" fill="#9B6FCC" fontSize="11" fontFamily="monospace">VWAP</text>
      </g>
    </svg>
  );
}
