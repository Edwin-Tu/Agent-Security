from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def test_policy_decision_output_contains_all_fields():
    context = PolicyContext(
        normalized_prompt="test output",
        attack_category="direct_secret_request",
        risk_score=85,
        risk_level="high",
        matched_assets=[{"asset_id": "secret_001", "risk_level": "high", "allowed_roles": ["owner"]}],
        user_role="guest",
        is_authorized=False,
        session_risk_score=20,
        input_guard_flags=["sensitive_request"],
        classifier_confidence=0.95,
        history_flags=["partial_probe"],
    )
    decision = DefensePolicyEngine().decide(context)
    assert decision.action == PolicyAction.BLOCK
    assert decision.reason
    assert decision.risk_score == 85
    assert decision.risk_level == "high"
    assert isinstance(decision.monitoring_level, str)
    assert isinstance(decision.required_skills, list)
    assert isinstance(decision.prompt_constraints, list)
    assert isinstance(decision.should_block, bool)
    assert isinstance(decision.should_rewrite, bool)
    assert isinstance(decision.should_restrict, bool)
    assert isinstance(decision.should_escalate, bool)
    assert isinstance(decision.log_level, str)
