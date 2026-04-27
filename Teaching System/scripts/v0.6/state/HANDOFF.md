# v0.6 执行接手文档

> **如果你是接手的 Claude，从这里开始读。**

## 元信息

- **最后更新**：2026-04-23 20:05（v0.6 全部任务已交付；29/29 集成测试 PASS；等 commit）
- **当前阶段**：✅ **v0.6 完成** — Task 0~4 验收逐条通过；Polygon 0 failed 不需 synthetic 路径；详情见 `acceptance.md`
- **D8 决策**：✅ A+（Polygon 重拉 + gap-fill fallback 分层隔离） — 实际 0 failed，fallback 路径未触发（代码已接线）
- **拉取范围**：✅ 窄（2025-10-01 ~ 2026-04-11） — 132 clean+short 日 + 6 节假日识别
- **Plan 版本**：R7（已 5 轮 review，全部 approve）

---

## 如果你是接手的 Claude，按此顺序读

1. **本文件** — 当前阶段、待办、上下文速览
2. **Plan 全文**：`docs/planning/v0.6-data-foundation/data-foundation-plan.md`
3. **Reviews（可选）**：`docs/planning/v0.6-data-foundation/reviews/`（5 份，理解决策演化用）
4. **本目录 README**：`scripts/v0.6/README.md`（harness 用法）
5. 跑 `./run.sh status` 验证 harness 骨架未腐烂

---

## 待用户确认（动手前必须问）

- [ ] **`POLYGON_API_KEY` 是否已 export**？最近一次检查（2026-04-23）：未设置
  - 若未设置：让用户 `export POLYGON_API_KEY="<key>"`
  - key 来源：`CLAUDE.md` 第 ~76 行明文（用户已确认 R5 时不轮换）
  - 严格按 plan 第 0a 节凭据规范：脚本只读 env var，不打印 key，不在 acceptance 粘含 key 命令
- [x] **拉取范围**：✅ 窄（2025-10-01 ~ 2026-04-11） — 2026-04-23 选定；后续如需补 Q3 再做

---

## 已完成清单（v0.6 交付全部 ✅）

- [x] Plan R1→R7 共 7 版迭代，5 轮 review 全部 approve
- [x] D8=A+ 拍板（2026-04-23）
- [x] Harness 骨架已建
- [x] **Task 0** — Polygon fetch + audit
  - fetch 132 done / 6 holidays / 0 failed，32 分钟；产出 `data/raw/bulk/SPY_1min_2025-10-01_2026-04-11.continuous.csv`（老 `.csv` 保留）
  - audit：新 CSV 130 clean / 2 short / 0 gappy；2026-01-07 seed 窗口 67 bars ✓；老 bulk 的 4/38/90 分类数对比登记
  - 半日市：2025-11-28 感恩节次日、2025-12-24 圣诞夜（均为合法 short_session）
- [x] **Task 1** — `build_json.py` 重构
  - 新 CLI：`--batch` / `--force` / `--synthetic-list`；误触保护（bulk 不带 `--batch`/`--date` 报错）
  - 向量化：`build_all_day_bars` 对全量 df 调 `build_bars` 一次，按日分桶；132 天 1.87s（<< 60s 目标），真跑 3.4s
  - 新 meta 字段：`session_type` / `gap_count` / `warmup_complete.{1m,5m}`（`_build_meta` 两条路径共用）
  - 等价性：`SPY_2026-03-06` 向量化 vs 单日路径字节级一致；规范化 diff vs 原 `SPY_2026-04-13.json` 除 generated_at + 3 新字段外完全一致
- [x] **Task 2** — `slice_teaching_segment.py` 新建
  - 4 冒烟场景 全过：同日 / 跨日 / 跨周末 / 缺源报错
  - 不变量：2026-04-13 11:35-12:11 preheat=30 → 1m 67/67 + 5m 33，initial_index 30/25
  - Escape hatches：`--allow-gappy-slice`、`--allow-synthetic`（默认严格报错）
  - meta 全字段对齐 plan R5：`initial_timeframe/initial_index_{1m,5m}/expected_bars_1m/actual_bars_1m/window_gap_count/source_gap_count/source_synthetic/window`
