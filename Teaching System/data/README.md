# SPY 实盘数据目录

## 目录结构

```
data/
├── raw/                    # 原始下载数据，只进不改
│   ├── daily/              # 每日收盘下载（日常操作）
│   │   └── SPY_1min_YYYY-MM-DD.csv
│   └── bulk/               # 历史批量下载
│       ├── SPY_1min_<start>_<end>.csv             # 老 bulk（可能含 gap/short）
│       └── SPY_1min_<start>_<end>.continuous.csv  # Polygon 重拉的连续版本（v0.6）
├── processed/              # 程序加工后的数据（引擎默认池）
│   ├── SPY_YYYY-MM-DD.json
│   └── synthetic_fallback/  # gap-fill 合成的日（v0.7+ 扫描器默认不读）
├── build_json.py             # 主数据管道：CSV → JSON（含 warmup / SMA / HA / VWAP）
├── slice_teaching_segment.py # 切片工具（v0.6）：从 processed/ 切教学窗口
├── aggregate_5min.py         # 辅助工具：1min → 5min 聚合
├── JSON_SCHEMA.md            # JSON 输出格式规范
└── README.md                 # 本文件
```

## 脚本说明

### `build_json.py` — 主数据管道

**功能**：从 1min CSV 生成引擎可消费的 `processed/SPY_YYYY-MM-DD.json`

**核心特性**：
- 自动计算 HA（Heikin-Ashi）、SMA（10/50/200）、累积 VWAP
- `--warmup` 参数支持跨日 SMA 热启动，让均线从开盘第一根 bar 就有值
- HA 和 VWAP 按交易日重置，SMA 跨日连续滚动（与 moomoo 等专业平台逻辑一致）
- 自动 RTH 过滤（09:30 ~ 16:00 ET）
- 自动 1min → 5min 聚合

**用法**：

```bash
# 推荐：自动搜索 raw/bulk/ + raw/daily/ 中的历史数据做 warmup
python build_json.py raw/daily/SPY_1min_2026-04-14.csv --auto-warmup

# 手动指定 warmup 文件
python build_json.py raw/daily/SPY_1min_2026-04-14.csv \
  --warmup raw/bulk/SPY_1min_2025-10-01_2026-04-11.csv

# 从 bulk CSV 提取指定日期（bulk 自带跨日 warmup）
python build_json.py raw/bulk/SPY_1min_2025-10-01_2026-04-11.csv --date 2026-01-07

# 无 warmup（不推荐，早盘 MA 大面积缺失）
python build_json.py raw/daily/SPY_1min_2026-04-14.csv

# 给 teaching_segments.json 补回 ts 字段
python build_json.py --fix-ts
```

`--auto-warmup` 会自动扫描 `raw/bulk/` 和 `raw/daily/` 中所有早于目标日期的 CSV，拼接后做 warmup。无需手动指定文件路径，只要历史 CSV 在目录里就能自动发现。

**为什么需要 warmup**：

| 指标 | 无 warmup 时首次有值 | 开盘段空白 |
|------|---------------------|-----------|
| MA10 | 09:40（10 min） | 影响小 |
| MA50 | 10:20（50 min） | 错过早盘信号 |
| MA200 | 12:50（200 min） | 大半天空白 |

使用 `--warmup` 后，所有 MA 从 09:30 第一根 bar 即有值。

### `aggregate_5min.py` — 辅助聚合

```bash
python aggregate_5min.py raw/daily/SPY_1min_YYYY-MM-DD.csv
```

> 注：`build_json.py` 已内置 5min 聚合，此脚本仅在需要单独生成 5min CSV 时使用。

## 命名规范

| 类型 | 格式 | 示例 |
|---|---|---|
| 单日 CSV | `SPY_1min_{YYYY-MM-DD}.csv` | `SPY_1min_2026-04-14.csv` |
| 批量 CSV | `SPY_1min_{起始}_{结束}.csv` | `SPY_1min_2025-10-01_2026-04-11.csv` |
| 产出 JSON | `SPY_{YYYY-MM-DD}.json` | `SPY_2026-04-14.json` |

> **注意**：只下载 1min 数据。5min 由脚本自动聚合。

## 数据源字段说明

### 日常下载（6 列）

| 字段 | 说明 |
|---|---|
| `datetime` | 时间戳，含时区 `2026-04-13 09:30:00-04:00` |
| `open` | 开盘价 |
| `high` | 最高价 |
| `low` | 最低价 |
| `close` | 收盘价 |
| `volume` | 成交量 |

### 历史批量下载（10 列，额外字段）

| 字段 | 说明 |
|---|---|
| `timestamp` | 时间戳（无时区，ET 本地时间） |
| `date` | 日期 |
| `time` | 时间 |
| `vwap` | 成交量加权平均价 |
| `trades` | 成交笔数 |

