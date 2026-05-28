from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_asset_risk_score_accumulates_and_caps_at_100():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "direct_secret_request",
            "matched_assets": [
                {"asset_id": "secret_001", "risk_level": "critical", "match_type": "exact_match"},
                {"asset_id": "secret_002", "risk_level": "high", "match_type": "alias_match"},
            ],
            "authorization_status": "authorized",
        }
    )

    assert result.risk_score == 100
    assert "matched_critical_risk_asset" in result.risk_factors
    assert "matched_high_risk_asset" in result.risk_factors
