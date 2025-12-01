# Ollama Integration for Context Rot Experiments

This document describes the Ollama integration added to the Context Rot experiment framework, enabling offline experimentation with local open-source models.

## Overview

The Ollama provider extends the existing model provider architecture to support local model inference through Ollama. This allows researchers to:

- Run experiments completely offline
- Avoid API costs for large-scale testing
- Use open-source models (Llama, Qwen, Mistral, etc.)
- Employ local models as LLM judges for evaluation

## Architecture

### Files Added/Modified

#### New Files

1. **[experiments/models/providers/ollama.py](experiments/models/providers/ollama.py)**
   - Implementation of `OllamaProvider` class
   - Inherits from `BaseProvider`
   - Handles communication with local Ollama server
   - Configurable host via `OLLAMA_HOST` environment variable

2. **[experiments/models/providers/__init__.py](experiments/models/providers/__init__.py)**
   - Package initialization for providers module
   - Exports all provider classes

3. **[examples/ollama_example.py](examples/ollama_example.py)**
   - Example script demonstrating Ollama usage
   - Shows both basic provider usage and judge configuration

4. **[tests/test_ollama_provider.py](tests/test_ollama_provider.py)**
   - Comprehensive test suite for Ollama provider
   - Tests single prompt, batch processing, and client initialization

5. **[CHANGELOG.md](CHANGELOG.md)**
   - Detailed changelog documenting all additions

6. **This file ([OLLAMA_INTEGRATION.md](OLLAMA_INTEGRATION.md))**
   - Integration documentation

#### Modified Files

1. **[experiments/models/llm_judge.py](experiments/models/llm_judge.py)**
   - Added `provider` parameter to `__init__` method
   - Added `_get_provider()` method for dynamic provider selection
   - Imported all provider classes
   - Default remains OpenAI for backward compatibility

2. **[requirements.txt](requirements.txt)**
   - Added `ollama>=0.4.8` dependency

3. **[experiments/models/README.md](experiments/models/README.md)**
   - Added Ollama provider documentation
   - Added setup instructions
   - Added usage examples for both testing and judging

4. **[README.md](README.md)**
   - Updated Quick Start section with Ollama setup
   - Added Ollama to environment variables list

## Usage Examples

### 1. Basic Provider Usage

```python
from models.providers.ollama import OllamaProvider

provider = OllamaProvider()
provider.main(
    input_path="input.csv",
    output_path="output.csv",
    input_column="prompt",
    output_column="response",
    model_name="llama3.1:8b",
    max_context_length=128000,
    max_tokens_per_minute=1000000  # No rate limits for local
)
```

### 2. Using Ollama as LLM Judge

```python
from models.llm_judge import LLMJudge

judge = LLMJudge(
    prompt=your_judge_prompt,
    model_name="qwen2.5:14b",
    provider="ollama"  # Key parameter
)

judge.evaluate(
    input_path="results.csv",
    output_path="judged_results.csv",
    max_context_length=128000,
    max_tokens_per_minute=1000000
)
```

### 3. Custom Ollama Host

```bash
export OLLAMA_HOST="http://remote-server:11434"
python your_experiment.py
```

## Setup Instructions

### 1. Install Ollama

```bash
# macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Or download from https://ollama.ai
```

### 2. Pull Models

```bash
# Example models for testing
ollama pull llama3.1:8b
ollama pull qwen2.5:14b
ollama pull mistral:7b

# Verify installation
ollama list
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
# Test the Ollama provider
python tests/test_ollama_provider.py

# Run example script
python examples/ollama_example.py
```

## Implementation Details

### OllamaProvider Class

The `OllamaProvider` class follows the same interface as other providers:

```python
class OllamaProvider(BaseProvider):
    def process_single_prompt(self, prompt: str, model_name: str,
                            max_output_tokens: int, index: int) -> tuple[int, str]:
        """Process a single prompt using Ollama."""
        # Uses ollama.Client to communicate with local server

    def get_client(self) -> Any:
        """Initialize Ollama client with configurable host."""
        # Returns ollama.Client instance
```

