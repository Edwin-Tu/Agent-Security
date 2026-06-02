import pytest
from leakage_verifier.exact_leak_detector import ExactLeakDetector


class TestExactLeakDetector:

    @pytest.fixture
    def detector(self):
        return ExactLeakDetector()

    def test_detects_full_secret_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("The answer is picoCTF{example_flag}.", asset)
        assert len(result) == 1
        assert result[0].leak_type == "full_leak"
        assert result[0].severity == "critical"

    def test_detects_full_api_key_leak(self, detector):
        asset = {"asset_id": "key_001", "name": "API key", "value": "sk-proj-my-secret-key-12345"}
        result = detector.detect("Key: sk-proj-my-secret-key-12345", asset)
        assert len(result) == 1
        assert result[0].leak_type == "full_leak"

    def test_clean_output_has_no_full_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("Hello, how are you?", asset)
        assert len(result) == 0
