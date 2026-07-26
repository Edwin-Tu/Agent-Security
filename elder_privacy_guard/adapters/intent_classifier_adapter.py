from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, cast

from elder_privacy_guard.adapters import path_loader

UNKNOWN_VALUE = "UNKNOWN"


@dataclass(slots=True)
class IntentClassification:
    intent: str = UNKNOWN_VALUE
    operation: str = UNKNOWN_VALUE
    scope: str = UNKNOWN_VALUE
    disclosure_mode: str = UNKNOWN_VALUE
    asset_reference_type: str = UNKNOWN_VALUE
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    is_available: bool = False


class _IntentClassifierProtocol(Protocol):
    def __init__(self, rules_path: str | None = None) -> None: ...

    def classify(
        self,
        text: str,
        matched_assets: list[object] | None = None,
        input_guard_flags: list[object] | None = None,
        attack_categories: list[object] | None = None,
        session_history: object | None = None,
    ) -> object: ...


def classify_intent(
    text: str,
    matched_assets: list[object] | None = None,
    input_guard_flags: list[object] | None = None,
    attack_categories: list[object] | None = None,
    session_history: object | None = None,
) -> IntentClassification:
    if not path_loader.is_agent_security_available():
        return IntentClassification()

    try:
        intent_classifier_module = importlib.import_module("intent_classifier")
        intent_classifier = cast(
            type[_IntentClassifierProtocol], getattr(intent_classifier_module, "IntentClassifier")
        )
        classifier = intent_classifier()
        result = classifier.classify(
            text,
            matched_assets=matched_assets,
            input_guard_flags=input_guard_flags,
            attack_categories=attack_categories,
            session_history=session_history,
        )
    except Exception:
        return IntentClassification()

    return IntentClassification(
        intent=_as_text(getattr(result, "intent", UNKNOWN_VALUE)),
        operation=_as_text(getattr(result, "operation", UNKNOWN_VALUE)),
        scope=_as_text(getattr(result, "scope", UNKNOWN_VALUE)),
        disclosure_mode=_as_text(getattr(result, "disclosure_mode", UNKNOWN_VALUE)),
        asset_reference_type=_as_text(getattr(result, "asset_reference_type", UNKNOWN_VALUE)),
        confidence=float(getattr(result, "confidence", 0.0)),
        reasons=_as_reason_list(getattr(result, "reasons", [])),
        is_available=True,
    )


def _as_text(value: object) -> str:
    if isinstance(value, Enum):
        return cast(str, value.value)
    if value is None:
        return UNKNOWN_VALUE
    return str(value)


def _as_reason_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = cast(list[object], value)
        return [str(item) for item in items]
    return [str(value)]
