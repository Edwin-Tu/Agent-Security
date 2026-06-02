from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def make_context(**kwargs) -> PolicyContext:
    defaults = {
        "normalized_prompt": "escalation prompt",
        "attack_category": None,
        "risk_score": 30,
        "risk_level": "medium",
        "matched_assets": [],
        "user_role": "owner",
        "is_authorized": True,
        "session_risk_score": 0,
        "input_guard_flags": [],
        "classifier_confidence": 0.7,
        "history_flags": [],
    }
    defaults.update(kwargs)
    return PolicyContext(**defaults)


def test_session_risk_80_escalates():
    decision = DefensePolicyEngine().decide(make_context(session_risk_score=80))
    assert decision.action == PolicyAction.ESCALATE
    assert decision.should_escalate is True


def test_session_risk_95_blocks_and_escalates():
    decision = DefensePolicyEngine().decide(make_context(session_risk_score=95))
    assert decision.action == PolicyAction.BLOCK
    assert decision.should_escalate is True
