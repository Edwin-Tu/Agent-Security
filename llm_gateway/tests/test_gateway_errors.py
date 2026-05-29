import pytest
from llm_gateway.model_config import ModelOptions
from llm_gateway.errors import InvalidModelOptionsError


class TestGatewayErrors:

    def test_invalid_temperature_raises_error(self):
        with pytest.raises(InvalidModelOptionsError, match="temperature"):
            ModelOptions(temperature=-1)

    def test_invalid_top_p_raises_error(self):
        with pytest.raises(InvalidModelOptionsError, match="top_p"):
            ModelOptions(top_p=1.5)

    def test_invalid_num_ctx_raises_error(self):
        with pytest.raises(InvalidModelOptionsError, match="num_ctx"):
            ModelOptions(num_ctx=0)

    def test_invalid_num_predict_raises_error(self):
        with pytest.raises(InvalidModelOptionsError, match="num_predict"):
            ModelOptions(num_predict=-1)

    def test_invalid_timeout_raises_error(self):
        with pytest.raises(InvalidModelOptionsError, match="timeout_seconds"):
            ModelOptions(timeout_seconds=0)

    def test_error_response_does_not_expose_sensitive_prompt(self):
        from llm_gateway.ollama_client import OllamaClient
        client = OllamaClient()
        secret = "my-secret-token-abc123"
        from unittest.mock import patch, MagicMock
        with patch("requests.post") as mock_post:
            mock_post.side_effect = Exception("generic error without secret")
            result = client.generate(secret, "mistral:latest")
        assert result.error_type is not None
        assert secret not in str(result.error_message or "")
