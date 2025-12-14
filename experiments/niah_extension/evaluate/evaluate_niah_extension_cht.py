import argparse
import sys
import os
import dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.llm_judge import LLMJudge

dotenv.load_dotenv()

def main():
    DEFAULT_PROMPT = """
        根據這個問題和正確答案，判斷回應是否正確（意思是它在事實上與正確答案一致）。
        你必須只回應 "true" 或 "false"。
        如果回應有部分不正確，例如拼寫錯誤，請回應 "false"。
        如果回應包含文本片段或額外的支持信息，但仍然保持正確答案且沒有改變意思，請回應 "true"。
        如果回應以類似「以下是文件中最相關的資訊：」開頭，請回應 "true"。只要後續內容與正確答案一致即可。

        問題：{question}

        正確答案：{correct_answer}

        需要判斷的回應：{output}

        指示：只回應 "true"（如果回應在事實上與正確答案一致）或 "false"（如果不一致）。不要提供任何解釋 - 只需回答 "true" 或 "false"。
        """

    parser = argparse.ArgumentParser(description='使用 LLM 評判器評估繁體中文 NIAH 結果')

    parser.add_argument('--prompt', type=str, default=DEFAULT_PROMPT,
                       help='評判提示模板（使用 {output}、{question}、{correct_answer} 作為佔位符）')
    parser.add_argument('--input-path', type=str, required=True,
                       help='輸入（模型輸出）CSV 文件路徑')
    parser.add_argument('--output-path', type=str, required=True,
                       help='輸出 CSV 文件路徑')
    parser.add_argument('--force', action='store_true',
                       help='強制重跑：若輸出 CSV 已存在，先刪除再重新生成（避免沿用舊進度）')
    parser.add_argument('--model-name', type=str, default='gpt-4.1-2025-04-14',
                       help='要使用的模型名稱（預設：gpt-4.1-2025-04-14）')
    parser.add_argument('--provider', type=str, default='openai',
                       choices=['openai', 'ollama'],
                       help='評判 Provider（預設：openai）')
    default_ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    parser.add_argument('--ollama-base-url', type=str, default=default_ollama_base_url,
                       help='Ollama base URL（僅用於 ollama provider，預設：$OLLAMA_BASE_URL 或 http://localhost:11434）')
    parser.add_argument('--ollama-num-ctx', type=int, default=8192,
                       help='Ollama num_ctx（context window），避免長 prompt 或預設值過小導致 runner 崩潰（預設：8192）')
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

    args = parser.parse_args()

    try:
        if args.force and os.path.exists(args.output_path):
            os.remove(args.output_path)
            print(f"已刪除既有輸出檔案以強制重跑：{args.output_path}")

        print("=== 繁體中文 NIAH 評估 ===")
        print(f"輸入文件: {args.input_path}")
        print(f"輸出文件: {args.output_path}")
        print(f"評判 Provider: {args.provider}")
        print(f"評判模型: {args.model_name}")
        if args.provider == 'ollama':
            print(f"Ollama URL: {args.ollama_base_url}")
        print("=" * 50)

        judge = LLMJudge(
            prompt=args.prompt,
            model_name=args.model_name,
            output_column=args.output_column,
            question_column=args.question_column,
            correct_answer_column=args.correct_answer_column,
            provider_name=args.provider,
            ollama_base_url=args.ollama_base_url,
            ollama_num_ctx=args.ollama_num_ctx if args.provider == 'ollama' else None
        )

        judge.evaluate(
            input_path=args.input_path,
            output_path=args.output_path,
            max_context_length=args.max_context_length,
            max_tokens_per_minute=args.max_tokens_per_minute
        )

        print("\n評估完成！")

    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
