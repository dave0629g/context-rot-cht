import requests
from typing import Any
from ..base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama local service provider"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama provider

        Args:
            base_url: Ollama API base URL, default is http://localhost:11434
        """
        self.base_url = base_url.rstrip('/')
        super().__init__()

    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        """
        Process a single prompt using Ollama API

        Args:
            prompt: Input prompt text
            model_name: Model name (e.g., 'qwen3:0.6b')
            max_output_tokens: Maximum number of tokens to generate
            index: Index of the prompt in the batch

        Returns:
            Tuple of (index, response_text)
        """
        try:
            url = f"{self.base_url}/api/generate"

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": max_output_tokens,
                }
            }

            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()

            result = response.json()

            if 'response' in result:
                return index, result['response']
            else:
                return index, "ERROR_NO_CONTENT"

        except requests.exceptions.Timeout:
            return index, "ERROR_TIMEOUT: Request timeout"
        except requests.exceptions.RequestException as e:
            return index, f"ERROR_REQUEST: {str(e)}"
        except Exception as e:
            return index, f"ERROR_UNKNOWN: {str(e)}"

    def get_client(self) -> Any:
        """
        Get client instance (for Ollama, we use requests directly)
        Returns the base URL as the "client"
        """
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            print(f"Successfully connected to Ollama at {self.base_url}")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama at {self.base_url}: {e}")

        return self.base_url
