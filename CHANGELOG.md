# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - Ollama Provider Support

- **Ollama Provider** ([experiments/models/providers/ollama.py](experiments/models/providers/ollama.py))
  - New provider for running experiments with local open-source models via Ollama
  - Supports any model available in Ollama (Llama, Qwen, Mistral, etc.)
  - Configurable via `OLLAMA_HOST` environment variable
  - No API key required for offline experimentation

- **LLM Judge Enhancement** ([experiments/models/llm_judge.py](experiments/models/llm_judge.py))
  - Added configurable provider support to `LLMJudge` class
  - Can now use Ollama models as judges via `provider="ollama"` parameter
  - Supports all existing providers: OpenAI, Anthropic, Google, and Ollama

- **Documentation**
  - Updated [experiments/models/README.md](experiments/models/README.md) with Ollama setup and usage instructions
  - Updated [README.md](README.md) with Ollama quick start guide
  - Added example script [examples/ollama_example.py](examples/ollama_example.py)
  - Added test suite [tests/test_ollama_provider.py](tests/test_ollama_provider.py)

- **Dependencies**
  - Added `ollama>=0.4.8` to [requirements.txt](requirements.txt)

### Use Cases

This extension enables:
1. **Offline Experimentation**: Run experiments without internet connectivity or API access
2. **Cost-Effective Testing**: No API costs for local model inference
3. **Academic Research**: Reproducible experiments with locally hosted models
4. **Model Comparison**: Test both API-based and local models in the same framework
5. **Local Judging**: Use open-source models for evaluation to reduce API costs

### Compatibility

- Fully backward compatible with existing experiments
- All original providers (OpenAI, Anthropic, Google) continue to work unchanged
- Existing experiment scripts require no modifications
