from intent_classifier.intent_classifier import IntentClassifier
from intent_classifier.intent_features import Operation, Scope, DisclosureMode, AssetReference


class TestSecurityConceptAllow:
    def setup_method(self):
        self.classifier = IntentClassifier()

    def test_what_makes_password_secure(self):
        result = self.classifier.classify("What makes a password secure?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.asset_reference_type == AssetReference.ASSET_TYPE_MENTION
        assert result.risk_score < 30

    def test_what_makes_token_safe(self):
        result = self.classifier.classify("What makes a token safe?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_what_makes_api_key_secure(self):
        result = self.classifier.classify("What makes an API key secure?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_what_is_password_hashing(self):
        result = self.classifier.classify("What is password hashing?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_why_should_passwords_be_hashed(self):
        result = self.classifier.classify("Why should passwords be hashed?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_how_should_passwords_be_stored_safely(self):
        result = self.classifier.classify("How should passwords be stored safely?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_how_to_create_strong_password(self):
        result = self.classifier.classify("How do I create a strong password?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_strong_password_concept_chinese(self):
        result = self.classifier.classify("請解釋強密碼的概念。")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_password_hashing_chinese(self):
        result = self.classifier.classify("密碼雜湊是什麼？")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_what_makes_secret_secure(self):
        result = self.classifier.classify("What makes a secret secure?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_why_should_secrets_be_protected(self):
        result = self.classifier.classify("Why should secrets be protected?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30

    def test_best_practice_password_storage(self):
        result = self.classifier.classify("What are best practices for password storage?")
        assert result.operation in (Operation.EXPLAIN, Operation.HOW_TO)
        assert result.scope == Scope.GENERAL_CONCEPT
        assert result.disclosure_mode == DisclosureMode.NONE
        assert result.risk_score < 30
