#!/usr/bin/env python3
"""
最小 Ollama Provider 測試
Minimal test for Ollama provider and judge functionality
"""

import sys
import os

print("=" * 60)
print("Ollama Provider - Minimal Test")
print("=" * 60)

# ============================================================
# 測試 1: 單一提示測試 (Single Prompt Test)
# ============================================================
print("\n[Test 1] Single Prompt")
print("-" * 60)

try:
    from models.providers.ollama import OllamaProvider

    provider = OllamaProvider()
    print("✓ OllamaProvider initialized")

    # 簡單的測試提示
    test_prompt = "What is 2+2? Answer with just the number."
    model_name = "llama3.1:8b"  # 修改為您已安裝的模型

    print(f"  Prompt: {test_prompt}")
    print(f"  Model: {model_name}")

    idx, response = provider.process_single_prompt(
        prompt=test_prompt,
        model_name=model_name,
        max_output_tokens=50,
        index=0
    )

    if response.startswith("ERROR"):
        print(f"✗ Error: {response}")
        sys.exit(1)
    else:
        print(f"✓ Response: {response.strip()}")

except Exception as e:
    print(f"✗ Test 1 failed: {e}")
    print("\nMake sure:")
    print("  1. Ollama is running (ollama serve)")
    print("  2. Model is installed (ollama pull llama3.1:8b)")
    sys.exit(1)

# ============================================================
# 測試 2: LLM Judge 功能 (LLM Judge Test)
# ============================================================
print("\n[Test 2] LLM Judge")
print("-" * 60)

try:
    from models.llm_judge import LLMJudge

    # 簡單的 judge prompt
    judge_prompt = """Compare the output with the correct answer.
Output: {output}
Correct Answer: {correct_answer}

Are they equivalent? Answer only 'True' or 'False'."""

    judge = LLMJudge(
        prompt=judge_prompt,
        model_name="llama3.1:8b",  # 修改為您已安裝的模型
        provider="ollama",
        output_column="test_output",
        question_column="test_question",
        correct_answer_column="test_answer"
    )

    print("✓ LLMJudge initialized with Ollama provider")
    print(f"  Model: llama3.1:8b")
    print(f"  Provider: ollama")

    # 測試 judge 的單一評估
    test_output = "4"
    test_answer = "4"

    formatted_prompt = judge_prompt.format(
        output=test_output,
        question="",  # 不需要 question
        correct_answer=test_answer
    )

    idx, judge_response = provider.process_single_prompt(
        prompt=formatted_prompt,
        model_name="llama3.1:8b",
        max_output_tokens=10,
        index=0
    )

    print(f"✓ Judge response: {judge_response.strip()}")

except Exception as e:
    print(f"✗ Test 2 failed: {e}")
    sys.exit(1)

# ============================================================
# 完成
# ============================================================
print("\n" + "=" * 60)
print("✓ All tests passed!")
print("=" * 60)
print("\nOllama provider is ready for:")
print("  • Running experiments with local models")
print("  • Using Ollama models as LLM judges")
print("\nNext steps:")
print("  • See experiments/models/README.md for usage examples")
print("  • Try examples/ollama_example.py for more examples")
