from runtime_monitor.interruption_handler import InterruptionHandler
from runtime_monitor.monitor_result import RuntimeMonitorResult


class TestInterruptionHandler:
    def setup_method(self):
        self.handler = InterruptionHandler()

    def test_safe_response_does_not_include_secret(self):
        result = RuntimeMonitorResult(
            allowed=False,
            interrupted=True,
            reason="Detected protected secret.",
            matched_type="exact_secret",
            matched_value="picoCTF{secret_123}",
            risk_level="high",
        )
        response = self.handler.build_safe_response(result)
        assert "picoCTF{secret_123}" not in response
        assert "受保護資訊" in response

    def test_safe_response_for_restricted_token(self):
        result = RuntimeMonitorResult(
            allowed=False,
            interrupted=True,
            reason="Detected restricted token.",
            matched_type="restricted_token",
            matched_value="sk-abc",
            risk_level="high",
        )
        response = self.handler.build_safe_response(result)
        assert "sk-abc" not in response
        assert "受保護資訊" in response

    def test_safe_response_for_safe_output(self):
        result = RuntimeMonitorResult(
            allowed=True,
            interrupted=False,
            reason="No issues detected.",
            risk_level="low",
        )
        response = self.handler.build_safe_response(result)
        assert response is None

    def test_safe_response_message_is_informative(self):
        result = RuntimeMonitorResult(
            allowed=False,
            interrupted=True,
            reason="Detected high risk content.",
            matched_type="exact_secret",
            matched_value="[REDACTED]",
            risk_level="critical",
        )
        response = self.handler.build_safe_response(result)
        assert "中止生成" in response or "協助回答" in response
