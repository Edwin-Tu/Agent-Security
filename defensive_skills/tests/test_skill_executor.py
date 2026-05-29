import pytest
from defensive_skills.skill_models import SkillInput, DetectionResult, DefenseResult
from defensive_skills.base_skill import BaseSkill
from defensive_skills.skill_executor import SkillExecutor


class _MatchSkill(BaseSkill):
    skill_name = "match_skill"
    attack_categories = ["test"]

    def detect(self, skill_input):
        return DetectionResult(
            matched=True,
            confidence=0.9,
            matched_rules=["test_rule"],
            risk_tags=["test_tag"],
        )

    def defend(self, skill_input, detection_result):
        return DefenseResult(
            action="BLOCK",
            safe_prompt="blocked",
            risk_tags=["test_tag"],
            runtime_checks=["test_check"],
            restrictions=["no_output"],
            evidence={"skill_name": "match_skill", "matched_rules": ["test_rule"]},
        )


class _AnotherMatchSkill(BaseSkill):
    skill_name = "another_match"
    attack_categories = ["test2"]

    def detect(self, skill_input):
        return DetectionResult(
            matched=True,
            confidence=0.8,
            matched_rules=["another_rule"],
            risk_tags=["another_tag"],
        )

    def defend(self, skill_input, detection_result):
        return DefenseResult(
            action="RESTRICT",
            safe_prompt="restricted",
            risk_tags=["another_tag"],
            runtime_checks=["another_check"],
            restrictions=["limited_output"],
            evidence={"skill_name": "another_match", "matched_rules": ["another_rule"]},
        )


class _NoMatchSkill(BaseSkill):
    skill_name = "no_match"
    attack_categories = ["safe"]

    def detect(self, skill_input):
        return DetectionResult(matched=False)

    def defend(self, skill_input, detection_result):
        return DefenseResult(action="ALLOW")


class _WarnSkill(BaseSkill):
    skill_name = "warn_skill"
    attack_categories = ["warn"]

    def detect(self, skill_input):
        return DetectionResult(matched=True, confidence=0.5, risk_tags=["warn_tag"])

    def defend(self, skill_input, detection_result):
        return DefenseResult(
            action="WARN",
            risk_tags=["warn_tag"],
            runtime_checks=["warn_check"],
            evidence={"skill_name": "warn_skill"},
        )


class TestSkillExecutor:
    def test_no_skill_matched_returns_allow(self):
        executor = SkillExecutor()
        no_match = _NoMatchSkill()
        inp = SkillInput(
            original_prompt="safe question",
            normalized_prompt="safe question",
            attack_category="safe",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [no_match])
        assert result.action == "ALLOW"

    def test_single_skill_matched(self):
        executor = SkillExecutor()
        match_skill = _MatchSkill()
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [match_skill])
        assert result.action == "BLOCK"
        assert result.evidence["match_skill"] is not None

    def test_multiple_skills_merge_evidence(self):
        executor = SkillExecutor()
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [_MatchSkill(), _AnotherMatchSkill()])
        assert "match_skill" in result.evidence
        assert "another_match" in result.evidence

    def test_multiple_skills_choose_highest_severity(self):
        executor = SkillExecutor()
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [_WarnSkill(), _MatchSkill()])
        assert result.action == "BLOCK"

    def test_runtime_checks_no_duplicate(self):
        executor = SkillExecutor()
        s1 = _MatchSkill()
        s2 = _AnotherMatchSkill()
        s2.runtime_checks = ["test_check"]
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [s1, s2])
        checks = result.runtime_checks
        assert len(checks) == len(set(checks))

    def test_risk_tags_no_duplicate(self):
        executor = SkillExecutor()
        s1 = _MatchSkill()
        s2 = _AnotherMatchSkill()
        s2.risk_tags = ["test_tag"]
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [s1, s2])
        tags = result.risk_tags
        assert len(tags) == len(set(tags))

    def test_restrictions_no_duplicate(self):
        executor = SkillExecutor()
        s1 = _MatchSkill()
        s2 = _AnotherMatchSkill()
        s2.restrictions = ["no_output"]
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [s1, s2])
        restrictions = result.restrictions
        assert len(restrictions) == len(set(restrictions))

    def test_mixed_match_and_no_match(self):
        executor = SkillExecutor()
        inp = SkillInput(
            original_prompt="test",
            normalized_prompt="test",
            attack_category="test",
            policy_action="ALLOW",
        )
        result = executor.execute(inp, [_NoMatchSkill(), _MatchSkill()])
        assert result.action == "BLOCK"
