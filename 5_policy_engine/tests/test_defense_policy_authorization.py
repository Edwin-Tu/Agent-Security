from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def build_context(**kwargs) -> PolicyContext:
    defaults = {
        "normalized_prompt": "ask for secret",
        "attack_category": "direct_secret_request",
        "risk_score": 60,
        "risk_level": "high",
        "matched_assets": [{"asset_id": "secret_001", "risk_level": "high", "allowed_roles": ["owner"]}],
        "user_role": "guest",
        "is_authorized": False,
        "session_risk_score": 0,
        "input_guard_flags": [],
        "classifier_confidence": 0.85,
        "history_flags": [],
    }
    defaults.update(kwargs)
    return PolicyContext(**defaults)


def test_unauthorized_guest_high_risk_asset_requests_authorization():
    decision = DefensePolicyEngine().decide(build_context(risk_score=60))
    assert decision.action == PolicyAction.AUTHORIZE


def test_unauthorized_guest_high_risk_asset_blocks_on_severe_risk():
    decision = DefensePolicyEngine().decide(build_context(risk_score=80))
    assert decision.action == PolicyAction.BLOCK


def test_authorized_owner_does_not_authorize():
    decision = DefensePolicyEngine().decide(
        build_context(user_role="owner", is_authorized=True, risk_score=40)
    )
    assert decision.action != PolicyAction.AUTHORIZE
