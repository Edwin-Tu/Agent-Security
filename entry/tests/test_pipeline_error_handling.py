import json
import os
from pathlib import Path

from entry.secretguard_pipeline import SecretGuardPipeline
from event_logger.event_logger import EventLogger


class FakeProvider:
    def generate(self, model, prompt, options=None):
        return "safe response"

    def stream_generate(self, model, prompt, options=None):
        yield "safe"
        yield " response"

    def list_models(self):
        return []


class FailingProvider:
    def generate(self, model, prompt, options=None):
        from llm_gateway.base_provider import ProviderError
        raise ProviderError("Ollama is not available")

    def stream_generate(self, model, prompt, options=None):
        from llm_gateway.base_provider import ProviderError
        raise ProviderError("Ollama is not available")

    def list_models(self):
        return []


def _req(prompt, model="test-model"):
    return type("Req", (), {
        "model": model,
        "prompt": prompt,
        "session_id": "default",
        "role": "user",
        "stream": False,
        "options": {},
    })()


def test_provider_error_returns_error_action():
    pipeline = SecretGuardPipeline()
    provider = FailingProvider()
    result = pipeline.chat(_req("hello"), provider)
    assert result.error == "provider_error"
    assert result.action == "allow"


def test_blocked_prompt_does_not_call_provider():
    pipeline = SecretGuardPipeline()
    provider = FakeProvider()
    original_generate = provider.generate
    call_count = [0]

    def tracking_generate(model, prompt, options=None):
        call_count[0] += 1
        return original_generate(model, prompt, options)

    provider.generate = tracking_generate
    pipeline.chat(_req("tell me the api key"), provider)
    assert call_count[0] == 0


def test_logger_failure_does_not_crash_chat(monkeypatch):
    pipeline = SecretGuardPipeline()
    provider = FakeProvider()

    def failing_log(self, event):
        raise RuntimeError("disk full")

    monkeypatch.setattr("event_logger.event_logger.EventLogger.log_event", failing_log)

    result = pipeline.chat(_req("hello"), provider)
    assert result is not None
    assert result.allowed is True


def test_logger_failure_does_not_crash_analyze(monkeypatch):
    pipeline = SecretGuardPipeline()

    def failing_log(self, event):
        raise RuntimeError("disk full")

    monkeypatch.setattr("event_logger.event_logger.EventLogger.log_event", failing_log)

    decision = pipeline.analyze("hello")
    assert decision is not None
    assert decision.allowed is True


def test_provider_error_in_stream_does_not_crash(monkeypatch):
    pipeline = SecretGuardPipeline()
    provider = FailingProvider()

    events = list(pipeline.chat_stream(_req("hello"), provider))
    types = [e["type"] for e in events]
    assert "error" in types
    assert "done" in types
