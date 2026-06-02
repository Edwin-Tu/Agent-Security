import pytest
from leakage_verifier.encoding_leak_detector import EncodingLeakDetector


class TestEncodingLeakDetector:

    @pytest.fixture
    def detector(self):
        return EncodingLeakDetector()

    def test_detects_base64_encoded_secret(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("Encoded: cGljb0NURnthYmN9", asset)
        assert len(result) == 1
        assert result[0].leak_type == "encoding_leak"
        assert "base64" in result[0].match_type.lower()

    def test_detects_hex_encoded_secret(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("Hex: 7069636f4354467b6162637d", asset)
        assert len(result) == 1
        assert "hex" in result[0].match_type.lower()

    def test_detects_url_encoded_secret(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("URL: picoCTF%7Babc%7D", asset)
        assert len(result) == 1
        assert "url" in result[0].match_type.lower()

    def test_detects_rot13_encoded_secret(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("ROT13: cvpbPGS{nop}", asset)
        assert len(result) == 1
        assert "rot13" in result[0].match_type.lower()

    def test_invalid_encoded_text_does_not_crash(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("!!! invalid !!!", asset)
        assert result is not None

    def test_random_text_is_not_encoding_leak(self, detector):
        asset = {"asset_id": "secret_001", "name": "test", "value": "picoCTF{abc}"}
        result = detector.detect("The quick brown fox jumps over the lazy dog.", asset)
        assert len(result) == 0
