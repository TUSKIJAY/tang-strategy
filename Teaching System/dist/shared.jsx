/* shared.jsx — Layout, Sidebar, TopNav, Data */

let MODULES = [
  { id: 'environment', num: '01', name: '环境判断', icon: 'analytics', tag: '核心', desc: '在分析任何局部形态之前，先确定主要市场背景。判断主趋势方向、均线排列和是否允许进入执行层。', tags: ['5分钟背景', '均线排列'], goal: '先判断方向是否清楚，再决定是否进入 1分钟观察。' },
  { id: 'ma10', num: '02', name: 'MA10核心入场', icon: 'trending_up', tag: '主力', desc: '在清晰趋势背景下，等待价格回踩或反抽 MA10，并用确认 K 判断是否执行。', tags: ['Support MA10', 'Reject MA10'], goal: '区分标准回踩、边缘降级和看似触发但不能做的反例。' },
  { id: 'signal-b', num: '03', name: '信号B', icon: 'bolt', tag: '进阶', desc: '核心入场错过后，只在趋势动量仍强且二次确认出现时参与延续。', tags: ['延续', 'VWAP拦截'], goal: '避免把二次确认做成末端追价。' },
  { id: 'candle-quality', num: '04', name: 'K线质量', icon: 'grid_view', tag: '过滤', desc: '用实体、影线和收盘位置判断确认 K 是否真的支持执行。', tags: ['实体比例', '衰竭'], goal: '看到质量不合格的 K 线时能主动降级或放弃。' },
  { id: 'levels', num: '05', name: '关卡空间', icon: 'layers', tag: '结构', desc: '检查 VWAP、MA50、MA200、盘前高低点等关卡是否挡住目标空间。', tags: ['VWAP', 'MA200'], goal: '在信号触发时同步判断风险回报是否成立。' },
  { id: 'exit', num: '06', name: '出场管理', icon: 'logout', tag: '风控', desc: '开仓前定义止损，运行中按结构分批止盈和移动止损。', tags: ['止损', '止盈'], goal: '把离场动作写进计划，而不是交给临场情绪。' },
];

let MISTAKES = [
  { id: 'err-01', name: '提前进场', icon: 'speed', freq: '高频', desc: '在确认 K 收盘之前预判入场，把观察动作误当成执行动作。', symptom: '参考 K 还没收完就先下单。', correction: '等确认 K 收盘，把触发和执行拆成两个动作。', category: '进场错误', rule: '等待确认K收盘', rule_ids: ['support_ma10', 'reject_ma10'], module: 'ma10' },
  { id: 'err-02', name: '追鱼尾', icon: 'sprint', freq: null, desc: '最佳结构点已经过去后追入，止损变宽且目标空间变窄。', symptom: '看到连续加速才追，进场点远离原始结构。', correction: '错过就等下一次，只做二次确认，不做情绪追价。', category: '进场错误', rule: '错过就等下一次', rule_ids: ['signal_b'], module: 'ma10' },
  { id: 'err-03', name: '忽略5分钟背景', icon: 'hourglass_bottom', freq: '观察中', desc: '只盯 1分钟触发形态，忽略 5分钟方向不清或背景冲突。', symptom: '局部像触发，但大背景并不支持。', correction: '先过 5分钟背景，再进入 1分钟观察。', category: '进场错误', rule: '背景不清晰不做', rule_ids: ['background_5m'], module: 'environment' },
  { id: 'err-04', name: '该走不走', icon: 'front_hand', freq: null, desc: '忽视明确失效信号，让计划交易变成希望单。', symptom: '止损条件出现后仍继续扛单。', correction: '开仓前定义止损，失效即离场。', category: '出场错误', rule: '失效即离场', rule_ids: ['moving_stop'], module: 'exit' },
  { id: 'err-05', name: '关卡太近还做', icon: 'block', freq: null, desc: '目标位空间不足时仍然进场，忽视风险回报比。', symptom: '刚入场就撞 VWAP、MA200 或前高前低。', correction: '空间不足时降级观察或直接不做。', category: '过滤错误', rule: '空间不足不做', rule_ids: ['vwap_distance_filter'], module: 'levels' },
  { id: 'err-06', name: 'K线质量差还做', icon: 'grid_view', freq: null, desc: '确认 K 出现长影线、实体缩小或收盘不干净时仍然执行。', symptom: '只看方向，不看实体和收盘位置。', correction: '质量不合格时等待下一根确认。', category: '过滤错误', rule: '确认K质量必须通过', rule_ids: ['candle_body_quality'], module: 'candle-quality' },
];

let CASES = [];

let RULES = [];
let SEGMENTS = [];
let TRAINING_ITEMS = [];

const TOP_NAV_ITEMS = [
  { id: 'hub', label: '策略地图' },
  { id: 'case', label: '案例剧场' },
  { id: 'playbook', label: '规则库' },
  { id: 'archives', label: '案例档案' },
  { id: 'mistakes', label: '错误日志' },
];

const SIDEBAR_ITEMS = [
  { id: 'environment', icon: 'analytics', label: '环境判断' },
  { id: 'ma10', icon: 'trending_up', label: 'MA10核心入场' },
  { id: 'signal-b', icon: 'bolt', label: '信号B' },
  { id: 'candle-quality', icon: 'grid_view', label: 'K线质量' },
  { id: 'levels', icon: 'layers', label: '关卡空间' },
  { id: 'exit', icon: 'logout', label: '出场管理' },
  { id: 'mistakes', icon: 'warning', label: '错误日志' },
];

const DATA_PATHS = {
  rules: '../rules/compiled/index.json',
  cases: '../cases/index.json',
  segments: '../data/processed/teaching_segments.json',
  training: '../training/checkpoints.json',
};

function normalizeRule(raw) {
  return {
    ...raw,
    id: raw.id || raw.rule_id,
    module: raw.module || raw.module_id,
    filter: raw.filter || (Array.isArray(raw.filters) ? raw.filters.join(' / ') : raw.filters),
  };
}

function normalizeCase(raw) {
  const gradeLabelMap = { standard: '标准例', edge: '边缘例', anti: '反例', candidate: '待审核' };
  return {
    ...raw,
    id: raw.id || raw.case_id,
    module: raw.module || raw.module_id,
    grade: raw.grade_label || gradeLabelMap[raw.grade] || raw.grade || '标准例',
    entry: raw.entry || raw.answer?.action || '—',
    stop: raw.stop || '—',
    rr: raw.rr || '—',
    result: raw.result || raw.answer?.decision || '教学样本',
  };
}

function normalizeTraining(raw) {
  const items = raw.training || raw.items || [];
  return items.map(item => ({
    ...item,
    steps: item.steps || item.decision_steps || [],
  }));
}

function applyRuntimeData(payload) {
  RULES = (payload.rules?.rules || payload.rules || []).map(normalizeRule);
  CASES = (payload.cases?.cases || payload.cases || []).map(normalizeCase);
  SEGMENTS = payload.segments?.segments || [];
  TRAINING_ITEMS = normalizeTraining(payload.training || {});
  Object.assign(window, { MODULES, MISTAKES, CASES, RULES, SEGMENTS, TRAINING_ITEMS });
}

function fetchJson(path) {
  return fetch(path, { cache: 'no-store' }).then(res => {
    if (!res.ok) throw new Error(`${path}: ${res.status}`);
    return res.json();
  });
}

function readInlineJson(id) {
  // Standalone build inlines data as <script type="application/json" id="...">；
  // dev mode 下没有这个标签，返回 null 走 fetch 路径。
  const node = document.getElementById(id);
  if (!node || !node.textContent) return null;
  try {
    return JSON.parse(node.textContent);
  } catch (err) {
    console.warn(`[teaching-system] inline JSON #${id} parse failed`, err);
    return null;
  }
}

