from __future__ import annotations

from typing import cast

from elder_privacy_guard.adapters.attack_classifier_adapter import classify_attack
from elder_privacy_guard.adapters.intent_classifier_adapter import classify_intent
from elder_privacy_guard.adapters.normalization_adapter import normalize
from elder_privacy_guard.adapters.path_loader import load_agent_security_path
from elder_privacy_guard.data_masker import mask_text
from elder_privacy_guard.health_data_detector import detect_health_data
from elder_privacy_guard.input_security import PolicyAction, assess_input
from elder_privacy_guard.models import Decision, HealthSummary, PIISummary, PrivacyDecision
from elder_privacy_guard.pii_detector import detect_pii
from elder_privacy_guard.privacy_policy import evaluate_privacy


class ElderInputGuard:
    _agent_security_used: bool

    def __init__(self, auto_load_agent_security: bool = True) -> None:
        self._agent_security_used = False
        if auto_load_agent_security:
            try:
                _ = load_agent_security_path()
            except Exception:
                self._agent_security_used = False
            else:
                self._agent_security_used = True

    def guard(self, text: str, context: object | None = None) -> PrivacyDecision:
        normalized = normalize(text)
        pii_matches = detect_pii(text)
        health_matches = detect_health_data(text)
        attack = classify_attack(text, normalized.normalized_text)
        intent = classify_intent(text)
        security = assess_input(text, context)

        attack_categories = [cast(object, category) for category in attack.matched_categories]
        legacy_decision, legacy_reasons = evaluate_privacy(
            text,
            pii_matches,
            health_matches,
            attack_categories=attack_categories,
            intent_operation=intent.operation,
            intent_scope=intent.scope,
            intent_disclosure_mode=intent.disclosure_mode,
        )

        legacy_effective = legacy_decision
        if (
            legacy_decision is Decision.REJECT
            and security.action is PolicyAction.ALLOW
            and not security.risks
            and ("BENIGN_SECURITY_DISCUSSION" in security.intents or self._looks_like_meta_discussion(text))
        ):
            legacy_effective = Decision.PASS

        decision = self._merge_decision(legacy_effective, security.action, bool(pii_matches or health_matches))
        effective_legacy_reasons = [] if legacy_effective is not legacy_decision else legacy_reasons
        reasons = list(dict.fromkeys([*security.reasons, *effective_legacy_reasons]))

        sanitized_text = text
        if decision is not Decision.REJECT and (pii_matches or health_matches):
            sanitized_text = mask_text(text, pii_matches, health_matches)

        evidence = security.evidence()
        model_called = decision is not Decision.REJECT and security.action not in {
            PolicyAction.BLOCK,
            PolicyAction.REQUIRE_AUTH,
            PolicyAction.REVIEW,
        }
        evidence["enforcement"] = {"model_called": model_called, "success": True}

        metadata: dict[str, object] = {
            "normalization_available": normalized.is_available,
            "attack_available": attack.is_available,
            "intent_available": intent.is_available,
            "context_provided": context is not None,
            "pii_categories": [match.category.value for match in pii_matches],
            "health_categories": [match.category.value for match in health_matches],
            "attack_categories": list(attack.matched_categories),
            "intent_operation": intent.operation,
            "intent_scope": intent.scope,
            "intent_disclosure_mode": intent.disclosure_mode,
            "structured_evidence": evidence,
        }

        self._agent_security_used = normalized.is_available or attack.is_available or intent.is_available or self._agent_security_used

        return PrivacyDecision(
            decision=decision,
            sanitized_text=sanitized_text,
            reasons=reasons,
            pii_summaries=[PIISummary(category=match.category, masked=match.masked) for match in pii_matches],
            health_summaries=[HealthSummary(category=match.category, masked=match.masked) for match in health_matches],
            agent_security_used=self._agent_security_used,
            metadata=metadata,
            policy_action=security.action.value if decision is not Decision.SANITIZE else PolicyAction.SANITIZE.value,
            owasp_risks=[risk.value for risk in security.risks],
            model_called=model_called,
            _pii_matches=pii_matches,
            _health_matches=health_matches,
        )

    @staticmethod
    def _looks_like_meta_discussion(text: str) -> bool:
        lowered = text.lower()
        markers = (
            "什麼是", "是什麼", "概念", "解釋", "說明", "分析", "風險", "為什麼", "如何",
            "what is", "explain", "analyze", "analyse", "why", "risk",
        )
        return any(marker in lowered for marker in markers)

    @staticmethod
    def _merge_decision(legacy: Decision, action: PolicyAction, has_sensitive_input: bool) -> Decision:
        if legacy is Decision.REJECT or action in {PolicyAction.BLOCK, PolicyAction.REQUIRE_AUTH, PolicyAction.REVIEW}:
            return Decision.REJECT
        if legacy is Decision.SANITIZE or has_sensitive_input:
            return Decision.SANITIZE
        return Decision.PASS
