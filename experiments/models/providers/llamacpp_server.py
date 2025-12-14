import requests
from typing import Any
from ..base_provider import BaseProvider


class LlamaCppServerProvider(BaseProvider):
    """llama.cpp server provider (remote HTTP API)"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize llama.cpp server provider

        Args:
            base_url: llama.cpp server base URL
        """
        self.base_url = base_url.rstrip('/')
        super().__init__()

    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        """
        Process a single prompt using llama.cpp server API

        Args:
            prompt: Input prompt text
            model_name: Model name (not used, server loads one model)
            max_output_tokens: Maximum number of tokens to generate
            index: Index of the prompt in the batch

        Returns:
            Tuple of (index, response_text)
        """
        try:
            url = f"{self.base_url}/completion"

            payload = {
                "prompt": prompt,
                "n_predict": max_output_tokens,
                "temperature": 0.0,
                "top_p": 1.0,
                "stop": ["User:", "使用者:", "\n\n"],
            }

            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()

            result = response.json()

            if 'content' in result:
                return index, result['content'].strip()
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
        Get client instance (for llama.cpp server, we use requests directly)
        Returns the base URL as the "client"
        """
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            # llama.cpp server might not have /health, try / instead
            if response.status_code == 404:
                response = requests.get(self.base_url, timeout=5)
            response.raise_for_status()
            print(f"Successfully connected to llama.cpp server at {self.base_url}")
        except Exception as e:
            print(f"Warning: Could not connect to llama.cpp server at {self.base_url}: {e}")
            print("Make sure the server is running!")

        return self.base_url
