from guards.restricted_token_guard import RestrictedTokenGuard
from runtime.stream_monitor import StreamMonitor
from runtime.interruption_handler import InterruptionHandler


class RuntimeGuard:
    def __init__(self, restricted_tokens: list[str] = None):
        self.token_guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens)
        self.interrupter = InterruptionHandler()
        self.monitor = StreamMonitor(self.token_guard)

    def check_output(self, text: str) -> dict:
        result = self.token_guard.detect(text)
        if result["blocked"]:
            self.interrupter.interrupt(result["reason"], "output_check")
            return {"blocked": True, "reason": result["reason"], "matched_tokens": result["matched_tokens"]}
        return {"blocked": False, "reason": "Output passed."}

    def check_stream(self, chunks) -> dict:
        return self.monitor.monitor(chunks)

    def reset(self):
        self.interrupter.clear()
