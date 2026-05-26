import json
from pathlib import Path
from typing import Optional

from expansion.risk_map_writer import RiskMapWriter
from expansion.token_risk_classifier import TokenRiskClassifier
from prompts.guard_prompt import SYSTEM_PROMPT, TOKEN_ANALYSIS_TEMPLATE
from runtime.ollama_client import OllamaClient


class AITokenExpander:

    def __init__(
        self,
        client: OllamaClient,
        risk_map_writer: Optional[RiskMapWriter] = None,
        classifier: Optional[TokenRiskClassifier] = None,
        token_rules_path: str = "policies/token_rules.json",
        auto_learn: bool = True,
    ):
        self.client = client
        self.risk_map_writer = risk_map_writer or RiskMapWriter()
        self.classifier = classifier or TokenRiskClassifier()
        self.token_rules_path = token_rules_path
        self.auto_learn = auto_learn

    def analyze(self, raw_token: str) -> Optional[dict]:
        prompt = TOKEN_ANALYSIS_TEMPLATE.format(raw_token=raw_token)
        result = self.client.generate_json(prompt, system_prompt=SYSTEM_PROMPT)

        if not result:
            return None
        if "category" not in result:
            return None

        self._validate(result)
        return result

    def analyze_and_learn(self, raw_token: str) -> Optional[dict]:
        result = self.analyze(raw_token)
        if not result:
            return None

        if self.auto_learn:
            self.learn(result, raw_token)

        return result

    def learn(self, topology: dict, raw_token: str) -> None:
        category = topology.get("category", "").strip().lower()
        risk_level = topology.get("risk_level", "low")
        expanded_tokens = topology.get("expanded_tokens", [])
        specific_values = topology.get("specific_values", [])
        related_categories = topology.get("related_categories", [])

        if not category:
            return

        # 1. 寫入 token_rules.json
        self._append_to_token_rules(category, expanded_tokens, related_categories)

        # 2. 寫入 token_risk_map.json
        self._append_to_risk_map(category, risk_level, expanded_tokens, specific_values)

    # ------------------------------------------------------------------
    # 內部：寫入 policies
    # ------------------------------------------------------------------

    def _append_to_token_rules(
        self,
        category: str,
        expanded_tokens: list[str],
        related_categories: list[str],
    ) -> None:
        path = Path(self.token_rules_path)
        rules: dict = {}
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    rules = json.load(f)
            except (json.JSONDecodeError, IOError):
                rules = {}

        if category not in rules:
            rules[category] = []

        existing = set(rules[category])
        for token in expanded_tokens:
            normalized = token.strip().lower()
            if normalized and normalized not in existing:
                rules[category].append(normalized)
                existing.add(normalized)

        for rel_cat in related_categories:
            rel_norm = rel_cat.strip().lower()
            if rel_norm and rel_norm not in rules:
                rules[rel_norm] = []
                if rel_norm not in existing:
                    rules[category].append(rel_norm)

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)

    def _append_to_risk_map(
        self,
        category: str,
        risk_level: str,
        expanded_tokens: list[str],
        specific_values: list[str],
    ) -> None:
        risk_map = self.risk_map_writer.load_risk_map()

        all_tokens = [category] + expanded_tokens + specific_values
        for token in all_tokens:
            normalized = token.strip().lower()
            if normalized and normalized not in risk_map:
                risk_map[normalized] = risk_level

        self.risk_map_writer.save_risk_map(risk_map)

    # ------------------------------------------------------------------
    # 驗證
    # ------------------------------------------------------------------

    @staticmethod
    def _validate(result: dict) -> None:
        valid_levels = {"high", "medium", "low"}
        level = result.get("risk_level", "").lower()
        if level not in valid_levels:
            result["risk_level"] = "low"
