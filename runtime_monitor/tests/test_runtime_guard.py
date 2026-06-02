from runtime_monitor.stream_monitor import RuntimeStreamMonitor
from runtime_monitor.interruption_handler import InterruptionHandler
from runtime_monitor.runtime_guard import RuntimeGuard


class TestRuntimeGuard:
    def setup_method(self):
        self.monitor = RuntimeStreamMonitor(
            protected_assets=[{"value": "picoCTF{secret_123}", "risk_level": "high"}],
            restricted_tokens=[],
        )
        self.handler = InterruptionHandler()
        self.guard = RuntimeGuard(self.monitor, self.handler)

    def test_runtime_guard_stops_stream_after_detection(self):
        chunks = ["The answer is ", "picoCTF{secret_123}", " do not show this later"]
        response = self.guard.process_stream(chunks)
        assert "picoCTF{secret_123}" not in response
        assert "do not show this later" not in response
        assert "受保護資訊" in response

    def test_guard_returns_safe_chunks_when_no_detection(self):
        chunks = ["This is ", "a safe ", "response."]
        response = self.guard.process_stream(chunks)
        assert response == "This is a safe response."

    def test_guard_stops_on_restricted_token(self):
        monitor = RuntimeStreamMonitor(
            protected_assets=[],
            restricted_tokens=["sk-"],
        )
        guard = RuntimeGuard(monitor, self.handler)
        chunks = ["Here is ", "sk-abc123", " more text"]
        response = guard.process_stream(chunks)
        assert "sk-abc123" not in response
        assert "more text" not in response
        assert "受保護資訊" in response

    def test_guard_stops_on_first_chunk_if_dangerous(self):
        chunks = ["picoCTF{secret_123}", "this should not appear"]
        response = self.guard.process_stream(chunks)
        assert "this should not appear" not in response
