/* pages-2.jsx — 模块训练, 错误日志, 规则库, 案例档案 */

/* ============================================================
 * Replay-drill helpers (training-replay-drill-redesign-plan.md)
 * Drill flow: hide future → 等待/做多/做空/放弃 → reveal → review.
 * ============================================================ */

const DRILL_PREVIEW_BARS = 12;        // bars before signal user can see at start
const DRILL_REVIEW_REVEAL_BARS = 12;  // bars after submission to play out for review
const DRILL_MIN_DISTANCE = 8;         // minimum drill-start distance from signal

const DRILL_REASON_GROUPS = [
  { id: 'background', label: '背景', keys: ['trend_ok', 'ma_alignment_ok'] },
  { id: 'trigger',    label: '触发', keys: ['touch_ma10', 'confirm_bar', 'body_not_cross'] },
  { id: 'risk',       label: '风险/空间', keys: ['stop_defined', 'reward_ok', 'vwap_side', 'vwap_intercept'] },
  { id: 'no_trade',   label: '过滤/不做', keys: ['forbidden_absent'] },
];
const DRILL_REASON_KEY_TO_GROUP = (() => {
  const map = {};
  DRILL_REASON_GROUPS.forEach(g => g.keys.forEach(k => { map[k] = g.id; }));
  return map;
})();

function clamp(value, lo, hi) {
  if (Number.isNaN(value)) return lo;
  return Math.max(lo, Math.min(hi, value));
}

function tsMs(b) {
  if (!b) return null;
  if (typeof b.ts !== 'string') return null;
  const t = new Date(b.ts).getTime();
  return Number.isFinite(t) ? t : null;
}

function barTimeLabel(b) {
  return b?.t || (b?.ts ? b.ts.slice(11, 16) : '—');
}

// Signal-relative drill start. Returns null when segment is not evaluable.
function computeDrillInit(segment, caseObj) {
  const bars1m = segment?.bars_1m || [];
  const last1mIndex = Math.max(0, bars1m.length - 1);
  const signalIndex = segment?.derived?.signal_bar_index ?? caseObj?.decision_bar?.bar_index ?? null;
  if (signalIndex == null) {
    const fallback = clamp((segment?.preheat_count ?? 12) - 6, 0, last1mIndex);
    return { drillStartIndex: fallback, signalIndex: null, last1mIndex, replayOnly: true };
  }
  const proposedStart = clamp(signalIndex - DRILL_PREVIEW_BARS, 0, last1mIndex);
  const distance = signalIndex - proposedStart;
  const drillStart = distance < DRILL_MIN_DISTANCE
    ? clamp(0, 0, last1mIndex)
    : proposedStart;
  return { drillStartIndex: drillStart, signalIndex, last1mIndex, replayOnly: false };
}

// 5m cutoff that mirrors a given 1m cutoff (the last 5m bar whose start <= 1m bar's ts).
function compute5mCutoffFor1m(segment, idx1m) {
  const bars1m = segment?.bars_1m || [];
  const bars5m = segment?.bars_5m || [];
  if (!bars5m.length || !bars1m.length || idx1m == null) return null;
  const oneMs = tsMs(bars1m[clamp(idx1m, 0, bars1m.length - 1)]);
  if (oneMs == null) return null;
  let last = -1;
  for (let i = 0; i < bars5m.length; i += 1) {
    const fiveMs = tsMs(bars5m[i]);
    if (fiveMs == null) continue;
    if (fiveMs <= oneMs) last = i; else break;
  }
  return last >= 0 ? last : null;
}

// 5m → 1m index map: first 1m bar at or after the 5m bar's ts.
function map5mTo1mIndex(segment, idx5m) {
  const bars1m = segment?.bars_1m || [];
  const bars5m = segment?.bars_5m || [];
  const five = bars5m[idx5m];
  if (!five || !bars1m.length) return null;
  const targetMs = tsMs(five);
  if (targetMs == null) return null;
  for (let i = 0; i < bars1m.length; i += 1) {
    const ms = tsMs(bars1m[i]);
    if (ms != null && ms >= targetMs) return i;
  }
  return bars1m.length - 1;
}

// Static module → applicable rule_ids map. Plan §4.3: do not infer category
// matches from display text; keep these explicit.
const DRILL_MODULE_RULES = {
  ma10: ['support_ma10', 'reject_ma10'],
  'signal-b': ['signal_b'],
  'candle-quality': ['candle_body_quality'],
  levels: ['vwap_distance_filter'],
  environment: ['background_5m'],
  exit: ['moving_stop'],
};

function findCasesForModule(moduleId) {
  const ruleIds = DRILL_MODULE_RULES[moduleId] || [];
  return CASES.filter(c => {
    if (c.module === moduleId || c.module_id === moduleId) return true;
    if (ruleIds.length && (c.rule_ids || []).some(rid => ruleIds.includes(rid))) return true;
    return false;
  });
}

// Plan §3.3 expected-action resolver.
function resolveExpectedAction(caseObj) {
  if (!caseObj) return null;
  const grade = (caseObj.grade || '').toString().toLowerCase();
  if (grade === 'anti' || caseObj.grade === '反例') return '放弃';
  const answer = (caseObj.answer || '').toString();
  if (/不做|降级观察|放弃|跳过/.test(answer)) return '放弃';
  const dir = (caseObj.direction || '').toString().toUpperCase();
  if (dir === 'CALL' || dir === 'LONG' || dir === '多') return '做多';
  if (dir === 'PUT' || dir === 'SHORT' || dir === '空') return '做空';
  // Rule-id fallback only when case fields missing.
  const ruleIds = caseObj.rule_ids || [];
  if (ruleIds.includes('support_ma10')) return '做多';
  if (ruleIds.includes('reject_ma10')) return '做空';
  if (ruleIds.includes('signal_b')) return '做空';
  if (ruleIds.includes('candle_body_quality') || ruleIds.includes('vwap_distance_filter')) return '放弃';
  return null;
}

function getConfirmIndex(segment) {
  const cps = segment?.derived?.checkpoints || [];
  const cb = cps.find(cp => cp.key === 'confirm_bar');
  return (cb && Number.isFinite(cb.bar_index)) ? cb.bar_index : null;
}

// Plan §3.2 timing classification.
function classifyTiming(submittedIndex, signalIndex, confirmIndex, last1mIndex) {
  if (signalIndex == null) return 'not_scored';
  if (submittedIndex < signalIndex) return 'too_early';
  const validEnd = clamp((confirmIndex ?? signalIndex) + 1, 0, last1mIndex);
  if (submittedIndex <= validEnd) return 'valid_window';
  return 'late';
}

