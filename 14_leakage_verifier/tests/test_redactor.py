import pytest
from leakage_verifier.redactor import Redactor


class TestRedactor:

    @pytest.fixture
    def redactor(self):
        return Redactor()

    def test_redacts_full_secret(self, redactor):
        result = redactor.redact("The flag is picoCTF{example_flag}", "picoCTF{example_flag}", "full_leak")
        assert "[REDACTED_SECRET]" in result
        assert "picoCTF" not in result

    def test_redacts_partial_fragment(self, redactor):
        result = redactor.redact("Found picoCTF in the output", "picoCTF", "partial_leak")
        assert "[REDACTED_PARTIAL]" in result

    def test_redacts_encoded_secret(self, redactor):
        result = redactor.redact("Encoded: cGljb0NURnthYmN9", "cGljb0NURnthYmN9", "encoding_leak")
        assert "[REDACTED_ENCODED_SECRET]" in result

    def test_does_not_create_nested_redaction(self, redactor):
        result = redactor.redact("[REDACTED_SECRET]", "[REDACTED_SECRET]", "full_leak")
        assert "[REDACTED_SECRET]" in result
        assert "[REDACTED_[REDACTED" not in result

    def test_clean_output_is_unchanged(self, redactor):
        result = redactor.redact("Hello, how are you?", "nonexistent", "full_leak")
        assert result == "Hello, how are you?"
