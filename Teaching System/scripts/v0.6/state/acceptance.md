# v0.6 Acceptance 累积报告

> 每个 task 跑完自动 append 一段。手动也可补记。
> 配套：本目录 HANDOFF.md（接手入口）、../README.md、../../docs/planning/v0.6-data-foundation/data-foundation-plan.md

---

## 模板（每段格式）

```
### Task X — YYYY-MM-DD HH:MM

**命令**：./run.sh taskX [args]
**耗时**：N 分 M 秒
**产出**：
  - <文件路径> (说明)
**关键 metrics**：
  - <指标名>: <值>
**验收逐条**：
  - [✓/✗] <验收标准 1>
  - [✓/✗] <验收标准 2>
**给下一个 Claude 的提示**：
  - <这一步发现 X，下一步注意 Y>
**问题/BLOCKED（如有）**：
  - <说明>
```

---

### Task 0 — 2026-04-23 19:16 ~ 19:48（fetch 32min + concat + audit）

**命令**：
```bash
POLYGON_API_KEY="<env>" python3 "scripts/v0.6/tasks/task0_fetch.py" \
  --start 2025-10-01 --end 2026-04-11
python3 "scripts/v0.6/tasks/task0_audit.py" --compare-old
```
**耗时**：Polygon 拉 1913 s = 31m53s；concat < 1s；audit < 1s

**产出**：
  - `data/raw/bulk/SPY_1min_2025-10-01_2026-04-11.continuous.csv`（119050 行，10.3 MB；老 `.csv` 保留）
  - `scripts/v0.6/state/task0_daily/SPY_YYYY-MM-DD.csv`（132 个 per-day CSV，断点续跑状态）
  - `scripts/v0.6/state/task0_progress.json`（done/holidays/failed/short 状态文件）

**关键 metrics**：
  - done=132 holidays=6 failed=0 short=2
  - 节假日识别：2025-11-27 Thanksgiving / 2025-12-25 Christmas / 2026-01-01 New Year / 2026-01-19 MLK / 2026-02-16 Presidents / 2026-04-03 Good Friday（全部对）
  - 短日：2025-11-28（感恩节次日 ½市）/ 2025-12-24（圣诞夜 ½市）— 半日市真实数据，非异常

**审计对比**：

| 分类 | 老 `SPY_1min_*.csv` | 新 `.continuous.csv` |
|---|---|---|
| `full_session_clean` | **4** | **130** |
| `full_session_gappy` | 38 | 0 |
| `short_session` | 90 | 2 |
| `invalid_session` | 0 | 0 |
| 总 RTH bars | 48586 | 51122 |
| 2026-01-07 11:05-12:11 seed 窗口 | 50 bars ❌ | **67 bars ✅** |

**验收逐条**（plan D8=A+ 路径）：
  - [✓] 新 CSV ≥ 120 天 `full_session_clean`（实得 130）
  - [✓] 2026-01-07 seed 窗口实际 67 根（plan 明确不变量）
  - [✓] Polygon key 从 `os.environ["POLYGON_API_KEY"]` 读，脚本不打印 key，本文件不粘含 key URL
  - [✓] 单日级断点续跑：dry-run 2026-04-10 已 done；全量 fetch 自动跳过；可用 Ctrl+C + 重跑验证
  - [-] synthetic_fallback 路径：Polygon 0 失败，本轮未触发（`--synthetic-list` 路由已在 Task 1 实现可用）

**给下一个 Claude 的提示**：
  - 老 bulk CSV 没删，留作对比。如需清理，等 v0.7+ 筛选器上线且确认新数据稳定后再删
  - 短日 2 个保留在 `processed/`（`session_type=short_session`），v0.7+ 扫描器可自己决定是否纳入候选池
  - 窄范围（2025-10-01 起）决定了 bulk 前 3~4 天 `warmup_complete.5m=false`（5m 的 m250 ≈ 3.5 交易日） — 如需更完整 5m warmup，后续补 2025 Q3 数据

---

### Task 1 — 2026-04-23 19:3X（实现 + 等价性验证 + 真跑）

