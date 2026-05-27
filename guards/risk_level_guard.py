import json
from pathlib import Path
from core.token_risk_classifier import TokenRiskClassifier


class RiskLevelGuard:
    def __init__(self, risk_map_path: str = None, threshold: str = "medium"):
        self.risk_map_path = risk_map_path or str(
            Path(__file__).parent.parent / "policies" / "token_risk_map.json"
        )
        self.classifier = TokenRiskClassifier()
        self.risk_map: dict[str, str] = self._load_risk_map()
        self.threshold: str = threshold

    def _load_risk_map(self) -> dict:
        path = Path(self.risk_map_path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("token_risk", {})

    def get_risk_level(self, token: str) -> str:
        token_lower = token.lower().strip()
        return self.risk_map.get(token_lower, "low")

    def check(self, matched_tokens: list[str]) -> dict:
        if not matched_tokens:
            return {"blocked": False, "risk_levels": {}, "max_level": "low", "threshold": self.threshold, "reason": "No tokens to check."}
        risk_levels = {}
        for token in matched_tokens:
            risk_levels[token] = self.get_risk_level(token)
        max_level = max(risk_levels.values(), key=lambda l: self.classifier.LEVEL_ORDER.get(l, 0))
        blocked = self.classifier.LEVEL_ORDER.get(max_level, 0) >= self.classifier.LEVEL_ORDER.get(self.threshold, 1)
        return {"blocked": blocked, "risk_levels": risk_levels, "max_level": max_level, "threshold": self.threshold, "reason": f"Max risk level: {max_level}, threshold: {self.threshold}"}

    def update_threshold(self, threshold: str):
        self.threshold = threshold

    def reload_risk_map(self):
        self.risk_map = self._load_risk_map()
