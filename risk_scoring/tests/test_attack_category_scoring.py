from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_direct_secret_request_has_high_score_and_factor():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "direct_secret_request",
            "authorization_status": "unauthorized",
        }
    )

    assert result.risk_score >= 60
    assert "direct_secret_request" in result.risk_factors


def test_unknown_attack_category_is_handled_gracefully():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "unknown_new_attack",
            "authorization_status": "unauthorized",
        }
    )

    assert result.risk_score >= 40
    assert "unknown_attack_category" in result.risk_factors
