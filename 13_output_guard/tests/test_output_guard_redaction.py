import pytest
from output_guard.output_guard import OutputGuard


class TestOutputGuardRedaction:

    @pytest.fixture
    def guard(self):
        return OutputGuard()

    def test_api_key_redaction_placeholder(self, guard):
        text = "key: sk-proj-123456789012345678901234567890"
        result = guard.inspect(text)
        assert result.is_redacted or result.is_blocked
        safe = result.safe_output
        assert "sk-proj-123456789012345678901234567890" not in safe
        if result.action == "REDACT":
            assert "[REDACTED" in safe

    def test_private_key_block_placeholder(self, guard):
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA\n-----END RSA PRIVATE KEY-----"
        result = guard.inspect(text)
        assert result.is_blocked or result.is_redacted
        assert "PRIVATE KEY" not in result.safe_output
        assert "[REDACTED" in result.safe_output or result.action == "BLOCK"

    def test_multiple_secrets_are_all_redacted(self, guard):
        text = "api_key=abcdefg and password=123456"
        result = guard.inspect(text)
        assert result.leakage_detected
        assert "abcdefg" not in result.safe_output
        assert "123456" not in result.safe_output

    def test_redaction_does_not_create_nested_placeholders(self, guard):
        text = "api_key=abcdefg"
        result = guard.inspect(text)
        safe = result.safe_output
        assert "[REDACTED" in safe
        assert "[REDACTED_[REDACTED" not in safe

    def test_safe_text_is_not_modified(self, guard):
        text = "Hello, how are you today?"
        result = guard.inspect(text)
        assert result.safe_output == text
        assert not result.is_redacted
        assert not result.is_blocked
