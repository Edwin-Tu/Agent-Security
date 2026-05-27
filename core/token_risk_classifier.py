from typing import Optional


class TokenRiskClassifier:

    CATEGORY_RISK_MAP: dict[str, str] = {
        "password": "high",
        "api_key": "high",
        "private_key": "high",
        "credential": "high",
        "token": "medium",
        "secret": "medium",
        "database": "low",
        "config": "low",
        "internal_rule": "low",
        "system_prompt": "low",
    }

    LEVEL_ORDER: dict[str, int] = {
        "low": 0,
        "medium": 1,
        "high": 2,
    }

    def __init__(
        self,
        risk_map: Optional[dict[str, str]] = None,
    ):
        if risk_map:
            self.risk_map = risk_map
        else:
            self.risk_map = dict(self.CATEGORY_RISK_MAP)

    def classify(self, category: str) -> str:
        normalized = category.strip().lower()
        return self.risk_map.get(normalized, "low")

    def classify_tokens(self, tokens: list[str]) -> dict[str, str]:
        return {t: self.classify(t) for t in tokens}

    def get_expanded_risk_map(
        self,
        expander,
    ) -> dict[str, str]:
        result: dict[str, str] = {}
        for category in self.risk_map:
            expanded = expander.expand([category])
            risk = self.risk_map[category]
            for token in expanded:
                result[token] = risk
        return result

    def risk_level(self, level: str) -> int:
        return self.LEVEL_ORDER.get(level, 0)

    def exceeds_threshold(self, level: str, threshold: str) -> bool:
        return self.risk_level(level) >= self.risk_level(threshold)
