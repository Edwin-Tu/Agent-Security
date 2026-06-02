from runtime_monitor.stream_monitor import RuntimeStreamMonitor


class TestSafeOutput:
    def setup_method(self):
        self.monitor = RuntimeStreamMonitor(
            protected_assets=[],
            restricted_tokens=["flag", "password"],
        )

    def test_allows_safe_stream_chunk(self):
        result = self.monitor.inspect_chunk("This is a normal explanation about Python.")
        assert result.allowed is True
        assert result.interrupted is False

    def test_allows_empty_chunk(self):
        result = self.monitor.inspect_chunk("")
        assert result.allowed is True
        assert result.interrupted is False

    def test_allows_multiple_safe_chunks(self):
        r1 = self.monitor.inspect_chunk("Today is a nice day.")
        r2 = self.monitor.inspect_chunk("The weather is great.")
        r3 = self.monitor.inspect_chunk("I love programming.")
        assert all(r.allowed for r in [r1, r2, r3])
        assert all(not r.interrupted for r in [r1, r2, r3])

    def test_buffer_does_not_grow_indefinitely(self):
        monitor = RuntimeStreamMonitor(
            protected_assets=[],
            restricted_tokens=[],
            max_buffer_size=100,
        )
        long_text = "a" * 200
        monitor.inspect_chunk(long_text)
        assert len(monitor._buffer) <= 100
