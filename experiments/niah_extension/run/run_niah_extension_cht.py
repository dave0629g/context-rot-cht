import argparse
import sys
import os
import dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.providers.openai import OpenAIProvider
from models.providers.anthropic import AnthropicProvider
from models.providers.google import GoogleProvider
from models.providers.ollama import OllamaProvider
from models.providers.huggingface import HuggingFaceProvider
from models.providers.llamacpp import LlamaCppProvider

dotenv.load_dotenv()

def get_provider(provider_name: str, model_name: str = None, ollama_base_url: str = None, ollama_num_ctx: int | None = None, hf_device: str = "auto",
                llamacpp_model_path: str = None, llamacpp_n_ctx: int = 8192, llamacpp_n_gpu_layers: int = -1):
    """
    獲取指定的 provider 實例

    Args:
        provider_name: Provider 名稱 (openai, anthropic, google, ollama, huggingface, llamacpp)
        model_name: 模型名稱
        ollama_base_url: Ollama 服務的 base URL (僅用於 ollama provider)
        hf_device: Hugging Face 設備 (auto, cuda, cpu)
        llamacpp_model_path: llama-cpp GGUF 模型路徑
        llamacpp_n_ctx: llama-cpp context 大小
        llamacpp_n_gpu_layers: llama-cpp GPU 層數

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
            return OllamaProvider(base_url=ollama_base_url, num_ctx=ollama_num_ctx)
        else:
            return OllamaProvider(num_ctx=ollama_num_ctx)  # 使用預設的 http://localhost:11434
    elif provider_name.lower() == 'huggingface':
        return HuggingFaceProvider(model_name=model_name, device=hf_device)
    elif provider_name.lower() == 'llamacpp':
        if not llamacpp_model_path:
            raise ValueError("llamacpp provider 需要 --llamacpp-model-path 參數")
        return LlamaCppProvider(model_path=llamacpp_model_path, n_ctx=llamacpp_n_ctx, n_gpu_layers=llamacpp_n_gpu_layers)
    else:
        raise ValueError(f"未知的 provider: {provider_name}. 可用的 providers: openai, anthropic, google, ollama, huggingface, llamacpp")


def main():
    parser = argparse.ArgumentParser(description='執行繁體中文 NIAH 延伸實驗')

    parser.add_argument('--provider', type=str, required=True,
                       choices=['openai', 'anthropic', 'google', 'ollama', 'huggingface', 'llamacpp'],
                       help='要使用的 Provider')
    parser.add_argument('--input-path', type=str, required=True,
                       help='輸入 CSV 文件路徑（由 create_haystacks_cht.py 生成）')
    parser.add_argument('--output-path', type=str, required=True,
                       help='輸出 CSV 文件路徑')
    parser.add_argument('--input-column', type=str, required=True,
                       help='包含輸入提示的欄位名稱')
    parser.add_argument('--output-column', type=str, required=True,
                       help='輸出結果的欄位名稱')
    parser.add_argument('--force', action='store_true',
                       help='強制重跑：若輸出 CSV 已存在，先刪除再重新生成（避免沿用舊進度）')
    parser.add_argument('--model-name', type=str, required=True,
                       help='要運行的模型名稱')
    parser.add_argument('--max-context-length', type=int, required=True,
                       help='最大 context 長度（tokens）')
    parser.add_argument('--ollama-num-ctx', type=int, default=None,
                       help='Ollama num_ctx（context window）。未指定則使用 max-context-length（較適合長 prompt）。')
    parser.add_argument('--max-tokens-per-minute', type=int, required=True,
                       help='每分鐘最大 tokens 數量（用於速率限制）')
    default_ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    parser.add_argument('--ollama-base-url', type=str, default=default_ollama_base_url,
                       help='Ollama 服務的 base URL（僅用於 ollama provider，預設: $OLLAMA_BASE_URL 或 http://localhost:11434）')
    parser.add_argument('--hf-device', type=str, default='auto',
                       choices=['auto', 'cuda', 'cpu'],
                       help='Hugging Face 運行設備（僅用於 huggingface provider，預設: auto）')
    parser.add_argument('--llamacpp-model-path', type=str, default=None,
                       help='llama-cpp GGUF 模型路徑（僅用於 llamacpp provider）')
    parser.add_argument('--llamacpp-n-ctx', type=int, default=8192,
                       help='llama-cpp context 大小（僅用於 llamacpp provider，預設: 8192）')
    parser.add_argument('--llamacpp-n-gpu-layers', type=int, default=-1,
                       help='llama-cpp GPU 層數（僅用於 llamacpp provider，-1=全部，0=CPU，預設: -1）')

    args = parser.parse_args()

    try:
        ollama_num_ctx = args.ollama_num_ctx
        if args.provider == 'ollama' and ollama_num_ctx is None:
            ollama_num_ctx = args.max_context_length

        if args.force and os.path.exists(args.output_path):
            os.remove(args.output_path)
            print(f"已刪除既有輸出檔案以強制重跑：{args.output_path}")

        provider = get_provider(
            args.provider,
            args.model_name,
            args.ollama_base_url,
            ollama_num_ctx,
            args.hf_device,
            args.llamacpp_model_path,
            args.llamacpp_n_ctx,
            args.llamacpp_n_gpu_layers
        )

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
