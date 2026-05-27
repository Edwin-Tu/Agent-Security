class RiskScoringEngine:
    LEVEL_SCORE = {"low": 1, "medium": 2, "high": 3}

    def __init__(self):
        self.base_score: int = 0
        self.modifiers: list[dict] = []

    def compute(self, threats: list[dict], assets: list[dict] = None, history: list[str] = None) -> dict:
        score = 0
        factors = []

        for threat in threats:
            s = self.LEVEL_SCORE.get(threat.get("risk_level", "low"), 1)
            score += s
            factors.append({"factor": f"attack:{threat['category']}", "delta": s})

        if assets:
            for asset in assets:
                s = self.LEVEL_SCORE.get(asset.get("risk_level", "low"), 1)
                score += s
                factors.append({"factor": f"asset:{asset.get('name','unknown')}", "delta": s})

        if history and len(history) >= 3:
            score += 2
            factors.append({"factor": "multi_turn_history", "delta": 2})

        for mod in self.modifiers:
            score += mod["delta"]
            factors.append({"factor": mod["name"], "delta": mod["delta"]})

        score = max(0, min(score, 10))

        if score >= 6:
            level = "high"
        elif score >= 3:
            level = "medium"
        else:
            level = "low"

        return {"score": score, "level": level, "factors": factors}

    def add_modifier(self, name: str, delta: int):
        self.modifiers.append({"name": name, "delta": delta})

    def reset(self):
        self.base_score = 0
        self.modifiers.clear()
