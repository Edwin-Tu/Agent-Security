import pytest
from unittest.mock import patch, MagicMock
from llm_gateway.ollama_client import OllamaClient
from llm_gateway.model_response import LLMChunk
from llm_gateway.model_config import ModelOptions


def _fake_stream_lines():
    lines = [
        b'{"model":"mistral:latest","response":"Hello","done":false}',
        b'{"model":"mistral:latest","response":" world","done":false}',
        b'{"model":"mistral:latest","response":"","done":true,"total_duration":1000000000}',
    ]
    for line in lines:
        yield line


class TestOllamaClientStream:

    def test_stream_generate_yields_chunks(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.iter_lines.return_value = _fake_stream_lines()
            mock_post.return_value = mock_resp
            chunks = list(client.stream_generate("safe prompt", "mistral:latest"))
        assert len(chunks) > 0
        assert all(isinstance(c, LLMChunk) for c in chunks)

    def test_stream_generate_chunk_is_standardized(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.iter_lines.return_value = _fake_stream_lines()
            mock_post.return_value = mock_resp
            chunks = list(client.stream_generate("safe prompt", "mistral:latest"))
        chunk = chunks[0]
        assert chunk.text == "Hello"
        assert chunk.model == "mistral:latest"
        assert chunk.done is False
        assert chunk.raw is not None

    def test_stream_generate_handles_done_chunk(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.iter_lines.return_value = _fake_stream_lines()
            mock_post.return_value = mock_resp
            chunks = list(client.stream_generate("safe prompt", "mistral:latest"))
        last_chunk = chunks[-1]
        assert last_chunk.done is True

    def test_stream_generate_can_be_interrupted(self):
        client = OllamaClient()
        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.iter_lines.return_value = _fake_stream_lines()
            mock_post.return_value = mock_resp
            chunks = list(client.stream_generate("safe prompt", "mistral:latest"))
        assert len(chunks) == 3

    def test_stream_generate_stops_when_should_stop_returns_true(self):
        client = OllamaClient()
        call_count = [0]

        def should_stop(chunk: LLMChunk) -> bool:
            call_count[0] += 1
            if "world" in chunk.text:
                return True
            return False

        with patch("requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.iter_lines.return_value = _fake_stream_lines()
            mock_post.return_value = mock_resp
            chunks = list(client.stream_generate("safe prompt", "mistral:latest", should_stop=should_stop))
        assert len(chunks) == 2
        assert chunks[-1].stopped_by_guard is True
