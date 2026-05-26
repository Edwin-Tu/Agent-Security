"""Risk scoring utilities for SecretGuard."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskAssessment:
    """Represents a final risk assessment for a prompt or output."""

    score: float
    level: str
    action: str


class RiskScorer:
    """Compute a normalized risk score and map it to a guardrail level."""

    @staticmethod
    def level_for_score(score: float) -> str:
        score = max(0.0, min(1.0, float(score)))
        if score >= 0.81:
            return "critical"
        if score >= 0.61:
            return "high"
        if score >= 0.31:
            return "medium"
        return "low"

    @staticmethod
    def action_for_level(level: str) -> str:
        mapping = {
            "low": "allow",
            "medium": "review",
            "high": "block",
            "critical": "block",
        }
        return mapping.get(level, "review")

    def score_indicators(self, indicators: list[str]) -> RiskAssessment:
        """Convert a list of suspicious indicators into a scalar risk assessment."""
        if not indicators:
            return RiskAssessment(score=0.0, level="low", action="allow")

        score = min(1.0, len(set(indicators)) * 0.18)
        level = self.level_for_score(score)
        return RiskAssessment(score=score, level=level, action=self.action_for_level(level))

    def score_from_hits(self, count: int, max_hits: int = 5) -> RiskAssessment:
        """A simple count-based risk scorer."""
        normalized = min(1.0, count / max_hits)
        level = self.level_for_score(normalized)
        return RiskAssessment(score=normalized, level=level, action=self.action_for_level(level))
