from collections.abc import Generator
from typing import Any


class ProviderError(Exception):
    """Raised when an LLM provider cannot complete a request."""


class BaseLLMProvider:
    def list_models(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def generate(
        self,
        model: str,
        prompt: str,
        options: dict[str, Any] | None = None,
    ) -> str:
        raise NotImplementedError

    def stream_generate(
        self,
        model: str,
        prompt: str,
        options: dict[str, Any] | None = None,
    ) -> Generator[str, None, None]:
        raise NotImplementedError
