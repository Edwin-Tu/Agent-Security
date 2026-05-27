class DefenseContext:
    def __init__(self):
        self.active_defenses: list[str] = []
        self.blocked_tokens: list[str] = []
        self.risk_levels: dict[str, str] = {}
        self.intervention_log: list[dict] = []
        self.policy_action: str = "allow"
        self.risk_score: int = 0

    def record_intervention(self, stage: str, reason: str, detail: dict = None):
        self.intervention_log.append({
            "stage": stage,
            "reason": reason,
            "detail": detail or {},
        })

    def set_policy_action(self, action: str):
        self.policy_action = action

    def set_risk_score(self, score: int):
        self.risk_score = score

    def summary(self) -> dict:
        return {
            "active_defenses": self.active_defenses,
            "blocked_tokens": self.blocked_tokens,
            "risk_levels": self.risk_levels,
            "policy_action": self.policy_action,
            "risk_score": self.risk_score,
            "intervention_count": len(self.intervention_log),
        }

    def reset(self):
        self.active_defenses.clear()
        self.blocked_tokens.clear()
        self.risk_levels.clear()
        self.intervention_log.clear()
        self.policy_action = "allow"
        self.risk_score = 0
