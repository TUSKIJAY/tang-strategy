## Module 6: 像船长一样指挥 AI

### Teaching Arc
- **Metaphor:** 航海图 + 职责牌——每块甲板（前端业务 / 引擎 / API / 内容 / 发布）有明确「谁说了算」；你不需要自己掌舵每一个螺丝，但要知道哪张海图该拿给大副。
- **Opening hook:** 你已经看过旅程、演员、对话、金库和安全阀。最后一课：用这张地图指挥 AI、打断死循环、做架构决策。
- **Key insight:** 所有权边界是第一生产力。`reviewWorkspace.js` 是纯函数工作区逻辑；kline 引擎只管图表通用控件；canonical trades 走完整文档原子写；远程动作永远需要单独授权。
- **"Why should I care?":** 这是 vibe coding 的毕业技能：用正确词汇下指令，用症状反查层级，拒绝 AI 越权（push / publish / --allow-date-loss）。

### Code Snippets (pre-extracted)

File: frontend/src/features/review/reviewWorkspace.js (lines 332–357)
```
// Ticker switch: keep the same date only when the target ticker owns it,
// otherwise select the target ticker's newest real date. A ticker without days
// is never fabricated; the current context is kept and reported.
export function switchTicker(days = [], current = {}, nextTicker = '') {
  const ordered = [...array(days)].sort(compareWorkspaceDays);
  const wanted = cleanText(nextTicker).toUpperCase();
  // ...
  const sameDate = currentDay
    ? targetDays.find((day) => day.trade_date === currentDay.trade_date)
    : null;
  if (sameDate) {
    return transition(sameDate, { kind: 'same-date', requested: wanted, reason: '' }, previousContext);
  }
  return transition(targetDays[0], { kind: 'newest-date', requested: wanted, reason: 'date-not-owned' }, previousContext);
}
```

File: frontend/src/features/review/reviewWorkspace.js (lines 359–371)
```
// Explicit day selection ... only a real day may be selected; a missing ticker/date keeps the current
// context and is reported instead of silently substituting another day.
export function selectWorkspaceDay(days = [], current = {}, { ticker = '', tradeDate = '', key = '' } = {}) {
  const previousContext = cleanText(current.context) || contextToken(current.day);
  const currentDay = current.day || null;
  const target = key
    ? findDayByKey(days, key)
    : findDay(days, { ticker, tradeDate });
  if (!target) {
    return transition(currentDay, {
      kind: 'missing-date',
      requested: key || `${cleanText(ticker).toUpperCase()}:${cleanText(tradeDate)}`,
      reason: 'no-such-day',
```

### Interactive Elements
- [x] **Code↔English** — switchTicker 不捏造日期；selectWorkspaceDay fail-closed 选择
- [x] **Quiz** — 3–4 场景题：日期 rail 顺序问题找谁；marker 颜色找谁；要发布需什么授权；401 vs 空图 vs 发布后旧数据
- [x] **Drag-and-drop or pattern cards** — 症状 → 先看哪一层（鉴权 / assemble / content / rebuild / Pages）
- [x] **Callout** — 小步本地 commit ≠ 授权 push/PR/Pages
- [x] **Icon rows** — 指挥 AI 的话术清单（中英术语对照）

### Reference Files
- interactive-elements: Code↔English, Quizzes, DnD or Pattern Cards, Callouts, Icon Rows, Glossary
- content-philosophy, gotchas

### Connections
- **Previous:** fail-closed
- **Next:** none — course end; encourage opening index and scrolling back

### Language
Simplified Chinese; exact code; practical AI-steering phrases.