**命令**：手动；走 `data/build_json.py`
**产出**：
  - `data/build_json.py` 重构，新增 `cmd_batch()` + `classify_session` + `compute_warmup_complete` + `build_all_day_bars` + `_build_meta`
  - 参数新增：`--batch` / `--force` / `--synthetic-list`
  - 入口误触保护：bulk CSV 不带 `--batch` 也不带 `--date` → 报错 `Bulk CSV requires --batch or --date`
**关键 metrics**：
  - 向量化批量构建 132 天耗时 **1.87 s**（目标 ≤ 60 s） — 快 30 倍
  - CSV load: 0.48 s
**验收逐条**：
  - [✓] `python build_json.py raw/bulk/...csv`（不带 --date / --batch）→ 报错提示两个选项
  - [✓] `--batch` 与 `--date` 互斥 → 报错
  - [✓] cmd_build 单日路径规范化 diff：`SPY_2026-04-13.json` force 重跑后仅 `generated_at / session_type / gap_count / warmup_complete` 差异，其余 meta 和 bars 完全一致
  - [✓] 向量化路径等价：`build_all_day_bars(bulk_df)` 对 `2026-03-06` 产出的 bars_1m/bars_5m 与原 `processed/SPY_2026-03-06.json` **字节级一致**
  - [✓] 新 meta 字段对 2026-04-13（clean 日）输出：`session_type=full_session_clean`、`gap_count=0`、`warmup_complete={1m:true,5m:true}`
  - [✓] `classify_session` 对 2025-10-01/02/03/06/07（old bulk 的 short 日）输出 `short_session` + 正确 gap_count（20/30/28/21/35）
  - [✓] batch 真跑新 `continuous.csv`：132 日耗时 **3.4 s**；分类汇总 130 clean / 0 gappy / 2 short / 0 invalid（完全对齐 audit 结果）
  - [-] synthetic_fallback 路由跑通 → **本轮未触发**（Polygon 0 failed，无 synthetic 日）；参数已接线，未来需要时生成 `synthetic.txt` 丢给 `--synthetic-list` 即可

**给下一个 Claude 的提示**：
  - cmd_batch 的 synthetic 路由已接线（`--synthetic-list`），但目前空闲。Task 0 fetch 跑完后若 failed 列表非空，生成 `synthetic.txt` 喂给 `--synthetic-list` 即可把那些日子落到 `processed/synthetic_fallback/`
  - `cmd_build` 老路径内部也加了 `_build_meta`，同时得到新字段 — daily CSV + `--auto-warmup` 的旧流程**输出体积变大但语义不变**，前端若强校验字段白名单需更新

---

### Task 2 — 2026-04-23 19:5X（实现 + 冒烟测试）

**命令**：手动；走 `data/slice_teaching_segment.py`
**产出**：
  - 新建 `data/slice_teaching_segment.py`（380 行）
**关键 metrics**：
  - 同日切片：<50ms / 次
**验收逐条**（plan Task 2 全部验收项的对照）：
  - [✓] 同日切片 2026-04-13 `--start 11:35 --end 12:11 --preheat 30` → 1m **67/67 bars**，5m **33 bars**，`initial_index_1m=30`，`initial_index_5m=25` — 完全符合 plan 不变量（虽然不是 2026-01-07，但结构等价；01-07 等 Task 0 数据到位后复核）
  - [✓] 跨日 preheat：2026-04-14 `--start 09:45 --end 10:30 --preheat 60` → 106 bars（60 preheat = 45 来自 04-13 15:15-15:59 + 15 来自 04-14 09:30-09:44），末根 10:30 ✓，接缝 04-13 15:59 → 04-14 09:30 无 16:00 无空时间戳 ✓
  - [✓] 跨周末：2026-04-20（周一）`--start 09:45 --end 10:30 --preheat 60` → preheat 来自 04-17（周五），结构与跨日 case 一致
  - [✓] 缺当日 JSON：`--date 2025-05-01` → 报错 `processed/SPY_2025-05-01.json not found — run build_json.py first`
  - [-] 缺前日 JSON 报错 → 未测（需要构造只留当日 JSON 的 fixture；行为与缺当日同路径，逻辑已实现）
  - [✓] **Gap 警告 / gappy index fallback**（self-audit 补测，2026-04-23 20:10）：
    - short_session 末端越界：`--date 2025-11-28 --start 14:00 --end 14:30`（半日市 13:00 收盘）→ 报错 `start time 14:00 is missing from source (in gap)` ✓
    - 手构 gappy fixture（从 2025-11-28 挖掉 12:00-12:10，伪装 gap_count=11）：
      - 严格模式 start 落 gap → 报错 + stderr `[WARN] source 2099-01-01 has 11 total gaps` ✓
      - `--allow-gappy-slice` → fallback 到 12:11，`initial_index_1m=20`、`expected=46 actual=40 window_gap=6 source_gap=11` 精确计算 ✓
  - [-] Synthetic 隔离 → 未触发（Polygon 0 failed，`processed/synthetic_fallback/` 为空）；代码路径：默认拒读 fallback 目录，加 `--allow-synthetic` 切到 — 逻辑已实现未跑
  - [✓] 浏览器渲染（Task 3 一并验）：seed fixture 67/33 bars 正常渲染，1m↔5m 切换、tooltip、8 条 MA + VWAP 全有值 — 详 Task 3 段

