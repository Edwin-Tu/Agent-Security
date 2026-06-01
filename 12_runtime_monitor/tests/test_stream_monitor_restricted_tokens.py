from runtime_monitor.stream_monitor import RuntimeStreamMonitor


class TestRestrictedTokens:
    def setup_method(self):
        self.monitor = RuntimeStreamMonitor(
            protected_assets=[],
            restricted_tokens=["BEGIN PRIVATE KEY", "sk-"],
        )

    def test_interrupts_restricted_token(self):
        result = self.monitor.inspect_chunk("Here is BEGIN PRIVATE KEY")
        assert result.interrupted is True
        assert result.matched_type == "restricted_token"

    def test_interrupts_sk_prefix_token(self):
        result = self.monitor.inspect_chunk("sk-abc123def456")
        assert result.interrupted is True
        assert result.matched_type == "restricted_token"

    def test_case_insensitive_restricted_token(self):
        result = self.monitor.inspect_chunk("begin private key")
        assert result.interrupted is True
        assert result.matched_type == "restricted_token"

    def test_restricted_token_in_rolling_buffer(self):
        self.monitor.inspect_chunk("some text before ")
        result = self.monitor.inspect_chunk("BEGIN PRIVATE KEY")
        assert result.interrupted is True
