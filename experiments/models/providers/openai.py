import os
from openai import OpenAI
from typing import Any
from ..base_provider import BaseProvider

class OpenAIProvider(BaseProvider):
    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        response = self.client.chat.completions.create(
            model=model_name,
            temperature=0,
            max_completion_tokens=max_output_tokens,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        if response.choices and len(response.choices) > 0:
            if response.choices[0].message.content == "":
                print(response)
            return index, response.choices[0].message.content
        else:
            return index, "ERROR_NO_CONTENT"

    def get_client(self) -> Any:
        # 支援自定義 base_url（用於 vLLM 等）
        base_url = os.getenv("OPENAI_API_BASE")
        api_key = os.getenv("OPENAI_API_KEY", "dummy")

        if base_url:
            print(f"Using custom OpenAI-compatible API: {base_url}")
            return OpenAI(api_key=api_key, base_url=base_url)
        else:
            return OpenAI(api_key=api_key)
