# Teaching System — Tang 策略教学系统

学习者侧的交互式 K 线回放教学器。

## 入口

| 用法 | 文件 | 启动方式 |
|---|---|---|
| **双击即用**（推荐） | `dist/Tang 策略教学系统-standalone.html` | 双击打开。907 KB 单文件，所有数据/JSX/引擎已 inline。首次需联网（Tailwind / React / Babel CDN），之后浏览器缓存可离线使用。 |
| **开发模式** | `dist/Tang 策略教学系统.html` | 必须通过本地 HTTP server 打开（如 `python -m http.server`），双击会因 file:// CORS 失败。 |

## 目录结构

```
Teaching System/
├── dist/                                 # 产品入口
│   ├── Tang 策略教学系统.html           # 多文件版（开发用）
│   ├── Tang 策略教学系统-standalone.html # 单文件版（产品交付）
│   ├── shared.jsx                       # 公共组件 + KlineEngineAdapter + KlineView
│   ├── pages-1.jsx                      # Hub / Module / Case / Fragment 页面
│   ├── pages-2.jsx                      # Training / Mistakes / Playbook / Archives 页面
│   └── kline-engine/                    # K 线引擎（Canvas 2D）
├── cases/index.json                     # 6 个教学案例索引
├── rules/compiled/index.json            # 7 条规则编译产物
├── training/checkpoints.json            # 训练步骤 / 八步清单数据
├── data/
│   ├── processed/teaching_segments.json # 教学切片（K 线 + 标注 + checkpoints inline）
│   ├── processed/SPY_*.json             # 日级权威 JSON（用于切新教学 segment）
│   ├── raw/                             # 原始 CSV（不入 git）
│   ├── build_json.py                    # CSV → JSON 数据管道
│   └── slice_teaching_segment.py        # 从日级 JSON 切教学窗口
├── src/                                 # 策略源码 + fixture 打包器
├── scripts/
│   ├── build_standalone.py              # 单文件构建器
│   └── v0.6/                            # Polygon 续拉 + 批量 harness
└── docs/                                # 规划 / 路线图 / 教学笔记
```

## 重新构建 standalone 单文件

每次改完 jsx 或核心 JSON（cases / rules / training / teaching_segments）后，在仓库根目录下跑一次：

```bash
python scripts/build_standalone.py
```

约 1 秒完成，输出体积 + 各 inline source 大小一览。

## shared.jsx 双模式数据加载

`useAppData` 优先从 `<script type="application/json" id="inline-data-*">` 标签读 inline 数据（standalone 模式），找不到时 fallback 到 `fetch()`（dev 模式）。同一份 jsx 两种模式都 work，无需维护两份。

## License

本仓库采用双许可证：

- 代码（包括 `src/`、`scripts/`、`dist/` 及构建自动化文件）：MIT License。
- 文档、教学材料、策略笔记和 `reference/` 资料：CC BY-NC 4.0，除非文件内另有说明。

本项目仅用于教育和研究，不构成金融建议、投资建议或任何买卖证券的建议。
