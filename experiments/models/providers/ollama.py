import requests
from typing import Any
from ..base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama local service provider"""

    def __init__(self, base_url: str = "http://localhost:11434", num_ctx: int | None = None):
        """
        Initialize Ollama provider

        Args:
            base_url: Ollama API base URL, default is http://localhost:11434
            num_ctx: Optional context window override for Ollama (options.num_ctx)
        """
        self.base_url = base_url.rstrip('/')
        self.num_ctx = num_ctx
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

            options: dict[str, Any] = {
                "temperature": 0,
                "num_predict": max_output_tokens,
            }
            # If provided, set Ollama context window explicitly.
            # This is important when prompts are long; otherwise Ollama may use a smaller default.
            if self.num_ctx is not None:
                options["num_ctx"] = int(self.num_ctx)

            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": options,
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
        except requests.exceptions.HTTPError as e:
            r = getattr(e, "response", None)
            status_code = getattr(r, "status_code", None)
            reason = getattr(r, "reason", "")

            # Best-effort parse error body (Ollama often returns JSON like {"error":"model 'x' not found"})
            error_text = None
            try:
                if r is not None:
                    body = r.json()
                    if isinstance(body, dict) and "error" in body:
                        error_text = str(body["error"])
                    else:
                        error_text = str(body)
            except Exception:
                try:
                    if r is not None:
                        error_text = (r.text or "").strip()
                except Exception:
                    error_text = None

            # If model not found, include local available models to help debug quickly
            if status_code == 404 and error_text and "not found" in error_text and "model" in error_text:
                available_models: list[str] = []
                try:
                    tags = requests.get(f"{self.base_url}/api/tags", timeout=10).json()
                    available_models = [m.get("name") for m in tags.get("models", []) if m.get("name")]
                except Exception:
                    available_models = []

                msg = f"ERROR_REQUEST: {status_code} {reason} - {error_text}"
                if available_models:
                    preview = ", ".join(available_models[:20])
                    suffix = "..." if len(available_models) > 20 else ""
                    msg += f" (local models: {preview}{suffix})"
                return index, msg

            if status_code is not None:
                if error_text:
                    return index, f"ERROR_REQUEST: {status_code} {reason} - {error_text}"
                return index, f"ERROR_REQUEST: {status_code} {reason}"
            return index, f"ERROR_REQUEST: {str(e)}"
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
