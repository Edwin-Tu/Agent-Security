from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def make_context(action_score: int) -> PolicyContext:
    return PolicyContext(
        normalized_prompt="prompt",
        attack_category="direct_secret_request",
        risk_score=action_score,
        risk_level="high",
        matched_assets=[{"asset_id": "secret_001", "risk_level": "high", "allowed_roles": ["owner"]}],
        user_role="guest",
        is_authorized=False,
        session_risk_score=0,
        input_guard_flags=[],
        classifier_confidence=0.9,
        history_flags=[],
    )


def test_restrict_block_authorize_generate_prompt_constraints():
    engine = DefensePolicyEngine()
    for risk_score in (50, 65, 85):
        decision = engine.decide(make_context(risk_score))
        assert isinstance(decision.prompt_constraints, list)
        if decision.action in (PolicyAction.REWRITE, PolicyAction.RESTRICT, PolicyAction.BLOCK, PolicyAction.AUTHORIZE, PolicyAction.ESCALATE):
            assert any("protect" in c.lower() or "secret" in c.lower() for c in decision.prompt_constraints)
