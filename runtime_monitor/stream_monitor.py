from __future__ import annotations
from typing import Any

from .monitor_result import RuntimeMonitorResult


class RuntimeStreamMonitor:
    def __init__(
        self,
        protected_assets: list[dict[str, Any]] | None = None,
        restricted_tokens: list[str] | None = None,
        max_buffer_size: int = 2000,
    ):
        self._assets: list[dict[str, Any]] = protected_assets or []
        self._restricted_tokens: list[str] = [t.lower() for t in (restricted_tokens or [])]
        self._max_buffer_size: int = max_buffer_size
        self._buffer: str = ""
        self._fragment_cache: dict[str, set[str]] = {}

    def inspect_chunk(self, chunk: str) -> RuntimeMonitorResult:
        if not chunk:
            return RuntimeMonitorResult(allowed=True, interrupted=False, reason="empty chunk", risk_level="low")

        self._buffer += chunk
        if len(self._buffer) > self._max_buffer_size:
            self._buffer = self._buffer[-self._max_buffer_size:]

        buffer_exact = self._check_buffer_exact()
        if buffer_exact is not None:
            return buffer_exact

        buffer_restricted = self._check_restricted(self._buffer)
        if buffer_restricted is not None:
            return buffer_restricted

        buffer_partial = self._check_partial(self._buffer)
        if buffer_partial is not None:
            return buffer_partial

        return RuntimeMonitorResult(allowed=True, interrupted=False, reason="no issues detected", risk_level="low")

    def inspect_buffer(self) -> RuntimeMonitorResult:
        buffer_exact = self._check_buffer_exact()
        if buffer_exact is not None:
            return buffer_exact
        buffer_restricted = self._check_restricted(self._buffer)
        if buffer_restricted is not None:
            return buffer_restricted
        partial = self._check_partial(self._buffer)
        if partial is not None:
            return partial
        return RuntimeMonitorResult(allowed=True, interrupted=False, reason="buffer safe", risk_level="low")

    def should_interrupt(self, result: RuntimeMonitorResult) -> bool:
        return result.interrupted is True or result.allowed is False

    def reset(self) -> None:
        self._buffer = ""

    def _check_buffer_exact(self) -> RuntimeMonitorResult | None:
        lower = self._buffer.lower()
        for asset in self._assets:
            value = asset.get("value", "")
            if not value:
                continue
            risk = asset.get("risk_level", "high")
            if value.lower() in lower:
                return RuntimeMonitorResult(
                    allowed=False,
                    interrupted=True,
                    reason="Detected protected secret in streaming output.",
                    matched_type="exact_secret",
                    matched_value="[REDACTED]",
                    risk_level=risk,
                )
        return None

    def _check_restricted(self, text: str) -> RuntimeMonitorResult | None:
        lower = text.lower()
        for token in self._restricted_tokens:
            if token in lower:
                return RuntimeMonitorResult(
                    allowed=False,
                    interrupted=True,
                    reason="Detected restricted token in streaming output.",
                    matched_type="restricted_token",
                    matched_value="[REDACTED]",
                    risk_level="high",
                )
        return None

    def _check_partial(self, text: str) -> RuntimeMonitorResult | None:
        lower = text.lower()
        for asset in self._assets:
            value = asset.get("value", "")
            if not value:
                continue
            risk = asset.get("risk_level", "high")
            fragments = self._get_partial_fragments(value)
            for frag in fragments:
                if frag in lower:
                    return RuntimeMonitorResult(
                        allowed=False,
                        interrupted=True,
                        reason="Detected partial leakage of protected asset.",
                        matched_type="partial_secret",
                        matched_value="[REDACTED]",
                        risk_level=risk,
                    )
        return None

    def _get_partial_fragments(self, value: str) -> set[str]:
        if value in self._fragment_cache:
            return self._fragment_cache[value]

        fragments: set[str] = set()
        lower = value.lower()
        n = len(lower)

        for length in range(7, n + 1):
            for i in range(n - length + 1):
                frag = lower[i:i + length]
                has_special = any(not c.isalnum() for c in frag)
                if has_special or length >= 8:
                    fragments.add(frag)

        self._fragment_cache[value] = fragments
        return fragments
