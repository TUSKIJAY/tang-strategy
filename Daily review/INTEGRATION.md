# Daily Review Agent Handoff

> 给后续 agent 的入口文档。先读这里，再读 `strategies/STRATEGY.md` 和 `strategies/strategy.schema.json`。
>
> 当前重点：把所有 Tang Strategy 策略沉淀成可校验的 JSON，并让 Daily Review 前端、Python 扫描器、回测脚本逐步围绕同一份策略配置工作。

## 1. 这是什么

`Daily review` 是一个本地静态复盘工具，不是通用交易平台。它服务于 Tang Strategy 的 SPY 日内复盘、信号标注、策略版本迭代和回测验证。

核心入口：

- `daily-review.html`：单文件静态前端。负责加载行情 JSON、展示 1m / 5m K 线、均线、VWAP、成交量、策略信号、交易区间和复盘 UI。
- `strategies/*.json`：策略机器配置。后续所有策略都应该转成这里的 JSON。
- `strategies/strategy.schema.json`：策略 JSON Schema。新增或修改策略时必须尽量通过它校验。
- `strategies/STRATEGY.md`：Tang Strategy 人工语义规范。改交易逻辑前必须先读。
- `app-data/scripts/scan_signals.py`：读取行情 JSON + 策略 JSON，输出带 annotations 的 reviewed JSON。
- `app-data/scripts/backtest.py`：SPY options scalping 回测脚本。

一句话目标：让“人工策略经验”变成“可版本化、可校验、可扫描、可复盘、可回测”的本地系统。

## 2. 现在要干什么

当前主线是策略 JSON 化和执行一致性：

1. 维护策略 JSON

   所有策略版本放在 `strategies/tang_*.json`。不要覆盖旧版本，新增版本用新文件名。每个文件要写清楚 `name`、`version`、`description`，并尽量加：

   ```json
   "$schema": "./strategy.schema.json"
   ```

2. 维护 JSON Schema

   `strategies/strategy.schema.json` 是策略结构的护栏。它现在已经兼容：

   - `tang_v1.json`
   - `tang_v2.json`
   - `tang_v3.json`
   - `tang_v3_3_1_flame.json`
   - `tang_v3_5_1_full.json`
   - `tang_v4_4_slope.json`

   如果新增策略需要新模块，优先扩展 schema，而不是绕过 schema。

3. 统一执行层

   长期目标是让策略 JSON 成为唯一策略输入。前端可以展示和预览，但权威扫描结果应逐步收敛到 `scan_signals.py` 生成的 reviewed JSON。

4. 保持三层一致

   改策略时要同步检查：

   - 人工规则：`strategies/STRATEGY.md`
   - 机器配置：`strategies/tang_*.json`
   - 执行逻辑：`daily-review.html` / `app-data/scripts/scan_signals.py` / `app-data/scripts/backtest.py`

## 3. 怎么干

### 进入项目后的第一步

```powershell
cd "Daily review"
git status --short
Get-ChildItem strategies
```

注意：这个仓库里经常有用户或其他 agent 的未提交改动。不要回滚、不覆盖、不顺手清理和当前任务无关的文件。

### 打开前端

前端没有构建步骤，直接打开 HTML：

```powershell
Start-Process ".\daily-review.html"
```

页面主要使用三类输入：

- `market-data/live/YYYY-MM-DD/SPY_YYYY-MM-DD.json`
- `reviewed/*.json`
- `strategies/tang_*.json`

### 校验策略 JSON

当前用 `ajv-cli` 校验 draft 2020-12 schema：

```powershell
npx --yes ajv-cli@5 validate --spec=draft2020 `
  -s "strategies/strategy.schema.json" `
  -d "strategies/tang_v*.json"
```

期望所有 `tang_v*.json` 都 valid。若失败，先判断是策略文件真的缺字段，还是 schema 对已有合理结构收得太紧。

### 生成 reviewed JSON

```powershell
python "app-data/scripts/scan_signals.py" `
  --data "market-data/live/2026-04-22/SPY_2026-04-22.json" `
  --strategy "strategies/tang_v3_5_1_full.json" `
  --out "reviewed/SPY_2026-04-22.tang_v3_5_1_full.json"
