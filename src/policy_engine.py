"""Policy engine for SecretGuard decisions."""

from __future__ import annotations


class PolicyEngine:
    """Translate risk levels into allow / review / block decisions."""

    ACTIONS = {"low": "allow", "medium": "review", "high": "block", "critical": "block"}

    def decide(self, level: str) -> str:
        return self.ACTIONS.get(level, "review")

    def should_block(self, level: str) -> bool:
        return self.decide(level) == "block"

    def should_review(self, level: str) -> bool:
        return self.decide(level) == "review"
