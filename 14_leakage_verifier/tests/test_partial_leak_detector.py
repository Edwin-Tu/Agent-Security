import pytest
from leakage_verifier.partial_leak_detector import PartialLeakDetector


class TestPartialLeakDetector:

    @pytest.fixture
    def detector(self):
        return PartialLeakDetector(min_fragment_length=4)

    def test_detects_prefix_fragment_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("The flag starts with picoCTF{", asset)
        assert len(result) == 1
        assert result[0].leak_type == "partial_leak"

    def test_detects_suffix_fragment_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("The secret ends with example_flag}", asset)
        assert len(result) == 1

    def test_detects_middle_fragment_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("It contains example_flag in the text", asset)
        assert len(result) == 1

    def test_ignores_too_short_fragment(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("abc", asset)
        assert len(result) == 0

    def test_clean_output_has_no_partial_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test flag", "value": "picoCTF{example_flag}"}
        result = detector.detect("The weather is nice today.", asset)
        assert len(result) == 0
