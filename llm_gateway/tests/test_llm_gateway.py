import pytest
from unittest.mock import patch, MagicMock
from llm_gateway.gateway import LLMGateway
from llm_gateway.ollama_client import OllamaClient
from llm_gateway.model_response import LLMResponse, LLMChunk
from llm_gateway.model_config import ModelOptions


class TestLLMGateway:

    def test_gateway_generate_delegates_to_ollama_client(self):
        gateway = LLMGateway()
        gateway.client = MagicMock(spec=OllamaClient)
        gateway.client.generate.return_value = LLMResponse(
            success=True, text="Hello", model="mistral:latest", done=True
        )
        result = gateway.generate("safe_prompt", "mistral:latest")
        gateway.client.generate.assert_called_once_with("safe_prompt", "mistral:latest", None)
        assert result.text == "Hello"

    def test_gateway_stream_delegates_to_ollama_client(self):
        gateway = LLMGateway()
        gateway.client = MagicMock(spec=OllamaClient)
        fake_chunks = [
            LLMChunk(text="Hello", model="mistral:latest", done=False),
            LLMChunk(text=" world", model="mistral:latest", done=True),
        ]
        gateway.client.stream_generate.return_value = fake_chunks
        result = list(gateway.stream_generate("safe_prompt", "mistral:latest"))
        gateway.client.stream_generate.assert_called_once_with(
            "safe_prompt", "mistral:latest", None, None
        )
        assert len(result) == 2

    def test_gateway_requires_safe_prompt(self):
        gateway = LLMGateway()
        with pytest.raises(ValueError, match="safe_prompt"):
            gateway.generate("", "mistral:latest")

    def test_gateway_returns_standard_response(self):
        gateway = LLMGateway()
        gateway.client = MagicMock(spec=OllamaClient)
        gateway.client.generate.return_value = LLMResponse(
            success=True, text="output", model="mistral:latest", done=True
        )
        result = gateway.generate("safe", "mistral:latest")
        assert isinstance(result, LLMResponse)

    def test_gateway_preserves_metadata(self):
        gateway = LLMGateway()
        gateway.client = MagicMock(spec=OllamaClient)
        gateway.client.generate.return_value = LLMResponse(
            success=True,
            text="output",
            model="mistral:latest",
            done=True,
            prompt_tokens=10,
            completion_tokens=20,
            total_duration_ms=1500,
        )
        result = gateway.generate("safe", "mistral:latest")
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.total_duration_ms == 1500
