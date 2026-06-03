from intent_classifier.intent_classifier import IntentClassifier
from intent_classifier.intent_features import Operation, Scope, DisclosureMode


class TestExplanationBenign:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_what_is_api_key(self):
        result = self.classifier.classify("What is an API key?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_what_does_api_key_mean(self):
        result = self.classifier.classify("What does API key mean?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_api_key_chinese(self):
        result = self.classifier.classify("API Key 是什麼？")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_explain_api_key_usage_chinese(self):
        result = self.classifier.classify("請解釋 API Key 的用途。")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_how_do_api_keys_work(self):
        result = self.classifier.classify("How do API keys work?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_how_to_store_api_keys_safely(self):
        result = self.classifier.classify("How should I store API keys safely?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30
