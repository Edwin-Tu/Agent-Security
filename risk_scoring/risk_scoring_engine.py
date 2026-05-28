from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .risk_score_result import RiskScoreResult
from .score_calculator import ScoreCalculator
from .session_risk_tracker import SessionRiskTracker


class RiskScoringEngine:
    def __init__(self, rules_path: str | None = None):
        self.rules_path = rules_path
        self.rules, self.fallback_to_default_rules = self._load_rules(rules_path)
        self.calculator = ScoreCalculator(self.rules)

    def _load_rules(self, rules_path: str | None) -> tuple[dict[str, Any], bool]:
        default_rules = ScoreCalculator.DEFAULT_RULES
        if rules_path:
            path = Path(rules_path)
        else:
            path = Path(__file__).parent / "scoring_rules.json"

        try:
            with path.open("r", encoding="utf-8") as handle:
                rules = json.load(handle)
            if not isinstance(rules, dict):
                raise ValueError("Invalid scoring rules format")
            return rules, False
        except (OSError, ValueError, json.JSONDecodeError):
            return default_rules, True

    def score(self, request_context: dict) -> RiskScoreResult:
        attack_category = request_context.get("attack_category")
        confidence = request_context.get("classifier_confidence")
        matched_assets = request_context.get("matched_assets") or []
        triggered_rules = request_context.get("triggered_rules") or []
        authorization_status = request_context.get("authorization_status", "unknown")
        session_signals = request_context.get("session_signals") or []

        attack_score = self.calculator.calculate_attack_score(attack_category)
        asset_score = self.calculator.calculate_asset_score(matched_assets)
        match_type_score = self.calculator.calculate_match_type_score(matched_assets)
        authorization_adjustment = self.calculator.calculate_authorization_adjustment(authorization_status)
        session_tracker = SessionRiskTracker(session_signals, self.rules)
        session_score = session_tracker.calculate_score()

        raw_score = attack_score + asset_score + match_type_score + authorization_adjustment + session_score
        risk_score = max(0, min(raw_score, 100))
        risk_level = self._get_risk_level(risk_score)
        recommended_action = self._get_recommended_action(risk_level)

        risk_factors = self._build_risk_factors(
            attack_category=attack_category,
            matched_assets=matched_assets,
            authorization_status=authorization_status,
            session_signals=session_signals,
            triggered_rules=triggered_rules,
        )

        requires_authorization = self._requires_authorization(
            authorization_status, attack_category, matched_assets, risk_score
        )
        enable_strict_runtime_monitor = self._enable_strict_runtime_monitor(
            risk_score, matched_assets, session_signals
        )

        if self.fallback_to_default_rules:
            risk_factors.append("fallback_to_default_rules")

        return RiskScoreResult(
            risk_score=risk_score,
            risk_level=risk_level,
            recommended_action=recommended_action,
            risk_factors=risk_factors,
            matched_assets=matched_assets,
            triggered_rules=triggered_rules,
            attack_category=attack_category,
            confidence=confidence,
            requires_authorization=requires_authorization,
            enable_strict_runtime_monitor=enable_strict_runtime_monitor,
        )

    def _get_risk_level(self, score: int) -> str:
        thresholds = self.rules.get("thresholds", {})
        for level, bounds in thresholds.items():
            if isinstance(bounds, list) and len(bounds) == 2:
                low, high = bounds
                if low <= score <= high:
                    return level
        return "low"

    def _get_recommended_action(self, risk_level: str) -> str:
        mapping = {
            "low": "ALLOW",
            "moderate": "WARN",
            "medium": "REWRITE",
            "high": "BLOCK",
            "critical": "BLOCK + ESCALATE",
        }
        return mapping.get(risk_level, "WARN")

    def _build_risk_factors(
        self,
        attack_category: str | None,
        matched_assets: list[dict],
        authorization_status: str,
        session_signals: list[str],
        triggered_rules: list[str],
    ) -> list[str]:
        factors: list[str] = []
        if attack_category:
            factors.append(attack_category)
            if attack_category not in self.rules.get("attack_category_scores", {}):
                factors.append("unknown_attack_category")

        if any(asset.get("risk_level") == "high" for asset in matched_assets):
            factors.append("matched_high_risk_asset")
        if any(asset.get("risk_level") == "critical" for asset in matched_assets):
            factors.append("matched_critical_risk_asset")

        for asset in matched_assets:
            match_type = asset.get("match_type")
            if match_type:
                factors.append(match_type)

        if authorization_status:
            if authorization_status not in {"owner", "authorized"}:
                factors.append(authorization_status)

        if triggered_rules:
            factors.extend(triggered_rules)

        if session_signals:
            factors.extend(session_signals)
            factors.append("multi_turn")

        return list(dict.fromkeys(factors))

    def _requires_authorization(
        self,
        authorization_status: str,
        attack_category: str | None,
        matched_assets: list[dict],
        risk_score: int,
    ) -> bool:
        if authorization_status in {"unauthorized", "unknown", "role_claim_only"}:
            return True
        if authorization_status in {"owner", "authorized"}:
            return False
        if matched_assets:
            return True
        return risk_score >= 60

    def _enable_strict_runtime_monitor(
        self,
        risk_score: int,
        matched_assets: list[dict],
        session_signals: list[str],
    ) -> bool:
        strict_match_types = {
            "partial_match",
            "encoding_match",
            "reconstruction_match",
            "translation_match",
        }
        if risk_score >= 60:
            return True
        if any(asset.get("match_type") in strict_match_types for asset in matched_assets):
            return True
        if any(signal in {"encoding_after_refusal", "session_marked_suspicious", "repeated_partial_request"}
               for signal in session_signals):
            return True
        return False
