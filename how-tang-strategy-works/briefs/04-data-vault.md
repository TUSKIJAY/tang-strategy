## Module 4: 数据保险库

### Teaching Arc
- **Metaphor:** 银行金库——外面有「受理窗口」的临时单据（seed JSON），真正上架的是金库里那本总账（tracked SQLite）。公开宣传册（GitHub Pages）也是从总账复印的，不是从草稿纸。
- **Opening hook:** 复盘包从 API 来，API 从 DB 读。那 DB 又从哪装货？还有不登录的公开静态站？
- **Key insight:** 唯一运行时真相是 `data/sqlite/tang_strategy_live_extended.db`。`content/trades` 是规范交易原文；seed 是本地抓取输入；Pages 是 DB 导出 JSON 再构建。
- **"Why should I care?":** AI 若把生成物写进 docs/ 或只改 seed 不 rebuild，你会发布错误数据。你会用正确词：candidate、promote、export、manifest。

### Code Snippets (pre-extracted)

File: backend/scripts/export_static_reviews.py (lines 18–21)
```
def slugify_day(day: dict[str, Any]) -> str:
    ticker = str(day["ticker"]).lower()
    session = str(day["session_mode"] or "session").lower().replace("_", "-")
    return f"{ticker}-{day['trade_date']}-{session}"
```

File: frontend/src/features/review/reviewWorkspace.js (lines 293–301)
```
export function resolveInitialWorkspace({ days = [], explicitKey = '', hash = '' } = {}) {
  const ordered = [...array(days)].sort(compareWorkspaceDays);
  if (!ordered.length) {
    return transition(null, { kind: 'empty', requested: '', reason: 'no-days' });
  }
  const explicit = findDayByKey(ordered, explicitKey);
  if (explicit) {
    return transition(explicit, { kind: 'explicit', requested: explicit.key, reason: '' });
  }
```

File: frontend/src/main.jsx (lines 63–65)
```
createRoot(document.getElementById('root')).render(
  import.meta.env.VITE_STATIC_REVIEWS === 'true' ? <StaticReviewsApp /> : <App />,
);
```

### Interactive Elements
- [x] **Code↔English** — slugify_day；resolveInitialWorkspace 确定性选择
- [x] **Quiz** — 3 题：Pages 读什么数据源；hash 无效时应该怎样；content/trades 与 DB 投影关系
- [x] **Numbered steps / flow** — seed → rebuild candidate → live DB → export JSON → StaticReviewsApp
- [x] **Layer or badge list** — interactive vs static 能力边界（无登录、无编辑）
- [x] **Callout** — 生成物不进 docs/

### Reference Files
- interactive-elements: Code↔English, Flow/steps, Quizzes, Badges, Callouts, Glossary
- content-philosophy, gotchas

### Connections
- **Previous:** API 对话
- **Next:** fail-closed 安全网 — 为什么更新要成对、可回滚

### Language
Simplified Chinese; exact code.
