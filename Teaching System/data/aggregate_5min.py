"""
1min K线 → 5min K线 聚合脚本

用法:
  python aggregate_5min.py <1min CSV 文件路径>
  python aggregate_5min.py raw/daily/SPY_1min_2026-04-13.csv

输出:
  同目录下生成 SPY_5min_YYYY-MM-DD.csv

聚合规则:
  open   = 第 1 根 1min 的 open
  high   = 5 根 1min 的 max(high)
  low    = 5 根 1min 的 min(low)
  close  = 第 5 根 1min 的 close
  volume = 5 根 1min 的 sum(volume)
"""

import sys
import os
import pandas as pd


def aggregate_to_5min(input_path: str) -> str:
    """将 1min CSV 聚合为 5min CSV，返回输出文件路径。"""

    df = pd.read_csv(input_path)

    # 统一时间列名：兼容 'datetime' 和 'timestamp' 两种格式
    time_col = "datetime" if "datetime" in df.columns else "timestamp"
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.set_index(time_col)

    # 只保留核心 OHLCV 列
    ohlcv_cols = ["open", "high", "low", "close", "volume"]
    df = df[[c for c in ohlcv_cols if c in df.columns]]

    # 按 5 分钟聚合
    agg_rules = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    df_5min = df.resample("5min").agg(agg_rules).dropna()

    # 生成输出路径：SPY_1min_xxx.csv → SPY_5min_xxx.csv
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path).replace("_1min_", "_5min_")
    output_path = os.path.join(dir_name, base_name)

    df_5min.to_csv(output_path)
    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python aggregate_5min.py <1min CSV 文件路径>")
        print("示例: python aggregate_5min.py raw/daily/SPY_1min_2026-04-13.csv")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"错误: 文件不存在 → {input_path}")
        sys.exit(1)

    output_path = aggregate_to_5min(input_path)

    # 统计对比
    df_in = pd.read_csv(input_path)
    df_out = pd.read_csv(output_path)
    print("[OK] Aggregation complete")
    print(f"   Input:  {input_path} ({len(df_in)} x 1min candles)")
    print(f"   Output: {output_path} ({len(df_out)} x 5min candles)")
    print(f"   Ratio:  {len(df_in)}/{len(df_out)} = {len(df_in)/len(df_out):.1f}x")


if __name__ == "__main__":
    main()
