from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


SKILL_MAPPING = {
    "encoding_bypass": "encoding_bypass_skill",
    "multi_turn_probe": "multi_turn_probe_skill",
    "homoglyph_obfuscation": "homoglyph_obfuscation_skill",
}


def make_context(attack_category: str) -> PolicyContext:
    return PolicyContext(
        normalized_prompt="test",
        attack_category=attack_category,
        risk_score=50,
        risk_level="medium",
        matched_assets=[],
        user_role="owner",
        is_authorized=True,
        session_risk_score=0,
        input_guard_flags=[],
        classifier_confidence=0.8,
        history_flags=[],
    )


def test_required_skills_mapping_for_attack_categories():
    engine = DefensePolicyEngine()
    for category, expected_skill in SKILL_MAPPING.items():
        decision = engine.decide(make_context(category))
        assert expected_skill in decision.required_skills
