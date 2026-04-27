"""
Task 2: slice_teaching_segment.py 切片工具实现 + 冒烟测试

参见 plan: ../../docs/planning/v0.6-data-foundation/data-foundation-plan.md#task-2
HANDOFF: ../state/HANDOFF.md
依赖：Task 1 已产出足够多的 processed/*.json 用于跨日 preheat 测试

主要新增 data/slice_teaching_segment.py（不在本目录）：

CLI:
  python slice_teaching_segment.py \
    --date YYYY-MM-DD \
    --start HH:MM --end HH:MM \
    --preheat N \
    --title "..." \
    --out PATH \
    [--allow-gappy-slice] [--allow-synthetic]

窗口语义（plan 中重要契约）：
- 1m: 闭区间 [start - preheat, end]
- 5m: 默认从当日 RTH 09:30 开始 → 包含 end 的 5m bucket（D6）
- 跨日 preheat：用 processed/SPY_*.json 文件名做交易日历，优先选 gap_count==0 的前一日
- 缺前日 → 报错 "prev day JSON not found ... Run: python build_json.py raw/bulk/...csv --batch"

initial_index 语义（R5 加固）：
- initial_index_1m = 实际查找 t == start 的下标（不再 = preheat 参数）
- start 在缺口里默认报错；--allow-gappy-slice 后 fallback 到晚于 start 最近一根
- initial_index_5m = bars_5m 中不晚于 start 时间的最近一根的下标

输出 JSON 必含字段：
  meta: { title, ticker, date, source, initial_timeframe, initial_index_1m, initial_index_5m,
          expected_bars_1m, actual_bars_1m, window_gap_count, source_gap_count,
          source_synthetic, generated_at }
  bars_1m, bars_5m, annotations_1m, annotations_5m (留空数组)

Synthetic 隔离（A+ 配套）：
- 默认拒读 processed/synthetic_fallback/ 下的源
- --allow-synthetic 才允许；产物 meta.source_synthetic = true

本脚本职责（4 个冒烟 case 验证）：
1. 当日切片不跨日（如 13:00-14:00 preheat 30）→ 验证 bars_1m 长度 = 91
2. 跨 1 日 preheat（preheat 60，start 09:45）→ 验证 preheat 来自前日 15:15-15:59
3. 跨周末（周一 start 09:45 preheat 60）→ 验证不出现周日时间戳
4. 缺前日 JSON → 验证报错与退出码
5. 浏览器人工 case：随机选一个产物喂 engine.loadData() 验证渲染（手动确认）

跑完 append 报告到 ../state/acceptance.md，更新 ../state/HANDOFF.md。
"""

import sys


def main():
    raise NotImplementedError(
        "Task 2 待接手 Claude 实现\n"
        "需要先实现 data/slice_teaching_segment.py，再写本脚本做冒烟测试"
    )


if __name__ == "__main__":
    main()
