import json
from pathlib import Path


class TokenExpander:
    def __init__(self, rule_path: str = "policies/token_rules.json"):
        self.rule_path = rule_path
        self.rules = self._load_rules()

    def _load_rules(self) -> dict:
        path = Path(__file__).resolve().parent.parent / self.rule_path
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize(self, token: str) -> str:
        return token.strip().lower()

    def expand(self, tokens: list[str]) -> set[str]:
        expanded = set()
        for token in tokens:
            normalized = self.normalize(token)
            expanded.add(normalized)
            for category, related in self.rules.items():
                if normalized == category.lower() or normalized in [r.lower() for r in related]:
                    expanded.add(category.lower())
                    for rel in related:
                        expanded.add(rel.lower())
                    break
        return expanded

    def get_all_categories(self) -> list[str]:
        return list(self.rules.keys())

    def reload(self):
        self.rules = self._load_rules()
