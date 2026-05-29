from policy_builder.policy_models import RequestProtectionPolicy, PolicyBuildInput
from policy_builder.policy_builder import PolicyBuilder, build_risk_level


def test_can_create_basic_request_protection_policy():
    policy = RequestProtectionPolicy(
        request_id="req_001",
        action="ALLOW",
        risk_score=10,
        risk_level="low",
        user_role="user",
        attack_category="benign",
    )
    assert policy.request_id == "req_001"
    assert policy.action == "ALLOW"
    assert policy.runtime_monitoring_enabled is True
    assert policy.output_verification_enabled is True


def test_risk_score_maps_to_risk_level():
    assert build_risk_level(0) == "low"
    assert build_risk_level(15) == "low"
    assert build_risk_level(29) == "low"
    assert build_risk_level(30) == "medium"
    assert build_risk_level(50) == "medium"
    assert build_risk_level(69) == "medium"
    assert build_risk_level(70) == "high"
    assert build_risk_level(100) == "high"


def test_allow_action_creates_basic_policy():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_002",
        original_prompt="What is security?",
        normalized_prompt="what is security",
        user_role="user",
        attack_category="benign",
        risk_score=10,
        policy_action="ALLOW",
        matched_assets=[],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    assert result.action == "ALLOW"
    assert result.risk_level == "low"
    assert result.output_verification_enabled is True
    assert result.runtime_monitoring_enabled is True
    assert result.require_authorization is False


def test_warn_action_keeps_output_verification():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_003",
        original_prompt="Tell me about passwords",
        normalized_prompt="tell me about passwords",
        user_role="user",
        attack_category="general_security_question",
        risk_score=35,
        policy_action="WARN",
        matched_assets=[],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    assert result.action == "WARN"
    assert result.risk_level == "medium"
    assert result.output_verification_enabled is True


def test_default_policy_has_output_verification_enabled():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_004",
        original_prompt="Hello",
        normalized_prompt="hello",
        user_role="user",
        attack_category="benign",
        risk_score=0,
        policy_action="ALLOW",
        matched_assets=[],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    assert result.output_verification_enabled is True
    assert result.verify_exact is True
