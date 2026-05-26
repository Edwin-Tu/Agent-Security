import json
from pathlib import Path
from typing import Optional


class TokenExpander:

    def __init__(
        self,
        rule_path: str = "policies/token_rules.json",
    ):
        self.rule_path: str = rule_path
        self.token_rules: dict = self._load_token_rules(rule_path)

    # ------------------------------------------------------------------
    # 規則載入
    # ------------------------------------------------------------------

    def _load_token_rules(self, rule_path: str) -> dict:
        path = Path(rule_path)
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}

    def reload(self) -> None:
        self.token_rules = self._load_token_rules(self.rule_path)

    # ------------------------------------------------------------------
    # Token 處理
    # ------------------------------------------------------------------

    @staticmethod
    def normalize(token: str) -> str:
        return token.strip().lower()

    def expand(self, tokens: list[str]) -> set[str]:
        expanded: set[str] = set()

        for token in tokens:
            normalized = self.normalize(token)
            if not normalized:
                continue

            expanded.add(normalized)

            related = self.token_rules.get(normalized, [])
            if isinstance(related, list):
                for rel in related:
                    rel_norm = self.normalize(str(rel))
                    if rel_norm:
                        expanded.add(rel_norm)

        return expanded

    def get_all_categories(self) -> list[str]:
        return list(self.token_rules.keys())
