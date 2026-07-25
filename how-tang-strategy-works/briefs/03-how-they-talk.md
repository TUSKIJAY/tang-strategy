## Module 3: 它们怎么对话

### Teaching Arc
- **Metaphor:** 门禁腕带——登录后拿到一条「临时通行证」（token），之后每次请求都要出示，不然被拒。
- **Opening hook:** 你知道谁是演员了。现在看他们怎么说话：密码 → token → 带 Authorization 的请求 → 组装好的复盘包。
- **Key insight:** 前端从不直接打开数据库；它只喊「API 路径」。后端校验身份后从 SQLite 拼出 `bars_1m`、`bars_5m`、`strategy`、`trade_records`。
- **"Why should I care?":** 「401 Unauthorized」和「图是空的」是完全不同的故障。能区分网络/鉴权/组装/渲染，就能打断 AI 的瞎改循环。

### Code Snippets (pre-extracted)

File: frontend/src/api/client.js (lines 18–28)
```
export async function login(password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ password }),
  });
  if (!response.ok) throw new Error('Password rejected');
  const data = await response.json();
  window.localStorage.setItem(TOKEN_KEY, data.token);
  window.localStorage.setItem(ROLE_KEY, data.role);
  return data;
}
```

File: frontend/src/api/client.js (lines 31–40)
```
export async function api(path, options = {}) {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
```

File: backend/app/auth.py (lines 49–54)
```
def role_from_password(password: str) -> Role | None:
    if password and hmac.compare_digest(password, settings.admin_password):
        return "admin"
    if password and hmac.compare_digest(password, settings.readonly_password):
        return "readonly"
    return None
```

File: backend/app/main.py (lines 157–169)
```
@app.get("/api/reviews/assemble")
def assemble_review(market_day_id: int, strategy_id: int, _: str = Depends(require_readonly)) -> dict[str, Any]:
    with connect() as conn:
        day = conn.execute("SELECT * FROM market_days WHERE id=?", (market_day_id,)).fetchone()
        if not day:
            raise HTTPException(status_code=404, detail="Market day not found")
        strategy_row = conn.execute("SELECT * FROM strategies WHERE id=? AND active=1", (strategy_id,)).fetchone()
        if not strategy_row:
            raise HTTPException(status_code=404, detail="Strategy not found")
        bars_1m_rows = _fetch_bar_rows(conn, "bars_1m", market_day_id)
        bars_5m = _build_5m_payload(conn, day, bars_1m_rows)
        strategy_json = json.loads(strategy_row["json_body"])
        trade_records = _trade_records_for_day(day["ticker"], day["trade_date"])
```

### Interactive Elements
- [x] **Code↔English** — login + api() Bearer 头；assemble_review 拼装
- [x] **Quiz** — 3 题：缺 token 症状；admin vs readonly 该找哪边；assemble 返回里没有 bars 先查什么
- [x] **Data flow animation** — Login → Token store → assemble request → DB → JSON bag（注意 data-steps 标签里不要用英文撇号 apostrophe）
- [x] **Callout** — Bearer token 像腕带；HMAC 比较密码防时序攻击可一句带过

### Reference Files
- interactive-elements: Code↔English, Message Flow, Quizzes, Callouts, Glossary
- content-philosophy, gotchas

### Connections
- **Previous:** 认识演员
- **Next:** 数据保险库 — 包里的数据从哪来、静态站怎么不登录也看得到

### Language
Simplified Chinese; exact code; no apostrophes inside single-quoted data-steps JSON labels.
