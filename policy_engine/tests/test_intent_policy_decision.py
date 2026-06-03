from policy_engine.defense_policy_engine import DefensePolicyEngine
from policy_engine.policy_context import PolicyContext
from policy_engine.policy_action import PolicyAction


def make_context(**kwargs) -> PolicyContext:
    defaults = {
        "normalized_prompt": "test",
        "attack_category": None,
        "risk_score": 30,
        "risk_level": "low",
        "matched_assets": [],
        "user_role": "user",
        "is_authorized": False,
        "session_risk_score": 0,
        "input_guard_flags": [],
        "classifier_confidence": 0.8,
        "history_flags": [],
        "operation": None,
        "scope": None,
        "disclosure_mode": None,
        "asset_reference_type": None,
    }
    defaults.update(kwargs)
    return PolicyContext(**defaults)


class TestIntentPolicyDecision:
    def test_general_api_key_explanation_allowed(self):
        ctx = make_context(
            risk_score=20,
            risk_level="low",
            operation="EXPLAIN",
            scope="GENERAL_CONCEPT",
            disclosure_mode="NONE",
            asset_reference_type="asset_type_mention",
        )
        decision = DefensePolicyEngine().decide(ctx)
        assert decision.action in (PolicyAction.ALLOW, PolicyAction.WARN)

    def test_api_key_disclosure_blocked(self):
        ctx = make_context(
            risk_score=50,
            risk_level="medium",
            operation="DISCLOSE",
            scope="UNKNOWN_INTERNAL",
            disclosure_mode="FULL_VALUE",
            asset_reference_type="asset_type_mention",
        )
        decision = DefensePolicyEngine().decide(ctx)
        assert decision.action == PolicyAction.BLOCK

    def test_hidden_context_extraction_blocked(self):
        ctx = make_context(
            risk_score=50,
            risk_level="medium",
            operation="EXTRACT",
            scope="HIDDEN_CONTEXT",
            disclosure_mode="FULL_VALUE",
            asset_reference_type="asset_type_mention",
        )
        decision = DefensePolicyEngine().decide(ctx)
        assert decision.action == PolicyAction.BLOCK

    def test_partial_reconstruction_blocked(self):
        ctx = make_context(
            risk_score=50,
            risk_level="medium",
            operation="RECONSTRUCT",
            scope="UNKNOWN_INTERNAL",
            disclosure_mode="PARTIAL_VALUE",
            asset_reference_type="asset_type_mention",
        )
        decision = DefensePolicyEngine().decide(ctx)
        assert decision.action == PolicyAction.BLOCK

    def test_encoded_transform_blocked(self):
        ctx = make_context(
            risk_score=50,
            risk_level="medium",
            operation="TRANSFORM",
            scope="UNKNOWN_INTERNAL",
            disclosure_mode="ENCODED_VALUE",
            asset_reference_type="asset_type_mention",
        )
        decision = DefensePolicyEngine().decide(ctx)
        assert decision.action == PolicyAction.BLOCK

    def test_explain_with_actual_value_blocked(self):
        ctx = make_context(
            risk_score=50,
            risk_level="medium",
            operation="DISCLOSE",
            scope="UNKNOWN_INTERNAL",
            disclosure_mode="FULL_VALUE",
            asset_reference_type="asset_type_mention",
        )
        decision = DefensePolicyEngine().decide(ctx)
        assert decision.action == PolicyAction.BLOCK

    def test_bypass_pressure_escalates_action(self):
        ctx_low = make_context(
            risk_score=20,
            risk_level="low",
            operation="BYPASS",
        )
        decision_low = DefensePolicyEngine().decide(ctx_low)
        assert decision_low.action in (PolicyAction.RESTRICT, PolicyAction.BLOCK)
        assert decision_low.action != PolicyAction.ALLOW

        ctx_high = make_context(
            risk_score=70,
            risk_level="high",
            operation="BYPASS",
        )
        decision_high = DefensePolicyEngine().decide(ctx_high)
        assert decision_high.action == PolicyAction.BLOCK
