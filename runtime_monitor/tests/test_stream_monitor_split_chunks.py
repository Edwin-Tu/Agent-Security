from runtime_monitor.stream_monitor import RuntimeStreamMonitor


class TestSplitChunks:
    def setup_method(self):
        self.monitor = RuntimeStreamMonitor(
            protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
            restricted_tokens=[],
        )

    def test_interrupts_secret_split_across_chunks(self):
        r1 = self.monitor.inspect_chunk("pico")
        r2 = self.monitor.inspect_chunk("CTF")
        r3 = self.monitor.inspect_chunk("{secret_123}")
        assert r1.interrupted is False
        assert r2.interrupted is False
        assert r3.interrupted is True
        assert r3.matched_type in ("exact_secret", "reconstructed_secret")

    def test_interrupts_on_second_chunk_when_rolling_buffer_has_secret(self):
        self.monitor.inspect_chunk("The secret is ")
        result = self.monitor.inspect_chunk("picoCTF{secret_123}")
        assert result.interrupted is True
        assert result.matched_type == "exact_secret"

    def test_interrupts_on_partial_reconstruction(self):
        self.monitor.inspect_chunk("picoCTF")
        result = self.monitor.inspect_chunk("{")
        result2 = self.monitor.inspect_chunk("secret_123}")
        assert result.interrupted is True
        assert result.matched_type == "partial_secret"

    def test_resets_buffer_between_requests(self):
        self.monitor.inspect_chunk("pico")
        self.monitor.reset()
        result = self.monitor.inspect_chunk("What is the weather today?")
        assert result.interrupted is False
        assert self.monitor._buffer == "What is the weather today?"
