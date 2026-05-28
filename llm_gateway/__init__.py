# Stage 10: LLM Gateway - Unified LLM interface & Ollama client

from .ollama_client import OllamaClient
from .base_llm import BaseLLM

__all__ = [
    "OllamaClient", "BaseLLM",
]
