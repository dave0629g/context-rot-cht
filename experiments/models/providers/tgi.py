import requests
from typing import Any
from ..base_provider import BaseProvider


class TGIProvider(BaseProvider):
    """Text Generation Inference (Hugging Face) provider"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize TGI provider

        Args:
            base_url: TGI server base URL
        """
        self.base_url = base_url.rstrip('/')
        super().__init__()

    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        """
        Process a single prompt using TGI API

        Args:
            prompt: Input prompt text
            model_name: Model name (not used, TGI loads one model)
            max_output_tokens: Maximum number of tokens to generate
            index: Index of the prompt in the batch

        Returns:
            Tuple of (index, response_text)
        """
        try:
            url = f"{self.base_url}/generate"

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_output_tokens,
                    "temperature": 0.0,
                    "do_sample": False,
                    "return_full_text": False,
                }
            }

            response = requests.post(url, json=payload, timeout=600)
            response.raise_for_status()

            result = response.json()

            if 'generated_text' in result:
                return index, result['generated_text']
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
        Get client instance (for TGI, we use requests directly)
        Returns the base URL as the "client"
        """
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            print(f"Successfully connected to TGI at {self.base_url}")
        except Exception as e:
            print(f"Warning: Could not connect to TGI at {self.base_url}: {e}")

        return self.base_url
