## Module 2: 认识演员

### Teaching Arc
- **Metaphor:** 剧组分工——前台演员（页面）、场务（API）、片库（SQLite）、剧本（strategies）、场记本（content/trades）。
- **Opening hook:** 上一课你看到「复盘一键出来」。这一课认识是谁在干活，方便你指挥 AI「改 X 别动 Y」。
- **Key insight:** Tang Strategy 是「全栈 monorepo」：浏览器里的 React 页面 + 服务器上的 FastAPI + 一个被 Git 跟踪的 SQLite 文件 + 规范 JSON 内容。
- **"Why should I care?":** 指错目录 = AI 改错层。能说出「这是 kline 引擎职责」就等于获得架构否决权。

### Code Snippets (pre-extracted)

File: frontend/src/main.jsx (lines 63–65)
```
createRoot(document.getElementById('root')).render(
  import.meta.env.VITE_STATIC_REVIEWS === 'true' ? <StaticReviewsApp /> : <App />,
);
```

File: backend/app/main.py (lines 36–43)
```
app = FastAPI(title="Tang Strategy API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Interactive Elements
- [x] **Code↔English translation** — VITE_STATIC_REVIEWS 双模式入口；FastAPI app 创建
- [x] **Quiz** — 3 题：静态 Pages vs 交互模式谁不该改登录；交易编辑应落 content 还是前端临时 state；kline 引擎 vs Review 业务控件所有权
- [x] **Group chat animation** — actors: Layout, ReviewPage, FastAPI, SQLite, KlineEngine. 对话：用户点 Review → Layout 切换 → ReviewPage 要数据 → FastAPI 查库 → 把包给 KlineEngine 画
- [x] **Visual file tree** — backend/app, frontend/src, data/sqlite, content/, strategies/
- [x] **Pattern cards or icon rows** — 6 个主角职责一句话
- [x] **Architecture diagram** optional if space

### Reference Files to Read
- `references/interactive-elements.md` → Group Chat, Visual File Tree, Icon-Label Rows / Pattern Cards, Code↔English, Quizzes, Glossary
- `references/content-philosophy.md` → always
- `references/gotchas.md` → always

### Connections
- **Previous:** 点开复盘 — 用户旅程
- **Next:** 它们怎么对话 — token、Bearer、assemble 细节
- **Tone:** 中文；actor 名固定：Layout, ReviewPage, FastAPI, SQLite, KlineEngine, StaticReviewsApp, Content Repo

### Language
Simplified Chinese prose; exact code; tooltips on first tech terms.
