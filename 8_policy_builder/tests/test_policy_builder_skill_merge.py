from policy_builder.policy_models import PolicyBuildInput
from policy_builder.policy_builder import PolicyBuilder


def test_enabled_skills_are_deduplicated():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_040",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="encoding_bypass",
        risk_score=60,
        policy_action="RESTRICT",
        matched_assets=[],
        enabled_skills=["skill_a", "skill_b", "skill_a"],
        skill_defense_results=[],
    ))
    assert result.enabled_skills.count("skill_a") == 1
    assert result.enabled_skills.count("skill_b") == 1
    assert len(result.enabled_skills) == 2


def test_skill_defense_merges_blocked_transformations():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_041",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="encoding_bypass",
        risk_score=60,
        policy_action="RESTRICT",
        matched_assets=[],
        enabled_skills=["enc_skill", "other_skill"],
        skill_defense_results=[
            {"skill_name": "enc_skill", "blocked_transformations": ["base64", "hex"], "verify_encoding": True},
            {"skill_name": "other_skill", "blocked_transformations": ["rot13"], "verify_encoding": False},
        ],
    ))
    assert "base64" in result.blocked_transformations
    assert "hex" in result.blocked_transformations
    assert "rot13" in result.blocked_transformations
    assert len(result.blocked_transformations) == 3


def test_encoding_skill_enables_verify_encoding():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_042",
        original_prompt="Test encode",
        normalized_prompt="test encode",
        user_role="user",
        attack_category="encoding_bypass",
        risk_score=50,
        policy_action="WARN",
        matched_assets=[],
        enabled_skills=["encoding_bypass_skill"],
        skill_defense_results=[
            {"skill_name": "encoding_bypass_skill", "verify_encoding": True, "blocked_transformations": []},
        ],
    ))
    assert result.verify_encoding is True


def test_reconstruction_skill_enables_verify_reconstruction():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_043",
        original_prompt="Test reconstruct",
        normalized_prompt="test reconstruct",
        user_role="user",
        attack_category="data_reconstruction",
        risk_score=60,
        policy_action="RESTRICT",
        matched_assets=[],
        enabled_skills=["data_reconstruction_skill"],
        skill_defense_results=[
            {"skill_name": "data_reconstruction_skill", "verify_reconstruction": True, "blocked_transformations": []},
        ],
    ))
    assert result.verify_reconstruction is True


def test_strict_runtime_takes_priority_over_normal():
    builder = PolicyBuilder()
    result = builder.build(PolicyBuildInput(
        request_id="req_044",
        original_prompt="Test",
        normalized_prompt="test",
        user_role="user",
        attack_category="multi_category",
        risk_score=70,
        policy_action="RESTRICT",
        matched_assets=[],
        enabled_skills=["skill_a", "skill_b"],
        skill_defense_results=[
            {"skill_name": "skill_a", "runtime_monitoring_mode": "normal", "blocked_transformations": []},
            {"skill_name": "skill_b", "runtime_monitoring_mode": "strict", "blocked_transformations": []},
        ],
    ))
    assert result.runtime_monitoring_mode == "strict"
