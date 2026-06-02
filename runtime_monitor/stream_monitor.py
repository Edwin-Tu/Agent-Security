from dataclasses import dataclass, field


@dataclass
class StreamCheckResult:
    allowed: bool
    reason: str | None = None
    risk_score: int = 0
    matched_pattern: str | None = None


class StreamMonitor:
    def __init__(self, restricted_patterns: list[str] | None = None):
        self._patterns = [p.lower() for p in (restricted_patterns or [])]
        self._buffer = ""
        self.interrupted = False

    def inspect_chunk(self, chunk: str) -> StreamCheckResult:
        if self.interrupted:
            return StreamCheckResult(
                allowed=False,
                reason="Stream already interrupted",
                risk_score=100,
                matched_pattern=None,
            )

        self._buffer += chunk

        for pattern in self._patterns:
            if pattern in self._buffer.lower():
                self.interrupted = True
                return StreamCheckResult(
                    allowed=False,
                    reason=f"Detected restricted pattern: {pattern}",
                    risk_score=95,
                    matched_pattern=pattern,
                )

        return StreamCheckResult(allowed=True)

    def reset(self):
        self._buffer = ""
        self.interrupted = False
