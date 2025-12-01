"""
Test script for Ollama provider integration.

This script validates that the Ollama provider works correctly
within the Context Rot experiment framework.

Usage:
    python tests/test_ollama_provider.py

Prerequisites:
    - Ollama installed and running
    - At least one model pulled (e.g., ollama pull llama3.1:8b)
"""

import sys
import os
import pandas as pd
import tempfile
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'experiments'))

from models.providers.ollama import OllamaProvider

def test_single_prompt():
    """Test processing a single prompt."""
    print("Test 1: Single Prompt Processing")
    print("-" * 40)

    provider = OllamaProvider()

    test_prompts = [
        ("What is 2+2?", "llama3.1:8b"),
        ("Name one color.", "llama3.1:8b"),
    ]

    for prompt, model in test_prompts:
        print(f"\nPrompt: {prompt}")
        print(f"Model: {model}")

        try:
            index, response = provider.process_single_prompt(
                prompt=prompt,
                model_name=model,
                max_output_tokens=50,
                index=0
            )

            if response.startswith("ERROR"):
                print(f"❌ Error: {response}")
                return False
            else:
                print(f"✓ Response: {response[:100]}")
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

    print("\n✓ Test 1 passed!")
    return True

def test_batch_processing():
    """Test batch processing with CSV files."""
    print("\n\nTest 2: Batch Processing")
    print("-" * 40)

    # Create temporary test data
    test_data = pd.DataFrame({
        'prompt': [
            'What is the capital of France?',
            'What is 10 + 5?',
            'Name a programming language.',
        ],
        'token_count': [100, 100, 100],
        'max_output_tokens': [50, 50, 50]
    })

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as input_file:
        input_path = input_file.name
        test_data.to_csv(input_path, index=False)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as output_file:
        output_path = output_file.name

    try:
        print(f"Input file: {input_path}")
        print(f"Output file: {output_path}")
        print(f"Test prompts: {len(test_data)}")

        provider = OllamaProvider()
        provider.main(
            input_path=input_path,
            output_path=output_path,
            input_column='prompt',
            output_column='response',
            model_name='llama3.1:8b',  # Change to your installed model
            max_context_length=128000,
            max_tokens_per_minute=1000000  # No rate limiting for local models
        )

        # Check results
        results = pd.read_csv(output_path)

        if 'response' not in results.columns:
            print("❌ Output column not found in results")
            return False

        success_count = (~results['response'].isna() &
                        ~results['response'].str.startswith('ERROR', na=False)).sum()

        print(f"\n✓ Processed {success_count}/{len(test_data)} prompts successfully")

        if success_count == len(test_data):
            print("✓ Test 2 passed!")
            return True
        else:
            print(f"⚠ Only {success_count}/{len(test_data)} prompts succeeded")
            return False

    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        try:
            os.unlink(input_path)
            os.unlink(output_path)
        except:
            pass

def test_client_initialization():
    """Test client initialization with custom host."""
    print("\n\nTest 3: Client Initialization")
    print("-" * 40)

    try:
        provider = OllamaProvider()
        print(f"✓ Provider initialized successfully")
        print(f"✓ Client type: {type(provider.client)}")
        print("✓ Test 3 passed!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False

def main():
    print("=" * 60)
    print("Ollama Provider Test Suite")
    print("=" * 60)
    print()
    print("This test requires:")
    print("1. Ollama installed and running")
    print("2. Model 'llama3.1:8b' available (or change the model name)")
    print("3. Default Ollama host (http://localhost:11434)")
    print()

    tests = [
        test_client_initialization,
        test_single_prompt,
        test_batch_processing,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)

    if all(results):
        print("\n🎉 All tests passed!")
        print("\nOllama provider is ready for use in experiments.")
        return 0
    else:
        print("\n⚠ Some tests failed.")
        print("\nPlease check:")
        print("- Ollama is running (ollama list)")
        print("- Required models are installed (ollama pull llama3.1:8b)")
        print("- OLLAMA_HOST is correctly configured")
        return 1

if __name__ == "__main__":
    sys.exit(main())
