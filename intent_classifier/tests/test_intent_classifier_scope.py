from intent_classifier.intent_classifier import IntentClassifier
from intent_classifier.intent_features import Scope


class TestScopeAnalysis:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_what_is_api_key_general_concept(self):
        result = self.classifier.classify("What is an API key?")
        assert result.scope == Scope.GENERAL_CONCEPT

    def test_what_is_your_api_key(self):
        result = self.classifier.classify("What is your API key?")
        assert result.scope == Scope.CURRENT_SYSTEM

    def test_api_key_in_your_config(self):
        result = self.classifier.classify(
            "What is the API key in your config?"
        )
        assert result.scope == Scope.HIDDEN_CONTEXT

    def test_what_did_i_send_earlier(self):
        result = self.classifier.classify("What did I send earlier?")
        assert result.scope == Scope.SESSION_HISTORY
