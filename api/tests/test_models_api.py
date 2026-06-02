from fastapi.testclient import TestClient

from api.server import app

client = TestClient(app)


def test_models_returns_list_when_ollama_available(monkeypatch):
    def mock_list_models(self):
        return [{"name": "qwen2.5-coder:7b"}]

    monkeypatch.setattr("llm_gateway.ollama_provider.OllamaProvider.list_models", mock_list_models)

    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert len(data["models"]) == 1
    assert data["models"][0]["name"] == "qwen2.5-coder:7b"
    assert data["error"] is None


def test_models_returns_error_when_ollama_unavailable(monkeypatch):
    from llm_gateway.base_provider import ProviderError

    def mock_list_models(self):
        raise ProviderError("Ollama is not available")

    monkeypatch.setattr("llm_gateway.ollama_provider.OllamaProvider.list_models", mock_list_models)

    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["provider"] == "ollama"
    assert len(data["models"]) == 1
    assert data["models"][0]["name"] == "qwen2.5-coder:7b"
    assert data["error"] is None


def test_models_returns_empty_when_ollama_fails_quietly(monkeypatch):
    def mock_list_models(self):
        return []

    monkeypatch.setattr("llm_gateway.ollama_provider.OllamaProvider.list_models", mock_list_models)

    response = client.get("/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert data["models"] == []
    assert data["error"] == "provider_error"
