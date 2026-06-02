import json
import os


class RoutingRulesLoader:
    def __init__(self, rules_path: str | None = None):
        if rules_path is None:
            rules_path = os.path.join(os.path.dirname(__file__), "routing_rules.json")
        self.rules_path = rules_path
        self._rules: dict = {}

    def load(self) -> dict:
        try:
            with open(self.rules_path, "r") as f:
                self._rules = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Routing rules file not found: {self.rules_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in routing rules file: {e}")
        return self._rules

    def get_rule(self, category: str) -> dict | None:
        return self._rules.get(category)

    def has_rule(self, category: str) -> bool:
        return category in self._rules

    def list_categories(self) -> list[str]:
        return list(self._rules.keys())
