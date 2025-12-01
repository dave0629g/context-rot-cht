#!/usr/bin/env python3
"""
最小環境檢查腳本 - Minimal environment sanity check
測試基本依賴和 providers 是否可正常導入
"""
import os
import sys

print("=" * 60)
print("Context Rot - Sanity Check")
print("=" * 60)

# 1. Python 版本
print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

# 2. 基本依賴
required_modules = ["pandas", "tiktoken", "tqdm"]
for m in required_modules:
    try:
        __import__(m)
        print(f"✓ {m}")
    except ImportError:
        print(f"✗ {m} (missing)")
        sys.exit(1)

# 3. Providers 測試
providers_to_test = [
    ("openai", "OpenAIProvider"),
    ("anthropic", "AnthropicProvider"),
    ("google", "GoogleProvider"),
    ("ollama", "OllamaProvider"),
]

print("\nProviders:")
for module_name, class_name in providers_to_test:
    try:
        module = __import__(f"models.providers.{module_name}", fromlist=[class_name])
        getattr(module, class_name)
        print(f"✓ {class_name}")
    except Exception as e:
        print(f"✗ {class_name}: {e}")

# 4. Ollama 連線測試 (optional)
print("\nOllama:")
try:
    from models.providers.ollama import OllamaProvider
    provider = OllamaProvider()
    print("✓ Ollama client initialized")
    print(f"  Host: {os.getenv('OLLAMA_HOST', 'http://localhost:11434')}")
except Exception as e:
    print(f"✗ Ollama: {e}")

print("\n" + "=" * 60)
print("Sanity check completed")
print("=" * 60)