- [x] **Task 3** — `prepare_kline_engine_v2_data.py` 降级
  - 删除 `teaching_segments.json` 依赖（grep = 0）、删除 3 个转换函数
  - seed 改为读 slicer 产出；fullDay 照旧；注入 HTML inline fixture
  - demo 选日：**2026-01-07 11:35-12:11 preheat=30**（九字段记录见 `acceptance.md`）
  - 浏览器冒烟：`runIntegrationTest()` **29/29 PASS**；seed 1m/5m 切换正确；fullDay 无回归
  - 额外收益：新 fixture 8 条 MA + VWAP 全有值（修复老 fixture 中 m5/m20/m30/m60/m120 null bug）
- [x] **Task 4** — 文档同步
  - `data/README.md` 加"v0.6 新增：批量生成 + 切片"大节（含审计对比表 / --batch / slicer 用法 / meta 新字段说明）
  - `CLAUDE.md` 关键文件表加 `slice_teaching_segment.py` 和 `scripts/v0.6/` 行；"数据下载后必须执行"节加 `--batch` 和 slicer 命令；增加 Polygon 续拉指引
  - `docs/ROADMAP.md` v0.6 标 ✅ 已交付，展开交付清单

---

## 下一步（给用户）

v0.6 代码 + 数据 + 文档全部到位。剩下的只有 **git commit**（未做；此 Claude 遵守"不主动 commit"的规则）。

建议 commit 拆分：
```bash
# 1) 数据基座（大）
git add "data/raw/bulk/SPY_1min_2025-10-01_2026-04-11.continuous.csv" \
        "data/processed/SPY_*.json" \
        "data/processed/kline-engine-v2-seed.json" \
        "data/processed/kline-engine-v2-full-day.json"
git commit -m "data(v0.6): Polygon 重拉 + 130 clean 日批量 processed JSON"

# 2) 代码（核心）
git add "data/build_json.py" \
        "data/slice_teaching_segment.py" \
        "src/prepare_kline_engine_v2_data.py" \
        "scripts/v0.6/**"
git commit -m "feat(v0.6): --batch + slicer + packer 降级"

# 3) 文档
git add "data/README.md" \
        "docs/ROADMAP.md" \
        "CLAUDE.md"
git commit -m "docs(v0.6): 同步批量生成/切片/Polygon 续拉流程"

# 4) HTML fixture 注入
git add "dist/kline-engine/kline-engine-v2.html"
git commit -m "chore(v0.6): 注入新 demo fixture（2026-01-07 Support MA10 + 2026-04-13 fullDay）"
```

如需继续推进 v0.7+，plan 里 Task 3/Task 4 已全部完成，直接进 v0.7 形态扫描器规划即可（利用本轮 130 个 clean 日 JSON）。

## 后续可选增强（非 plan 必需）

- 补 2025 Q3 Polygon 数据 → 消除 bulk 前 3~4 天 `warmup_complete.5m=false`
- Slicer 的 gappy / synthetic 场景冒烟测试（本轮数据太干净没机会触发，后续造假构造 gappy fixture 再测）
- `prepare_data.py` 退役（plan 明确放到 v0.7 随 Tang 策略新版本一起重写，本轮未动）

---

## 上下文速览（5 句话给接手 Claude）

1. **目标**：建 v0.7+ 形态扫描器的样本库底座，**不是修复任何具体的旧 seed 片段**
2. **数据现状**：bulk CSV 132 天里只有 4 天连续完整，所以要 Polygon 重拉
3. **A+ 分层**：成功重拉日落 `processed/`（干净库，扫描器默认池）；失败日 gap-fill 落 `processed/synthetic_fallback/`（隔离，需 `--allow-synthetic` 才切到）
4. **现有 seed_01 是占位**：v2 引擎 demo fixture，**不必复刻** — Task 3 由起草者从 `processed/` 中挑符合标准的干净日重新切（详见 plan R4 用户澄清）
5. **凭据**：暂不轮换 Polygon key，但所有新代码都用 env var，不要 hardcode

---

## 待协调/暂缓事项

（暂无 BLOCKED 项；如失败/卡住请在此 append）

---

## ⚠️ 重要：每完成一个子步骤，更新本文件

- 修改"当前阶段"、"已完成清单"
- 给"下一步具体动作"写出可直接执行的命令
- 待用户确认事项及时勾掉或新增
- 失败/BLOCKED 项写"待协调/暂缓事项"

更新粒度：每个 task 完成时 + task 内每 ~10% 进度时（保证下次接手最多落后 ~5min 工作）。
