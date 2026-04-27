# K 线引擎 v2 — 优化清单

> 关联文件：`dist/kline-engine/kline-engine-v2.html`
> DevPanel：`dist/kline-engine/kline-devpanel.js`
> 参考：`INTERNALS.md`（行号索引，优化后行号已变动）

---

## 设计目标

引擎定位为**基础设施**——只保留核心能力（K 线渲染、视窗管理、播放控制、标注系统、数据加载），剥离 demo/教学性质的 UI 装饰。后续所有功能（教程、复盘、信号检测等）以此为基座扩展。

**原则**：引擎瘦、接口稳、扩展在外部。

---

## 已完成

### OPT-001：移除底部进度条 + 状态栏 -- DONE

移除 scrubber DOM / CSS / `_bindProgressBar()` / `updateScrubber()` / `progressDragState` + 底部 status 面板。鼠标拖拽平移已覆盖导航需求。

### OPT-002：移除右上角快捷键提示 -- DONE

移除 message 面板（快捷键提示 + 播放状态提示）。快捷键提示迁移至 DevPanel。

### OPT-003：开发者工具面板（DevPanel） -- DONE

独立文件 `kline-devpanel.js`，可拆卸模块。功能：
- Engine State：实时显示 tf / index / bars / zoom / mode / playback
- Demo Fixtures：自动检测 `window.__klineEngineV2Fixtures`，按钮切换
- Data Import：拖拽/点击选择 JSON 文件导入，带格式校验
- Keyboard Shortcuts：快捷键速查

隔离方式：demo 页 `<script src="kline-devpanel.js">` 引入，产品页不引入即完全隔离。

### OPT-004：移除引擎内 fixture 切换 -- DONE

从引擎工具栏移除 Seed / Full Day 按钮，移除 `currentFixtureName` state，meta 显示去掉 fixture 引用。Fixture 切换功能迁移至 DevPanel。

---

## 当前引擎工具栏

瘦身后只剩纯引擎控件：

```
[ 1m ] [ 5m ] [ << ] [ > ] [ >> ] [ 0.5x ] [ 1x ] [ 2x ] [ 4x ] [ - Zoom ] [ + Zoom ] [ Follow ]
```

---

*继续添加新条目...*
