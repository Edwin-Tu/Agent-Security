import pytest
from unittest.mock import patch, MagicMock
from llm_gateway.ollama_client import OllamaClient
from llm_gateway.model_response import LLMResponse
from llm_gateway.model_config import ModelOptions


class TestOllamaClientGenerate:

    def test_generate_returns_llm_response(self):
        client = OllamaClient()
        fake_response = {
            "model": "mistral:latest",
            "response": "Hello world",
            "done": True,
            "prompt_eval_count": 10,
            "eval_count": 20,
            "total_duration": 1000000000,
        }
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = fake_response
            mock_post.return_value = mock_resp
            result = client.generate("safe prompt", "mistral:latest")
        assert isinstance(result, LLMResponse)
        assert result.success is True
        assert result.text == "Hello world"
        assert result.model == "mistral:latest"

    def test_generate_uses_safe_prompt(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {
                "model": "mistral:latest",
                "response": "output",
                "done": True,
            }
            mock_post.return_value = mock_resp
            client.generate("safe prompt", "mistral:latest")
            call_kwargs = mock_post.call_args[1]
            sent_payload = call_kwargs["json"]
            assert sent_payload["prompt"] == "safe prompt"

    def test_generate_with_invalid_model_returns_model_not_found(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_resp.raise_for_status.side_effect = Exception("Model not found")
            mock_post.return_value = mock_resp
            result = client.generate("safe prompt", "nonexistent:latest")
        assert result.success is False
        assert result.error_type == "model_not_found"

    def test_generate_timeout_returns_timeout_error(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_post.side_effect = TimeoutError("Request timed out")
            result = client.generate("safe prompt", "mistral:latest")
        assert result.success is False
        assert result.error_type == "timeout"

    def test_generate_does_not_log_raw_secret_in_error(self):
        client = OllamaClient()
        secret = "my-secret-api-key-12345"
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("some error")
            result = client.generate(secret, "mistral:latest")
        assert result.error_message is None or secret not in str(result.error_message)
