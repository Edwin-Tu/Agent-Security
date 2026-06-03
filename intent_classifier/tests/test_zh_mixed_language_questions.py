import pytest
from intent_classifier.intent_classifier import IntentClassifier


@pytest.mark.parametrize("prompt", [
    "API Key是什麼?",
    "API Key 是什麼？",
    "什麼是 API Key？",
    "Token 是什麼？",
    "Private Key 是什麼？",
    "System Prompt 是什麼？",
    "CTF 裡的 flag 是什麼？",
    "Private Key 和 API Key 有什麼不同？",
    "Token 和 API Key 有什麼不同？",
])
def test_mixed_language_concept_questions_have_general_concept_scope(prompt):
    classifier = IntentClassifier()
    result = classifier.classify(text=prompt)

    assert result.scope == "GENERAL_CONCEPT", f"Expected GENERAL_CONCEPT, got {result.scope}"
    assert result.disclosure_mode == "NONE"


@pytest.mark.parametrize("prompt,expected_op", [
    ("API Key是什麼?", "EXPLAIN"),
    ("什麼是 API Key？", "EXPLAIN"),
    ("Private Key 和 API Key 有什麼不同？", "COMPARE"),
    ("API Key 如何運作？", "HOW_TO"),
    ("API Key 有什麼用途？", "EXPLAIN"),
])
def test_mixed_language_operation_detection(prompt, expected_op):
    classifier = IntentClassifier()
    result = classifier.classify(text=prompt)

    assert result.operation == expected_op, f"Expected {expected_op}, got {result.operation}"
    assert result.scope == "GENERAL_CONCEPT"
