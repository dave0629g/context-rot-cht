import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import argparse
import os
import sys
from typing import Optional, Tuple

# 設定支援中文的字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft JhengHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_niah_heatmap(csv_path: str,
                       title: Optional[str] = None,
                       output_path: Optional[str] = None,
                       figsize: Tuple[int, int] = (10, 6)) -> pd.DataFrame:
    """
    創建 NIAH 性能熱圖

    Args:
        csv_path: 輸入 CSV 文件路徑（包含評估結果）
        title: 圖表標題（可選）
        output_path: 輸出圖片路徑（可選）
        figsize: 圖表大小（寬, 高）

    Returns:
        處理後的 DataFrame
    """

    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['llm_judge_output'])
    print(f"從 {csv_path} 載入了 {len(df)} 個有效樣本")

    # 清理 llm_judge_output，移除空白和換行
    df['accuracy'] = df['llm_judge_output'].apply(
        lambda x: 1 if str(x).strip().lower() == 'true' else 0
    )

    all_input_lengths = sorted(df['approximate_input_length'].unique())
    all_needle_depths = sorted(df['needle_depth'].unique())

    pivot_table = df.groupby(['approximate_input_length', 'needle_depth'])['accuracy'].mean().reset_index()
    pivot_table = pivot_table.pivot(index='needle_depth', columns='approximate_input_length', values='accuracy')

    heatmap_data = pd.DataFrame(
        index=all_needle_depths,
        columns=all_input_lengths,
        dtype=float
    )

    for depth in all_needle_depths:
        for length in all_input_lengths:
            if depth in pivot_table.index and length in pivot_table.columns:
                value = pivot_table.loc[depth, length]
                if pd.notna(value):
                    heatmap_data.loc[depth, length] = value

    plt.figure(figsize=figsize)

    colors = ['white', '#F28E2B']
    cmap = ListedColormap(colors)
    cmap.set_bad(color='lightgrey')

    im = plt.imshow(heatmap_data.values,
                    cmap=cmap,
                    aspect='auto',
                    vmin=0, vmax=1,
                    origin='lower')

    length_labels = []
    for length in all_input_lengths:
        if length < 1000:
            length_labels.append(str(length))
        else:
            length_labels.append(f"{int(length/1000)}K")

    plt.xticks(range(len(all_input_lengths)), length_labels)
    plt.yticks(range(len(all_needle_depths)), [f"{int(d)}%" for d in all_needle_depths])

    if title is None:
        title = f"NIAH 性能表現 - {os.path.basename(csv_path)}"
    plt.title(title, fontsize=14)
    plt.xlabel('輸入長度（tokens）', fontsize=12)
    plt.ylabel('Needle 深度（%）', fontsize=12)
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='white')
        print(f"熱圖已儲存至: {output_path}")
    plt.close()

    overall_accuracy = df['accuracy'].mean()
    print(f"\n整體準確率: {overall_accuracy:.3f}")
    print(f"總樣本數: {len(df)}")

    return df


def main():
    parser = argparse.ArgumentParser(description='創建繁體中文 NIAH 性能熱圖')
    parser.add_argument('--csv-path', type=str, required=True,
                       help='輸入 CSV 文件路徑')
    parser.add_argument('--title', type=str, default=None,
                       help='圖表標題（可選）')
    parser.add_argument('--output-path', type=str, default=None,
                       help='輸出圖片路徑（可選）')

    args = parser.parse_args()

    try:
        print("=== 繁體中文 NIAH 視覺化 ===")
        print(f"輸入文件: {args.csv_path}")
        if args.output_path:
            print(f"輸出圖片: {args.output_path}")
        print("=" * 50)

        create_niah_heatmap(
            csv_path=args.csv_path,
            title=args.title,
            output_path=args.output_path
        )

        print("\n視覺化完成！")

    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
