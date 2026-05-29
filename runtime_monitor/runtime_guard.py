from prompt_builder.restricted_token_guard import RestrictedTokenGuard
from runtime_monitor.stream_monitor import StreamMonitor
from runtime_monitor.interruption_handler import InterruptionHandler


class RuntimeGuard:
    def __init__(self, restricted_tokens: list[str] = None):
        self.token_guard = RestrictedTokenGuard(restricted_tokens=restricted_tokens)
        self.interrupter = InterruptionHandler()
        self.monitor = StreamMonitor(self.token_guard)

    def check_output(self, text: str) -> dict:
        if hasattr(self.token_guard, "check_text"):
            result = self.token_guard.check_text(text)
        else:
            result = self.token_guard.detect(text)

        blocked = result.get("blocked", result.get("matched", False))
        if blocked:
            self.interrupter.interrupt(result.get("reason", "Restricted token matched."), "output_check")
            matched_token = result.get("matched_token", [])
            matched_tokens = result.get("matched_tokens")
            if matched_tokens is None:
                matched_tokens = [m.get("token", "") for m in matched_token if m.get("token")]

            return {
                "blocked": True,
                "reason": result.get("reason", "Restricted token matched."),
                "severity": result.get("severity", "high"),
                "matched_tokens": matched_tokens,
                "matched_token": matched_token,
            }
        return {"blocked": False, "reason": "Output passed."}

    def check_stream(self, chunks) -> dict:
        return self.monitor.monitor(chunks)

    def reset(self):
        self.interrupter.clear()
