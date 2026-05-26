import json
from pathlib import Path
from typing import Optional

from expansion.token_risk_classifier import TokenRiskClassifier


class RiskLevelGuard:

    def __init__(
        self,
        classifier: TokenRiskClassifier,
        threshold: str = "medium",
        risk_map_path: str = "policies/token_risk_map.json",
    ):
        self.classifier = classifier
        self.threshold = threshold
        self.risk_map_path = risk_map_path

        self.risk_map: dict[str, str] = self._load_risk_map()

    # ------------------------------------------------------------------
    # 風險地圖載入
    # ------------------------------------------------------------------

    def _load_risk_map(self) -> dict[str, str]:
        path = Path(self.risk_map_path)
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}

    # ------------------------------------------------------------------
    # 風險檢查
    # ------------------------------------------------------------------

    def get_risk_level(self, token: str) -> str:
        normalized = token.strip().lower()
        return self.risk_map.get(normalized, "low")

    def check(self, matched_tokens: list[str]) -> dict:
        if not matched_tokens:
            return {
                "blocked": False,
                "risk_levels": {},
                "max_level": "low",
                "threshold": self.threshold,
                "reason": "No tokens matched.",
            }

        risk_levels: dict[str, str] = {}
        max_level: str = "low"

        for token in matched_tokens:
            level = self.get_risk_level(token)
            risk_levels[token] = level
            if self.classifier.exceeds_threshold(level, max_level):
                max_level = level

        blocked = self.classifier.exceeds_threshold(max_level, self.threshold)

        if blocked:
            reason = (
                f"Risk level '{max_level}' "
                f"exceeds threshold '{self.threshold}'. "
                f"Matched: {risk_levels}"
            )
        else:
            reason = (
                f"Risk level '{max_level}' "
                f"is within threshold '{self.threshold}'."
            )

        return {
            "blocked": blocked,
            "risk_levels": risk_levels,
            "max_level": max_level,
            "threshold": self.threshold,
            "reason": reason,
        }

    def update_threshold(self, threshold: str) -> None:
        self.threshold = threshold

    def reload_risk_map(self) -> None:
        self.risk_map = self._load_risk_map()
