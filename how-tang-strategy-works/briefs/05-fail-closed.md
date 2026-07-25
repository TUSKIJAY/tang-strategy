## Module 5: 宁可失败也不乱写

### Teaching Arc
- **Metaphor:** 空管塔台换跑道——新航班计划（candidate）必须全部检查通过，旧跑道（live DB）先备份；半空中发现问题就立刻切回备份，绝不半套计划落地。
- **Opening hook:** 每天要更新 SPY 和 QQQ。为什么不是「有一个就算了」？为什么 rebuild 失败时旧库必须完好？
- **Key insight:** Fail-closed：校验不过就拒绝写入。`promote_candidate` 对比-and-swap；pair orchestrator 要求同 provider 双标的同时通过。
- **"Why should I care?":** 你可以对 AI 说「禁止 --allow-date-loss」「禁止单 ticker 接受」「TV 优先，IB 只在硬门失败后」。这是生产可靠性语言。

### Code Snippets (pre-extracted)

File: backend/app/services/db_safety.py (lines 213–220)
```
def promote_candidate(
    live_path: Path,
    candidate_path: Path,
    baseline_token: DatabaseToken,
    backup_path: Path,
    post_validate: Callable[[Path], None],
) -> None:
    """Compare-and-swap a verified candidate while preserving a verified backup."""
```

File: backend/app/services/db_safety.py (lines 237–268)
```
    with db_write_lock(live):
        _checkpoint_and_require_quiescent(live)
        current_token = capture_database_token(live)
        if current_token != baseline_token:
            raise RuntimeError(
                "Refusing DB promotion: live DB drifted after the candidate snapshot "
                f"(baseline={baseline_token.as_dict()}, current={current_token.as_dict()})"
            )
        # ... identity checks ...
        os.replace(candidate, live)
        fsync_directory(live.parent)
        try:
            post_validate(live)
        except Exception:
            os.replace(backup, live)
            fsync_directory(live.parent)
            raise
```

File: backend/scripts/update_spy_qqq_market_day.py (lines 43–46)
```
PAIR = ("SPY", "QQQ")
SESSION_MODE = "extended"
PROVIDERS = {"tradingview", "ibkr"}
TRADINGVIEW_EXCHANGES = {"SPY": "AMEX", "QQQ": "NASDAQ"}
```

### Interactive Elements
- [x] **Code↔English** — promote_candidate 锁 + 漂移拒绝 + 失败回滚
- [x] **Quiz** — 3 场景：只拿到 SPY 怎么办；promote 中途 post_validate 失败；AI 提议 --allow-date-loss 日常用
- [x] **Data flow or step cards** — stage pair → validate → candidate → promote or keep old
- [x] **Callout** — fail-closed vs fail-open
- [x] **Optional spot-the-bug** — 伪代码里「先删 live 再写 candidate」是 bug

### Reference Files
- interactive-elements: Code↔English, Flow, Quizzes, Spot the Bug optional, Callouts, Glossary
- content-philosophy, gotchas

### Connections
- **Previous:** 数据从哪来
- **Next:** 指挥 AI — 所有权边界与调试地图

### Language
Simplified Chinese; exact code; no apostrophes in data-steps labels (use "it is" not "it's").
