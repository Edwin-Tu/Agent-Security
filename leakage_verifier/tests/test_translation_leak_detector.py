import pytest
from leakage_verifier.translation_leak_detector import TranslationLeakDetector


class TestTranslationLeakDetector:

    @pytest.fixture
    def detector(self):
        return TranslationLeakDetector()

    def test_detects_alias_based_translation_leak(self, detector):
        asset = {
            "asset_id": "secret_001",
            "name": "project name",
            "value": "Project Falcon",
            "aliases": ["獵鷹專案", "Falcon計畫"],
        }
        result = detector.detect("獵鷹專案將於下個月啟動。", asset)
        assert len(result) == 1
        assert result[0].leak_type == "translation_leak"

    def test_multiple_translation_hints_raise_confidence(self, detector):
        asset = {
            "asset_id": "secret_001",
            "name": "project name",
            "value": "Project Falcon",
            "aliases": ["獵鷹專案", "Falcon計畫", "機密專案"],
        }
        result = detector.detect("獵鷹專案和Falcon計畫都是機密專案", asset)
        assert len(result) == 1
        assert result[0].confidence > 0.5

    def test_unrelated_translation_is_not_leak(self, detector):
        asset = {
            "asset_id": "secret_001",
            "name": "project name",
            "value": "Project Falcon",
            "aliases": ["獵鷹專案", "Falcon計畫"],
        }
        result = detector.detect("今天天氣真好。", asset)
        assert len(result) == 0
