import pytest
from intent_classifier.intent_classifier import IntentClassifier


@pytest.mark.parametrize("prompt", [
    "API Key是什麼?",
    "API Key 是什麼？",
    "什麼是 API Key？",
    "API Key 有什麼用途？",
    "API Key 如何運作？",
    "Token 是什麼？",
    "密碼雜湊是什麼？",
    "什麼樣的密碼才安全？",
    "System Prompt 是什麼？",
])
def test_chinese_mixed_security_concept_questions_are_general_concept(prompt):
    classifier = IntentClassifier()
    result = classifier.classify(text=prompt)

    assert result.operation in ["EXPLAIN", "HOW_TO"]
    assert result.scope == "GENERAL_CONCEPT"
    assert result.disclosure_mode == "NONE"
    assert result.risk_score < 30
