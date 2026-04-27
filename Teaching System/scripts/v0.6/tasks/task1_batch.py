"""
Task 1: build_json.py --batch 显式化 + vectorized + meta 扩展

参见 plan: ../../docs/planning/v0.6-data-foundation/data-foundation-plan.md#task-1
HANDOFF: ../state/HANDOFF.md
依赖：Task 0 已产出连续完整的 raw/bulk/*.continuous.csv

主要改动落在 data/build_json.py（不在本目录）：

1. 入口语义（plan 修改方案 1）：
   - 新增 --batch flag，与 --date 互斥
   - 传 bulk CSV 不带 --date 也不带 --batch → 报错 "Bulk CSV requires --batch or --date"
   - --force 强制重跑（默认存在则跳过）

2. 性能优化（plan 修改方案 4，O(N²) → O(N)）：
   - 抽出 build_bars_vectorized(df_all)：一次在全量 DataFrame 上算完所有指标
     (HA 按日重置 / SMA 跨日滚动 / 累积 VWAP 按日重置)
   - 批量循环内只做 [bar for bar in all_bars if bar["ts"].startswith(date_str)]
   - 验收：130 天耗时 ≤ 60s

3. session 分类 + meta 字段（plan 修改方案 5/6）：
   - meta.session_type ∈ {full_session_clean, full_session_gappy, short_session, invalid_session}
   - meta.gap_count: int
   - meta.warmup_complete: { "1m": bool, "5m": bool }
     1m=true 当 bars_1m 全部 m250 非 null
     5m=true 当 bars_5m 全部 m250 非 null（5m m250 ≈ 3.5 个交易日，更难达成）

4. Diff 等价性（plan 修改方案 7）：
   - 规范化 diff：忽略 meta.generated_at 与新增兼容字段（session_type/gap_count/warmup_complete）
   - --force 重跑后规范化 diff 现有 9 个 processed/*.json 应 = 0

本脚本职责：
- 调用 ../../data/build_json.py --batch 处理 raw/bulk/*.continuous.csv
- 抽样验证 3 个日期的新 meta 字段
- 跑规范化 diff 等价性检查
- append 报告到 ../state/acceptance.md（含 clean/gappy/short 各日清单 + 实际耗时）
- 更新 ../state/HANDOFF.md
"""

import sys


def main():
    raise NotImplementedError(
        "Task 1 待接手 Claude 实现\n"
        "需要先改 data/build_json.py，再写本脚本驱动"
    )


if __name__ == "__main__":
    main()
