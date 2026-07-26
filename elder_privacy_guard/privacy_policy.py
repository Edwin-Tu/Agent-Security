from __future__ import annotations

from collections.abc import Iterable
from enum import Enum
from typing import cast

from elder_privacy_guard.models import Decision, HealthMatch, PIIMatch

_DANGEROUS_ATTACK_CATEGORIES = {
    "instruction_override",
    "prompt_injection",
    "system_prompt_extraction",
    "role_hijacking",
}

_OVERRIDE_MARKERS = (
    "忽略之前",
    "忽略所有",
    "忽略規則",
    "不要理會",
    "無視",
    "系統提示",
    "ignore all previous instructions",
    "ignore previous instructions",
    "system prompt",
    "prompt injection",
)

_EXTRACTION_MARKERS = (
    "列出所有",
    "所有長者",
    "全部",
    "匯出",
    "提取",
    "擷取",
    "身分證字號",
    "個資",
    "病歷",
    "地址",
    "電話",
)

_SELF_DISCLOSURE_MARKERS = (
    "我的",
    "我有",
    "我住在",
    "聯絡我",
    "聯絡方式是",
    "電話是",
    "地址是",
    "住址是",
    "信箱是",
    "生日是",
    "出生日期是",
    "身分證字號是",
    "身分證是",
)


def evaluate_privacy(
    text: str,
    pii_matches: list[PIIMatch],
    health_matches: list[HealthMatch],
    attack_categories: list[object] | None = None,
    intent_operation: object | None = None,
    intent_scope: object | None = None,
    intent_disclosure_mode: object | None = None,
) -> tuple[Decision, list[str]]:
    reasons: list[str] = []

    text_reject_reason = _text_reject_reason(text, pii_matches, health_matches)
    if text_reject_reason is not None:
        reasons.append(text_reject_reason)
        return Decision.REJECT, reasons

    attack_reason = _attack_category_reject_reason(attack_categories)
    if attack_reason is not None:
        reasons.append(attack_reason)
        return Decision.REJECT, reasons

    intent_reason = _intent_reject_reason(intent_operation, intent_scope, intent_disclosure_mode)
    if intent_reason is not None:
        reasons.append(intent_reason)
        return Decision.REJECT, reasons

    if pii_matches:
        reasons.append(_summarize_matches("PII", pii_matches))

    if health_matches:
        reasons.append(_summarize_matches("health", health_matches))

    if reasons:
        return Decision.SANITIZE, reasons

    return Decision.PASS, ["No sensitive data or hostile intent detected."]


def _text_reject_reason(
    text: str,
    _pii_matches: list[PIIMatch],
    _health_matches: list[HealthMatch],
) -> str | None:
    lowered = text.lower()
    has_self_disclosure_context = any(marker in text for marker in _SELF_DISCLOSURE_MARKERS)

    override_hit = any(marker in lowered for marker in _OVERRIDE_MARKERS)
    extraction_hit = any(marker in text for marker in _EXTRACTION_MARKERS)
    if override_hit and extraction_hit:
        return "Rejecting text with instruction override and bulk extraction intent."

    if override_hit and any(marker in lowered for marker in ("規則", "指令", "system", "prompt", "instruction")):
        return "Rejecting text with instruction override intent."

    if extraction_hit and any(marker in text for marker in ("身分證字號", "個資", "病歷", "地址", "電話")) and not has_self_disclosure_context:
        return "Rejecting text with bulk sensitive-data extraction intent."

    return None


def _attack_category_reject_reason(attack_categories: list[object] | None) -> str | None:
    if not attack_categories:
        return None

    normalized = {_normalize_token(category) for category in attack_categories}
    matched = sorted(category for category in normalized if category in _DANGEROUS_ATTACK_CATEGORIES)
    if not matched:
        return None

    return f"Rejecting dangerous attack categories: {', '.join(matched)}."


def _intent_reject_reason(
    intent_operation: object | None,
    intent_scope: object | None,
    intent_disclosure_mode: object | None,
) -> str | None:
    operation = _normalize_token(intent_operation)
    scope = _normalize_token(intent_scope)
    disclosure_mode = _normalize_token(intent_disclosure_mode)

    if operation == "extract" and scope == "protected_registry":
        return "Rejecting dangerous intent combination: EXTRACT with PROTECTED_REGISTRY."

    if operation == "extract" and disclosure_mode == "full_value" and scope == "protected_registry":
        return "Rejecting dangerous intent combination: EXTRACT with PROTECTED_REGISTRY and FULL_VALUE."

    return None


def _summarize_matches(label: str, matches: Iterable[PIIMatch | HealthMatch]) -> str:
    categories = sorted({_normalize_token(match.category) for match in matches})
    suffix = ", ".join(categories)
    return f"Sanitize {label} matches: {suffix}."


def _normalize_token(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, Enum):
        return cast(str, value.value).strip().lower()
    return str(value).strip().lower()
