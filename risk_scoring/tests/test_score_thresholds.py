from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_score_thresholds_map_to_actions():
    engine = RiskScoringEngine()
    low_result = engine.score(
        {
            "attack_category": "benign",
            "authorization_status": "authorized",
        }
    )
    moderate_result = engine.score(
        {
            "attack_category": "general_security_question",
            "authorization_status": "unknown",
        }
    )
    medium_result = engine.score(
        {
            "attack_category": "benign",
            "matched_assets": [{"asset_id": "doc_001", "risk_level": "critical", "match_type": "alias_match"}],
            "authorization_status": "authorized",
        }
    )
    high_result = engine.score(
        {
            "attack_category": "encoding_bypass",
            "authorization_status": "unauthorized",
        }
    )
    critical_result = engine.score(
        {
            "attack_category": "partial_disclosure",
            "authorization_status": "unauthorized",
            "matched_assets": [{"asset_id": "secret_001", "risk_level": "critical", "match_type": "reconstruction_match"}],
        }
    )

    assert low_result.risk_level in {"low", "moderate"}
    assert low_result.recommended_action == "ALLOW"
    assert moderate_result.risk_level == "moderate"
    assert moderate_result.recommended_action == "WARN"
    assert medium_result.risk_level == "medium"
    assert medium_result.recommended_action == "REWRITE"
    assert high_result.risk_level in {"high", "critical"}
    assert high_result.recommended_action in {"BLOCK", "BLOCK + ESCALATE"}
    assert critical_result.risk_level == "critical"
    assert critical_result.recommended_action == "BLOCK + ESCALATE"
