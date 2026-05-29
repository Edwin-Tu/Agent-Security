from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def build_context(risk_score: int, attack_category: str | None = None) -> PolicyContext:
    return PolicyContext(
        normalized_prompt="test prompt",
        attack_category=attack_category,
        risk_score=risk_score,
        risk_level="high" if risk_score >= 75 else "medium" if risk_score >= 40 else "low",
        matched_assets=[],
        user_role="owner",
        is_authorized=True,
        session_risk_score=0,
        input_guard_flags=[],
        classifier_confidence=0.8,
        history_flags=[],
    )


def test_threshold_allow_warn_rewrite_restrict_block_escalate():
    engine = DefensePolicyEngine()

    assert engine.decide(build_context(10)).action == PolicyAction.ALLOW
    assert engine.decide(build_context(30)).action == PolicyAction.WARN
    assert engine.decide(build_context(50)).action == PolicyAction.REWRITE
    assert engine.decide(build_context(65)).action == PolicyAction.RESTRICT
    assert engine.decide(build_context(85)).action == PolicyAction.BLOCK
    assert engine.decide(build_context(95)).action == PolicyAction.BLOCK


def test_threshold_escalate_flagged():
    decision = DefensePolicyEngine().decide(
        build_context(95),
        session_risk_score=0,
    )
    assert decision.should_escalate is True
    assert decision.action == PolicyAction.BLOCK
