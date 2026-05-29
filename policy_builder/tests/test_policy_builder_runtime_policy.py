from policy_builder.policy_models import PolicyBuildInput
from policy_builder.policy_builder import PolicyBuilder
from policy_builder.runtime_policy_builder import build_runtime_policy


def test_runtime_policy_contains_internal_only_true():
    builder = PolicyBuilder()
    policy = builder.build(PolicyBuildInput(
        request_id="req_060",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="direct_secret_request",
        risk_score=70,
        policy_action="RESTRICT",
        matched_assets=[
            {
                "asset_id": "sec_001",
                "name": "secret",
                "type": "key",
                "risk_level": "high",
                "value": "real_secret_value",
                "protection_modes": ["exact_match", "partial_match"],
            }
        ],
        enabled_skills=["test_skill"],
        skill_defense_results=[
            {"skill_name": "test_skill", "blocked_transformations": ["base64"], "verify_encoding": True},
        ],
    ))
    runtime_policy = build_runtime_policy(policy)
    assert runtime_policy["internal_only"] is True


def test_runtime_policy_contains_matcher_data():
    builder = PolicyBuilder()
    policy = builder.build(PolicyBuildInput(
        request_id="req_061",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="direct_secret_request",
        risk_score=70,
        policy_action="RESTRICT",
        matched_assets=[
            {
                "asset_id": "sec_001",
                "name": "secret key",
                "type": "key",
                "risk_level": "high",
                "value": "sk-abc123",
                "protection_modes": ["exact_match", "partial_match"],
                "aliases": ["secret", "key"],
            }
        ],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    runtime_policy = build_runtime_policy(policy)
    assert "asset_matchers" in runtime_policy
    assert len(runtime_policy["asset_matchers"]) > 0


def test_runtime_policy_includes_restricted_tokens():
    builder = PolicyBuilder()
    policy = builder.build(PolicyBuildInput(
        request_id="req_062",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="direct_secret_request",
        risk_score=70,
        policy_action="RESTRICT",
        matched_assets=[
            {
                "asset_id": "sec_001",
                "name": "my secret",
                "type": "key",
                "risk_level": "high",
                "value": "actual_value",
                "protection_modes": ["exact_match"],
                "aliases": ["my secret", "私钥"],
            }
        ],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    runtime_policy = build_runtime_policy(policy)
    assert "restricted_tokens" in runtime_policy
    assert len(runtime_policy["restricted_tokens"]) > 0


def test_runtime_policy_contains_runtime_monitoring_config():
    builder = PolicyBuilder()
    policy = builder.build(PolicyBuildInput(
        request_id="req_063",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="direct_secret_request",
        risk_score=70,
        policy_action="ESCALATE",
        matched_assets=[
            {
                "asset_id": "sec_001",
                "name": "critical secret",
                "type": "key",
                "risk_level": "critical",
                "value": "super_secret_42",
                "protection_modes": ["exact_match"],
            }
        ],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    runtime_policy = build_runtime_policy(policy)
    monitoring = runtime_policy.get("runtime_monitoring", {})
    assert monitoring.get("enabled") is True
    assert "mode" in monitoring


def test_runtime_policy_contains_verification_config():
    builder = PolicyBuilder()
    policy = builder.build(PolicyBuildInput(
        request_id="req_064",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="direct_secret_request",
        risk_score=70,
        policy_action="RESTRICT",
        matched_assets=[],
        enabled_skills=[],
        skill_defense_results=[],
    ))
    runtime_policy = build_runtime_policy(policy)
    verification = runtime_policy.get("verification", {})
    assert verification.get("exact") is True
