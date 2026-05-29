import pytest
from event_logger.event_schema import GuardEvent


class TestEventSchema:

    def test_auto_generates_event_id(self):
        event = GuardEvent()
        assert event.event_id is not None
        assert len(event.event_id) > 0

    def test_auto_generates_timestamp(self):
        event = GuardEvent()
        assert event.timestamp is not None
        assert "T" in event.timestamp

    def test_risk_score_clamped_below_zero(self):
        event = GuardEvent(risk_score=-10)
        assert event.risk_score == 0

    def test_risk_score_clamped_above_100(self):
        event = GuardEvent(risk_score=150)
        assert event.risk_score == 100

    def test_enabled_skills_defaults_to_empty_list(self):
        event = GuardEvent()
        assert event.enabled_skills == []

    def test_metadata_defaults_to_empty_dict(self):
        event = GuardEvent()
        assert event.metadata == {}

    def test_to_dict_returns_valid_dict(self):
        event = GuardEvent(
            attack_type="test",
            risk_score=50,
            policy_action="BLOCK",
            blocked=True,
        )
        d = event.to_dict()
        assert d["attack_type"] == "test"
        assert d["risk_score"] == 50
        assert d["policy_action"] == "BLOCK"
        assert d["blocked"] is True

    def test_from_dict_creates_event(self):
        data = {
            "attack_type": "direct_secret_request",
            "risk_score": 95,
            "policy_action": "BLOCK",
            "blocked": True,
        }
        event = GuardEvent.from_dict(data)
        assert isinstance(event, GuardEvent)
        assert event.attack_type == "direct_secret_request"
        assert event.risk_score == 95
        assert event.blocked is True
