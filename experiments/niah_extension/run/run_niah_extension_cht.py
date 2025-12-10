import argparse
import sys
import os
import dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.providers.openai import OpenAIProvider
from models.providers.anthropic import AnthropicProvider
from models.providers.google import GoogleProvider
from models.providers.ollama import OllamaProvider

dotenv.load_dotenv()

def get_provider(provider_name: str, model_name: str = None, ollama_base_url: str = None):
    """
    獲取指定的 provider 實例

    Args:
        provider_name: Provider 名稱 (openai, anthropic, google, ollama)
        model_name: 模型名稱
        ollama_base_url: Ollama 服務的 base URL (僅用於 ollama provider)

    Returns:
        Provider 實例
    """
    if provider_name.lower() == 'openai':
        return OpenAIProvider()
    elif provider_name.lower() == 'anthropic':
        return AnthropicProvider()
    elif provider_name.lower() == 'google':
        return GoogleProvider(model_name)
    elif provider_name.lower() == 'ollama':
        if ollama_base_url:
            return OllamaProvider(base_url=ollama_base_url)
        else:
            return OllamaProvider()  # 使用預設的 http://localhost:11434
    else:
        raise ValueError(f"未知的 provider: {provider_name}. 可用的 providers: openai, anthropic, google, ollama")


def main():
    parser = argparse.ArgumentParser(description='執行繁體中文 NIAH 延伸實驗')

    parser.add_argument('--provider', type=str, required=True,
                       choices=['openai', 'anthropic', 'google', 'ollama'],
                       help='要使用的 Provider')
    parser.add_argument('--input-path', type=str, required=True,
                       help='輸入 CSV 文件路徑（由 create_haystacks_cht.py 生成）')
    parser.add_argument('--output-path', type=str, required=True,
                       help='輸出 CSV 文件路徑')
    parser.add_argument('--input-column', type=str, required=True,
                       help='包含輸入提示的欄位名稱')
    parser.add_argument('--output-column', type=str, required=True,
                       help='輸出結果的欄位名稱')
    parser.add_argument('--model-name', type=str, required=True,
                       help='要運行的模型名稱')
    parser.add_argument('--max-context-length', type=int, required=True,
                       help='最大 context 長度（tokens）')
    parser.add_argument('--max-tokens-per-minute', type=int, required=True,
                       help='每分鐘最大 tokens 數量（用於速率限制）')
    parser.add_argument('--ollama-base-url', type=str, default='http://localhost:11434',
                       help='Ollama 服務的 base URL（僅用於 ollama provider，預設: http://localhost:11434）')

    args = parser.parse_args()

    try:
        provider = get_provider(args.provider, args.model_name, args.ollama_base_url)

        print(f"=== 繁體中文 NIAH 實驗 ===")
        print(f"Provider: {args.provider}")
        print(f"Model: {args.model_name}")
        print(f"輸入文件: {args.input_path}")
        print(f"輸出文件: {args.output_path}")
        if args.provider == 'ollama':
            print(f"Ollama URL: {args.ollama_base_url}")
        print(f"=" * 50)

        provider.main(
            input_path=args.input_path,
            output_path=args.output_path,
            input_column=args.input_column,
            output_column=args.output_column,
            model_name=args.model_name,
            max_context_length=args.max_context_length,
            max_tokens_per_minute=args.max_tokens_per_minute
        )

        print(f"\n實驗完成！")

    except Exception as e:
        print(f"錯誤: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
