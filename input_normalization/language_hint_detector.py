import json
import re
from pathlib import Path


def load_alias_rules() -> dict[str, list[str]]:
    config_path = Path(__file__).resolve().parent / "normalization_rules.json"
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return data.get("aliases", {})


def detect_aliases(text: str) -> tuple[list[str], list[str]]:
    if not isinstance(text, str):
        text = str(text)

    aliases = load_alias_rules()
    normalized = text.casefold()
    compacted = re.sub(r"\s+", "", normalized)
    matched: set[str] = set()
    languages: set[str] = set()

    for canonical, variants in aliases.items():
        for alias in variants:
            alias_norm = alias.casefold()
            alias_compact = re.sub(r"\s+", "", alias_norm)
            if alias_norm in normalized or alias_compact in compacted:
                matched.add(canonical)
                if re.search(r"[\u4e00-\u9fff]", alias):
                    languages.add("zh")
                else:
                    languages.add("en")
                break

    return sorted(matched), sorted(languages)
