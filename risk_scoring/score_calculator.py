from __future__ import annotations

from typing import Any


class ScoreCalculator:
    DEFAULT_RULES: dict[str, Any] = {
        "attack_category_scores": {
            "benign": 0,
            "general_security_question": 10,
            "direct_secret_request": 50,
            "role_play_bypass": 45,
            "instruction_override": 55,
            "system_prompt_extraction": 60,
            "encoding_bypass": 65,
            "translation_bypass": 60,
            "partial_disclosure": 70,
            "multi_turn_probe": 75,
            "data_reconstruction": 80,
            "authorization_bypass": 85,
            "unknown_suspicious": 40,
        },
        "asset_risk_scores": {
            "low": 10,
            "medium": 20,
            "high": 35,
            "critical": 50,
        },
        "match_type_scores": {
            "exact_match": 40,
            "alias_match": 25,
            "partial_match": 35,
            "encoding_match": 45,
            "translation_match": 40,
            "reconstruction_match": 50,
            "semantic_match": 35,
            "pattern_match": 30,
        },
        "authorization_adjustments": {
            "owner": -30,
            "authorized": -20,
            "unknown": 10,
            "unauthorized": 40,
            "role_claim_only": 30,
        },
        "session_signal_scores": {
            "repeated_secret_request": 20,
            "repeated_partial_request": 30,
            "previous_blocked_attempt": 25,
            "language_switching_probe": 20,
            "encoding_after_refusal": 30,
            "session_marked_suspicious": 30,
        },
        "thresholds": {
            "low": [0, 19],
            "moderate": [20, 39],
            "medium": [40, 59],
            "high": [60, 79],
            "critical": [80, 100],
        },
    }

    def __init__(self, rules: dict[str, Any]):
        self.rules = rules
        self.attack_category_scores = rules.get("attack_category_scores", self.DEFAULT_RULES["attack_category_scores"])
        self.asset_risk_scores = rules.get("asset_risk_scores", self.DEFAULT_RULES["asset_risk_scores"])
        self.match_type_scores = rules.get("match_type_scores", self.DEFAULT_RULES["match_type_scores"])
        self.authorization_adjustments = rules.get("authorization_adjustments", self.DEFAULT_RULES["authorization_adjustments"])
        self.session_signal_scores = rules.get("session_signal_scores", self.DEFAULT_RULES["session_signal_scores"])

    def calculate_attack_score(self, attack_category: str | None) -> int:
        if not attack_category:
            return 0
        return self.attack_category_scores.get(
            attack_category,
            self.attack_category_scores.get("unknown_suspicious", 40),
        )

    def calculate_asset_score(self, matched_assets: list[dict]) -> int:
        score = 0
        for asset in matched_assets:
            score += self.asset_risk_scores.get(asset.get("risk_level", "low"), 0)
        return score

    def calculate_match_type_score(self, matched_assets: list[dict]) -> int:
        score = 0
        for asset in matched_assets:
            score += self.match_type_scores.get(asset.get("match_type", ""), 0)
        return score

    def calculate_authorization_adjustment(self, authorization_status: str) -> int:
        return self.authorization_adjustments.get(
            authorization_status,
            self.authorization_adjustments.get("unknown", 10),
        )

    def calculate_session_score(self, session_signals: list[str]) -> int:
        return sum(
            self.session_signal_scores.get(signal, 0)
            for signal in session_signals
        )
