import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from attack_classifier.classifier import AttackClassifier


def get_classifier():
    attacks_path = Path(__file__).resolve().parent.parent / "rules" / "attacks.json"
    patterns_path = Path(__file__).resolve().parent.parent / "rules" / "attack_patterns.json"
    return AttackClassifier(
        attacks_path=str(attacks_path),
        patterns_path=str(patterns_path),
    )


class TestSafeInput:
    def setup_method(self):
        self.classifier = get_classifier()

    def test_safe_prompt_is_benign(self):
        result = self.classifier.classify("What is prompt injection?")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_normal_programming_question_is_benign(self):
        result = self.classifier.classify("How do I write a Python function to sort a list?")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_greeting_is_benign(self):
        result = self.classifier.classify("Hello, how are you?")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_general_knowledge_question_is_benign(self):
        result = self.classifier.classify("What is the capital of France?")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_empty_string_is_benign(self):
        result = self.classifier.classify("")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_whitespace_only_is_benign(self):
        result = self.classifier.classify("   ")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_learning_about_security_is_benign(self):
        result = self.classifier.classify("What is prompt injection and how does it work?")
        assert result.is_attack is False
        assert result.primary_category == "benign"

    def test_math_problem_is_benign(self):
        result = self.classifier.classify("What is 2 + 2?")
        assert result.is_attack is False
        assert result.primary_category == "benign"
