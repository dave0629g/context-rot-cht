from typing import Any
from ..base_provider import BaseProvider


class HuggingFaceProvider(BaseProvider):
    """Hugging Face Transformers provider for local models"""

    def __init__(self, model_name: str = "yentinglin/Taiwan-LLM-7B-v2.1-chat", device: str = "auto"):
        """
        Initialize Hugging Face provider

        Args:
            model_name: Hugging Face model ID
            device: Device to run on ('cuda', 'cpu', or 'auto')
        """
        self.model_name = model_name
        self.device = device
        super().__init__()

    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        """
        Process a single prompt using Hugging Face Transformers

        Args:
            prompt: Input prompt text
            model_name: Model name (overrides init model_name)
            max_output_tokens: Maximum number of tokens to generate
            index: Index of the prompt in the batch

        Returns:
            Tuple of (index, response_text)
        """
        try:
            # Generate response
            response = self.pipeline(
                prompt,
                max_new_tokens=max_output_tokens,
                temperature=0,
                do_sample=False,
                return_full_text=False,
            )

            if response and len(response) > 0:
                return index, response[0]['generated_text']
            else:
                return index, "ERROR_NO_CONTENT"

        except Exception as e:
            return index, f"ERROR_GENERATION: {str(e)}"

    def get_client(self) -> Any:
        """
        Get pipeline instance (loads the model)
        Returns the Hugging Face pipeline
        """
        try:
            from transformers import pipeline
            import torch

            print(f"Loading Hugging Face model: {self.model_name}")
            print(f"Device: {self.device}")

            # Determine device
            if self.device == "auto":
                device = 0 if torch.cuda.is_available() else -1
            elif self.device == "cuda":
                device = 0
            else:
                device = -1

            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=self.model_name,
                device=device,
                torch_dtype=torch.float16 if device >= 0 else torch.float32,
            )

            print(f"Model loaded successfully on device: {device}")
            return pipe

        except Exception as e:
            print(f"Error loading model: {e}")
            raise
