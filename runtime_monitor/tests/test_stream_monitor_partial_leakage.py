from runtime_monitor.stream_monitor import RuntimeStreamMonitor


class TestPartialLeakage:
    def setup_method(self):
        self.monitor = RuntimeStreamMonitor(
            protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
            restricted_tokens=[],
        )

    def test_detects_partial_secret_prefix(self):
        result = self.monitor.inspect_chunk("The flag starts with picoCTF{")
        assert result.interrupted is True
        assert result.matched_type == "partial_secret"

    def test_detects_partial_secret_suffix(self):
        result = self.monitor.inspect_chunk("secret_123")
        assert result.interrupted is True
        assert result.matched_type == "partial_secret"

    def test_detects_partial_secret_middle_fragment(self):
        result = self.monitor.inspect_chunk("The middle part is CTF{sec")
        assert result.interrupted is True
        assert result.matched_type == "partial_secret"
