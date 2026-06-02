from typing import Generator


class ProviderError(Exception):
    pass


class BaseLLMProvider:
    def list_models(self) -> list[dict]:
        raise NotImplementedError

    def generate(self, model: str, prompt: str, options: dict | None = None) -> str:
        raise NotImplementedError

    def stream_generate(self, model: str, prompt: str, options: dict | None = None) -> Generator[str, None, None]:
        raise NotImplementedError
        yield  # pragma: no cover
