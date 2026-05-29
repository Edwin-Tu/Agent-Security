import pytest
from output_guard.output_guard import OutputGuard


class TestOutputGuardResult:

    @pytest.fixture
    def guard(self):
        return OutputGuard()

    def test_result_contains_original_output(self, guard):
        text = "some text with sk-proj-123456789012345678901234567890"
        result = guard.inspect(text)
        assert result.original_output == text

    def test_result_contains_safe_output(self, guard):
        text = "some text with sk-proj-123456789012345678901234567890"
        result = guard.inspect(text)
        assert isinstance(result.safe_output, str)
        assert len(result.safe_output) > 0

    def test_result_marks_blocked_output(self, guard):
        text = "-----BEGIN PRIVATE KEY-----\nxxxx\n-----END PRIVATE KEY-----"
        result = guard.inspect(text)
        assert result.is_blocked or result.is_redacted

    def test_result_marks_redacted_output(self, guard):
        text = "api_key=super_secret_value"
        result = guard.inspect(text)
        assert result.is_redacted or result.is_blocked

    def test_result_contains_matched_patterns(self, guard):
        text = "sk-proj-123456789012345678901234567890"
        result = guard.inspect(text)
        assert len(result.matched_patterns) > 0

    def test_result_contains_matched_assets(self, guard):
        text = "some output"
        assets = [
            {
                "asset_id": "test_001",
                "name": "test",
                "type": "secret",
                "value": "some output",
                "aliases": [],
                "risk_level": "medium",
                "protection_modes": ["exact_match"],
            }
        ]
        result = guard.inspect(text, protected_assets=assets)
        assert len(result.matched_assets) > 0

    def test_result_contains_risk_level(self, guard):
        text = "hello world"
        result = guard.inspect(text)
        assert isinstance(result.risk_level, str)

    def test_result_contains_reasons(self, guard):
        text = "sk-proj-123456789012345678901234567890"
        result = guard.inspect(text)
        assert len(result.reasons) > 0
