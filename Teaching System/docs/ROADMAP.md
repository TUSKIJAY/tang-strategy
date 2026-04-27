# Tang Strategy Teaching — 版本更新路线图

> 创建日期：2026-04-14
> 最后更新：2026-04-23
> 版本策略：语义化版本 `vX.Y`（X = 大版本，Y = 功能迭代）
> 管理方式：每个版本完成后打 git tag，本文件随版本推进持续更新

---

## 版本总览

| 版本 | 代号 | 状态 | 核心目标 | 文档 |
|------|------|------|----------|------|
| v0.1 | 骨架成型 | ✅ 已完成 | 单文件交付的教学回放器原型 | — |
| v0.2 | 引擎重构 | ✅ 已完成 | K 线渲染引擎剥离、重构、增强并回灌 + UI 布局优化 | `planning/v0.2-kline-refactor/` |
| v0.3 | 数据修正 | ✅ 已完成 | 修复注解/校验缺陷，达到正式基线 | `planning/v0.3-data-fix/` |
| v0.4 | case-quality | 🟡 有条件通过 | 修复案例质量、重算 VWAP、补 5m 确认并纳入新教学内容 | `planning/v0.4-case-quality/` |
| v0.5 | ui-refactor | ✅ 已完成 | Restrained Elegance 视觉重构 + 版本物理隔离（产出 v0.5.html → v0.5.1.html） | `planning/v0.5-ui-refactor/` |
| v0.6 | data-foundation | ✅ 已交付（2026-04-23） | Polygon 重拉 130 clean 日 + `--batch` 向量化 + `slice_teaching_segment.py` + packer 降级；29/29 引擎集成测试通过 | `planning/v0.6-data-foundation/` |
| v1.0 | 正式发布 | 🔮 远期 | 全量教学内容 + 离线交付 + 全平台验证 | — |

### 平行 Track

| Track | 状态 | 说明 | 文档 |
|-------|------|------|------|
| kline-engine-v2 | ✅ 已完成（2026-04-14 验收） | 独立 K 线渲染引擎（单文件 HTML，Canvas 2D），不挂版本号 | `planning/kline-engine-v2/` |

---

## v0.1 — 骨架成型 ✅

> tag: `v0.1` → commit `954bf81`

- Canvas K 线渲染 + 滑动窗口回放引擎
- 注解气泡 + 八步清单 + 1m/5m 切换
- 两 Tab 架构 + 16 章折叠导航
- 数据预处理管线 + 14 个 segments 内嵌

---

## v0.2 — 引擎重构 ✅

> tag: `v0.2` → commit `d0a3dd8`
> 完整文档: `docs/planning/v0.2-kline-refactor/`

- K 线渲染引擎剥离到独立沙盒 → 重构 `render()` 为 7 个子函数 + `RenderContext`
- 5 项交互增强：rAF 节流 / 滚轮缩放 / 拖拽平移 / OHLC 面板 / 十字线标签
- 引擎回灌主文件 + 全量回归
- UI 布局优化：宽度拓宽、侧栏统一面板、粘性导航
- 11 项 UI 审查问题全部修复

### 版本文档

| 文件 | 用途 |
|------|------|
| `kline-module-plan.md` | K 线模块剥离方案 v5（五轮 AI Review） |
| `handoff-dev.md` | 开发交接文档 |
| `handoff-review.md` | UI 审查报告（11 项全部 ✅） |
| `acceptance.md` | 验收报告（有条件通过 → 转 v0.3 修复） |
| `kline-handoff.md` | Session 交接 |
| `reviews/` | AI Review 记录 |

---

## v0.3 — 数据修正 ✅

> tag: `v0.3`（待打）
> 完整文档: `docs/planning/v0.3-data-fix/`

- 修复注解文案：距离计算区分多空 + 文案模板按 category 分支
- 修正 MA 校验逻辑：5m seed 使用对应数据源
- 章节归属决策
- 重新生成数据 + 页面回归验证

## v0.4 — case-quality 🟡

> tag: `v0.4`（待打）
> 完整文档: `docs/planning/v0.4-case-quality/`
> 当前结论：有条件通过（待补浏览器内人工回放复验）

- VWAP 改为按交易日重置的日内累积 VWAP
- 修复 `seed_04`：Reject MA10 信号K改为绿色反抽后再压回
- 替换 `seed_03`：改为更标准的 Reject MA10 教学案例
- 强化 `seed_06 / seed_08`：补入 5m 拐头确认和 VWAP 拦截逻辑
- 新增第 16 章“多空转换的多次尝试”及对应动态案例
- 新建 `dist/tang-strategy-interactive v0.4.html`
- 案例列表升级为差异化标签展示，修正文案和数据注入链路