function loadDataset() {
  const inline = {
    rules: readInlineJson('inline-data-rules'),
    cases: readInlineJson('inline-data-cases'),
    segments: readInlineJson('inline-data-segments'),
    training: readInlineJson('inline-data-training'),
  };
  if (inline.rules && inline.cases && inline.segments && inline.training) {
    return Promise.resolve(inline);
  }
  return Promise.all([
    fetchJson(DATA_PATHS.rules),
    fetchJson(DATA_PATHS.cases),
    fetchJson(DATA_PATHS.segments),
    fetchJson(DATA_PATHS.training),
  ]).then(([rules, cases, segments, training]) => ({ rules, cases, segments, training }));
}

function useAppData() {
  const [state, setState] = React.useState({ loading: true, error: null });
  React.useEffect(() => {
    let cancelled = false;
    loadDataset().then(({ rules, cases, segments, training }) => {
      if (cancelled) return;
      applyRuntimeData({ rules, cases, segments, training });
      setState({ loading: false, error: null });
    }).catch(error => {
      console.error('[teaching-system] failed to load runtime data', error);
      if (!cancelled) setState({ loading: false, error });
    });
    return () => { cancelled = true; };
  }, []);
  return state;
}

function LoadingScreen({ error }) {
  return (
    <div className="min-h-screen bg-[#FAF9F5] text-[#1A1A19] flex items-center justify-center p-8 font-['Work_Sans']">
      <div className="max-w-md border border-[#D8D1C3] bg-white p-6 rounded">
        <h1 className="font-['Newsreader'] text-[28px] mb-2">{error ? '数据加载失败' : '正在加载教学系统'}</h1>
        <p className="text-[#6B6B66] text-[14px] leading-[1.6]">
          {error ? '请通过本地服务器打开 dist 目录，或检查 rules / cases / training JSON 是否存在。' : '正在读取 Rule Contract、Case Manifest 与教学切片。'}
        </p>
      </div>
    </div>
  );
}

function useHashRouter() {
  const [route, setRoute] = React.useState(() => {
    const h = window.location.hash.slice(1) || 'hub';
    return h;
  });
  React.useEffect(() => {
    const handler = () => setRoute(window.location.hash.slice(1) || 'hub');
    window.addEventListener('hashchange', handler);
    return () => window.removeEventListener('hashchange', handler);
  }, []);
  const navigate = React.useCallback((r) => { window.location.hash = r; }, []);
  return { route, navigate };
}

function TopNav({ activeTop, navigate }) {
  return (
    <header className="bg-[#FAF9F5] border-b border-[#D8D1C3] z-10 shrink-0">
      <div className="flex justify-between items-center h-16 px-6 w-full max-w-[1280px] mx-auto">
        <div className="flex items-center gap-8">
          <span className="text-xl font-semibold tracking-tight text-[#1A1A19] font-['Newsreader']">SPY 执行手册</span>
          <nav className="hidden md:flex gap-6">
            {TOP_NAV_ITEMS.map(item => (
              <a key={item.id} onClick={() => navigate(item.id)}
                className={`cursor-pointer font-['Newsreader'] transition-colors duration-200 ${activeTop === item.id ? 'text-[#1A1A19] border-b-2 border-[#8B9A6D] pb-1' : 'text-[#6B6B66] hover:text-[#1A1A19]'}`}>
                {item.label}
              </a>
            ))}
          </nav>
        </div>
        {/* 账号入口暂未启用 — 业务尚无登录态 */}
        {/* <button className="text-[#6B6B66] hover:text-[#1A1A19] transition-colors p-2 rounded-full">
          <span className="material-symbols-outlined">account_circle</span>
        </button> */}
      </div>
    </header>
  );
}

function Sidebar({ activeModule, navigate, onModuleClick }) {
  return (
    <nav className="hidden lg:flex flex-col h-full py-8 bg-[#FAF9F5] font-['Newsreader'] tracking-wide text-sm w-64 border-r border-[#D8D1C3] shrink-0">
      <div className="px-6 mb-8">
        <h2 className="font-bold text-[#1A1A19] font-h2 text-[24px] leading-[1.3] mb-1">执行指南</h2>
        <p className="text-[#6B6B66] font-['Space_Grotesk'] text-[14px]">Trading Playbook v1.0</p>
      </div>
      <ul className="flex-1 space-y-1 px-4 overflow-y-auto">
        {SIDEBAR_ITEMS.map(item => {
          const isActive = activeModule === item.id;
          return (
            <li key={item.id}>
              <a onClick={() => onModuleClick ? onModuleClick(item.id) : navigate(item.id === 'mistakes' ? 'mistakes' : `module/${item.id}`)}
                className={`flex items-center gap-3 px-4 py-2 cursor-pointer transition-all active:scale-[0.98] ${isActive ? 'bg-[#EDE9DD] border-r-4 border-[#8B9A6D] text-[#1A1A19] font-bold' : 'text-[#6B6B66] opacity-90 hover:bg-[#F0ECE1]'}`}>
                <span className="material-symbols-outlined text-[20px]">{item.icon}</span>
                <span>{item.label}</span>
              </a>
            </li>
          );
        })}
      </ul>
      <div className="mt-auto px-4 space-y-1 border-t border-[#D8D1C3] pt-4 mx-4">
        {/* 设置入口暂未启用 — 业务尚无可配置项 */}
        {/* <a className="flex items-center gap-3 px-4 py-2 text-[#6B6B66] opacity-90 hover:bg-[#F0ECE1] transition-all cursor-pointer">
          <span className="material-symbols-outlined text-[20px]">settings</span><span>设置</span>
        </a> */}
        <a className="flex items-center gap-3 px-4 py-2 text-[#6B6B66] opacity-90 hover:bg-[#F0ECE1] transition-all cursor-pointer">
          <span className="material-symbols-outlined text-[20px]">menu_book</span><span>术语表</span>
        </a>
      </div>
    </nav>
  );
}

function AppLayout({ children, activeTop, activeModule, navigate, onModuleClick }) {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#FAF9F5] text-[#1A1A19] font-['Work_Sans'] antialiased">
      <TopNav activeTop={activeTop} navigate={navigate} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar activeModule={activeModule} navigate={navigate} onModuleClick={onModuleClick} />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}

function getSegment(segmentId) {
  return SEGMENTS.find(s => s.id === segmentId) || SEGMENTS[0];
}

function getCase(caseId) {
  return CASES.find(c => c.id === caseId || c.case_id === caseId) || CASES[0];
}

function getCaseSegment(caseLike) {
  const c = typeof caseLike === 'string' ? getCase(caseLike) : caseLike;
  return c ? getSegment(c.segment_id) : SEGMENTS[0];
}

function checkpointFor(segment, key) {
  return (segment?.derived?.checkpoints || []).find(c => c.key === key);
}

/* === Checkpoint → chart highlight range ===
 * Maps a single `derived.checkpoints[i]` entry to engine highlight ranges.
 * Returns an array (0 or 1 item for the MVP) of
 *   { timeframe, startIndex, endIndex, style }
 * - 'olive' style for passed checkpoints, 'red' for failed, 'marker' for unknown.
 * - 5m-scope checkpoints (trend_ok / ma_alignment_ok) span the full 5m window.
 * - Bar-scope checkpoints center on the decision bar (±0 / +1 / to-end).
 * - Checkpoints with no bar_index (e.g. `forbidden_absent`) return [].
 */
