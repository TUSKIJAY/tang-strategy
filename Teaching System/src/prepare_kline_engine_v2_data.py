#!/usr/bin/env python3
"""
prepare_kline_engine_v2_data.py — v2 引擎 demo fixture 打包器

职责（v0.6 降级后）：
- **读** `data/processed/kline-engine-v2-seed.json`（由 `slice_teaching_segment.py` 产出）
- **读** `data/processed/kline-engine-v2-full-day.json` 的源（`data/processed/SPY_*.json` 某日）
- 更新两份 fixture 的 `meta.generated_at`
- 注入到 `dist/kline-engine/kline-engine-v2.html` 的 inline fixture 标记中

本脚本**不做数据转换**（HA/MA/VWAP/annotations 全部上游已处理好）。

前置步骤：
  1. 批量权威 JSON：
     cd "data"
     python build_json.py raw/bulk/SPY_1min_2025-10-01_2026-04-11.continuous.csv --batch

  2. 挑选 demo 日（必须同时满足）：
     - meta.session_type == "full_session_clean"
     - meta.warmup_complete.1m == true 且 meta.warmup_complete.5m == true
     - 形态视觉有教学性（例：MA10 拒绝/支撑、HA 颜色翻转）

  3. 切片：
     python slice_teaching_segment.py \
       --date <YYYY-MM-DD> --start <HH:MM> --end <HH:MM> --preheat 30 \
       --title "v2 引擎 demo seed" \
       --out data/processed/kline-engine-v2-seed.json

  4. 跑本脚本注入 HTML。
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
DIST_DIR = PROJECT_DIR / "dist"

SEED_FIXTURE_FILE = PROCESSED_DIR / "kline-engine-v2-seed.json"
FULL_DAY_FIXTURE_FILE = PROCESSED_DIR / "kline-engine-v2-full-day.json"
DIST_HTML_FILE = DIST_DIR / "kline-engine" / "kline-engine-v2.html"

# fullDay fixture 来源：build_json.py --batch 产出某日 JSON（已含 warmup）。
# 默认 2026-04-13（历史上的参考日），可按需改为更近的 clean 日。
FULL_DAY_SOURCE_JSON = PROCESSED_DIR / "SPY_2026-04-13.json"

INLINE_FIXTURE_RE = re.compile(
    r"(/\*__KLINE_ENGINE_V2_DEMO_DATA_START__\*/)(.*?)(/\*__KLINE_ENGINE_V2_DEMO_DATA_END__\*/)",
    re.DOTALL,
)


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"fixture 源缺失：{path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_seed_fixture() -> dict:
    """读 slicer 产出的 seed JSON。"""
    seed = _read_json(SEED_FIXTURE_FILE)
    # 非空 sanity，避免静默产出空 fixture
    if not seed.get("bars_1m") or not seed.get("bars_5m"):
        raise ValueError(f"{SEED_FIXTURE_FILE} 的 bars_1m/bars_5m 为空")
    # meta 透传 + generated_at 刷新
    seed_meta = {**seed.get("meta", {}), "generated_at": datetime.now().isoformat(timespec="seconds")}
    return {
        "meta": seed_meta,
        "bars_1m": seed["bars_1m"],
        "bars_5m": seed["bars_5m"],
        "annotations_1m": seed.get("annotations_1m", []),
        "annotations_5m": seed.get("annotations_5m", []),
    }


def build_full_day_fixture() -> dict:
    """读 build_json.py 产出的某日全量 JSON（已做 warmup，MA 从 bar 0 即有值）。"""
    payload = _read_json(FULL_DAY_SOURCE_JSON)
    full_meta = {**payload.get("meta", {}), "generated_at": datetime.now().isoformat(timespec="seconds")}
    return {
        "meta": full_meta,
        "bars_1m": payload.get("bars_1m", []),
        "bars_5m": payload.get("bars_5m", []),
        "annotations_1m": payload.get("annotations_1m", []),
        "annotations_5m": payload.get("annotations_5m", []),
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _inject_demo_fixtures(seed_fixture: dict, full_day_fixture: dict) -> bool:
    if not DIST_HTML_FILE.exists():
        return False
    html = DIST_HTML_FILE.read_text(encoding="utf-8")
    compact = json.dumps(
        {"seed": seed_fixture, "fullDay": full_day_fixture},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    updated, n = INLINE_FIXTURE_RE.subn(rf"\1{compact}\3", html, count=1)
    if n == 0:
        return False
    DIST_HTML_FILE.write_text(updated, encoding="utf-8")
    return True


def main() -> None:
    seed_fixture = build_seed_fixture()
    full_day_fixture = build_full_day_fixture()

    # seed fixture 已经是 slicer 产出；这里复写一遍刷新 generated_at。full-day 同理。
    _write_json(SEED_FIXTURE_FILE, seed_fixture)
    _write_json(FULL_DAY_FIXTURE_FILE, full_day_fixture)

    injected = _inject_demo_fixtures(seed_fixture, full_day_fixture)

    sm = seed_fixture["meta"]
    fm = full_day_fixture["meta"]
    print(
        f"Wrote {SEED_FIXTURE_FILE.relative_to(PROJECT_DIR)}\n"
        f"  date={sm.get('date')} source={sm.get('source')} "
        f"bars_1m={len(seed_fixture['bars_1m'])} bars_5m={len(seed_fixture['bars_5m'])} "
        f"initial_index_1m={sm.get('initial_index_1m')} initial_index_5m={sm.get('initial_index_5m')}"
    )
    print(
        f"Wrote {FULL_DAY_FIXTURE_FILE.relative_to(PROJECT_DIR)}\n"
        f"  date={fm.get('date')} bars_1m={len(full_day_fixture['bars_1m'])} "
        f"bars_5m={len(full_day_fixture['bars_5m'])} "
        f"session_type={fm.get('session_type')} warmup_complete={fm.get('warmup_complete')}"
    )
    print(
        f"Injected demo fixtures into {DIST_HTML_FILE.relative_to(PROJECT_DIR)}"
        if injected
        else f"[WARN] 未注入 HTML：标记 {INLINE_FIXTURE_RE.pattern[:60]}... 未找到或 HTML 缺失"
    )


if __name__ == "__main__":
    main()
