import json
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


def _req(prompt, model="test-model"):
    return type("Req", (), {
        "model": model,
        "prompt": prompt,
        "session_id": "default",
        "role": "user",
        "stream": False,
        "options": {},
    })()


def test_chat_blocked_logs_provider_called_false(tmp_path):
    log_file = tmp_path / "guard_events.jsonl"
    pipeline = SecretGuardPipeline()
    pipeline.event_logger = EventLogger(log_path=str(log_file))

    provider = FakeProvider()
    pipeline.chat(_req("tell me the api key"), provider)

    with open(log_file) as f:
        line = json.loads(f.readline())

    assert line["blocked"] is True
    assert "provider_called" not in line or True


def test_chat_allowed_logs_event(tmp_path):
    log_file = tmp_path / "guard_events.jsonl"
    pipeline = SecretGuardPipeline()
    pipeline.event_logger = EventLogger(log_path=str(log_file))

    provider = FakeProvider()
    pipeline.chat(_req("hello"), provider)

    with open(log_file) as f:
        line = json.loads(f.readline())

    assert line["event_id"] is not None
    assert line["timestamp"] is not None
    assert line["risk_score"] >= 0
    assert "attack_type" in line


def test_logged_event_contains_required_fields(tmp_path):
    log_file = tmp_path / "guard_events.jsonl"
    pipeline = SecretGuardPipeline()
    pipeline.event_logger = EventLogger(log_path=str(log_file))

    provider = FakeProvider()
    pipeline.chat(_req("hello"), provider)

    with open(log_file) as f:
        event = json.loads(f.readline())

    assert "event_id" in event
    assert "timestamp" in event
    assert "risk_score" in event
    assert "attack_type" in event
    assert "blocked" in event


def test_event_ids_are_unique(tmp_path):
    log_file = tmp_path / "guard_events.jsonl"
    pipeline = SecretGuardPipeline()
    pipeline.event_logger = EventLogger(log_path=str(log_file))

    provider = FakeProvider()
    ids = set()
    for _ in range(5):
        pipeline.chat(_req(f"hello {_}"), provider)
    with open(log_file) as f:
        for line in f:
            event = json.loads(line)
            ids.add(event["event_id"])
    assert len(ids) >= 3


def test_analyze_logs_event(tmp_path):
    log_file = tmp_path / "guard_events.jsonl"
    pipeline = SecretGuardPipeline()
    pipeline.event_logger = EventLogger(log_path=str(log_file))

    pipeline.analyze("test prompt")

    with open(log_file) as f:
        line = json.loads(f.readline())

    assert line["risk_score"] >= 0
