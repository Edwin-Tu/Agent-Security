from typing import Iterable, Optional
from prompt_builder.restricted_token_guard import RestrictedTokenGuard


class StreamMonitor:
    def __init__(self, guard: RestrictedTokenGuard, max_buffer: int = 1000):
        self.guard = guard
        self.max_buffer = max_buffer

    def monitor(self, chunks: Iterable[str]) -> dict:
        output = ""
        for chunk in chunks:
            if not chunk:
                continue
            output += chunk
            if len(output) > self.max_buffer:
                output = output[-self.max_buffer:]

            if hasattr(self.guard, "check_text"):
                result = self.guard.check_text(output)
            else:
                result = self.guard.detect(output)

            blocked = result.get("blocked", result.get("matched", False))
            if blocked:
                matched_token = result.get("matched_token", [])
                matched_tokens = result.get("matched_tokens")
                if matched_tokens is None:
                    matched_tokens = [m.get("token", "") for m in matched_token if m.get("token")]

                return {
                    "blocked": True,
                    "output": "[SecretGuard]\n此內容受到限制，未經授權無法提供。",
                    "matched_tokens": matched_tokens,
                    "matched_token": matched_token,
                    "severity": result.get("severity", "high"),
                    "reason": result.get("reason", "Restricted token matched."),
                }

        return {
            "blocked": False,
            "output": output,
            "matched_tokens": [],
            "matched_token": [],
            "severity": "low",
            "reason": "Monitor passed.",
        }