function checkpointToRanges(checkpoint, segment, caseObj) {
  if (!checkpoint || !segment) return [];
  const style = checkpoint.status === 'failed' || (checkpoint.passed === false && checkpoint.status == null)
    ? 'red'
    : checkpoint.status === 'passed' || checkpoint.passed === true
      ? 'olive'
      : 'marker';
  const bars1m = segment.bars_1m || [];
  const bars5m = segment.bars_5m || [];
  const decisionIdx = caseObj?.decision_bar?.bar_index
    ?? segment.derived?.signal_bar_index
    ?? checkpoint.bar_index
    ?? null;

  switch (checkpoint.key) {
    case 'trend_ok':
    case 'ma_alignment_ok':
      if (!bars5m.length) return [];
      return [{ timeframe: '5m', startIndex: 0, endIndex: bars5m.length - 1, style }];

    case 'confirm_bar': {
      if (decisionIdx == null || !bars1m.length) return [];
      const start = decisionIdx;
      const end = Math.min(bars1m.length - 1, decisionIdx + 1);
      return [{ timeframe: '1m', startIndex: start, endIndex: end, style }];
    }

    case 'reward_ok': {
      if (decisionIdx == null || !bars1m.length) return [];
      return [{ timeframe: '1m', startIndex: decisionIdx, endIndex: bars1m.length - 1, style }];
    }

    case 'touch_ma10':
    case 'body_not_cross':
    case 'stop_defined':
    case 'vwap_side':
    case 'vwap_intercept': {
      const idx = checkpoint.bar_index ?? decisionIdx;
      if (idx == null || !bars1m.length) return [];
      return [{ timeframe: '1m', startIndex: idx, endIndex: idx, style }];
    }

    case 'forbidden_absent':
    default:
      if (checkpoint.bar_index != null) {
        return [{ timeframe: '1m', startIndex: checkpoint.bar_index, endIndex: checkpoint.bar_index, style }];
      }
      return [];
  }
}

function checkpointPillClass(checkpoint) {
  const status = checkpoint?.status || (checkpoint?.passed === true ? 'passed' : checkpoint?.passed === false ? 'failed' : 'unknown');
  if (status === 'passed') return 'border-[#8B9A6D] text-[#56623F] bg-[#F4F6EE]';
  if (status === 'failed') return 'border-[#C9897E] text-[#8A4038] bg-[#FFF4F2]';
  if (status === 'warning') return 'border-[#D0A650] text-[#765C17] bg-[#FFF8E6]';
  return 'border-[#D8D1C3] text-[#6B6B66] bg-white';
}

/* === Training step → chart highlight ranges ===
 * A training step has `checkpoint_keys: string[]`. We resolve each key
 * through `checkpointToRanges`. When the resulting set mixes 1m and 5m,
 * prefer 1m (the primary teaching tf); users can manually flip tf via
 * the toolbar to inspect 5m context. Returns `null` when no range exists
 * so callers can pass it straight to `KlineView`.
 */
function stepToHighlightRanges(step, segment, caseObj) {
  if (!step || !segment) return null;
  const keys = step.checkpoint_keys || [];
  const ranges = [];
  keys.forEach(key => {
    const cp = checkpointFor(segment, key);
    if (!cp) return;
    checkpointToRanges(cp, segment, caseObj).forEach(r => ranges.push(r));
  });
  if (!ranges.length) return null;
  const has1m = ranges.some(r => r.timeframe === '1m');
  return has1m ? ranges.filter(r => r.timeframe === '1m') : ranges;
}

function MiniKlineSvg({ segment, mode = 'mini', height = 160, revealIndex = null }) {
  const barsRaw = segment?.bars_1m || [];
  const bars = revealIndex == null ? barsRaw : barsRaw.slice(0, Math.max(1, revealIndex + 1));
  const compact = mode === 'mini';
  const width = compact ? 360 : 920;
  const chartHeight = compact ? height - 16 : height - 58;
  const pad = compact ? 10 : 28;
  const visibleBars = compact ? bars.slice(-34) : bars;
  const prices = visibleBars.flatMap(b => {
    const visibleRefs = compact
      ? [b.hH ?? b.H, b.hL ?? b.L, b.m10]
      : [b.hH ?? b.H, b.hL ?? b.L, b.m10, b.m50, b.m200, b.vw];
    return visibleRefs.filter(v => typeof v === 'number' && v > 0);
  });
  const rawMin = prices.length ? Math.min(...prices) : 0;
  const rawMax = prices.length ? Math.max(...prices) : 1;
  const rawSpan = Math.max(0.01, rawMax - rawMin);
  const min = rawMin - rawSpan * (compact ? 0.08 : 0.05);
  const max = rawMax + rawSpan * (compact ? 0.08 : 0.05);
  const span = Math.max(0.01, max - min);
  const x = i => pad + (i + 0.5) * ((width - pad * 2) / Math.max(1, visibleBars.length));
  const y = v => pad + (max - v) / span * (chartHeight - pad * 2);
  const candleW = Math.max(2, Math.min(compact ? 5 : 9, ((width - pad * 2) / Math.max(1, visibleBars.length)) * 0.55));
  const lineFor = key => visibleBars
    .map((b, i) => typeof b[key] === 'number' && b[key] > 0 ? `${x(i)},${y(b[key])}` : null)
    .filter(Boolean)
    .join(' ');
  const signalIndex = segment?.derived?.signal_bar_index;
  const signalVisibleIndex = signalIndex == null ? -1 : signalIndex - Math.max(0, bars.length - visibleBars.length);
  const signalBar = visibleBars[signalVisibleIndex];

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full block" role="img" aria-label={segment?.title || 'K线证据图'}>
      <rect x="0" y="0" width={width} height={height} fill="#FFFFFF" />
      {[0, 0.25, 0.5, 0.75, 1].map((t, i) => (
        <line key={i} x1={pad} x2={width - pad} y1={pad + t * (chartHeight - pad * 2)} y2={pad + t * (chartHeight - pad * 2)} stroke="#E6E0D3" strokeWidth="1" />
      ))}
      {!compact && <polyline points={lineFor('m50')} fill="none" stroke="#C0A86B" strokeWidth="1.2" opacity="0.75" />}
      <polyline points={lineFor('m10')} fill="none" stroke="#8B9A6D" strokeWidth={compact ? 1.4 : 1.8} />
      {!compact && <polyline points={lineFor('m200')} fill="none" stroke="#6B6B66" strokeWidth="1" opacity="0.5" />}
      {visibleBars.map((b, i) => {
        const open = b.hO ?? b.O;
        const close = b.hC ?? b.C;
        const high = b.hH ?? b.H;
        const low = b.hL ?? b.L;
        const up = close >= open;
        const color = up ? '#5E7D5B' : '#9B5950';
        const bodyY = Math.min(y(open), y(close));
        const bodyH = Math.max(1.5, Math.abs(y(open) - y(close)));
        return (
          <g key={`${b.t}-${i}`}>
            <line x1={x(i)} x2={x(i)} y1={y(high)} y2={y(low)} stroke={color} strokeWidth="1" />
            <rect x={x(i) - candleW / 2} y={bodyY} width={candleW} height={bodyH} fill={up ? '#FFFFFF' : color} stroke={color} strokeWidth="1" />
          </g>
        );
      })}
      {signalBar && (
        <g>
          <line x1={x(signalVisibleIndex)} x2={x(signalVisibleIndex)} y1={pad} y2={chartHeight - pad} stroke="#8B9A6D" strokeWidth="1.5" strokeDasharray="4 4" />
          <circle cx={x(signalVisibleIndex)} cy={y(signalBar.hC ?? signalBar.C)} r={compact ? 4 : 6} fill="#8B9A6D" />
        </g>
      )}
      {!compact && (
        <g fontFamily="Space Grotesk, sans-serif" fontSize="12" fill="#6B6B66">
          <text x={pad} y={height - 25}>{segment?.date || ''} · {segment?.title || ''}</text>
          <text x={width - pad - 210} y={height - 25}>MA10 / MA50 / MA200 · HA</text>
        </g>
      )}
    </svg>
  );
}

/* === 真实引擎适配层 ===
 * 策略：
 *  - mini 模式继续使用 SVG 缩略图（列表页不应 spawn 完整引擎）
 *  - evidence / lab 模式挂载 window.KlineEngine
 *  - 当 segmentId 变化时 loadData 复用实例，路由卸载时 destroy
 *  - evidence 模式通过 .kline-host--evidence CSS 隐藏工具栏和 HUD
 *  - 决策 bar 通过 scrollTo({ timeframe, barIndex, highlight: true, center: true }) 高亮闪烁
 */

