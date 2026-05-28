class DefensePolicyEngine:
    ACTION_ORDER = ["allow", "warn", "rewrite", "restrict", "block", "authorize", "escalate"]

    def __init__(self, threshold: str = "medium"):
        self.threshold = threshold

    def decide(self, risk_result: dict, context: dict = None) -> dict:
        score = risk_result.get("score", 0)
        level = risk_result.get("level", "low")
        escalated = (context or {}).get("escalated", False)
        accumulated = (context or {}).get("accumulated_risk", 0)

        if accumulated >= 5 or escalated:
            action = "escalate"
        elif score >= 6:
            action = "block"
        elif score >= 4:
            action = "restrict"
        elif score >= 2:
            action = "warn"
        else:
            action = "allow"

        return {
            "action": action,
            "risk_score": score,
            "risk_level": level,
            "threshold": self.threshold,
            "reason": f"Risk {score}/{level} → action: {action}",
        }

    def requires_block(self, decision: dict) -> bool:
        return decision.get("action") in ("block", "escalate")

    def requires_restriction(self, decision: dict) -> bool:
        return decision.get("action") in ("restrict", "block", "escalate")