### 版本文档

| 文件 | 用途 |
|------|------|
| `case-quality-plan.md` | v0.4 计划文档 |
| `case-quality-acceptance.md` | 验收报告（当前为有条件通过） |
| `reviews/` | AI Review 记录 |

---

## v0.5 — ui-refactor ✅

> tag: `v0.5.1`（待打）
> 完整文档: `docs/planning/v0.5-ui-refactor/`
> 交付产物: `dist/tang-strategy-interactive v0.5.html` → 后续小修产出 `v0.5.1.html`（2026-04-16）

- Restrained Elegance v2.0 设计语言：Token 化、去毛玻璃 / 大圆角 / 大阴影
- 全局卡片扁平化（圆角降至 8px，统一 1px 淡灰外边框）
- 教程单列阅读重构（`#handbookContent` 65ch 宽、统一字体栈）
- **工程化分叉**：不再原地覆盖，`v0.4.html` 无损封存 + 新建 `v0.5.html`，`src/build_html.py` 指针优先指向 v0.5
- 后续补丁 v0.5.1：收口 UI 小问题

### 版本文档

| 文件 | 用途 |
|------|------|
| `ui-refactor-plan.md` | v0.5 计划（R4 紧急回退版） |
| `acceptance-v1-001.md` | 验收报告（pass） |
| `reviews/` | AI Review 记录 |

---

## v0.6 — data-foundation ✅

> tag: `v0.6`（待打）
> 完整文档: `docs/planning/v0.6-data-foundation/`
> 当前状态：✅ 已交付（2026-04-23）

**背景**：Tang 策略审核中，新教学流程从"单独算"改为"实盘 JSON 切片"。本版本只建底座 + 切片工具，**不动策略信号检测**（等新策略落地后专项重构）。

### 交付清单

- [x] **Polygon 历史重拉**（D8=A+）：2025-10-01 ~ 2026-04-11，耗时 32 分钟，0 失败 → `raw/bulk/SPY_1min_<start>_<end>.continuous.csv`
- [x] **数据基座升级**：老 bulk 4 clean/38 gappy/90 short → 新 continuous **130 clean / 0 gappy / 2 短日（半日市）**
- [x] **`build_json.py --batch`**：向量化 132 天 1.87s（<< 60s 目标）；加 `session_type` / `gap_count` / `warmup_complete.{1m,5m}` 三个 meta 字段；误触保护（bulk 不带 `--batch`/`--date` 报错）
- [x] **`slice_teaching_segment.py`**：切片工具，支持跨日 / 跨周末 preheat、gap 感知（`--allow-gappy-slice`）、synthetic 隔离（`--allow-synthetic`）
- [x] **`prepare_kline_engine_v2_data.py` 降级**：删除 `teaching_segments.json` 依赖，改为读 slicer 产出 + build_json 日 JSON；seed 选 2026-01-07 11:35-12:11 preheat 30（`full_session_clean` + `warmup_complete.{1m,5m}=true`）
- [x] **引擎 29 项集成测试全过**；seed 模式渲染 8 条 MA + VWAP 全有值（修复老 fixture 中 m5/m20/m30/m60/m120 全 null 的 bug）

### 版本文档

| 文件 | 用途 |
|------|------|
| `data-foundation-plan.md` | v0.6 计划（R7） |
| `reviews/` | AI Review 记录（agent01 + agent02 各 5 轮） |
| `../../scripts/v0.6/` | 执行 harness（HANDOFF / acceptance / per-task Python） |

---

## v0.7+ — 筛选器（远期）📋

> 目标：基于 Tang 策略八步清单的形态扫描器，输出"哪些日子的哪些时间窗符合标准"，配合 v0.6 切片工具批量落盘
> 前置：Tang 策略审核完成

---

## 历史 v0.5 候选方向（未进入本轮版本）

以下方向在 v0.5 立项时曾作为候选，未进入本轮执行，留作后续版本参考：

| 方向 | 来源 | 描述 |
|------|------|------|
| 页面级复验 | v0.4 验收条件 | 浏览器内逐案例回放、注解气泡、1m/5m 切换、缩放拖拽复验 |
| 更高周期可视化 | v0.4 新教学内容 | 给 15m 背景补前端可视化，而不是只停留在文案层 |
| 教学内容扩充 | 既有待办 | 补充 ch08~12 案例、修复 seed_12/13 日期 |
| 注解文案精修 | 既有技术债 | 自动生成文案替换为更明确的手写教学引导 |
| 移动端 / 触控 | 未验证项 | 375px 真机 + 触控手势回归 |
| 离线交付 | 长尾问题 | Google Fonts 依赖、favicon、纯离线分发 |

