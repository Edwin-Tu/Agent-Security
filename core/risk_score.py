class RiskScore:
    LEVEL_ORDER = {"low": 0, "medium": 1, "high": 2}

    def __init__(self):
        self.base_level: str = "low"
        self.modifiers: list[dict] = []

    def score_from_level(self, level: str) -> int:
        return self.LEVEL_ORDER.get(level, 0)

    def level_from_score(self, score: int) -> str:
        for level, val in sorted(self.LEVEL_ORDER.items(), key=lambda x: x[1], reverse=True):
            if score >= val:
                return level
        return "low"

    def add_modifier(self, name: str, delta: int, reason: str = ""):
        self.modifiers.append({"name": name, "delta": delta, "reason": reason})

    def compute(self, detected_threats: list[dict]) -> dict:
        if not detected_threats:
            return {"score": 0, "level": "low", "max_level": "low"}
        max_score = 0
        for threat in detected_threats:
            level = threat.get("risk_level", "low")
            score = self.score_from_level(level)
            if score > max_score:
                max_score = score
        for mod in self.modifiers:
            max_score += mod["delta"]
        max_score = max(0, min(max_score, 2))
        final_level = self.level_from_score(max_score)
        return {
            "score": max_score,
            "level": final_level,
            "max_level": final_level,
        }

    def exceeds_threshold(self, detected_threats: list[dict], threshold: str = "medium") -> bool:
        result = self.compute(detected_threats)
        return self.score_from_level(result["level"]) >= self.score_from_level(threshold)