### Key Features

1. **Error Handling**: Comprehensive error handling with `ERROR:` prefix for failed requests
2. **Empty Response Detection**: Warns when Ollama returns empty content
3. **Configurable Host**: Supports custom Ollama servers via environment variable
4. **Temperature Control**: Fixed at 0 for reproducibility
5. **Token Limit**: Uses `num_predict` option to limit output tokens

### Integration with LLMJudge

The `LLMJudge` class now accepts a `provider` parameter:

```python
def __init__(self, ..., provider: str = "openai"):
    self.provider = self._get_provider(provider)

def _get_provider(self, provider_name: str):
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "ollama": OllamaProvider,  # New
    }
    return providers[provider_name.lower()]()
```

## Performance Considerations

### Local Model Advantages

- **No Rate Limits**: Process unlimited tokens per minute
- **No API Costs**: Free inference on your hardware
- **Privacy**: Data never leaves your machine
- **Offline**: No internet required

### Local Model Considerations

- **Hardware**: Requires adequate RAM/VRAM for model size
- **Speed**: Depends on your hardware (GPU recommended)
- **Model Selection**: Choose models appropriate for your hardware
  - 7B models: ~8GB RAM minimum
  - 13-14B models: ~16GB RAM minimum
  - 70B+ models: Require high-end hardware or quantization

### Recommended Models for Context Rot Experiments

| Model | Size | Context Length | Use Case |
|-------|------|----------------|----------|
| llama3.1:8b | ~8GB | 128K | Testing, general tasks |
| qwen2.5:14b | ~14GB | 128K | Judging, complex tasks |
| mistral:7b | ~7GB | 32K | Fast testing |
| codellama:13b | ~13GB | 16K | Code-related experiments |

## Backward Compatibility

All changes are fully backward compatible:

- Existing experiments work without modification
- `LLMJudge` defaults to OpenAI provider
- No changes to `BaseProvider` interface
- Other providers (OpenAI, Anthropic, Google) unchanged

## Testing

Run the test suite to verify installation:

```bash
# Comprehensive test suite
python tests/test_ollama_provider.py

# Expected output:
# ✓ Client initialization
# ✓ Single prompt processing
# ✓ Batch CSV processing
# 🎉 All tests passed!
```

## Future Enhancements

Potential future improvements:

1. **Streaming Support**: Add streaming responses for long outputs
2. **Batch Optimization**: Parallel processing for multi-GPU setups
3. **Model Management**: Automatic model pulling if not available
4. **Context Window Detection**: Auto-detect model context limits
5. **Quantization Options**: Support for different quantization levels

## Troubleshooting

### Common Issues

**Issue**: "Connection refused" error
```
Solution: Ensure Ollama is running (ollama serve)
```

**Issue**: "Model not found"
```
Solution: Pull the model first (ollama pull model-name)
```

**Issue**: "Out of memory"
```
Solution: Use a smaller model or increase system RAM
```

**Issue**: Slow inference
```
Solution:
- Use GPU if available
- Use quantized models
- Reduce max_output_tokens
```

## Academic Use Cases

This integration is particularly valuable for:

1. **Reproducibility**: Local models ensure consistent results
2. **Accessibility**: No API keys or costs required
3. **Privacy**: Sensitive data stays local
4. **Customization**: Fine-tune models for specific tasks
5. **Comparison Studies**: Compare API vs local models

## References

- [Ollama Official Website](https://ollama.ai)
- [Ollama Python Library](https://github.com/ollama/ollama-python)
- [Context Rot Technical Report](https://research.trychroma.com/context-rot)

## License

This integration maintains the same license as the original Context Rot repository.

## Contributing

To contribute improvements to the Ollama integration:

1. Test changes with multiple models
2. Ensure backward compatibility
3. Update documentation
4. Add tests for new features
5. Follow existing code style

---

**Version**: 1.0
**Date**: 2025-12-02
**Status**: Ready for academic experimentation
