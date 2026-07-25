## Module 1: 点开复盘

### Teaching Arc
- **Metaphor:** 像进电影院：你选好哪部片子（标的+日期），放映员把胶片（K 线）和字幕（交易点位）一起装进放映机。
- **Opening hook:** 你打开 Tang Strategy，登录后点「复盘」，选一个交易日——图表和交易标记就出现了。下面拆开这一秒里发生了什么。
- **Key insight:** 屏幕上的「一页复盘」不是魔法，是后端把行情 + 策略 + 交易记录打包成一份 JSON 后，前端再画出来。
- **"Why should I care?":** 知道这条链路后，你才能对 AI 说「改的是组装接口，还是画图引擎」，而不是「图坏了你看着办」。

### Code Snippets (pre-extracted)

File: frontend/src/main.jsx (lines 42–49)
```
  if (!authenticated) return <LoginPage onLogin={() => setAuthenticated(true)} />;

  return (
    <Layout active={active} onNavigate={setActive}>
      {active === 'dashboard' && <DashboardPage state={state} setState={setState} onNavigate={setActive} />}
      {active === 'review' && <ReviewPage state={state} setState={setState} onNavigate={setActive} />}
      {active === 'backtest' && <BacktestPage state={state} setState={setState} />}
```

File: frontend/src/pages/ReviewPage.jsx (lines 259–265)
```
  useEffect(() => {
    if (!selectedDay || !selectedStrategy) return;
    setLoading(true);
    setError('');
    Api.review(selectedDay.id, selectedStrategy.id)
      .then((payload) => {
        setReview(payload);
```

File: frontend/src/api/client.js (lines 54–59)
```
export const Api = {
  tickers: () => api('/tickers'),
  marketDays: (params = {}) => api(`/market-days?${new URLSearchParams(params)}`),
  bars: (id, timeframe) => api(`/market-days/${id}/bars?timeframe=${timeframe}`),
  strategies: () => api('/strategies'),
  review: (marketDayId, strategyId) => api(`/reviews/assemble?market_day_id=${marketDayId}&strategy_id=${strategyId}`),
```

### Interactive Elements
- [x] **Code↔English translation** — main.jsx 路由切换；ReviewPage 的 Api.review 调用
- [x] **Quiz** — 3 道场景题：用户看不到图时优先查哪一层；assemble 缺什么参数；登录页 vs 复盘页职责
- [x] **Data flow animation** — actors: You → ReviewPage → API → SQLite → Chart. Steps: 选日 → 请求 assemble → 读库 → 返回 payload → 画图
- [x] **Numbered step cards** — 用户旅程 5 步
- [x] **Callout** — 「一页 = 一次组装」

### Reference Files to Read
- `references/interactive-elements.md` → Code↔English, Message Flow, Numbered Step Cards, Multiple-Choice Quizzes, Callout Boxes, Glossary Tooltips
- `references/content-philosophy.md` → always
- `references/gotchas.md` → always

### Connections
- **Previous module:** none — course start
- **Next module:** 认识演员 — 会命名 frontend / backend / DB / content
- **Tone/style notes:** 中文正文；技术词保留英文并加 term tooltip；accent forest；不要用 restaurant 隐喻；actor 命名统一：ReviewPage / FastAPI / SQLite / KlineEngine

### Language
Write all learner-facing prose in **Simplified Chinese**. Keep code snippets exact English. Technical terms first-use get `.term` tooltips in Chinese definitions.