**给下一个 Claude 的提示**：
  - 产出 JSON 结构按 plan R5 字段表对齐：`initial_timeframe/initial_index_1m/initial_index_5m/expected_bars_1m/actual_bars_1m/window_gap_count/source_gap_count/source_synthetic/window`，annotations 留空数组
  - `_find_prev_day_json` 优先 gap_count==0；没有干净前日时 fallback 到最近（warning 到 stderr）
  - 切片逻辑 CLI 严格用 `--allow-gappy-slice` / `--allow-synthetic` 两个 escape hatch，默认报错；与 plan R5 修正一致

---



### Task 3 — 2026-04-23 20:00（demo seed 选日 + packer 降级 + HTML 冒烟）

**命令**：
```bash
# 1) 切 demo seed
python3 "data/slice_teaching_segment.py" \
  --date 2026-01-07 --start 11:35 --end 12:11 --preheat 30 \
  --title "v2 引擎 demo seed — 2026-01-07 Support MA10" \
  --out "data/processed/kline-engine-v2-seed.json"

# 2) 跑 packer 注入 HTML
python3 "src/prepare_kline_engine_v2_data.py"

# 3) 浏览器冒烟：打开 kline-engine-v2.html 跑 runIntegrationTest()
```

**Seed 选用记录**（plan R5 九字段格式）：
```
date:                  2026-01-07
start:                 11:35
end:                   12:11
preheat:               30
session_type:          full_session_clean
warmup_complete_1m:    true
warmup_complete_5m:    true
source_gap_count:      0
window_gap_count:      0
选用理由:              plan 明确的不变量锚点（67 bars / 33 bars / initial_index_1m=30 / initial_index_5m=25），
                      新 Polygon 数据下所有条件全部满足；Support MA10 形态教学性保留；与历史 seed_01 对齐便于对比。
                      未来 v0.7+ 扫描器选出更标准片段时，只需 re-run slicer + packer 即可替换。
```

**验收逐条**（plan Task 3 行为型）：
  - [✓] 脚本不再 import / 读 `teaching_segments.json`（grep 返回 0 匹配）
  - [✓] `kline-engine-v2-seed.json.meta.source == "slice_teaching_segment.py"`
  - [✓] `meta.date == "2026-01-07"` 在 `processed/` 里存在
  - [✓] seed 模式：67 根 1m bar、33 根 5m bar、`initial_index_1m=30`（=11:35）、`initial_index_5m=25`（=11:35 桶）
  - [✓] K 线渲染 / tooltip / OHLC + **8 条 MA + VWAP 全有值**（对比老 fixture m5/m20/m30/m60/m120 null bug，意外修复）
  - [✓] 1m ↔ 5m 切换：`engine.setTimeframe('5m')` → tf=5m idx=25 bars=33；切回 1m → idx=30 不丢位置
  - [✓] fullDay 模式：`SPY_2026-04-13.json` 390 bars，meta 携带 `session_type=full_session_clean` + `warmup_complete={1m:true,5m:true}`，无回归
  - [✓] `runIntegrationTest()` **29/29 PASS，0 FAIL**
  - [-] 缩放 / 拖动 / preheat 区域拖动可见 → 未做自动化；视觉确认 preheat 段（11:05-11:34，30 根）左侧 visually 可见；完整拖动交互留人工抽验

