from typing import Any
from ..base_provider import BaseProvider


class LlamaCppProvider(BaseProvider):
    """llama-cpp-python provider for GGUF models"""

    def __init__(self, model_path: str, n_ctx: int = 8192, n_gpu_layers: int = -1):
        """
        Initialize llama-cpp-python provider

        Args:
            model_path: Path to GGUF model file
            n_ctx: Context size (default: 8192)
            n_gpu_layers: Number of layers to offload to GPU (-1 = all, 0 = CPU only)
        """
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        super().__init__()

    def process_single_prompt(self, prompt: str, model_name: str, max_output_tokens: int, index: int) -> tuple[int, str]:
        """
        Process a single prompt using llama-cpp-python

        Args:
            prompt: Input prompt text
            model_name: Model name (not used, model already loaded)
            max_output_tokens: Maximum number of tokens to generate
            index: Index of the prompt in the batch

        Returns:
            Tuple of (index, response_text)
        """
        try:
            # Generate response
            response = self.client(
                prompt,
                max_tokens=max_output_tokens,
                temperature=0.0,
                top_p=1.0,
                echo=False,
                stop=["User:", "使用者:", "\n\n"],
            )

            if response and 'choices' in response and len(response['choices']) > 0:
                text = response['choices'][0]['text']
                return index, text.strip()
            else:
                return index, "ERROR_NO_CONTENT"

        except Exception as e:
            return index, f"ERROR_GENERATION: {str(e)}"

    def get_client(self) -> Any:
        """
        Load GGUF model using llama-cpp-python
        Returns the Llama instance
        """
        try:
            from llama_cpp import Llama

            print(f"Loading GGUF model from: {self.model_path}")
            print(f"Context size: {self.n_ctx}")
            print(f"GPU layers: {self.n_gpu_layers}")

            # Load model
            llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False,
            )

            print(f"Model loaded successfully")
            return llm

        except ImportError:
            print("Error: llama-cpp-python not installed")
            print("Install with: pip install llama-cpp-python")
            print("For GPU support: CMAKE_ARGS=\"-DLLAMA_CUDA=on\" pip install llama-cpp-python")
            raise
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
