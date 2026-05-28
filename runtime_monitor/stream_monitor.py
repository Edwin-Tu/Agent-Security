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
            result = self.guard.detect(output)
            if result["blocked"]:
                return {"blocked": True, "output": "[SecretGuard]\n此內容受到限制，未經授權無法提供。", "matched_tokens": result["matched_tokens"], "reason": result["reason"]}
        return {"blocked": False, "output": output, "matched_tokens": [], "reason": "Monitor passed."}
