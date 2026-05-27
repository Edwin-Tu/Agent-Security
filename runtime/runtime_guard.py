from guards.restricted_token_guard import RestrictedTokenGuard
from guards.risk_level_guard import RiskLevelGuard
from runtime.stream_monitor import StreamMonitor
from runtime.interruption_handler import InterruptionHandler


class RuntimeGuard:
    def __init__(self, restricted_tokens: list[str] = None, threshold: str = "medium"):
        self.token_guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens)
        self.risk_guard = RiskLevelGuard(threshold=threshold)
        self.interrupter = InterruptionHandler()
        self.monitor = StreamMonitor(self.token_guard)

    def check_output(self, text: str) -> dict:
        detect_result = self.token_guard.detect(text)
        if detect_result["blocked"]:
            risk_result = self.risk_guard.check(detect_result["matched_tokens"])
            if risk_result["blocked"]:
                self.interrupter.interrupt(risk_result["reason"])
                return {"blocked": True, "reason": risk_result["reason"], "matched_tokens": detect_result["matched_tokens"]}
        return {"blocked": False, "reason": "Output passed."}

    def check_stream(self, chunks) -> dict:
        return self.monitor.monitor(chunks)

    def reset(self):
        self.interrupter.clear()
