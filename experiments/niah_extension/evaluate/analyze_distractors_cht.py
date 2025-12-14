import argparse
import sys
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import dotenv

dotenv.load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.llm_judge import LLMJudge

# 設定支援中文的字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft JhengHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def create_histogram_for_file(csv_path: str, visual_output_path: str = None, model_name: str = None):
    """
    為指定的 CSV 文件創建干擾項分佈直方圖

    Args:
        csv_path: 輸入 CSV 文件路徑
        visual_output_path: 輸出圖片路徑（可選）
        model_name: 模型名稱（用於圖表標題）

    Returns:
        處理後的 DataFrame
    """
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['distractor_label'])

    df['distractor_label'] = df['distractor_label'].astype(str)

    plt.figure(figsize=(10, 6))

    value_counts = df['distractor_label'].value_counts().sort_index()
    normalized_counts = value_counts / value_counts.sum()

    plt.bar(normalized_counts.index.astype(str), normalized_counts.values,
            alpha=0.7, edgecolor='none')
    plt.xlabel('干擾項選擇', fontsize=12)
    plt.ylabel('比例', fontsize=12)
    plt.title(f'{model_name} 的幻覺分佈', fontsize=14)
    plt.grid(axis='y', alpha=0.3)

    if visual_output_path:
        plt.savefig(visual_output_path, dpi=300, bbox_inches='tight')
        print(f"直方圖已儲存至: {visual_output_path}")
    plt.close()

    print(f"總有效樣本數: {len(df)}")
    print(f"數值計數:\n{df['distractor_label'].value_counts().sort_index()}")

    return df


def main():
    DEFAULT_PROMPT = """
        根據這個模型輸出，它對以下問題給出了什麼回應：{question}

        選擇最接近的選項，如果沒有一個選項符合或提到了多個選項，則選擇「以上皆非」（-1）。
        如果提到了某個選項但不是確定的，並且有猶豫，提到「然而」或表示輕微猶豫的內容，則選擇「以上皆非」（-1）。
        如果提到文件中存在不一致，則選擇「以上皆非」（-1）。

        選項：
        {distractors}

        模型輸出：{output}

        再次提醒，如果提到了多個選項或有任何猶豫，則選擇「以上皆非」（-1）。

        指示：只輸出數字。如果沒有提到任何特定選項，輸出 -1。
        """

    parser = argparse.ArgumentParser(description='使用 LLM 評判器分析繁體中文 NIAH 干擾項')

    parser.add_argument('--prompt', type=str, default=DEFAULT_PROMPT,
                       help='評判提示模板（使用 {output}、{question}、{correct_answer}、{distractors} 作為佔位符）')
    parser.add_argument('--input-path', type=str, required=True,
                       help='輸入 CSV 文件路徑')
    parser.add_argument('--output-path', type=str, required=True,
                       help='輸出 CSV 文件路徑')
    parser.add_argument('--visual-path', type=str, required=True,
                       help='視覺化輸出文件路徑')
    parser.add_argument('--model-name', type=str, default='gpt-4.1-2025-04-14',
                       help='要使用的模型名稱（預設：gpt-4.1-2025-04-14）')
    parser.add_argument('--output-column', type=str, default='output',
                       help='包含模型輸出的欄位名稱（預設：output）')
    parser.add_argument('--question-column', type=str, default='question',
                       help='包含問題的欄位名稱（預設：question）')
    parser.add_argument('--correct-answer-column', type=str, default='answer',
                       help='包含正確答案的欄位名稱（預設：answer）')
    parser.add_argument('--max-context-length', type=int, default=1_047_576,
                       help='最大 context 長度（tokens）（預設：1_047_576）')
    parser.add_argument('--max-tokens-per-minute', type=int, default=2_000_000,
                       help='每分鐘最大 tokens 數量用於速率限制（預設：2_000_000）')
    parser.add_argument('--distractors-file', type=str, default=None,
                       help='包含干擾項的 JSON 文件路徑')

    args = parser.parse_args()

    try:
        print("=== 繁體中文 NIAH 干擾項分析 ===")
        print(f"輸入文件: {args.input_path}")
        print(f"輸出文件: {args.output_path}")
        print(f"視覺化文件: {args.visual_path}")
        print(f"評判模型: {args.model_name}")
        if args.distractors_file:
            print(f"干擾項文件: {args.distractors_file}")
        print("=" * 50)

        judge = LLMJudge(
            prompt=args.prompt,
            model_name=args.model_name,
            output_column=args.output_column,
            question_column=args.question_column,
            correct_answer_column=args.correct_answer_column,
            distractors_file=args.distractors_file
        )

        judge.analyze_distractors(
            input_path=args.input_path,
            output_path=args.output_path,
            max_context_length=args.max_context_length,
            max_tokens_per_minute=args.max_tokens_per_minute
        )

        create_histogram_for_file(args.output_path, args.visual_path, args.model_name)

        print("\n干擾項分析完成！")

    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
