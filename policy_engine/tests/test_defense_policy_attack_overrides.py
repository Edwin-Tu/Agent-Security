from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def make_context(**kwargs) -> PolicyContext:
    defaults = {
        "normalized_prompt": "attack prompt",
        "attack_category": None,
        "risk_score": 50,
        "risk_level": "medium",
        "matched_assets": [],
        "user_role": "owner",
        "is_authorized": True,
        "session_risk_score": 0,
        "input_guard_flags": [],
        "classifier_confidence": 0.9,
        "history_flags": [],
    }
    defaults.update(kwargs)
    return PolicyContext(**defaults)


def test_system_prompt_extraction_blocks():
    decision = DefensePolicyEngine().decide(
        make_context(attack_category="system_prompt_extraction", risk_score=30)
    )
    assert decision.action == PolicyAction.BLOCK


def test_encoding_bypass_block_over_threshold():
    decision = DefensePolicyEngine().decide(
        make_context(attack_category="encoding_bypass", risk_score=70)
    )
    assert decision.action == PolicyAction.BLOCK


def test_encoding_bypass_restrict_below_threshold():
    decision = DefensePolicyEngine().decide(
        make_context(attack_category="encoding_bypass", risk_score=50)
    )
    assert decision.action == PolicyAction.RESTRICT


def test_direct_secret_request_blocks_when_matched_assets():
    decision = DefensePolicyEngine().decide(
        make_context(
            attack_category="direct_secret_request",
            matched_assets=[{"asset_id": "secret_001", "risk_level": "high"}],
            risk_score=50,
        )
    )
    assert decision.action == PolicyAction.BLOCK


def test_partial_disclosure_restricts_or_escalates():
    decision = DefensePolicyEngine().decide(
        make_context(attack_category="partial_disclosure", risk_score=40)
    )
    assert decision.action in (PolicyAction.RESTRICT, PolicyAction.ESCALATE)
    assert decision.should_restrict is True
