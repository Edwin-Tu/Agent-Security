import pytest
from pathlib import Path
from event_logger.event_writer import EventWriter
from event_logger.event_query import EventQuery


@pytest.fixture
def log_with_events(tmp_path):
    log_path = str(tmp_path / "events.jsonl")
    writer = EventWriter(log_path)
    events = [
        {"attack_type": "direct_request", "policy_action": "BLOCK", "blocked": True, "leakage_detected": False, "risk_level": "high"},
        {"attack_type": "jailbreak", "policy_action": "BLOCK", "blocked": True, "leakage_detected": False, "risk_level": "critical"},
        {"attack_type": "safe", "policy_action": "ALLOW", "blocked": False, "leakage_detected": False, "risk_level": "low"},
        {"attack_type": "leakage", "policy_action": "REDACT", "blocked": False, "leakage_detected": True, "risk_level": "medium"},
    ]
    for e in events:
        writer.write(e)
    return log_path


class TestEventQuery:

    def test_all_returns_all_events(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.all()
        assert len(events) == 4

    def test_latest_returns_n_events(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.latest(2)
        assert len(events) == 2

    def test_filter_by_attack_type(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.filter(attack_type="direct_request")
        assert len(events) == 1
        assert events[0]["attack_type"] == "direct_request"

    def test_filter_by_policy_action(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.filter(policy_action="BLOCK")
        assert len(events) == 2

    def test_filter_by_blocked(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.filter(blocked=True)
        assert len(events) == 2

    def test_filter_by_leakage_detected(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.filter(leakage_detected=True)
        assert len(events) == 1

    def test_filter_by_risk_level(self, log_with_events):
        query = EventQuery(log_with_events)
        events = query.filter(risk_level="low")
        assert len(events) == 1

    def test_empty_log_file_returns_empty_list(self, tmp_path):
        log_path = str(tmp_path / "empty.jsonl")
        Path(log_path).touch()
        query = EventQuery(log_path)
        events = query.all()
        assert events == []
