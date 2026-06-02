import pytest
from defensive_skills.skill_models import SkillInput, DetectionResult, DefenseResult


class TestSkillInput:
    def test_default_values(self):
        inp = SkillInput(
            original_prompt="hello",
            normalized_prompt="hello",
            attack_category="direct_request",
            policy_action="ALLOW",
        )
        assert inp.original_prompt == "hello"
        assert inp.normalized_prompt == "hello"
        assert inp.attack_category == "direct_request"
        assert inp.policy_action == "ALLOW"
        assert inp.risk_score == 0
        assert inp.protected_assets == []
        assert inp.session_context == {}
        assert inp.user_role is None
        assert inp.metadata == {}

    def test_with_all_fields(self):
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="encoding_bypass",
            policy_action="RESTRICT",
            risk_score=85,
            protected_assets=[{"name": "flag"}],
            session_context={"turn": 3},
            user_role="user",
            metadata={"source": "web"},
        )
        assert inp.risk_score == 85
        assert inp.protected_assets == [{"name": "flag"}]
        assert inp.session_context == {"turn": 3}
        assert inp.user_role == "user"
        assert inp.metadata == {"source": "web"}


class TestDetectionResult:
    def test_default_values(self):
        r = DetectionResult(matched=False)
        assert r.matched is False
        assert r.confidence == 0.0
        assert r.matched_rules == []
        assert r.matched_assets == []
        assert r.reasons == []
        assert r.risk_tags == []

    def test_matched_true(self):
        r = DetectionResult(
            matched=True,
            confidence=0.95,
            matched_rules=["direct_secret_request"],
            matched_assets=["flag"],
            reasons=["user asked for secret directly"],
            risk_tags=["direct_secret_request"],
        )
        assert r.matched is True
        assert r.confidence == 0.95
        assert "direct_secret_request" in r.matched_rules
        assert "flag" in r.matched_assets
        assert len(r.reasons) == 1
        assert "direct_secret_request" in r.risk_tags


class TestDefenseResult:
    def test_default_values(self):
        r = DefenseResult(action="ALLOW")
        assert r.action == "ALLOW"
        assert r.safe_prompt is None
        assert r.response_message is None
        assert r.restrictions == []
        assert r.risk_tags == []
        assert r.runtime_checks == []
        assert r.evidence == {}

    def test_full_result(self):
        r = DefenseResult(
            action="BLOCK",
            safe_prompt="blocked",
            response_message="Access denied",
            restrictions=["no_secret_output"],
            risk_tags=["direct_secret_request"],
            runtime_checks=["exact_secret_check"],
            evidence={"skill_name": "DirectRequestSkill", "matched_rules": ["direct_secret_request"]},
        )
        assert r.action == "BLOCK"
        assert r.safe_prompt == "blocked"
        assert r.response_message == "Access denied"
        assert "no_secret_output" in r.restrictions
        assert r.evidence["skill_name"] == "DirectRequestSkill"
