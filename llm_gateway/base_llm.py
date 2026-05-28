from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> dict:
        pass

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: str = "") -> str:
        pass

    @abstractmethod
    def list_models(self) -> list[str]:
        pass
