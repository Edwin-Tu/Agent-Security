import json
from pathlib import Path


class AttackClassifier:
    def __init__(self, attack_patterns_path: str = None):
        self.attack_patterns_path = attack_patterns_path or str(
            Path(__file__).parent / "attack_patterns.json"
        )
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> dict:
        path = Path(self.attack_patterns_path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def classify(self, text: str) -> list[dict]:
        if not text or not self.patterns:
            return []
        text_lower = text.lower()
        detected = []
        for category, config in self.patterns.items():
            for pattern in config.get("patterns", []):
                if pattern.lower() in text_lower:
                    detected.append({
                        "category": category,
                        "matched_pattern": pattern,
                        "confidence": config.get("confidence", 0.5),
                        "risk_level": config.get("risk_level", "medium"),
                    })
                    break
        return detected

    def classify_with_context(self, text: str, history: list[str] = None) -> list[dict]:
        results = self.classify(text)
        if history:
            for entry in history:
                results.extend(self.classify(entry))
        seen = set()
        unique = []
        for r in results:
            key = r["category"]
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique

    def classify_multi_label(self, text: str) -> list[dict]:
        return self.classify(text)

    def category_scoring(self, threats: list[dict]) -> dict:
        if not threats:
            return {"max_risk": "low", "category_count": 0, "categories": []}
        risk_order = {"low": 0, "medium": 1, "high": 2}
        max_risk = max((t.get("risk_level", "low") for t in threats), key=lambda r: risk_order.get(r, 0))
        categories = list(set(t["category"] for t in threats))
        return {
            "max_risk": max_risk,
            "category_count": len(categories),
            "categories": categories,
        }

    def reload(self):
        self.patterns = self._load_patterns()
