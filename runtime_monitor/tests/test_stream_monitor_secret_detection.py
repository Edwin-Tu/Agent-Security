from runtime_monitor.stream_monitor import RuntimeStreamMonitor


class TestSecretDetection:
    def setup_method(self):
        self.monitor = RuntimeStreamMonitor(
            protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
            restricted_tokens=[],
        )

    def test_interrupts_exact_secret_chunk(self):
        result = self.monitor.inspect_chunk("The answer is picoCTF{secret_123}")
        assert result.allowed is False
        assert result.interrupted is True
        assert result.matched_type == "exact_secret"

    def test_interrupts_secret_alone(self):
        result = self.monitor.inspect_chunk("picoCTF{secret_123}")
        assert result.interrupted is True
        assert result.matched_type == "exact_secret"

    def test_case_insensitive_secret_detection(self):
        result = self.monitor.inspect_chunk("PICOCTF{SECRET_123}")
        assert result.interrupted is True
        assert result.matched_type == "exact_secret"

    def test_does_not_leak_matched_value(self):
        result = self.monitor.inspect_chunk("picoCTF{secret_123}")
        assert result.matched_value == "[REDACTED]"
