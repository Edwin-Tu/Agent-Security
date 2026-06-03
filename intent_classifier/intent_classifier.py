import re

from intent_classifier.intent_result import IntentResult
from intent_classifier.intent_features import (
    AssetReference, Operation, Scope, DisclosureMode,
)
from intent_classifier.intent_rules import load_rules


class IntentClassifier:
    def __init__(self, rules_path: str | None = None):
        self.rules_path = rules_path
        self._rules = None

    def _ensure_rules(self):
        if self._rules is None:
            self._rules = load_rules(self.rules_path)

    def classify(
        self,
        text: str,
        matched_assets: list | None = None,
        input_guard_flags: list | None = None,
        attack_categories: list | None = None,
        session_history: list | None = None,
    ) -> IntentResult:
        self._ensure_rules()
        text_lower = text.lower()

        asset_reference_type, asset_type = self._detect_asset_reference(text_lower, matched_assets)
        scope = self._detect_scope(text_lower)
        operation = self._detect_operation(text_lower, scope, asset_reference_type)
        disclosure_mode = self._detect_disclosure_mode(text_lower, operation)
        risk_score = self._compute_risk_score(operation, asset_reference_type)
        confidence = self._compute_confidence(text_lower, operation)
        reasons = self._build_reasons(operation, scope, disclosure_mode, asset_type)
        matched_features = self._collect_matched_features(text_lower)

        return IntentResult(
            intent=f"{operation}:{scope}:{disclosure_mode}",
            operation=operation,
            scope=scope,
            disclosure_mode=disclosure_mode,
            asset_reference_type=asset_reference_type,
            asset_type=asset_type,
            risk_score=risk_score,
            confidence=confidence,
            reasons=reasons,
            matched_features=matched_features,
            metadata={
                "text_length": len(text),
                "has_assets": matched_assets is not None and len(matched_assets) > 0,
            },
        )

    def _detect_operation(self, text_lower: str, scope: str, asset_reference_type: str) -> str:
        op_patterns = self._rules["operation_patterns"]
        priority = self._rules.get("operation_priority", [
            "BYPASS", "EXTRACT", "RECONSTRUCT", "TRANSFORM",
            "DISCLOSE", "AUTHORIZE_CLAIM", "GENERATE_EXAMPLE",
            "HOW_TO", "COMPARE", "EXPLAIN", "UNKNOWN"
        ])

        matched = set()
        for op, patterns in op_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matched.add(op)
                    break

        best_op = Operation.UNKNOWN
        for op in priority:
            if op in matched:
                best_op = op
                break

        escalation_scopes = {
            Scope.CURRENT_SYSTEM, Scope.HIDDEN_CONTEXT,
            Scope.USER_PROVIDED_TEXT, Scope.PROTECTED_REGISTRY,
            Scope.SESSION_HISTORY,
        }
        if best_op in (Operation.EXPLAIN, Operation.HOW_TO, Operation.COMPARE):
            if scope in escalation_scopes:
                if asset_reference_type != AssetReference.NO_ASSET_REFERENCE:
                    for high_op in ["BYPASS", "DISCLOSE", "EXTRACT", "RECONSTRUCT", "TRANSFORM"]:
                        if high_op in matched:
                            return high_op
                    return Operation.DISCLOSE

        return best_op

    def _detect_scope(self, text_lower: str) -> str:
        scope_patterns = self._rules["scope_patterns"]
        priority = ["SESSION_HISTORY", "HIDDEN_CONTEXT", "USER_PROVIDED_TEXT",
                     "PROTECTED_REGISTRY", "CURRENT_SYSTEM",
                     "GENERAL_CONCEPT", "EXAMPLE_PLACEHOLDER"]

        for s in priority:
            patterns = scope_patterns.get(s, [])
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    if (s != Scope.GENERAL_CONCEPT
                            and self._is_concept_question(text_lower)
                            and self._is_generic_scope_keyword_only(text_lower, s)):
                        return Scope.GENERAL_CONCEPT
                    return s

        if self._is_concept_question(text_lower):
            return Scope.GENERAL_CONCEPT

        return Scope.UNKNOWN_INTERNAL

    def _is_generic_scope_keyword_only(self, text_lower: str, scope: str) -> bool:
        specific_patterns = {
            "CURRENT_SYSTEM": [r"\byour\b"],
            "HIDDEN_CONTEXT": [r"your\s+config", r"from\s+your", r"stored"],
        }
        patterns = specific_patterns.get(scope, [])
        return not any(re.search(p, text_lower) for p in patterns)

    def _is_concept_question(self, text_lower: str) -> bool:
        patterns = [
            "what is", "what does", "what are", "explain", "define",
            "how do", "how to", "how can", "how should", "how does",
            "what makes",
            "why should",
            "什麼是", "是什麼", "解釋", "定義", "概念", "用途",
            "如何運作", "什麼樣的",
        ]
        return any(re.search(p, text_lower) for p in patterns)

    def _detect_disclosure_mode(self, text_lower: str, operation: str) -> str:
        disc_patterns = self._rules["disclosure_patterns"]
        for mode, patterns in disc_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return mode
        if operation == Operation.DISCLOSE:
            return DisclosureMode.FULL_VALUE
        return DisclosureMode.NONE

    def _detect_asset_reference(self, text_lower: str, matched_assets: list | None = None) -> tuple:
        if matched_assets and len(matched_assets) > 0:
            return AssetReference.PROTECTED_REGISTRY_MATCH, matched_assets[0] if isinstance(matched_assets[0], str) else str(matched_assets[0])

        value_patterns = self._rules.get("asset_value_patterns", [])
        for vp in value_patterns:
            if re.search(vp, text_lower):
                return AssetReference.ASSET_VALUE_REFERENCE, "credential_value"

        asset_terms = self._rules["asset_terms"]
        for asset_type, terms in asset_terms.items():
            for term in terms:
                if term in text_lower:
                    return AssetReference.ASSET_TYPE_MENTION, asset_type

        return AssetReference.NO_ASSET_REFERENCE, None

    def _compute_risk_score(self, operation: str, asset_reference_type: str) -> int:
        risk_weights = self._rules["risk_weights"]
        base_score = risk_weights.get(operation, risk_weights.get("UNKNOWN", 20))
        if asset_reference_type == AssetReference.NO_ASSET_REFERENCE:
            base_score = min(base_score, 10)
        return base_score

    def _compute_confidence(self, text_lower: str, operation: str) -> float:
        if operation == Operation.UNKNOWN:
            return 0.3
        op_patterns = self._rules["operation_patterns"].get(operation, [])
        match_count = sum(1 for p in op_patterns if re.search(p, text_lower))
        if match_count >= 2:
            return 0.95
        if match_count == 1:
            return 0.85
        return 0.5

    def _build_reasons(self, operation: str, scope: str, disclosure_mode: str, asset_type: str | None) -> list[str]:
        reasons = []
        if operation != Operation.UNKNOWN:
            reasons.append(f"Detected operation: {operation}")
        if asset_type:
            reasons.append(f"Asset referenced: {asset_type}")
        reasons.append(f"Scope: {scope}")
        reasons.append(f"Disclosure mode: {disclosure_mode}")
        return reasons

    def _collect_matched_features(self, text_lower: str) -> list[str]:
        features = []
        for op, patterns in self._rules["operation_patterns"].items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    features.append(f"op:{op}")
                    break
        for scope, patterns in self._rules["scope_patterns"].items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    features.append(f"scope:{scope}")
                    break
        for asset_type, terms in self._rules["asset_terms"].items():
            for term in terms:
                if term in text_lower:
                    features.append(f"asset:{asset_type}")
                    break
        return features
