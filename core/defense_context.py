class DefenseContext:
    def __init__(self):
        self.active_defenses: list[str] = []
        self.blocked_tokens: list[str] = []
        self.risk_levels: dict[str, str] = {}
        self.intervention_log: list[dict] = []
        self.threshold: str = "medium"

    def record_intervention(self, stage: str, reason: str, detail: dict = None):
        self.intervention_log.append({
            "stage": stage,
            "reason": reason,
            "detail": detail or {},
        })

    def set_threshold(self, level: str):
        self.threshold = level

    def get_threshold(self) -> str:
        return self.threshold

    def summary(self) -> dict:
        return {
            "active_defenses": self.active_defenses,
            "blocked_tokens": self.blocked_tokens,
            "risk_levels": self.risk_levels,
            "threshold": self.threshold,
            "intervention_count": len(self.intervention_log),
            "interventions": self.intervention_log,
        }

    def reset(self):
        self.active_defenses.clear()
        self.blocked_tokens.clear()
        self.risk_levels.clear()
        self.intervention_log.clear()
        self.threshold = "medium"
