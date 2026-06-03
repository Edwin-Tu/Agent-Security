import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from input_guard.detectors.keyword_detector import KeywordDetector


class TestKeywordDetectorIntentSignals:
    def setup_method(self):
        self.detector = KeywordDetector()

    def test_api_key_mention_is_not_direct_secret_request(self):
        result = self.detector.detect("API key")
        assert "direct_secret_request" not in result["rules"]
        assert "asset_type_mention" in result["rules"]

    def test_token_mention_is_not_direct_secret_request(self):
        result = self.detector.detect("token")
        assert "direct_secret_request" not in result["rules"]
        assert "asset_type_mention" in result["rules"]
