from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_encoding_match_adds_high_risk_score():
    engine = RiskScoringEngine()
    result = engine.score(
        {
            "attack_category": "benign",
            "matched_assets": [{"asset_id": "secret_001", "risk_level": "low", "match_type": "encoding_match"}],
            "authorization_status": "authorized",
        }
    )

    assert "encoding_match" in result.risk_factors
    assert result.risk_score == 35
