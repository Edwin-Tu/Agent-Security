import pytest
from event_logger.event_summary import EventSummary


class TestEventSummary:

    @pytest.fixture
    def events(self):
        return [
            {"attack_type": "direct_request", "policy_action": "BLOCK", "blocked": True, "leakage_detected": False, "risk_score": 95, "enabled_skills": ["skill_a"]},
            {"attack_type": "jailbreak", "policy_action": "BLOCK", "blocked": True, "leakage_detected": False, "risk_score": 80, "enabled_skills": ["skill_b"]},
            {"attack_type": "safe", "policy_action": "ALLOW", "blocked": False, "leakage_detected": False, "risk_score": 0, "enabled_skills": []},
            {"attack_type": "leakage", "policy_action": "REDACT", "blocked": False, "leakage_detected": True, "risk_score": 60, "enabled_skills": ["skill_a", "skill_c"]},
            {"attack_type": "direct_request", "policy_action": "WARN", "blocked": False, "leakage_detected": False, "risk_score": 30, "enabled_skills": ["skill_a"]},
        ]

    def test_total_events_count(self, events):
        summary = EventSummary(events).build()
        assert summary["total_events"] == 5

    def test_block_count(self, events):
        summary = EventSummary(events).build()
        assert summary["block_count"] == 2

    def test_leakage_count(self, events):
        summary = EventSummary(events).build()
        assert summary["leakage_count"] == 1

    def test_highest_risk_score(self, events):
        summary = EventSummary(events).build()
        assert summary["highest_risk_score"] == 95

    def test_average_risk_score(self, events):
        summary = EventSummary(events).build()
        assert summary["average_risk_score"] == 53.0

    def test_most_common_attack_type(self, events):
        summary = EventSummary(events).build()
        assert summary["most_common_attack_type"] == "direct_request"

    def test_most_common_policy_action(self, events):
        summary = EventSummary(events).build()
        assert summary["most_common_policy_action"] == "BLOCK"

    def test_most_common_enabled_skill(self, events):
        summary = EventSummary(events).build()
        assert summary["most_common_enabled_skill"] == "skill_a"

    def test_empty_events_returns_sensible_defaults(self):
        summary = EventSummary([]).build()
        assert summary["total_events"] == 0
        assert summary["highest_risk_score"] == 0
        assert summary["average_risk_score"] == 0.0