// Plan #1: per-step checkpoint pills for the right rail. Source = current
// case's training record (TRAINING_ITEMS). Each step contributes a pill row;
// pills resolve through segment.derived.checkpoints. Same filter rules as
// buildReasonGroups (hide unlabeled / passed forbidden_absent without flags).
function buildDecisionStepPills(caseObj, segment) {
  if (!caseObj || !segment) return [];
  const items = (typeof TRAINING_ITEMS !== 'undefined' ? TRAINING_ITEMS : (window.TRAINING_ITEMS || []));
  const record = items.find(t => t.case_id === caseObj.id);
  if (!record || !Array.isArray(record.steps)) return [];
  const cps = segment.derived?.checkpoints || [];
  const cpByKey = Object.fromEntries(cps.map(cp => [cp.key, cp]));
  const isVisible = (cp) => {
    if (!cp) return false;
    if (!cp.label && !cp.reason && !cp.notes) return false;
    if (cp.key === 'forbidden_absent') {
      const flags = cp.metrics?.forbidden_flags;
      const hasFlags = Array.isArray(flags) ? flags.length > 0 : false;
      if (!hasFlags && cp.passed !== false) return false;
    }
    return true;
  };
  return record.steps
    .map(step => {
      const seenKey = new Set();
      const pills = (step.checkpoint_keys || [])
        .map(k => cpByKey[k])
        .filter(cp => cp && isVisible(cp) && !seenKey.has(cp.key) && (seenKey.add(cp.key), true));
      return { step: step.step || step.name || '步骤', pills };
    })
    .filter(row => row.pills.length > 0);
}

// Plan §3.4 reason chip groups (filtered, never raw checkpoint dump).
function buildReasonGroups(segment) {
  const cps = segment?.derived?.checkpoints || [];
  const cpByKey = {};
  cps.forEach(cp => { cpByKey[cp.key] = cp; });
  const groups = DRILL_REASON_GROUPS.map(g => {
    const items = g.keys
      .map(k => cpByKey[k])
      .filter(cp => {
        if (!cp) return false;
        if (!cp.label && !cp.reason && !cp.notes) return false;
        // forbidden_absent only surfaces when there's actual no-trade content.
        if (cp.key === 'forbidden_absent') {
          const flags = cp.metrics?.forbidden_flags;
          const hasFlags = Array.isArray(flags) ? flags.length > 0 : false;
          if (!hasFlags && cp.passed !== false) return false;
        }
        return true;
      });
    return { ...g, items };
  });
  return groups.filter(g => g.items.length > 0);
}

function reviewReasons(selectedKeys, segment) {
  const cps = segment?.derived?.checkpoints || [];
  const cpByKey = Object.fromEntries(cps.map(cp => [cp.key, cp]));
  // Plan #2: misses must come from the same visible chip set the user could
  // have actually selected. Otherwise standard long/short cases report a passed
  // forbidden_absent (filtered out of buildReasonGroups when it has no flags)
  // as a missed reason — semantically possible but pure noise to the user.
  const visibleGroups = buildReasonGroups(segment);
  const visibleByKey = Object.fromEntries(
    visibleGroups.flatMap(g => g.items).map(cp => [cp.key, cp])
  );
  const hits = [];
  const contradictions = [];
  selectedKeys.forEach(key => {
    const cp = cpByKey[key];
    if (!cp) return;
    if (cp.passed === false) contradictions.push(cp);
    else hits.push(cp);
  });
  const misses = Object.values(visibleByKey).filter(cp =>
    cp.passed === true && !selectedKeys.includes(cp.key) && cp.label
  );
  return { hits, misses, contradictions };
}

function buildReviewText({ timingLabel, expectedAction, actionCorrect, submittedAction, signalIndex, validWindow, bars1m, bars5m, submittedIndex, confirmIndex, submittedTimeframe, submitted5mIndex }) {
  const parts = [];
  if (expectedAction == null) {
    parts.push('该案例当前为只读复盘，未给出标准动作；可参考检查点理解理由。');
    return parts.join(' ');
  }
  if (expectedAction === '放弃') {
    parts.push(actionCorrect
      ? `标准动作是放弃，已正确识别。`
      : `标准动作是放弃；当前选择是「${submittedAction}」。`);
  } else {
    parts.push(actionCorrect
      ? `方向正确：${expectedAction}。`
      : `方向不符：标准是「${expectedAction}」，本次是「${submittedAction}」。`);
    const sigT = barTimeLabel(bars1m?.[signalIndex]);
    const winT = validWindow ? barTimeLabel(bars1m?.[validWindow.end]) : null;
    if (timingLabel === 'too_early') {
      parts.push(`时机过早：信号 K 在 ${sigT} 才出现。`);
    } else if (timingLabel === 'valid_window') {
      parts.push(`时机合理：在标准窗口 (${sigT}–${winT}) 内出手。`);
    } else if (timingLabel === 'late') {
      parts.push(`时机偏晚：标准窗口在 ${winT} 已收尾。`);
    }
  }
  // Plan #3: 5m → 1m mapping explanation. We map 5m commits to the FIRST 1m
  // bar at-or-after that 5m bar's start ts; users sometimes assume the entire
  // 5m candle is "the same moment", so make the rule explicit in the review.
  if (submittedTimeframe === '5m' && submitted5mIndex != null) {
    const five = bars5m?.[submitted5mIndex];
    const fiveStartT = barTimeLabel(five);
    const mappedT = barTimeLabel(bars1m?.[submittedIndex]);
    parts.push(`5m 提交按该 5m K 起点 ${fiveStartT} 映射到 1m #${submittedIndex} (${mappedT})；评分以这根 1m bar 的位置为准。`);
  }
  return parts.join(' ');
}

const DRILL_TIMING_LABEL = {
  too_early: { text: '过早', tone: 'red' },
  valid_window: { text: '窗口内', tone: 'olive' },
  late: { text: '偏晚', tone: 'red' },
  not_scored: { text: '未评分', tone: 'neutral' },
};

const DRILL_ACTIONS = [
  { key: '做多', tone: 'long',  hint: 'CALL' },
  { key: '做空', tone: 'short', hint: 'PUT' },
  { key: '放弃', tone: 'pass',  hint: 'NO TRADE' },
];

