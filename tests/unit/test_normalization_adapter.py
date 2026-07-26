from __future__ import annotations

import sys
import types
from dataclasses import is_dataclass

import pytest

import elder_privacy_guard.adapters.normalization_adapter as normalization_adapter
import elder_privacy_guard.adapters.path_loader as path_loader


def test_normalize_fallback_returns_stripped_lowercase_and_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    path_loader.reset()
    monkeypatch.delitem(sys.modules, "input_normalization", raising=False)

    result = normalization_adapter.normalize("  Hello World  ")

    assert is_dataclass(result)
    assert result.raw_text == "  Hello World  "
    assert result.normalized_text == "hello world"
    assert result.suspicion_flags == []
    assert result.transformations == []
    assert result.detected_languages == []
    assert result.is_available is False


@pytest.mark.parametrize(
    ("input_text", "expected_normalized_text"),
    [
        ("", ""),
        ("   \t\n  ", ""),
    ],
)
def test_normalize_fallback_handles_empty_and_whitespace_only_input(
    input_text: str,
    expected_normalized_text: str,
) -> None:
    path_loader.reset()

    result = normalization_adapter.normalize(input_text)

    assert result.normalized_text == expected_normalized_text
    assert result.raw_text == input_text
    assert result.is_available is False


def test_normalize_fallback_preserves_traditional_chinese_text() -> None:
    path_loader.reset()

    result = normalization_adapter.normalize("  長照服務  ")

    assert result.normalized_text == "長照服務"
    assert result.raw_text == "  長照服務  "
    assert result.is_available is False


def test_normalize_connected_mode_maps_agent_security_result_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_module = types.ModuleType("input_normalization")

    def fake_normalize_input(text: str) -> object:
        _ = text
        return types.SimpleNamespace(
            raw_text="RAW",
            normalized_text="normalized",
            suspicion_flags=["flag-a"],
            transformations=[{"type": "strip"}],
            detected_languages=["zh"],
        )

    setattr(fake_module, "normalize_input", fake_normalize_input)
    monkeypatch.setitem(sys.modules, "input_normalization", fake_module)
    monkeypatch.setattr(normalization_adapter, "is_agent_security_available", lambda: True)

    result = normalization_adapter.normalize("  source text  ")

    assert result.raw_text == "RAW"
    assert result.normalized_text == "normalized"
    assert result.suspicion_flags == ["flag-a"]
    assert result.transformations == [{"type": "strip"}]
    assert result.detected_languages == ["zh"]
    assert result.is_available is True
