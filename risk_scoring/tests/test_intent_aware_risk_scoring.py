from risk_scoring.risk_scoring_engine import RiskScoringEngine


class TestIntentAwareRiskScoring:
    def setup_method(self):
        self.engine = RiskScoringEngine()

    def test_asset_type_mention_only_is_low_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "UNKNOWN",
            "scope": "UNKNOWN",
            "disclosure_mode": "NONE",
        })
        assert result.risk_score < 30

    def test_api_key_explanation_is_low_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "EXPLAIN",
            "scope": "GENERAL_CONCEPT",
            "disclosure_mode": "NONE",
        })
        assert result.risk_score < 30

    def test_api_key_disclosure_is_high_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "DISCLOSE",
            "scope": "UNKNOWN_INTERNAL",
            "disclosure_mode": "FULL_VALUE",
        })
        assert result.risk_score >= 75

    def test_hidden_context_extraction_is_high_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "EXTRACT",
            "scope": "HIDDEN_CONTEXT",
            "disclosure_mode": "FULL_VALUE",
        })
        assert result.risk_score >= 75

    def test_partial_reconstruction_is_high_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "RECONSTRUCT",
            "scope": "UNKNOWN_INTERNAL",
            "disclosure_mode": "PARTIAL_VALUE",
        })
        assert result.risk_score >= 75

    def test_encoded_transform_is_high_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "TRANSFORM",
            "scope": "UNKNOWN_INTERNAL",
            "disclosure_mode": "ENCODED_VALUE",
        })
        assert result.risk_score >= 75

    def test_explain_plus_actual_value_is_high_risk(self):
        result = self.engine.score({
            "asset_reference_type": "asset_type_mention",
            "operation": "DISCLOSE",
            "scope": "UNKNOWN_INTERNAL",
            "disclosure_mode": "FULL_VALUE",
        })
        assert result.risk_score >= 75
