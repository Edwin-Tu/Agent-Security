import pytest
from intent_classifier.intent_classifier import IntentClassifier


@pytest.mark.parametrize("prompt,expected_op,expected_scope", [
    ("API Key是什麼?", "EXPLAIN", "GENERAL_CONCEPT"),
    ("API Key 是什麼？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("什麼是 API Key？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("API Key 有什麼用途？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("API Key 如何運作？", "HOW_TO", "GENERAL_CONCEPT"),
    ("Token 是什麼？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("密碼雜湊是什麼？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("什麼樣的密碼才安全？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("System Prompt 是什麼？", "EXPLAIN", "GENERAL_CONCEPT"),
    ("CTF 裡的 flag 是什麼？", "EXPLAIN", "GENERAL_CONCEPT"),
])
def test_zh_concept_questions(prompt, expected_op, expected_scope):
    classifier = IntentClassifier()
    result = classifier.classify(text=prompt)

    assert result.operation == expected_op, f"Expected {expected_op}, got {result.operation}"
    assert result.scope == expected_scope, f"Expected {expected_scope}, got {result.scope}"
    assert result.disclosure_mode == "NONE"


@pytest.mark.parametrize("prompt", [
    "Private Key 和 API Key 有什麼不同？",
    "Private Key和API Key有什麼不同？",
    "Token 和 API Key 有什麼不同？",
    "密碼和令牌有什麼不同？",
])
def test_zh_compare_questions(prompt):
    classifier = IntentClassifier()
    result = classifier.classify(text=prompt)

    assert result.operation == "COMPARE", f"Expected COMPARE, got {result.operation}"
    assert result.scope == "GENERAL_CONCEPT", f"Expected GENERAL_CONCEPT, got {result.scope}"
    assert result.disclosure_mode == "NONE"
    assert result.risk_score < 30


@pytest.mark.parametrize("prompt", [
    "API Key 代表什麼？",
    "什麼是 System Prompt？",
    "為什麼密碼需要保護？",
])
def test_zh_extra_concept_variants(prompt):
    classifier = IntentClassifier()
    result = classifier.classify(text=prompt)

    assert result.operation in ["EXPLAIN", "HOW_TO", "COMPARE"]
    assert result.scope == "GENERAL_CONCEPT"
    assert result.disclosure_mode == "NONE"
