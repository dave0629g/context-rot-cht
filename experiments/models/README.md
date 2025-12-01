# Models

We support OpenAI, Anthropic, Google, and Ollama providers. While Qwen is included in our evaluation results, we don't provide a Qwen implementation due to the specificity in custom deployments.

## File Structure

```
models/
├── README.md
├── base_provider.py          # Abstract base class for all providers
├── llm_judge.py             # LLM judge for evaluation
└── providers/
    ├── openai.py            # OpenAI provider implementation
    ├── anthropic.py         # Anthropic provider implementation
    ├── google.py            # Google provider implementation
    └── ollama.py            # Ollama provider implementation (local models)
```

## Environment Variables

- **OpenAI**: `OPENAI_API_KEY`
- **Anthropic**: `ANTHROPIC_API_KEY`
- **Google**: `GOOGLE_APPLICATION_CREDENTIALS` and `GOOGLE_MODEL_PATH`
- **Ollama**: `OLLAMA_HOST` (optional, defaults to `http://localhost:11434`)

## Ollama Provider

The Ollama provider enables running experiments with local open-source models. This is particularly useful for:
- Offline experimentation
- Cost-effective testing at scale
- Academic research with reproducible local models
- Using Ollama models as LLM judges

### Setup

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the models you want to use:
   ```bash
   ollama pull llama3.1:8b
   ollama pull qwen2.5:14b
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```

### Usage

Use the Ollama provider just like other providers, specifying the model name from your local Ollama installation:

```python
from models.providers.ollama import OllamaProvider

provider = OllamaProvider()
provider.main(
    input_path="input.csv",
    output_path="output.csv",
    input_column="prompt",
    output_column="response",
    model_name="llama3.1:8b",  # Use any Ollama model
    max_context_length=128000,
    max_tokens_per_minute=1000000  # No rate limits for local models
)
```

### Using Ollama as LLM Judge

You can use Ollama models for evaluation:

```python
from models.llm_judge import LLMJudge

judge = LLMJudge(
    prompt=your_judge_prompt,
    model_name="qwen2.5:14b",
    provider="ollama"  # Specify Ollama provider
)
judge.evaluate(
    input_path="results.csv",
    output_path="judged_results.csv",
    max_context_length=128000,
    max_tokens_per_minute=1000000
)
```

## Adding New Providers

To add a new provider, inherit from `BaseProvider` and implement:
- `process_single_prompt()`: Process a single prompt
- `get_client()`: Initialize API client