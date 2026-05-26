"""Output guard implementation for SecretGuard."""

from __future__ import annotations

from .leakage_detector import LeakageDetector
from .policy_engine import PolicyEngine
from .risk_scorer import RiskScorer


class OutputGuard:
    """Check model outputs for leakage and sanitize them before returning."""

    def __init__(self, policy_engine: PolicyEngine | None = None, risk_scorer: RiskScorer | None = None):
        self.policy_engine = policy_engine or PolicyEngine()
        self.risk_scorer = risk_scorer or RiskScorer()
        self.leakage_detector = LeakageDetector()

    def inspect(self, output: str) -> dict:
        redacted_output, findings = self.leakage_detector.redact(output)
        count = len(findings)
        assessment = self.risk_scorer.score_from_hits(count)
        decision = self.policy_engine.decide(assessment.level)

        return {
            "output": output,
            "sanitized_output": redacted_output,
            "findings": findings,
            "risk_score": assessment.score,
            "level": assessment.level,
            "action": decision,
            "blocked": decision == "block",
            "redacted": redacted_output != output,
        }