const CASE_RELEVANT_MA = {
  ma10: ['m10', 'm50', 'm200', 'vw'],
  'signal-b': ['m10', 'm50', 'm200', 'vw'],
  'candle-quality': ['m10', 'm50', 'vw'],
  levels: ['m10', 'm50', 'm200', 'vw'],
  environment: ['m10', 'm50', 'm200', 'vw'],
  exit: ['m10', 'm50', 'm200', 'vw'],
};

// MA legend metadata — keep colors aligned with engine drawMALines() / toolbar swatches.
const MA_LEGEND = [
  { key: 'm5',   label: 'MA5',   color: '#eab308' },
  { key: 'm10',  label: 'MA10',  color: '#e6a23c' },
  { key: 'm20',  label: 'MA20',  color: '#ec4899' },
  { key: 'm30',  label: 'MA30',  color: '#14b8a6' },
  { key: 'm50',  label: 'MA50',  color: '#409eff' },
  { key: 'm60',  label: 'MA60',  color: '#6366f1' },
  { key: 'm120', label: 'MA120', color: '#f43f5e' },
  { key: 'm200', label: 'MA200', color: '#67c23a' },
  { key: 'vw',   label: 'VWAP',  color: '#a855f7' },
];

function segmentToEnginePayload(segment, caseObj) {
  if (!segment) return null;
  const signalIndex = segment?.derived?.signal_bar_index ?? 0;
  const decisionTf = caseObj?.decision_bar?.timeframe || '1m';
  const decisionIndex = caseObj?.decision_bar?.bar_index ?? signalIndex;
  return {
    meta: {
      title: caseObj?.title || segment.title || segment.id,
      ticker: caseObj?.ticker || 'SPY',
      date: segment.date,
      source: `teaching_segments.${segment.id}`,
      initial_timeframe: decisionTf,
      initial_index_1m: decisionTf === '1m' ? decisionIndex : signalIndex,
      initial_index_5m: decisionTf === '5m' ? decisionIndex : Math.max(0, Math.floor(signalIndex / 5)),
    },
    bars_1m: segment.bars_1m || [],
    bars_5m: segment.bars_5m || [],
    annotations_1m: segment.annotations_1m || [],
    annotations_5m: segment.annotations_5m || [],
  };
}

