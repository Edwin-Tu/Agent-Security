import pytest
from event_logger.event_redactor import EventRedactor


class TestEventRedactor:

    @pytest.fixture
    def redactor(self):
        return EventRedactor()

    def test_flag_is_redacted(self, redactor):
        text = "The flag is picoCTF{example_flag}"
        result = redactor.redact_text(text)
        assert "[REDACTED_SECRET]" in result
        assert "picoCTF" not in result

    def test_api_key_is_redacted(self, redactor):
        text = "key: sk-proj-123456789012345678901234567890"
        result = redactor.redact_text(text)
        assert "[REDACTED_API_KEY]" in result
        assert "sk-proj" not in result

    def test_private_key_block_is_redacted(self, redactor):
        text = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSj\n-----END PRIVATE KEY-----"
        result = redactor.redact_text(text)
        assert "[REDACTED_PRIVATE_KEY]" in result
        assert "PRIVATE KEY" not in result

    def test_password_field_is_redacted(self, redactor):
        event = {"secret": "my_password_123", "password": "supersecret", "text": "hello"}
        result = redactor.redact_event(event)
        assert result["secret"] == "[REDACTED_SECRET]"
        assert result["password"] == "[REDACTED_PASSWORD]"

    def test_secret_field_is_redacted(self, redactor):
        event = {"api_key": "sk-proj-test-12345", "text": "hello"}
        result = redactor.redact_event(event)
        assert result["api_key"] == "[REDACTED_API_KEY]"

    def test_leakage_evidence_is_redacted(self, redactor):
        event = {"leakage_evidence": "picoCTF{leaked_flag}", "text": "hello"}
        result = redactor.redact_event(event)
        assert "picoCTF" not in result["leakage_evidence"]

    def test_redaction_does_not_break_nested_dict(self, redactor):
        event = {"metadata": {"key": "sk-proj-123456789012345678901234567890"}, "text": "hello"}
        result = redactor.redact_event(event)
        assert "sk-proj" not in str(result)

    def test_redaction_does_not_create_nested_placeholder(self, redactor):
        text = "[REDACTED_API_KEY]"
        result = redactor.redact_text(text)
        assert "[REDACTED_[REDACTED" not in result
        assert result == "[REDACTED_API_KEY]"