```

输出文件必须能被 `daily-review.html` 加载，并保留 `annotations_1m` / `annotations_5m`。

### 跑回测

```powershell
python "app-data/scripts/backtest.py" 2026-04-14 --profile loose

python "app-data/scripts/backtest.py" 2026-04-13 2026-04-14 2026-04-15 `
  --batch --profile moderate --prem-sl 50 --prem-tp 80 --trail 35
```

`backtest.py` 默认从 `Daily review/data/` 找原始 CSV，也支持 `TANG_DATA_DIR`：

```powershell
$env:TANG_DATA_DIR = "D:\path\to\data"
```

## 4. 目录地图

```text
Daily review/
  daily-review.html                 # 静态前端入口，包含 UI、Kline Engine、浏览器端策略扫描/展示 glue
  INTEGRATION.md                    # 本文，agent handoff
  app-data/
    scripts/
      scan_signals.py               # 行情 JSON + 策略 JSON -> reviewed JSON
      backtest.py                   # SPY 期权策略回测
  market-data/
    live/YYYY-MM-DD/
      SPY_YYYY-MM-DD.json           # 日内行情 JSON
      tradytics_options_market_gex_*.json
  reviewed/
    *.json                          # 已扫描、带 annotations 的复盘数据
  strategies/
    STRATEGY.md                     # Tang Strategy 人工规范
    strategy.schema.json            # 策略 JSON Schema
    tang_v*.json                    # 策略配置版本
    tang_*.pine                     # PineScript 实现或参考
```

## 5. 数据契约

行情 / reviewed JSON 顶层结构：

```json
{
  "meta": {
    "title": "SPY 2026-04-13 Full Day",
    "ticker": "SPY",
    "date": "2026-04-13",
    "strategy": {
      "name": "Tang v3.5.1 Full",
      "version": "3.5.1"
    }
  },
  "bars_1m": [],
  "bars_5m": [],
  "annotations_1m": [],
  "annotations_5m": []
}
```

bar 常用字段：

- 时间：`ts`, `t`
- 原始 OHLCV：`O`, `H`, `L`, `C`, `V`
- Heikin-Ashi：`hO`, `hH`, `hL`, `hC`
- 指标：`m5`, `m10`, `m20`, `m30`, `m50`, `m60`, `m120`, `m200`, `vw`

annotation 常用字段：

```json
{
  "bar_index": 123,
  "timeframe": "1m",
  "title": "Strong PUT",
  "body": "reason / detail",
  "type": "signal",
  "style": "red",
  "anchor_side": "top",
  "score": 2
}
```

前端会做宽松 normalize，但新脚本不要依赖隐式默认值。输出时尽量补齐字段。

## 6. 策略 JSON 约定

最小稳定骨架：

```json
{
  "$schema": "./strategy.schema.json",
  "name": "Tang vX",
  "version": "X.Y",
  "description": "这一版相对上一版改变了什么",
  "trend": {},
  "signals": [],
  "scoring": { "enabled": false },
  "exit": {},
  "filter": {},
  "hard_blocks": {}
}
```

策略 JSON 的设计原则：

- `description` 必须写人话，方便复盘时知道这一版为什么存在。
- `signals[].id` 保持稳定，展示层和 reviewed JSON 可能依赖它。
- 派生信号可以用 `extends + extra_conditions`，不一定要重复完整 `conditions`。
- 新增模块可以先作为普通 object 放入，但要补到 `strategy.schema.json` 的 `properties` 里。
- 不要把执行状态、当天交易情绪、临时备注写进策略 JSON。策略 JSON 只放可复用规则。

## 7. Tang Strategy 核心边界

不要把它改成普通指标交叉系统。当前策略精神是：

1. 5m 先定大方向。
2. 1m 等 MA10 / MA20 / MA30 附近的 HA 形态。
3. 顺势做 CALL / PUT，不猜顶底，不做反手。
4. 用 MA50 / MA200 / VWAP 判断前方空间和止盈压力。
5. 入场理由消失就出场。

版本差异很重要：

