from __future__ import annotations

from .input_normalizer import normalize_input
from .normalization_result import NormalizationResult


class InputNormalizer:
    """Legacy wrapper for backward compatibility."""

    def normalize(self, text: str) -> NormalizationResult:
        return normalize_input(text)


NormalizedInput = NormalizationResult

__all__ = [
    "normalize_input",
    "NormalizationResult",
    "InputNormalizer",
    "NormalizedInput",
]
