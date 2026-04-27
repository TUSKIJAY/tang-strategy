#!/usr/bin/env bash
# v0.6 harness — 任务执行入口
# 详见 README.md 与 state/HANDOFF.md
set -euo pipefail
cd "$(dirname "$0")"

CMD="${1:-help}"
shift || true

run_task() {
  local task="$1"
  local script="tasks/${task}.py"
  if [ ! -f "$script" ]; then
    echo "ERROR: $script 不存在"
    exit 1
  fi
  echo "=== 运行 $task ==="
  python3 "$script" "$@"
}

case "$CMD" in
  status)
    if [ -f state/HANDOFF.md ]; then
      echo "=== v0.6 Harness 状态（HANDOFF.md 头部 30 行）==="
      head -30 state/HANDOFF.md
      echo ""
      echo "（完整状态读 state/HANDOFF.md）"
    else
      echo "ERROR: state/HANDOFF.md 不存在 — harness 未初始化"
      exit 1
    fi
    ;;
  task0)
    run_task task0_fetch "$@"
    ;;
  task0-audit)
    run_task task0_audit "$@"
    ;;
  task1)
    run_task task1_batch "$@"
    ;;
  task2)
    run_task task2_smoke "$@"
    ;;
  task3)
    run_task task3_demo_pack "$@"
    ;;
  all)
    for t in task0 task1 task2 task3; do
      "$0" "$t"
    done
    ;;
  help|--help|-h|*)
    cat <<EOF
v0.6 harness — 用法

  ./run.sh status              查看当前状态（HANDOFF.md 头部）
  ./run.sh task0 [args]        Task 0 — Polygon 拉取（断点续跑）
  ./run.sh task0-audit         Task 0 数据审计（独立可跑）
  ./run.sh task1 [args]        Task 1 — build_json.py --batch
  ./run.sh task2 [args]        Task 2 — 切片工具冒烟测试
  ./run.sh task3 [args]        Task 3 — demo seed 打包 + 集成测试
  ./run.sh all                 串行跑全部
  ./run.sh help                本帮助

接手指南：先读 state/HANDOFF.md
完整 plan：../../docs/planning/v0.6-data-foundation/data-foundation-plan.md
EOF
    ;;
esac
