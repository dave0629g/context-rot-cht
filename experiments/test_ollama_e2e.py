#!/usr/bin/env python3
"""
Ollama 端到端測試 (End-to-End Test)
測試完整的實驗流程：生成回應 → LLM Judge 評估
"""

import sys
import os
import pandas as pd
import tempfile

print("=" * 60)
print("Ollama E2E Test: Generate + Judge")
print("=" * 60)

# 配置
MODEL_NAME = "llama3.1:8b"  # 修改為您已安裝的模型
MAX_TOKENS = 100

# ============================================================
# 步驟 1: 準備測試資料
# ============================================================
print("\n[Step 1] Prepare test data")
print("-" * 60)

test_data = pd.DataFrame({
    'prompt': [
        'What is 2+2? Answer with just the number.',
        'What is the capital of France? Answer with just the city name.',
        'Is water wet? Answer yes or no.',
    ],
    'expected_answer': [
        '4',
        'Paris',
        'yes',
    ],
    'token_count': [100, 100, 100],
    'max_output_tokens': [MAX_TOKENS, MAX_TOKENS, MAX_TOKENS]
})

print(f"✓ Created {len(test_data)} test cases")

# 建立臨時檔案
with tempfile.NamedTemporaryFile(mode='w', suffix='_input.csv', delete=False) as f:
    input_csv = f.name
    test_data.to_csv(input_csv, index=False)
    print(f"✓ Saved input: {input_csv}")

output_csv = input_csv.replace('_input.csv', '_output.csv')
judged_csv = input_csv.replace('_input.csv', '_judged.csv')

# ============================================================
# 步驟 2: 使用 Ollama 生成回應
# ============================================================
print("\n[Step 2] Generate responses with Ollama")
print("-" * 60)

try:
    from models.providers.ollama import OllamaProvider

    provider = OllamaProvider()
    print(f"✓ Using model: {MODEL_NAME}")

    provider.main(
        input_path=input_csv,
        output_path=output_csv,
        input_column='prompt',
        output_column='response',
        model_name=MODEL_NAME,
        max_context_length=128000,
        max_tokens_per_minute=1000000  # 無限制
    )

    # 檢查結果
    results = pd.read_csv(output_csv)
    success_count = (~results['response'].isna() &
                     ~results['response'].str.startswith('ERROR', na=False)).sum()

    print(f"✓ Generated {success_count}/{len(results)} responses")

    if success_count == 0:
        print("✗ No successful responses")
        sys.exit(1)

except Exception as e:
    print(f"✗ Generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================
# 步驟 3: 使用 Ollama Judge 評估
# ============================================================
print("\n[Step 3] Evaluate with Ollama Judge")
print("-" * 60)

try:
    from models.llm_judge import LLMJudge

    # Judge prompt
    judge_prompt = """You are evaluating if the model output correctly answers the question.

Question: {question}
Expected Answer: {correct_answer}
Model Output: {output}

Does the model output match the expected answer? Consider semantically equivalent answers as correct.
Answer only 'True' or 'False'."""

    judge = LLMJudge(
        prompt=judge_prompt,
        model_name=MODEL_NAME,
        provider="ollama",
        output_column="response",
        question_column="prompt",
        correct_answer_column="expected_answer"
    )

    print(f"✓ Using judge model: {MODEL_NAME}")

    # 準備 judge 輸入
    results['prompt'] = test_data['prompt']
    results['expected_answer'] = test_data['expected_answer']
    results.to_csv(output_csv, index=False)

    # 執行評估
    judge.evaluate(
        input_path=output_csv,
        output_path=judged_csv,
        max_context_length=128000,
        max_tokens_per_minute=1000000
    )

    # 檢查 judge 結果
    judged = pd.read_csv(judged_csv)

    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)

    for idx, row in judged.iterrows():
        prompt = row['prompt'][:50] + "..." if len(row['prompt']) > 50 else row['prompt']
        response = str(row['response'])[:50] if pd.notna(row['response']) else "N/A"
        expected = row['expected_answer']
        judgment = str(row['llm_judge_output']) if pd.notna(row['llm_judge_output']) else "N/A"

        print(f"\nCase {idx + 1}:")
        print(f"  Q: {prompt}")
        print(f"  A: {response}")
        print(f"  Expected: {expected}")
        print(f"  Judge: {judgment}")

except Exception as e:
    print(f"✗ Judge evaluation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================
# 清理
# ============================================================
print("\n" + "=" * 60)
print("Cleanup")
print("=" * 60)

for filepath in [input_csv, output_csv, judged_csv]:
    if os.path.exists(filepath):
        print(f"✓ Keeping: {filepath}")
        # os.unlink(filepath)  # 取消註解以自動刪除

print("\n" + "=" * 60)
print("✓ E2E test completed successfully!")
print("=" * 60)
print("\nOllama is ready for full experiments with:")
print(f"  • Model: {MODEL_NAME}")
print("  • Provider: OllamaProvider")
print("  • Judge: LLMJudge with Ollama")
