"""
Example script demonstrating how to use the Ollama provider for local model testing.

This script shows how to:
1. Use Ollama for running experiments with local models
2. Use Ollama models as LLM judges for evaluation

Prerequisites:
- Install Ollama from https://ollama.ai
- Pull the desired model: ollama pull llama3.1:8b
- Ensure Ollama is running (check with: ollama list)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'experiments'))

from models.providers.ollama import OllamaProvider
from models.llm_judge import LLMJudge

def test_ollama_provider():
    """Test basic Ollama provider functionality."""
    print("Testing Ollama Provider...")

    provider = OllamaProvider()

    # Simple test prompt
    index, response = provider.process_single_prompt(
        prompt="What is 2+2? Answer with just the number.",
        model_name="llama3.1:8b",  # Change to any model you have installed
        max_output_tokens=100,
        index=0
    )

    print(f"Response: {response}")
    print("✓ Ollama provider test completed successfully!\n")

def test_ollama_judge():
    """Demonstrate using Ollama as an LLM judge."""
    print("Testing Ollama as LLM Judge...")

    # Simple judge prompt for testing
    judge_prompt = """You are evaluating if the output correctly answers the question.

Question: {question}
Correct Answer: {correct_answer}
Model Output: {output}

Does the model output correctly answer the question? Respond with only 'True' or 'False'."""

    judge = LLMJudge(
        prompt=judge_prompt,
        model_name="llama3.1:8b",  # Use any Ollama model
        provider="ollama",
        output_column="model_output",
        question_column="question",
        correct_answer_column="answer"
    )

    print("✓ Ollama judge initialized successfully!")
    print(f"  Judge Model: llama3.1:8b")
    print(f"  Provider: Ollama\n")

def main():
    print("=" * 60)
    print("Ollama Provider Examples")
    print("=" * 60)
    print()

    try:
        test_ollama_provider()
        test_ollama_judge()

        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Prepare your experiment CSV files")
        print("2. Use OllamaProvider.main() to run batch experiments")
        print("3. Use LLMJudge.evaluate() with provider='ollama' for evaluation")
        print()
        print("See experiments/models/README.md for detailed usage examples.")

    except Exception as e:
        print(f"Error: {e}")
        print()
        print("Make sure:")
        print("1. Ollama is installed and running")
        print("2. You have pulled the required model: ollama pull llama3.1:8b")
        print("3. OLLAMA_HOST is correctly set (or using default localhost:11434)")

if __name__ == "__main__":
    main()