---

## 平行 Track: kline-engine-v2 ✅

> 验收日期：2026-04-14
> 完整文档：`docs/planning/kline-engine-v2/`
> 产出：`dist/kline-engine/kline-engine-v2.html`（单文件，含完整 JS/CSS/demo）

独立 K 线渲染引擎，对标 moomoo 视觉。核心模块：EventBus / DataManager / ViewportManager / Renderer / InteractionManager / PlaybackManager / AnnotationManager。

公共 API：`loadData / setTimeframe / scrollTo / play / pause / setSpeed / on / off / getCurrentIndex / destroy`。事件：`data:loaded / viewport:changed / playback:tick / playback:state / annotation:click / bar:click`。

详见 `dist/kline-engine/INTEGRATION.md`（对接说明）、`planning/kline-engine-v2/INTERNALS.md`（内部结构）。

---

## v1.0 — 正式发布 🔮

> 前置条件：所有 v0.x 迭代完成

### 里程碑标准

- [ ] 16 章教学内容全覆盖
- [ ] 全量注解为手写教学引导
- [ ] 375px ~ 2560px 全断点通过
- [ ] Chrome / Firefox / Safari / Edge 四浏览器通过
- [ ] 完全离线可用（零外部依赖）
- [ ] 用户测试反馈收集 + 迭代

### 可选增强（v1.x）

- 练习模式：隐藏注解，让用户自行判断并评分
- 多策略支持：不仅限于 Tang 策略
- 数据导入：支持用户上传自己的 K 线数据
- PWA 封装：可安装到桌面/手机主屏

---

## 版本管理约定

### 文档组织规则

每个版本的文档统一存放在 `docs/planning/v<X.Y>-<代号>/` 下：

```
docs/
├── ROADMAP.md                           # 本文件（唯一活文档）
├── real_chart_analysis.md               # 16 图教学分析（长期参考）
└── planning/                            # 按版本组织
    ├── v0.2-kline-refactor/             # ✅ 已完成
    │   ├── kline-module-plan.md
    │   ├── handoff-dev.md
    │   ├── handoff-review.md
    │   ├── acceptance.md
    │   ├── kline-handoff.md
    │   └── reviews/
    ├── v0.3-data-fix/                   # ✅ 已完成
    │   └── data-fix-plan.md
    ├── v0.4-case-quality/               # 🟡 有条件通过
    │   ├── case-quality-plan.md
    │   ├── case-quality-acceptance.md
    │   └── reviews/
    ├── v0.5-ui-refactor/                # ✅ 已完成
    │   ├── ui-refactor-plan.md
    │   ├── acceptance-v1-001.md
    │   └── reviews/
    ├── v0.6-data-foundation/            # 🟡 进行中
    │   ├── data-foundation-plan.md
    │   └── reviews/
    ├── kline-engine-v2/                 # ✅ 平行 track（独立引擎）
    │   ├── kline-engine-v2-plan.md
    │   ├── ACCEPTANCE.md
    │   ├── INTERNALS.md
    │   ├── OPTIMIZATION.md
    │   ├── handoffs/
    │   ├── assets/
    │   └── reviews/
    └── daily-review/                    # 📋 Daily review 产品规划（非教程版本线）
        └── daily-review-plan.md
```

**规则**：
- docs 根目录只放**当前活跃的全局文档**（ROADMAP、长期参考资料）
- 版本专属文档（计划、交接、验收、review）全部放入版本子目录
- 版本完成后，文档原地保留（不再移动），靠 git tag 标记节点

### Git Tag 规则

```bash
git tag -a v0.4 -m "v0.4: <代号> — <一句话描述>"
```

### Commit Message 前缀

```
feat(v0.4): <描述>
fix(v0.4): <描述>
docs(v0.4): <描述>
```

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-04-14 | 创建路线图；v0.3 标记完成；整理 docs 目录结构（handoff/acceptance/review 归入版本子目录） |
| 2026-04-14 | 更新 v0.4 为 `case-quality`，补充验收状态、文档索引和 v0.5 候选方向 |
| 2026-04-23 | v0.5 ui-refactor 标记完成（v0.5.1 已交付）；新增 v0.6 data-foundation（进行中）；新增 v0.7+ 筛选器远期规划；新增 kline-engine-v2 与 daily-review 两条平行 track 入口；更新 docs 目录树 |
