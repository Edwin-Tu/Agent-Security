import pytest
from output_guard.output_guard import OutputGuard


class TestOutputGuardPatterns:

    @pytest.fixture
    def guard(self):
        return OutputGuard()

    def test_api_key_is_redacted(self, guard):
        text = "My API key is sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz123456"
        result = guard.inspect(text)
        assert result.is_redacted or result.is_blocked
        assert "sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz123456" not in result.safe_output

    def test_github_token_is_redacted(self, guard):
        text = "Token: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        result = guard.inspect(text)
        assert result.is_redacted or result.is_blocked
        assert "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" not in result.safe_output

    def test_jwt_is_detected(self, guard):
        text = "jwt: eyJhbGciOiJIUzI1NiJ9.eyJ0ZXN0IjoiMSJ9.some_signature"
        result = guard.inspect(text)
        assert result.leakage_detected
        assert "jwt" in str(result.matched_patterns).lower() or "token" in str(result.matched_patterns).lower()

    def test_private_key_is_blocked(self, guard):
        text = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQ\n-----END PRIVATE KEY-----"
        result = guard.inspect(text)
        assert result.is_blocked or result.is_redacted
        assert "PRIVATE KEY" not in result.safe_output

    def test_flag_pattern_is_blocked_or_redacted(self, guard):
        text = "The flag is picoCTF{example_flag}"
        result = guard.inspect(text)
        assert result.leakage_detected
        assert "picoCTF{example_flag}" not in result.safe_output

    def test_password_assignment_is_redacted(self, guard):
        text = "password=123456"
        result = guard.inspect(text)
        assert result.leakage_detected
        assert "password=123456" not in result.safe_output

    def test_safe_output_is_allowed(self, guard):
        text = "Hello, this is a normal conversation about weather."
        result = guard.inspect(text)
        assert not result.is_blocked
        assert not result.is_redacted
        assert not result.leakage_detected
        assert result.safe_output == text
        assert result.action == "ALLOW"