function TrainingPage({ moduleId, navigate }) {
  const mod = MODULES.find(m => m.id === moduleId) || MODULES[0];

  // Case selection — TRAINING_ITEMS first, then any module-matching cases (replay-only fallback).
  const moduleTrainings = TRAINING_ITEMS.filter(item => item.module_id === mod.id);
  const moduleCases = React.useMemo(() => findCasesForModule(mod.id), [mod.id]);
  const trainedCaseIds = new Set(moduleTrainings.map(t => t.case_id));
  const drillCases = React.useMemo(() => {
    const ordered = [];
    const seen = new Set();
    moduleTrainings.forEach(t => {
      const c = CASES.find(cc => cc.id === t.case_id);
      if (c && !seen.has(c.id)) { ordered.push(c); seen.add(c.id); }
    });
    moduleCases.forEach(c => { if (!seen.has(c.id)) { ordered.push(c); seen.add(c.id); } });
    return ordered;
  }, [moduleTrainings, moduleCases]);
  const fallbackCase = drillCases[0] || CASES[0];

  const [selectedCaseId, setSelectedCaseId] = React.useState(fallbackCase?.id);
  React.useEffect(() => { setSelectedCaseId(fallbackCase?.id); }, [mod.id]);

  const caseItem = React.useMemo(
    () => CASES.find(c => c.id === selectedCaseId) || fallbackCase,
    [selectedCaseId, fallbackCase],
  );
  const segment = React.useMemo(() => getCaseSegment(caseItem), [caseItem?.id]);
  const bars1m = segment?.bars_1m || [];
  const bars5m = segment?.bars_5m || [];

  const drillInit = React.useMemo(() => computeDrillInit(segment, caseItem), [segment?.id, caseItem?.id]);
  const expectedAction = React.useMemo(() => resolveExpectedAction(caseItem), [caseItem?.id]);
  const evaluable = !drillInit.replayOnly && expectedAction != null;
  const reasonGroups = React.useMemo(() => buildReasonGroups(segment), [segment?.id]);
  const decisionStepRows = React.useMemo(() => buildDecisionStepPills(caseItem, segment), [caseItem?.id, segment?.id]);

  const [phase, setPhase] = React.useState('replay');
  const [currentIndex, setCurrentIndex] = React.useState(drillInit.drillStartIndex);
  const [revealCutoffIndex, setRevealCutoffIndex] = React.useState(drillInit.drillStartIndex);
  const [selectedReasonKeys, setSelectedReasonKeys] = React.useState([]);
  const [waitLog, setWaitLog] = React.useState([]);
  const [submittedAction, setSubmittedAction] = React.useState(null);
  const [submittedIndex, setSubmittedIndex] = React.useState(null);
  const [reviewState, setReviewState] = React.useState(null);
  const [pillHighlightKey, setPillHighlightKey] = React.useState(null);
  const [playbackSnap, setPlaybackSnap] = React.useState({ playing: false, timeframe: '1m', index: drillInit.drillStartIndex, theme: 'dark', speed: 1 });
  const [engineApi, setEngineApi] = React.useState(null);
  const playbackTargetRef = React.useRef(null);
  const currentIndexRef = React.useRef(drillInit.drillStartIndex);
  React.useEffect(() => { currentIndexRef.current = currentIndex; }, [currentIndex]);

  // Reset all drill state when case or module switches.
  React.useEffect(() => {
    setPhase('replay');
    setCurrentIndex(drillInit.drillStartIndex);
    setRevealCutoffIndex(drillInit.drillStartIndex);
    setSelectedReasonKeys([]);
    setWaitLog([]);
    setSubmittedAction(null);
    setSubmittedIndex(null);
    setReviewState(null);
    setPillHighlightKey(null);
    playbackTargetRef.current = null;
  }, [caseItem?.id, drillInit.drillStartIndex]);

  // After engine ready (or case switch), park the engine on the drill start bar
  // so the chart is centered on what the user can see.
  React.useEffect(() => {
    if (!engineApi || !segment) return;
    if (phase !== 'replay') return;
    engineApi.scrollTo({ timeframe: '1m', index: drillInit.drillStartIndex, center: true });
  }, [engineApi, segment?.id, drillInit.drillStartIndex]);

  // Plan §4.2: when phase is submitted and outcome playback hits the reveal
  // target, pause and surface the review panel. User pause is respected.
  React.useEffect(() => {
    if (phase !== 'submitted') return;
    if (!engineApi) return;
    const target = playbackTargetRef.current?.target;
    if (target == null) return;
    if (playbackSnap.timeframe === '1m' && playbackSnap.index >= target) {
      engineApi.pause();
      setPhase('review');
    }
  }, [phase, playbackSnap.index, playbackSnap.timeframe, engineApi]);

  // Compute the cutoff prop. Plan: hide both 1m and 5m future bars.
  const revealCutoffProp = React.useMemo(() => {
    const fiveCut = compute5mCutoffFor1m(segment, revealCutoffIndex);
    const items = [{ timeframe: '1m', barIndex: revealCutoffIndex }];
    if (fiveCut != null) items.push({ timeframe: '5m', barIndex: fiveCut });
    return items;
  }, [segment?.id, revealCutoffIndex]);

  // Plan #1: pill click → checkpoint highlight via checkpointToRanges.
  // Highest-priority overlay: when pill is selected, it overrides the default
  // submission highlight so the user can scan evidence freely.
  const pillHighlightRanges = React.useMemo(() => {
    if (!pillHighlightKey || !segment) return null;
    const cp = (segment.derived?.checkpoints || []).find(c => c.key === pillHighlightKey);
    if (!cp) return null;
    const helper = window.checkpointToRanges;
    if (typeof helper !== 'function') return null;
    const ranges = helper(cp, segment, caseItem) || [];
    return ranges.length ? ranges : null;
  }, [pillHighlightKey, segment?.id, caseItem?.id]);

  // Highlight ranges. Pill highlight wins (any phase). Otherwise: replay clean,
  // submitted/review shows [signal..confirm] band + submitted marker.
  const highlightRangesProp = React.useMemo(() => {
    if (pillHighlightRanges) return pillHighlightRanges;
    if (phase === 'replay') return null;
    if (submittedIndex == null) return null;
    const ranges = [];
    const sigIdx = drillInit.signalIndex;
    const confirmIdx = getConfirmIndex(segment);
    if (sigIdx != null) {
      const winEnd = clamp((confirmIdx ?? sigIdx) + 1, 0, drillInit.last1mIndex);
      ranges.push({ timeframe: '1m', startIndex: sigIdx, endIndex: winEnd, style: 'olive' });
    }
    const subTone = (reviewState?.actionCorrect === false || reviewState?.timingLabel === 'too_early' || reviewState?.timingLabel === 'late')
      ? 'red' : 'blue';
    ranges.push({ timeframe: '1m', startIndex: submittedIndex, endIndex: submittedIndex, style: subTone });
    return ranges;
  }, [pillHighlightRanges, phase, submittedIndex, segment?.id, drillInit.signalIndex, drillInit.last1mIndex, reviewState]);

  const handleWait = () => {
    if (phase !== 'replay') return;
    const next = Math.min(currentIndexRef.current + 1, drillInit.last1mIndex);
    if (next === currentIndexRef.current) return;
    currentIndexRef.current = next;
    setCurrentIndex(next);
    setRevealCutoffIndex(next);
    setWaitLog(prev => [...prev, { index: next, time: barTimeLabel(bars1m[next]) }]);
    if (engineApi) {
      // Keep the engine current bar in sync with the visible front edge so
      // outcome playback can later start exactly at submittedIndex.
      engineApi.scrollTo({ timeframe: '1m', index: next, center: false });
    }
  };

  const resolveSubmittedIndex = () => {
    if (playbackSnap.timeframe === '5m' && Number.isFinite(playbackSnap.index)) {
      const mapped = map5mTo1mIndex(segment, playbackSnap.index);
      if (mapped != null) return mapped;
    }
    return currentIndex;
  };

  const handleSubmit = (action) => {
    if (phase !== 'replay') return;
    const idx = resolveSubmittedIndex();
    // Plan #3: capture 5m source-of-submit info (if user clicked while engine
    // was on 5m). resolveSubmittedIndex already mapped to 1m; we just remember
    // which 5m bar drove the mapping so the review can explain the 5m → 1m rule.
    const submittedTimeframe = playbackSnap.timeframe === '5m' ? '5m' : '1m';
    const submitted5mIndex = submittedTimeframe === '5m' && Number.isFinite(playbackSnap.index)
      ? playbackSnap.index : null;
    setSubmittedAction(action);
    setSubmittedIndex(idx);

    const sigIdx = drillInit.signalIndex;
    const confirmIdx = getConfirmIndex(segment);
    const isPassExpected = expectedAction === '放弃';
    const timingLabel = (!evaluable || isPassExpected)
      ? 'not_scored'
      : classifyTiming(idx, sigIdx, confirmIdx, drillInit.last1mIndex);
    const actionCorrect = expectedAction == null ? null : action === expectedAction;
    const timingCorrect = (!evaluable || isPassExpected) ? null : timingLabel === 'valid_window';
    const reasonReview = reviewReasons(selectedReasonKeys, segment);
    const validWindow = sigIdx != null
      ? { start: sigIdx, end: clamp((confirmIdx ?? sigIdx) + 1, 0, drillInit.last1mIndex) }
      : null;
    const reviewText = buildReviewText({
      timingLabel, expectedAction, actionCorrect, submittedAction: action,
      signalIndex: sigIdx, validWindow, bars1m, bars5m,
      submittedIndex: idx, confirmIndex: confirmIdx,
      submittedTimeframe, submitted5mIndex,
    });
    setReviewState({
      timingLabel, expectedAction, actionCorrect, timingCorrect,
      submittedIndex: idx, signalIndex: sigIdx, validWindow,
      submittedTimeframe, submitted5mIndex,
      reasonHits: reasonReview.hits,
      reasonMisses: reasonReview.misses,
      reasonContradictions: reasonReview.contradictions,
      reviewText,
    });

    const revealTarget = Math.min(idx + DRILL_REVIEW_REVEAL_BARS, drillInit.last1mIndex);
    playbackTargetRef.current = { target: revealTarget };
    setRevealCutoffIndex(revealTarget);
    setPhase('submitted');

    // Force back to 1m, center on submitted bar, then start playback toward the reveal target.
    if (engineApi) {
      engineApi.scrollTo({ timeframe: '1m', index: idx, center: true });
      // setRevealCutoff auto-pauses; defer play() until after the cutoff prop has been forwarded.
      setTimeout(() => {
        if (!engineApi) return;
        if (idx >= revealTarget) { setPhase('review'); return; }
        engineApi.playPause(); // paused → play
      }, 60);
    } else if (idx >= revealTarget) {
      setPhase('review');
    }
  };

  const toggleReason = (key) => {
    if (phase !== 'replay') return;
    setSelectedReasonKeys(prev => prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]);
  };

  // Plan #1: pill click toggles the highlight overlay; second click clears.
  // Lightweight nav only — does not affect drill / scoring / reason selection.
  const togglePillHighlight = (key) => {
    setPillHighlightKey(prev => prev === key ? null : key);
  };

  const handleRetry = () => {
    setPhase('replay');
    setCurrentIndex(drillInit.drillStartIndex);
    setRevealCutoffIndex(drillInit.drillStartIndex);
    setSelectedReasonKeys([]);
    setWaitLog([]);
    setSubmittedAction(null);
    setSubmittedIndex(null);
    setReviewState(null);
    playbackTargetRef.current = null;
    if (engineApi) engineApi.scrollTo({ timeframe: '1m', index: drillInit.drillStartIndex, center: true });
  };

  const handleNextCase = () => {
    if (drillCases.length <= 1) return;
    const idx = drillCases.findIndex(c => c.id === selectedCaseId);
    const nextCase = drillCases[(idx + 1) % drillCases.length];
    setSelectedCaseId(nextCase.id);
  };

  const handleRevealAll = () => {
    if (phase !== 'review') return;
    setRevealCutoffIndex(drillInit.last1mIndex);
    if (engineApi) {
      engineApi.scrollTo({ timeframe: '1m', index: drillInit.last1mIndex, center: true });
    }
  };

  const handleResumePlayback = () => {
    if (phase !== 'submitted' || !engineApi) return;
    engineApi.playPause();
  };

  const handleOpenReview = () => {
    if (phase === 'submitted' && engineApi) engineApi.pause();
    setPhase('review');
  };

  const drillStartTime = barTimeLabel(bars1m[drillInit.drillStartIndex]);
  const currentBarTime = barTimeLabel(bars1m[currentIndex]);
  const totalSteps = Math.max(1, drillInit.last1mIndex - drillInit.drillStartIndex);
  const stepsTaken = clamp(currentIndex - drillInit.drillStartIndex, 0, totalSteps);

  return (
    <AppLayout activeTop="hub" activeModule={mod.id} navigate={navigate}
      onModuleClick={(id) => navigate(`training/${id}`)}>
      <div className="px-8 py-8 max-w-[1440px] mx-auto">
        {/* 顶栏：返回 + 面包屑 + case 切换 tab */}
        <div className="mb-6 flex items-end justify-between gap-4 flex-wrap pb-3 border-b border-[#ded7ca]">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(`module/${mod.id}`)} className="font-['Work_Sans'] text-[14px] text-[#6B6B66] hover:text-[#1A1A19] flex items-center gap-1">
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>返回{mod.name}
            </button>
            <span className="h-5 w-px bg-[#cbc6bd]" aria-hidden="true" />
            <div>
              <span className="font-['Inter'] text-[11px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase block leading-tight">实盘回放训练</span>
              <h1 className="font-['Newsreader'] text-[22px] font-medium leading-tight text-[#1A1A19]">{mod.name} · 隐藏未来 K 线决策</h1>
            </div>
          </div>
          {drillCases.length > 1 && (
            <div className="flex items-center gap-1 -mb-3" role="tablist">
              {drillCases.map(c => {
                const isActive = c.id === selectedCaseId;
                const trained = trainedCaseIds.has(c.id);
                return (
                  <button key={c.id} onClick={() => setSelectedCaseId(c.id)} role="tab" aria-selected={isActive}
                    className={`px-4 py-2 font-['Work_Sans'] text-[14px] border-b-2 transition-colors ${isActive ? 'border-[#1A1A19] text-[#1A1A19] font-semibold' : 'border-transparent text-[#7a776f] hover:text-[#1A1A19]'}`}
                    title={trained ? '案例选择' : '案例选择 · 仅复盘（未配置训练答案）'}>
                    {c.title || c.id}
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* 2 列：chart 8 / rail 4 */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <div className="xl:col-span-8">
            <KlineView
              mode="lab" height={580}
              segmentId={caseItem?.segment_id} caseId={caseItem?.id}
              revealCutoff={revealCutoffProp}
              highlightRanges={highlightRangesProp}
              lockPlayback={phase === 'replay'}
              onPlaybackChange={setPlaybackSnap}
              onEngineReady={setEngineApi}
            />
          </div>

          <aside className="xl:col-span-4 flex flex-col gap-4">
            {/* 当前状态 */}
            <div className="bg-white border border-[#ded7ca] rounded p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-['Space_Grotesk'] text-[11px] tracking-[0.08em] text-[#7a776f] uppercase">
                  {phase === 'replay' ? '决策中' : phase === 'submitted' ? '播放走势中' : '复盘'}
                </span>
                <span className="font-['Inter'] text-[11px] text-[#7a776f]">{playbackSnap.timeframe} · 起点 {drillStartTime}</span>
              </div>
              <div className="flex items-end justify-between gap-2">
                <div>
                  <div className="font-['Newsreader'] text-[20px] font-medium text-[#1A1A19]">{currentBarTime}</div>
                  <div className="font-['Inter'] text-[11px] text-[#7a776f] mt-1">1m #{currentIndex} · 已等 {waitLog.length} 根</div>
                </div>
                <div className="text-right">
                  <div className="font-['Inter'] text-[11px] text-[#7a776f]">未来已隐藏</div>
                  <div className="font-['Space_Grotesk'] text-[12px] text-[#494740]">显示 {stepsTaken}/{totalSteps}</div>
                </div>
              </div>
              {!evaluable && (
                <p className="mt-3 font-['Work_Sans'] text-[12px] text-[#8A4038]">
                  此案例未配置标准动作，仅作为只读复盘 — 提交后不计分。
                </p>
              )}
              {/* Plan #3: 5m 提交映射提示。在 submitted/review 阶段如果是从 5m 提交，
                  显示该 5m K 起点 → 1m bar 的映射，避免用户以为自己是在"5m 当前 K 内"决策。*/}
              {(phase === 'submitted' || phase === 'review') && reviewState?.submittedTimeframe === '5m' && reviewState?.submitted5mIndex != null && (
                <p className="mt-3 font-['Work_Sans'] text-[12px] text-[#494740]">
                  5m 提交按 {barTimeLabel(bars5m[reviewState.submitted5mIndex])} 起点映射到 1m #{reviewState.submittedIndex} ({barTimeLabel(bars1m[reviewState.submittedIndex])})
                </p>
              )}
            </div>

            {/* 动作按钮 */}
            <div className="bg-white border border-[#ded7ca] rounded p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-['Inter'] text-[11px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase">行动</span>
                <span className="font-['Inter'] text-[11px] text-[#7a776f]">在任意可见 K 上做决定</span>
              </div>
              <button
                type="button"
                onClick={handleWait}
                disabled={phase !== 'replay' || currentIndex >= drillInit.last1mIndex}
                className="w-full mb-3 border border-[#1A1A19] bg-white text-[#1A1A19] py-2.5 rounded font-['Inter'] text-[13px] font-semibold tracking-[0.05em] hover:bg-[#f4f2ec] transition-colors disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                <span className="material-symbols-outlined text-[18px]">timer</span>
                等待一根 K
              </button>
              <div className="grid grid-cols-3 gap-2">
                {DRILL_ACTIONS.map(a => {
                  const styles = a.tone === 'long'
                    ? 'border-[#56623F] bg-[#F4F6EE] text-[#56623F] hover:bg-[#e9eed7]'
                    : a.tone === 'short'
                      ? 'border-[#8A4038] bg-[#FFF4F2] text-[#8A4038] hover:bg-[#fde8e3]'
                      : 'border-[#7a776f] bg-white text-[#494740] hover:bg-[#ebe7e6]';
                  return (
                    <button
                      key={a.key}
                      type="button"
                      disabled={phase !== 'replay'}
                      onClick={() => handleSubmit(a.key)}
                      className={`border rounded py-2 font-['Inter'] text-[13px] font-semibold flex flex-col items-center transition-colors disabled:opacity-30 disabled:cursor-not-allowed ${styles}`}>
                      <span>{a.key}</span>
                      <span className="font-['Space_Grotesk'] text-[10px] tracking-[0.08em] opacity-70 mt-0.5">{a.hint}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Plan #1: 决策步骤 pills（证据导航，点击高亮对应位置；不计分） */}
            {decisionStepRows.length > 0 && (
              <div className="bg-white border border-[#ded7ca] rounded p-4 space-y-3">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-['Inter'] text-[11px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase">决策步骤 · 证据导航</span>
                  {pillHighlightKey && (
                    <button type="button" onClick={() => setPillHighlightKey(null)}
                      className="font-['Inter'] text-[11px] text-[#494740] underline hover:text-[#1A1A19]">
                      清除高亮
                    </button>
                  )}
                </div>
                <div className="space-y-2.5">
                  {decisionStepRows.map((row, ri) => (
                    <div key={ri}>
                      <div className="font-['Space_Grotesk'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1.5">{row.step}</div>
                      <div className="flex gap-1.5 flex-wrap">
                        {row.pills.map(cp => {
                          const active = pillHighlightKey === cp.key;
                          const failed = cp.passed === false;
                          const base = 'px-2.5 py-1 border rounded font-["Inter"] text-[12px] transition-colors';
                          const styles = active
                            ? (failed ? 'border-[#8A4038] bg-[#FFF4F2] text-[#8A4038]' : 'border-[#1A1A19] bg-[#1A1A19] text-white')
                            : (failed ? 'border-[#d8b4af] text-[#8A4038] bg-white hover:bg-[#fde8e3]'
                                      : 'border-[#ded7ca] text-[#494740] bg-white hover:bg-[#f7f3f1]');
                          return (
                            <button key={cp.key} type="button"
                              onClick={() => togglePillHighlight(cp.key)}
                              title={cp.reason || cp.notes || cp.label}
                              className={`${base} ${styles}`}>
                              {cp.label || cp.key}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 理由 chips */}
            {reasonGroups.length > 0 && (
              <div className="bg-white border border-[#ded7ca] rounded p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-['Inter'] text-[11px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase">理由（多选）</span>
                  <span className="font-['Inter'] text-[11px] text-[#7a776f]">已选 {selectedReasonKeys.length}</span>
                </div>
                <div className="space-y-3">
                  {reasonGroups.map(g => (
                    <div key={g.id}>
                      <div className="font-['Space_Grotesk'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1.5">{g.label}</div>
                      <div className="flex gap-1.5 flex-wrap">
                        {g.items.map(cp => {
                          const selected = selectedReasonKeys.includes(cp.key);
                          const failedTone = cp.passed === false;
                          const base = 'px-2.5 py-1 border rounded font-["Inter"] text-[12px] transition-colors disabled:cursor-not-allowed';
                          const styles = selected
                            ? (failedTone ? 'border-[#8A4038] bg-[#FFF4F2] text-[#8A4038]' : 'border-[#56623F] bg-[#F4F6EE] text-[#56623F]')
                            : 'border-[#ded7ca] text-[#494740] bg-white hover:bg-[#f7f3f1]';
                          return (
                            <button key={cp.key} type="button"
                              disabled={phase !== 'replay'}
                              onClick={() => toggleReason(cp.key)}
                              title={cp.reason || cp.notes || cp.label}
                              className={`${base} ${styles}`}>
                              {cp.label || cp.key}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 等待日志 */}
            {waitLog.length > 0 && (
              <div className="bg-white border border-[#ded7ca] rounded p-4">
                <div className="font-['Inter'] text-[11px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase mb-2">等待日志</div>
                <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                  {waitLog.map((w, i) => (
                    <span key={i} className="font-['Space_Grotesk'] text-[11px] px-1.5 py-0.5 border border-[#ded7ca] rounded text-[#494740]">{w.time}</span>
                  ))}
                </div>
              </div>
            )}

            {/* 复盘面板 */}
            {(phase === 'submitted' || phase === 'review') && reviewState && (
              <div className="bg-white border border-[#ded7ca] rounded p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="font-['Inter'] text-[11px] font-semibold tracking-[0.08em] text-[#7a776f] uppercase">复盘</span>
                  {phase === 'submitted' && (
                    <div className="flex gap-2">
                      <button type="button" onClick={playbackSnap.playing ? handleOpenReview : handleResumePlayback}
                        className="font-['Inter'] text-[11px] text-[#494740] underline hover:text-[#1A1A19]">
                        {playbackSnap.playing ? '直接看复盘' : '继续播放'}
                      </button>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-2 mb-3">
                  <div>
                    <div className="font-['Inter'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1">本次动作</div>
                    <DataPill tone={reviewState.actionCorrect === true ? 'olive' : reviewState.actionCorrect === false ? 'red' : 'neutral'}>
                      {submittedAction}
                    </DataPill>
                  </div>
                  <div>
                    <div className="font-['Inter'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1">标准动作</div>
                    <DataPill tone={reviewState.expectedAction ? 'olive' : 'neutral'}>
                      {reviewState.expectedAction || '—'}
                    </DataPill>
                  </div>
                  <div>
                    <div className="font-['Inter'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1">时机</div>
                    <DataPill tone={DRILL_TIMING_LABEL[reviewState.timingLabel]?.tone || 'neutral'}>
                      {DRILL_TIMING_LABEL[reviewState.timingLabel]?.text || '—'}
                    </DataPill>
                  </div>
                  <div>
                    <div className="font-['Inter'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1">等待次数</div>
                    <DataPill tone="neutral">{waitLog.length}</DataPill>
                  </div>
                </div>

                {phase === 'review' && (
                  <>
                    <p className="font-['Work_Sans'] text-[13px] text-[#494740] leading-relaxed mb-3">{reviewState.reviewText}</p>

                    {(reviewState.reasonHits.length > 0 || reviewState.reasonMisses.length > 0 || reviewState.reasonContradictions.length > 0) && (
                      <div className="space-y-2 mb-3">
                        {reviewState.reasonHits.length > 0 && (
                          <div>
                            <div className="font-['Space_Grotesk'] text-[10px] tracking-[0.08em] text-[#56623F] uppercase mb-1">命中理由</div>
                            <div className="flex gap-1.5 flex-wrap">
                              {reviewState.reasonHits.map(cp => <DataPill key={cp.key} tone="olive">{cp.label}</DataPill>)}
                            </div>
                          </div>
                        )}
                        {reviewState.reasonMisses.length > 0 && (
                          <div>
                            <div className="font-['Space_Grotesk'] text-[10px] tracking-[0.08em] text-[#7a776f] uppercase mb-1">遗漏理由</div>
                            <div className="flex gap-1.5 flex-wrap">
                              {reviewState.reasonMisses.map(cp => <DataPill key={cp.key} tone="neutral">{cp.label}</DataPill>)}
                            </div>
                          </div>
                        )}
                        {reviewState.reasonContradictions.length > 0 && (
                          <div>
                            <div className="font-['Space_Grotesk'] text-[10px] tracking-[0.08em] text-[#8A4038] uppercase mb-1">理由与证据冲突</div>
                            <div className="flex gap-1.5 flex-wrap">
                              {reviewState.reasonContradictions.map(cp => <DataPill key={cp.key} tone="red">{cp.label}</DataPill>)}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex gap-2 flex-wrap">
                      <button type="button" onClick={handleRevealAll}
                        className="border border-[#ded7ca] text-[#494740] px-3 py-1.5 rounded font-['Inter'] text-[12px] hover:bg-[#f7f3f1]">
                        继续播放到结尾
                      </button>
                      <button type="button" onClick={handleRetry}
                        className="border border-[#1A1A19] text-[#1A1A19] px-3 py-1.5 rounded font-['Inter'] text-[12px] hover:bg-[#ebe7e6]">
                        重做本案例
                      </button>
                      {drillCases.length > 1 && (
                        <button type="button" onClick={handleNextCase}
                          className="bg-[#1A1A19] text-white px-3 py-1.5 rounded font-['Inter'] text-[12px] hover:bg-[#313030]">
                          换一个案例
                        </button>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </aside>
        </div>
      </div>
    </AppLayout>
  );
}

function MistakesPage({ navigate }) {
  return (
    <AppLayout activeTop="mistakes" activeModule="mistakes" navigate={navigate}
      onModuleClick={(id) => id === 'mistakes' ? navigate('mistakes') : navigate(`module/${id}`)}>
      <div className="p-12 max-w-[1280px] mx-auto">
        <header className="mb-8 pb-4 border-b border-[#cbc6bd]">
          <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2] mb-2">错误日志</h1>
          <p className="font-['Work_Sans'] text-[18px] leading-[1.6] text-[#494740] max-w-2xl">
            执行错误的严格记录。识别冲动行为的模式，是纪律性遵守执行手册的第一步。
          </p>
        </header>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {MISTAKES.map(err => (
            <article key={err.id}
              className="relative group bg-white border border-[#cbc6bd] rounded p-8 shadow-[0px_4px_12px_rgba(23,22,19,0.05)] hover:border-[#7a776f] transition-colors flex flex-col min-h-[280px]">
              {err.freq && (
                <div className="absolute top-4 right-4">
                  <span className={`font-['Inter'] text-[12px] font-semibold tracking-[0.05em] px-2 py-1 rounded border ${err.freq === '高频' ? 'bg-[#ffdad6] text-[#93000a] border-[#ba1a1a]/20' : 'bg-[#ebe7e6] text-[#494740] border-[#cbc6bd]'}`}>
                    {err.freq}
                  </span>
                </div>
              )}
              <div className="mb-auto">
                <span className="material-symbols-outlined text-[32px] text-[#ba1a1a] mb-4 block">{err.icon}</span>
                <h3 className="font-['Newsreader'] text-[24px] font-medium mb-2 group-hover:text-[#000] transition-colors">{err.name}</h3>
                <p className="font-['Work_Sans'] text-[16px] leading-[1.6] text-[#494740]">{err.desc}</p>
                <div className="mt-3 flex items-center gap-2">
                  <span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] px-2 py-1 bg-[#f1edec] text-[#494740] rounded-sm border border-[#cbc6bd]/30">{err.category}</span>
                </div>
              </div>
              <div className="mt-6 pt-4 border-t border-[#cbc6bd] flex items-center justify-between">
                <span className="font-['Space_Grotesk'] text-[14px] text-[#7a776f]">{err.id.toUpperCase()}</span>
                <a onClick={() => navigate(`mistake/${err.id}`)}
                  className="text-[#56623F] font-medium font-['Work_Sans'] text-[16px] flex items-center gap-1 hover:underline cursor-pointer">
                  进入错误详情 <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </a>
              </div>
            </article>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}

function MistakeDetailPage({ mistakeId, navigate }) {
  const err = MISTAKES.find(e => e.id === mistakeId) || MISTAKES[0];
  const mod = MODULES.find(m => m.id === err.module) || MODULES[0];
  const relatedRules = (err.rule_ids || []).map(id => RULES.find(r => r.id === id)).filter(Boolean);
  // Rank by mistake-tag match → rule match → module match, so anti-cases tagged
  // with this mistake win over unrelated standard cases in the same module.
  const tagHit = c => (c.mistake_tags || []).includes(err.name);
  const ruleHit = c => (c.rule_ids || []).some(id => (err.rule_ids || []).includes(id));
  const moduleHit = c => c.module === err.module;
  const relatedCases = [...CASES]
    .map(c => ({ c, score: (tagHit(c) ? 4 : 0) + (ruleHit(c) ? 2 : 0) + (moduleHit(c) ? 1 : 0) + (c.grade === '反例' ? 1 : 0) }))
    .filter(x => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .map(x => x.c);
  // Evidence preference: mistake-tagged anti case > any anti case > top-ranked case.
  const evidenceCase = relatedCases.find(c => tagHit(c) && c.grade === '反例')
    || relatedCases.find(c => c.grade === '反例')
    || relatedCases[0]
    || CASES[0];

  return (
    <AppLayout activeTop="mistakes" activeModule="mistakes" navigate={navigate}
      onModuleClick={(id) => id === 'mistakes' ? navigate('mistakes') : navigate(`module/${id}`)}>
      <div className="p-12 max-w-[1120px] mx-auto">
        <button onClick={() => navigate('mistakes')} className="font-['Work_Sans'] text-[14px] text-[#6B6B66] hover:text-[#1A1A19] mb-6 flex items-center gap-1">
          <span className="material-symbols-outlined text-[16px]">arrow_back</span>返回错误日志
        </button>
        <header className="mb-8 pb-4 border-b border-[#D8D1C3]">
          <div className="flex items-center gap-3 mb-3">
            <span className="material-symbols-outlined text-[#ba1a1a]">{err.icon}</span>
            <DataPill tone="red">{err.category}</DataPill>
            {err.freq && <DataPill tone="red">{err.freq}</DataPill>}
          </div>
          <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2] text-[#1A1A19] mb-2">{err.name}</h1>
          <p className="font-['Work_Sans'] text-[18px] leading-[1.6] text-[#6B6B66] max-w-3xl">{err.desc}</p>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <div className="xl:col-span-7 space-y-6">
            <section className="bg-white border border-[#D8D1C3] rounded p-6">
              <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">错误拆解</h2>
              <div className="space-y-4">
                <div><DataPill>症状</DataPill><p className="font-['Work_Sans'] text-[15px] text-[#1A1A19] mt-2">{err.symptom}</p></div>
                <div><DataPill>违反规则</DataPill><p className="font-['Work_Sans'] text-[15px] text-[#1A1A19] mt-2">{relatedRules.map(r => r.name).join('、') || err.rule}</p></div>
                <div><DataPill>纠正动作</DataPill><p className="font-['Work_Sans'] text-[15px] text-[#1A1A19] mt-2">{err.correction}</p></div>
              </div>
            </section>
            <section>
              <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">反例证据</h2>
              <KlineView mode="evidence" height={360} segmentId={evidenceCase?.segment_id} caseId={evidenceCase?.id} />
            </section>
          </div>

          <aside className="xl:col-span-5 space-y-6">
            <section className="bg-white border border-[#D8D1C3] rounded p-6">
              <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">关联策略</h2>
              <button onClick={() => navigate(`module/${mod.id}`)} className="w-full text-left border border-[#D8D1C3] p-4 rounded hover:border-[#8B9A6D]">
                <span className="font-['Space_Grotesk'] text-[12px] text-[#6B6B66]">{mod.num}</span>
                <h3 className="font-['Newsreader'] text-[22px] text-[#1A1A19]">{mod.name}</h3>
                <p className="font-['Work_Sans'] text-[14px] text-[#6B6B66] mt-1">{mod.goal}</p>
              </button>
            </section>
            <section className="bg-white border border-[#D8D1C3] rounded p-6">
              <h2 className="font-['Newsreader'] text-[24px] font-medium mb-4">相关案例</h2>
              <div className="space-y-3">
                {relatedCases.slice(0, 4).map(c => (
                  <button key={c.id} onClick={() => navigate(`case/${c.id}`)} className="w-full flex justify-between items-center text-left border border-[#E6E0D3] px-3 py-2 rounded hover:bg-[#FAF9F5]">
                    <span className="font-['Work_Sans'] text-[14px]">{c.title}</span>
                    <GradePill grade={c.grade} />
                  </button>
                ))}
              </div>
            </section>
            <button onClick={() => navigate(`training/${err.module}`)}
              className="w-full bg-[#1A1A19] text-white font-['Work_Sans'] text-[16px] py-3 rounded hover:bg-[#2A2924] transition-colors flex justify-center items-center gap-2">
              进入纠正训练 <span className="material-symbols-outlined text-sm">arrow_forward</span>
            </button>
          </aside>
        </div>
      </div>
    </AppLayout>
  );
}

function PlaybookPage({ navigate }) {
  const [selectedRule, setSelectedRule] = React.useState(RULES[0]);
  const [filterType, setFilterType] = React.useState('全部');
  const types = ['全部', '进场信号', '过滤条件', '出场规则', '不做条件'];
  const filtered = filterType === '全部' ? RULES : RULES.filter(r => r.type === filterType);

  return (
    <AppLayout activeTop="playbook" activeModule={null} navigate={navigate}>
      <div className="p-12 max-w-[1280px] mx-auto">
        <header className="mb-8 pb-4 border-b border-[#cbc6bd]">
          <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2] mb-2">规则库</h1>
          <p className="font-['Work_Sans'] text-[18px] leading-[1.6] text-[#494740] max-w-2xl">
            Rule Contract 的可视化速查。一本可搜索、可过滤、可复核的交易执行手册。
          </p>
        </header>

        <div className="flex gap-3 mb-6 flex-wrap">
          {types.map(t => (
            <button key={t} onClick={() => setFilterType(t)}
              className={`px-3 py-1.5 rounded font-['Inter'] text-[12px] font-semibold tracking-[0.05em] border transition-colors ${filterType === t ? 'bg-[#000] text-white border-[#000]' : 'bg-white text-[#494740] border-[#cbc6bd] hover:bg-[#f1edec]'}`}>
              {t}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Rule list */}
          <div className="xl:col-span-5 space-y-3">
            {filtered.map(rule => (
              <div key={rule.id} onClick={() => setSelectedRule(rule)}
                className={`p-4 border rounded cursor-pointer transition-all ${selectedRule?.id === rule.id ? 'border-[#285fa2] bg-[#d5e3ff]/10 shadow-[0px_4px_12px_rgba(23,22,19,0.05)]' : 'border-[#ded7ca] bg-white hover:shadow-[0px_4px_12px_rgba(23,22,19,0.05)]'}`}>
                <div className="flex justify-between items-start mb-2">
                  <span className="font-['Space_Grotesk'] text-[12px] text-[#7a776f]">{rule.id.toUpperCase()}</span>
                  <div className="flex gap-2">
                    <span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] px-2 py-0.5 bg-[#f1edec] text-[#494740] rounded-sm border border-[#cbc6bd]/30">{rule.type}</span>
                    <span className={`font-['Inter'] text-[10px] font-semibold tracking-[0.05em] px-2 py-0.5 rounded-sm border ${rule.status === '已审核' ? 'bg-[#d5e3ff]/20 text-[#004585] border-[#a7c8ff]/30' : 'bg-[#f1edec] text-[#7a776f] border-[#cbc6bd]/30'}`}>{rule.status}</span>
                  </div>
                </div>
                <h3 className="font-['Newsreader'] text-[18px] font-medium">{rule.name}</h3>
                <p className="font-['Work_Sans'] text-[14px] text-[#494740] mt-1 line-clamp-2">{rule.setup}</p>
              </div>
            ))}
          </div>

          {/* Rule detail */}
          <div className="xl:col-span-7">
            {selectedRule && (
              <div className="bg-white border border-[#ded7ca] rounded p-6 shadow-[0px_4px_12px_rgba(23,22,19,0.05)] sticky top-6">
                <div className="flex justify-between items-start mb-4 pb-3 border-b border-[#ded7ca]">
                  <div>
                    <span className="font-['Space_Grotesk'] text-[12px] text-[#7a776f] block mb-1">{selectedRule.id.toUpperCase()}</span>
                    <h2 className="font-['Newsreader'] text-[32px] font-medium leading-[1.3]">{selectedRule.name}</h2>
                  </div>
                  <span className={`font-['Inter'] text-[12px] font-semibold tracking-[0.05em] px-2 py-1 rounded-sm border ${selectedRule.status === '已审核' ? 'bg-[#d5e3ff]/20 text-[#004585] border-[#a7c8ff]/30' : 'bg-[#f1edec] text-[#7a776f] border-[#cbc6bd]/30'}`}>{selectedRule.status}</span>
                </div>
                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">成立条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{selectedRule.setup}</p></div>
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">触发条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{selectedRule.trigger}</p></div>
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">过滤条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{selectedRule.filter}</p></div>
                  <div><span className="font-['Inter'] text-[10px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-1">失效条件</span><p className="font-['Work_Sans'] text-[14px] text-[#494740]">{selectedRule.invalid}</p></div>
                </div>
                <div className="border-t border-[#ded7ca] pt-4 flex gap-3">
                  {CASES.filter(c => c.module === selectedRule.module).length > 0 && (
                    <button onClick={() => navigate(`case/${CASES.find(c => c.module === selectedRule.module).id}`)}
                      className="px-4 py-2 border border-[#000] text-[#000] rounded font-['Inter'] text-[12px] font-semibold tracking-[0.05em] hover:bg-[#ebe7e6] transition-colors">
                      查看案例
                    </button>
                  )}
                  <button onClick={() => navigate(`module/${selectedRule.module}`)}
                    className="px-4 py-2 text-[#285fa2] font-['Work_Sans'] text-[14px] hover:underline">
                    进入策略章节 →
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

function ArchivesPage({ navigate }) {
  const [filterModule, setFilterModule] = React.useState('全部');
  const [filterGrade, setFilterGrade] = React.useState('全部');
  const modules = ['全部', ...MODULES.map(m => m.name)];
  const grades = ['全部', '标准例', '边缘例', '反例'];

  const filtered = CASES.filter(c => {
    const modMatch = filterModule === '全部' || MODULES.find(m => m.id === c.module)?.name === filterModule;
    const gradeMatch = filterGrade === '全部' || c.grade === filterGrade;
    return modMatch && gradeMatch;
  });

  return (
    <AppLayout activeTop="archives" activeModule={null} navigate={navigate}>
      <div className="p-12 max-w-[1280px] mx-auto">
        <header className="mb-8 pb-4 border-b border-[#cbc6bd]">
          <h1 className="font-['Newsreader'] text-[40px] font-semibold leading-[1.2] mb-2">案例档案</h1>
          <p className="font-['Work_Sans'] text-[18px] leading-[1.6] text-[#494740] max-w-2xl">
            全部实盘样本的检索与归档。按日期、策略模块、样本类型快速定位。
          </p>
        </header>

        {/* Filters */}
        <div className="flex flex-wrap gap-6 mb-6">
          <div>
            <span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-2">策略模块</span>
            <div className="flex gap-2 flex-wrap">
              {modules.map(m => (
                <button key={m} onClick={() => setFilterModule(m)}
                  className={`px-3 py-1.5 rounded font-['Inter'] text-[12px] font-semibold tracking-[0.05em] border transition-colors ${filterModule === m ? 'bg-[#000] text-white border-[#000]' : 'bg-white text-[#494740] border-[#cbc6bd] hover:bg-[#f1edec]'}`}>
                  {m}
                </button>
              ))}
            </div>
          </div>
          <div>
            <span className="font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase block mb-2">样本类型</span>
            <div className="flex gap-2">
              {grades.map(g => (
                <button key={g} onClick={() => setFilterGrade(g)}
                  className={`px-3 py-1.5 rounded font-['Inter'] text-[12px] font-semibold tracking-[0.05em] border transition-colors ${filterGrade === g ? 'bg-[#000] text-white border-[#000]' : 'bg-white text-[#494740] border-[#cbc6bd] hover:bg-[#f1edec]'}`}>
                  {g}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white border border-[#ded7ca] rounded overflow-hidden shadow-[0px_4px_12px_rgba(23,22,19,0.05)]">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[#ded7ca] bg-[#f7f3f1]">
                <th className="text-left px-4 py-3 font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase">案例</th>
                <th className="text-left px-4 py-3 font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase">日期</th>
                <th className="text-left px-4 py-3 font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase">策略</th>
                <th className="text-left px-4 py-3 font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase">类型</th>
                <th className="text-left px-4 py-3 font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase">方向</th>
                <th className="text-left px-4 py-3 font-['Inter'] text-[12px] font-semibold tracking-[0.05em] text-[#7a776f] uppercase">结果</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(c => {
                const mod = MODULES.find(m => m.id === c.module);
                return (
                  <tr key={c.id} className="border-b border-[#ded7ca] last:border-b-0 hover:bg-[#f7f3f1] transition-colors cursor-pointer"
                    onClick={() => navigate(`case/${c.id}`)}>
                    <td className="px-4 py-3 font-['Newsreader'] text-[16px] font-medium">{c.title}</td>
                    <td className="px-4 py-3 font-['Space_Grotesk'] text-[14px] text-[#494740]">{c.date}</td>
                    <td className="px-4 py-3 font-['Work_Sans'] text-[14px] text-[#494740]">{mod?.name}</td>
                    <td className="px-4 py-3"><GradePill grade={c.grade} /></td>
                    <td className="px-4 py-3 font-['Space_Grotesk'] text-[14px]">{c.direction}</td>
                    <td className="px-4 py-3 font-['Space_Grotesk'] text-[14px] font-medium text-[#285fa2]">{c.result}</td>
                    <td className="px-4 py-3"><span className="material-symbols-outlined text-[16px] text-[#7a776f]">arrow_forward</span></td>
                  </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr><td colSpan="7" className="px-4 py-8 text-center font-['Work_Sans'] text-[14px] text-[#7a776f]">暂无匹配的案例</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  );
}


Object.assign(window, { TrainingPage, MistakesPage, MistakeDetailPage, PlaybookPage, ArchivesPage });