function KlineEngineAdapter({ mode, segment, caseObj, height, revealCutoff, highlightRanges, lockPlayback, onEngineReady, onPlaybackChange, onMaVisibilityChange, onHoverChange }) {
  const hostRef = React.useRef(null);
  const engineRef = React.useRef(null);
  const currentSegmentIdRef = React.useRef(null);
  const resetTargetRef = React.useRef({ timeframe: '1m', index: 0 });
  // Track latest cutoff/highlight so the loadData effect (which runs *after*
  // the prop-change effects on first mount) can re-apply them once the
  // engine finishes loading — otherwise loadData() wipes any prior state.
  const revealCutoffRef = React.useRef(revealCutoff);
  const highlightRangesRef = React.useRef(highlightRanges);
  React.useEffect(() => { revealCutoffRef.current = revealCutoff; }, [revealCutoff]);
  React.useEffect(() => { highlightRangesRef.current = highlightRanges; }, [highlightRanges]);

  // Whenever the caller changes revealCutoff, forward to engine immediately
  // (independent of data load — cutoff can toggle without reloading).
  // Accepts: null | number | { timeframe, barIndex } | array of objects.
  // Array form is used by TrainingPage to set both 1m and 5m cutoffs together.
  const cutoffKey = React.useMemo(() => {
    if (revealCutoff == null) return 'null';
    if (typeof revealCutoff === 'number') return `n:${revealCutoff}`;
    if (Array.isArray(revealCutoff)) {
      return revealCutoff.map(c => `${c?.timeframe || '?'}:${c?.barIndex ?? '?'}`).join('|');
    }
    return `${revealCutoff.timeframe || '?'}:${revealCutoff.barIndex ?? '?'}`;
  }, [revealCutoff]);
  React.useEffect(() => {
    const engine = engineRef.current;
    if (!engine || typeof engine.setRevealCutoff !== 'function') return;
    if (revealCutoff == null) {
      engine.setRevealCutoff(null);
    } else if (Array.isArray(revealCutoff)) {
      revealCutoff.forEach(item => {
        if (item && typeof item === 'object') engine.setRevealCutoff(item);
      });
    } else {
      engine.setRevealCutoff(revealCutoff);
    }
  }, [cutoffKey]);

  // Highlight ranges: forward to engine; if the (first) range's tf differs
  // from the engine's current tf, auto-switch so the highlight is visible.
  // Caller supplies null/[] to clear.
  const rangesKey = React.useMemo(() => {
    if (!highlightRanges || !highlightRanges.length) return 'none';
    return highlightRanges.map(r => `${r.timeframe}:${r.startIndex}-${r.endIndex}:${r.style || 'olive'}`).join('|');
  }, [highlightRanges]);
  React.useEffect(() => {
    const engine = engineRef.current;
    if (!engine || typeof engine.setHighlightRanges !== 'function') return;
    if (!highlightRanges || !highlightRanges.length) {
      engine.setHighlightRanges(null);
      return;
    }
    const first = highlightRanges[0];
    const targetTf = first.timeframe;
    if (targetTf && targetTf !== engine.getTimeframe()) {
      try { engine.setTimeframe(targetTf); } catch (_) { /* ignore */ }
    }
    engine.setHighlightRanges(highlightRanges);
    // Center the chart on the middle of the range so the band is visible; if it
    // was already in view, scrollTo is effectively a no-op + flash highlight.
    const midIndex = Math.floor((first.startIndex + first.endIndex) / 2);
    try {
      engine.scrollTo({ timeframe: targetTf, barIndex: midIndex, highlight: false, center: true });
    } catch (_) { /* ignore */ }
  }, [rangesKey]);

  // Mount/destroy once per component instance; loadData on segment change.
  React.useEffect(() => {
    if (!hostRef.current || typeof window.KlineEngine !== 'function') return;
    const engine = new window.KlineEngine({ container: hostRef.current });
    engineRef.current = engine;
    const publishPlayback = () => {
      if (typeof onPlaybackChange !== 'function') return;
      onPlaybackChange({
        playing: typeof engine.isPlaying === 'function' ? engine.isPlaying() : false,
        speed: typeof engine.getSpeed === 'function' ? engine.getSpeed() : 1,
        timeframe: typeof engine.getTimeframe === 'function' ? engine.getTimeframe() : '1m',
        index: typeof engine.getCurrentIndex === 'function' ? engine.getCurrentIndex() : 0,
        theme: typeof engine.getTheme === 'function' ? engine.getTheme() : 'dark',
      });
    };
    const publishMaVisibility = () => {
      if (typeof onMaVisibilityChange !== 'function') return;
      onMaVisibilityChange({ ...(engine.maVisibility || {}) });
    };
    const api = {
      playPause: () => { engine.togglePlayback(); publishPlayback(); },
      stepBack: () => { engine.stepBack(); publishPlayback(); },
      stepForward: () => { engine.stepForward(); publishPlayback(); },
      resetTo: (targetOverride) => {
        const target = targetOverride || resetTargetRef.current || { timeframe: '1m', index: 0 };
        engine.pause();
        if (target.theme && typeof engine.setTheme === 'function') {
          try { engine.setTheme(target.theme); } catch (_) { /* ignore */ }
        }
        try {
          engine.scrollTo({ timeframe: target.timeframe, barIndex: target.index, highlight: true, center: true });
        } catch (_) {
          try { engine.setCurrentIndex(target.index, { follow: true }); } catch (__) { /* ignore */ }
        }
        publishPlayback();
      },
      toggleTheme: () => {
        if (typeof engine.setTheme === 'function' && typeof engine.getTheme === 'function') {
          engine.setTheme(engine.getTheme() === 'dark' ? 'light' : 'dark');
        }
        publishPlayback();
      },
      pause: () => { engine.pause(); publishPlayback(); },
      snapshot: publishPlayback,
      scrollTo: (target) => {
        if (!target) return;
        engine.pause();
        try {
          engine.scrollTo({
            timeframe: target.timeframe || engine.getTimeframe?.() || '1m',
            barIndex: target.index ?? 0,
            highlight: !!target.highlight,
            center: target.center !== false,
          });
        } catch (_) { /* ignore */ }
        publishPlayback();
      },
      // MA visibility — read directly from engine.maVisibility, mutate then refresh.
      // The engine emits `ma:visibility` for any toggle (toolbar or external).
      getMaVisibility: () => ({ ...(engine.maVisibility || {}) }),
      setMaOn: (key, on) => {
        if (!engine.maVisibility || !(key in engine.maVisibility)) return;
        const next = !!on;
        if (engine.maVisibility[key] === next) return;
        engine.maVisibility[key] = next;
        try { window.localStorage?.setItem('klineEngineV2:maVisibility', JSON.stringify(engine.maVisibility)); } catch (_) {}
        if (typeof engine._updateToolbarState === 'function') engine._updateToolbarState();
        if (typeof engine.emit === 'function') engine.emit('ma:visibility', { ...engine.maVisibility });
        if (typeof engine.scheduleRender === 'function') engine.scheduleRender();
        publishMaVisibility();
      },
    };
    if (typeof onEngineReady === 'function') onEngineReady(api);
    const offPlaybackState = engine.on('playback:state', publishPlayback);
    const offPlaybackTick = engine.on('playback:tick', publishPlayback);
    const offViewport = engine.on('viewport:changed', publishPlayback);
    const offDataLoaded = engine.on('data:loaded', () => { publishPlayback(); publishMaVisibility(); });
    const offTheme = engine.on('theme:changed', publishPlayback);
    const offMa = engine.on('ma:visibility', publishMaVisibility);
    const offHover = engine.on('hover:bar', (payload) => {
      if (typeof onHoverChange === 'function') onHoverChange(payload || { index: null, timeframe: null });
    });
    return () => {
      offPlaybackState();
      offPlaybackTick();
      offViewport();
      offDataLoaded();
      offTheme();
      offMa();
      offHover();
      if (typeof onEngineReady === 'function') onEngineReady(null);
      try { engine.destroy(); } catch (e) { /* noop */ }
      engineRef.current = null;
      currentSegmentIdRef.current = null;
    };
  }, []);

  // Load data whenever the target segment or case changes.
  React.useEffect(() => {
    const engine = engineRef.current;
    if (!engine || !segment) return;
    const payload = segmentToEnginePayload(segment, caseObj);
    if (!payload) return;
    resetTargetRef.current = {
      timeframe: payload.meta?.initial_timeframe || '1m',
      index: payload.meta?.initial_timeframe === '5m'
        ? (payload.meta?.initial_index_5m ?? 0)
        : (payload.meta?.initial_index_1m ?? 0),
    };

    const applyTeachingChrome = () => {
      const vis = engine.maVisibility || {};
      if (mode === 'fragment') {
        Object.keys(vis).forEach(k => { vis[k] = true; });
      } else {
        const moduleId = caseObj?.module || caseObj?.module_id || segment?.chapter;
        const keep = new Set(CASE_RELEVANT_MA[moduleId] || ['m10', 'm50', 'm200', 'vw']);
        Object.keys(vis).forEach(k => { vis[k] = keep.has(k); });
      }
      if (typeof engine._updateToolbarState === 'function') engine._updateToolbarState();
      // Notify subscribers so the React legend mirrors the pruned defaults.
      if (typeof engine.emit === 'function') engine.emit('ma:visibility', { ...vis });
      if (typeof engine.scheduleRender === 'function') engine.scheduleRender();

      // Override engine brand title with the case title — the engine keeps
      // "Kline Engine v2" hardcoded but teaching pages want a per-case label.
      // The `[data-role="meta"]` subtitle is left to the engine (date | tf).
      const titleEl = hostRef.current?.querySelector('.kline-engine__title');
      if (titleEl) {
        titleEl.textContent = caseObj?.title || segment?.title || segment?.id || 'Kline Engine v2';
      }

      const decisionTf = caseObj?.decision_bar?.timeframe || '1m';
      const decisionIndex = caseObj?.decision_bar?.bar_index ?? segment?.derived?.signal_bar_index ?? null;
      if (decisionIndex != null) {
        try {
          engine.scrollTo({ timeframe: decisionTf, barIndex: decisionIndex, highlight: true, center: true });
        } catch (e) { /* engine may clamp/ignore if tf lacks data */ }
      }

      // loadData() clears cutoff + highlight — re-apply the latest props so
      // first-mount and case-switch don't lose teaching state set by parent.
      const cutoffNow = revealCutoffRef.current;
      if (cutoffNow != null && typeof engine.setRevealCutoff === 'function') {
        try {
          if (Array.isArray(cutoffNow)) {
            cutoffNow.forEach(item => { if (item && typeof item === 'object') engine.setRevealCutoff(item); });
          } else {
            engine.setRevealCutoff(cutoffNow);
          }
        } catch (_) { /* ignore */ }
      }
      const rangesNow = highlightRangesRef.current;
      if (rangesNow && rangesNow.length && typeof engine.setHighlightRanges === 'function') {
        const firstTf = rangesNow[0].timeframe;
        if (firstTf && firstTf !== engine.getTimeframe()) {
          try { engine.setTimeframe(firstTf); } catch (_) { /* ignore */ }
        }
        try { engine.setHighlightRanges(rangesNow); } catch (_) { /* ignore */ }
      }
    };

    // Skip reload when the same segment is requested (common in React StrictMode).
    if (currentSegmentIdRef.current === segment.id) {
      applyTeachingChrome();
      return;
    }
    currentSegmentIdRef.current = segment.id;

    const off = engine.on('data:loaded', () => {
      off();
      applyTeachingChrome();
    });
    try {
      engine.loadData(payload);
      if (typeof onPlaybackChange === 'function') {
        onPlaybackChange({
          playing: typeof engine.isPlaying === 'function' ? engine.isPlaying() : false,
          speed: typeof engine.getSpeed === 'function' ? engine.getSpeed() : 1,
          timeframe: typeof engine.getTimeframe === 'function' ? engine.getTimeframe() : '1m',
          index: typeof engine.getCurrentIndex === 'function' ? engine.getCurrentIndex() : 0,
          theme: typeof engine.getTheme === 'function' ? engine.getTheme() : 'dark',
        });
      }
    } catch (e) {
      console.error('[teaching-system] loadData failed', e);
      off();
    }
  }, [segment?.id, caseObj?.id, mode]);

  const hostClassName = `kline-host kline-host--${mode}${lockPlayback ? ' kline-host--replay-locked' : ''}`;
  return (
    <div
      ref={hostRef}
      className={hostClassName}
      style={{ width: '100%', height }}
    />
  );
}

/* === 5m 实时聚合 ===
 * 把当前 1m 的 OHLCV 折算回所属 5m 窗口（券商视角的"正在形成的当前 K"）。
 * 已完成的 5m bar 直接复用 bars_5m（含预计算的 MA/VWAP）。
 * 唯一被改写的是"current 5m"那一根：
 *   - O = window 内首根 1m 的 O（保持锁定）
 *   - H = max(window 内 1m H)
 *   - L = min(window 内 1m L)
 *   - C = 当前 1m C
 *   - V = sum
 * HA 用上一根 5m 的 hO/hC 推导，使 candle 颜色与主图一致。
 * MA/VWAP 第一阶段沿用 bars_5m 末位的预计算值（教学场景可接受小幅抖动）。
 */
