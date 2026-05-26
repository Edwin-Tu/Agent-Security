"""Ollama connector interface for SecretGuard."""

from __future__ import annotations


class OllamaConnector:
    """A lightweight interface for local Ollama-compatible inference."""

    def __init__(self, host: str = "http://localhost:11434", model: str = "qwen2.5"):
        self.host = host
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        """Return a placeholder result for local-model generation.

        The actual Ollama integration can be added later. This method is intentionally
        lightweight so the guardrail package remains importable even without extra
        dependencies installed.
        """
        return (
            f"[placeholder] model={self.model} host={self.host} prompt={prompt[:80]}"
            + ("..." if len(prompt) > 80 else "")
        )

    def is_available(self) -> bool:
        """Return True when a local Ollama endpoint is expected to be reachable.

        This is a placeholder check; replace it with an HTTP probe when integrating
        with an actual Ollama deployment.
        """
        return True
