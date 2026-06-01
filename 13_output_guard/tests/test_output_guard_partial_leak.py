import pytest
from output_guard.output_guard import OutputGuard


class TestOutputGuardPartialLeak:

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
        ]

    def test_secret_prefix_partial_leak_is_detected(self, guard, assets):
        text = "The flag starts with picoCTF{"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected

    def test_secret_suffix_partial_leak_is_detected(self, guard, assets):
        text = "The secret ends with example_flag}"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected

    def test_secret_middle_fragment_is_detected(self, guard, assets):
        text = "The secret contains example_flag in the middle"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected

    def test_short_fragment_is_not_false_positive(self, guard):
        text = "abc"
        result = guard.inspect(text)
        assert not result.leakage_detected

    def test_multiple_fragments_raise_partial_leak(self, guard, assets):
        text = "picoCTF{ and example_flag and }"
        result = guard.inspect(text, protected_assets=assets)
        assert result.leakage_detected
