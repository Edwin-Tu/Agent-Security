from typing import Callable, Generator
from .ollama_client import OllamaClient
from .model_response import LLMResponse, LLMChunk
from .model_config import ModelOptions


class LLMGateway:
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def generate(
        self,
        safe_prompt: str,
        model: str,
        options: ModelOptions | None = None,
    ) -> LLMResponse:
        if not safe_prompt:
            raise ValueError("safe_prompt is required")
        return self.client.generate(safe_prompt, model, options)

    def stream_generate(
        self,
        safe_prompt: str,
        model: str,
        options: ModelOptions | None = None,
        should_stop: Callable[[LLMChunk], bool] | None = None,
    ) -> Generator[LLMChunk, None, None]:
        if not safe_prompt:
            raise ValueError("safe_prompt is required")
        yield from self.client.stream_generate(safe_prompt, model, options, should_stop)
