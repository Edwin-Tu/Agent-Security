import json
from pathlib import Path


class AttackTaxonomy:
    def __init__(self, attacks_path: str = None):
        self.attacks_path = attacks_path or str(
            Path(__file__).parent / "attacks.json"
        )
        self.attacks = self._load()

    def _load(self) -> dict:
        path = Path(self.attacks_path)
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get(self, attack_id: str) -> dict | None:
        return self.attacks.get(attack_id)

    def all(self) -> dict:
        return dict(self.attacks)

    def by_risk_level(self, level: str) -> list[tuple[str, dict]]:
        return [(k, v) for k, v in self.attacks.items() if v.get("risk_level") == level]

    def categories(self) -> list[str]:
        return list(self.attacks.keys())

    def lookup_by_pattern(self, text: str) -> list[tuple[str, dict]]:
        text_lower = text.lower()
        matches = []
        for attack_id, config in self.attacks.items():
            for pattern in config.get("patterns", []):
                if pattern.lower() in text_lower:
                    matches.append((attack_id, config))
                    break
        return matches

    def mitigation_for(self, attack_id: str) -> list[str]:
        attack = self.get(attack_id)
        if not attack:
            return []
        return [m.strip() for m in attack.get("mitigation", "").split(",") if m.strip()]

    def reload(self):
        self.attacks = self._load()
