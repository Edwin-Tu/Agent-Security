from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_general_security_question_is_low_or_moderate():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "general_security_question",
            "classifier_confidence": 0.88,
            "matched_assets": [],
            "triggered_rules": [],
            "authorization_status": "unknown",
            "session_signals": [],
        }
    )

    assert result.risk_level in {"low", "moderate"}
    assert result.recommended_action in {"ALLOW", "WARN"}


def test_direct_secret_request_is_high_or_critical():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "direct_secret_request",
            "classifier_confidence": 0.92,
            "matched_assets": [{"asset_id": "secret_001", "risk_level": "high", "match_type": "alias_match"}],
            "triggered_rules": ["direct_secret_request", "flag_alias_detected"],
            "authorization_status": "unauthorized",
            "session_signals": [],
        }
    )

    assert result.risk_score >= 60
    assert result.risk_level in {"high", "critical"}
    assert result.recommended_action in {"BLOCK", "BLOCK + ESCALATE"}
    assert "direct_secret_request" in result.risk_factors


def test_partial_disclosure_results_in_critical_risk():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "partial_disclosure",
            "matched_assets": [{"asset_id": "secret_002", "risk_level": "medium", "match_type": "partial_match"}],
            "authorization_status": "unauthorized",
        }
    )

    assert result.risk_score >= 80
    assert result.risk_level == "critical"
    assert "partial_match" in result.risk_factors


def test_encoding_bypass_has_no_allow_action():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "encoding_bypass",
            "matched_assets": [{"asset_id": "secret_003", "risk_level": "low", "match_type": "encoding_match"}],
            "authorization_status": "unauthorized",
        }
    )

    assert result.risk_score >= 60
    assert result.recommended_action != "ALLOW"
    assert "encoding_match" in result.risk_factors


def test_role_claim_only_is_treated_as_suspicious():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "system_prompt_extraction",
            "authorization_status": "role_claim_only",
        }
    )

    assert result.risk_score >= 60
    assert "role_claim_only" in result.risk_factors


def test_authorized_user_reduces_risk_but_keeps_matched_asset_factors():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "general_security_question",
            "matched_assets": [{"asset_id": "doc_001", "risk_level": "medium", "match_type": "semantic_match"}],
            "authorization_status": "authorized",
        }
    )

    assert result.risk_score < 60
    assert result.matched_assets
    assert "semantic_match" in result.risk_factors


def test_risk_score_never_exceeds_100():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "authorization_bypass",
            "authorization_status": "unauthorized",
            "matched_assets": [
                {"asset_id": "secret_001", "risk_level": "critical", "match_type": "reconstruction_match"},
                {"asset_id": "secret_002", "risk_level": "high", "match_type": "exact_match"},
            ],
            "session_signals": ["previous_blocked_attempt"],
        }
    )

    assert result.risk_score == 100


def test_unknown_attack_category_recorded_in_risk_factors():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "unknown_new_attack",
            "authorization_status": "unauthorized",
        }
    )

    assert "unknown_attack_category" in result.risk_factors


def test_scoring_rules_fallback_adds_risk_factor(tmp_path):
    broken = tmp_path / "bad.json"
    broken.write_text("{", encoding="utf-8")
    engine = RiskScoringEngine(rules_path=str(broken))

    result = engine.score({"attack_category": "benign"})
    assert engine.fallback_to_default_rules is True
    assert "fallback_to_default_rules" in result.risk_factors
