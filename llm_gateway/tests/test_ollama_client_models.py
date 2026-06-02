import pytest
from unittest.mock import patch, MagicMock
from llm_gateway.ollama_client import OllamaClient
from llm_gateway.model_response import OllamaModelInfo


class TestOllamaClientModels:

    def test_list_models_returns_model_info(self):
        client = OllamaClient()
        fake_response = {
            "models": [
                {"name": "mistral:latest", "modified_at": "2024-01-01", "size": 4100000000},
                {"name": "llama2:latest", "modified_at": "2024-01-02", "size": 3800000000},
            ]
        }
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = fake_response
            mock_get.return_value = mock_resp
            models = client.list_models()
        assert len(models) == 2
        assert all(isinstance(m, OllamaModelInfo) for m in models)
        assert models[0].name == "mistral:latest"
        assert models[1].name == "llama2:latest"

    def test_list_models_handles_empty_model_list(self):
        client = OllamaClient()
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"models": []}
            mock_get.return_value = mock_resp
            models = client.list_models()
        assert models == []

    def test_list_models_handles_invalid_response(self):
        client = OllamaClient()
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Unexpected error")
            models = client.list_models()
        assert models == []