function aggregate5mAt(segment, current1mIndex) {
  const bars1m = segment?.bars_1m || [];
  const bars5m = segment?.bars_5m || [];
  if (!bars1m.length || !bars5m.length) return { bars: bars5m.slice(), liveIdx: -1 };
  const tsUnix = (b) => Math.floor(new Date(b.ts).getTime() / 1000);
  const fiveStarts = bars5m.map(tsUnix);
  const idx = Math.max(0, Math.min(current1mIndex, bars1m.length - 1));
  const cur1m = bars1m[idx];
  if (!cur1m) return { bars: bars5m.slice(), liveIdx: -1 };
  const cur1mTs = tsUnix(cur1m);
  let liveIdx = -1;
  for (let j = bars5m.length - 1; j >= 0; j -= 1) {
    if (fiveStarts[j] <= cur1mTs) { liveIdx = j; break; }
  }
  if (liveIdx < 0) return { bars: bars5m.slice(), liveIdx: -1 };
  const result = [];
  for (let j = 0; j < liveIdx; j += 1) result.push(bars5m[j]);
  const liveStart = fiveStarts[liveIdx];
  const liveEnd = liveStart + 300;
  const live1ms = [];
  for (let i = 0; i <= idx; i += 1) {
    const t = tsUnix(bars1m[i]);
    if (t >= liveStart && t < liveEnd) live1ms.push(bars1m[i]);
  }
  if (!live1ms.length) {
    result.push(bars5m[liveIdx]);
  } else {
    const O = live1ms[0].O;
    const H = live1ms.reduce((m, b) => Math.max(m, b.H), -Infinity);
    const L = live1ms.reduce((m, b) => Math.min(m, b.L), Infinity);
    const C = live1ms[live1ms.length - 1].C;
    const V = live1ms.reduce((s, b) => s + (b.V || 0), 0);
    const prev = bars5m[liveIdx - 1] || bars5m[liveIdx];
    const prevHO = prev.hO ?? prev.O;
    const prevHC = prev.hC ?? prev.C;
    const haOpen = (prevHO + prevHC) / 2;
    const haClose = (O + H + L + C) / 4;
    const haHigh = Math.max(H, haOpen, haClose);
    const haLow = Math.min(L, haOpen, haClose);
    result.push({
      ...bars5m[liveIdx],
      O, H, L, C, V,
      hO: haOpen, hC: haClose, hH: haHigh, hL: haLow,
      __live: true,
    });
  }
  return { bars: result, liveIdx };
}

// Find the first bars_1m index whose ts >= the given 5m window start (unix s).
function first1mIndexAtOrAfter(bars1m, fiveStartTsUnix) {
  for (let i = 0; i < bars1m.length; i += 1) {
    const t = Math.floor(new Date(bars1m[i].ts).getTime() / 1000);
    if (t >= fiveStartTsUnix) return i;
  }
  return -1;
}