**关键 metrics**：
  - Packer 代码行数 189 → ~110（删 `normalize_annotations/adapt_seed_bars/find_initial_index_5m`）
  - HTML 注入的 fixture size：seed 67+33 bars + fullDay 390+78 bars（比老 fixture 更完整的 MA 覆盖）
  - 引擎集成测试：29 项全 PASS，含 data:loaded / viewport / playback / annotation / destroy 五大类

**给下一个 Claude 的提示**：
  - Task 3 没有"保留旧 annotations"的要求（plan R4 删除）。现 seed fixture 的 annotations 数组为空 — 人工可按需在 `slice_teaching_segment.py` 产出后手动补 annotation JSON，或等 v0.7+ 筛选器批量自动标注
  - 如果切到别的 demo 日，必须同时满足 `full_session_clean` + `warmup_complete.1m=true` + `warmup_complete.5m=true`；前 3~4 天（10 月初）`warmup_complete.5m=false`，不合资格；验收格式按本文件九字段记录

---

### Self-audit 补齐 — 2026-04-23 20:10

用户问"全部都做完了？"触发的补刀：

1. **2026-04-14 ~ 2026-04-22 共 7 个 daily JSON 缺新 meta 字段** — 这些文件是 Task 1 refactor 之前产出的，未经 `--batch` 覆盖（不在 bulk 范围）。逐个用 `build_json.py --warmup raw/bulk/SPY_1min_*.continuous.csv` 重建，全部 `session=full_session_clean, warmup={1m:true, 5m:true}`，新字段全部落地 ✓
2. **Task 2 Gappy 场景测试**（见上面 Task 2 段补充）— 4 个 gappy 相关 case 全过

---

### v0.6 整体交付总结 — 2026-04-23 20:05

| Task | 状态 | 证据 |
|---|---|---|
| Task 0 fetch + audit | ✅ | 0 failed / 130 clean / 6 holiday 对；seed 窗口 67 bars ✓ |
| Task 1 `--batch` | ✅ | 132 天 3.4s；新 meta 字段全对；规范化 diff 单日 vs 批量 = 0 |
| Task 2 slicer | ✅ | 同日 / 跨日 / 跨周末 / 缺源报错 4 个冒烟全过 |
| Task 3 packer 降级 | ✅ | 9 字段选用记录；29/29 集成测试；HTML 渲染正常 |
| Task 4 文档 | ✅ | `data/README.md` 加两节；`CLAUDE.md` 关键文件表 + 下载命令表；`ROADMAP.md` v0.6 标 ✅ |

**风险归档**：
- ✅ bulk CSV 数据连续性问题（已发生高概率）→ Polygon 重拉完全解决
- ✅ MA warmup 起始日不完整（已发生高概率）→ `warmup_complete.{1m,5m}` 字段如实登记；demo 日选取强制 1m+5m 全 true
- ✅ Vectorized 重构与原单日逻辑不一致（中）→ `SPY_2026-03-06` 字节级等价验证通过
- ✅ 跨日 preheat 时区/交易日历边界（中）→ 4 个边界 case 全过，不引入外部日历库
- ✅ Seed fixture 行为退化（低）→ 29 项集成测试 0 失败
- ✅ Polygon 限速 / API 失败（中）→ 32 min 跑完，0 失败，未触发 fallback
- ✅ Batch 性能（低）→ 1.87s / 132 天（目标 60s，快 30x）

**未触发但保留的能力**（留给未来）：
- `build_json.py --synthetic-list` + `processed/synthetic_fallback/` 路由（本轮 0 synthetic）
- `slice_teaching_segment.py --allow-gappy-slice` + `--allow-synthetic`（本轮无触发场景）
- Q3 2025 数据扩展（窄范围不缺 1m warmup，但 5m warmup 前 3~4 日稍弱；后续如需更完整可补拉）