> 两种格式的核心 OHLCV 字段一致，`build_json.py` 自动兼容两种格式。

## 日常操作流程

1. 收盘后下载 SPY 1min 数据，放入 `raw/daily/`
2. 运行 `python build_json.py raw/daily/SPY_1min_YYYY-MM-DD.csv --auto-warmup`
3. 产出 `processed/SPY_YYYY-MM-DD.json`，可直接导入 K 线引擎
4. 通过 DevPanel 的 Data Import 拖拽导入，或通过 `engine.loadData(json)` 加载

## 归档说明

- 历史 JSON 冗余文件已归档至 `../_archive/data-json-backup/`
- bulk 目录中的历史 5min CSV 保留为参照基准，后续不再更新

---

## v0.6 新增：批量生成 + 切片（data foundation）

### 数据连续性现状（2026-04-23 Polygon 重拉后）

| 分类 | 老 bulk `SPY_1min_*.csv` | 新 `.continuous.csv` |
|---|---|---|
| `full_session_clean` | 4 天 | **130 天** |
| `full_session_gappy` | 38 天 | 0 天 |
| `short_session` | 90 天 | 2 天（半日市：感恩节次日 + 圣诞夜） |
| `invalid_session` | 0 天 | 0 天 |
| **合计** | 132 天 | 132 天（+ 6 个节假日已识别） |

重拉命令（需要 `POLYGON_API_KEY` 环境变量，免费档 5 次/分钟）：
```bash
POLYGON_API_KEY="<key>" python3 ../scripts/v0.6/tasks/task0_fetch.py \
  --start 2025-10-01 --end 2026-04-11
```
单日级断点续跑。拉完会自动 concat 到 `raw/bulk/SPY_1min_<start>_<end>.continuous.csv`。审计：
```bash
python3 ../scripts/v0.6/tasks/task0_audit.py --compare-old
```

### 批量生成历史库：`build_json.py --batch`

```bash
# 标准全量批处理（~3.5 秒 / 130 天）
python build_json.py raw/bulk/SPY_1min_2025-10-01_2026-04-11.continuous.csv --batch

# 强制覆盖已存在 JSON
python build_json.py raw/bulk/<...>.continuous.csv --batch --force

# 指定 synthetic 日路由到 processed/synthetic_fallback/
python build_json.py raw/bulk/<...>.continuous.csv --batch --synthetic-list synthetic_days.txt
```

**误触保护**：对 bulk CSV 不带 `--batch` 也不带 `--date` 会直接报错 `Bulk CSV requires --batch or --date`，防止静默走全量。

**每日 meta 新增字段**（v0.6）：
- `session_type`: `full_session_clean` / `full_session_gappy` / `short_session` / `invalid_session`
- `gap_count`: RTH 内相邻 bar 间隔 > 1min 的次数
- `warmup_complete`: `{ "1m": bool, "5m": bool }` — 该 timeframe 的全部 bar 的 m250 是否均非 null
  - 5m 的 m250 ≈ 3.5 个交易日历史，比 1m 更难完成；bulk 起始日前 3~4 天常见 `1m=true, 5m=false`

**性能**：向量化路径 `build_all_day_bars` 对全量 df 调 `build_bars` 一次再按日分桶 — 130 天 1.87s（目标 ≤60s）。

### 切片教学段：`slice_teaching_segment.py`

```bash
python slice_teaching_segment.py \
  --date 2026-01-07 \
  --start 11:35 --end 12:11 \
  --preheat 30 \
  --title "MA10 首次拒绝" \
  --out processed/teaching/seg_0107_reject.json
```

**窗口语义**：
- 1m 闭区间 `[start - preheat*1min, end]`（例 `11:35 + preheat=30` → 首根 11:05、末根 `end`）
- 5m 默认从当日 RTH 09:30 到包含 `end` 的那个 5m bucket 起点
- `preheat` 超过 `start - 09:30` 的部分自动从 `processed/` 里前一交易日 JSON 尾部补齐；优先选 `gap_count==0` 的前日
- 周末 / 假日自动跳过（`processed/` 里本来就没有那些日期）

**产出 meta 字段**（消费者审计用）：
- `initial_index_1m` / `initial_index_5m` — `t == start` 在最终切片中的下标
- `expected_bars_1m` / `actual_bars_1m` / `window_gap_count` — 预期 vs 实际 bar 数，差值 = 窗口内 gap
- `source_gap_count` / `source_synthetic` — 透传源日状态

**Escape hatches**（默认严格，需显式开启）：
- `--allow-gappy-slice`：`start` 落在缺口里时 fallback 到最近后续 bar
- `--allow-synthetic`：允许读 `processed/synthetic_fallback/` 下的源 JSON

---
