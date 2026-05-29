import pytest
from unittest.mock import patch, MagicMock
from llm_gateway.ollama_client import OllamaClient
from llm_gateway.errors import OllamaConnectionError


class TestOllamaClientConnection:

    def test_check_connection_success(self):
        client = OllamaClient()
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp
            result = client.check_connection()
        assert result.success is True
        assert result.error_type is None

    def test_check_connection_failed_when_ollama_is_down(self):
        client = OllamaClient()
        with patch("requests.get") as mock_get:
            mock_get.side_effect = OllamaConnectionError("Connection refused")
            result = client.check_connection()
        assert result.success is False
        assert result.error_type == "connection_error"

    def test_connection_error_returns_safe_error(self):
        client = OllamaClient()
        with patch("requests.get") as mock_get:
            mock_get.side_effect = OllamaConnectionError("Connection refused")
            result = client.check_connection()
        assert result.success is False
        assert "Connection refused" not in str(result.error_message or "")
