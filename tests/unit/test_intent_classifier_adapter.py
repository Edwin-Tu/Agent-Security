from __future__ import annotations

import sys
import types
from dataclasses import is_dataclass
from enum import Enum

import elder_privacy_guard.adapters.intent_classifier_adapter as adapter
import elder_privacy_guard.adapters.path_loader as path_loader
import pytest


def test_intent_classification_dataclass_exists() -> None:
    assert hasattr(adapter, "IntentClassification")
    assert is_dataclass(adapter.IntentClassification)


def test_classify_intent_returns_unknown_defaults_when_agent_security_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(path_loader, "is_agent_security_available", lambda: False)

    result = adapter.classify_intent("hello")

    assert result.is_available is False
    assert result.intent == "UNKNOWN"
    assert result.operation == "UNKNOWN"
    assert result.scope == "UNKNOWN"
    assert result.disclosure_mode == "UNKNOWN"
    assert result.asset_reference_type == "UNKNOWN"
    assert result.confidence == 0.0
    assert result.reasons == []


def test_classify_intent_handles_empty_input_when_agent_security_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(path_loader, "is_agent_security_available", lambda: False)

    result = adapter.classify_intent("")

    assert result.is_available is False
    assert result.intent == "UNKNOWN"
    assert result.reasons == []


def test_classify_intent_maps_connected_agent_security_result_and_passthrough_args(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeOperation(str, Enum):
        EXTRACT = "EXTRACT"

    class FakeScope(str, Enum):
        PROTECTED_REGISTRY = "PROTECTED_REGISTRY"

    class FakeDisclosureMode(str, Enum):
        FULL_VALUE = "FULL_VALUE"

    class FakeIntentClassifier:
        rules_path: object | None

        def __init__(self, rules_path: object | None = None) -> None:
            self.rules_path = rules_path

        def classify(
            self,
            text: str,
            matched_assets: list[object] | None = None,
            input_guard_flags: list[object] | None = None,
            attack_categories: list[object] | None = None,
            session_history: object | None = None,
        ) -> object:
            assert text == "prompt"
            assert matched_assets == ["asset-1"]
            assert input_guard_flags == ["flag-a"]
            assert attack_categories == ["prompt-injection"]
            assert session_history is None
            return types.SimpleNamespace(
                intent="intent:extract",
                operation=FakeOperation.EXTRACT,
                scope=FakeScope.PROTECTED_REGISTRY,
                disclosure_mode=FakeDisclosureMode.FULL_VALUE,
                asset_reference_type="REFERENCE",
                confidence=0.87,
                reasons=["matched rule"],
            )

    fake_module = types.ModuleType("intent_classifier")
    setattr(fake_module, "IntentClassifier", FakeIntentClassifier)
    monkeypatch.setitem(sys.modules, "intent_classifier", fake_module)
    monkeypatch.setattr(path_loader, "is_agent_security_available", lambda: True)

    result = adapter.classify_intent(
        "prompt",
        matched_assets=["asset-1"],
        input_guard_flags=["flag-a"],
        attack_categories=["prompt-injection"],
    )

    assert result.is_available is True
    assert result.intent == "intent:extract"
    assert result.operation == "EXTRACT"
    assert result.scope == "PROTECTED_REGISTRY"
    assert result.disclosure_mode == "FULL_VALUE"
    assert result.asset_reference_type == "REFERENCE"
    assert result.confidence == 0.87
    assert result.reasons == ["matched rule"]


def test_classify_intent_returns_unknown_defaults_when_classifier_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RaisingIntentClassifier:
        rules_path: object | None

        def __init__(self, rules_path: object | None = None) -> None:
            self.rules_path = rules_path

        def classify(
            self,
            _text: str,
            _matched_assets: list[object] | None = None,
            _input_guard_flags: list[object] | None = None,
            _attack_categories: list[object] | None = None,
            _session_history: object | None = None,
        ) -> object:
            raise RuntimeError("boom")

    fake_module = types.ModuleType("intent_classifier")
    setattr(fake_module, "IntentClassifier", RaisingIntentClassifier)
    monkeypatch.setitem(sys.modules, "intent_classifier", fake_module)
    monkeypatch.setattr(path_loader, "is_agent_security_available", lambda: True)

    result = adapter.classify_intent("prompt")

    assert result.is_available is False
    assert result.intent == "UNKNOWN"
    assert result.operation == "UNKNOWN"
    assert result.scope == "UNKNOWN"
    assert result.disclosure_mode == "UNKNOWN"
    assert result.asset_reference_type == "UNKNOWN"
    assert result.confidence == 0.0
    assert result.reasons == []
