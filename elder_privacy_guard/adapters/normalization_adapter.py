from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Callable, Protocol, cast

from elder_privacy_guard.adapters.path_loader import is_agent_security_available


@dataclass(slots=True)
class NormalizationResult:
    normalized_text: str
    raw_text: str
    suspicion_flags: list[str]
    transformations: list[dict[str, object]]
    detected_languages: list[str]
    is_available: bool


class _NormalizedInputResult(Protocol):
    raw_text: str
    normalized_text: str
    suspicion_flags: list[str]
    transformations: list[dict[str, object]]
    detected_languages: list[str]


def normalize(text: str) -> NormalizationResult:
    if not is_agent_security_available():
        return _fallback_result(text)

    try:
        normalize_input_module = importlib.import_module("input_normalization")
    except (ImportError, ModuleNotFoundError):
        return _fallback_result(text)

    try:
        normalize_input = cast(
            Callable[[str], _NormalizedInputResult],
            getattr(normalize_input_module, "normalize_input"),
        )
        result = normalize_input(text)
    except Exception:
        return _fallback_result(text)

    return NormalizationResult(
        normalized_text=result.normalized_text,
        raw_text=result.raw_text,
        suspicion_flags=list(result.suspicion_flags),
        transformations=list(result.transformations),
        detected_languages=list(result.detected_languages),
        is_available=True,
    )


def _fallback_result(text: str) -> NormalizationResult:
    return NormalizationResult(
        normalized_text=text.strip().lower(),
        raw_text=text,
        suspicion_flags=[],
        transformations=[],
        detected_languages=[],
        is_available=False,
    )
