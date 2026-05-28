from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_multi_turn_signals_increase_risk():
    engine = RiskScoringEngine()
    baseline = engine.score(
        {
            "attack_category": "general_security_question",
            "authorization_status": "authorized",
        }
    )
    higher = engine.score(
        {
            "attack_category": "general_security_question",
            "authorization_status": "authorized",
            "session_signals": ["repeated_partial_request", "previous_blocked_attempt"],
        }
    )

    assert higher.risk_score > baseline.risk_score
    assert "multi_turn" in higher.risk_factors
    assert "previous_blocked_attempt" in higher.risk_factors
