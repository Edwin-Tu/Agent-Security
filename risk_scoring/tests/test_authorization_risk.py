from risk_scoring.risk_scoring_engine import RiskScoringEngine


def test_authorized_user_reduces_risk_but_keeps_factors():
    engine = RiskScoringEngine()
    authorized_result = engine.score(
        {
            "attack_category": "general_security_question",
            "matched_assets": [{"asset_id": "doc_001", "risk_level": "medium", "match_type": "alias_match"}],
            "authorization_status": "authorized",
        }
    )

    assert authorized_result.risk_score < 40
    assert authorized_result.matched_assets
    assert "alias_match" in authorized_result.risk_factors
    assert authorized_result.requires_authorization is False
