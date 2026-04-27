"""
Task 3: prepare_kline_engine_v2_data.py 降级为 fixture 打包器 + demo seed 选取

参见 plan: ../../docs/planning/v0.6-data-foundation/data-foundation-plan.md#task-3
HANDOFF: ../state/HANDOFF.md
依赖：Task 1 已产出 processed/*.json + Task 2 切片工具就绪

⚠️ R4 关键澄清（用户原话）：
seed_01 是 v2 引擎的占位 fixture，不是必须复刻的 ground truth。
本任务核心是脚本解耦（不再读 teaching_segments.json），不是字节级复刻旧 seed。

主要改动落在 src/prepare_kline_engine_v2_data.py（不在本目录）：

1. seed fixture 数据来源：
   - 起草者从 Task 1 产出的 processed/ 中挑一个 demo 候选日，必须同时满足：
     * meta.session_type == "full_session_clean"
     * meta.warmup_complete.1m == true 且 meta.warmup_complete.5m == true
     * 形态视觉上具有教学性（MA10 拒绝/支撑清晰、HA 颜色翻转明显等）
   - 调 slice_teaching_segment.py 切出教学窗口
   - 不绑死 2026-01-07，不强求保留旧 annotations

2. 删除老路径函数：
   build_seed_fixture / adapt_seed_bars / find_initial_index_5m / normalize_annotations
   等仅为 teaching_segments.json 服务的代码

3. fullDay fixture 维持现状（已直接读 processed/SPY_2026-04-13.json）

验收（行为型）：
- 脚本不再 import / 读 teaching_segments.json
- 浏览器打开 kline-engine-v2.html → seed 模式：渲染 / tooltip / 缩放 / 1m↔5m 切换 / preheat 拖动 全通过
- 浏览器打开 kline-engine-v2.html → fullDay 模式：与本轮已修复版本一致，无回归
- runIntegrationTest() 29 项继续通过
- acceptance.md 按 9 字段格式登记 seed 选用记录：
    date / start / end / preheat / session_type
    warmup_complete_1m / warmup_complete_5m
    source_gap_count / window_gap_count / 选用理由

本脚本职责：
- 询问起草者（或自动按 acceptance 评分）选 demo 日
- 调切片工具产出新 seed
- 跑 runIntegrationTest()
- append 报告到 ../state/acceptance.md，更新 ../state/HANDOFF.md
"""

import sys


def main():
    raise NotImplementedError(
        "Task 3 待接手 Claude 实现\n"
        "需要先改 src/prepare_kline_engine_v2_data.py，再写本脚本驱动"
    )


if __name__ == "__main__":
    main()