function Aggregate5mBand({ segment, playback, onJumpTo, height = 72 }) {
  const tf = playback?.timeframe || '1m';
  const idx = playback?.index ?? 0;
  const segId = segment?.id;
  const { bars, liveIdx } = React.useMemo(() => {
    if (!segment) return { bars: [], liveIdx: -1 };
    if (tf === '5m') {
      // Main chart already on 5m; band shows static bars_5m, highlight = current 5m index.
      return { bars: segment.bars_5m || [], liveIdx: idx };
    }
    return aggregate5mAt(segment, idx);
  }, [segId, tf, idx]);
  if (!bars.length) return null;

  const width = 1000;
  const pad = 6;
  const prices = bars.flatMap(b => [b.hH ?? b.H, b.hL ?? b.L]).filter(v => typeof v === 'number' && Number.isFinite(v));
  if (!prices.length) return null;
  const rawMin = Math.min(...prices);
  const rawMax = Math.max(...prices);
  const rawSpan = Math.max(0.01, rawMax - rawMin);
  const min = rawMin - rawSpan * 0.10;
  const max = rawMax + rawSpan * 0.10;
  const span = Math.max(0.01, max - min);
  const stepX = (width - pad * 2) / Math.max(1, bars.length);
  const x = i => pad + (i + 0.5) * stepX;
  const y = v => pad + (max - v) / span * (height - pad * 2);
  const candleW = Math.max(2, Math.min(8, stepX * 0.55));
  // Extract HH:MM directly from the ISO string to keep ET (data-native TZ).
  // Avoid Date#getHours() — it would convert to the browser's local TZ.
  const liveTime = (() => {
    if (liveIdx < 0) return '';
    const ts = bars[liveIdx]?.ts;
    if (!ts || typeof ts !== 'string') return '';
    const m = ts.match(/T(\d{2}:\d{2})/);
    return m ? m[1] : '';
  })();

  return (
    <div className="border-b border-[#E6E0D3] bg-[#FAF9F5] relative" style={{ height }}>
      <span className="absolute top-1 left-2 font-['Inter'] text-[10px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase pointer-events-none">5min · 实时聚合</span>
      {liveIdx >= 0 && bars[liveIdx]?.__live && (
        <span className="absolute top-1 right-2 font-['Space_Grotesk'] text-[10px] text-[#285fa2] pointer-events-none">{liveTime} · 形成中</span>
      )}
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="w-full h-full block">
        {bars.map((b, i) => {
          const open = b.hO ?? b.O;
          const close = b.hC ?? b.C;
          const high = b.hH ?? b.H;
          const low = b.hL ?? b.L;
          if (![open, close, high, low].every(v => typeof v === 'number' && Number.isFinite(v))) return null;
          const up = close >= open;
          const color = up ? '#5E7D5B' : '#9B5950';
          const isLive = i === liveIdx;
          const bodyY = Math.min(y(open), y(close));
          const bodyH = Math.max(1, Math.abs(y(open) - y(close)));
          return (
            <g key={`${b.ts}-${i}`} style={{ cursor: onJumpTo ? 'pointer' : 'default' }}
               onClick={() => onJumpTo?.(i, b)}>
              {isLive && (
                <rect x={Math.max(0, x(i) - stepX / 2)} y={1} width={stepX} height={height - 2}
                  fill="#285fa2" opacity="0.08" />
              )}
              <line x1={x(i)} x2={x(i)} y1={y(high)} y2={y(low)} stroke={color}
                strokeWidth={isLive ? 1.5 : 1} opacity={isLive ? 1 : 0.85} />
              <rect x={x(i) - candleW / 2} y={bodyY} width={candleW} height={bodyH}
                fill={up ? '#FFFFFF' : color} stroke={color}
                strokeWidth={isLive ? 1.5 : 1} opacity={isLive ? 1 : 0.92} />
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// Format a numeric MA / VWAP value for the legend. 3 decimals matches the
// price-axis precision used by the engine's right gutter labels (Plan #9).
function formatMaValue(v) {
  if (typeof v !== 'number' || !Number.isFinite(v)) return null;
  return v.toFixed(3);
}

function MaLegend({ visibility, onToggle, available, unavailableReasons, bar, source }) {
  if (!visibility || !Object.keys(visibility).length) return null;
  // `available` is a Set of MA keys that actually carry data in this segment.
  // `unavailableReasons` is an optional map { key → reason text } for tooltips.
  // `bar` is the resolved focus/hover bar (Plan #9): Moomoo-style values are
  // pulled from `bar[ma.key]` and shown next to the active MA's label so the
  // user can read the value directly without inspecting the price axis.
  // `source` is 'hover' | 'focus' — purely informational, used in the title bar.
  // Items missing data render as disabled (very light, no border, not clickable)
  // so the user sees all MA options but isn't misled into thinking the toggle
  // is broken when the line never appears.
  return (
    <div className="flex flex-wrap items-center gap-1.5 px-4 py-2 border-b border-[#E6E0D3] bg-[#FAF9F5]">
      <span
        className="font-['Inter'] text-[11px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase mr-1"
        title={source === 'hover' ? '当前数值来自鼠标悬停的 K 线' : '当前数值来自当前 focus K 线（鼠标移开 K 线时）'}
      >
        均线
      </span>
      {MA_LEGEND.map(ma => {
        const on = !!visibility[ma.key];
        const has = !available || available.has(ma.key);
        if (!has) {
          const reason = unavailableReasons?.[ma.key]
            || `教学切片 JSON 的 bars_1m / bars_5m 不含 ${ma.label} 字段。重跑 slice_teaching_segment.py 可补充。`;
          return (
            <span
              key={ma.key}
              className="flex items-center gap-1.5 px-2 py-0.5 rounded border border-transparent text-[#c8c5bc] cursor-not-allowed font-['Inter'] text-[11px] font-medium"
              title={reason}
            >
              <span className="inline-block rounded-full" style={{ width: 8, height: 8, background: ma.color, opacity: 0.18 }} />
              {ma.label}
            </span>
          );
        }
        // Only show a value when the MA is enabled AND the resolved bar carries
        // a finite numeric value for this key. `bar` may be missing during the
        // brief window before the engine first emits playback state.
        const valueStr = on && bar ? formatMaValue(bar[ma.key]) : null;
        return (
          <button
            key={ma.key}
            type="button"
            onClick={() => onToggle?.(ma.key, !on)}
            className={`flex items-center gap-1.5 px-2 py-0.5 rounded border transition-colors font-['Inter'] text-[11px] font-medium ${on ? 'border-[#C9C0AD] bg-white text-[#1A1A19]' : 'border-transparent bg-transparent text-[#a8a59c] hover:bg-white/60'}`}
            title={`${on ? '隐藏' : '显示'} ${ma.label}`}
          >
            <span className="inline-block rounded-full" style={{ width: 8, height: 8, background: ma.color, opacity: on ? 1 : 0.35 }} />
            <span>{ma.label}</span>
            {valueStr != null && (
              <span
                className="font-['Space_Grotesk'] tabular-nums text-[11px] tracking-tight"
                style={{ color: ma.color }}
              >
                {valueStr}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}

function computeAvailableMaSet(segment) {
  if (!segment) return new Set();
  // A MA key is "available" when at least one bar (1m or 5m) in this segment
  // has a non-null numeric value for it. Probes the first ~80 bars to keep
  // this cheap; teaching segments typically have 30–60 bars.
  const set = new Set();
  const keys = ['m5','m10','m20','m30','m50','m60','m120','m200','vw'];
  const probe = (bars) => {
    if (!bars || !bars.length) return;
    const limit = Math.min(bars.length, 80);
    for (const k of keys) {
      if (set.has(k)) continue;
      for (let i = 0; i < limit; i += 1) {
        const v = bars[i] && bars[i][k];
        if (typeof v === 'number' && Number.isFinite(v)) { set.add(k); break; }
      }
    }
  };
  probe(segment.bars_1m);
  probe(segment.bars_5m);
  return set;
}

// Resolve the effective reveal cutoff for a given timeframe from the prop's
// polymorphic shape (null | number | { tf, idx } | array). Returns null when no
// cutoff applies. Used by the MA value legend so focus-bar values never read
// past the current reveal cutoff.
function resolveCutoffForTf(revealCutoff, currentTf, fallbackTf) {
  if (revealCutoff == null) return null;
  if (typeof revealCutoff === 'number') {
    return currentTf === fallbackTf ? revealCutoff : null;
  }
  if (Array.isArray(revealCutoff)) {
    for (const item of revealCutoff) {
      if (item && item.timeframe === currentTf && typeof item.barIndex === 'number') return item.barIndex;
    }
    return null;
  }
  if (typeof revealCutoff === 'object') {
    if (revealCutoff.timeframe === currentTf && typeof revealCutoff.barIndex === 'number') return revealCutoff.barIndex;
  }
  return null;
}

function KlineView({ mode = 'evidence', segmentId, caseId, segmentData, caseData, height, revealCutoff, highlightRanges, lockPlayback, onPlaybackChange: externalOnPlaybackChange, onEngineReady: externalOnEngineReady }) {
  const c = caseData || (caseId ? getCase(caseId) : null);
  const segment = segmentData || (segmentId ? getSegment(segmentId) : getCaseSegment(c));
  const isLab = mode === 'lab';
  const isFragment = mode === 'fragment';
  const isMini = mode === 'mini';
  const chartHeight = height || (isMini ? 160 : isLab ? 540 : isFragment ? 620 : 360);
  const title = isMini ? 'K线缩略图' : isLab ? 'K线回放训练台' : isFragment ? '片段K线工作台' : 'K线证据图';
  const modeLabel = isMini ? 'mini' : isLab ? 'lab' : isFragment ? 'fragment' : 'evidence';
  const engineAvailable = typeof window !== 'undefined' && typeof window.KlineEngine === 'function';
  const useEngine = !isMini && engineAvailable;
  const [engineControls, setEngineControls] = React.useState(null);
  const [playback, setPlayback] = React.useState({ playing: false, speed: 1, timeframe: c?.decision_bar?.timeframe || '1m', index: c?.decision_bar?.bar_index || 0, theme: 'dark' });
  const [hoverState, setHoverState] = React.useState({ index: null, timeframe: null });
  const [showMarkers, setShowMarkers] = React.useState(false);
  const [maVis, setMaVis] = React.useState({});
  const availableMaSet = React.useMemo(() => computeAvailableMaSet(segment), [segment?.id]);
  // Effective bar for MA value legend: hover bar wins when the cursor is over a
  // candle on the same timeframe currently displayed; otherwise fall back to
  // the focus bar (currentIndex), clamped against the reveal cutoff so replay
  // hidden-future never leaks future MA values via the legend.
  const legendBar = React.useMemo(() => {
    if (!segment) return null;
    const tf = playback.timeframe || '1m';
    const bars = tf === '5m' ? segment.bars_5m : segment.bars_1m;
    if (!bars || !bars.length) return null;
    const useHover = hoverState.index != null && hoverState.timeframe === tf;
    if (useHover) {
      const hb = bars[hoverState.index];
      if (hb) return hb;
    }
    let focusIdx = playback.index ?? 0;
    const cutoff = resolveCutoffForTf(revealCutoff, tf, tf);
    if (cutoff != null && focusIdx > cutoff) focusIdx = cutoff;
    if (focusIdx < 0) focusIdx = 0;
    if (focusIdx >= bars.length) focusIdx = bars.length - 1;
    return bars[focusIdx] || null;
  }, [segment?.id, playback.timeframe, playback.index, hoverState.index, hoverState.timeframe, revealCutoff]);
  const initialViewRef = React.useRef(null);
  const handlePlaybackChange = React.useCallback((next) => {
    setPlayback(next);
    if (!initialViewRef.current) {
      initialViewRef.current = {
        timeframe: next.timeframe || '1m',
        index: next.index || 0,
        theme: next.theme || 'dark',
        showMarkers,
      };
    }
    if (typeof externalOnPlaybackChange === 'function') externalOnPlaybackChange(next);
  }, [externalOnPlaybackChange]);
  const handleEngineReady = React.useCallback((api) => {
    setEngineControls(api);
    if (typeof externalOnEngineReady === 'function') externalOnEngineReady(api);
  }, [externalOnEngineReady]);
  React.useEffect(() => {
    initialViewRef.current = null;
    setShowMarkers(false);
    // Reset hover on case/segment switch — the cached hover index from the
    // previous segment would otherwise read into the new segment's bar at the
    // same numeric index until the next render frame fires.
    setHoverState({ index: null, timeframe: null });
  }, [segment?.id, c?.id, mode]);
  const showCompactControls = mode === 'evidence' && useEngine && !!engineControls;
  const markerRanges = React.useMemo(() => {
    if (mode !== 'evidence' || !segment) return null;
    const dedupe = new Set();
    const ranges = [];
    (segment?.derived?.checkpoints || []).forEach(cp => {
      checkpointToRanges(cp, segment, c).forEach(range => {
        if (range.timeframe !== '1m') return;
        if (range.endIndex - range.startIndex > 2) return;
        const key = `${range.timeframe}:${range.startIndex}-${range.endIndex}`;
        if (dedupe.has(key)) return;
        dedupe.add(key);
        ranges.push({ ...range, style: cp.passed === false ? 'red' : 'marker' });
      });
    });
    return ranges.length ? ranges.slice(0, 5) : null;
  }, [mode, segment?.id, c?.id]);
  const activeHighlightRanges = React.useMemo(() => {
    const external = highlightRanges || [];
    const teachingMarkers = showMarkers && markerRanges ? markerRanges : [];
    const combined = [...external, ...teachingMarkers];
    return combined.length ? combined : null;
  }, [highlightRanges, showMarkers, markerRanges]);

  return (
    <div className={isFragment ? "bg-white overflow-hidden" : "bg-white border border-[#D8D1C3] rounded overflow-hidden"}>
      {!isMini && !isFragment && (
        <div className="flex flex-wrap justify-between items-center gap-3 px-4 py-3 border-b border-[#E6E0D3]">
          <div className="flex items-center gap-3 min-w-0">
            <span className="font-['Newsreader'] text-[22px] font-medium text-[#1A1A19]">{title}</span>
            <span className="font-['Space_Grotesk'] text-[12px] text-[#6B6B66] border border-[#D8D1C3] px-2 py-0.5 rounded">KlineView mode="{modeLabel}"</span>
          </div>
          <div className="font-['Space_Grotesk'] text-[12px] text-[#6B6B66]">
            {segment?.date} · {c?.decision_bar?.time || ''}
          </div>
        </div>
      )}
      {!isMini && useEngine && engineControls && (
        <MaLegend
          visibility={maVis}
          onToggle={(key, on) => engineControls.setMaOn?.(key, on)}
          available={availableMaSet}
          bar={legendBar}
          source={hoverState.index != null && hoverState.timeframe === (playback.timeframe || '1m') ? 'hover' : 'focus'}
        />
      )}
      <div style={{ height: chartHeight }}>
        {!segment ? (
          <div className="h-full flex flex-col items-center justify-center text-[#6B6B66]">
            <span className="material-symbols-outlined text-[42px] mb-3 opacity-50">candlestick_chart</span>
            <span className="font-['Work_Sans'] text-[14px]">等待教学切片数据</span>
          </div>
        ) : useEngine ? (
          <KlineEngineAdapter
            mode={mode}
            segment={segment}
            caseObj={c}
            height={chartHeight}
            revealCutoff={revealCutoff}
            highlightRanges={activeHighlightRanges}
            lockPlayback={lockPlayback}
            onEngineReady={handleEngineReady}
            onPlaybackChange={handlePlaybackChange}
            onMaVisibilityChange={setMaVis}
            onHoverChange={setHoverState}
          />
        ) : (
          <MiniKlineSvg segment={segment} mode={mode} height={chartHeight} />
        )}
      </div>
      {!isMini && !isFragment && (
        <div className="px-4 py-3 border-t border-[#E6E0D3] flex flex-wrap items-center justify-between gap-3 text-[12px] text-[#6B6B66]">
          <div className="flex flex-wrap gap-2">
            {(segment?.derived?.checkpoints || []).slice(0, 5).map(cp => (
              <span key={cp.key} className={`px-2 py-1 border rounded font-['Inter'] ${checkpointPillClass(cp)}`}>{cp.label}</span>
            ))}
          </div>
          {showCompactControls && (
            <div className="flex items-center gap-2 ml-auto">
              <button type="button" onClick={() => {
                const target = initialViewRef.current || { timeframe: playback.timeframe, index: playback.index, theme: playback.theme, showMarkers: false };
                setShowMarkers(!!target.showMarkers);
                engineControls.resetTo(target);
              }} className="h-8 px-2.5 border border-[#C9C0AD] rounded flex items-center gap-1 text-[#494740] hover:bg-[#F7F3F1] font-['Inter'] text-[12px]" title="复位到初始展示状态">
                <span className="material-symbols-outlined text-[17px]">restart_alt</span>
                复位
              </button>
              <button type="button" onClick={() => engineControls.stepBack()} className="w-8 h-8 border border-[#C9C0AD] rounded flex items-center justify-center text-[#494740] hover:bg-[#F7F3F1]" title="上一根K线">
                <span className="material-symbols-outlined text-[18px]">skip_previous</span>
              </button>
              <button type="button" onClick={() => engineControls.playPause()} className="h-8 px-3 border border-[#1A1A19] bg-[#1A1A19] text-white rounded flex items-center gap-1 font-['Inter'] text-[12px] font-semibold" title={playback.playing ? '暂停' : '播放'}>
                <span className="material-symbols-outlined text-[17px]">{playback.playing ? 'pause' : 'play_arrow'}</span>
                {playback.playing ? '暂停' : '播放'}
              </button>
              <button type="button" onClick={() => engineControls.stepForward()} className="w-8 h-8 border border-[#C9C0AD] rounded flex items-center justify-center text-[#494740] hover:bg-[#F7F3F1]" title="下一根K线">
                <span className="material-symbols-outlined text-[18px]">skip_next</span>
              </button>
              <button type="button" onClick={() => setShowMarkers(v => !v)} className={`h-8 px-2.5 border rounded flex items-center gap-1 font-['Inter'] text-[12px] ${showMarkers ? 'border-[#8B9A6D] text-[#56623F] bg-[#F4F6EE]' : 'border-[#C9C0AD] text-[#7a776f] bg-white'}`} title={showMarkers ? '关闭K线提示标记' : '开启K线提示标记'}>
                <span className="material-symbols-outlined text-[17px]">adjust</span>
                {showMarkers ? '提示开' : '提示关'}
              </button>
              <button type="button" onClick={() => engineControls.toggleTheme()} className="h-8 px-2.5 border border-[#C9C0AD] rounded flex items-center gap-1 text-[#494740] hover:bg-[#F7F3F1] font-['Inter'] text-[12px]" title="切换K线背景颜色">
                <span className="material-symbols-outlined text-[17px]">{playback.theme === 'dark' ? 'dark_mode' : 'light_mode'}</span>
                背景
              </button>
              <span className="font-['Space_Grotesk'] text-[12px] text-[#7a776f] min-w-[58px] text-right">{playback.timeframe} · #{playback.index}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function KlinePlaceholder({ height = 320, label = 'K线证据图', ...rest }) {
  return <KlineView mode="evidence" height={height} {...rest} />;
}

function DataPill({ children, tone = 'neutral' }) {
  const styles = {
    neutral: 'border-[#D8D1C3] text-[#6B6B66] bg-white',
    olive: 'border-[#8B9A6D] text-[#56623F] bg-[#F4F6EE]',
    red: 'border-[#C9897E] text-[#8A4038] bg-[#FFF4F2]',
    amber: 'border-[#D0A650] text-[#765C17] bg-[#FFF8E6]',
  };
  return (
    <span className={`font-['Inter'] text-[12px] font-semibold px-2 py-1 rounded border ${styles[tone] || styles.neutral}`}>
      {children}
    </span>
  );
}

function GradePill({ grade }) {
  const styles = {
    '标准例': 'bg-secondary-fixed/20 text-[#004585] border-secondary-fixed-dim/30',
    '边缘例': 'bg-surface-container-high text-on-surface-variant border-outline-variant',
    '反例': 'bg-error-container/20 text-on-error-container border-error-container/30',
  };
  return (
    <span className={`font-['Inter'] text-[12px] font-semibold tracking-[0.05em] px-2 py-1 rounded-sm border ${styles[grade] || styles['标准例']}`}>
      {grade}
    </span>
  );
}

Object.assign(window, {
  MODULES, MISTAKES, CASES, RULES, TOP_NAV_ITEMS, SIDEBAR_ITEMS, SEGMENTS, TRAINING_ITEMS,
  useHashRouter, useAppData, LoadingScreen, TopNav, Sidebar, AppLayout,
  getSegment, getCase, getCaseSegment, checkpointFor, checkpointToRanges, stepToHighlightRanges,
  KlineView, KlineEngineAdapter, KlinePlaceholder, GradePill, DataPill, MaLegend, MA_LEGEND,
  segmentToEnginePayload, aggregate5mAt, first1mIndexAtOrAfter, Aggregate5mBand,
});
