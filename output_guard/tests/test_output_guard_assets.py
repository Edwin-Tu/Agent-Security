import pytest
from output_guard.output_guard import OutputGuard


class TestOutputGuardAssets:

    @pytest.fixture
    def guard(self):
        return OutputGuard()

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
                "protection_modes": ["exact_match", "partial_match"],
            },
            {
                "asset_id": "secret_002",
                "name": "API key",
                "type": "api_key",
                "value": "sk-proj-my-secret-key-12345",
                "aliases": ["mykey", "my-api-key"],
                "risk_level": "high",
                "protection_modes": ["exact_match", "partial_match"],
            },
        ]

    def test_user_defined_secret_is_detected(self, guard, assets):
        text = "The secret value is picoCTF{example_flag}"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected
        assert "secret_001" in result.matched_assets

    def test_user_defined_secret_is_redacted(self, guard, assets):
        text = "The secret value is picoCTF{example_flag}"
        result = guard.inspect(text, protected_assets=assets)
        assert "picoCTF{example_flag}" not in result.safe_output
        assert result.is_redacted or result.is_blocked

    def test_secret_alias_is_detected(self, guard, assets):
        text = "這裡是通關碼"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected
        assert "通關碼" in str(result.matched_patterns) or "secret_001" in result.matched_assets

    def test_multiple_assets_are_detected(self, guard, assets):
        text = "Flag is picoCTF{example_flag} and key is sk-proj-my-secret-key-12345"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected
        assert "secret_001" in result.matched_assets
        assert "secret_002" in result.matched_assets

    def test_case_insensitive_asset_match(self, guard, assets):
        text = "PICOCTF{EXAMPLE_FLAG}"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected
