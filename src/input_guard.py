"""Input guard implementation for SecretGuard."""

from __future__ import annotations

import re

from .policy_engine import PolicyEngine
from .risk_scorer import RiskScorer


class InputGuard:
    """Inspect user prompts for common attack patterns and assign risk."""

    INJECTION_PATTERNS = [
        re.compile(r"ignore (all|previous) instructions", re.IGNORECASE),
        re.compile(r"system prompt", re.IGNORECASE),
        re.compile(r"developer mode", re.IGNORECASE),
        re.compile(r"jailbreak", re.IGNORECASE),
        re.compile(r"role confusion", re.IGNORECASE),
        re.compile(r"act as|pretend to be|you are now", re.IGNORECASE),
    ]

    def __init__(self, policy_engine: PolicyEngine | None = None, risk_scorer: RiskScorer | None = None):
        self.policy_engine = policy_engine or PolicyEngine()
        self.risk_scorer = risk_scorer or RiskScorer()

    def inspect(self, prompt: str) -> dict:
        indicators = []
        for pattern in self.INJECTION_PATTERNS:
            if pattern.search(prompt):
                indicators.append(pattern.pattern)

        if len(prompt) > 4000:
            indicators.append("long_prompt")

        assessment = self.risk_scorer.score_indicators(indicators)
        decision = self.policy_engine.decide(assessment.level)

        return {
            "prompt": prompt,
            "indicators": indicators,
            "risk_score": assessment.score,
            "level": assessment.level,
            "action": decision,
            "blocked": decision == "block",
        }
