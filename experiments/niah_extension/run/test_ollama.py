#!/usr/bin/env python3
"""
測試 Ollama 連接和可用模型
"""

import sys
import os
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from models.providers.ollama import OllamaProvider


def test_ollama_connection(base_url: str = "http://127.0.0.1:11434"):
    """測試 Ollama 連接並列出可用模型"""
    print(f"正在測試 Ollama 連接: {base_url}")
    print("=" * 50)

    try:
        # 測試連接
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()

        data = response.json()

        if 'models' in data and len(data['models']) > 0:
            print(f"\n✓ 成功連接到 Ollama！")
            print(f"\n可用的模型 ({len(data['models'])} 個):")
            print("-" * 50)

            for model in data['models']:
                name = model.get('name', 'unknown')
                size = model.get('size', 0) / (1024**3)  # 轉換為 GB
                modified = model.get('modified_at', 'unknown')
                print(f"  • {name}")
                print(f"    大小: {size:.2f} GB")
                print(f"    修改時間: {modified}")
                print()
        else:
            print("⚠ 連接成功，但沒有找到可用的模型")
            print("請先使用 'ollama pull <model-name>' 下載模型")

    except requests.exceptions.ConnectionError:
        print(f"✗ 無法連接到 Ollama 服務")
        print(f"  請確認 Ollama 正在運行，並且監聽 {base_url}")
        print(f"  你可以使用 'ollama serve' 啟動服務")
        sys.exit(1)

    except requests.exceptions.Timeout:
        print(f"✗ 連接超時")
        print(f"  Ollama 服務可能沒有回應")
        sys.exit(1)

    except Exception as e:
        print(f"✗ 錯誤: {e}")
        sys.exit(1)


def test_simple_query(base_url: str = "http://127.0.0.1:11434", model_name: str = "qwen3:0.6b"):
    """測試簡單的查詢"""
    print("\n" + "=" * 50)
    print(f"測試簡單查詢: {model_name}")
    print("=" * 50)

    try:
        provider = OllamaProvider(base_url=base_url)

        test_prompt = "請用一句話回答：台灣的首都是哪裡？"
        print(f"\n提示: {test_prompt}")
        print("\n處理中...")

        index, response = provider.process_single_prompt(
            prompt=test_prompt,
            model_name=model_name,
            max_output_tokens=100,
            index=0
        )

        print(f"\n回應:")
        print(f"{response}")

        if response.startswith("ERROR"):
            print(f"\n✗ 查詢失敗")
            return False
        else:
            print(f"\n✓ 查詢成功！")
            return True

    except Exception as e:
        print(f"\n✗ 測試失敗: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='測試 Ollama 連接')
    parser.add_argument('--base-url', type=str, default='http://127.0.0.1:11434',
                       help='Ollama base URL (預設: http://127.0.0.1:11434)')
    parser.add_argument('--model', type=str, default='qwen3:0.6b',
                       help='要測試的模型名稱 (預設: qwen3:0.6b)')
    parser.add_argument('--skip-query', action='store_true',
                       help='跳過查詢測試，只檢查連接')

    args = parser.parse_args()

    # 測試連接
    test_ollama_connection(args.base_url)

    # 測試查詢
    if not args.skip_query:
        success = test_simple_query(args.base_url, args.model)
        if not success:
            sys.exit(1)

    print("\n" + "=" * 50)
    print("所有測試完成！")
    print("=" * 50)
