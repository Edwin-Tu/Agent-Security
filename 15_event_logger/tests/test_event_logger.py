import pytest
import json
import os
from pathlib import Path
from event_logger.event_logger import EventLogger
from event_logger.event_schema import GuardEvent


class TestEventLogger:

    @pytest.fixture
    def tmp_log(self, tmp_path):
        return str(tmp_path / "guard_events.jsonl")

    def test_log_event_accepts_guard_event(self, tmp_log):
        logger = EventLogger(log_path=tmp_log)
        event = GuardEvent(attack_type="test", risk_score=50, policy_action="BLOCK", blocked=True)
        result = logger.log_event(event)
        assert isinstance(result, GuardEvent)
        assert Path(tmp_log).exists()

    def test_log_event_accepts_dict(self, tmp_log):
        logger = EventLogger(log_path=tmp_log)
        data = {"attack_type": "test", "risk_score": 50, "policy_action": "BLOCK", "blocked": True}
        result = logger.log_event(data)
        assert isinstance(result, GuardEvent)
        assert Path(tmp_log).exists()

    def test_log_event_calls_redaction(self, tmp_log):
        logger = EventLogger(log_path=tmp_log)
        data = {"attack_type": "test", "risk_score": 50, "policy_action": "ALLOW",
                "input_summary": "My key is sk-proj-123456789012345678901234567890"}
        logger.log_event(data)
        with open(tmp_log, "r") as f:
            line = f.readline()
        assert "sk-proj-123456789012345678901234567890" not in line

    def test_missing_non_required_fields_does_not_crash(self, tmp_log):
        logger = EventLogger(log_path=tmp_log)
        data = {"attack_type": "minimal_test"}
        event = logger.log_event(data)
        assert isinstance(event, GuardEvent)
        assert event.attack_type == "minimal_test"

    def test_log_file_exists_after_write(self, tmp_log):
        logger = EventLogger(log_path=tmp_log)
        logger.log_event({"attack_type": "test", "risk_score": 10, "policy_action": "ALLOW"})
        assert Path(tmp_log).exists()

    def test_logged_event_can_be_read_back(self, tmp_log):
        logger = EventLogger(log_path=tmp_log)
        logger.log_event({"attack_type": "readback_test", "risk_score": 30, "policy_action": "WARN"})
        with open(tmp_log, "r") as f:
            line = json.loads(f.readline())
        assert line["attack_type"] == "readback_test"
        assert line["risk_score"] == 30
