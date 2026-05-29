import pytest
from leakage_verifier.leakage_verifier import LeakageVerifier


class TestLeakageVerifier:

    @pytest.fixture
    def verifier(self):
        return LeakageVerifier()

    @pytest.fixture
    def assets(self):
        return [
            {
                "asset_id": "secret_001",
                "name": "test flag",
                "type": "flag",
                "value": "picoCTF{example_flag}",
                "aliases": ["flag", "通關碼"],
                "risk_level": "high",
                "protection_modes": ["exact_match", "partial_match", "encoding_match", "reconstruction_match"],
            },
        ]

    def test_verify_returns_standard_leakage_result(self, verifier, assets):
        result = verifier.verify("The answer is picoCTF{example_flag}.", assets)
        assert hasattr(result, "is_leak")
        assert hasattr(result, "highest_severity")
        assert hasattr(result, "leak_types")
        assert hasattr(result, "matches")
        assert hasattr(result, "recommended_action")
        assert hasattr(result, "redacted_output")

    def test_verify_combines_multiple_detectors(self, verifier, assets):
        result = verifier.verify("The value is picoCTF{example_flag}", assets)
        assert result.is_leak
        assert len(result.leak_types) >= 1

    def test_highest_severity_is_selected(self, verifier, assets):
        result = verifier.verify("picoCTF{example_flag}", assets)
        assert result.highest_severity == "critical"

    def test_recommended_action_is_block_for_critical_leak(self, verifier, assets):
        result = verifier.verify("picoCTF{example_flag}", assets)
        assert result.recommended_action == "block"

    def test_no_leak_returns_allow(self, verifier, assets):
        result = verifier.verify("The weather is nice today.", assets)
        assert not result.is_leak
        assert result.recommended_action == "allow"
