import json
from pathlib import Path


class RulesLoadError(Exception):
    pass


def load_rules(rules_path: str | None = None) -> dict:
    if rules_path is None:
        rules_path = str(Path(__file__).parent / "intent_rules.json")

    path = Path(rules_path)
    if not path.exists():
        raise RulesLoadError(f"Rules file not found: {rules_path}")

    if not path.is_file():
        raise RulesLoadError(f"Rules path is not a file: {rules_path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise RulesLoadError(f"Invalid JSON in rules file '{rules_path}': {e}")

    if not isinstance(data, dict):
        raise RulesLoadError(f"Rules file must contain a JSON object, got {type(data).__name__}")

    required_keys = ["operation_patterns", "scope_patterns", "disclosure_patterns", "asset_terms", "risk_weights"]
    for key in required_keys:
        if key not in data:
            raise RulesLoadError(f"Missing required key '{key}' in rules file: {rules_path}")

    return data
