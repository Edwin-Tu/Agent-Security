from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import importlib
from pathlib import Path
from typing import Protocol, cast

from elder_privacy_guard.adapters import path_loader


@dataclass(slots=True)
class AttackClassification:
    is_attack: bool
    primary_category: str
    matched_categories: list[str]
    confidence: float
    evidence: list[str]
    is_available: bool


class _AttackClassifierProtocol(Protocol):
    def classify(
        self,
        prompt: str,
        normalized_prompt: str | None = None,
        input_guard_result: object | None = None,
        session_context: object | None = None,
    ) -> object:
        ...


class _AttackClassifierFactory(Protocol):
    def __call__(self, *, attacks_path: Path, patterns_path: Path) -> _AttackClassifierProtocol:
        ...


def classify_attack(
    prompt: str,
    normalized_prompt: str | None = None,
    input_guard_result: object | None = None,
    session_context: object | None = None,
) -> AttackClassification:
    if not prompt.strip():
        return _benign_unavailable_result()

    agent_security_path = path_loader.get_agent_security_path()
    if agent_security_path is None:
        return _benign_unavailable_result()

    try:
        classifier_module = importlib.import_module("attack_classifier")
        classifier_factory = cast(_AttackClassifierFactory, getattr(classifier_module, "AttackClassifier"))
        rules_dir = agent_security_path / "attack_classifier" / "rules"
        classifier = classifier_factory(
            attacks_path=rules_dir / "attacks.json",
            patterns_path=rules_dir / "attack_patterns.json",
        )
        raw_result = classifier.classify(
            prompt,
            normalized_prompt=normalized_prompt,
            input_guard_result=input_guard_result,
            session_context=session_context,
        )
        return _map_attack_result(raw_result)
    except Exception as exc:
        return _unavailable_error_result(exc)


def _map_attack_result(raw_result: object) -> AttackClassification:
    if isinstance(raw_result, list):
        return _map_legacy_result(cast(Sequence[Mapping[str, object]], raw_result))

    if isinstance(raw_result, Mapping):
        matched_categories_value: object = raw_result["matched_categories"] if "matched_categories" in raw_result else []
        evidence_value: object = raw_result["evidence"] if "evidence" in raw_result else []
        return AttackClassification(
            is_attack=bool(raw_result["is_attack"]) if "is_attack" in raw_result else False,
            primary_category=str(raw_result["primary_category"]) if "primary_category" in raw_result else "benign",
            matched_categories=[str(category) for category in _as_list(matched_categories_value)],
            confidence=_to_float(raw_result["confidence"]) if "confidence" in raw_result else 0.0,
            evidence=[str(item) for item in _as_list(evidence_value)],
            is_available=True,
        )

    if hasattr(raw_result, "is_attack"):
        return AttackClassification(
            is_attack=bool(getattr(raw_result, "is_attack", False)),
            primary_category=str(getattr(raw_result, "primary_category", "benign")),
            matched_categories=[str(category) for category in _as_list(getattr(raw_result, "matched_categories", []))],
            confidence=_to_float(getattr(raw_result, "confidence", 0.0)),
            evidence=[str(item) for item in _as_list(getattr(raw_result, "evidence", []))],
            is_available=True,
        )

    return _unavailable_error_result(ValueError("Unsupported attack classifier result shape"))


def _map_legacy_result(raw_result: Sequence[Mapping[str, object]]) -> AttackClassification:
    if not raw_result:
        return AttackClassification(
            is_attack=False,
            primary_category="benign",
            matched_categories=[],
            confidence=0.0,
            evidence=[],
            is_available=True,
        )

    matched_categories: list[str] = []
    evidence: list[str] = []
    confidence = 0.0

    for item in raw_result:
        mapping_item: dict[str, object] = cast(dict[str, object], item)
        category = str(mapping_item["category"]) if "category" in mapping_item else "benign"
        if category not in matched_categories:
            matched_categories.append(category)
        matched_pattern = str(mapping_item["matched_pattern"]) if "matched_pattern" in mapping_item else ""
        evidence.append(matched_pattern)
        confidence_value = mapping_item["confidence"] if "confidence" in mapping_item else 0.0
        confidence = max(confidence, _to_float(confidence_value))

    return AttackClassification(
        is_attack=True,
        primary_category=matched_categories[0],
        matched_categories=matched_categories,
        confidence=confidence,
        evidence=evidence,
        is_available=True,
    )


def _benign_unavailable_result() -> AttackClassification:
    return AttackClassification(
        is_attack=False,
        primary_category="benign",
        matched_categories=[],
        confidence=0.0,
        evidence=[],
        is_available=False,
    )


def _unavailable_error_result(exc: Exception) -> AttackClassification:
    return AttackClassification(
        is_attack=False,
        primary_category="unavailable",
        matched_categories=[],
        confidence=0.0,
        evidence=[f"Attack classifier unavailable: {exc}"],
        is_available=False,
    )


def _as_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return cast(list[object], value)
    if isinstance(value, tuple):
        return list(cast(Sequence[object], value))
    return [value]


def _to_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0