- v1/v2 偏早期：严格趋势、MA10 Reject / Support、基础评分或无评分。
- v3 系列加入多周期冲突、空间、成交量、分批止盈、期权上下文。
- v3.3.1 / v3.5.1 / v4.4 是从 PineScript/消息转换来的更完整配置。
- v4.4 Slope 加入 5m MA10/20/30 顺势过滤、1m MA10 斜率、持仓状态机、10 根 K 冷却、elite Strong 判定。

不要把某一版的规则硬套到所有版本。执行层应读取策略 JSON，而不是用文件名猜规则。

## 8. Kline Engine 注意点

`daily-review.html` 内嵌 Kline Engine v2，并额外加了 Daily Review 的交易复盘层。

需要保留的扩展：

- `engine._trades`
- `simulateTrades()`
- `drawTradeZones(ctx, rc)`
- 渲染顺序中交易区间和 annotation pin 的叠加

常用 API：

- `setCandleType('ha' | 'normal')` / `getCandleType()`
- `setRevealCutoff(input)` / `getRevealCutoff(timeframe?)`
- `setHighlightRanges(input)` / `getHighlightRanges()`
- `setTheme('dark' | 'light')` / `getTheme()`
- `engine.maVisibility` 控制 MA/VWAP 显隐

同步上游 Kline Engine 时不能简单覆盖 `daily-review.html`，要确认这些 Daily Review 扩展还在。

## 9. 优先级路线

建议新 agent 按这个顺序推进：

1. 策略 JSON/schema

   新策略先写 JSON，再跑 schema 校验，再用真实日数据扫描。

2. 扫描一致性

   优先让 `scan_signals.py` 覆盖更多策略字段，减少前端和 Python 双实现漂移。

3. reviewed 数据质量

   用 `reviewed/*.json` 固定样例检查信号数量、关键时间、图上 pin、统计卡片是否稳定。

4. 前端拆分

   `daily-review.html` 已经很大。后续可拆成 `src/kline-engine.js`、`src/signal-scanner.js`、`src/storage.js`、`src/app.js`、`src/styles.css`。拆分前先决定是否继续支持直接打开 HTML。

5. 回测贴合策略 JSON

   `backtest.py` 目前仍有大量内置逻辑。长期目标是让它读取策略 JSON 的 exit/filter/options，而不是维护另一套参数宇宙。

## 10. 验收清单

改完至少检查：

- `daily-review.html` 能直接打开，无控制台错误。
- 加载 `market-data/live/.../SPY_*.json` 能显示 1m / 5m K 线。
- 加载 `reviewed/*.json` 不丢 annotations。
- 上传或选择策略后，图上 pin、信号列表、顶部统计一致。
- HA / OHLC、Light / Dark、MA/VWAP 显隐可切换。
- 播放、步进、缩放、Follow、Overview 可用。
- `setRevealCutoff()` 和 `setHighlightRanges()` 仍可用于教学联动。
- `scan_signals.py` 能生成 reviewed JSON，且前端可加载。
- 策略文件通过 `strategy.schema.json` 校验。
- 如果改了回测，至少跑一个单日命令和一个 batch 命令。

## 11. 不要做

- 不要删除历史 `tang_v*.json`。它们是策略演化记录。
- 不要覆盖 reviewed 文件，除非输出文件名明确包含日期和策略版本。
- 不要只改前端扫描逻辑而忘记 `scan_signals.py`，也不要反过来。
- 不要把 Tang Strategy 简化成 MA 金叉死叉。
- 不要在 canvas render 里塞复杂业务计算。指标和信号应来自数据或扫描层。
- 不要碰和当前任务无关的 git 改动。

## 12. 快速定位

- 入口文档：`INTEGRATION.md`
- 页面入口：`daily-review.html`
- 策略文字规范：`strategies/STRATEGY.md`
- 策略 schema：`strategies/strategy.schema.json`
- 当前最完整配置之一：`strategies/tang_v3_5_1_full.json`
- 当前最新斜率版配置：`strategies/tang_v4_4_slope.json`
- 信号扫描：`app-data/scripts/scan_signals.py`
- 回测：`app-data/scripts/backtest.py`
- 示例 reviewed：`reviewed/kline-engine-v2-full-day.json`
