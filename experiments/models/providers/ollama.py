import os
from ollama import Client
from typing import Any
from ..base_provider import BaseProvider

class OllamaProvider(BaseProvider):
    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        try:
            response = self.client.chat(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0,
                    "num_predict": max_output_tokens,
                }
            )

            if response and 'message' in response and 'content' in response['message']:
                content = response['message']['content']
                if content == "":
                    print(f"WARNING: Empty content received for index {index}")
                    print(response)
                return index, content
            else:
                return index, "ERROR_NO_CONTENT"
        except Exception as e:
            return index, f"ERROR: {str(e)}"

    def get_client(self) -> Any:
        # Allow custom Ollama host via environment variable, default to localhost
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return Client(host=ollama_host)
