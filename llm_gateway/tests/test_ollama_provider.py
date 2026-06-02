import json

import httpx
import pytest
from llm_gateway.ollama_provider import OllamaProvider
from llm_gateway.base_provider import ProviderError


def _provider_with_handler(handler, base_url="http://test:11434"):
    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url=base_url, transport=transport)
    return OllamaProvider(base_url=base_url, client=client)


def test_list_models_parses_tags_response():
    def handler(request):
        return httpx.Response(
            200,
            json={
                "models": [
                    {"name": "qwen2.5-coder:7b", "modified_at": "2024-01-01", "size": 12345},
                    {"name": "llama3:8b", "modified_at": "2024-01-02", "size": 67890},
                ]
            },
        )

    provider = _provider_with_handler(handler)
    models = provider.list_models()
    assert len(models) == 2
    assert models[0]["name"] == "qwen2.5-coder:7b"
    assert models[1]["name"] == "llama3:8b"


def test_list_models_empty_on_no_models():
    def handler(request):
        return httpx.Response(200, json={"models": []})

    provider = _provider_with_handler(handler)
    models = provider.list_models()
    assert models == []


def test_generate_parses_response():
    def handler(request):
        return httpx.Response(
            200,
            json={"response": "Hello!", "model": "qwen2.5-coder:7b", "done": True},
        )

    provider = _provider_with_handler(handler)
    result = provider.generate("test prompt", "qwen2.5-coder:7b")
    assert result == "Hello!"


def test_generate_accepts_options():
    def handler(request):
        body = json.loads(request.read())
        assert body.get("options", {}).get("temperature") == 0.5
        return httpx.Response(
            200,
            json={"response": "ok", "model": "qwen2.5-coder:7b", "done": True},
        )

    provider = _provider_with_handler(handler)
    result = provider.generate("test", "qwen2.5-coder:7b", options={"temperature": 0.5})
    assert result == "ok"


def test_stream_generate_yields_chunks():
    chunks_data = [
        b'{"response":"Hello ","done":false}\n',
        b'{"response":"world!","done":false}\n',
        b'{"response":"","done":true}\n',
    ]

    def handler(request):
        return httpx.Response(200, content=b"".join(chunks_data))

    provider = _provider_with_handler(handler)
    results = list(provider.stream_generate("test", "qwen2.5-coder:7b"))
    assert results == ["Hello ", "world!"]


def test_connection_error_raises_provider_error():
    def handler(request):
        raise httpx.ConnectError("Connection refused")

    provider = _provider_with_handler(handler)
    with pytest.raises(ProviderError):
        provider.list_models()


def test_generate_connection_error_raises_provider_error():
    def handler(request):
        raise httpx.ConnectError("Connection refused")

    provider = _provider_with_handler(handler)
    with pytest.raises(ProviderError):
        provider.generate("test", "qwen2.5-coder:7b")


def test_http_error_raises_provider_error():
    def handler(request):
        return httpx.Response(500)

    provider = _provider_with_handler(handler)
    with pytest.raises(ProviderError):
        provider.generate("test", "qwen2.5-coder:7b")
