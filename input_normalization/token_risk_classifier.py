import json
from pathlib import Path


class TokenRiskClassifier:
    LEVEL_ORDER = {"low": 0, "medium": 1, "high": 2}

    def __init__(self, risk_map_path: str = None):
        self.risk_map_path = risk_map_path or str(
            Path(__file__).resolve().parent.parent / "risk_scoring" / "token_risk_map.json"
        )
        self.risk_map = self._load_risk_map()

    def _load_risk_map(self) -> dict:
        path = Path(self.risk_map_path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("token_risk", {})

    def classify(self, token: str) -> str:
        token_lower = token.lower().strip()
        return self.risk_map.get(token_lower, "low")

    def classify_tokens(self, tokens: list[str]) -> dict[str, str]:
        return {t: self.classify(t) for t in tokens}

    def to_int(self, level: str) -> int:
        return self.LEVEL_ORDER.get(level, 0)

    def exceeds_threshold(self, level: str, threshold: str = "medium") -> bool:
        return self.to_int(level) >= self.to_int(threshold)
