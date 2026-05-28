import json
from pathlib import Path


class PatternLoaderError(Exception):
    pass


class PatternLoader:
    @staticmethod
    def load_attacks(path: str) -> list[dict]:
        path_obj = Path(path)
        if not path_obj.exists():
            raise PatternLoaderError(f"Attacks file not found: {path}")
        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise PatternLoaderError(f"Invalid JSON in attacks file: {e}")
        if not isinstance(data, list):
            raise PatternLoaderError("Attacks file must contain a JSON array")
        return data

    @staticmethod
    def load_attack_patterns(path: str) -> list[dict]:
        path_obj = Path(path)
        if not path_obj.exists():
            raise PatternLoaderError(f"Attack patterns file not found: {path}")
        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise PatternLoaderError(f"Invalid JSON in attack patterns file: {e}")
        if not isinstance(data, list):
            raise PatternLoaderError("Attack patterns file must contain a JSON array")
        return data

    @staticmethod
    def build_attack_map(attacks: list[dict]) -> dict[str, dict]:
        return {a["category"]: a for a in attacks if "category" in a}
